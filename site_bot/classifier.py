"""Turns a site message into structured data.

`ClaudeClassifier` is the real one. `KeywordClassifier` is a crude offline stand-in used by the
tests and when no API key is configured, so the rest of the pipeline can run anywhere.
"""
import json
import re
from dataclasses import dataclass, field

import anthropic

CATEGORIES = ["progress", "material_request", "approval", "procurement_update", "follow_up", "issue",
              "safety", "labour", "question", "other"]
CATEGORY_AR = {"progress": "تقدّم عمل", "material_request": "طلب مواد",
               "approval": "موافقة", "procurement_update": "تحديث مشتريات", "follow_up": "متابعة طلب", "issue": "مشكلة أو تأخير", "safety": "سلامة",
               "labour": "عمالة ومعدات", "question": "استفسار", "other": "أخرى"}


@dataclass
class Classification:
    category: str
    confidence: float
    summary: str
    project_code: str | None = None
    block: str | None = None
    floor: str | None = None
    items: list[dict] = field(default_factory=list)  # {material, spec, quantity, unit}
    needed_by: str | None = None
    boq_code: str | None = None
    workers: int | None = None
    equipment: str | None = None

    @property
    def location(self) -> str | None:
        parts = [self.block and f"بلوك {self.block}", self.floor and f"الطابق {self.floor}"]
        return " · ".join(p for p in parts if p) or None


def _nullable(type_: str) -> dict:
    return {"anyOf": [{"type": type_}, {"type": "null"}]}


SCHEMA = {
    "type": "object",
    "properties": {
        "category": {"type": "string", "enum": CATEGORIES},
        "confidence": {"type": "number"},
        "summary": {"type": "string"},
        "project_code": _nullable("string"),
        "block": _nullable("string"),
        "floor": _nullable("string"),
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "material": {"type": "string"},
                    "spec": _nullable("string"),
                    "quantity": _nullable("number"),
                    "unit": _nullable("string"),
                },
                "required": ["material", "spec", "quantity", "unit"],
                "additionalProperties": False,
            },
        },
        "needed_by": _nullable("string"),
        "boq_code": _nullable("string"),
        "workers": _nullable("integer"),
        "equipment": _nullable("string"),
    },
    "required": [
        "category", "confidence", "summary", "project_code", "block", "floor",
        "items", "needed_by", "boq_code", "workers", "equipment",
    ],
    "additionalProperties": False,
}

BATCH_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"index": {"type": "integer"}, **SCHEMA["properties"]},
                "required": ["index", *SCHEMA["required"]],
                "additionalProperties": False,
            },
        },
    },
    "required": ["results"],
    "additionalProperties": False,
}

SYSTEM_PROMPT = """You read WhatsApp messages from the site engineers, foremen, procurement and management of a construction contractor. Messages may be in English, Arabic or a mix, written quickly on a phone by people of many nationalities, so expect misspellings and trade shorthand:
- English site shorthand: "keep order" / "arrange" = please purchase; LPO (also PLO) = local purchase order; "src 20", "45N", "SRC 45 N/M3" = concrete grade; "big palm" = big pump; holoblock / hollow block; BRC = steel mesh; "cartoon" = carton; "back" or "bag" = bag; keycote / keycode / key coat = a bonding product; BD = Bahraini dinar.
- Arabic site slang: صبة = concrete pour, بلوك 20 = 20cm block, حديد 12 = 12mm rebar, قصارة = plaster, بوكلين = excavator.

Classify each message into exactly one category:
- progress: work done or started on site
- material_request: someone asks for materials, supplies, equipment, a rental or a concrete booking (concrete bookings include grade, volume, date, time and pump: put grade and pump in spec, date and time in needed_by)
- approval: a manager approves or rejects something, or someone asks for approval of a quotation, payment or purchase
- procurement_update: a quotation or price, an LPO or order placed, a payment or cheque, a delivery on its way, arrived or collected, a rental stopped or returned
- follow_up: chasing an earlier request ("any update?", "still not received", "reminding you", "urgent" on its own)
- issue: a delay, breakdown, missing delivery, or anything blocking work
- safety: an injury, accident, near miss, or hazard. Choose this whenever safety is involved, even if the message also mentions other things.
- labour: headcount of workers or equipment on site
- question: a technical question or request for information
- other: anything else

Extract only what the message states; leave a field null when it is not stated. Do not guess quantities.
- items: one entry per material requested, or per quantity of work done for progress. Put diameters, sizes and grades in spec (e.g. "Ø12", "20 سم", "B300").
- block: the building or block letter if mentioned. floor: the floor as written.
- needed_by: the delivery time as the engineer said it (e.g. "بكرا الصبح").
- boq_code: only if the work clearly matches one of the BOQ items you are given.
- project_code: one of the projects you are given, matched by name even when misspelled ("ansar galary" is Ansar Gallery); for a group chat use the earlier messages when the message itself doesn't say; null if it can't be told.
- summary: one short sentence a manager can read in a daily report, in the same language as the message.
- confidence: 0 to 1, how sure you are of the category."""

GROUP_CHAT_NOTE = """

These messages come from a company WhatsApp group exported as text, so they include chatter and replies to earlier messages. Classify every message listed in <messages>, one result per index. Messages in <earlier> are context only: use them to understand replies (e.g. "Approved" under a quotation is an approval for that quotation's project, "وصل" after a request is a procurement_update). Greetings, thanks, bare acknowledgements, and general notices to staff (meetings, attendance, HR) are other."""


class ClaudeClassifier:
    def __init__(self, client: anthropic.Anthropic | None = None, model: str = "claude-opus-5-5"):
        self.client = client or anthropic.Anthropic()
        self.model = model

    def classify(self, text: str, projects: list[dict], boq: list[dict]) -> Classification:
        context = {
            "engineer_projects": [{"code": p["code"], "name": p["name"]} for p in projects],
            "boq_items": [
                {"code": b["code"], "description": b["description"], "unit": b["unit"]} for b in boq
            ],
        }
        response = self.client.beta.messages.create(
            model=self.model,
            max_tokens=4096,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            output_config={
                "effort": "low",
                "format": {"type": "json_schema", "schema": SCHEMA},
            },
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": (
                    f"<context>{json.dumps(context, ensure_ascii=False)}</context>\n"
                    f"<message>{text}</message>"
                ),
            }],
        )
        if response.stop_reason != "end_turn":
            # A refusal or truncation: keep the message and send it to a human.
            return Classification("other", 0.0, text[:120])
        data = json.loads(next(b.text for b in response.content if b.type == "text"))
        return Classification(**data)

    def classify_batch(self, messages: list[dict], earlier: list[dict], projects: list[dict]) -> list[Classification]:
        """Classify a run of group-chat messages in one call. Each message: {index, sender, time, text}."""
        projects_json = json.dumps([{"code": p["code"], "name": p["name"]} for p in projects], ensure_ascii=False)
        fmt = lambda ms: "\n".join(f"[{m['index']}] {m['time']} {m['sender']}: {m['text']}" for m in ms)
        response = self.client.beta.messages.create(
            model=self.model,
            max_tokens=16000,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            output_config={"effort": "low", "format": {"type": "json_schema", "schema": BATCH_SCHEMA}},
            system=SYSTEM_PROMPT + GROUP_CHAT_NOTE,
            messages=[{
                "role": "user",
                "content": (f"<projects>{projects_json}</projects>\n<earlier>\n{fmt(earlier)}\n</earlier>\n"
                            f"<messages>\n{fmt(messages)}\n</messages>"),
            }],
        )
        by_index = {}
        if response.stop_reason == "end_turn":
            for r in json.loads(next(b.text for b in response.content if b.type == "text"))["results"]:
                i = r.pop("index")
                by_index[i] = Classification(**r)
        # Anything the model skipped, refused or truncated goes to human review.
        return [by_index.get(m["index"]) or Classification("other", 0.0, m["text"][:120]) for m in messages]


# ---------------------------------------------------------------------------
# Offline fallback

_ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def _norm(text: str) -> str:
    text = text.translate(_ARABIC_DIGITS).lower()
    return re.sub("[أإآ]", "ا", text).replace("ة", "ه").replace("ى", "ي")


def _has(text: str, words: str) -> bool:
    # Arabic has no \b; accept a word start optionally glued to و/ف/ب/ل.
    return re.search(rf"(?:^|[\s،,.؟?!])[وفبل]?(?:{words})", text) is not None


_MATERIALS = "حديد|اسمنت|رمل|حصمه|خشب|باطون|خرسانه|سيراميك|بلاط|دهان|كابلات|مواسير|شبك"
_UNITS = "طن|م3|م³|كوب|م2|م²|متر|كيس|حبه|لوح"
_FLOORS = {"الارضي": "الأرضي", "الاول": "الأول", "التاني": "الثاني", "الثاني": "الثاني",
           "التالت": "الثالث", "الثالث": "الثالث", "الرابع": "الرابع"}


class KeywordClassifier:
    def classify(self, text: str, projects: list[dict], boq: list[dict]) -> Classification:
        t = _norm(text)
        if _has(t, "وقع|سقط|طاح|اصابه|انصاب|حادث|اسعاف|خطر|حريق|accident|injur|unsafe|ppe"):
            category = "safety"
        elif _has(t, "any update|still not|reminding|not received|not procured|متابعه|شو صار"):
            category = "follow_up"
        elif _has(t, "approved|approve|approval|موافق|موافقه"):
            category = "approval"
        elif _has(t, "بدنا|بدي|نحتاج|محتاجين|اطلبوا|ابعتولنا|ارسلوا|ناقصنا|لازمنا") and (
            re.search(_MATERIALS, t) or re.search(r"\d", t)
        ) or _has(t, "keep order|arrange|book|i need|need"):
            category = "material_request"
        elif _has(t, "ما وصل|ما اجا|تاخير|متاخر|مشكله|عطل|خربان|واقفه|واقف|توقف|مطر|not working|delay|problem"):
            category = "issue"
        elif _has(t, "وصل|وصلت|انطلب|طلبنا|عرض سعر|السعر|بالطريق|lpo|quotation|purchased|delivered|collected|cheque|chq|vat"):
            category = "procurement_update"
        elif _has(t, "صبينا|خلصنا|ركبنا|بلشنا|انجزنا|اشتغلنا|بنينا|قصرنا|دهنا|تم"):
            category = "progress"
        elif _has(t, "عامل|عمال|بوكلين|حفار|رافعه|كرين|معدات"):
            category = "labour"
        elif re.search("[؟?]", t):
            category = "question"
        else:
            category = "other"

        c = Classification(category, 0.5, text[:120])
        if len(projects) == 1:
            c.project_code = projects[0]["code"]
        if m := re.search(r"(?:بلوك|مبنى)\s+([A-Za-z])(?![A-Za-z])", text):
            c.block = m.group(1).upper()
        if m := re.search(r"(?:الطابق|ط)\s*(الارضي|الاول|التاني|الثاني|التالت|الثالث|الرابع|\d+)", t):
            c.floor = _FLOORS.get(m.group(1), m.group(1))
        if m := re.search(r"(بعد بكرا|بكرا|بكره|غدا|اليوم)", t):
            c.needed_by = m.group(1)
        if category == "material_request" and (mat := re.search(_MATERIALS, t)):
            qty = re.search(rf"(\d+(?:\.\d+)?)\s*({_UNITS})", t)
            spec = re.search(r"حديد\s*(?:قطر\s*)?(\d{1,2})(?!\d)", t)
            c.items.append({
                "material": mat.group(0),
                "spec": f"Ø{spec.group(1)}" if spec else None,
                "quantity": float(qty.group(1)) if qty else None,
                "unit": qty.group(2) if qty else None,
            })
        if category == "labour" and (m := re.search(r"(\d+)\s*عامل", t)):
            c.workers = int(m.group(1))
        return c

    def classify_batch(self, messages: list[dict], earlier: list[dict], projects: list[dict]) -> list[Classification]:
        return [self.classify(m["text"], projects, []) for m in messages]
