"""Command line for the staff portal.

    python -m portal create-admin ammar "Dr Ammar"     # first management account (asks for a password)
    python -m portal seed-demo                          # example sites, people and data to try it out
    python -m portal run                                # start on http://localhost:8000
"""
import argparse
import getpass
import os
from datetime import date, timedelta

from . import db
from .app import hash_password, now, today

DB_PATH = os.environ.get("PORTAL_DB", "portal.sqlite3")
DEMO_PASSWORD = "demo-1234"


def add_user(conn, username, name, role, password, job_title="", must_change=True):
    return conn.execute(
        "INSERT INTO users (username, name, job_title, role, password_hash, must_change_password, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (username, name, job_title, role, hash_password(password), int(must_change), now())).lastrowid


def seed_demo(conn):
    """Invented people on example sites. Everyone signs in with DEMO_PASSWORD."""
    day = date.fromisoformat(today())
    sites = {}
    for code, name, location in [("DW", "Diyar Walk", "Diyar Al Muharraq"), ("AG", "Ansar Gallery", "Tubli"),
                                 ("HQ", "Ramez HQ", "Hidd"), ("V6", "6 Villas", "Saar")]:
        sites[code] = conn.execute("INSERT INTO sites (code, name, location) VALUES (?, ?, ?)",
                                   (code, name, location)).lastrowid
    people = {}
    for username, name, role, title, codes in [
        ("manager", "Demo Manager", "management", "General Manager", []),
        ("buyer", "Demo Buyer", "procurement", "Procurement Officer", []),
        ("sara", "Sara (demo)", "employee", "Project Engineer", ["DW", "V6"]),
        ("omar", "Omar (demo)", "employee", "Site Foreman", ["AG", "HQ"]),
        ("ravi", "Ravi (demo)", "employee", "Site Foreman", ["DW"]),
        ("lina", "Lina (demo)", "employee", "Document Controller", ["HQ"]),
    ]:
        people[username] = add_user(conn, username, name, role, DEMO_PASSWORD, title, must_change=False)
        conn.executemany("INSERT INTO user_sites VALUES (?, ?)", [(people[username], sites[c]) for c in codes])

    def task(who, title, site, due, done=False, high=False, age=3):
        created = (day - timedelta(days=age)).isoformat() + "T08:00:00+03:00"
        conn.execute(
            "INSERT INTO tasks (title, site_id, assigned_to, created_by, due_date, priority, status, done_at, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (title, sites.get(site), people[who], people["manager"], due and (day + timedelta(days=due)).isoformat(),
             "high" if high else "normal", "done" if done else "open", now() if done else None, created))

    task("sara", "Submit weekly progress report to consultant", "V6", -2, high=True)
    task("sara", "Get TIO inspection booked for slab level", "DW", 1)
    task("sara", "Review revised BOQ with QS", "DW", 4)
    task("sara", "Send look-ahead programme", "V6", 0, done=True)
    task("omar", "Return rented scaffolding to supplier", "AG", -1)
    task("omar", "Collect signed invoices from site", "HQ", 0)
    task("omar", "Check curing of first floor columns", "HQ", None, done=True)
    task("ravi", "Book concrete pump for Monday pour", "DW", 2, high=True)
    task("lina", "File signed delivery notes", "HQ", -4)
    task("lina", "Update drawing register", "HQ", 3)

    def log(who, site, text):
        conn.execute("INSERT INTO daily_logs (user_id, site_id, day, text, created_at) VALUES (?, ?, ?, ?, ?)",
                     (people[who], sites[site], day.isoformat(), text, now()))

    log("sara", "DW", "Slab reinforcement checked with consultant, approved for pour. Two RFIs submitted.")
    log("omar", "AG", "Block work on second floor 60% done. Tile glue delivery received, 100 bags.")

    def request(who, site, status, items, urgent=False, needed=2):
        rid = conn.execute(
            "INSERT INTO requests (site_id, requested_by, needed_by, urgent, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (sites[site], people[who], (day + timedelta(days=needed)).isoformat(), int(urgent), status, now())).lastrowid
        conn.executemany("INSERT INTO request_items (request_id, material, spec, qty, unit) VALUES (?, ?, ?, ?, ?)",
                         [(rid, *i) for i in items])
        conn.execute("INSERT INTO request_events (request_id, user_id, action, at) VALUES (?, ?, 'create', ?)",
                     (rid, people[who], now()))

    request("ravi", "DW", "pending", [("Ready-mix concrete", "SRC 45N, big pump", 85, "m3")], urgent=True, needed=1)
    request("omar", "AG", "pending", [("Hollow block", "4 inch", 5000, "nos"), ("Tile glue", "", 200, "bags")])
    request("omar", "HQ", "approved", [("BRC mesh", "8 mm", 150, "nos")])
    request("sara", "V6", "ordered", [("Gypsum access panel", "60x60", 25, "nos")])
    conn.execute("UPDATE meta SET value = value + 1 WHERE key = 'rev'")


def main():
    ap = argparse.ArgumentParser(prog="portal")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("create-admin", help="create a management account")
    p.add_argument("username"); p.add_argument("name"); p.add_argument("--password")
    sub.add_parser("seed-demo", help="fill an empty database with example data")
    p = sub.add_parser("run", help="start the web server")
    p.add_argument("--host", default="127.0.0.1"); p.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()

    if args.cmd == "run":
        import uvicorn
        os.environ.setdefault("PORTAL_DB", DB_PATH)
        uvicorn.run("portal.asgi:app", host=args.host, port=args.port)
        return

    db.init(DB_PATH)
    conn = db.connect(DB_PATH)
    if args.cmd == "create-admin":
        password = args.password or getpass.getpass("Password (8+ characters): ")
        if len(password) < 8:
            raise SystemExit("Password must be at least 8 characters.")
        add_user(conn, args.username.lower(), args.name, "management", password, must_change=False)
        print(f"Created management account '{args.username.lower()}'.")
    elif args.cmd == "seed-demo":
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
            raise SystemExit("The database already has users; seed-demo only fills an empty one.")
        seed_demo(conn)
        print(f"Demo data added. Sign in as manager, buyer, sara, omar, ravi or lina with password {DEMO_PASSWORD}")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
