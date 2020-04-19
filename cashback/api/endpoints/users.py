import logging
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from cashback import crud
from cashback.api.utils.db import get_db
from cashback.api.utils.security import (
    get_current_active_superuser,
    get_current_active_user,
)
from cashback.models.user import User as DBUser
from cashback.schemas.user import User, UserCreate, UserUpdate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/users/", response_model=List[User])
def list_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: DBUser = Depends(get_current_active_superuser),
):
    """
    List users.
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/users/", response_model=User, status_code=201)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: DBUser = Depends(get_current_active_superuser),
):
    """
    Create new user.
    """
    email_user = crud.user.get_by_email(db, email=user_in.email)
    cpf_user = crud.user.get_by_cpf(db, cpf=user_in.cpf)
    if email_user or cpf_user:
        msg = (
            f"The user with this email {email_user} or "
            f"cpf {cpf_user}, already exists in the system."
        )

        logger.debug(msg)
        raise HTTPException(
            status_code=409, detail=msg,
        )

    user = crud.user.create(db, obj_in=user_in)
    logger.info(f"Create user with success! User: {user_in.email}")
    return user


@router.get("/user/profile/", response_model=User)
def get_current_user(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user),
):
    """
    Get current user.
    """
    logger.info(f"Get current user with success.")
    return current_user


@router.put("/user/profile/", response_model=User)
def update_current_user(
    *,
    db: Session = Depends(get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    is_active: bool = Body(None),
    current_user: DBUser = Depends(get_current_active_user),
):
    """
    Update current user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if is_active is not None:
        user_in.is_active = is_active

    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)

    logger.info(f"Update user with success! User: {user_in.email}")
    return user


@router.get("/user/{user_id}/", response_model=User)
def get_user_by_id(
    user_id: int,
    current_user: DBUser = Depends(get_current_active_superuser),
    db: Session = Depends(get_db),
):
    """
    Get a specific user by id.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        msg = f"The user {user_id} does not exist in the system"
        logger.debug(msg)
        raise HTTPException(
            status_code=404, detail=msg,
        )

    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        msg = f"The user {user_id} doesn't have enough privileges"
        logger.debug(msg)
        raise HTTPException(status_code=403, detail=msg)

    return user


@router.put("/user/{user_id}/", response_model=User)
def update_user_by_id(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: DBUser = Depends(get_current_active_superuser),
):
    """
    Update a user.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        msg = f"The user {user_id} not found in the system"
        logger.debug(msg)
        raise HTTPException(
            status_code=404, detail=msg,
        )

    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    logger.info(f"Update user with success! User: {user_in.email}")
    return user
