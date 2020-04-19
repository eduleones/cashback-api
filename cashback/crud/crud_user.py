import logging
from typing import Optional

from sqlalchemy.orm import Session

from cashback.core.security import get_password_hash, verify_password
from cashback.crud.base import CRUDBase
from cashback.crud.utils import normalize_cpf
from cashback.models.user import User
from cashback.schemas.user import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


# pylint: disable=redefined-outer-name
class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(
        self, db_session: Session, *, email: str
    ) -> Optional[User]:
        return db_session.query(User).filter(User.email == email).first()

    def get_by_cpf(self, db_session: Session, *, cpf: str) -> Optional[User]:
        cpf = normalize_cpf(cpf)
        return db_session.query(User).filter(User.cpf == cpf).first()

    def create(self, db_session: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            cpf=normalize_cpf(obj_in.cpf),
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )
        try:
            db_session.add(db_obj)
            db_session.commit()
            db_session.refresh(db_obj)
            return db_obj
        except Exception as err:
            logger.error(f"DB Rollback in CRUDUser create: {err}")
            db_session.rollback()
            raise

    def authenticate(
        self, db_session: Session, *, email: str, password: str
    ) -> Optional[User]:
        user = self.get_by_email(db_session, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser


user = CRUDUser(User)
