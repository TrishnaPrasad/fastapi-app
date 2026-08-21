from datetime import datetime, timezone

import jwt
from sqlalchemy.orm import Session

from app.core.security import create_access_token, decode_token, create_refresh_token
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


def rotate_refresh_token(
    self,
    db: Session,
    refresh_token,
):
    payload = decode_token(refresh_token)

    if payload.get("type") != "refresh":
        return None

    jti = payload.get("jti")
    user_id = payload.get("sub")

    if not jti or not user_id:
        return None

    stored_token = self.refresh_token_repository.get_by_jti(
        db,
        jti,
    )

    if stored_token is None:
        return None

    if stored_token.revoked_at is not None:
        return None

    now = datetime.now(timezone.utc)

    if stored_token.expires_at <= now:
        return None

    # Revoke the old refresh token first.
    self.refresh_token_repository.revoke(
        db,
        stored_token,
    )

    # Create a new token pair.
    access_token = create_access_token(int(user_id))

    new_refresh_token, new_refresh_record = self.create_refresh_token(
        db=db,
        user_id=int(user_id),
    )

    return (
        access_token,
        new_refresh_token,
        new_refresh_record,
    )
