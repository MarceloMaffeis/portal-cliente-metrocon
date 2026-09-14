# -*- coding: utf-8 -*-
import sqlite3
import os
from contextlib import contextmanager

DB_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(DB_DIR)
DB_PATH = os.path.join(DB_DIR, 'metrocon_portal.db')
SCHEMA_PATH = os.path.join(DB_DIR, 'schema.sql')

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON;')
    return conn

@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(f'Schema not found: {SCHEMA_PATH}')
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    with get_db() as conn:
        conn.executescript(schema_sql)

def execute_query(query: str, params: tuple = ()) -> list[sqlite3.Row]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

def execute_one(query: str, params: tuple = ()) -> sqlite3.Row | None:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

def execute_insert(query: str, params: tuple = ()) -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.lastrowid

def execute_update(query: str, params: tuple = ()) -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.rowcount
