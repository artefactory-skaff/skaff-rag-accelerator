import os
import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple


class Database:
    """A simple wrapper class for SQLite database operations."""

    def __init__(self):
        """Initialize the Database object by setting the database path based on the environment."""
        db_name = (
            "test.sqlite" if os.getenv("TESTING", "false").lower() == "true" else "database.sqlite"
        )
        self.db_path = Path(__file__).parent / db_name

    def __enter__(self) -> "Database":
        """Enter the runtime context related to the database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self

    def __exit__(self, exc_type: Optional[type]) -> None:
        """Exit the runtime context and close the database connection properly."""
        if exc_type is not None:
            self.conn.rollback()
        self.conn.commit()
        self.conn.close()

    def query(self, query: str, params: Optional[Tuple] = None) -> List[List[sqlite3.Row]]:
        """Execute a query against the database."""
        cursor = self.conn.cursor()
        results = []
        commands = filter(None, query.split(";"))
        for command in commands:
            cursor.execute(command, params or ())
            results.append(cursor.fetchall())
        return results

    def query_from_file(self, file_path: Path) -> None:
        """Execute a query from a SQL file."""
        with Path.open(file_path, "r") as file:
            query = file.read()
        self.query(query)

    def delete_db(self) -> None:
        """Delete the database file from the filesystem."""
        if self.conn:
            self.conn.close()
        if self.db_path.exists():
            self.db_path.unlink(missing_ok=True)


with Database() as connection:
    connection.query_from_file(Path(__file__).parent / "database_init.sql")
