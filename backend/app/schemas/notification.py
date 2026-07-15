from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    kind: str
    title: str
    message: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    read_at: Optional[datetime] = None
    created_at: datetime
