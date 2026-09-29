import json
import ast
from app.core.database import SessionLocal
from app.models.video import Video
from app.agents.pattern_agent import pattern_graph

def load_transcript(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return ast.literal_eval(raw)

def run_pattern_agent_for_video(video_id:str) -> list[dict]:
    db = SessionLocal()
    try:
        video = db.query(Video).filter(Video.video_id == video_id).first()
        if video is None:
            raise ValueError(f"No video found with video_id={video_id}")
        if video.transcript_json is None:
            raise ValueError("This video has no transcript yet")
        
        transcript = load_transcript(video.transcript_json)
        
        # Build the starting state
        initial_state = {
            "video_id": video_id,
            "transcript_words": transcript["words"],
            "prosody": {
                "speech_ratio": video.speech_ratio,
                "avg_pause_length_sec": video.avg_pause_length_sec,
                "avg_pitch_variation": video.avg_pitch_variation,
            },
            "candidate_patterns": [],  
            "verified_patterns": [],
            "retry_count": 0,
            
        }
        
        result_state = pattern_graph.invoke(initial_state)
        return result_state["candidate_patterns"]
    finally:
        db.close()