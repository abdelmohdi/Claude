import pytest
from fastapi.testclient import TestClient

from portal import db
from portal.__main__ import DEMO_PASSWORD, seed_demo
from portal.app import create_app

H = {"X-Requested-With": "portal"}


@pytest.fixture
def app(tmp_path):
    path = str(tmp_path / "portal.sqlite3")
    application = create_app(path)
    conn = db.connect(path)
    seed_demo(conn)
    conn.commit()
    conn.close()
    return application


def signed_in(app, username, password=DEMO_PASSWORD):
    c = TestClient(app, headers=H)
    r = c.post("/api/login", json={"username": username, "password": password})
    assert r.status_code == 200, r.text
    return c


@pytest.fixture
def manager(app): return signed_in(app, "manager")
@pytest.fixture
def sara(app): return signed_in(app, "sara")
@pytest.fixture
def omar(app): return signed_in(app, "omar")
@pytest.fixture
def buyer(app): return signed_in(app, "buyer")


def test_login_required_and_wrong_password(app):
    c = TestClient(app, headers=H)
    assert c.get("/api/home").status_code == 401
    assert c.post("/api/login", json={"username": "sara", "password": "nope"}).status_code == 401
    assert c.post("/api/login", json={"username": "nobody", "password": "nope"}).status_code == 401


def test_lockout_after_repeated_failures(app):
    c = TestClient(app, headers=H)
    for _ in range(8):
        assert c.post("/api/login", json={"username": "sara", "password": "bad"}).status_code == 401
    assert c.post("/api/login", json={"username": "sara", "password": DEMO_PASSWORD}).status_code == 429


def test_writes_without_header_are_refused(app, sara):
    plain = TestClient(app, cookies=sara.cookies)
    assert plain.post("/api/logs", json={"text": "x"}).status_code == 403


def test_home_shows_reminders_and_sites(sara):
    home = sara.get("/api/home").json()
    assert home["reminders"]["overdue"] == 1
    assert home["reminders"]["log_missing"] is False
    assert {s["code"] for s in home["sites"]} == {"DW", "V6"}
    assert [t["title"] for t in home["tasks"] if t["overdue"]] == ["Submit weekly progress report to consultant"]


def test_ticking_a_task_shows_up_for_management(sara, manager):
    before = manager.get("/api/pulse").json()["rev"]
    task = next(t for t in sara.get("/api/home").json()["tasks"] if t["overdue"])
    assert sara.patch(f"/api/tasks/{task['id']}", json={"status": "done"}).json()["status"] == "done"

    assert manager.get("/api/pulse").json()["rev"] > before
    over = manager.get("/api/overview").json()
    row = next(p for p in over["people"] if p["name"].startswith("Sara"))
    assert (row["overdue"], row["done_week"]) == (0, 2)
    assert over["feed"][0]["kind"] == "task_done"
    assert manager.get("/api/notifications").json()[0]["kind"] == "task_done"


def test_employee_cannot_edit_or_delete_assigned_task_or_touch_others(sara, omar):
    task = sara.get("/api/home").json()["tasks"][0]
    assert sara.patch(f"/api/tasks/{task['id']}", json={"title": "easier"}).status_code == 403
    assert sara.delete(f"/api/tasks/{task['id']}").status_code == 403
    assert omar.patch(f"/api/tasks/{task['id']}", json={"status": "done"}).status_code == 403


def test_own_task_lifecycle(sara):
    t = sara.post("/api/tasks", json={"title": "Call supplier", "due_date": "2030-01-01"}).json()
    assert t["assignee_name"].startswith("Sara") and not t["overdue"]
    assert sara.patch(f"/api/tasks/{t['id']}", json={"title": "Call the supplier", "due_date": None}).json()["due_date"] is None
    assert sara.delete(f"/api/tasks/{t['id']}").status_code == 200


def test_only_management_assigns_to_others(sara, manager):
    users = {u["username"]: u["id"] for u in manager.get("/api/users").json()}
    assert sara.post("/api/tasks", json={"title": "x", "assigned_to": users["omar"]}).status_code == 403
    assert manager.post("/api/tasks", json={"title": "Site photos", "assigned_to": users["omar"]}).status_code == 200


def test_daily_log_add_edit_and_management_view(app, manager):
    lina = signed_in(app, "lina")
    assert lina.get("/api/home").json()["reminders"]["log_missing"] is True
    entry = lina.post("/api/logs", json={"text": "Filed 12 delivery notes"}).json()
    assert lina.put(f"/api/logs/{entry['id']}", json={"text": "Filed 14 delivery notes"}).json()["text"].startswith("Filed 14")
    day = manager.get("/api/logs").json()
    assert "Lina (demo)" in {e["user_name"] for e in day["entries"]}
    assert {m["name"] for m in day["missing"]} == {"Demo Buyer", "Ravi (demo)"}
    assert signed_in(app, "sara").delete(f"/api/logs/{entry['id']}").status_code == 403


def test_request_flow_from_site_to_delivery(sara, manager, buyer):
    site = next(s for s in sara.get("/api/home").json()["sites"] if s["code"] == "DW")
    body = {"site_id": site["id"], "urgent": True, "needed_by": "2030-01-05",
            "items": [{"material": "Tile glue", "spec": "Plafix", "qty": 100, "unit": "bags"}]}
    req = sara.post("/api/requests", json=body).json()
    assert req["ref"].startswith("MR-") and req["status"] == "pending" and req["actions"] == ["cancel"]
    rid = req["id"]

    assert buyer.post(f"/api/requests/{rid}/action", json={"action": "order"}).status_code == 403
    assert sara.post(f"/api/requests/{rid}/action", json={"action": "approve"}).status_code == 403
    assert manager.post(f"/api/requests/{rid}/action", json={"action": "reject"}).status_code == 400

    assert manager.post(f"/api/requests/{rid}/action", json={"action": "approve"}).json()["status"] == "approved"
    assert buyer.get("/api/notifications").json()[0]["kind"] == "request_approve"
    assert buyer.post(f"/api/requests/{rid}/action", json={"action": "order", "note": "LPO 0950"}).json()["status"] == "ordered"
    done = sara.post(f"/api/requests/{rid}/action", json={"action": "deliver"}).json()
    assert done["status"] == "delivered" and done["actions"] == []
    assert [e["action"] for e in done["events"]] == ["create", "approve", "order", "deliver"]
    assert {n["kind"] for n in sara.get("/api/notifications").json()} >= {"request_approve", "request_order"}


def test_cannot_request_for_someone_elses_site_or_see_their_requests(sara, omar):
    ag = next(s for s in omar.get("/api/sites").json() if s["code"] == "AG")
    body = {"site_id": ag["id"], "items": [{"material": "Cement"}]}
    assert sara.post("/api/requests", json=body).status_code == 403
    assert sara.get(f"/api/sites/{ag['id']}").status_code == 403
    theirs = omar.get("/api/requests").json()[0]
    assert sara.get(f"/api/requests/{theirs['id']}").status_code == 404
    assert all(r["site_code"] in ("DW", "V6") for r in sara.get("/api/requests").json())


def test_management_pages_are_closed_to_employees(sara):
    for path in ("/api/overview", "/api/users", "/api/users/1/tracker"):
        assert sara.get(path).status_code == 403
    assert sara.post("/api/sites", json={"code": "X", "name": "X"}).status_code == 403
    assert sara.post("/api/users", json={"username": "evil", "name": "E", "password": "12345678",
                                         "role": "management"}).status_code == 403


def test_new_user_must_change_password_then_works(app, manager):
    sites = manager.get("/api/sites").json()
    r = manager.post("/api/users", json={"username": "habib", "name": "Habib", "job_title": "Foreman",
                                         "password": "temp-pass-1", "site_ids": [sites[0]["id"]]})
    assert r.status_code == 200
    habib = signed_in(app, "habib", "temp-pass-1")
    assert habib.get("/api/me").json()["must_change_password"] == 1
    assert habib.get("/api/home").status_code == 403
    assert habib.post("/api/password", json={"current": "temp-pass-1", "new": "short"}).status_code == 422
    assert habib.post("/api/password", json={"current": "temp-pass-1", "new": "my-own-pass-9"}).status_code == 200
    assert len(habib.get("/api/home").json()["sites"]) == 1


def test_reset_password_and_deactivate_sign_the_user_out(app, manager, sara):
    sid = next(u["id"] for u in manager.get("/api/users").json() if u["username"] == "sara")
    manager.patch(f"/api/users/{sid}", json={"password": "new-temp-123"})
    assert sara.get("/api/me").status_code == 401
    again = signed_in(app, "sara", "new-temp-123")
    manager.patch(f"/api/users/{sid}", json={"active": False})
    assert again.get("/api/me").status_code == 401
    assert TestClient(app, headers=H).post("/api/login", json={"username": "sara", "password": "new-temp-123"}).status_code == 401


def test_last_manager_is_protected(manager):
    me = manager.get("/api/me").json()
    assert manager.patch(f"/api/users/{me['id']}", json={"role": "employee"}).status_code == 400
    assert manager.patch(f"/api/users/{me['id']}", json={"active": False}).status_code == 400


def test_site_membership_controls_access(app, manager):
    site = manager.post("/api/sites", json={"code": "nv", "name": "Al Nouman Villa"}).json()
    assert site["code"] == "NV"
    assert manager.post("/api/sites", json={"code": "NV", "name": "dup"}).status_code == 400
    lina = signed_in(app, "lina")
    assert lina.get(f"/api/sites/{site['id']}").status_code == 403
    lid = lina.get("/api/me").json()["id"]
    manager.patch(f"/api/sites/{site['id']}", json={"member_ids": [lid]})
    assert [m["id"] for m in lina.get(f"/api/sites/{site['id']}").json()["members"]] == [lid]


def test_tracker_and_logout(manager, sara):
    sid = sara.get("/api/me").json()["id"]
    tr = manager.get(f"/api/users/{sid}/tracker").json()
    assert len(tr["tasks"]) == 4 and len(tr["logs"]) == 1 and len(tr["requests"]) == 1
    sara.post("/api/logout")
    assert sara.get("/api/me").status_code == 401


def test_index_and_static_are_served(app):
    c = TestClient(app)
    assert "app.js" in c.get("/").text
    assert "frame-ancestors" in c.get("/").headers["content-security-policy"]
