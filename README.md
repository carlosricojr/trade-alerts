# Trade Alerts

Automated forex trade alerting system that monitors USD/CAD and GBP/USD for specific trading opportunities.

## Features

- Monitors USD/CAD for breakout above 1.3890
- Alerts 5 minutes before Bank of England announcement (Aug 7, 2025, 11:00 UTC)
- Push notifications via ntfy.sh
- Auto-shutdown after all alerts triggered

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Install ntfy app on your phone and subscribe to topic: `carlos-fx-alerts-1066`

3. Run the monitor:
   ```bash
   uv run src/main.py
   ```

## Configuration

Edit `src/main.py` to modify:
- `NTFY_TOPIC`: Your ntfy notification topic
- `USDCAD_ENTRY_TRIGGER`: USD/CAD breakout level (default: 1.3890)
- `CHECK_INTERVAL_SECONDS`: Price check frequency (default: 60s)

## Testing

```bash
uv run pytest
```

## Requirements

- Python 3.9+
- UV package manager
- Active internet connection for price data and notifications