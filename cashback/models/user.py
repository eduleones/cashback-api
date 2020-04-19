import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, Sequence, String
from sqlalchemy.orm import relationship

from cashback.db.base_class import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, Sequence("user_id_seq"), primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String(150), nullable=True)
    cpf = Column(String(20), unique=True, index=True, nullable=True)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    orders = relationship("Order", back_populates="reseller")
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, onupdate=datetime.datetime.now())
