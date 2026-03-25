from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.config import settings


class GoogleOAuthError(Exception):
    pass


def verify_google_token(token: str) -> dict:
    """Verify Google OAuth ID token and return user info.

    Returns dict with: sub, email, name, picture
    """
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
        if idinfo["iss"] not in ("accounts.google.com", "https://accounts.google.com"):
            raise GoogleOAuthError("Invalid issuer")
        return {
            "sub": idinfo["sub"],
            "email": idinfo["email"],
            "name": idinfo.get("name", ""),
            "picture": idinfo.get("picture", ""),
        }
    except ValueError as e:
        raise GoogleOAuthError(f"Invalid Google token: {e}")
