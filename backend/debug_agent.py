"""
Shows what the Pattern Agent proposed, and how each proposal scored in verification.

Usage (from backend/):
    uv run python debug_agent.py VIDEO_ID

Costs one GPT-4o call (two if the graph retries).
"""
import sys
from difflib import SequenceMatcher

from app.core.database import SessionLocal
from app.models.video import Video
from app.agents.runner import load_transcript
from app.agents.pattern_agent import pattern_graph
from app.agents.verification import get_transcript_window, MATCH_THRESHOLD

video_id = sys.argv[1]  # the YouTube video id you ingested, e.g. dQw4w9WgXcQ

db = SessionLocal()
video = db.query(Video).filter(Video.video_id == video_id).first()
if video is None or video.transcript_json is None:
    sys.exit("That video isn't in the DB, or has no transcript yet (run extraction first).")

words = load_transcript(video.transcript_json)["words"]

# Same starting state the real runner builds (Chapter 8, Step 4)
state = {
    "video_id": video_id,
    "transcript_words": words,
    "prosody": {
        "speech_ratio": video.speech_ratio,
        "avg_pause_length_sec": video.avg_pause_length_sec,
        "avg_pitch_variation": video.avg_pitch_variation,
    },
    "candidate_patterns": [],
    "verified_patterns": [],
    "retry_count": 0,
}

out = pattern_graph.invoke(state)

print(f"\nretries used: {out['retry_count']}")
print(f"proposed (last attempt): {len(out['candidate_patterns'])}   verified: {len(out['verified_patterns'])}\n")

# Re-score each proposal the same way verify_evidence did, so you can SEE why it passed or failed
for p in out["candidate_patterns"]:
    window = get_transcript_window(words, p["timestamp_sec"])
    score = SequenceMatcher(None, p["quote_or_evidence"].lower(), window.lower()).ratio()
    verdict = "KEPT   " if score >= MATCH_THRESHOLD else "DROPPED"
    print(f"{verdict} score={score:.2f} @ {p['timestamp_sec']:.0f}s  [{p['channel']}] {p['pattern_name']}")
    print(f"         quote: {p['quote_or_evidence']}\n")

db.close()
