from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.video import Video
from app.services.audio_download import download_audio
from app.services.transcript_service import transcribe
from app.services.prosody_service import extract_prosody_features
from app.services.content_gate import refine_gate_with_signal

@celery_app.task
def run_extraction(video_id:str):
    db = SessionLocal()
    try:
        video = db.query(Video).filter(Video.video_id == video_id).first()
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
        
        return {"accepted":accepted, "reason":reason}
    finally:
        db.close()