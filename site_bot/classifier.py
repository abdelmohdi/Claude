"""Turns a site message into structured data.

`ClaudeClassifier` is the real one. `KeywordClassifier` is a crude offline stand-in used by the
tests and when no API key is configured, so the rest of the pipeline can run anywhere.
"""
import json
import re
from dataclasses import dataclass, field

import anthropic

CATEGORIES = ["progress", "material_request", "issue", "safety", "labour", "question", "other"]


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

SYSTEM_PROMPT = """You read WhatsApp messages that site engineers at a construction contractor send to the company's bot. Messages are in Arabic, usually Levantine dialect, often mixed with English terms and site slang (صبة = concrete pour, بلوك 20 = 20cm block, حديد 12 = 12mm rebar, قصارة = plaster, بوكلين = excavator).

Classify each message into exactly one category:
- progress: work done or started on site
- material_request: the engineer needs materials or supplies delivered
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
- project_code: one of the engineer's projects you are given; null if the message doesn't say and they have more than one.
- summary: one short Arabic sentence a manager can read in a daily report.
- confidence: 0 to 1, how sure you are of the category."""


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


# ---------------------------------------------------------------------------
# Offline fallback

_ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def _norm(text: str) -> str:
    text = text.translate(_ARABIC_DIGITS)
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
        if _has(t, "وقع|سقط|طاح|اصابه|انصاب|حادث|اسعاف|خطر|حريق"):
            category = "safety"
        elif _has(t, "بدنا|بدي|نحتاج|محتاجين|اطلبوا|ابعتولنا|ارسلوا|ناقصنا|لازمنا") and (
            re.search(_MATERIALS, t) or re.search(r"\d", t)
        ):
            category = "material_request"
        elif _has(t, "ما وصل|ما اجا|تاخير|متاخر|مشكله|عطل|خربان|واقفه|واقف|توقف|مطر"):
            category = "issue"
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
