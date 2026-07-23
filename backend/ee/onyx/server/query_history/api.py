import csv
from datetime import datetime
from datetime import timezone
from io import BytesIO
from io import StringIO
from uuid import UUID
from uuid import uuid4

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi.responses import StreamingResponse
from sqlalchemy import desc
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import Session

from ee.onyx.server.query_history.models import AbridgedSearchDoc
from ee.onyx.server.query_history.models import ChatSessionMinimal
from ee.onyx.server.query_history.models import ChatSessionSnapshot
from ee.onyx.server.query_history.models import MessageSnapshot
from ee.onyx.server.query_history.models import QueryHistoryExport
from onyx.auth.permissions import require_permission
from onyx.auth.users import get_display_email
from onyx.background.task_utils import construct_query_history_report_name
from onyx.configs.constants import FileOrigin
from onyx.configs.constants import FileType
from onyx.configs.constants import MessageType
from onyx.configs.constants import PUBLIC_API_TAGS
from onyx.configs.constants import QAFeedbackType
from onyx.configs.constants import QueryHistoryType
from onyx.configs.constants import SessionType
from onyx.db.chat import get_chat_session_by_id
from onyx.db.engine.sql_engine import get_session
from onyx.db.enums import Permission
from onyx.db.enums import TaskStatus
from onyx.db.models import ChatMessage
from onyx.db.models import ChatSession
from onyx.db.models import FileRecord
from onyx.db.models import TaskQueueState
from onyx.db.models import User
from onyx.error_handling.error_codes import OnyxErrorCode
from onyx.error_handling.exceptions import OnyxError
from onyx.file_store.file_store import get_default_file_store
from onyx.server.documents.models import PaginatedReturn
from onyx.server.settings.store import load_settings

router = APIRouter()

ONYX_ANONYMIZED_EMAIL = "anonymous@anonymous.invalid"


def ensure_query_history_is_enabled(
    disallowed: list[QueryHistoryType],
) -> QueryHistoryType:
    query_history_type = load_settings().query_history_type or QueryHistoryType.NORMAL
    if query_history_type in disallowed:
        raise OnyxError(
            OnyxErrorCode.INSUFFICIENT_PERMISSIONS,
            "Query history has been disabled by the administrator.",
        )
    return query_history_type


def _day_bounds(
    start: datetime | None, end: datetime | None
) -> tuple[datetime, datetime]:
    now = datetime.now(tz=timezone.utc)
    return start or datetime.fromtimestamp(0, tz=timezone.utc), end or now


def _feedback_type_for_message(message: ChatMessage) -> QAFeedbackType | None:
    positives = 0
    negatives = 0
    for feedback in message.chat_message_feedbacks:
        if feedback.is_positive is True:
            positives += 1
        elif feedback.is_positive is False:
            negatives += 1

    if positives and negatives:
        return QAFeedbackType.MIXED
    if positives:
        return QAFeedbackType.LIKE
    if negatives:
        return QAFeedbackType.DISLIKE
    return None


def _session_feedback_type(chat_session: ChatSession) -> QAFeedbackType | None:
    message_feedback_types = [
        _feedback_type_for_message(message)
        for message in chat_session.messages
        if message.message_type == MessageType.ASSISTANT
    ]
    message_feedback_types = [
        feedback for feedback in message_feedback_types if feedback is not None
    ]
    if not message_feedback_types:
        return None
    if QAFeedbackType.MIXED in message_feedback_types:
        return QAFeedbackType.MIXED
    if (
        QAFeedbackType.LIKE in message_feedback_types
        and QAFeedbackType.DISLIKE in message_feedback_types
    ):
        return QAFeedbackType.MIXED
    if QAFeedbackType.LIKE in message_feedback_types:
        return QAFeedbackType.LIKE
    if QAFeedbackType.DISLIKE in message_feedback_types:
        return QAFeedbackType.DISLIKE
    return None


def _message_snapshot(message: ChatMessage) -> MessageSnapshot:
    documents = [
        AbridgedSearchDoc(
            document_id=search_doc.document_id,
            semantic_identifier=search_doc.semantic_id,
            link=search_doc.link,
        )
        for search_doc in message.search_docs
    ]

    feedback_text = None
    for feedback in message.chat_message_feedbacks:
        if feedback.feedback_text:
            feedback_text = feedback.feedback_text
            break

    return MessageSnapshot(
        id=message.id,
        message=message.message,
        message_type=message.message_type,
        documents=documents,
        feedback_type=_feedback_type_for_message(message),
        feedback_text=feedback_text,
        time_created=message.time_sent,
    )


def _session_flow_type(chat_session: ChatSession) -> SessionType:
    return SessionType.SLACK if chat_session.onyxbot_flow else SessionType.CHAT


def _session_snapshot(chat_session: ChatSession) -> ChatSessionSnapshot:
    messages = sorted(
        chat_session.messages, key=lambda message: (message.time_sent, message.id)
    )
    return ChatSessionSnapshot(
        id=chat_session.id,
        user_email=(
            get_display_email(chat_session.user.email)
            if chat_session.user and chat_session.user.email
            else None
        ),
        name=chat_session.description,
        messages=[_message_snapshot(message) for message in messages],
        assistant_id=chat_session.persona_id,
        assistant_name=chat_session.persona.name if chat_session.persona else None,
        time_created=chat_session.time_created,
        flow_type=_session_flow_type(chat_session),
    )


def _session_minimal(chat_session: ChatSession) -> ChatSessionMinimal:
    messages = sorted(
        chat_session.messages, key=lambda message: (message.time_sent, message.id)
    )
    first_user_message = next(
        (
            message.message
            for message in messages
            if message.message_type == MessageType.USER
        ),
        "",
    )
    first_ai_message = next(
        (
            message.message
            for message in messages
            if message.message_type == MessageType.ASSISTANT
        ),
        "",
    )

    return ChatSessionMinimal(
        id=chat_session.id,
        user_email=(
            get_display_email(chat_session.user.email)
            if chat_session.user and chat_session.user.email
            else None
        ),
        name=chat_session.description,
        first_user_message=first_user_message,
        first_ai_message=first_ai_message,
        assistant_id=chat_session.persona_id,
        assistant_name=chat_session.persona.name if chat_session.persona else None,
        time_created=chat_session.time_created,
        feedback_type=_session_feedback_type(chat_session),
        flow_type=_session_flow_type(chat_session),
        conversation_length=sum(
            1
            for message in chat_session.messages
            if message.message_type in {MessageType.USER, MessageType.ASSISTANT}
        ),
    )


def _query_sessions(
    db_session: Session,
    start_time: datetime | None,
    end_time: datetime | None,
) -> list[ChatSession]:
    stmt = (
        select(ChatSession)
        .where(ChatSession.deleted.is_(False))
        .options(
            selectinload(ChatSession.user),
            selectinload(ChatSession.persona),
            selectinload(ChatSession.messages).selectinload(ChatMessage.search_docs),
            selectinload(ChatSession.messages).selectinload(
                ChatMessage.chat_message_feedbacks
            ),
        )
        .order_by(desc(ChatSession.time_created))
    )
    if start_time is not None:
        stmt = stmt.where(ChatSession.time_created >= start_time)
    if end_time is not None:
        stmt = stmt.where(ChatSession.time_created <= end_time)

    return list(db_session.scalars(stmt))


@router.get("/admin/chat-session-history")
def get_chat_session_history(
    page_num: int = Query(0, ge=0),
    page_size: int = Query(10, ge=1),
    feedback_type: QAFeedbackType | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    _: User = Depends(require_permission(Permission.FULL_ADMIN_PANEL_ACCESS)),
    db_session: Session = Depends(get_session),
) -> PaginatedReturn[ChatSessionMinimal]:
    ensure_query_history_is_enabled(disallowed=[QueryHistoryType.DISABLED])
    sessions = _query_sessions(db_session, start_time, end_time)
    items = [_session_minimal(chat_session) for chat_session in sessions]

    if feedback_type is not None:
        items = [item for item in items if item.feedback_type == feedback_type]

    total_items = len(items)
    start_index = page_num * page_size
    end_index = start_index + page_size
    return PaginatedReturn(items=items[start_index:end_index], total_items=total_items)


@router.get("/admin/chat-session-history/{chat_session_id}")
def get_chat_session_admin(
    chat_session_id: UUID,
    _: User = Depends(require_permission(Permission.FULL_ADMIN_PANEL_ACCESS)),
    db_session: Session = Depends(get_session),
) -> ChatSessionSnapshot:
    query_history_type = ensure_query_history_is_enabled(
        disallowed=[QueryHistoryType.DISABLED]
    )
    try:
        chat_session = get_chat_session_by_id(chat_session_id, None, db_session)
    except ValueError as exc:
        raise OnyxError(OnyxErrorCode.NOT_FOUND, "Chat session not found") from exc
    snapshot = _session_snapshot(chat_session)
    if query_history_type == QueryHistoryType.ANONYMIZED and snapshot.user_email:
        snapshot.user_email = ONYX_ANONYMIZED_EMAIL
    return snapshot


def _query_history_task_name(start: datetime, end: datetime) -> str:
    return f"query-history|{start.isoformat()}|{end.isoformat()}"


def _build_query_history_csv(
    db_session: Session,
    start: datetime,
    end: datetime,
) -> str:
    sessions = _query_sessions(db_session, start, end)
    output = StringIO()
    writer = csv.DictWriter(
        output,
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
    writer.writeheader()

    for session in sessions:
        for message in sorted(
            session.messages, key=lambda msg: (msg.time_sent, msg.id)
        ):
            if message.message_type != MessageType.ASSISTANT:
                continue
            writer.writerow(
                {
                    "session_id": str(session.id),
                    "user_id": str(session.user_id) if session.user_id else "",
                    "flow_type": _session_flow_type(session),
                    "time_sent": message.time_sent.isoformat(),
                    "assistant_name": session.persona.name if session.persona else "",
                    "user_email": (
                        get_display_email(session.user.email)
                        if session.user and session.user.email
                        else ""
                    ),
                    "number_of_tokens": message.token_count,
                    "llm_model": message.model_display_name or "",
                }
            )

    return output.getvalue()


@router.get("/admin/query-history/list")
def list_all_query_history_exports(
    _: User = Depends(require_permission(Permission.FULL_ADMIN_PANEL_ACCESS)),
    db_session: Session = Depends(get_session),
) -> list[QueryHistoryExport]:
    ensure_query_history_is_enabled(disallowed=[QueryHistoryType.DISABLED])
    pending_tasks = [
        QueryHistoryExport.from_task(task)
        for task in db_session.scalars(
            select(TaskQueueState).where(
                TaskQueueState.task_name.like("query-history|%")
            )
        )
    ]
    generated_files = [
        QueryHistoryExport.from_file(file)
        for file in db_session.scalars(
            select(FileRecord).where(
                FileRecord.file_origin == FileOrigin.QUERY_HISTORY_CSV
            )
        )
    ]

    merged: dict[str, QueryHistoryExport] = {
        task.task_id: task for task in pending_tasks
    }
    for generated_file in generated_files:
        merged[generated_file.task_id] = generated_file

    return sorted(merged.values(), key=lambda item: item.start_time, reverse=True)


@router.post("/admin/query-history/start-export", tags=PUBLIC_API_TAGS)
def start_query_history_export(
    _: User = Depends(require_permission(Permission.FULL_ADMIN_PANEL_ACCESS)),
    db_session: Session = Depends(get_session),
    start: datetime | None = None,
    end: datetime | None = None,
) -> dict[str, str]:
    ensure_query_history_is_enabled(disallowed=[QueryHistoryType.DISABLED])
    start = start or datetime.fromtimestamp(0, tz=timezone.utc)
    end = end or datetime.now(tz=timezone.utc)
    if start >= end:
        raise OnyxError(
            OnyxErrorCode.INVALID_INPUT,
            f"Start time must come before end time, but instead got the start time coming after; {start=} {end=}",
        )

    task_id = str(uuid4())
    task = TaskQueueState(
        task_id=task_id,
        task_name=_query_history_task_name(start, end),
        status=TaskStatus.PENDING,
        start_time=datetime.now(tz=timezone.utc),
    )
    db_session.add(task)
    db_session.commit()

    report_name = construct_query_history_report_name(task_id)
    csv_bytes = _build_query_history_csv(db_session, start, end)
    file_store = get_default_file_store()
    file_store.save_file(
        content=BytesIO(csv_bytes.encode()),
        display_name=report_name,
        file_origin=FileOrigin.QUERY_HISTORY_CSV,
        file_type=FileType.CSV.value,
        file_metadata={"start": start.isoformat(), "end": end.isoformat()},
        file_id=report_name,
    )
    task.status = TaskStatus.SUCCESS
    db_session.commit()
    return {"request_id": task_id}


@router.get("/admin/query-history/export-status", tags=PUBLIC_API_TAGS)
def get_query_history_export_status(
    request_id: str,
    _: User = Depends(require_permission(Permission.FULL_ADMIN_PANEL_ACCESS)),
    db_session: Session = Depends(get_session),
) -> dict[str, str]:
    ensure_query_history_is_enabled(disallowed=[QueryHistoryType.DISABLED])
    task = db_session.scalar(
        select(TaskQueueState).where(TaskQueueState.task_id == request_id)
    )
    if task:
        return {"status": task.status}

    file_store = get_default_file_store()
    report_name = construct_query_history_report_name(request_id)
    if file_store.has_file(
        file_id=report_name,
        file_origin=FileOrigin.QUERY_HISTORY_CSV,
        file_type=FileType.CSV.value,
    ):
        return {"status": TaskStatus.SUCCESS}

    raise OnyxError(OnyxErrorCode.NOT_FOUND, "Query history export not found")


@router.get("/admin/query-history/download", tags=PUBLIC_API_TAGS)
def download_query_history_csv(
    request_id: str,
    _: User = Depends(require_permission(Permission.FULL_ADMIN_PANEL_ACCESS)),
) -> StreamingResponse:
    ensure_query_history_is_enabled(disallowed=[QueryHistoryType.DISABLED])
    report_name = construct_query_history_report_name(request_id)
    file_store = get_default_file_store()
    if not file_store.has_file(
        file_id=report_name,
        file_origin=FileOrigin.QUERY_HISTORY_CSV,
        file_type=FileType.CSV.value,
    ):
        raise OnyxError(OnyxErrorCode.NOT_FOUND, "Query history export not found")

    file_stream = file_store.read_file(report_name)
    headers = {"Content-Disposition": f'attachment; filename="{report_name}"'}
    return StreamingResponse(
        file_stream, media_type=FileType.CSV.value, headers=headers
    )
