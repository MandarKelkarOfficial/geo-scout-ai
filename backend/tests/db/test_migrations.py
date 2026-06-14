import os
import tempfile
import pytest
import sqlite3
from alembic.config import Config
from alembic import command
from app.core.config import get_settings

@pytest.fixture
def temp_db_url():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    # Store old url
    old_url = get_settings().DATABASE_URL
    
    # Alembic env.py reads get_settings().DATABASE_URL, so we must mock it.
    get_settings().DATABASE_URL = f"sqlite+aiosqlite:///{path}"
    
    yield path
    
    # Restore
    get_settings().DATABASE_URL = old_url
    os.remove(path)

def test_alembic_migrations(temp_db_url):
    # Setup Alembic Config pointing to our alembic.ini
    alembic_cfg = Config("alembic.ini")
    
    # 1. Upgrade to head
    command.upgrade(alembic_cfg, "head")
    
    # 2. Assert tables exist by querying sqlite_master directly
    conn = sqlite3.connect(temp_db_url)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    conn.close()
    
    expected_tables = {
        "alembic_version",
        "users",
        "chat_sessions",
        "query_logs",
        "saved_locations",
        "real_estate_listings"
    }
    
    assert expected_tables.issubset(tables), f"Missing tables. Found: {tables}"
    
    # 3. Downgrade to base
    command.downgrade(alembic_cfg, "base")
    
    # 4. Assert tables are gone
    conn = sqlite3.connect(temp_db_url)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables_after = {row[0] for row in cursor.fetchall()}
    conn.close()
    
    # Alembic might leave sqlite_sequence depending on autoincrement usage
    # but the main tables should be gone.
    assert "users" not in tables_after
    assert "chat_sessions" not in tables_after
