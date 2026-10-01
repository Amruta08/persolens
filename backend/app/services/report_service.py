import json
from datetime, timezone

def format_timestamp(seconds: float) -> str:
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"   ## e.g. "1:04:32" for videos over an hour
    return f"{minutes:02d}:{secs:02d}"


# Builds youtube URL that jumps straight to given moment
def build_deep_link(youtube_url:str, timestamp_sec:float) -> str:
    separator = "&" if "?" in youtube_url else "?"
    return f"{youtube_url}{separator}t={int(timestamp_sec)}s"


# Turns one verified pattern into display-ready shape the extension wants
def format_pattern(pattern: dict, youtube_url: str) -> dict:
    return {
        "channel": pattern["channel"],
        "pattern_name": pattern["pattern_name"],
        "description": pattern["description"],
        "quote_or_evidence": pattern["quote_or_evidence"],
        "timestamp_sec": pattern["timestamp_sec"],
        "timestamp_label": format_timestamp(pattern["timestamp_sec"]),
        "deep_link": build_deep_link(youtube_url, pattern["timestamp_sec"]),
    }