# ✈️ Flight Status Notifier

**Flight Status Notifier** is a lightweight Python tool that fetches real-time flight data from the **Aviationstack API** and sends formatted updates directly to **Telegram** via a bot.

It works in two modes:

* **Local mode** using `config.json`
* **Scheduled mode** using **GitHub Actions** (fully automated flight checks)

This makes it perfect for tracking your flights, monitoring a friend’s journey, or automatically receiving flight updates without running your computer.

---

## 🚀 Features

* Real-time flight tracking using the free Aviationstack API
* Telegram bot notifications
* Multi-flight support
* Local + GitHub Actions support
* Safe secret handling (no keys in the repo)
* Python 3.9+ compatible

# Local Configuration

Create a **config.json** file in the project root (never commit this file):

```json
{
  "aviationstack_api_key": "YOUR_API_KEY",
  "telegram_bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
  "telegram_chat_id": 123456789,
  "flights": ["6E203", "UK811"]
}
```

Run the script:

```bash
python flight_status_notifier.py
```

You should receive a Telegram message with the flight status.

---

# GitHub Actions Scheduler 

To run the notifier automatically on a schedule (e.g., every 2 hours):

## Add GitHub Secrets

Go to:

**Repository → Settings → Secrets and variables → Actions → Secrets**

Add these:

| Name                      | Value                      |
| ------------------------- | -------------------------- |
| `AVIATIONSTACK_API_KEY` | Your Aviationstack API key |
| `TELEGRAM_BOT_TOKEN`    | Your Telegram bot token    |
| `TELEGRAM_CHAT_ID`      | Your numeric chat ID       |

---

## Add GitHub Variable

Go to:

**Settings → Secrets and variables → Actions → Variables**

Add:

| Name             | Value (comma-separated flights) |
| ---------------- | ------------------------------- |
| `FLIGHT_CODES` | `6E203,UK811`                 |

---

## The GitHub Workflow

Included at:

```
.github/workflows/flight-status.yml
```

The workflow:

* Runs every 2 hours (UTC)
* Installs Python
* Installs dependencies
* Executes the notifier with your secrets

Modify the cron schedule here:

```yaml
cron: "0 */2 * * *"
```

Examples:

| Schedule       | Cron            |
| -------------- | --------------- |
| Every hour     | `0 * * * *`   |
| Every 6 hours  | `0 */6 * * *` |
| 8 AM IST daily | `30 2 * * *`  |
