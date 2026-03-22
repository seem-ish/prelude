"""
Prelude database connection utilities.
Uses psycopg2 with a simple connection factory.
"""

import os
import psycopg2
import psycopg2.extras
from contextlib import contextmanager


def get_db_url():
    url = os.environ.get("PRELUDE_DB_URL", "postgresql://localhost:5432/prelude")
    return url


@contextmanager
def get_conn():
    """Context manager that yields a psycopg2 connection and commits/closes it."""
    conn = psycopg2.connect(get_db_url())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def query(sql, params=None):
    """Run a SELECT query, return list of dicts."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params or ())
            return [dict(row) for row in cur.fetchall()]


def execute(sql, params=None):
    """Run an INSERT/UPDATE/DELETE, return rowcount."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.rowcount


def execute_returning(sql, params=None):
    """Run an INSERT ... RETURNING, return the first row as dict."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params or ())
            return dict(cur.fetchone())
