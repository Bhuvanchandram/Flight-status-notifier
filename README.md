# Flight Status Notifier ✈️

A simple, local-first Python script that sends real-time flight status updates to Telegram.
It uses the Aviationstack API to fetch live departure/arrival details and pushes formatted notifications via a Telegram bot.

## Features

- Real-time flight tracking using free Aviationstack API
- Telegram alerts for flight status, delays, schedule changes
- Supports multiple flights
- Runs locally — no server required
- Easy to automate with Task Scheduler or cron
- Python 3.9+ compatible

## Configuration

Create a `config.json` file (excluded from GitHub) with:

- Aviationstack API key
- Telegram bot token
- Telegram chat ID
- List of flight numbers to track

See `config.example.json` for structure.

---

Made for travel convenience and automation.
