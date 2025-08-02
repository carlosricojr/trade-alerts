# Forex Trade Alerter
#
# This script automates the monitoring of the two trading opportunities
# identified in your "Forex Volatility Trade Optimization" document.
#
# It checks for two primary conditions:
#   1. A price breakout for USD/CAD above the specified resistance level.
#   2. The time of the Bank of England (BoE) interest rate decision for GBP/USD.
#
# When a condition is met, it sends a push notification to your phone.
#

# --- SETUP INSTRUCTIONS ---
#
# 1. Install necessary Python libraries:
#    pip install requests yfinance pandas
#
# 2. Install the ntfy app on your phone (available on iOS and Android):
#    - Website: https://ntfy.sh/
#    - Once installed, "subscribe" to a topic. This can be any name you want,
#      but make it unique and hard to guess (e.g., "my-fx-alerts-Abc123").
#
# 3. Update the CONFIG section below:
#    - Set the `NTFY_TOPIC` variable to the topic name you subscribed to.
#    - Verify the trade parameters are correct.
#
# 4. Run the script from your terminal:
#    python your_script_name.py
#
# The script will then run continuously, checking prices every minute.

import requests
import yfinance as yf
import pandas as pd
import time
import datetime

# --- CONFIGURATION ---

# Notification Settings
# Replace "your-secret-topic-name" with the topic you subscribed to in the ntfy app.
NTFY_TOPIC = "carlos-fx-alerts-1066"

# Trade Parameters for USD/CAD
USDCAD_TICKER = "CAD=X"
USDCAD_ENTRY_TRIGGER = 1.3890

# Trade Parameters for GBP/USD
GBPUSD_TICKER = "GBPUSD=X"
# Bank of England Announcement Time (August 7, 2025, 11:00 UTC)
BOE_ANNOUNCEMENT_UTC = datetime.datetime(2025, 8, 7, 11, 0, 0, tzinfo=datetime.timezone.utc)

# Script Settings
CHECK_INTERVAL_SECONDS = 60  # Check prices every 60 seconds

# --- CORE LOGIC ---

def send_notification(title, message, tags=""):
    """
    Sends a push notification using ntfy.sh.
    """
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode('utf-8'),
            headers={
                "Title": title,
                "Tags": tags, # e.g., "warning", "info", "heavy_check_mark"
            }
        )
        print(f"[{datetime.datetime.now()}] Notification Sent: {title}")
    except Exception as e:
        print(f"Error sending notification: {e}")

def check_usdcad_breakout(already_triggered):
    """
    Checks if USD/CAD has closed above the entry trigger price.
    Uses 1-minute interval data to approximate a candle close.
    """
    if already_triggered:
        return True # Don't send duplicate alerts

    try:
        # Fetch the last few minutes of data to check the most recent price
        data = yf.download(USDCAD_TICKER, period="1d", interval="1m", auto_adjust=True, progress=False)
        if data.empty:
            print(f"[{datetime.datetime.now()}] No data for USD/CAD, skipping check.")
            return False

        last_price = data['Close'].iloc[-1].item()
        print(f"[{datetime.datetime.now()}] Checking USD/CAD: Last Price = {last_price:.4f}, Trigger = {USDCAD_ENTRY_TRIGGER:.4f}")

        if last_price > USDCAD_ENTRY_TRIGGER:
            title = "🚨 USD/CAD TRADE ALERT 🚨"
            message = f"USD/CAD has broken above the entry trigger of {USDCAD_ENTRY_TRIGGER}. Last price: {last_price:.4f}"
            send_notification(title, message, tags="warning")
            return True # Mark as triggered
    except Exception as e:
        print(f"Error checking USD/CAD: {e}")

    return False

def check_boe_announcement(already_triggered):
    """
    Checks if it's time for the BoE announcement and sends an alert.
    """
    if already_triggered:
        return True # Don't send duplicate alerts

    now_utc = datetime.datetime.now(datetime.timezone.utc)

    # Alert a few minutes before the event
    alert_window_start = BOE_ANNOUNCEMENT_UTC - datetime.timedelta(minutes=5)

    print(f"[{datetime.datetime.now()}] Checking BoE time: Now (UTC) = {now_utc.strftime('%Y-%m-%d %H:%M')}, Event (UTC) = {BOE_ANNOUNCEMENT_UTC.strftime('%Y-%m-%d %H:%M')}")

    if now_utc >= alert_window_start:
        title = "🔔 GBP/USD EVENT ALERT 🔔"
        message = f"Bank of England announcement is at 11:00 UTC. Monitor GBP/USD for post-announcement low to form and break."
        send_notification(title, message, tags="info")
        return True # Mark as triggered

    return False

def main():
    """
    Main loop to run the monitoring checks.
    """
    print("--- Forex Trade Alerter Started ---")
    print(f"Monitoring USD/CAD for breakout above {USDCAD_ENTRY_TRIGGER}")
    print(f"Monitoring for BoE announcement on {BOE_ANNOUNCEMENT_UTC.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"Notifications will be sent to ntfy.sh topic: {NTFY_TOPIC}")
    print("-----------------------------------")

    # State flags to prevent sending repeated notifications
    usdcad_triggered = False
    boe_triggered = False

    while True:
        try:
            # Only check if the alert hasn't already been sent
            if not usdcad_triggered:
                usdcad_triggered = check_usdcad_breakout(usdcad_triggered)

            if not boe_triggered:
                boe_triggered = check_boe_announcement(boe_triggered)

            # If all alerts have been sent, the script's job is done.
            if usdcad_triggered and boe_triggered:
                print("All trade alerts have been triggered. Shutting down script.")
                break

            # Wait for the next interval
            time.sleep(CHECK_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print("\nScript stopped by user.")
            break
        except Exception as e:
            print(f"An unexpected error occurred in the main loop: {e}")
            # Wait a bit before retrying to avoid spamming errors
            time.sleep(60)

if __name__ == "__main__":
    main()
