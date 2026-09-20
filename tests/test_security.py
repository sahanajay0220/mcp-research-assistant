import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "assignment_4_python"))

from database import get_connection, init_db


def test_sql_injection_is_blocked():
    """Try to smuggle a DROP TABLE command through the title field."""
    init_db()  # make sure the table exists

    payload = "Fake Paper'); DROP TABLE citations; --"

    conn = get_connection()

    # Clean up any leftover rows from previous test runs first.
    conn.execute("DELETE FROM citations WHERE author = ?", ("Attacker",))
    conn.commit()

    conn.execute(
        "INSERT INTO citations (title, author, year) VALUES (?, ?, ?)",
        (payload, "Attacker", 2020),
    )
    conn.commit()

    # If the injection had "worked", this next line would throw an error
    # because the table would no longer exist.
    rows = conn.execute("SELECT title FROM citations WHERE author = ?", ("Attacker",)).fetchall()

    assert len(rows) == 1
    assert rows[0]["title"] == payload  # stored as literal text, not executed
    print("PASSED: SQL injection payload was stored safely as plain text.")

    # Clean up after ourselves so re-running this test stays reliable.
    conn.execute("DELETE FROM citations WHERE author = ?", ("Attacker",))
    conn.commit()
    conn.close()


def test_error_disclosure_is_blocked():
    """Force a real database failure and confirm the error message doesn't leak details."""
    import server  # imports the actual tool function

    db_path = os.path.join(os.path.dirname(__file__), "..", "src", "assignment_4_python", "citations.db")
    os.chmod(db_path, 0o444)  # make the file read-only

    try:
        result = server.add_citation("Should Fail", "Tester", 2021)
        assert result["status"] == "error"
        assert "internal error" in result["message"]
        # Make sure nothing technical leaked into the message shown to the user.
        assert "sqlite3" not in result["message"]
        assert "Traceback" not in result["message"]
        assert "readonly" not in result["message"]
        print("PASSED: Internal error was hidden from the user, generic message shown instead.")
    finally:       
        os.chmod(db_path, 0o666)  # restore write access so later tests/runs still work


if __name__ == "__main__":
    test_sql_injection_is_blocked()
    test_error_disclosure_is_blocked()