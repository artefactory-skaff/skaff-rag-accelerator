from logging import Logger
import os
from typing import Optional, Any
from pathlib import Path
from dotenv import load_dotenv

import sqlglot
from dbutils.pooled_db import PooledDB
from logging import Logger
from sqlalchemy.engine.url import make_url

from backend.logger import get_logger

POOL = None
class Database:
    DIALECT_PLACEHOLDERS = {
        "sqlite": "?",
        "postgresql": "%s",
        "mysql": "%s",
    }

    def __init__(self, connection_string: str = None, logger: Logger = None):
        self.connection_string = connection_string or os.getenv("DATABASE_URL")
        self.logger = logger or get_logger()

        self.url = make_url(self.connection_string)

        self.logger.debug("Creating connection pool")
        global POOL
        POOL = POOL or self._create_pool()  # Makes the pool a singleton
        self.pool = POOL
        self.conn = None

    def __enter__(self) -> "Database":
        self.logger.debug("Getting connection from pool")
        self.conn = self.pool.connection()
        return self

    def __exit__(self, exc_type: Optional[type], exc_value: Optional[BaseException], traceback: Optional[Any]) -> None:
        if self.conn:
            if exc_type:
                self.logger.error("Transaction failed", exc_info=(exc_type, exc_value, traceback))
                self.conn.rollback()
            else:
                self.conn.commit()
            self.logger.debug("Returning connection to pool")
            self.conn.close()
            self.conn = None

    def execute(self, query: str, params: Optional[tuple] = None) -> Any:
        cursor = self.conn.cursor()
        try:
            query = query.replace("?", self.DIALECT_PLACEHOLDERS[self.url.drivername])
            self.logger.debug(f"Executing query: {query}")
            cursor.execute(query, params or ())
            return cursor
        except Exception as e:
            cursor.close()
            self.logger.exception("Query execution failed", exc_info=e)
            raise

    def fetchone(self, query: str, params: Optional[tuple] = None) -> Optional[tuple]:
        cursor = self.execute(query, params)
        try:
            return cursor.fetchone()
        finally:
            cursor.close()

    def fetchall(self, query: str, params: Optional[tuple] = None) -> list:
        cursor = self.execute(query, params)
        try:
            return cursor.fetchall()
        finally:
            cursor.close()

    def initialize_schema(self):
        try:
            self.logger.debug("Initializing database schema")
            sql_script = Path(__file__).parent.joinpath('db_init.sql').read_text()
            transpiled_sql = sqlglot.transpile(sql_script, read='sqlite', write=self.url.drivername.replace("postgresql", "postgres"))
            for statement in transpiled_sql:
                self.execute(statement)
            self.logger.info(f"Database schema initialized successfully for {self.url.drivername}")
        except Exception as e:
            self.logger.exception("Schema initialization failed", exc_info=e)
            raise
        
    def _create_pool(self) -> PooledDB:
        if self.connection_string.startswith("sqlite:///"):
            import sqlite3
            Path(self.connection_string.replace("sqlite:///", "")).parent.mkdir(parents=True, exist_ok=True)
            return PooledDB(creator=sqlite3, database=self.connection_string.replace("sqlite:///", ""), maxconnections=5)
        elif self.connection_string.startswith("postgresql://"):
            import psycopg2
            return PooledDB(creator=psycopg2, dsn=self.connection_string, maxconnections=5)
        elif self.connection_string.startswith("mysql://"):
            import mysql.connector
            return PooledDB(creator=mysql.connector, user=self.url.username, password=self.url.password, host=self.url.host, port=self.url.port, database=self.url.database, maxconnections=5)
        elif self.connection_string.startswith("mysql+pymysql://"):
            import mysql.connector
            return PooledDB(creator=mysql.connector, user=self.url.username, password=self.url.password, host=self.url.host, port=self.url.port, database=self.url.database, maxconnections=5)
        elif self.connection_string.startswith("sqlserver://"):
            import pyodbc
            return PooledDB(creator=pyodbc, dsn=self.connection_string.replace("sqlserver://", ""), maxconnections=5)
        else:
            raise ValueError(f"Unsupported database type: {self.url.drivername}")
