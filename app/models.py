from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, UniqueConstraint

class Subscriber(SQLModel, table=True):
    __tablename__ = "subscribers"
    __table_args__ = (UniqueConstraint("email"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    nba: bool = Field(default=False)
    mlb: bool = Field(default=False)
    nhl: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
