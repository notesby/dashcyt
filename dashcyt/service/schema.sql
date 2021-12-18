CREATE TABLE IF NOT EXISTS user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS report (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    name TEXT NOT NULL,
    FOREIGN KEY (created_by) REFERENCES user(user_id)
);

CREATE TABLE IF NOT EXISTS graph (
    graph_id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES user(user_id)
);

CREATE TABLE IF NOT EXISTS saved_field (
    saved_field_id INTEGER PRIMARY KEY AUTOINCREMENT,
    field_id INTEGER NOT NULL,
    val TEXT NOT NULL,
    FOREIGN KEY (field_id) REFERENCES available_field(field_id)
);

CREATE TABLE IF NOT EXISTS graph_fields (
    graph_id INTEGER NOT NULL,
    available_field_id INTEGER NOT NULL,
    FOREIGN KEY (graph_id) REFERENCES graph(graph_id),
    FOREIGN KEY (available_field_id) REFERENCES available_field(field_id)
);

CREATE TABLE IF NOT EXISTS available_field (
    field_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    description TEXT NOT NULL
);