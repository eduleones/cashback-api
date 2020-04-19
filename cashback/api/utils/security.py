import logging

import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from sqlalchemy.orm import Session

from cashback import crud
from cashback.api.utils.db import get_db
from cashback.core import config
from cashback.core.jwt import ALGORITHM
from cashback.models.user import User
from cashback.schemas.token import TokenPayload

logger = logging.getLogger(__name__)
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login/access-token/")


def get_current_user(
    db: Session = Depends(get_db), token: str = Security(reusable_oauth2)
):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except PyJWTError:
        error_msg = "Token error - Could not validate credentials"
        logger.error(error_msg)
        raise HTTPException(
            status_code=403, detail=error_msg,
        )
    user = crud.user.get(db, id=token_data.user_id)
    if not user:
        error_msg = "User not found"
        logger.error(error_msg)
        raise HTTPException(status_code=404, detail=error_msg)
    return user


def get_current_active_user(current_user: User = Security(get_current_user)):
    if not crud.user.is_active(current_user):
        error_msg = "Inactive user"
        logger.error(error_msg)
        raise HTTPException(status_code=401, detail=error_msg)
    return current_user


def get_current_active_superuser(
    current_user: User = Security(get_current_user),
):
    if not crud.user.is_superuser(current_user):
        error_msg = "The user doesn't have enough privileges"
        logger.error(error_msg)
        raise HTTPException(status_code=403, detail=error_msg)
    return current_user
