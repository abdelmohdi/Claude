"""Webhook endpoint for the WhatsApp Cloud API. Run: uvicorn site_bot.server:app"""
import json
import logging
import os

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse

from . import config, db, pipeline
from .whatsapp import Incoming, Sender, parse_webhook, signature_ok

log = logging.getLogger("site_bot")
app = FastAPI(title="site-bot")
classifier = config.make_classifier()
sender = Sender()


@app.get("/webhook")
def verify(request: Request):
    q = request.query_params
    if q.get("hub.mode") == "subscribe" and q.get("hub.verify_token") == os.environ.get("WHATSAPP_VERIFY_TOKEN"):
        return PlainTextResponse(q.get("hub.challenge", ""))
    raise HTTPException(403)


@app.post("/webhook")
async def receive(request: Request, background: BackgroundTasks):
    body = await request.body()
    secret = os.environ.get("WHATSAPP_APP_SECRET")
    if secret and not signature_ok(secret, body, request.headers.get("x-hub-signature-256")):
        raise HTTPException(401)
    for incoming in parse_webhook(json.loads(body)):
        # Answer WhatsApp right away; classification can take a few seconds.
        background.add_task(process, incoming)
    return {"ok": True}


def process(incoming: Incoming) -> None:
    conn = db.connect(config.DB_PATH)
    try:
        outcome = pipeline.handle(conn, classifier, incoming.phone, incoming.text, incoming.kind,
                                  incoming.media_id, incoming.wa_message_id)
    except Exception:
        log.exception("failed to process %s from %s: %r", incoming.wa_message_id, incoming.phone, incoming.text)
        sender.send(incoming.phone, "صار خطأ بمعالجة رسالتك. جرّب تبعتها كمان مرة بعد شوي.")
        return
    finally:
        conn.close()
    if outcome.reply:
        sender.send(incoming.phone, outcome.reply)
    for phone, text in outcome.notify:
        sender.send(phone, text)
