from pydantic import BaseModel
from typing import Literal

class Moment(BaseModel):
    timestamp_sec: float
    quote: str

class CandidatePattern(BaseModel):
    channel: Literal["communication"]
    pattern_name: str
    description: str
    why_it_works: str
    try_it: str
    moments: list[Moment]

class PatternProposals(BaseModel):
    patterns: list[CandidatePattern]