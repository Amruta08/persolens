import json
from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.video import Video
from app.services.audio_download import download_audio
from app.services.transcript_service import transcribe
from app.services.prosody_service import extract_prosody_features, compute_pace
from app.services.content_gate import refine_gate_with_signal
from app.agents.runner import run_pattern_agent_for_video
from app.services.report_service import build_report
from app.services.cache_service import cache_report

# Stages of extraction
STEPS = [
    ("Downloading the audio", 5),
    ("Transcribing the speech", 20),
    ("Measuring the voice", 40),
    ("Finding speaking patterns", 70),
    ("Building the report", 95),
]

# Tells celery this job is stage number step_number
def report_progress(task, step_number:int) -> None:
    label, percent = STEPS[step_number - 1]
    task.update_state(
        state="PROGRESS",
        meta={
            "step": label,
            "step_number": step_number,
            "total_steps": len(STEPS),
            "percent": percent,
        },
    )

@celery_app.task
def run_extraction(video_id:str):
    db = SessionLocal()
    try:
        video = db.query(Video).filter(Video.video_id == video_id).first()

        report_progress(self, 1)
        audio_path = download_audio(video.youtube_url)

        report_progress(self, 2)
        transcript = transcribe(audio_path)

        report_progress(self, 3)
        prosody = extract_prosody_features(audio_path)

        pace = compute_pace(transcript["words"])
        accepted, reason = refine_gate_with_signal(transcript["text"], prosody["speech_ratio"])
        
        video.transcript_json = json.dumps(transcript)
        video.speech_ratio = prosody["speech_ratio"]
        video.avg_pause_length_sec = prosody["avg_pause_length_sec"]
        video.avg_pitch_variation = prosody["pitch_variation_semitones"]
        video.duration_sec = prosody["total_duration_sec"]
        video.vocal_json = json.dumps({**prosody, **pace}) 
        video.gate_accepted = "accepted" if accepted else "rejected"
        video.gate_reason = reason
        db.commit()

        if not accepted:
            return {"accepted":False, "reason":reason, "pattern_count":0}
        
        report_progress(self, 4)
        verified_patterns = run_pattern_agent_for_video(video_id)

        report_progress(self, 5)
        report = build_report(video, verified_patterns)
        video.patterns_json = json.dumps(verified_patterns)
        db.commit()

        cache_report(video_id, report)

        return {"accepted":True, "reason":reason, "pattern_count": len(verified_patterns)}
    finally:
        db.close()