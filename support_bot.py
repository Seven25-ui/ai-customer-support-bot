"""
AI Customer Support Bot (Telegram)
------------------------------------
Usa ka customizable customer support chatbot para sa bisan unsang
business (restaurant, clinic, shop, etc.) gamit ang Claude AI.

Setup:
    pip install python-telegram-bot anthropic --upgrade

    1. I-set ang imong Telegram Bot Token ug Anthropic API Key sa
       environment variables (dili i-hardcode diri, para safe):

       export TELEGRAM_BOT_TOKEN="imong_token_gikan_sa_BotFather"
       export ANTHROPIC_API_KEY="imong_api_key"

    2. I-edit ang business_info.json (o himuon kung wala pa) para
       ma-customize sa specific business nga imong gi-demo.

    3. Pag-run:
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

# Kada user (chat_id) naa'y kaugalingong conversation history
conversations = {}
MAX_HISTORY = 10  # ka messages nga i-keep per user, para dili modako ang cost


def load_business_info():
    """I-load ang business details - gikan ni ang 'knowledge' sa bot."""
    if os.path.exists(BUSINESS_INFO_FILE):
        with open(BUSINESS_INFO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    # Default template kung wala pa gi-himo ang config
    default = {
        "business_name": "Sample Restaurant",
        "description": "Usa ka casual dining restaurant nga nag-serve og Filipino cuisine.",
        "hours": "Lunes-Domingo, 10AM - 9PM",
        "location": "Cebu City, Philippines",
        "contact": "0917-000-0000",
        "faq": [
            {"q": "Naa ba moy delivery?", "a": "Oo, via Grab/Foodpanda ug direct call/text."},
            {"q": "Naa moy vegetarian options?", "a": "Oo, naa mi'y pipila ka vegetarian dishes sa menu."},
        ],
        "tone": "Friendly, helpful, professional. Taglish/Bisaya ok depende sa customer.",
    }
    with open(BUSINESS_INFO_FILE, "w", encoding="utf-8") as f:
        json.dump(default, f, indent=2, ensure_ascii=False)
    return default


def build_system_prompt(info):
    faq_text = "\n".join(f"Q: {item['q']}\nA: {item['a']}" for item in info["faq"])

    return f"""Ikaw ang AI customer support assistant sa {info['business_name']}.

BUSINESS INFO:
- Description: {info['description']}
- Hours: {info['hours']}
- Location: {info['location']}
- Contact: {info['contact']}

FREQUENTLY ASKED QUESTIONS:
{faq_text}

TONE: {info['tone']}

MGA PATAKARAN:
- Tubaga lang base sa info nga naa sa taas. Kung wala ka kabalo sa tubag, ingna
  nga i-refer nimo sa staff/contact number - ayaw pag-imbento og information.
  - Sulti nga klaro ug summarized ang imong tubag, dili sobra ka taas.
- Kung mangutana ang customer og bisan unsa nga dili related sa business
  (e.g. general knowledge questions), politely i-redirect balik sa topic
  sa business.
"""


BUSINESS_INFO = load_business_info()
SYSTEM_PROMPT = build_system_prompt(BUSINESS_INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Kumusta! Ako si {BUSINESS_INFO['business_name']} Assistant 🤖\n"
        f"Pangutan-a ko bisan unsa bahin sa among business - menu, hours, "
        f"location, o bisan unsa!"
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
            "Pasensya, naay technical issue. Palihug sulayi pag-usab o "
            f"i-contact direkta ang {BUSINESS_INFO['contact']}."
        )


def main():
    if not TELEGRAM_TOKEN or not ANTHROPIC_KEY:
        print("ERROR: I-set una ang TELEGRAM_BOT_TOKEN ug ANTHROPIC_API_KEY "
              "nga environment variables.")
        return

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(f"Bot running para sa {BUSINESS_INFO['business_name']}...")
    app.run_polling()


if __name__ == "__main__":
    main()
