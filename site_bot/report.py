"""Daily reports, written for WhatsApp: problems first, then open requests, then what got done."""
from . import db
from .pipeline import _describe

STATUS_AR = {"pending_approval": "بانتظار موافقة", "approved": "موافق عليه",
             "ordered": "انطلب", "delivered": "وصل", "rejected": "مرفوض"}


def project_report(conn, project, day: str) -> str:
    pid = project["id"]
    issues = conn.execute(
        "SELECT * FROM issues WHERE project_id = ? AND (day = ? OR status = 'open')"
        " ORDER BY kind = 'safety' DESC, id", (pid, day)).fetchall()
    requests = conn.execute(
        "SELECT * FROM material_requests WHERE project_id = ?"
        " AND (status IN ('pending_approval', 'approved', 'ordered') OR date(created_at) = ?) ORDER BY id",
        (pid, day)).fetchall()
    progress = conn.execute(
        "SELECT pe.*, b.code AS boq_code FROM progress_entries pe"
        " LEFT JOIN boq_items b ON b.id = pe.boq_item_id WHERE pe.project_id = ? AND pe.day = ? ORDER BY pe.id",
        (pid, day)).fetchall()
    labour = conn.execute(
        "SELECT * FROM labour_entries WHERE project_id = ? AND day = ? ORDER BY id DESC LIMIT 1",
        (pid, day)).fetchone()
    count = conn.execute(
        "SELECT COUNT(*) FROM messages WHERE project_id = ? AND date(received_at) = ?", (pid, day)
    ).fetchone()[0]

    lines = [f"*تقرير يومي · {project['code']} · {project['name']}*", f"{day} · من {count} رسالة"]
    if issues:
        lines.append("\n*يحتاج انتباه*")
        lines += [f"- {'[سلامة] ' if i['kind'] == 'safety' else ''}{i['description']}" for i in issues]
    if requests:
        lines.append("\n*طلبات المواد*")
        lines += [f"- {db.request_ref(r['id'], r['created_at'])} {_describe(r)} · {STATUS_AR[r['status']]}"
                  for r in requests]
    lines.append("\n*المنجز اليوم*")
    if progress:
        for p in progress:
            qty = f" · {p['qty']:g} {p['unit'] or ''}" if p["qty"] is not None else ""
            boq = f" [{p['boq_code']}]" if p["boq_code"] else ""
            loc = f" ({p['location']})" if p["location"] else ""
            lines.append(f"- {p['description']}{loc}{qty}{boq}")
    else:
        lines.append("- ما وصل أي تحديث تقدّم اليوم")
    if labour:
        extra = f" · {labour['equipment']}" if labour["equipment"] else ""
        lines.append(f"\n*العمالة:* {labour['workers'] if labour['workers'] is not None else '؟'} عامل{extra}")
    return "\n".join(lines)


def management_report(conn, day: str) -> str:
    projects = conn.execute("SELECT * FROM projects ORDER BY code").fetchall()
    return "\n\n———\n\n".join(project_report(conn, p, day) for p in projects)


def silent_engineers(conn, day: str):
    """Engineers who sent nothing today: they get the 5pm reminder."""
    return conn.execute(
        "SELECT * FROM users u WHERE u.role = 'engineer' AND NOT EXISTS ("
        " SELECT 1 FROM messages m WHERE m.user_id = u.id AND date(m.received_at) = ?)", (day,)
    ).fetchall()
