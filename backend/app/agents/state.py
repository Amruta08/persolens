from typing import TypedDict

class AnalysisState(TypedDict):
    video_id: str
    transcript_words: list[dict]
    prosody: dict
    candidate_patterns: list[dict]
    verified_patterns: list[dict]
    retry_count: int