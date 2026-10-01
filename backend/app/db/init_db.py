from app.db.database import Base, engine
from app.db import models
import logging


logger = logging.getLogger(__name__)


def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")


if __name__ == "__main__":
    init_db()
