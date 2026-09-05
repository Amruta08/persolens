from fastapi import FastAPI, Depends
from app.core.config import settings
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.video import Video
from app.services.content_gate import fetch_video_metadata, check_gate
from app.services.audio_download import download_audio
from app.services.transcript_service import transcribe
from app.services.prosody_service import extract_prosody_features
from app.services.content_gate import refine_gate_with_signal
from urllib.parse import urlparse, parse_qs

app = FastAPI(title=settings.app_name)

def extract_video_id(youtube_url: str) -> str:
    parsed = urlparse(youtube_url)
    return parse_qs(parsed.query)["v"][0]

@app.get("/health")
def health_check():
    return {"status":"ok", "environment":settings.environment}

@app.post("/videos/ingest")
def ingest_video(youtube_url:str, db:Session=Depends(get_db)):
    video_id = extract_video_id(youtube_url)
    metadata = fetch_video_metadata(video_id)
    accepted, reason = check_gate(metadata["category_id"], metadata["title"])
    
    video = Video(
        youtube_url=youtube_url,
        video_id=video_id,
        title=metadata["title"],
        category_id=metadata["category_id"],
        gate_accepted = "accepted" if accepted else "rejected",
        gate_reason=reason,
    )
    
    db.add(video)
    db.commit()
    db.refresh(video)
    
    return {
        "video_id":video.video_id,
        "accepted":accepted,
        "reason":reason
        }

@app.post("/videos/{video_id}/extract")
def extract_video(video_id: str, db:Session = Depends(get_db)):
    video = db.query(Video).filter(Video.video_id == video_id).first()
    if not video or video.gate_accepted != "accepted":
        return {"error": "Video not found or did not pass the initial gate"}
    
    audio_path = download_audio(video.youtube_url)
    transcript = transcribe(audio_path)
    prosody = extract_prosody_features(audio_path)
    
    accepted, reason = refine_gate_with_signal(transcript["text"], prosody["speech_ratio"])
    
    video.transcript_json = str(transcript)
    video.speech_ratio = prosody["speech_ratio"]
    video.avg_pause_length_sec = prosody["avg_pause_length_sec"]
    video.avg_pitch_variation = prosody["avg_pitch_variation"]
    video.gate_accepted = "accepted" if accepted else "rejected"
    video.gate_reason = reason
    db.commit()
    
    return {"accepted": accepted, "reason": reason, "word_count": len(transcript["words"]), "prosody": prosody}
    
    