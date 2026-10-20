from typing import Any

from app.config import settings

try:
    from supabase import Client, create_client
except ImportError:
    create_client = None
    Client = Any


class AuthService:
    def __init__(self):
        self._client: Client | None = None
        if create_client and settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY:
            try:
                self._client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
            except Exception as e:
                print(f"Supabase client initialization failed: {e}")

    @property
    def client(self) -> Client | None:
        return self._client

    def verify_token(self, token: str) -> dict | None:
        """
        Verifies a user token/JWT sent from the extension.
        Returns user info if valid, else None.
        """
        if not self.client:
            # Under mock environment, bypass validation for testing
            return {"id": "mock-user-id", "email": "mock@truvision.com"}

        try:
            user_response = self.client.auth.get_user(token)
            if user_response and user_response.user:
                return {"id": user_response.user.id, "email": user_response.user.email}
        except Exception as e:
            print(f"Token verification failed: {e}")
        return None
