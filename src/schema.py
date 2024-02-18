from sqlmodel import SQLModel, Field
from typing import Optional

import datetime
from enum import Enum


class FileType(Enum):
    AUDIO = "audio"
    TEXT = "text"
    VIDEO = "video"


class Information(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field()
    title: Optional[str] = Field(default="NA", unique=False)
    hash_id: str = Field(unique=True)
    created_at: float = Field(default=datetime.datetime.now().timestamp())
    file_type: FileType
    # cost: Optional[float] = Field(default=0.0)
    text: str = Field(default="")
    embedded: bool = Field(default=False)

    __table_args__ = {"extend_existing": True}
