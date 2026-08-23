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
        refresh_token: str,
    ):
        print("=== ROTATE REFRESH TOKEN ===")

        try:
            payload = decode_token(refresh_token)
            print("REFRESH PAYLOAD:", payload)

        except jwt.ExpiredSignatureError:
            print("REFRESH TOKEN JWT EXPIRED")
            return None

        except jwt.PyJWTError as exc:
            print(
                "REFRESH TOKEN JWT INVALID:",
                type(exc).__name__,
                exc,
            )
            return None

        if payload.get("type") != "refresh":
            print("WRONG TOKEN TYPE:", payload.get("type"))
            return None

        jti = payload.get("jti")
        user_id = payload.get("sub")

        print("REFRESH JTI:", jti)
        print("REFRESH USER ID:", user_id)

        if not jti or not user_id:
            print("MISSING JTI OR USER ID")
            return None

        stored_token = self.refresh_token_repository.get_by_jti(
            db,
            jti,
        )

        print("DB REFRESH TOKEN:", stored_token)

        if stored_token is None:
            print("NO REFRESH TOKEN RECORD FOUND")
            return None

        if stored_token.revoked_at is not None:
            print("REFRESH TOKEN ALREADY REVOKED")
            return None

        now = datetime.now(timezone.utc)

        db_expires_at = self._as_utc(stored_token.expires_at)

        if db_expires_at <= now:
            return None

        print("NOW:", now)
        print("DB EXPIRES:", db_expires_at)

        if db_expires_at <= now:
            print("DB REFRESH TOKEN EXPIRED")
            return None

        print("REFRESH TOKEN VALID")

        self.refresh_token_repository.revoke(
            db,
            stored_token,
        )

        access_token = create_access_token(int(user_id))

        new_refresh_token, new_refresh_record = self.create_refresh_token(
            db=db,
            user_id=int(user_id),
        )

        print("OLD REFRESH TOKEN REVOKED")
        print("NEW ACCESS TOKEN CREATED")
        print("NEW REFRESH TOKEN CREATED")
        print("NEW REFRESH DB ID:", new_refresh_record.id)

        return (
            access_token,
            new_refresh_token,
            new_refresh_record,
        )

    def _as_utc(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)

    def revoke_by_token(
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

        stored_token = self.refresh_token_repository.get_by_jti(
            db,
            jti,
        )

        if stored_token is None:
            return None

        if stored_token.revoked_at is not None:
            return stored_token

        return self.refresh_token_repository.revoke(
            db,
            stored_token,
        )
