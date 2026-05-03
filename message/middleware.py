import os
from functools import lru_cache
from urllib.parse import parse_qs

import jwt
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

MESSAGE_APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@lru_cache(maxsize=1)
def _get_public_key_pem() -> str:
    """Load PEM once; path comes from JWT_PUBLIC_KEY_PATH (compose volume)."""
    path = os.environ.get(
        "JWT_PUBLIC_KEY_PATH",
        os.path.join(MESSAGE_APP_ROOT, "jwt_key", "public.pem"),
    )
    with open(path, encoding="utf-8") as f:
        return f.read()


class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        scope["user"] = AnonymousUser()

        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token")

        if not token:
            return await self.app(scope, receive, send)

        try:
            public_key = _get_public_key_pem()
            payload = jwt.decode(
                token[0],
                public_key,
                algorithms=["RS256"],
                options={"verify_aud": False},
            )
            user_id = payload.get("user_id")
            if user_id:
                user = await self.get_user(user_id)
                scope["user"] = user
        except jwt.ExpiredSignatureError:
            pass
        except jwt.InvalidTokenError:
            pass
        except OSError:
            pass

        return await self.app(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()
