#!/usr/bin/env python3
import json
import os
import sys
from typing import Optional, Dict, Any, List
from datetime import datetime
import requests

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

AVIATIONSTACK_BASE_URL = "http://api.aviationstack.com/v1/flights"


def load_config() -> Dict[str, Any]:
    """
    Load config from environment variables (for GitHub Actions)
    or from config.json (for local runs).
    """

    # 1. Try environment variables first (GitHub Actions / CI)
    env_api_key = os.getenv("AVIATIONSTACK_API_KEY")
    env_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    env_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    env_flights = os.getenv("FLIGHT_CODES")

    if env_api_key and env_bot_token and env_chat_id and env_flights:
        flights_list = [
            f.strip() for f in env_flights.split(",") if f.strip()
        ]
        if not flights_list:
            print("FLIGHT_CODES env var is set but empty.", file=sys.stderr)
            sys.exit(1)

        return {
            "aviationstack_api_key": env_api_key,
            "telegram_bot_token": env_bot_token,
            "telegram_chat_id": env_chat_id,
            "flights": flights_list,
        }

    # 2. Fallback: local config.json (for local development)
    if not os.path.exists(CONFIG_PATH):
        print(
            "No environment variables set and config.json not found. "
            "Set env vars or create config.json.",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    required = [
        "aviationstack_api_key",
        "telegram_bot_token",
        "telegram_chat_id",
        "flights",
    ]

    for key in required:
        if key not in cfg or not cfg[key]:
            print(f"Missing '{key}' in config.json", file=sys.stderr)
            sys.exit(1)

    return cfg


def fetch_flight_status(api_key: str, flight_iata: str) -> Optional[Dict[str, Any]]:
    """Call Aviationstack API for a specific IATA flight number"""

    params = {
        "access_key": api_key,
        "flight_iata": flight_iata,
    }

    try:
        r = requests.get(AVIATIONSTACK_BASE_URL, params=params, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"[{flight_iata}] API request failed: {e}", file=sys.stderr)
        return None

    data = r.json()
    flights = data.get("data") or []

    if not flights:
        print(f"[{flight_iata}] No data from API", file=sys.stderr)
        return None

    return flights[0]


def parse_time(iso_str: Optional[str]) -> str:
    """Convert ISO time to readable format"""
    if not iso_str:
        return "N/A"

    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso_str


def format_msg(flight: Dict[str, Any], code: str) -> str:
    """Format Telegram message text"""

    airline = (flight.get("airline") or {}).get("name") or "Unknown Airline"
    status = (flight.get("flight_status") or "unknown").upper()
    flight_num = (flight.get("flight") or {}).get("iata") or code

    dep = flight.get("departure") or {}
    arr = flight.get("arrival") or {}

    dep_airport = dep.get("airport") or "Unknown"
    dep_iata = dep.get("iata") or "-"
    dep_sched = parse_time(dep.get("scheduled"))
    dep_est = parse_time(dep.get("estimated"))

    arr_airport = arr.get("airport") or "Unknown"
    arr_iata = arr.get("iata") or "-"
    arr_sched = parse_time(arr.get("scheduled"))
    arr_est = parse_time(arr.get("estimated"))

    msg = [
        f"✈️ *Flight Update*: {flight_num}",
        f"Airline: {airline}",
        "",
        f"Status: *{status}*",
        "",
        f"Departure: {dep_airport} ({dep_iata})",
        f" • Scheduled: {dep_sched}",
        f" • Estimated: {dep_est}",
        "",
        f"Arrival: {arr_airport} ({arr_iata})",
        f" • Scheduled: {arr_sched}",
        f" • Estimated: {arr_est}",
    ]

    if dep.get("delay") is not None:
        msg.append(f"\nDelay reported: {dep.get('delay')} min")

    return "\n".join(msg)


def send_telegram(bot_token: str, chat_id: str, text: str) -> bool:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    try:
        r = requests.post(
            url,
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=15,
        )
        r.raise_for_status()
        return True
    except Exception as e:
        print(f"Telegram send error: {e}", file=sys.stderr)
        return False


def main():
    cfg = load_config()
    api_key = cfg["aviationstack_api_key"]
    bot_token = cfg["telegram_bot_token"]
    chat_id = str(cfg["telegram_chat_id"])
    flights = cfg["flights"]

    for code in flights:
        print(f"Checking {code}...")

        info = fetch_flight_status(api_key, code)

        if not info:
            send_telegram(bot_token, chat_id, f"⚠️ Could not fetch info for {code}")
            continue

        msg = format_msg(info, code)
        ok = send_telegram(bot_token, chat_id, msg)

        if ok:
            print(f"Sent update for {code}")
        else:
            print(f"Failed to send for {code}")


if __name__ == "__main__":
    main()