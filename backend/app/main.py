from fastapi import FastAPI, Depends
from app.core.config import settings
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.video import Video
from app.services.content_gate import fetch_video_metadata, check_gate
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