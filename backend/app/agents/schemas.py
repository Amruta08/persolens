from pydantic import BaseModel
from typing import Literal

class CandidatePattern(BaseModel):
    channel: Literal["communication", "vocal"]
    pattern_name: str
    description: str
    timestamp_sec: float
    quote_or_evidence: str

class PatternProposals(BaseModel):
    patterns: list[CandidatePattern]