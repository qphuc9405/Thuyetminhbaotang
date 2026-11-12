from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from ..config import get_settings


class Base(DeclarativeBase):
    pass


_engine = None
_Session = None


def get_engine(url: str | None = None):
    global _engine, _Session
    if _engine is None or url:
        u = url or get_settings().database_url
        kw = {"connect_args": {"check_same_thread": False}} if u.startswith("sqlite") else {}
        _engine = create_engine(u, future=True, **kw)
        if u.startswith("sqlite"):
            @event.listens_for(_engine, "connect")
            def _fk(dbapi_con, _):  # noqa: ANN001
                dbapi_con.execute("PRAGMA foreign_keys=ON")
        _Session = sessionmaker(bind=_engine, expire_on_commit=False, future=True)
    return _engine


def init_db(url: str | None = None) -> None:
    from . import models  # noqa: F401  (đăng ký bảng)
    Base.metadata.create_all(get_engine(url))


def get_session() -> Iterator[Session]:
    get_engine()
    s = _Session()
    try:
        yield s
    finally:
        s.close()


@contextmanager
def session_scope() -> Iterator[Session]:
    get_engine()
    s = _Session()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()
