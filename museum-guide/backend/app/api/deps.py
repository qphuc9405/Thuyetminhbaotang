from __future__ import annotations

from fastapi import Request
from sqlalchemy.orm import Session

from ..database.database import get_session  # noqa: F401


def app_state(request: Request):
    return request.app.state
