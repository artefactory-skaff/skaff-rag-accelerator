import os
import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple


class Database:
    def __init__(self):
        db_name = (
            "test.sqlite" if os.getenv("TESTING", "false").lower() == "true" else "database.sqlite"
        )
        self.db_path = Path(__file__).parent / db_name

    def __enter__(self) -> "Database":
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self

    def __exit__(
        self, exc_type: Optional[type], exc_val: Optional[type], exc_tb: Optional[type]
    ) -> None:
        if exc_type is not None:
            self.conn.rollback()
        self.conn.commit()
        self.conn.close()

    def query(self, query: str, params: Optional[Tuple] = None) -> List[List[sqlite3.Row]]:
        cursor = self.conn.cursor()
        results = []
        commands = filter(None, query.split(";"))
        for command in commands:
            cursor.execute(command, params or ())
            results.append(cursor.fetchall())
        return results

    def query_from_file(self, file_path: Path) -> None:
        with Path.open(file_path, "r") as file:
            query = file.read()
        self.query(query)

    def delete_db(self) -> None:
        if self.conn:
            self.conn.close()
        if self.db_path.exists():
            self.db_path.unlink(missing_ok=True)


with Database() as connection:
    connection.query_from_file(Path(__file__).parent / "database_init.sql")
