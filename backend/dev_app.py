"""
LOCAL DEVELOPMENT ONLY. Never deploy this file.

Runs your real app, but replaces Clerk login with a fixed local test user,
so /docs works without a token:

    uv run uvicorn dev_app:app --reload

Your real code in app/main.py is untouched. Rate limiting and quotas still apply
(to the user 'dev_local_user').
"""
from datetime import datetime, timezone
from fastapi import Depends
from sqlalchemy.orm import Session

from app.main import app
from app.core.auth import get_current_user, next_month_start
from app.core.database import get_db
from app.models.user import User


def local_dev_user(db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.clerk_user_id == "dev_local_user").first()
    if user is None:
        user = User(
            clerk_user_id="dev_local_user",
            plan="free",
            monthly_quota=1000,
            requests_this_month=0,
            quota_reset_at=next_month_start(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


app.dependency_overrides[get_current_user] = local_dev_user
