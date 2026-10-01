import jwt
from jwt import PyJWKClient
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

_jwks_client = PyJWKClient(settings.clerk_jwks_url)

# Verifies raw jwt string is signed by clerk and not expired and returns the decoded payload
def verify_clerk_token(token: str) -> dict:
    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],          
            options={"verify_aud": False},  ## PersonaLens doesn't use Clerk's "audience" feature yet
        )
        return payload
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from e


# Pulls Authorization header off the request, verifies it and returns Clerk user ID
def get_current_clerk_id(authorization: str = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")
    
    token = authorization.removeprefix("Bearer ").strip()
    payload = verify_clerk_token(token)
    return payload["sub"]

# Turns verfied clerk ID into a real user row in our database
def get_current_user(clerk_id: str = Depends(get_current_clerk_id), db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.clerk_user_id == clerk_id).first()

    if user is None:
        user = User(
            clerk_user_id=clerk_id,
            plan="free",
            monthly_quota=20,                         
            requests_this_month=0,
            quota_reset_at=next_month_start(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user

# Reset monthly counter
def next_month_start(from_dt: datetime | None = None) -> datetime:
    dt = from_dt or datetime.now(timezone.utc)
    if dt.month == 12:
        return dt.replace(year=dt.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    return dt.replace(month=dt.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)

