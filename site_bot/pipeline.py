"""What happens to one incoming WhatsApp message: store it, classify it, create records, decide who hears about it."""
import json
import logging
import re
from dataclasses import asdict, dataclass, field

import anthropic

from . import db
from .classifier import Classification

log = logging.getLogger("site_bot")
LOW_CONFIDENCE = 0.5
APPROVAL_RE = re.compile(r"(موافق|رفض)\s+(MR-\d{4}-(\d+))(.*)", re.S)


@dataclass
class Outcome:
    reply: str | None
    notify: list[tuple[str, str]] = field(default_factory=list)  # (phone, text)


def handle(conn, classifier, phone: str, text: str | None, kind: str = "text",
           media_id: str | None = None, wa_message_id: str | None = None) -> Outcome:
    user = db.user_by_phone(conn, phone)
    if user is None:
        return Outcome("هذا الرقم غير مسجّل بالنظام. تواصل مع إدارة الشركة لإضافتك.")
    if wa_message_id and conn.execute(
        "SELECT 1 FROM messages WHERE wa_message_id = ?", (wa_message_id,)
    ).fetchone():
        return Outcome(None)  # WhatsApp retries deliveries; process each message once

    if text and user["role"] in ("manager", "management") and (m := APPROVAL_RE.match(text.strip())):
        return _decide(conn, user, m)

    projects = [dict(p) for p in db.projects_for(conn, user["id"])]
    single = projects[0] if len(projects) == 1 else None

    if not text:
        _store(conn, user, single, kind, None, media_id, wa_message_id, None)
        conn.commit()
        if kind == "audio":
            return Outcome("وصل الفويس. تحويل الصوت لنص مش مفعّل بالنسخة التجريبية، ابعتها كتابة لو سمحت.")
        return Outcome("وصلت الصورة وانحفظت.")

    # Store before classifying, so an AI outage never loses a message (see reprocess_pending).
    msg_id = _store(conn, user, single, kind, text, media_id, wa_message_id, None)
    conn.commit()
    return _route(conn, classifier, user, projects, msg_id, text)


def reprocess_pending(conn, classifier) -> list[tuple[str, Outcome]]:
    """Classify text messages that were stored while the AI was unreachable."""
    results = []
    for row in conn.execute(
        "SELECT m.id, m.text, u.phone FROM messages m JOIN users u ON u.id = m.user_id"
        " WHERE m.category IS NULL AND m.text IS NOT NULL ORDER BY m.id"
    ).fetchall():
        user = db.user_by_phone(conn, row["phone"])
        projects = [dict(p) for p in db.projects_for(conn, user["id"])]
        results.append((row["phone"], _route(conn, classifier, user, projects, row["id"], row["text"])))
    return results


def _route(conn, classifier, user, projects, msg_id: int, text: str) -> Outcome:
    single = projects[0] if len(projects) == 1 else None
    boq = [dict(b) for b in db.boq_for(conn, single["id"])] if single else []
    try:
        c = classifier.classify(text, projects, boq)
    except anthropic.APIError:
        log.exception("classification failed for message %s; left for reprocess_pending", msg_id)
        return Outcome("وصلت رسالتك وانحفظت. النظام مشغول هلّق ورح تتعالج تلقائياً بعد شوي.")
    project = next((p for p in projects if p["code"] == c.project_code), single)
    conn.execute(
        "UPDATE messages SET project_id = ?, category = ?, confidence = ?, extracted_json = ? WHERE id = ?",
        (project and project["id"], c.category, c.confidence,
         json.dumps(asdict(c), ensure_ascii=False), msg_id),
    )

    if project is None:
        conn.commit()
        names = "، ".join(f"{p['code']} ({p['name']})" for p in projects)
        return Outcome(f"لأي مشروع هالرسالة؟ مشاريعك: {names}. ابعتها مرة تانية واذكر رقم المشروع.")

    if c.category == "other" or c.confidence < LOW_CONFIDENCE:
        conn.commit()
        return Outcome("ما قدرت أفهم الرسالة بشكل أكيد، انبعتت لمراجعة بشرية.")

    outcome = _HANDLERS[c.category](conn, user, project, c, msg_id)
    conn.commit()
    return outcome


def _store(conn, user, project, kind, text, media_id, wa_message_id, c: Classification | None) -> int:
    cur = conn.execute(
        "INSERT INTO messages (wa_message_id, user_id, project_id, kind, text, media_id,"
        " category, confidence, extracted_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (wa_message_id, user["id"], project and project["id"], kind, text, media_id,
         c and c.category, c and c.confidence,
         c and json.dumps(asdict(c), ensure_ascii=False)),
    )
    return cur.lastrowid


def _progress(conn, user, project, c, msg_id):
    boq = conn.execute(
        "SELECT * FROM boq_items WHERE project_id = ? AND code = ?", (project["id"], c.boq_code)
    ).fetchone() if c.boq_code else None
    for item in c.items or [{"quantity": None, "unit": None}]:
        conn.execute(
            "INSERT INTO progress_entries (project_id, boq_item_id, location, description, qty, unit,"
            " message_id, day) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (project["id"], boq and boq["id"], c.location, c.summary,
             item["quantity"], item["unit"], msg_id, db.today()),
        )
        if boq and item["quantity"] and item["unit"] == boq["unit"]:
            conn.execute("UPDATE boq_items SET qty_done = qty_done + ? WHERE id = ?",
                         (item["quantity"], boq["id"]))
    where = f" ({c.location})" if c.location else ""
    return Outcome(f"تسجّل التقدّم{where} ورح يطلع بتقرير اليوم.\nإذا في شي غلط ردّ بالتصحيح.")


def _material_request(conn, user, project, c, msg_id):
    items = c.items or [{"material": c.summary, "spec": None, "quantity": None, "unit": None}]
    lines = []
    for item in items:
        cur = conn.execute(
            "INSERT INTO material_requests (project_id, requested_by, material, spec, qty, unit,"
            " needed_by, message_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (project["id"], user["id"], item["material"], item["spec"], item["quantity"],
             item["unit"], c.needed_by, msg_id),
        )
        row = conn.execute("SELECT * FROM material_requests WHERE id = ?", (cur.lastrowid,)).fetchone()
        lines.append(f"{db.request_ref(row['id'], row['created_at'])}: {_describe(row)}")
    listing = "\n".join(lines)
    managers = db.users_with_role(conn, "manager", project["id"])
    notify = [(m["phone"], f"طلب مواد جديد من {user['name']} · {project['name']}\n{listing}\n"
               f"للموافقة ردّ: موافق <رقم الطلب>  أو  رفض <رقم الطلب> <السبب>") for m in managers]
    when = f"\nمطلوب: {c.needed_by}" if c.needed_by else ""
    return Outcome(f"تم تسجيل الطلب:\n{listing}{when}\nانبعت لمدير المشروع للموافقة، ورح نبلّغك بكل تحديث.",
                   notify)


def _issue(conn, user, project, c, msg_id):
    kind = "safety" if c.category == "safety" else "issue"
    conn.execute(
        "INSERT INTO issues (project_id, kind, description, message_id, day) VALUES (?, ?, ?, ?, ?)",
        (project["id"], kind, c.summary, msg_id, db.today()),
    )
    recipients = list(db.users_with_role(conn, "manager", project["id"]))
    if kind == "safety":
        recipients += db.users_with_role(conn, "management")
        alert = f"بلاغ سلامة · {project['name']}\n{c.summary}\nمن: {user['name']}"
        reply = "وصل البلاغ للإدارة ومدير المشروع فوراً. البلاغ مفتوح لحد ما ينسكّر بملاحظة."
    else:
        alert = f"مشكلة بالموقع · {project['name']}\n{c.summary}\nمن: {user['name']}"
        reply = "تسجّلت المشكلة ووصلت لمدير المشروع."
    return Outcome(reply, [(r["phone"], alert) for r in recipients])


def _labour(conn, user, project, c, msg_id):
    conn.execute(
        "INSERT INTO labour_entries (project_id, workers, equipment, message_id, day) VALUES (?, ?, ?, ?, ?)",
        (project["id"], c.workers, c.equipment, msg_id, db.today()),
    )
    return Outcome("تسجّلت العمالة والمعدات لليوم.")


def _question(conn, user, project, c, msg_id):
    managers = db.users_with_role(conn, "manager", project["id"])
    text = f"استفسار من {user['name']} · {project['name']}\n{c.summary}"
    return Outcome("انبعت سؤالك لمدير المشروع.", [(m["phone"], text) for m in managers])


def _procurement_update(conn, user, project, c, msg_id):
    # Kept on the message row; linking it to a specific request is for the procurement phase.
    return Outcome("تسجّل تحديث المشتريات.")


_HANDLERS = {
    "progress": _progress,
    "material_request": _material_request,
    "procurement_update": _procurement_update,
    "approval": _procurement_update,
    "follow_up": _procurement_update,
    "issue": _issue,
    "safety": _issue,
    "labour": _labour,
    "question": _question,
}


def _describe(row) -> str:
    qty = f"{row['qty']:g} {row['unit'] or ''}".strip() if row["qty"] is not None else ""
    return " ".join(p for p in (row["material"], row["spec"], qty) if p)


def _decide(conn, user, m: re.Match) -> Outcome:
    word, ref, request_id, note = m.group(1), m.group(2), int(m.group(3)), m.group(4).strip()
    req = conn.execute("SELECT * FROM material_requests WHERE id = ?", (request_id,)).fetchone()
    if req is None or db.request_ref(req["id"], req["created_at"]) != ref:
        return Outcome(f"ما لقيت طلب برقم {ref}.")
    allowed = user["role"] == "management" or conn.execute(
        "SELECT 1 FROM user_projects WHERE user_id = ? AND project_id = ?", (user["id"], req["project_id"])
    ).fetchone()
    if not allowed:
        return Outcome("ما عندك صلاحية على هالمشروع.")
    if req["status"] != "pending_approval":
        return Outcome(f"الطلب {ref} مش بانتظار موافقة (حالته: {req['status']}).")

    status = "approved" if word == "موافق" else "rejected"
    conn.execute("UPDATE material_requests SET status = ? WHERE id = ?", (status, request_id))
    conn.execute("INSERT INTO approvals (request_id, approver_id, decision, note) VALUES (?, ?, ?, ?)",
                 (request_id, user["id"], status, note or None))
    conn.commit()

    requester = conn.execute("SELECT * FROM users WHERE id = ?", (req["requested_by"],)).fetchone()
    desc = _describe(req)
    if status == "approved":
        notify = [(requester["phone"], f"انوافق على طلبك {ref} ({desc}) وانبعت للمشتريات.")]
        notify += [(p["phone"], f"طلب موافق عليه {ref}: {desc}"
                    + (f"\nمطلوب: {req['needed_by']}" if req["needed_by"] else ""))
                   for p in db.users_with_role(conn, "procurement")]
    else:
        notify = [(requester["phone"], f"انرفض طلبك {ref} ({desc})" + (f": {note}" if note else "."))]
    return Outcome(f"تم: {ref} {'موافق عليه' if status == 'approved' else 'مرفوض'}.", notify)
