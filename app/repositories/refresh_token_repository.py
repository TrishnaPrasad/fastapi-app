from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:

    def create(
        self,
        db: Session,
        user_id: int,
        jti: str,
        expires_at: datetime,
    ):
        refresh_token = RefreshToken(
            user_id=user_id,
            jti=jti,
            expires_at=expires_at,
        )

        db.add(refresh_token)
        db.commit()
        db.refresh(refresh_token)

        return refresh_token

    def get_by_jti(
        self,
        db: Session,
        jti: str,
    ):
        return db.query(RefreshToken).filter(RefreshToken.jti == jti).first()

    def revoke(
        self,
        db: Session,
        refresh_token: RefreshToken,
    ):
        refresh_token.revoked_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(refresh_token)

        return refresh_token
