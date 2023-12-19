-- Go to https://dbdiagram.io/d/RAGAAS-63dbdcc6296d97641d7e07c8
-- Make your changes
-- Export > Export to PostgresSQL (or other)
-- Translate to SQLite (works with a cmd+k in Cursor, or https://www.rebasedata.com/convert-postgresql-to-sqlite-online)
-- Paste here
-- Replace "CREATE TABLE" with "CREATE TABLE IF NOT EXISTS"

CREATE TABLE IF NOT EXISTS "user" (
    "email" TEXT PRIMARY KEY,
    "password" TEXT
);

CREATE TABLE IF NOT EXISTS "chat" (
    "id" TEXT PRIMARY KEY,
    "user_id" TEXT,
    FOREIGN KEY ("user_id") REFERENCES "user" ("email")
);

CREATE TABLE IF NOT EXISTS "message" (
    "id" TEXT PRIMARY KEY,
    "timestamp" TEXT,
    "chat_id" TEXT,
    "sender" TEXT,
    "content" TEXT,
    FOREIGN KEY ("chat_id") REFERENCES "chat" ("id")
);

CREATE TABLE IF NOT EXISTS "feedback" (
    "id" TEXT PRIMARY KEY,
    "message_id" TEXT,
    "feedback" TEXT,
    FOREIGN KEY ("message_id") REFERENCES "message" ("id")
);
