"""WhatsApp Business Cloud API: parse incoming webhooks, check their signature, send text replies."""
import hashlib
import hmac
import json
import os
import urllib.request
from dataclasses import dataclass


@dataclass
class Incoming:
    wa_message_id: str
    phone: str
    kind: str  # text, image, audio, other
    text: str | None
    media_id: str | None


def parse_webhook(payload: dict) -> list[Incoming]:
    out = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            for m in change.get("value", {}).get("messages", []):
                kind = m.get("type")
                if kind == "text":
                    out.append(Incoming(m["id"], m["from"], "text", m["text"]["body"], None))
                elif kind in ("image", "audio", "document", "video"):
                    media = m[kind]
                    out.append(Incoming(m["id"], m["from"], "audio" if kind == "audio" else "image",
                                        media.get("caption"), media.get("id")))
                elif kind == "button":
                    out.append(Incoming(m["id"], m["from"], "text", m["button"]["text"], None))
                else:
                    out.append(Incoming(m["id"], m["from"], "other", None, None))
    return out


def signature_ok(app_secret: str, body: bytes, header: str | None) -> bool:
    if not header or not header.startswith("sha256="):
        return False
    expected = hmac.new(app_secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header.removeprefix("sha256="))


class Sender:
    """Sends via the Cloud API when configured; otherwise prints, so the CLI works offline."""

    def __init__(self):
        self.token = os.environ.get("WHATSAPP_TOKEN")
        self.phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
        self.api_version = os.environ.get("WHATSAPP_API_VERSION", "v21.0")

    def send(self, to: str, text: str) -> None:
        if not (self.token and self.phone_number_id):
            print(f"\n→ {to}\n{text}")
            return
        req = urllib.request.Request(
            f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages",
            data=json.dumps({"messaging_product": "whatsapp", "to": to, "type": "text",
                             "text": {"body": text}}).encode(),
            headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=15).close()
