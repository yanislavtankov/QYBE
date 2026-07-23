from collections import defaultdict
from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone

from fastapi import APIRouter
from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import Session

from onyx.auth.permissions import require_permission
from onyx.configs.constants import MessageType
from onyx.configs.constants import QAFeedbackType
from onyx.db.engine.sql_engine import get_session
from onyx.db.enums import Permission
from onyx.db.models import ChatMessage
from onyx.db.models import ChatSession
from onyx.db.models import User

router = APIRouter(prefix="/analytics")

_DEFAULT_LOOKBACK_DAYS = 30


class QueryAnalyticsResponse(BaseModel):
    total_queries: int
    total_likes: int
    total_dislikes: int
    date: date


class UserAnalyticsResponse(BaseModel):
    total_active_users: int
    date: date


class OnyxbotAnalyticsResponse(BaseModel):
    total_queries: int
    auto_resolved: int
    date: date


class PersonaMessageAnalyticsResponse(BaseModel):
    total_messages: int
    date: date
    persona_id: int


class PersonaUniqueUserAnalyticsResponse(BaseModel):
    unique_users: int
    date: date
    persona_id: int


def _day_bounds(
    start: datetime | None, end: datetime | None
) -> tuple[datetime, datetime]:
    now = datetime.now(tz=timezone.utc)
    resolved_start = start or (now - timedelta(days=_DEFAULT_LOOKBACK_DAYS))
    resolved_end = end or now
    return resolved_start, resolved_end


def _session_feedback_type(session: ChatSession) -> QAFeedbackType | None:
    positives = 0
    negatives = 0
    for message in session.messages:
        if message.message_type != MessageType.ASSISTANT:
            continue
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


def _date_key(value: datetime) -> date:
    return value.date()


@router.get("/admin/query")
def get_query_analytics(
    start: datetime | None = None,
    end: datetime | None = None,
    _: User = Depends(require_permission(Permission.FULL_ADMIN_PANEL_ACCESS)),
    db_session: Session = Depends(get_session),
) -> list[QueryAnalyticsResponse]:
    start, end = _day_bounds(start, end)
    stmt = (
        select(ChatSession)
        .where(ChatSession.deleted.is_(False))
        .where(ChatSession.time_created >= start)
        .where(ChatSession.time_created <= end)
        .options(
            selectinload(ChatSession.messages).selectinload(
                ChatMessage.chat_message_feedbacks
            )
        )
        .order_by(ChatSession.time_created.asc())
    )
    sessions = list(db_session.scalars(stmt))

    query_usage_by_day: dict[date, dict[str, int]] = defaultdict(
        lambda: {"queries": 0, "likes": 0, "dislikes": 0}
    )
    for session in sessions:
        day = _date_key(session.time_created)
        query_usage_by_day[day]["queries"] += 1
        feedback_type = _session_feedback_type(session)
        if feedback_type == QAFeedbackType.LIKE:
            query_usage_by_day[day]["likes"] += 1
        elif feedback_type == QAFeedbackType.DISLIKE:
            query_usage_by_day[day]["dislikes"] += 1

    return [
        QueryAnalyticsResponse(
            total_queries=values["queries"],
            total_likes=values["likes"],
            total_dislikes=values["dislikes"],
            date=day,
        )
        for day, values in sorted(query_usage_by_day.items())
    ]


@router.get("/admin/user")
def get_user_analytics(
    start: datetime | None = None,
    end: datetime | None = None,
    _: User = Depends(require_permission(Permission.FULL_ADMIN_PANEL_ACCESS)),
    db_session: Session = Depends(get_session),
) -> list[UserAnalyticsResponse]:
    start, end = _day_bounds(start, end)
    stmt = (
        select(ChatSession.user_id, func.date(ChatSession.time_created))
        .where(ChatSession.deleted.is_(False))
        .where(ChatSession.user_id.is_not(None))
        .where(ChatSession.time_created >= start)
        .where(ChatSession.time_created <= end)
        .distinct()
    )
    rows = db_session.execute(stmt).all()

    users_by_day: dict[date, int] = defaultdict(int)
    for _, day in rows:
        if day is not None:
            users_by_day[day] += 1

    return [
        UserAnalyticsResponse(total_active_users=count, date=day)
        for day, count in sorted(users_by_day.items())
    ]


@router.get("/admin/onyxbot")
def get_onyxbot_analytics(
    start: datetime | None = None,
    end: datetime | None = None,
    _: User = Depends(require_permission(Permission.FULL_ADMIN_PANEL_ACCESS)),
    db_session: Session = Depends(get_session),
) -> list[OnyxbotAnalyticsResponse]:
    start, end = _day_bounds(start, end)
    stmt = (
        select(ChatSession)
        .where(ChatSession.onyxbot_flow.is_(True))
        .where(ChatSession.time_created >= start)
        .where(ChatSession.time_created <= end)
        .options(selectinload(ChatSession.messages))
        .order_by(ChatSession.time_created.asc())
    )
    sessions = list(db_session.scalars(stmt))

    by_day: dict[date, dict[str, int]] = defaultdict(
        lambda: {"queries": 0, "auto_resolved": 0}
    )
    for session in sessions:
        day = _date_key(session.time_created)
        by_day[day]["queries"] += 1

    return [
        OnyxbotAnalyticsResponse(
            total_queries=values["queries"],
            auto_resolved=values["auto_resolved"],
            date=day,
        )
        for day, values in sorted(by_day.items())
    ]


@router.get("/admin/persona/messages")
def get_persona_message_analytics(
    persona_id: int,
    start: datetime | None = None,
    end: datetime | None = None,
    _: User = Depends(require_permission(Permission.FULL_ADMIN_PANEL_ACCESS)),
    db_session: Session = Depends(get_session),
) -> list[PersonaMessageAnalyticsResponse]:
    start, end = _day_bounds(start, end)
    stmt = (
        select(ChatSession)
        .where(ChatSession.persona_id == persona_id)
        .where(ChatSession.time_created >= start)
        .where(ChatSession.time_created <= end)
        .options(selectinload(ChatSession.messages))
    )
    sessions = list(db_session.scalars(stmt))

    by_day: dict[date, int] = defaultdict(int)
    for session in sessions:
        by_day[_date_key(session.time_created)] += sum(
            1
            for message in session.messages
            if message.message_type == MessageType.ASSISTANT
        )

    return [
        PersonaMessageAnalyticsResponse(
            total_messages=count, date=day, persona_id=persona_id
        )
        for day, count in sorted(by_day.items())
    ]


@router.get("/admin/persona/unique-users")
def get_persona_unique_users(
    persona_id: int,
    start: datetime | None = None,
    end: datetime | None = None,
    _: User = Depends(require_permission(Permission.FULL_ADMIN_PANEL_ACCESS)),
    db_session: Session = Depends(get_session),
) -> list[PersonaUniqueUserAnalyticsResponse]:
    start, end = _day_bounds(start, end)
    stmt = (
        select(ChatSession.user_id, func.date(ChatSession.time_created))
        .where(ChatSession.persona_id == persona_id)
        .where(ChatSession.user_id.is_not(None))
        .where(ChatSession.time_created >= start)
        .where(ChatSession.time_created <= end)
        .distinct()
    )
    rows = db_session.execute(stmt).all()

    by_day: dict[date, set[str]] = defaultdict(set)
    for user_id, day in rows:
        if day is not None and user_id is not None:
            by_day[day].add(str(user_id))

    return [
        PersonaUniqueUserAnalyticsResponse(
            unique_users=len(user_ids), date=day, persona_id=persona_id
        )
        for day, user_ids in sorted(by_day.items())
    ]
