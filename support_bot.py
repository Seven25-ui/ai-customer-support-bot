"""
AI Customer Support Bot (Telegram)
----------------------------------
A customizable customer support chatbot for any business
(restaurant, clinic, shop, etc.) powered by Claude AI.

Setup:
    pip install -r requirements.txt

    1. Set your credentials as environment variables
       (never hardcode them in this file):

       export TELEGRAM_BOT_TOKEN="your_token_from_BotFather"
       export ANTHROPIC_API_KEY="your_api_key"

       Optional:
       export CLAUDE_MODEL="model-name"   # defaults to claude-sonnet-4-6

    2. Edit business_info.json (or let it auto-generate on first run)
       to customize the bot for a specific business.

    3. Run:
       python support_bot.py
"""

import asyncio
import json
import logging
import os
import time

import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TELEGRAM_TOKEN = os.environ.get("8873449618:AAHoZVR4-zALe7C1k0N8YY85PpQvrN5W1Ik
")
ANTHROPIC_KEY = os.environ.get("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")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")
BUSINESS_INFO_FILE = "business_info.json"

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

MAX_HISTORY = 10                  # messages kept per customer (controls token cost)
MIN_SECONDS_BETWEEN_MESSAGES = 2  # simple per-customer rate limit

REQUIRED_KEYS = [
    "business_name",
    "description",
    "hours",
    "location",
    "contact",
    "faq",
    "tone",
]

# Per-customer state (in memory; resets when the bot restarts)
conversations = {}
last_message_time = {}


# ---------------------------------------------------------------------------
# Business info (the bot's knowledge base)
# ---------------------------------------------------------------------------
def load_business_info():
    """Load and validate the business details from business_info.json."""
    if not os.path.exists(BUSINESS_INFO_FILE):
        default = {
            "business_name": "Sample Restaurant",
            "description": "A casual dining restaurant serving Filipino cuisine.",
            "hours": "Monday-Sunday, 10AM - 9PM",
            "location": "Cebu City, Philippines",
            "contact": "0917-000-0000",
            "faq": [
                {
                    "q": "Do you offer delivery?",
                    "a": "Yes, via Grab/Foodpanda or direct call/text.",
                },
                {
                    "q": "Do you have vegetarian options?",
                    "a": "Yes, we have several vegetarian dishes on the menu.",
                },
            ],
            "tone": "Friendly, helpful, professional.",
        }
        with open(BUSINESS_INFO_FILE, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2, ensure_ascii=False)
        logger.info("Created a default %s. Edit it for your business.", BUSINESS_INFO_FILE)
        return default

    try:
        with open(BUSINESS_INFO_FILE, "r", encoding="utf-8") as f:
            info = json.load(f)
    except json.JSONDecodeError as e:
        raise SystemExit(f"ERROR: {BUSINESS_INFO_FILE} is not valid JSON: {e}")

    missing = [k for k in REQUIRED_KEYS if k not in info]
    if missing:
        raise SystemExit(
            f"ERROR: {BUSINESS_INFO_FILE} is missing required field(s): "
            f"{', '.join(missing)}"
        )

    if not isinstance(info["faq"], list) or not all(
        isinstance(item, dict) and "q" in item and "a" in item for item in info["faq"]
    ):
        raise SystemExit(
            f"ERROR: 'faq' in {BUSINESS_INFO_FILE} must be a list of "
            f'{{"q": "...", "a": "..."}} items.'
        )

    return info


def build_system_prompt(info):
    faq_text = "\n".join(f"Q: {item['q']}\nA: {item['a']}" for item in info["faq"])

    return f"""You are the AI customer support assistant for {info['business_name']}.

BUSINESS INFO:
- Description: {info['description']}
- Hours: {info['hours']}
- Location: {info['location']}
- Contact: {info['contact']}

FREQUENTLY ASKED QUESTIONS:
{faq_text}

TONE: {info['tone']}

RULES:
- Only answer based on the information above. If you don't know the
  answer, say so and refer the customer to staff or the contact number.
  Never invent information (prices, dishes, policies, availability).
- Keep answers clear and concise, not overly long.
- Reply in the customer's language when you can (English, Tagalog, or Bisaya).
- If the customer asks something unrelated to the business (for example,
  general knowledge questions), politely redirect back to the business topic.
"""


BUSINESS_INFO = load_business_info()
SYSTEM_PROMPT = build_system_prompt(BUSINESS_INFO)


# ---------------------------------------------------------------------------
# Claude API call (blocking, so it is run in a thread from the async handler)
# ---------------------------------------------------------------------------
def call_claude(messages):
    headers = {
        "x-api-key": ANTHROPIC_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": CLAUDE_MODEL,
        "max_tokens": 500,
        "system": SYSTEM_PROMPT,
        "messages": messages,
    }
    resp = requests.post(ANTHROPIC_API_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    text = "".join(
        block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
    ).strip()
    if not text:
        raise ValueError("Empty response from Claude API")
    return text


# ---------------------------------------------------------------------------
# Telegram handlers
# ---------------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Hi! I'm the {BUSINESS_INFO['business_name']} Assistant 🤖\n"
        "Ask me about our hours, location, menu or services.\n"
        "Send /reset anytime to start a new conversation."
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    conversations.pop(chat_id, None)
    await update.message.reply_text("Conversation cleared. How can I help you?")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # Simple rate limit: ignore messages that arrive too quickly
    now = time.time()
    if now - last_message_time.get(chat_id, 0) < MIN_SECONDS_BETWEEN_MESSAGES:
        return
    last_message_time[chat_id] = now

    history = conversations.setdefault(chat_id, [])
    history.append({"role": "user", "content": update.message.text})

    # Keep only the last N messages, and make sure the first one is from
    # the user (the Claude API requires the conversation to start with "user")
    del history[:-MAX_HISTORY]
    while history and history[0]["role"] != "user":
        history.pop(0)

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    try:
        reply_text = await asyncio.to_thread(call_claude, history)
        history.append({"role": "assistant", "content": reply_text})
        await update.message.reply_text(reply_text)

    except Exception as e:
        logger.error("Error handling message from chat %s: %s", chat_id, e)
        history.pop()  # remove the user message that failed, so history stays valid
        await update.message.reply_text(
            "Sorry, we're experiencing a technical issue. Please try again "
            f"or contact us directly at {BUSINESS_INFO['contact']}."
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    if not TELEGRAM_TOKEN or not ANTHROPIC_KEY:
        print(
            "ERROR: Please set the TELEGRAM_BOT_TOKEN and ANTHROPIC_API_KEY "
            "environment variables first."
        )
        return

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(f"Bot running for {BUSINESS_INFO['business_name']}...")
    app.run_polling()


if __name__ == "__main__":
    main()
