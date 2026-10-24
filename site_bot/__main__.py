"""Command line: setup, simulation and the scheduled jobs (daily report, 5pm reminder, reprocessing).

    python -m site_bot seed
    python -m site_bot simulate +10000000001 "بدنا 20 طن حديد قطر 12 لبكرا"
    python -m site_bot report            # cron: 0 19 * * *
    python -m site_bot remind            # cron: 0 17 * * *
    python -m site_bot reprocess         # cron: */10 * * * *
    python -m site_bot import-chat "WhatsApp Chat with المشتريات.txt"
"""
import argparse
import csv

from . import chat_export, config, db, pipeline, report
from .classifier import ClaudeClassifier
from .whatsapp import Sender


def add_project(conn, code, name):
    conn.execute("INSERT INTO projects (code, name) VALUES (?, ?)", (code, name))


def add_user(conn, name, phone, role, project_codes=()):
    uid = conn.execute("INSERT INTO users (name, phone, role) VALUES (?, ?, ?)", (name, phone, role)).lastrowid
    for code in project_codes:
        pid = conn.execute("SELECT id FROM projects WHERE code = ?", (code,)).fetchone()["id"]
        conn.execute("INSERT INTO user_projects (user_id, project_id) VALUES (?, ?)", (uid, pid))


def import_boq(conn, project_code, path):
    """CSV with columns code,description,unit,qty (save the Excel sheet as CSV UTF-8)."""
    pid = conn.execute("SELECT id FROM projects WHERE code = ?", (project_code,)).fetchone()["id"]
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    conn.executemany(
        "INSERT INTO boq_items (project_id, code, description, unit, qty) VALUES (?, ?, ?, ?, ?)"
        " ON CONFLICT (project_id, code) DO UPDATE SET description = excluded.description,"
        " unit = excluded.unit, qty = excluded.qty",
        [(pid, r["code"], r["description"], r["unit"], float(r["qty"])) for r in rows],
    )
    return len(rows)


def seed(conn):
    """Example company: fake names and numbers, for trying the bot before real data is loaded."""
    for code, name in [("P03", "عمارة سكنية"), ("P05", "مدرسة"), ("P07", "مستودعات")]:
        add_project(conn, code, name)
    add_user(conn, "م. مهندس موقع 1", "10000000001", "engineer", ["P03"])
    add_user(conn, "م. مهندس موقع 2", "10000000002", "engineer", ["P05"])
    add_user(conn, "م. مهندس موقع 3", "10000000003", "engineer", ["P05", "P07"])
    add_user(conn, "مدير مشاريع", "10000000010", "manager", ["P03", "P05", "P07"])
    add_user(conn, "المشتريات", "10000000020", "procurement")
    add_user(conn, "الإدارة", "10000000030", "management")
    conn.executemany(
        "INSERT INTO boq_items (project_id, code, description, unit, qty) VALUES (1, ?, ?, ?, ?)",
        [("C-03-012", "صب سقف خرسانة مسلحة", "م³", 640), ("M-04-003", "بلوك 20 سم", "م²", 4200),
         ("F-01-002", "قصارة داخلية", "م²", 9800)],
    )
    conn.commit()


def main():
    ap = argparse.ArgumentParser(prog="site_bot")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("seed")
    p = sub.add_parser("add-project"); p.add_argument("code"); p.add_argument("name")
    p = sub.add_parser("add-user")
    p.add_argument("name"); p.add_argument("phone")
    p.add_argument("role", choices=["engineer", "manager", "procurement", "management"])
    p.add_argument("--projects", default="", help="comma-separated project codes")
    p = sub.add_parser("import-boq"); p.add_argument("project"); p.add_argument("csv")
    p = sub.add_parser("simulate"); p.add_argument("phone"); p.add_argument("text")
    p = sub.add_parser("report"); p.add_argument("--day", default=None)
    p = sub.add_parser("remind"); p.add_argument("--day", default=None)
    sub.add_parser("reprocess")
    p = sub.add_parser("import-chat", help="classify an exported WhatsApp chat into a review spreadsheet")
    p.add_argument("file"); p.add_argument("--out", default="مراجعة_المحادثة.xlsx")
    p.add_argument("--since", help="only messages on or after this date, YYYY-MM-DD")
    p.add_argument("--yes", action="store_true", help="don't ask before calling the AI")
    args = ap.parse_args()

    conn = db.connect(config.DB_PATH)
    sender = Sender()
    day = getattr(args, "day", None) or db.today()

    if args.cmd == "seed":
        seed(conn)
        print("Seeded 3 example projects and 6 example users.")
    elif args.cmd == "add-project":
        add_project(conn, args.code, args.name); conn.commit()
    elif args.cmd == "add-user":
        add_user(conn, args.name, args.phone, args.role, [c for c in args.projects.split(",") if c])
        conn.commit()
    elif args.cmd == "import-boq":
        n = import_boq(conn, args.project, args.csv); conn.commit()
        print(f"Imported {n} BOQ items into {args.project}.")
    elif args.cmd == "simulate":
        out = pipeline.handle(conn, config.make_classifier(), args.phone, args.text)
        if out.reply:
            sender.send(args.phone, out.reply)
        for phone, text in out.notify:
            sender.send(phone, text)
    elif args.cmd == "report":
        for p in conn.execute("SELECT * FROM projects ORDER BY code"):
            text = report.project_report(conn, p, day)
            for m in db.users_with_role(conn, "manager", p["id"]):
                sender.send(m["phone"], text)
        summary = report.management_report(conn, day)
        for m in db.users_with_role(conn, "management"):
            sender.send(m["phone"], summary)
    elif args.cmd == "remind":
        for u in report.silent_engineers(conn, day):
            sender.send(u["phone"], "تذكير: ما وصلنا تحديث اليوم. ابعت شو انعمل بالموقع، ولو فويس قصير.")
    elif args.cmd == "import-chat":
        import_chat(conn, args)
    elif args.cmd == "reprocess":
        for phone, out in pipeline.reprocess_pending(conn, config.make_classifier()):
            if out.reply:
                sender.send(phone, out.reply)
            for to, text in out.notify:
                sender.send(to, text)


def import_chat(conn, args):
    with open(args.file, encoding="utf-8-sig") as f:
        messages = chat_export.parse(f.read())
    if args.since:
        messages = [m for m in messages if m.sent_at.date().isoformat() >= args.since]
    if not messages:
        print("No messages found. Is this a WhatsApp 'Export chat' .txt file?")
        return
    n_ai, batches = sum(m.needs_ai for m in messages), chat_export.batches_needed(messages)
    print(f"{len(messages)} messages from {messages[0].sent_at:%Y-%m-%d} to {messages[-1].sent_at:%Y-%m-%d}; "
          f"{n_ai} need classifying ({batches} AI calls).")
    classifier = config.make_classifier()
    if isinstance(classifier, ClaudeClassifier):
        # Rough: about 5 cents per call of 30 messages at low effort. Check the console for real spend.
        print(f"Rough cost: about ${batches * 0.05:.2f} on {classifier.model}.")
        if not args.yes and input("Continue? [y/N] ").strip().lower() != "y":
            return
    else:
        print("Offline keyword classifier (no ANTHROPIC_API_KEY): results are only a rough preview.")
    projects = [dict(p) for p in conn.execute("SELECT code, name FROM projects ORDER BY code")]
    results = chat_export.classify(messages, classifier, projects,
                                   progress=lambda done, total: print(f"  {done}/{total}", end="\r"))
    chat_export.write_review(args.out, messages, results)
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
