import json
from datetime import datetime, timezone
from app.services.vocal_patterns import build_vocal_patterns

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

# Reads measured vocal numbers saved during extraction
def local_vocal_metrics(video) -> dict:
    if not video.vocal_json:
        return {}
    return json.loads(video.vocal_json)


# Turns raw librosa numbers into display-read summary block
def format_vocal_summary(video) -> dict:
    return {
        "speech_ratio": video.speech_ratio,
        "speech_seconds": metrics.get("speech_seconds"),
        "silent_seconds": metrics.get("silent_seconds"),
        "words_per_min": metrics.get("words_per_min"),
        "pauses_per_min": metrics.get("pauses_per_min"),
        "pitch_variation_semitones": metrics.get("pitch_variation_semitones"),
    }


# Main assembly function which takes video row and list of verified patterns and returns JSON-ready report
def build_report(video, verified_patterns: list[dict]) -> dict:

    # Speech patterns from llm
    speech_patterns = []
    for p in verified_patterns:
        if p["channel"] == "communication":
            speech_patterns.append(format_pattern(p, video.youtube_url))
    
    # vocal patterns built from measurements
    vocal_patterns = build_vocal_patterns(load_vocal_metrics(video), video.youtube_url)

    all_patterns = speech_patterns + vocal_patterns


    return{
        "video_id": video.video_id,
        "title": video.title,
        "youtube_url": video.youtube_url,
        "generated_at": datetime.now(timezone.utc).isoformat(),  ## when this report was assembled
        "vocal_summary": format_vocal_summary(video),
        "pattern_count": len(verified_patterns),
        "patterns": all_patterns,
    }