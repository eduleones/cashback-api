from cashback import crud
from cashback.core import config
from cashback.schemas.user import UserAdminCreate


def init_db(db_session):
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)

    user = crud.user.get_by_email(
        db_session, email=config.FIRST_SUPERUSER_EMAIL
    )
    if not user:
        user_in = UserAdminCreate(
            email=config.FIRST_SUPERUSER_EMAIL,
            password=config.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.user.create(db_session, obj_in=user_in)
