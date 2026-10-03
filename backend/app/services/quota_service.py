from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.core.auth import next_month_start

# Checks whether a user still has quota left and resets counter if a new month has started since their last request
def check_and_increment_quota(user: User, db: Session) -> None:
    now = datetime.now(timezone.utc)

    if now >= user.quota_reset_at:
        user.requests_this_month = 0
        user.quota_reset_at = next_month_start(now)
    
    if user.requests_this_month >= user.monthly_quota:
        db.commit()
        raise HTTPException(
            status_code=403,
            detail=f"Monthly quota of {user.monthly_quota} extractions reached. Resets {user.quota_reset_at.isoformat()}.",
        )
    
    user.requests_this_month += 1
    db.commit()
