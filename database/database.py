from pathlib import Path
import sqlite3
from typing import List

class DatabaseConnection:
    def __enter__(self):
        self.conn = sqlite3.connect(Path(__file__).parent / "database.sqlite")
        self.conn.row_factory = sqlite3.Row
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()

    def query(self, query, params=None) -> List[List[sqlite3.Row]]:
        cursor = self.conn.cursor()
        results = []
        commands = filter(None, query.split(";"))
        for command in commands:
            cursor.execute(command, params or ())
            results.append(cursor.fetchall())
        return results
    
    def query_from_file(self, file_path):
        with open(file_path, 'r') as file:
            query = file.read()
        self.query(query)

with DatabaseConnection() as connection:
    connection.query_from_file(Path(__file__).parent / "database_init.sql")