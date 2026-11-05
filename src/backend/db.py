from contextlib import contextmanager
from typing import Iterator

import pymysql

from backend.config import settings


def get_connection() -> pymysql.connections.Connection:
    return pymysql.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


@contextmanager
def transaction() -> Iterator[pymysql.connections.Connection]:
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
