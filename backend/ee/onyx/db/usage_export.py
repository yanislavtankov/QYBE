from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class UsageReportMetadata(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    report_name: str
    requestor: str | None = None
    time_created: datetime
    period_from: datetime | None = None
    period_to: datetime | None = None
