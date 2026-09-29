from difflib import SequenceMatcher

WINDOW_SEC = 8.0
MATCH_THRESHOLD = 0.5

def get_transcript_window(transcript_words: list[dict], timestamp_sec: float) -> str:
    nearby_words = [
        w["word"] for w in transcript_words
        if abs(w["start"] - timestamp_sec) <= WINDOW_SEC   # only words close in time to the claim
    ]
    return " ".join(nearby_words)


def quote_is_supported(pattern: dict, transcript_words: list[dict]) -> bool:
    window_text = get_transcript_window(transcript_words, pattern["timestamp_sec"])
    if not window_text:
        return False
    
    similarity = SequenceMatcher(
        None,
        pattern["quote_or_evidence"].lower(),
        window_text.lower()
    ).ratio()

    return similarity >= MATCH_THRESHOLD


def verify_evidence(state: dict) -> dict:
    candidates = state["candidate_patterns"]
    transcript_words = state["transcript_words"]
    
    verified = [p for p in candidates if quote_is_supported(p, transcript_words)]
    return {"verified_patterns": verified}