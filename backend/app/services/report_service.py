import json
from datetime, timezone

# Converts raw seconds into MM:SS or H:MM:SS
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


# Turns raw librosa numbers into display-read summary block
def format_vocal_summary(video) -> dict:
    return {
        "speech_ratio": video.speech_ratio,
        "avg_pause_length_sec": video.avg_pause_length_sec,
        "avg_pitch_variation": video.avg_pitch_variation,
    }


# Main assembly function which takes video row and list of verified patterns and returns JSON-ready report
def build_report(video, verified_patterns: list[dict]) -> dict:
    return{
        "video_id": video.video_id,
        "title": video.title,
        "youtube_url": video.youtube_url,
        "generated_at": datetime.now(timezone.utc).isoformat(),  ## when this report was assembled
        "vocal_summary": format_vocal_summary(video),
        "pattern_count": len(verified_patterns),
        "patterns": [format_pattern(p, video.youtube_url) for p in verified_patterns],
    }