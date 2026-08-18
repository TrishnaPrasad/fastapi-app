from datetime import datetime, timezone

import jwt
from sqlalchemy.orm import Session

from app.core.security import decode_token, create_refresh_token
from app.repositories.refresh_token_repository import RefreshTokenRepository


class RefreshTokenService:

    def __init__(self):
        self.refresh_token_repository = RefreshTokenRepository()

    def create_refresh_token(
        self,
        db: Session,
        user_id: int,
    ):
        token = create_refresh_token(user_id)

        payload = decode_token(token)

        jti = payload["jti"]

        expires_at = datetime.fromtimestamp(
            payload["exp"],
            tz=timezone.utc,
        )

        refresh_token = self.refresh_token_repository.create(
            db=db,
            user_id=user_id,
            jti=jti,
            expires_at=expires_at,
        )

        return token, refresh_token

    def validate_refresh_token(
        self,
        db: Session,
        token: str,
    ):
        try:
            payload = decode_token(token)

        except jwt.PyJWTError:
            return None

        if payload.get("type") != "refresh":
            return None

        jti = payload.get("jti")

        if not jti:
            return None

        refresh_token = self.refresh_token_repository.get_by_jti(
            db,
            jti,
        )

        if refresh_token is None:
            return None

        if refresh_token.revoked_at is not None:
            return None

        if refresh_token.expires_at <= datetime.now(timezone.utc):
            return None

        return payload, refresh_token

    def revoke_refresh_token(
        self,
        db: Session,
        refresh_token,
    ):
        return self.refresh_token_repository.revoke(
            db,
            refresh_token,
        )
