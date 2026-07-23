import csv
from datetime import datetime
from datetime import timezone
from io import BytesIO
from io import StringIO
from typing import Any
from uuid import uuid4
from zipfile import ZIP_DEFLATED
from zipfile import ZipFile

from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastapi import Response
from fastapi import status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import desc
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import Session

from ee.onyx.db.usage_export import UsageReportMetadata
from onyx.auth.permissions import require_permission
from onyx.auth.users import get_display_email
from onyx.configs.constants import FileOrigin
from onyx.configs.constants import MessageType
from onyx.db.engine.sql_engine import get_session
from onyx.db.enums import Permission
from onyx.db.models import ChatSession
from onyx.db.models import UsageReport
from onyx.db.models import User
from onyx.error_handling.error_codes import OnyxErrorCode
from onyx.error_handling.exceptions import OnyxError
from onyx.file_store.file_store import get_default_file_store

router = APIRouter(prefix="/admin")


class UsageReportRequest(BaseModel):
    period_from: datetime | None = None
    period_to: datetime | None = None


def _usage_report_bounds(
    period_from: datetime | None, period_to: datetime | None
) -> tuple[datetime, datetime]:
    now = datetime.now(tz=timezone.utc)
    return period_from or datetime.fromtimestamp(0, tz=timezone.utc), period_to or now


def _query_sessions(
    db_session: Session,
    period_from: datetime,
    period_to: datetime,
) -> list[ChatSession]:
    stmt = (
        select(ChatSession)
        .where(ChatSession.deleted.is_(False))
        .where(ChatSession.time_created >= period_from)
        .where(ChatSession.time_created <= period_to)
        .options(
            selectinload(ChatSession.user),
            selectinload(ChatSession.persona),
            selectinload(ChatSession.messages),
        )
        .order_by(desc(ChatSession.time_created))
    )
    return list(db_session.scalars(stmt))


def _build_usage_report_zip(
    db_session: Session,
    period_from: datetime,
    period_to: datetime,
) -> bytes:
    sessions = _query_sessions(db_session, period_from, period_to)

    chat_rows: list[dict[str, Any]] = []
    user_rows: dict[str, dict[str, Any]] = {}
    for session in sessions:
        user_email = (
            get_display_email(session.user.email)
            if session.user and session.user.email
            else ""
        )
        user_key = str(session.user_id) if session.user_id else ""
        if user_key and user_key not in user_rows:
            user_rows[user_key] = {
                "user_id": user_key,
                "user_email": user_email,
                "session_count": 0,
                "message_count": 0,
            }
        if user_key:
            user_rows[user_key]["session_count"] += 1

        for message in session.messages:
            if message.message_type != MessageType.ASSISTANT:
                continue
            if user_key:
                user_rows[user_key]["message_count"] += 1
            chat_rows.append(
                {
                    "session_id": str(session.id),
                    "user_id": user_key,
                    "flow_type": "Slack" if session.onyxbot_flow else "Chat",
                    "time_sent": message.time_sent.isoformat(),
                    "assistant_name": session.persona.name if session.persona else "",
                    "user_email": user_email,
                    "number_of_tokens": message.token_count,
                    "llm_model": message.model_display_name or "",
                }
            )

    chat_buffer = StringIO()
    chat_writer = csv.DictWriter(
        chat_buffer,
        fieldnames=[
            "session_id",
            "user_id",
            "flow_type",
            "time_sent",
            "assistant_name",
            "user_email",
            "number_of_tokens",
            "llm_model",
        ],
    )
    chat_writer.writeheader()
    for row in chat_rows:
        chat_writer.writerow(row)

    users_buffer = StringIO()
    users_writer = csv.DictWriter(
        users_buffer,
        fieldnames=["user_id", "user_email", "session_count", "message_count"],
    )
    users_writer.writeheader()
    for row in user_rows.values():
        users_writer.writerow(row)

    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w", compression=ZIP_DEFLATED) as zip_file:
        zip_file.writestr("chat_messages.csv", chat_buffer.getvalue())
        zip_file.writestr("users.csv", users_buffer.getvalue())
    return zip_buffer.getvalue()


@router.get("/usage-report")
def list_usage_reports(
    _: User = Depends(require_permission(Permission.FULL_ADMIN_PANEL_ACCESS)),
    db_session: Session = Depends(get_session),
) -> list[UsageReportMetadata]:
    reports = list(
        db_session.scalars(select(UsageReport).order_by(desc(UsageReport.time_created)))
    )
    return [
        UsageReportMetadata(
            report_name=report.report_name,
            requestor=(
                get_display_email(report.requestor.email)
                if report.requestor and report.requestor.email
                else None
            ),
            time_created=report.time_created,
            period_from=report.period_from,
            period_to=report.period_to,
        )
        for report in reports
    ]


@router.post("/usage-report", status_code=status.HTTP_204_NO_CONTENT)
def generate_usage_report(
    request: UsageReportRequest = Body(default_factory=UsageReportRequest),
    current_user: User = Depends(
        require_permission(Permission.FULL_ADMIN_PANEL_ACCESS)
    ),
    db_session: Session = Depends(get_session),
) -> Response:
    period_from, period_to = _usage_report_bounds(
        request.period_from, request.period_to
    )
    if period_from >= period_to:
        raise OnyxError(
            OnyxErrorCode.INVALID_INPUT, "period_from must be before period_to"
        )

    report_name = f"usage-report-{uuid4()}.zip"
    report_bytes = _build_usage_report_zip(db_session, period_from, period_to)
    file_store = get_default_file_store()
    file_store.save_file(
        content=BytesIO(report_bytes),
        display_name=report_name,
        file_origin=FileOrigin.GENERATED_REPORT,
        file_type="application/zip",
        file_id=report_name,
    )

    usage_report = UsageReport(
        report_name=report_name,
        requestor_user_id=current_user.id,
        period_from=period_from,
        period_to=period_to,
    )
    db_session.add(usage_report)
    db_session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/usage-report/{report_name}")
def read_usage_report(
    report_name: str,
    _: User = Depends(require_permission(Permission.FULL_ADMIN_PANEL_ACCESS)),
    db_session: Session = Depends(get_session),
) -> StreamingResponse:
    report = db_session.scalar(
        select(UsageReport).where(UsageReport.report_name == report_name)
    )
    if report is None:
        raise OnyxError(OnyxErrorCode.NOT_FOUND, "Usage report not found")

    file_store = get_default_file_store()
    if not file_store.has_file(
        file_id=report_name,
        file_origin=FileOrigin.GENERATED_REPORT,
        file_type="application/zip",
    ):
        raise OnyxError(OnyxErrorCode.NOT_FOUND, "Usage report not found")

    stream = file_store.read_file(report_name)
    headers = {"Content-Disposition": f'attachment; filename="{report_name}"'}
    return StreamingResponse(stream, media_type="application/zip", headers=headers)
