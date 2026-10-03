import json
from fastapi import FastAPI, Depends, HTTPException
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
from app.tasks import run_extraction
from app.services.cache_service import get_cached_report, cache_report
from app.core.celery_app import celery_app
from celery.result import AsyncResult
from app.services.report_service import build_report
from app.services.cache_service import get_cached_report, cache_report
from app.core.auth import get_current_user
from app.services.rate_limit import check_rate_limit
from app.services.quota_service import check_and_increment_quota
from app.models.user import User


app = FastAPI(title=settings.app_name)

def extract_video_id(youtube_url: str) -> str:
    parsed = urlparse(youtube_url)
    return parse_qs(parsed.query)["v"][0]

@app.get("/health")
def health_check():
    return {"status":"ok", "environment":settings.environment}

@app.post("/videos/ingest")
def ingest_video(youtube_url:str, db:Session=Depends(get_db), current_user: User = Depends(get_current_user)):
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
def extract_video(video_id: str, db:Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    check_rate_limit(current_user.id, "extract", max_requests=5, window_seconds=60)
    check_and_increment_quota(current_user, db)

    cached = get_cached_report(video_id)
    if cached:
        return {"status": "cached", "result": cached}

    task = run_extraction.delay(video_id)
    return {"status": "queued", "job_id": task.id}

@app.get("/videos/{video_id}/report")
def get_report(video_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Return already cached report is exists
    cached = get_cached_report(video_id)
    if cached:
        return cached

    # Default path if not cached
    video = db.query(Video).filter(Video.video_id == video_id).first()
    if video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.patterns_json is None:
        raise HTTPException(status_code=404, detail="Report not available for this video yet")
    
    verified_patterns = json.loads(video.patterns_json)
    report = build_report(video, verified_patterns)

    cache_report(video_id, report)
    return report



@app.get("/jobs/{job_id}")
def job_status(job_id: str):
    result = AsyncResult(job_id, app=celery_app)
    if result.ready() and result.successful():
        cache_report(job_id, result.result)
    return {"status": result.status, "result": result.result if result.ready() else None}