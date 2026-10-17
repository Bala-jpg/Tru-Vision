from fastapi import APIRouter, HTTPException, Depends, Header
from app.models.schemas import PreferencesRequest, PreferencesResponse
from app.services.auth_service import AuthService
from typing import Optional

router = APIRouter()
auth_service = AuthService()

def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Validates the bearer token against Supabase.
    Returns user payload or raises 401.
    """
    if not authorization or not authorization.startswith("Bearer "):
        # For mock/local environments where Supabase URL is not yet configured, bypass auth
        if not auth_service.client:
            return {"id": "mock-user", "email": "mock@example.com"}
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    token = authorization.split(" ")[1]
    user = auth_service.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session token")
    return user

@router.get("/preferences", response_model=PreferencesResponse)
async def get_preferences(user: dict = Depends(get_current_user)):
    """
    GET /api/v1/preferences
    Retrieves extension preferences for the logged-in user from Supabase.
    """
    # Initialize default preferences
    default_prefs = {
        "tts_enabled": True,
        "tts_voice": "en-IN-Wavenet-B",
        "tts_speed": 1.0,
        "captions_enabled": True,
        "caption_font_size": "medium",
        "sign_detection_enabled": True,
        "overlay_position": "bottom-right",
        "overlay_opacity": 0.9
    }

    if not auth_service.client:
        return default_prefs

    try:
        # Fetch from Supabase user_preferences table
        response = auth_service.client.table("user_preferences").select("*").eq("user_id", user["id"]).execute()
        if response.data:
            return response.data[0]
        
        # If no settings row exists, insert one
        insert_data = {"user_id": user["id"], **default_prefs}
        auth_service.client.table("user_preferences").insert(insert_data).execute()
        return default_prefs
    except Exception as e:
        print(f"Failed to fetch preferences from Supabase: {e}")
        return default_prefs

@router.put("/preferences", response_model=PreferencesResponse)
async def update_preferences(payload: PreferencesRequest, user: dict = Depends(get_current_user)):
    """
    PUT /api/v1/preferences
    Updates preferences row for the active user.
    """
    update_data = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    
    if not auth_service.client:
        # Return what was updated for testing
        return {
            "tts_enabled": update_data.get("tts_enabled", True),
            "tts_voice": update_data.get("tts_voice", "en-IN-Wavenet-B"),
            "tts_speed": update_data.get("tts_speed", 1.0),
            "captions_enabled": update_data.get("captions_enabled", True),
            "caption_font_size": update_data.get("caption_font_size", "medium"),
            "sign_detection_enabled": update_data.get("sign_detection_enabled", True),
            "overlay_position": update_data.get("overlay_position", "bottom-right"),
            "overlay_opacity": update_data.get("overlay_opacity", 0.9)
        }

    try:
        response = auth_service.client.table("user_preferences").update(update_data).eq("user_id", user["id"]).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=400, detail="Failed to update preferences row")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
