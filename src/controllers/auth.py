from datetime import UTC, datetime, timedelta

import jwt
from litestar import Controller, Response, post, status_codes
from litestar.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models import User
from src.schemas import LogInDTO, SignUpDTO


class AuthController(Controller):
    @post('/signup', dto=SignUpDTO)
    async def sign_up(self, db_session: AsyncSession, data: User) -> Response:
        try:
            data.set_password(data.hashed_password)
            db_session.add(data)
            await db_session.commit()
            await db_session.refresh(data)
        except IntegrityError:
            raise HTTPException(status_code=status_codes.HTTP_400_BAD_REQUEST)

        return Response({'token': self.generate_token({'user_id': data.id})})

    @post('/login', dto=LogInDTO)
    async def log_in(self, db_session: AsyncSession, data: User) -> Response:
        user = (
            await db_session.execute(select(User).filter(User.email == data.email))
        ).scalar_one_or_none()

        if not (user and user.check_password(data.hashed_password)):
            raise HTTPException(
                status_code=status_codes.HTTP_400_BAD_REQUEST, detail='Invalid username or password',
            )

        return Response(
            {'token': self.generate_token({'user_id': user.id})},
            status_code=status_codes.HTTP_200_OK,
        )

    def generate_token(self, payload: dict):
        payload['exp'] = datetime.now(UTC) + timedelta(seconds=settings.jwt_expiration)

        return jwt.encode(payload, settings.secret_key)
