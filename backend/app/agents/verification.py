import re
from difflib import SequenceMatcher

WINDOW_SEC = 8.0
MATCH_THRESHOLD = 0.7
MIN_QUOTE_WORDS = 3
MAX_MOMENTS = 3

# Strips punctuation and reduces it to lowercase
def to_words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


# Real words whisper heard near a timestamp
def get_window(transcript_words: list[dict], timestamp_sec: float) -> list[dict]:
    window = []

    for w in transcript_words:
        if abs(w["start"] - timestamp_sec) <= WINDOW_SEC:
            for token in to_words(w["word"]):
                window.append({"word": token, "start": w["start"]})
    
    return window


# Check one quote against the transcript
def check_quote(quote: str, timestamp_sec: float, transcript_words: list[dict]) -> tuple[float, float]:
    quote_words = to_words(quote)
    window = get_window(transcript_words, timestamp_sec)
    if len(quote_words) < MIN_QUOTE_WORDS or not window:
        return 0.0, timestamp_sec
    
    window_words = [w["word"] for w in window]
    matcher = SequenceMatcher(None, quote_words, window_words, autojunk=False)

    matched = 0
    first_start = None
    for block in matcher.get_matching_blocks():
        if block.size < 2:
            continue
        matched += block.size
        if first_start is None:
            first_start = window[block.b]["start"]
    
    if first_start is None:
        return 0.0, timestamp_sec
    return matched / len(quote_words), first_start


# Keep moments of one pattern that really appear in transcript
def verify_moments(moments: list[dict], transcript_words: list[dict]) -> list[dict]:
    kept = []
    for m in moments:
        match, start_sec = check_quote(m["quote"], m["timestamp_sec"], transcript_words)
        if match >= MATCH_THRESHOLD:
            kept.append({"timestamp_sec": start_sec, "quote": m["quote"], "match": round(match, 2)})
    kept.sort(key=lambda m: m["timestamp_sec"])
    return kept[:MAX_MOMENTS]


# Pattern survives if at least one of its moments checks out
def verify_evidence(state: dict) -> dict:
    transcript_words = state["transcript_words"]
    verified = []

    for p in state["candidate_patterns"]:
        moments = verify_moments(p["moments"], transcript_words)
        if moments:
            verified.append({**p, "moments": moments})

    return {"verified_patterns": verified}



# def get_transcript_window(transcript_words: list[dict], timestamp_sec: float) -> str:
#     nearby_words = [
#         w["word"] for w in transcript_words
#         if abs(w["start"] - timestamp_sec) <= WINDOW_SEC   # only words close in time to the claim
#     ]
#     return " ".join(nearby_words)


# def quote_is_supported(pattern: dict, transcript_words: list[dict]) -> bool:
#     window_text = get_transcript_window(transcript_words, pattern["timestamp_sec"])
#     if not window_text:
#         return False
    
#     similarity = SequenceMatcher(
#         None,
#         pattern["quote_or_evidence"].lower(),
#         window_text.lower()
#     ).ratio()

#     return similarity >= MATCH_THRESHOLD


