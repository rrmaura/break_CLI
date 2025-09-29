#!/usr/bin/env python3
"""
Simple terminal break tracker with notifications and daily email reports.
Usage: python3 break_tracker.py [minutes]
"""

import sys
import time
import json
import os
import subprocess
from datetime import datetime, timedelta
import threading
import smtplib
from email.mime.text import MIMEText
from pathlib import Path
import yaml

# Configuration file paths
CONFIG_DIR = Path.home() / ".config" / "break_tracker"
CONFIG_FILE = CONFIG_DIR / "config.yaml"
DATA_FILE = CONFIG_DIR / "break_data.json"

# Default configuration
DEFAULT_CONFIG = {
    "email": {
        "enabled": False,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "from_email": "your_email@gmail.com",
        "to_email": "your_email@gmail.com",
        "password": "your_app_password",  # Use app-specific password for Gmail
    },
    "default_snooze_minutes": 5,
}


def ensure_config():
    """Create config directory and files if they don't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w") as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, indent=2)
        print(f"Created config file at {CONFIG_FILE}")
        print("Please edit it to enable email notifications if desired.")
        return False
    return True


def load_config():
    """Load configuration from file."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return yaml.safe_load(f)
    return DEFAULT_CONFIG


def load_break_data():
    """Load today's break data."""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            # Check if data is from today
            today = datetime.now().strftime("%Y-%m-%d")
            if data.get("date") == today:
                return data

    # Return new data structure for today
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "total_minutes": 0,
        "breaks": [],
    }


def save_break_data(data):
    """Save break data to file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def send_notification(title, message):
    """Send desktop notification on Fedora."""
    try:
        subprocess.run(
            [
                "notify-send",
                "--urgency=critical",
                "--app-name=Break Tracker",
                title,
                message,
            ],
            check=True,
        )
    except subprocess.CalledProcessError:
        print(
            f"\n⚠️  Notification failed. Install libnotify: sudo dnf install libnotify"
        )
        print(f"📢 {title}: {message}")
    except FileNotFoundError:
        print(
            f"\n⚠️  notify-send not found. Install it with: sudo dnf install libnotify"
        )
        print(f"📢 {title}: {message}")


def send_daily_email(yesterday_minutes):
    """Send daily email report."""
    config = load_config()
    if not config["email"]["enabled"]:
        return

    try:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        msg = MIMEText("")
        msg["Subject"] = f"Break time {yesterday}: {yesterday_minutes} minutes"
        msg["From"] = config["email"]["from_email"]
        msg["To"] = config["email"]["to_email"]

        with smtplib.SMTP(
            config["email"]["smtp_server"], config["email"]["smtp_port"]
        ) as server:
            server.starttls()
            server.login(config["email"]["from_email"], config["email"]["password"])
            server.send_message(msg)

        print(f"✉️  Daily report sent: {yesterday_minutes} minutes")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


def check_and_send_yesterday_report():
    """Check if we need to send yesterday's report."""
    # Load yesterday's data if it exists
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            if data.get("date") == yesterday and not data.get("report_sent", False):
                send_daily_email(data["total_minutes"])
                data["report_sent"] = True
                save_break_data(data)


def format_time(minutes):
    """Format minutes into hours and minutes."""
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}h {mins}m"


def run_break(minutes):
    """Run a break timer with snooze functionality."""
    data = load_break_data()
    config = load_config()

    break_start = datetime.now()
    snooze_count = 0
    total_break_minutes = minutes

    print(f"\n🚀 Starting {minutes} minute break")
    print(
        f"⏰ Will notify at {(break_start + timedelta(minutes=minutes)).strftime('%H:%M:%S')}"
    )
    print(f"\n💡 Press Ctrl+C to end break early\n")

    try:
        while True:
            # Wait for the break duration
            remaining = minutes * 60
            while remaining > 0:
                mins, secs = divmod(remaining, 60)
                timer = f"⏳ {mins:02d}:{secs:02d} remaining"
                print(f"\r{timer}", end="", flush=True)
                time.sleep(1)
                remaining -= 1

            print("\r" + " " * 30 + "\r", end="")  # Clear the timer line

            # Break is done, send notification
            if snooze_count == 0:
                send_notification(
                    "Break's over! 🎯",
                    f"Your {minutes} minute break is done. Back to work!",
                )
                print(f"\n✅ Break complete! ({minutes} minutes)")
            else:
                accumulated = total_break_minutes
                send_notification(
                    f"Snooze #{snooze_count + 1} over! ⏰",
                    f"Total break time: {accumulated} minutes",
                )
                print(f"\n⏰ Snooze #{snooze_count + 1} complete!")
                print(f"📊 Total break time: {format_time(accumulated)}")

            # Ask for snooze
            print("\n🔄 Options:")
            print("  [Enter] = Back to work")
            print("  [number] = Snooze for X minutes")
            print("  [s/S] = Snooze for 5 minutes (default)")

            try:
                response = input("👉 ").strip().lower()

                if response == "":
                    # End break
                    break
                elif response == "s":
                    # Default snooze
                    minutes = config["default_snooze_minutes"]
                    snooze_count += 1
                    total_break_minutes += minutes
                    print(f"\n😴 Snoozing for {minutes} more minutes...")
                    print(f"📈 Snooze count: {snooze_count}")
                else:
                    # Custom snooze duration
                    try:
                        minutes = int(response)
                        if minutes > 0:
                            snooze_count += 1
                            total_break_minutes += minutes
                            print(f"\n😴 Snoozing for {minutes} more minutes...")
                            print(f"📈 Snooze count: {snooze_count}")
                        else:
                            break
                    except ValueError:
                        break

            except KeyboardInterrupt:
                print("\n\n⚠️  Snooze cancelled")
                break

    except KeyboardInterrupt:
        # Calculate actual time spent
        actual_minutes = int((datetime.now() - break_start).total_seconds() / 60)
        total_break_minutes = actual_minutes
        print(f"\n\n⚠️  Break ended early after {actual_minutes} minutes")

    # Save break data
    data["total_minutes"] += total_break_minutes
    data["breaks"].append(
        {
            "start": break_start.isoformat(),
            "minutes": total_break_minutes,
            "snoozes": snooze_count,
        }
    )
    save_break_data(data)

    # Show summary
    print(f"\n📊 Today's break summary:")
    print(f"   • This break: {format_time(total_break_minutes)}")
    print(f"   • Total today: {format_time(data['total_minutes'])}")
    print(f"   • Break count: {len(data['breaks'])}")

    if snooze_count > 0:
        print(f"   • Snoozes this break: {snooze_count}")


def show_today_stats():
    """Show today's break statistics."""
    data = load_break_data()
    print(f"\n📊 Today's Statistics ({data['date']})")
    print(f"   • Total break time: {format_time(data['total_minutes'])}")
    print(f"   • Number of breaks: {len(data['breaks'])}")

    if data["breaks"]:
        print(f"\n📝 Break history:")
        for i, b in enumerate(data["breaks"], 1):
            start_time = datetime.fromisoformat(b["start"]).strftime("%H:%M")
            snooze_info = f" ({b['snoozes']} snoozes)" if b["snoozes"] > 0 else ""
            print(f"   {i}. {start_time} - {b['minutes']}m{snooze_info}")


def main():
    """Main entry point."""
    if not ensure_config():
        print(
            "\n⚠️  Please configure email settings in ~/.config/break_tracker/config.yaml"
        )
        print(
            "   Set 'enabled': true and add your email credentials for daily reports\n"
        )

    # Check for yesterday's report
    check_and_send_yesterday_report()

    if len(sys.argv) < 2:
        # No arguments, show stats
        show_today_stats()
        print("\n💡 Usage: python3 break_tracker.py [minutes]")
        print("   Example: python3 break_tracker.py 7")
        return

    try:
        minutes = int(sys.argv[1])
        if minutes <= 0:
            print("❌ Please specify a positive number of minutes")
            return
        run_break(minutes)
    except ValueError:
        if sys.argv[1] in ["stats", "status", "s"]:
            show_today_stats()
        else:
            print(f"❌ Invalid input: {sys.argv[1]}")
            print("💡 Usage: python3 break_tracker.py [minutes|stats]")


if __name__ == "__main__":
    main()
