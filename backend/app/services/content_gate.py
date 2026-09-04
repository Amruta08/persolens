import httpx
from app.core.config import settings

# Youtube's category ID for Music
MUSIC_CATEGORY_ID = "10"

def check_gate(category_id:str, title:str) -> tuple[bool, str | None]:
    if category_id == MUSIC_CATEGORY_ID:
        return False, "Category suggests non-speech content"
    if "asmr" in title.lower():
        return False, "Title suggests non-speech content"
    return True, None

def fetch_video_metadata(video_id: str) -> dict:
    response = httpx.get(
        "https://www.googleapis.com/youtube/v3/videos",
        params = {
            "id":video_id, 
            "part":"snippet,contentDetails", 
            "key":settings.youtube_api_key},
    )
    
    response.raise_for_status()
    item = response.json()["items"][0]
    return {
        "title": item["snippet"]["title"],
        "category_id": item["snippet"]["categoryId"]
    }