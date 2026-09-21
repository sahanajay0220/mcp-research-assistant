from pathlib import Path
import sqlite3
import logging

BASE_DIR = Path(__file__).resolve().parent

LOG_FILE = BASE_DIR / "server_errors.log"
logging.basicConfig(filename=LOG_FILE, level=logging.ERROR)
logger = logging.getLogger("research-assistant")

DB_FILE = BASE_DIR / "citations.db"

def get_connection():
    """Open a connection to the database file."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def init_db():
    """Create the citations table if it doesn't already exist."""
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS citations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            year INTEGER NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


init_db()

class InvalidInputError(Exception):
    """Raised when input fails validation, safe to show to the user."""


def validate_citation_input(title: str, author: str, year: int):
    """Check that citation fields are reasonable before they touch the database."""
    if not isinstance(title, str) or not title.strip():
        raise InvalidInputError("title must be a non-empty string")
    if len(title) > 300:
        raise InvalidInputError("title is too long (max 300 characters)")

    if not isinstance(author, str) or not author.strip():
        raise InvalidInputError("author must be a non-empty string")
    if len(author) > 200:
        raise InvalidInputError("author is too long (max 200 characters)")

    if not isinstance(year, int):
        raise InvalidInputError("year must be a whole number")
    if year < 1000 or year > 2100:
        raise InvalidInputError("year must be between 1000 and 2100")