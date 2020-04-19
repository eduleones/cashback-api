import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from cashback import crud
from cashback.api.utils.db import get_db
from cashback.api.utils.security import get_current_user
from cashback.core import config
from cashback.core.jwt import create_access_token
from cashback.models.user import User as DBUser
from cashback.schemas.token import Token
from cashback.schemas.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/login/access-token/", response_model=Token)
def get_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=401, detail="Incorrect username or password"
        )
    if not crud.user.is_active(user):
        raise HTTPException(status_code=403, detail="Inactive user")
    access_token_expires = timedelta(
        minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    logger.info(f"User {form_data.username} has logged in successfully.")
    return {
        "access_token": create_access_token(
            data={"user_id": user.id}, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/login/test-token/", response_model=User, status_code=200)
def test_token(current_user: DBUser = Depends(get_current_user)):
    """
    Test access token
    """
    return {"test-token": "ok"}
