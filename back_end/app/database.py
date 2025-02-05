from math import ceil

from sqlalchemy import event
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, create_engine
from sqlmodel.sql.expression import Select, SelectOfScalar

from app.log_config import logger

from .config import DATABASE_URL, LOG_LEVEL

if DATABASE_URL is None:
    raise Exception("Database url not found, check .env")


# * Pool settings
POOL_SIZE = 20

# ? Allows up to 30 connections (20 pool + 10 overflow)
MAX_OVERFLOW = 10
# ? Wait up to 10 seconds for a connection
POOL_TIMEOUT = 10
# ? Recycle connections after 30 minutes
POOL_RECYCLE = 1800

engine = create_engine(
    url=DATABASE_URL,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE,
    pool_pre_ping=True,
    connect_args={"options": "-c statement_timeout=5000"},
    # Uncomment to see SQL queries for debugging
    # echo=True,
)

logger.setLevel(level=LOG_LEVEL)


# * Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)


def get_pool_stats(pool):
    return {"pool_size": pool.size(), "checked_out": pool.checkedout(), "overflow": pool.overflow()}


@event.listens_for(engine, "connect")
def on_connect(db_api_connection, connection_record):  # noqa: ARG001
    stats = get_pool_stats(engine.pool)
    logger.debug(f"New connection established. " f"Pool size: {stats['pool_size']}, " f"Checked out: {stats['checked_out']}, " f"Overflow: {stats['overflow']}.")


@event.listens_for(engine, "checkout")
def on_checkout(db_api_connection, connection_record, connection_proxy):  # noqa: ARG001
    stats = get_pool_stats(engine.pool)
    logger.debug(f"Connection checked out from pool. " f"Pool size: {stats['pool_size']}, " f"Checked out: {stats['checked_out']}, " f"Overflow: {stats['overflow']}.")


@event.listens_for(engine, "checkin")
def on_checkin(db_api_connection, connection_record):  # noqa: ARG001
    stats = get_pool_stats(engine.pool)
    logger.debug(f"Connection returned to pool. " f"Pool size: {stats['pool_size']}, " f"Checked out: {stats['checked_out']}, " f"Overflow: {stats['overflow']}.")


class Page:
    def __init__(self, contents, page, page_size, total):
        self.contents = contents
        self.previous_page = None
        self.next_page = None
        self.has_previous = page > 1
        if self.has_previous:
            self.previous_page = page - 1
        previous_items = (page - 1) * page_size
        self.has_next = previous_items + len(contents) < total
        if self.has_next:
            self.next_page = page + 1
        self.total = total
        self.pages = int(ceil(total / float(page_size)))

    def to_dict(self):
        return {
            "contents": self.contents,
            "previous_page": self.previous_page,
            "next_page": self.next_page,
            "has_previous": self.has_previous,
            "has_next": self.has_next,
            "total": self.total,
            "pages": self.pages,
        }


def paginate(session: Session, query: Select | SelectOfScalar, page: int, page_size: int):
    if page <= 0:
        raise AttributeError("page needs to be >= 1")
    if page_size <= 0:
        raise AttributeError("page_size needs to be >= 1")

    # todo find better solution or run raw sql
    total: int = len(session.exec(query).all())
    result = list(session.exec(statement=query.limit(page_size).offset((page - 1) * page_size)).all())

    return Page(result, page, page_size, total)
