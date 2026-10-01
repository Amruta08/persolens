from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    clerk_user_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, nullable=True)     
    plan = Column(String, default="free", nullable=False)
    monthly_quota = Column(Integer, default=20, nullable=False)
    requests_this_month = Column(Integer, default=0, nullable=False)
    quota_reset_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))