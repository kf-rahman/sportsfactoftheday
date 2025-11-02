from pydantic import BaseModel, EmailStr, Field
from typing import List, Literal

Sport = Literal["nba", "mlb", "nhl"]

class SubscribeIn(BaseModel):
    email: EmailStr
    sports: List[Sport] = Field(default_factory=list)

class SubscribeOut(BaseModel):
    ok: bool
    message: str
