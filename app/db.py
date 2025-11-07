from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class Subscriber(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    nba: bool = Field(default=False)
    mlb: bool = Field(default=False)
    nhl: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
