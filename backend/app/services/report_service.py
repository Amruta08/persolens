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