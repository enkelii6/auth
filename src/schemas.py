from litestar.plugins.sqlalchemy import SQLAlchemyDTO, SQLAlchemyDTOConfig

from src.models import User


class SignUpDTO(SQLAlchemyDTO[User]):
    config = SQLAlchemyDTOConfig(exclude={'id'}, rename_fields={'hashed_password': 'password'})


class LogInDTO(SQLAlchemyDTO[User]):
    config = SQLAlchemyDTOConfig(exclude={'id', 'username'}, rename_fields={'hashed_password': 'password'})
