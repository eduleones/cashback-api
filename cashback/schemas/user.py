from typing import Optional

from pydantic import BaseModel, EmailStr


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    full_name: Optional[str] = None
    cpf: Optional[str] = None


class UserBaseInDB(UserBase):
    id: int = None

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class UserCreate(UserBaseInDB):
    email: EmailStr
    password: str
    full_name: str
    cpf: str


# User Admin
class UserAdminCreate(UserBaseInDB):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


# Properties to receive via API on update
class UserUpdate(UserBaseInDB):
    password: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True


# Additional properties to return via API
class User(UserBaseInDB):
    pass
