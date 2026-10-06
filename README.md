# AI Customer Support Bot (Telegram)

A customizable AI customer support chatbot built with Python, the Telegram Bot API, and Claude (Anthropic). It can be set up for any small business (restaurants, clinics, retail shops, and more) by editing a single configuration file, with no code changes required.

## 🎯 The Problem This Solves

Small businesses lose customers to slow replies on repetitive questions: hours, location, menu or services, delivery, payment options. This bot answers those questions instantly, 24/7, using the business's own information as its knowledge base.

## ✨ Features

- **Instant AI replies** powered by Claude, based on the business's own FAQ and info
- **Per-business customization** through one `business_info.json` file. Switch from a restaurant to a clinic to a shop in minutes, with no code changes
- **Conversation memory**: the bot remembers recent messages in a chat for natural, multi-turn conversations
- **Guardrails**: it stays on-topic, redirects unrelated questions back to the business, and says so when it doesn't know something instead of guessing
- **Multilingual replies**: answers in the customer's language when it can (English, Tagalog, Bisaya)
- **Handles many customers at once**: API calls run without blocking the bot, and a simple per-customer rate limit prevents spam
- **Graceful error handling**: if the AI service is unavailable, the customer is pointed to the business's real contact number
- **Config validation**: clear error messages if `business_info.json` is missing a field
- **`/reset` command** so customers can start a fresh conversation

## 🎬 Demo

> Add a screenshot or screen recording of the bot here.

Example conversation (sample restaurant config):

> **Customer:** What time do you open?
> **Bot:** We're open every day from 10 AM to 9 PM. Anything else I can help with?
>
> **Customer:** Naa mo delivery?
> **Bot:** Oo, naa mi delivery via Grab/Foodpanda, o pwede ra pud mo-call or text sa 0917-000-0000.
>
> **Customer:** Do you serve sushi?
> **Bot:** I don't have that information. Please contact us at 0917-000-0000 and our staff will be happy to help.

*Replace these replies with real output from your bot.*

## 🛠️ Tech Stack

- Python 3
- `python-telegram-bot` for the Telegram Bot API
- Claude API (Anthropic) via HTTP requests
- JSON configuration (no database needed)

## 🚀 Setup

1. Clone this repo and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a bot with [@BotFather](https://t.me/BotFather) on Telegram and copy the bot token.

3. Get a Claude API key from [console.anthropic.com](https://console.anthropic.com).

4. Set your credentials as environment variables:
   ```bash
   export TELEGRAM_BOT_TOKEN="your_token_here"
   export ANTHROPIC_API_KEY="your_key_here"
   ```
   Optional: choose a different Claude model with `export CLAUDE_MODEL="model-name"`. The default is `claude-sonnet-4-6`.

5. Edit `business_info.json` with the business's real details. If the file doesn't exist, the bot creates a sample one on first run.

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

To set the bot up for a new client, just replace this file. The more complete the FAQ, the better the answers.

## ☁️ Deployment

For 24/7 uptime, run the bot on a small server or a free/low-cost host (a VPS, Render, or a Raspberry Pi) instead of a personal computer or phone.

- **Costs:** Telegram bots are free to run. Claude API usage is billed per message and is usually small for small-business traffic.
- **Security:** never commit your tokens or API keys. Use environment variables.

## ⚠️ Current Limitations

- Conversation history is kept in memory and resets when the bot restarts
- The bot only knows what is in `business_info.json`. Keep it up to date
- It uses polling, which is fine for small businesses. Very high traffic would call for webhooks and a database

## 📈 Possible Extensions

- Appointment or reservation booking
- Order-taking with a connected menu or inventory
- Handoff to a human agent for complex questions
- Analytics on the most common customer questions
- Persistent conversation storage

## 📄 License

MIT. Free to use and adapt.

---

**Need this set up for your business?** I'm available for custom setup on [Upwork](https://www.upwork.com/freelancers/~01498b9e52730e5da9).
