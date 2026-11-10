"""Staff portal API: accounts, tasks, daily logs, sites and material requests."""
import hashlib
import hmac
import json
import os
import secrets
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import db
from .db import one, rows

STATIC = Path(__file__).parent / "static"
COOKIE = "portal_session"
SESSION_DAYS = 14
TZ = ZoneInfo(os.environ.get("PORTAL_TZ", "Asia/Bahrain"))
MAX_FAILED_LOGINS, LOCKOUT_SECONDS = 8, 600
OPEN_REQUEST = ("pending", "approved", "ordered")


def now() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def today() -> str:
    return datetime.now(TZ).date().isoformat()


# --------------------------------------------------------------------------- passwords

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt${salt.hex()}${digest.hex()}"


def check_password(password: str, stored: str) -> bool:
    try:
        _, salt, digest = stored.split("$")
        got = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=2**14, r=8, p=1)
    except ValueError:
        return False
    return hmac.compare_digest(got.hex(), digest)


# --------------------------------------------------------------------------- request bodies

Short = Field(default="", max_length=200)


class LoginIn(BaseModel):
    username: str = Field(max_length=64)
    password: str = Field(max_length=200)


class PasswordIn(BaseModel):
    current: str = Field(max_length=200)
    new: str = Field(min_length=8, max_length=200)


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    details: str = Field(default="", max_length=2000)
    site_id: int | None = None
    assigned_to: int | None = None
    due_date: date | None = None
    priority: Literal["normal", "high"] = "normal"


class TaskPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    details: str | None = Field(default=None, max_length=2000)
    site_id: int | None = None
    due_date: date | None = None
    priority: Literal["normal", "high"] | None = None
    status: Literal["open", "done"] | None = None


class LogIn(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    site_id: int | None = None


class ItemIn(BaseModel):
    material: str = Field(min_length=1, max_length=200)
    spec: str = Short
    qty: float | None = Field(default=None, gt=0)
    unit: str = Field(default="", max_length=30)


class RequestIn(BaseModel):
    site_id: int
    items: list[ItemIn] = Field(min_length=1, max_length=50)
    needed_by: date | None = None
    urgent: bool = False
    note: str = Field(default="", max_length=1000)


class ActionIn(BaseModel):
    action: Literal["approve", "reject", "order", "deliver", "cancel"]
    note: str = Field(default="", max_length=500)


class SiteIn(BaseModel):
    code: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=100)
    location: str = Short


class SitePatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    location: str | None = Field(default=None, max_length=200)
    active: bool | None = None
    member_ids: list[int] | None = None


Role = Literal["employee", "procurement", "management"]


class UserIn(BaseModel):
    username: str = Field(pattern=r"^[a-z0-9._-]{3,32}$")
    name: str = Field(min_length=1, max_length=100)
    role: Role = "employee"
    job_title: str = Field(default="", max_length=100)
    password: str = Field(min_length=8, max_length=200)
    site_ids: list[int] = []


class UserPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    role: Role | None = None
    job_title: str | None = Field(default=None, max_length=100)
    active: bool | None = None
    site_ids: list[int] | None = None
    password: str | None = Field(default=None, min_length=8, max_length=200)


# --------------------------------------------------------------------------- queries

TASKS = """SELECT t.*, s.name AS site_name, a.name AS assignee_name, c.name AS creator_name
           FROM tasks t LEFT JOIN sites s ON s.id = t.site_id
           JOIN users a ON a.id = t.assigned_to JOIN users c ON c.id = t.created_by"""
TASK_ORDER = " ORDER BY t.status = 'done', t.due_date IS NULL, t.due_date, t.priority = 'high' DESC, t.id"
REQUESTS = """SELECT r.*, s.name AS site_name, s.code AS site_code, u.name AS requester_name
              FROM requests r JOIN sites s ON s.id = r.site_id JOIN users u ON u.id = r.requested_by"""
LOGS = """SELECT l.*, s.name AS site_name, u.name AS user_name
          FROM daily_logs l LEFT JOIN sites s ON s.id = l.site_id JOIN users u ON u.id = l.user_id"""
PUBLIC_USER = "id, username, name, job_title, role, active, must_change_password"


def task_out(t: dict) -> dict:
    t["overdue"] = t["status"] == "open" and bool(t["due_date"]) and t["due_date"] < today()
    return t


def tasks(conn, where: str, *args) -> list[dict]:
    return [task_out(t) for t in rows(conn, f"{TASKS} WHERE {where}{TASK_ORDER}", *args)]


def allowed_actions(r: dict, user: dict) -> list[str]:
    boss, buyer, mine = user["role"] == "management", user["role"] == "procurement", r["requested_by"] == user["id"]
    by_status = {
        "pending": (["approve", "reject"] if boss else []) + (["cancel"] if boss or mine else []),
        "approved": ["order"] if boss or buyer else [],
        "ordered": ["deliver"] if boss or buyer or mine else [],
    }
    return by_status.get(r["status"], [])


def requests_out(conn, user: dict, where: str, *args, limit: int = 200) -> list[dict]:
    found = rows(conn, f"{REQUESTS} WHERE {where} ORDER BY r.id DESC LIMIT {limit}", *args)
    if not found:
        return []
    marks = ",".join("?" * len(found))
    items: dict[int, list] = {}
    for i in rows(conn, f"SELECT * FROM request_items WHERE request_id IN ({marks}) ORDER BY id",
                  *[r["id"] for r in found]):
        items.setdefault(i["request_id"], []).append(i)
    for r in found:
        r["ref"] = f"MR-{r['created_at'][:4]}-{r['id']:04d}"
        r["urgent"] = bool(r["urgent"])
        r["items"] = items.get(r["id"], [])
        r["actions"] = allowed_actions(r, user)
    return found


def site_ids_of(conn, user_id: int) -> list[int]:
    return [r["site_id"] for r in rows(conn, "SELECT site_id FROM user_sites WHERE user_id = ?", user_id)]


def sees_everything(user: dict) -> bool:
    return user["role"] in ("management", "procurement")


def visible_requests(conn, user: dict, extra: str = "1", *args) -> list[dict]:
    if sees_everything(user):
        return requests_out(conn, user, extra, *args)
    return requests_out(
        conn, user,
        f"(r.requested_by = ? OR r.site_id IN (SELECT site_id FROM user_sites WHERE user_id = ?)) AND {extra}",
        user["id"], user["id"], *args)


def bump(conn) -> None:
    conn.execute("UPDATE meta SET value = value + 1 WHERE key = 'rev'")


def record(conn, user: dict, kind: str, data: dict, link: str = "", notify: list[int] | set[int] = ()) -> None:
    """Add to the activity feed, notify the given users (never the actor), and mark the data changed."""
    payload = json.dumps({"name": user["name"], **data}, ensure_ascii=False)
    conn.execute("INSERT INTO activity (user_id, kind, data, link, at) VALUES (?, ?, ?, ?, ?)",
                 (user["id"], kind, payload, link, now()))
    for uid in set(notify) - {user["id"]}:
        conn.execute("INSERT INTO notifications (user_id, kind, data, link, at) VALUES (?, ?, ?, ?, ?)",
                     (uid, kind, payload, link, now()))
    bump(conn)


def ids_with_role(conn, *roles: str) -> list[int]:
    marks = ",".join("?" * len(roles))
    return [r["id"] for r in rows(conn, f"SELECT id FROM users WHERE active = 1 AND role IN ({marks})", *roles)]


def set_members(conn, column: str, owner_id: int, other_column: str, ids: list[int]) -> None:
    conn.execute(f"DELETE FROM user_sites WHERE {column} = ?", (owner_id,))
    conn.executemany(f"INSERT OR IGNORE INTO user_sites ({column}, {other_column}) VALUES (?, ?)",
                     [(owner_id, i) for i in set(ids)])


def fail(status: int, code: str):
    raise HTTPException(status, code)


# --------------------------------------------------------------------------- app

def create_app(db_path: str) -> FastAPI:
    db.init(db_path)
    app = FastAPI(title="Staff portal", docs_url=None, redoc_url=None, openapi_url=None)
    failed_logins: dict[str, list[float]] = {}

    def get_db():
        conn = db.connect(db_path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def current_user(request: Request, conn=Depends(get_db)) -> dict:
        token = request.cookies.get(COOKIE)
        user = token and one(
            conn,
            f"SELECT u.{PUBLIC_USER.replace(', ', ', u.')} FROM sessions s JOIN users u ON u.id = s.user_id"
            " WHERE s.token_hash = ? AND s.expires_at > ? AND u.active = 1",
            hashlib.sha256(token.encode()).hexdigest(), time.time())
        if not user:
            fail(401, "not_signed_in")
        return user

    def ready_user(user=Depends(current_user)) -> dict:
        if user["must_change_password"]:
            fail(403, "must_change_password")
        return user

    def manager(user=Depends(ready_user)) -> dict:
        if user["role"] != "management":
            fail(403, "management_only")
        return user

    @app.middleware("http")
    async def guard(request: Request, call_next):
        # Browsers never add this header to cross-site form posts, so requiring it blocks CSRF.
        if (request.url.path.startswith("/api/") and request.method not in ("GET", "HEAD")
                and request.headers.get("x-requested-with") != "portal"):
            return JSONResponse({"detail": "bad_request_origin"}, status_code=403)
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self' https://fonts.googleapis.com; "
            "font-src https://fonts.gstatic.com; frame-ancestors 'none'")
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    # ----------------------------------------------------------------------- session

    @app.post("/api/login")
    def login(body: LoginIn, request: Request, response: Response, conn=Depends(get_db)):
        username = body.username.strip().lower()
        recent = [t for t in failed_logins.get(username, []) if t > time.time() - LOCKOUT_SECONDS]
        if len(recent) >= MAX_FAILED_LOGINS:
            fail(429, "too_many_attempts")
        user = one(conn, "SELECT * FROM users WHERE username = ? AND active = 1", username)
        # Hash even for unknown users so response time doesn't reveal which usernames exist.
        if not check_password(body.password, user["password_hash"] if user else hash_password("x")) or not user:
            failed_logins[username] = recent + [time.time()]
            fail(401, "wrong_login")
        failed_logins.pop(username, None)
        token = secrets.token_urlsafe(32)
        conn.execute("DELETE FROM sessions WHERE expires_at < ?", (time.time(),))
        conn.execute("INSERT INTO sessions VALUES (?, ?, ?)",
                     (hashlib.sha256(token.encode()).hexdigest(), user["id"], time.time() + SESSION_DAYS * 86400))
        https = request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https"
        response.set_cookie(COOKIE, token, max_age=SESSION_DAYS * 86400, httponly=True, samesite="strict",
                            secure=https, path="/")
        return {k: user[k] for k in PUBLIC_USER.split(", ")}

    @app.post("/api/logout")
    def logout(request: Request, response: Response, conn=Depends(get_db)):
        token = request.cookies.get(COOKIE, "")
        conn.execute("DELETE FROM sessions WHERE token_hash = ?", (hashlib.sha256(token.encode()).hexdigest(),))
        response.delete_cookie(COOKIE, path="/")
        return {}

    @app.get("/api/me")
    def me(user=Depends(current_user)):
        return user

    @app.post("/api/password")
    def change_password(body: PasswordIn, request: Request, user=Depends(current_user), conn=Depends(get_db)):
        stored = one(conn, "SELECT password_hash FROM users WHERE id = ?", user["id"])["password_hash"]
        if not check_password(body.current, stored):
            fail(400, "wrong_current_password")
        if body.new == body.current:
            fail(400, "same_password")
        conn.execute("UPDATE users SET password_hash = ?, must_change_password = 0 WHERE id = ?",
                     (hash_password(body.new), user["id"]))
        keep = hashlib.sha256(request.cookies.get(COOKIE, "").encode()).hexdigest()
        conn.execute("DELETE FROM sessions WHERE user_id = ? AND token_hash != ?", (user["id"], keep))
        return {}

    @app.get("/api/pulse")
    def pulse(user=Depends(current_user), conn=Depends(get_db)):
        return {
            "rev": one(conn, "SELECT value FROM meta WHERE key = 'rev'")["value"],
            "unread": one(conn, "SELECT COUNT(*) AS n FROM notifications WHERE user_id = ? AND read = 0",
                          user["id"])["n"],
        }

    # ----------------------------------------------------------------------- my day

    def my_sites(conn, user: dict) -> list[dict]:
        scope = "1" if user["role"] == "management" else "s.id IN (SELECT site_id FROM user_sites WHERE user_id = ?)"
        args = () if user["role"] == "management" else (user["id"],)
        return rows(conn, f"""
            SELECT s.*,
              (SELECT COUNT(*) FROM tasks t WHERE t.site_id = s.id AND t.status = 'open') AS open_tasks,
              (SELECT COUNT(*) FROM requests r WHERE r.site_id = s.id
                 AND r.status IN ('pending', 'approved', 'ordered')) AS open_requests,
              (SELECT COUNT(*) FROM user_sites us WHERE us.site_id = s.id) AS members
            FROM sites s WHERE {scope} ORDER BY s.active DESC, s.name""", *args)

    @app.get("/api/home")
    def home(user=Depends(ready_user), conn=Depends(get_db)):
        day = today()
        mine = tasks(conn, "t.assigned_to = ? AND (t.status = 'open' OR substr(t.done_at, 1, 10) = ?)",
                     user["id"], day)
        logs = rows(conn, f"{LOGS} WHERE l.user_id = ? AND l.day = ? ORDER BY l.id", user["id"], day)
        open_tasks = [t for t in mine if t["status"] == "open"]
        reminders = {
            "overdue": sum(t["overdue"] for t in open_tasks),
            "due_today": sum(t["due_date"] == day for t in open_tasks),
            "carried_over": sum(t["created_at"][:10] < day and not t["overdue"] for t in open_tasks),
            "log_missing": not logs,
            "my_pending_requests": one(
                conn, "SELECT COUNT(*) AS n FROM requests WHERE requested_by = ? AND status = 'pending'",
                user["id"])["n"],
            "to_receive": one(
                conn, "SELECT COUNT(*) AS n FROM requests WHERE requested_by = ? AND status = 'ordered'",
                user["id"])["n"],
        }
        if user["role"] == "management":
            reminders["approvals_waiting"] = one(
                conn, "SELECT COUNT(*) AS n FROM requests WHERE status = 'pending'")["n"]
        if user["role"] == "procurement":
            reminders["to_order"] = one(conn, "SELECT COUNT(*) AS n FROM requests WHERE status = 'approved'")["n"]
        return {
            "today": day, "tasks": mine, "logs": logs, "reminders": reminders,
            "sites": [s for s in my_sites(conn, user) if s["active"]],
            "requests": requests_out(conn, user, "r.requested_by = ?", user["id"], limit=8),
        }

    # ----------------------------------------------------------------------- tasks

    def task_or_404(conn, task_id: int) -> dict:
        found = tasks(conn, "t.id = ?", task_id)
        return found[0] if found else fail(404, "not_found")

    def check_site(conn, site_id: int | None) -> None:
        if site_id is not None and not one(conn, "SELECT 1 AS x FROM sites WHERE id = ?", site_id):
            fail(400, "unknown_site")

    @app.post("/api/tasks")
    def create_task(body: TaskIn, user=Depends(ready_user), conn=Depends(get_db)):
        assignee = body.assigned_to or user["id"]
        if assignee != user["id"]:
            if user["role"] != "management":
                fail(403, "management_only")
            if not one(conn, "SELECT 1 AS x FROM users WHERE id = ? AND active = 1", assignee):
                fail(400, "unknown_user")
        check_site(conn, body.site_id)
        cur = conn.execute(
            "INSERT INTO tasks (title, details, site_id, assigned_to, created_by, due_date, priority, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (body.title.strip(), body.details.strip(), body.site_id, assignee, user["id"],
             body.due_date and body.due_date.isoformat(), body.priority, now()))
        if assignee != user["id"]:
            record(conn, user, "task_assigned", {"title": body.title.strip()}, "#/home", notify=[assignee])
        else:
            bump(conn)
        return task_or_404(conn, cur.lastrowid)

    @app.patch("/api/tasks/{task_id}")
    def update_task(task_id: int, body: TaskPatch, user=Depends(ready_user), conn=Depends(get_db)):
        task = task_or_404(conn, task_id)
        boss = user["role"] == "management"
        changes = body.model_dump(exclude_unset=True)
        if not boss and task["assigned_to"] != user["id"]:
            fail(403, "not_yours")
        # Someone assigned a task by management may tick it off, but not rewrite it.
        if not boss and task["created_by"] != user["id"] and set(changes) - {"status"}:
            fail(403, "only_status")
        check_site(conn, changes.get("site_id"))
        if "due_date" in changes and changes["due_date"]:
            changes["due_date"] = changes["due_date"].isoformat()
        if changes.get("status") and changes["status"] != task["status"]:
            changes["done_at"] = now() if changes["status"] == "done" else None
            kind = "task_done" if changes["status"] == "done" else "task_reopened"
            record(conn, user, kind, {"title": task["title"]}, f"#/user/{task['assigned_to']}",
                   notify=[task["created_by"]] if kind == "task_done" else [])
        if changes:
            sets = ", ".join(f"{k} = ?" for k in changes)
            conn.execute(f"UPDATE tasks SET {sets} WHERE id = ?", (*changes.values(), task_id))
            bump(conn)
        return task_or_404(conn, task_id)

    @app.delete("/api/tasks/{task_id}")
    def delete_task(task_id: int, user=Depends(ready_user), conn=Depends(get_db)):
        task = task_or_404(conn, task_id)
        if user["role"] != "management" and task["created_by"] != user["id"]:
            fail(403, "not_yours")
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        bump(conn)
        return {}

    # ----------------------------------------------------------------------- daily logs

    @app.post("/api/logs")
    def add_log(body: LogIn, user=Depends(ready_user), conn=Depends(get_db)):
        check_site(conn, body.site_id)
        cur = conn.execute("INSERT INTO daily_logs (user_id, site_id, day, text, created_at) VALUES (?, ?, ?, ?, ?)",
                           (user["id"], body.site_id, today(), body.text.strip(), now()))
        record(conn, user, "log_added", {"text": body.text.strip()[:140]}, f"#/user/{user['id']}")
        return one(conn, f"{LOGS} WHERE l.id = ?", cur.lastrowid)

    def own_log_of_today(conn, log_id: int, user: dict) -> dict:
        log = one(conn, "SELECT * FROM daily_logs WHERE id = ?", log_id) or fail(404, "not_found")
        if log["user_id"] != user["id"]:
            fail(403, "not_yours")
        if log["day"] != today():
            fail(400, "day_closed")
        return log

    @app.put("/api/logs/{log_id}")
    def edit_log(log_id: int, body: LogIn, user=Depends(ready_user), conn=Depends(get_db)):
        own_log_of_today(conn, log_id, user)
        check_site(conn, body.site_id)
        conn.execute("UPDATE daily_logs SET text = ?, site_id = ?, updated_at = ? WHERE id = ?",
                     (body.text.strip(), body.site_id, now(), log_id))
        bump(conn)
        return one(conn, f"{LOGS} WHERE l.id = ?", log_id)

    @app.delete("/api/logs/{log_id}")
    def delete_log(log_id: int, user=Depends(ready_user), conn=Depends(get_db)):
        own_log_of_today(conn, log_id, user)
        conn.execute("DELETE FROM daily_logs WHERE id = ?", (log_id,))
        bump(conn)
        return {}

    @app.get("/api/logs")
    def list_logs(day: date | None = None, user=Depends(ready_user), conn=Depends(get_db)):
        if user["role"] != "management":
            return {"entries": rows(conn, f"{LOGS} WHERE l.user_id = ? ORDER BY l.id DESC LIMIT 60", user["id"])}
        d = (day or date.fromisoformat(today())).isoformat()
        return {
            "day": d,
            "entries": rows(conn, f"{LOGS} WHERE l.day = ? ORDER BY u.name, l.id", d),
            "missing": rows(conn, """SELECT id, name, job_title FROM users
                                     WHERE active = 1 AND role != 'management' AND substr(created_at, 1, 10) <= ?
                                       AND id NOT IN (SELECT user_id FROM daily_logs WHERE day = ?)
                                     ORDER BY name""", d, d),
        }

    # ----------------------------------------------------------------------- sites

    @app.get("/api/sites")
    def list_sites(user=Depends(ready_user), conn=Depends(get_db)):
        return my_sites(conn, user)

    @app.post("/api/sites")
    def create_site(body: SiteIn, user=Depends(manager), conn=Depends(get_db)):
        code = body.code.strip().upper()
        if one(conn, "SELECT 1 AS x FROM sites WHERE code = ?", code):
            fail(400, "code_taken")
        cur = conn.execute("INSERT INTO sites (code, name, location) VALUES (?, ?, ?)",
                           (code, body.name.strip(), body.location.strip()))
        bump(conn)
        return one(conn, "SELECT * FROM sites WHERE id = ?", cur.lastrowid)

    def site_for(conn, site_id: int, user: dict) -> dict:
        site = one(conn, "SELECT * FROM sites WHERE id = ?", site_id) or fail(404, "not_found")
        if not sees_everything(user) and site_id not in site_ids_of(conn, user["id"]):
            fail(403, "not_your_site")
        return site

    @app.get("/api/sites/{site_id}")
    def site_detail(site_id: int, user=Depends(ready_user), conn=Depends(get_db)):
        site = site_for(conn, site_id, user)
        site["today"] = today()
        site["members"] = rows(conn, """SELECT u.id, u.name, u.job_title, u.role FROM users u
                                        JOIN user_sites us ON us.user_id = u.id
                                        WHERE us.site_id = ? AND u.active = 1 ORDER BY u.name""", site_id)
        site["tasks"] = tasks(conn, "t.site_id = ? AND t.status = 'open'", site_id)
        site["requests"] = requests_out(conn, user, "r.site_id = ?", site_id, limit=30)
        site["logs"] = rows(conn, f"{LOGS} WHERE l.site_id = ? ORDER BY l.id DESC LIMIT 15", site_id)
        return site

    @app.patch("/api/sites/{site_id}")
    def update_site(site_id: int, body: SitePatch, user=Depends(manager), conn=Depends(get_db)):
        site_for(conn, site_id, user)
        changes = body.model_dump(exclude_unset=True)
        members = changes.pop("member_ids", None)
        if "active" in changes:
            changes["active"] = int(changes["active"])
        if changes:
            sets = ", ".join(f"{k} = ?" for k in changes)
            conn.execute(f"UPDATE sites SET {sets} WHERE id = ?", (*changes.values(), site_id))
        if members is not None:
            known = {r["id"] for r in rows(conn, "SELECT id FROM users")}
            set_members(conn, "site_id", site_id, "user_id", [m for m in members if m in known])
        bump(conn)
        return one(conn, "SELECT * FROM sites WHERE id = ?", site_id)

    # ----------------------------------------------------------------------- material requests

    @app.get("/api/requests")
    def list_requests(user=Depends(ready_user), conn=Depends(get_db)):
        return visible_requests(conn, user)

    @app.post("/api/requests")
    def create_request(body: RequestIn, user=Depends(ready_user), conn=Depends(get_db)):
        site = one(conn, "SELECT * FROM sites WHERE id = ? AND active = 1", body.site_id) or fail(400, "unknown_site")
        if user["role"] != "management" and body.site_id not in site_ids_of(conn, user["id"]):
            fail(403, "not_your_site")
        cur = conn.execute(
            "INSERT INTO requests (site_id, requested_by, needed_by, urgent, note, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (body.site_id, user["id"], body.needed_by and body.needed_by.isoformat(), int(body.urgent),
             body.note.strip(), now()))
        rid = cur.lastrowid
        conn.executemany("INSERT INTO request_items (request_id, material, spec, qty, unit) VALUES (?, ?, ?, ?, ?)",
                         [(rid, i.material.strip(), i.spec.strip(), i.qty, i.unit.strip()) for i in body.items])
        conn.execute("INSERT INTO request_events (request_id, user_id, action, at) VALUES (?, ?, 'create', ?)",
                     (rid, user["id"], now()))
        req = requests_out(conn, user, "r.id = ?", rid)[0]
        record(conn, user, "request_new", {"ref": req["ref"], "site": site["name"], "urgent": body.urgent},
               f"#/request/{rid}", notify=ids_with_role(conn, "management"))
        return req

    def request_for(conn, request_id: int, user: dict) -> dict:
        found = visible_requests(conn, user, "r.id = ?", request_id)
        return found[0] if found else fail(404, "not_found")

    @app.get("/api/requests/{request_id}")
    def request_detail(request_id: int, user=Depends(ready_user), conn=Depends(get_db)):
        req = request_for(conn, request_id, user)
        req["events"] = rows(conn, """SELECT e.action, e.note, e.at, u.name FROM request_events e
                                      JOIN users u ON u.id = e.user_id WHERE e.request_id = ? ORDER BY e.id""",
                             request_id)
        return req

    @app.post("/api/requests/{request_id}/action")
    def act_on_request(request_id: int, body: ActionIn, user=Depends(ready_user), conn=Depends(get_db)):
        req = request_for(conn, request_id, user)
        if body.action not in req["actions"]:
            fail(403, "action_not_allowed")
        if body.action == "reject" and not body.note.strip():
            fail(400, "reason_required")
        status = {"approve": "approved", "reject": "rejected", "order": "ordered", "deliver": "delivered",
                  "cancel": "cancelled"}[body.action]
        # The status check in WHERE stops two people acting on the same request at once.
        done = conn.execute("UPDATE requests SET status = ? WHERE id = ? AND status = ?",
                            (status, request_id, req["status"])).rowcount
        if not done:
            fail(409, "already_changed")
        conn.execute("INSERT INTO request_events (request_id, user_id, action, note, at) VALUES (?, ?, ?, ?, ?)",
                     (request_id, user["id"], body.action, body.note.strip(), now()))
        notify = {req["requested_by"]}
        if body.action == "approve":
            notify |= set(ids_with_role(conn, "procurement"))
        if body.action == "deliver":
            notify |= set(ids_with_role(conn, "procurement", "management"))
        record(conn, user, f"request_{body.action}", {"ref": req["ref"], "site": req["site_name"],
                                                       "note": body.note.strip()},
               f"#/request/{request_id}", notify=notify)
        return request_detail(request_id, user, conn)

    # ----------------------------------------------------------------------- management

    @app.get("/api/overview")
    def overview(user=Depends(manager), conn=Depends(get_db)):
        day, week_ago = today(), (date.fromisoformat(today()) - timedelta(days=7)).isoformat()
        people = rows(conn, """
            SELECT u.id, u.name, u.job_title, u.role,
              (SELECT COUNT(*) FROM tasks t WHERE t.assigned_to = u.id AND t.status = 'open') AS open_tasks,
              (SELECT COUNT(*) FROM tasks t WHERE t.assigned_to = u.id AND t.status = 'open'
                 AND t.due_date < ?) AS overdue,
              (SELECT COUNT(*) FROM tasks t WHERE t.assigned_to = u.id AND t.status = 'done'
                 AND substr(t.done_at, 1, 10) >= ?) AS done_week,
              (SELECT COUNT(*) FROM daily_logs l WHERE l.user_id = u.id AND l.day = ?) AS logs_today,
              (SELECT MAX(l.day) FROM daily_logs l WHERE l.user_id = u.id) AS last_log_day,
              (SELECT COUNT(*) FROM requests r WHERE r.requested_by = u.id
                 AND r.status IN ('pending', 'approved', 'ordered')) AS open_requests,
              (SELECT COUNT(*) FROM user_sites us WHERE us.user_id = u.id) AS sites
            FROM users u WHERE u.active = 1 AND u.role != 'management'
            ORDER BY overdue DESC, open_tasks DESC, u.name""", day, week_ago, day)
        counts = {r["status"]: r["n"] for r in rows(conn, "SELECT status, COUNT(*) AS n FROM requests GROUP BY status")}
        feed = rows(conn, "SELECT kind, data, link, at FROM activity ORDER BY id DESC LIMIT 25")
        for f in feed:
            f["data"] = json.loads(f["data"])
        return {
            "today": day,
            "people": people,
            "stats": {
                "open_tasks": sum(p["open_tasks"] for p in people),
                "overdue": sum(p["overdue"] for p in people),
                "logged_today": sum(bool(p["logs_today"]) for p in people),
                "people": len(people),
                "pending": counts.get("pending", 0),
                "approved": counts.get("approved", 0),
                "ordered": counts.get("ordered", 0),
            },
            "approvals": requests_out(conn, user, "r.status = 'pending'"),
            "feed": feed,
        }

    @app.get("/api/users")
    def list_users(user=Depends(manager), conn=Depends(get_db)):
        users = rows(conn, f"SELECT {PUBLIC_USER} FROM users ORDER BY active DESC, name")
        for u in users:
            u["site_ids"] = site_ids_of(conn, u["id"])
        return users

    @app.post("/api/users")
    def create_user(body: UserIn, user=Depends(manager), conn=Depends(get_db)):
        if one(conn, "SELECT 1 AS x FROM users WHERE username = ?", body.username):
            fail(400, "username_taken")
        cur = conn.execute(
            "INSERT INTO users (username, name, job_title, role, password_hash, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (body.username, body.name.strip(), body.job_title.strip(), body.role, hash_password(body.password), now()))
        known = {r["id"] for r in rows(conn, "SELECT id FROM sites")}
        set_members(conn, "user_id", cur.lastrowid, "site_id", [s for s in body.site_ids if s in known])
        bump(conn)
        return one(conn, f"SELECT {PUBLIC_USER} FROM users WHERE id = ?", cur.lastrowid)

    @app.patch("/api/users/{user_id}")
    def update_user(user_id: int, body: UserPatch, user=Depends(manager), conn=Depends(get_db)):
        target = one(conn, "SELECT * FROM users WHERE id = ?", user_id) or fail(404, "not_found")
        changes = body.model_dump(exclude_unset=True)
        sites = changes.pop("site_ids", None)
        password = changes.pop("password", None)
        loses_management = target["role"] == "management" and (
            changes.get("active") is False or changes.get("role", "management") != "management")
        if loses_management:
            if user_id == user["id"]:
                fail(400, "cannot_demote_self")
            if len(ids_with_role(conn, "management")) <= 1:
                fail(400, "last_manager")
        if "active" in changes:
            changes["active"] = int(changes["active"])
        if password:
            changes |= {"password_hash": hash_password(password), "must_change_password": 1}
        if changes:
            sets = ", ".join(f"{k} = ?" for k in changes)
            conn.execute(f"UPDATE users SET {sets} WHERE id = ?", (*changes.values(), user_id))
        if password or changes.get("active") == 0:
            conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        if sites is not None:
            known = {r["id"] for r in rows(conn, "SELECT id FROM sites")}
            set_members(conn, "user_id", user_id, "site_id", [s for s in sites if s in known])
        bump(conn)
        return one(conn, f"SELECT {PUBLIC_USER} FROM users WHERE id = ?", user_id)

    @app.get("/api/users/{user_id}/tracker")
    def tracker(user_id: int, user=Depends(manager), conn=Depends(get_db)):
        target = one(conn, f"SELECT {PUBLIC_USER} FROM users WHERE id = ?", user_id) or fail(404, "not_found")
        since = (date.fromisoformat(today()) - timedelta(days=14)).isoformat()
        return {
            "user": target,
            "today": today(),
            "sites": rows(conn, """SELECT s.id, s.name, s.code FROM sites s JOIN user_sites us ON us.site_id = s.id
                                   WHERE us.user_id = ? ORDER BY s.name""", user_id),
            "tasks": tasks(conn, "t.assigned_to = ? AND (t.status = 'open' OR substr(t.done_at, 1, 10) >= ?)",
                           user_id, since),
            "logs": rows(conn, f"{LOGS} WHERE l.user_id = ? AND l.day >= ? ORDER BY l.day DESC, l.id", user_id, since),
            "requests": requests_out(conn, user, "r.requested_by = ?", user_id, limit=20),
        }

    # ----------------------------------------------------------------------- notifications

    @app.get("/api/notifications")
    def notifications(user=Depends(ready_user), conn=Depends(get_db)):
        found = rows(conn, "SELECT id, kind, data, link, read, at FROM notifications WHERE user_id = ?"
                           " ORDER BY id DESC LIMIT 50", user["id"])
        for n in found:
            n["data"] = json.loads(n["data"])
        return found

    @app.post("/api/notifications/read")
    def read_notifications(user=Depends(ready_user), conn=Depends(get_db)):
        conn.execute("UPDATE notifications SET read = 1 WHERE user_id = ?", (user["id"],))
        return {}

    # ----------------------------------------------------------------------- pages

    @app.get("/")
    def index():
        return FileResponse(STATIC / "index.html", headers={"Cache-Control": "no-cache"})

    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    return app
