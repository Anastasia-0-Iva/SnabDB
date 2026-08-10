CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    date TEXT,
    urgency TEXT,
    product TEXT,
    region TEXT,
    responsible TEXT,
    stage TEXT,
    delivery TEXT,
    document TEXT,
    comment TEXT,
    file_path TEXT
);