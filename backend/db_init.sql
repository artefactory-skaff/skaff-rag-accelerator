-- Go to https://dbdiagram.io/d/RAGAAS-63dbdcc6296d97641d7e07c8
-- Make your changes
-- Export > Export to PostgresSQL (or other)
-- Paste here
-- Replace "CREATE TABLE" with "CREATE TABLE IF NOT EXISTS"

CREATE TABLE IF NOT EXISTS "users" (
    "email" VARCHAR(255) PRIMARY KEY,
    "password" TEXT
);

CREATE TABLE IF NOT EXISTS "chat" (
    "id" VARCHAR(255) PRIMARY KEY,
    "timestamp" DATETIME,
    "user_id" VARCHAR(255),
    FOREIGN KEY ("user_id") REFERENCES "users" ("email")
);

CREATE TABLE IF NOT EXISTS "message" (
    "id" VARCHAR(255) PRIMARY KEY,
    "timestamp" DATETIME,
    "chat_id" VARCHAR(255),
    "sender" TEXT,
    "content" TEXT,
    FOREIGN KEY ("chat_id") REFERENCES "chat" ("id")
);

CREATE TABLE IF NOT EXISTS "feedback" (
    "id" VARCHAR(255) PRIMARY KEY,
    "message_id" VARCHAR(255),
    "feedback" TEXT,
    FOREIGN KEY ("message_id") REFERENCES "message" ("id")
);
