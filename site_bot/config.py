import os

from .classifier import ClaudeClassifier, KeywordClassifier

DB_PATH = os.environ.get("SITE_BOT_DB", "site_bot.sqlite3")


def make_classifier():
    """Claude when credentials exist; the keyword stand-in when SITE_BOT_OFFLINE=1 or there is no key."""
    if os.environ.get("SITE_BOT_OFFLINE") == "1" or not (
        os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
    ):
        return KeywordClassifier()
    return ClaudeClassifier(model=os.environ.get("SITE_BOT_MODEL", "claude-opus-5-5"))
