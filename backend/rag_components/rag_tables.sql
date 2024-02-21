-- Dialect MUST be sqlite, even if the database you use is different.
-- It is transpiled to the right dialect when executed.

CREATE TABLE IF NOT EXISTS "message_history" (
    "id" INTEGER PRIMARY KEY,
    "timestamp" DATETIME,
    "session_id" TEXT,
    "message" TEXT
);
