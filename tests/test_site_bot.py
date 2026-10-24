import hashlib
import hmac
import json
from types import SimpleNamespace

import anthropic
import httpx
import pytest

from site_bot import __main__ as cli
from site_bot import db, pipeline, report
from site_bot.classifier import Classification, ClaudeClassifier, KeywordClassifier
from site_bot.whatsapp import parse_webhook, signature_ok

ENG = "10000000001"      # engineer on P03 only
ENG_MULTI = "10000000003"  # engineer on P05 and P07
MANAGER = "10000000010"
PROCUREMENT = "10000000020"
MANAGEMENT = "10000000030"


@pytest.fixture
def conn():
    c = db.connect(":memory:")
    cli.seed(c)
    return c


def send(conn, phone, text, classifier=None, **kw):
    return pipeline.handle(conn, classifier or KeywordClassifier(), phone, text, **kw)


class Fixed:
    def __init__(self, c):
        self.c = c

    def classify(self, text, projects, boq):
        return self.c


def test_material_request_goes_to_manager_then_procurement(conn):
    out = send(conn, ENG, "بدنا 20 طن حديد قطر 12 لبكرا الصبح عشان صبة بلوك B")
    assert "MR-" in out.reply
    assert [p for p, _ in out.notify] == [MANAGER]
    req = conn.execute("SELECT * FROM material_requests").fetchone()
    assert (req["material"], req["spec"], req["qty"], req["unit"]) == ("حديد", "Ø12", 20, "طن")
    assert req["needed_by"] == "بكرا"

    ref = db.request_ref(req["id"], req["created_at"])
    out = send(conn, MANAGER, f"موافق {ref}")
    assert conn.execute("SELECT status FROM material_requests").fetchone()[0] == "approved"
    assert {p for p, _ in out.notify} == {ENG, PROCUREMENT}


def test_rejection_reaches_the_engineer_with_reason(conn):
    send(conn, ENG, "بدنا 50 كيس اسمنت بكرا")
    req = conn.execute("SELECT * FROM material_requests").fetchone()
    out = send(conn, MANAGER, f"رفض {db.request_ref(req['id'], req['created_at'])} عنا بالمخزن")
    assert out.notify == [(ENG, out.notify[0][1])] and "عنا بالمخزن" in out.notify[0][1]


def test_engineer_cannot_approve(conn):
    send(conn, ENG, "بدنا 50 كيس اسمنت بكرا")
    req = conn.execute("SELECT * FROM material_requests").fetchone()
    send(conn, ENG, f"موافق {db.request_ref(req['id'], req['created_at'])}")
    assert conn.execute("SELECT status FROM material_requests").fetchone()[0] == "pending_approval"


def test_safety_alerts_management_immediately(conn):
    out = send(conn, ENG, "عامل وقع عن السقالة بالطابق الأول، تم إسعافه والوضع مستقر")
    assert {p for p, _ in out.notify} == {MANAGER, MANAGEMENT}
    assert conn.execute("SELECT kind FROM issues").fetchone()[0] == "safety"


def test_unknown_number_is_refused(conn):
    out = send(conn, "19999999999", "صبينا السقف")
    assert "غير مسجّل" in out.reply
    assert conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0] == 0


def test_duplicate_delivery_is_processed_once(conn):
    send(conn, ENG, "اليوم عنا 14 عامل", wa_message_id="wamid.1")
    out = send(conn, ENG, "اليوم عنا 14 عامل", wa_message_id="wamid.1")
    assert out.reply is None
    assert conn.execute("SELECT COUNT(*) FROM labour_entries").fetchone()[0] == 1


def test_multi_project_engineer_is_asked_which_project(conn):
    out = send(conn, ENG_MULTI, "صبينا سقف الطابق التاني")
    assert "لأي مشروع" in out.reply and "P05" in out.reply
    assert conn.execute("SELECT COUNT(*) FROM progress_entries").fetchone()[0] == 0


def test_progress_updates_boq_quantity(conn):
    c = Classification("progress", 0.9, "صب سقف بلوك B ط2", "P03", "B", "الثاني",
                       [{"material": "خرسانة", "spec": None, "quantity": 86, "unit": "م³"}],
                       boq_code="C-03-012")
    out = send(conn, ENG, "صبينا سقف التاني بلوك B، 86 كوب", classifier=Fixed(c))
    assert "بلوك B" in out.reply
    assert conn.execute("SELECT qty_done FROM boq_items WHERE code = 'C-03-012'").fetchone()[0] == 86


def test_ai_outage_keeps_message_for_reprocessing(conn):
    class Down:
        def classify(self, *a):
            raise anthropic.APIConnectionError(request=httpx.Request("POST", "https://api.anthropic.com"))

    out = send(conn, ENG, "اليوم عنا 14 عامل", classifier=Down())
    assert "انحفظت" in out.reply
    assert conn.execute("SELECT category FROM messages").fetchone()[0] is None

    [(phone, out)] = pipeline.reprocess_pending(conn, KeywordClassifier())
    assert phone == ENG and "العمالة" in out.reply
    assert conn.execute("SELECT category FROM messages").fetchone()[0] == "labour"
    assert pipeline.reprocess_pending(conn, KeywordClassifier()) == []


def test_voice_note_is_stored_and_acknowledged(conn):
    out = send(conn, ENG, None, kind="audio", media_id="media.9")
    assert "الفويس" in out.reply
    assert conn.execute("SELECT kind, media_id FROM messages").fetchone()[:] == ("audio", "media.9")


def test_daily_report_puts_problems_first(conn):
    send(conn, ENG, "صبينا سقف الطابق التاني بلوك B اليوم")
    send(conn, ENG, "الباطون الجاهز ما وصل، والمضخة واقفة من الساعة 8")
    send(conn, ENG, "بدنا 20 طن حديد قطر 12 لبكرا")
    text = report.project_report(conn, conn.execute("SELECT * FROM projects WHERE code='P03'").fetchone(),
                                 db.today())
    assert text.index("يحتاج انتباه") < text.index("طلبات المواد") < text.index("المنجز اليوم")
    assert "بانتظار موافقة" in text and "من 3 رسالة" in text


def test_silent_engineers_get_reminded(conn):
    send(conn, ENG, "صبينا السقف اليوم")
    assert {u["phone"] for u in report.silent_engineers(conn, db.today())} == {"10000000002", ENG_MULTI}


def test_import_boq_upserts(conn, tmp_path):
    f = tmp_path / "boq.csv"
    f.write_text("code,description,unit,qty\nC-03-012,صب سقف,م³,700\nX-1,دهان,م²,50\n", encoding="utf-8")
    assert cli.import_boq(conn, "P03", f) == 2
    assert conn.execute("SELECT qty FROM boq_items WHERE code='C-03-012'").fetchone()[0] == 700
    assert conn.execute("SELECT COUNT(*) FROM boq_items").fetchone()[0] == 4


def test_parse_webhook_text_image_audio():
    payload = {"entry": [{"changes": [{"value": {"messages": [
        {"id": "a", "from": ENG, "type": "text", "text": {"body": "مرحبا"}},
        {"id": "b", "from": ENG, "type": "image", "image": {"id": "img1", "caption": "السقف"}},
        {"id": "c", "from": ENG, "type": "audio", "audio": {"id": "aud1"}},
    ]}}]}]}
    got = [(m.kind, m.text, m.media_id) for m in parse_webhook(payload)]
    assert got == [("text", "مرحبا", None), ("image", "السقف", "img1"), ("audio", None, "aud1")]
    assert parse_webhook({"entry": [{"changes": [{"value": {"statuses": [{}]}}]}]}) == []


def test_signature_check():
    body = b'{"x":1}'
    good = "sha256=" + hmac.new(b"s3cret", body, hashlib.sha256).hexdigest()
    assert signature_ok("s3cret", body, good)
    assert not signature_ok("s3cret", body + b" ", good)
    assert not signature_ok("s3cret", body, None)


def test_claude_classifier_request_and_parsing():
    payload = {"category": "material_request", "confidence": 0.95, "summary": "طلب حديد",
               "project_code": "P03", "block": "B", "floor": None,
               "items": [{"material": "حديد", "spec": "Ø12", "quantity": 20, "unit": "طن"}],
               "needed_by": "بكرا", "boq_code": None, "workers": None, "equipment": None}
    calls = []

    def create(**kw):
        calls.append(kw)
        return SimpleNamespace(stop_reason="end_turn",
                               content=[SimpleNamespace(type="text", text=json.dumps(payload))])

    client = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(create=create)))
    c = ClaudeClassifier(client=client).classify("بدنا حديد", [{"code": "P03", "name": "عمارة"}], [])
    assert c.category == "material_request" and c.items[0]["spec"] == "Ø12"
    kw = calls[0]
    assert kw["model"] == "claude-opus-5-5" and kw["fallbacks"] == "default"
    assert kw["output_config"]["format"]["type"] == "json_schema"


def test_claude_refusal_falls_back_to_human_review():
    def create(**kw):
        return SimpleNamespace(stop_reason="refusal", content=[])

    client = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(create=create)))
    assert ClaudeClassifier(client=client).classify("x", [], []).category == "other"


def test_webhook_endpoint(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    from site_bot import config, server

    path = str(tmp_path / "bot.sqlite3")
    cli.seed(db.connect(path))
    sent = []
    monkeypatch.setattr(config, "DB_PATH", path)
    monkeypatch.setattr(server, "classifier", KeywordClassifier())
    monkeypatch.setattr(server.sender, "send", lambda to, text: sent.append(to))
    monkeypatch.setenv("WHATSAPP_VERIFY_TOKEN", "tok")
    monkeypatch.setenv("WHATSAPP_APP_SECRET", "s3cret")
    client = TestClient(server.app)

    assert client.get("/webhook", params={"hub.mode": "subscribe", "hub.verify_token": "tok",
                                          "hub.challenge": "42"}).text == "42"
    assert client.get("/webhook", params={"hub.mode": "subscribe", "hub.verify_token": "no"}).status_code == 403

    body = json.dumps({"entry": [{"changes": [{"value": {"messages": [
        {"id": "w1", "from": ENG, "type": "text", "text": {"body": "عامل وقع عن السقالة"}}]}}]}]}).encode()
    assert client.post("/webhook", content=body, headers={"x-hub-signature-256": "sha256=bad"}).status_code == 401
    sig = "sha256=" + hmac.new(b"s3cret", body, hashlib.sha256).hexdigest()
    assert client.post("/webhook", content=body, headers={"x-hub-signature-256": sig}).status_code == 200
    assert sent == [ENG, MANAGER, MANAGEMENT]
