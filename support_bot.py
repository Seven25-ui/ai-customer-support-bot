"""
AI Customer Support Bot (Telegram)
------------------------------------
A customizable customer support chatbot for any business
(restaurant, clinic, shop, etc.) powered by Claude AI.

Setup:
    pip install python-telegram-bot requests --upgrade

    1. Set your Telegram Bot Token and Anthropic API Key as
       environment variables (do not hardcode them here, for safety):

       export TELEGRAM_BOT_TOKEN="your_token_from_BotFather"
       export ANTHROPIC_API_KEY="your_api_key"

    2. Edit business_info.json (or let it auto-generate on first run)
       to customize the bot for a specific business.

    3. Run:
       python support_bot.py
"""

import os
import json
import logging
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")
BUSINESS_INFO_FILE = "business_info.json"

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

# Each user (chat_id) gets their own conversation history
conversations = {}
MAX_HISTORY = 10  # messages to keep per user, to keep token cost down


def load_business_info():
    """Load the business details - this is the bot's 'knowledge base'."""
    if os.path.exists(BUSINESS_INFO_FILE):
        with open(BUSINESS_INFO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    # Default template if the config file doesn't exist yet
    default = {
        "business_name": "Sample Restaurant",
        "description": "A casual dining restaurant serving Filipino cuisine.",
        "hours": "Monday-Sunday, 10AM - 9PM",
        "location": "Cebu City, Philippines",
        "contact": "0917-000-0000",
        "faq": [
            {"q": "Do you offer delivery?", "a": "Yes, via Grab/Foodpanda or direct call/text."},
            {"q": "Do you have vegetarian options?", "a": "Yes, we have several vegetarian dishes on the menu."},
        ],
        "tone": "Friendly, helpful, professional.",
    }
    with open(BUSINESS_INFO_FILE, "w", encoding="utf-8") as f:
        json.dump(default, f, indent=2, ensure_ascii=False)
    return default


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
  answer, refer the customer to staff/the contact number - never
  invent information.
- Keep answers clear and concise, not overly long.
- If the customer asks something unrelated to the business (e.g.
  general knowledge questions), politely redirect back to the
  business topic.
"""


BUSINESS_INFO = load_business_info()
SYSTEM_PROMPT = build_system_prompt(BUSINESS_INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Hi! I'm the {BUSINESS_INFO['business_name']} Assistant 🤖\n"
        f"Ask me anything about our business - menu, hours, "
        f"location, or anything else!"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_message = update.message.text

    if chat_id not in conversations:
        conversations[chat_id] = []

    conversations[chat_id].append({"role": "user", "content": user_message})
    conversations[chat_id] = conversations[chat_id][-MAX_HISTORY:]

    try:
        headers = {
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": "claude-sonnet-4-6",
            "max_tokens": 500,
            "system": SYSTEM_PROMPT,
            "messages": conversations[chat_id],
        }

        resp = requests.post(ANTHROPIC_API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        reply_text = data["content"][0]["text"]

        conversations[chat_id].append({"role": "assistant", "content": reply_text})

        await update.message.reply_text(reply_text)

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(
            "Sorry, we're experiencing a technical issue. Please try again "
            f"or contact us directly at {BUSINESS_INFO['contact']}."
        )


def main():
    if not TELEGRAM_TOKEN or not ANTHROPIC_KEY:
        print("ERROR: Please set the TELEGRAM_BOT_TOKEN and ANTHROPIC_API_KEY "
              "environment variables first.")
        return

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(f"Bot running for {BUSINESS_INFO['business_name']}...")
    app.run_polling()


if __name__ == "__main__":
    main()
