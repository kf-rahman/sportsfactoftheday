from typing import List, Literal
from pydantic import BaseModel, EmailStr, Field

Sport = Literal["nba", "mlb", "nhl"]

class SubscribeIn(BaseModel):
    email: EmailStr
    sports: List[Sport] = Field(default_factory=list)

class SubscribeOut(BaseModel):
    ok: bool
    message: str
    email_sent: bool = False
