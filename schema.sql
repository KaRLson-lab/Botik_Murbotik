CREATE TABLE IF NOT EXISTS entries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    mood        INTEGER NOT NULL CHECK(mood BETWEEN 1 AND 5),
    work_hours  REAL    NOT NULL CHECK(work_hours >= 0),
    sleep_hours REAL    NOT NULL CHECK(sleep_hours >= 0),
    comment     TEXT    DEFAULT '',
    created_at  TEXT    DEFAULT (datetime('now'))
);


CREATE TABLE IF NOT EXISTS reminders (
    user_id INTEGER PRIMARY KEY,
    hour    INTEGER NOT NULL DEFAULT 21,
    minute  INTEGER NOT NULL DEFAULT 0
);