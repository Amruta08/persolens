from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.core.database import Base

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    youtube_url = Column(String, nullable=False)
    video_id = Column(String, nullable=False, index=True)
    title = Column(String)
    category_id = Column(String)
    duration_sec = Column(Float)
    gate_accepted = Column(String)
    gate_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)