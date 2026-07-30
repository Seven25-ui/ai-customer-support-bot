# AI Customer Support Bot (Telegram)

A customizable AI-powered customer support chatbot built with Python, the Telegram Bot API, and Claude (Anthropic). Designed to be deployed for any small business — restaurants, clinics, retail shops, etc. — by editing a single configuration file, with no code changes required.

## 🎯 The Problem This Solves

Small businesses lose customers to slow response times on repetitive questions — hours, location, menu/services, delivery options, pricing. This bot answers those questions instantly, 24/7, using the business's own information as its knowledge base (no hallucinated answers).

## ✨ Features

- **Instant AI responses** powered by Claude, grounded strictly in the business's provided FAQ/info
- **Per-business customization** via a single `business_info.json` file — swap from a restaurant to a clinic to a shop in minutes, zero code changes
- **Conversation memory** — the bot remembers context within a chat session for natural, multi-turn conversations
- **Graceful error handling** — if the AI service is unavailable, customers are redirected to a real contact number instead of getting a broken experience
- **Guardrails** — the bot stays on-topic and redirects unrelated questions back to the business, and admits when it doesn't know something instead of making up answers

## 🛠️ Tech Stack

- Python 3
- `python-telegram-bot` — Telegram Bot API wrapper
- Claude API (Anthropic) via direct HTTP requests
- JSON-based configuration (no database required for MVP)

## 🚀 Setup

1. Clone this repo and install dependencies:
   ```bash
   pip install python-telegram-bot requests --upgrade
   ```

2. Create a bot via [@BotFather](https://t.me/BotFather) on Telegram and get your bot token.

3. Get a Claude API key from [console.anthropic.com](https://console.anthropic.com).

4. Set your credentials as environment variables:
   ```bash
   export TELEGRAM_BOT_TOKEN="your_token_here"
   export ANTHROPIC_API_KEY="your_key_here"
   ```

5. Edit `business_info.json` with your business's real details (or let the bot generate a default template on first run).

6. Run the bot:
   ```bash
   python support_bot.py
   ```

## ⚙️ Customization

All business-specific knowledge lives in `business_info.json`:

```json
{
  "business_name": "Your Business Name",
  "description": "Short description of the business",
  "hours": "Operating hours",
  "location": "Address",
  "contact": "Phone/contact number",
  "faq": [
    {"q": "Question customers commonly ask", "a": "The answer"}
  ],
  "tone": "How the bot should sound"
}
```

No code changes needed to onboard a new client — just replace this file.

## 📈 Possible Extensions

- Multi-language support (auto-detect customer language)
- Appointment/reservation booking integration
- Order-taking with a connected menu/inventory system
- Handoff to a human agent for complex queries
- Analytics dashboard for common customer questions

## 📄 License

MIT — free to use and adapt.

---

*Built as part of exploring practical AI automation for small businesses.*

