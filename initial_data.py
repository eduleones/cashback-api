import logging

from cashback.db.init_db import init_db
from cashback.db.session import db_session

logger = logging.getLogger(__name__)


def init():
    init_db(db_session)


def main():
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
