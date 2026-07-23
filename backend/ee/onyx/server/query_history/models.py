from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict

from onyx.background.task_utils import extract_task_id_from_query_history_report_name
from onyx.configs.constants import MessageType
from onyx.configs.constants import QAFeedbackType
from onyx.configs.constants import SessionType
from onyx.db.enums import TaskStatus
from onyx.db.models import FileRecord
from onyx.db.models import TaskQueueState


class AbridgedSearchDoc(BaseModel):
    document_id: str
    semantic_identifier: str
    link: str | None = None


class MessageSnapshot(BaseModel):
    id: int
    message: str
    message_type: MessageType
    documents: list[AbridgedSearchDoc]
    feedback_type: QAFeedbackType | None = None
    feedback_text: str | None = None
    time_created: datetime


class ChatSessionMinimal(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_email: str | None = None
    name: str | None = None
    first_user_message: str
    first_ai_message: str
    assistant_id: int | None = None
    assistant_name: str | None = None
    time_created: datetime
    feedback_type: QAFeedbackType | None = None
    flow_type: SessionType
    conversation_length: int


class ChatSessionSnapshot(BaseModel):
    id: UUID
    user_email: str | None = None
    name: str | None = None
    messages: list[MessageSnapshot]
    assistant_id: int | None = None
    assistant_name: str | None = None
    time_created: datetime
    flow_type: SessionType


class QueryHistoryExport(BaseModel):
    task_id: str
    status: TaskStatus
    start: datetime
    end: datetime
    start_time: datetime

    @classmethod
    def from_task(cls, task_queue_state: TaskQueueState) -> "QueryHistoryExport":
        start, end = _parse_task_name(task_queue_state.task_name)
        return cls(
            task_id=task_queue_state.task_id,
            status=task_queue_state.status,
            start=start,
            end=end,
            start_time=task_queue_state.start_time or task_queue_state.register_time,
        )

    @classmethod
    def from_file(cls, file: FileRecord) -> "QueryHistoryExport":
        raw_metadata = file.file_metadata
        metadata: dict[str, Any] = (
            {str(key): value for key, value in raw_metadata.items()}
            if isinstance(raw_metadata, dict)
            else {}
        )
        start_raw = metadata.get("start")
        end_raw = metadata.get("end")
        if not isinstance(start_raw, str) or not isinstance(end_raw, str):
            now = datetime.now()
            start = now
            end = now
        else:
            start = datetime.fromisoformat(start_raw)
            end = datetime.fromisoformat(end_raw)
        return cls(
            task_id=extract_task_id_from_query_history_report_name(file.file_id),
            status=TaskStatus.SUCCESS,
            start=start,
            end=end,
            start_time=file.created_at,
        )


def _parse_task_name(task_name: str) -> tuple[datetime, datetime]:
    parts = task_name.split("|", 2)
    if len(parts) == 3:
        return datetime.fromisoformat(parts[1]), datetime.fromisoformat(parts[2])
    now = datetime.now()
    return now, now
