"""SQLite storage. Every incoming message is kept verbatim; structured records point back to it."""
import sqlite3
from datetime import date

SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('engineer', 'manager', 'procurement', 'management'))
);
CREATE TABLE IF NOT EXISTS user_projects (
    user_id INTEGER NOT NULL REFERENCES users(id),
    project_id INTEGER NOT NULL REFERENCES projects(id),
    PRIMARY KEY (user_id, project_id)
);
CREATE TABLE IF NOT EXISTS boq_items (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    code TEXT NOT NULL,
    description TEXT NOT NULL,
    unit TEXT NOT NULL,
    qty REAL NOT NULL,
    qty_done REAL NOT NULL DEFAULT 0,
    UNIQUE (project_id, code)
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    wa_message_id TEXT UNIQUE,
    user_id INTEGER NOT NULL REFERENCES users(id),
    project_id INTEGER REFERENCES projects(id),
    kind TEXT NOT NULL,
    text TEXT,
    media_id TEXT,
    received_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    category TEXT,
    confidence REAL,
    extracted_json TEXT
);
CREATE TABLE IF NOT EXISTS progress_entries (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    boq_item_id INTEGER REFERENCES boq_items(id),
    location TEXT,
    description TEXT NOT NULL,
    qty REAL,
    unit TEXT,
    message_id INTEGER NOT NULL REFERENCES messages(id),
    day TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS material_requests (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    requested_by INTEGER NOT NULL REFERENCES users(id),
    material TEXT NOT NULL,
    spec TEXT,
    qty REAL,
    unit TEXT,
    needed_by TEXT,
    status TEXT NOT NULL DEFAULT 'pending_approval'
        CHECK (status IN ('pending_approval', 'approved', 'rejected', 'ordered', 'delivered')),
    message_id INTEGER NOT NULL REFERENCES messages(id),
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);
CREATE TABLE IF NOT EXISTS approvals (
    id INTEGER PRIMARY KEY,
    request_id INTEGER NOT NULL REFERENCES material_requests(id),
    approver_id INTEGER NOT NULL REFERENCES users(id),
    decision TEXT NOT NULL,
    note TEXT,
    decided_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);
CREATE TABLE IF NOT EXISTS issues (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    kind TEXT NOT NULL CHECK (kind IN ('issue', 'safety')),
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    message_id INTEGER NOT NULL REFERENCES messages(id),
    day TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS labour_entries (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    workers INTEGER,
    equipment TEXT,
    message_id INTEGER NOT NULL REFERENCES messages(id),
    day TEXT NOT NULL
);
"""


def connect(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn


def today() -> str:
    return date.today().isoformat()


def request_ref(request_id: int, created_at: str) -> str:
    return f"MR-{created_at[:4]}-{request_id:04d}"


def user_by_phone(conn, phone: str):
    return conn.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()


def projects_for(conn, user_id: int):
    return conn.execute(
        "SELECT p.* FROM projects p JOIN user_projects up ON up.project_id = p.id"
        " WHERE up.user_id = ? ORDER BY p.code",
        (user_id,),
    ).fetchall()


def users_with_role(conn, role: str, project_id: int | None = None):
    if project_id is None:
        return conn.execute("SELECT * FROM users WHERE role = ?", (role,)).fetchall()
    return conn.execute(
        "SELECT u.* FROM users u JOIN user_projects up ON up.user_id = u.id"
        " WHERE u.role = ? AND up.project_id = ?",
        (role, project_id),
    ).fetchall()


def boq_for(conn, project_id: int):
    return conn.execute(
        "SELECT * FROM boq_items WHERE project_id = ? ORDER BY code", (project_id,)
    ).fetchall()
