from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime, timezone
from app.core.database import Base

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    youtube_url = Column(String, nullable=False)
    video_id = Column(String, nullable=False, index=True)
    title = Column(String)
    category_id = Column(String)
    duration_sec = Column(Float)
    transcript_json = Column(Text, nullable=True)
    speech_ratio = Column(Float, nullable=True)
    avg_pause_length_sec = Column(Float, nullable=True)
    avg_pitch_variation = Column(Float, nullable=True)
    gate_accepted = Column(String)
    gate_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))