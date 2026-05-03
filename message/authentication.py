import logging
import os

import jwt
from django.conf import settings
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication


class ServiceUser:
    def __init__(self, user_id, role):
        self.id = user_id
        self.role = str(role).lower() if role is not None else None
        self.is_authenticated = True


logger = logging.getLogger(__name__)


class CustomJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header:
            raise exceptions.AuthenticationFailed("Missing Authorization header.")
        if not auth_header.startswith("Bearer "):
            raise exceptions.AuthenticationFailed("Invalid Authorization header format.")

        token = auth_header.split(" ", 1)[1].strip()
        if not token:
            raise exceptions.AuthenticationFailed("Missing token.")

        payload = self._decode_token(token)
        user_id = payload.get("user_id")
        role = payload.get("role")
        if user_id is None or role is None:
            raise exceptions.AuthenticationFailed("Token missing required claims.")

        return ServiceUser(user_id=user_id, role=role), payload

    def _decode_token(self, token):
        expected_issuer = os.getenv("JWT_ISSUER")
        expected_audience = os.getenv("JWT_AUDIENCE")
        public_key = getattr(settings, "JWT_PUBLIC_KEY", None)
        if not public_key:
            raise exceptions.AuthenticationFailed("JWT public key is not configured.")

        try:
            return jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                issuer=expected_issuer if expected_issuer else None,
                audience=expected_audience if expected_audience else None,
                options={"verify_aud": bool(expected_audience)},
            )
        except jwt.ExpiredSignatureError as exc:
            logger.warning("JWT expired: %s", exc)
            raise exceptions.AuthenticationFailed("Token has expired.")
        except jwt.InvalidTokenError as exc:
            raise exceptions.AuthenticationFailed(f"Invalid token: {exc}")
