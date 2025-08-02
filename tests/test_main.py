# tests/test_main.py
#
# This file contains the test suite for the Forex Trade Alerter script.
# It uses pytest and the pytest-mock plugin to test the application's logic
# in a controlled environment, without making real network requests or
# depending on the current time.
#

import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
import datetime
from src import main  # Assuming your script is in src/main.py

# --- Test Setup ---

# Define a consistent "now" for time-sensitive tests
# This is a time *before* the BoE announcement
MOCK_NOW = datetime.datetime(2025, 8, 7, 10, 0, 0, tzinfo=datetime.timezone.utc)

# --- Test Cases ---

@patch('src.main.requests.post')
def test_send_notification(mock_post):
    """
    Tests that send_notification calls the ntfy.sh API correctly.
    """
    # Arrange
    title = "Test Title"
    message = "Test Message"
    tags = "test_tag"
    
    # Act
    main.send_notification(title, message, tags)

    # Assert
    mock_post.assert_called_once_with(
        f"https://ntfy.sh/{main.NTFY_TOPIC}",
        data=message.encode('utf-8'),
        headers={"Title": title, "Tags": tags}
    )

@patch('src.main.send_notification')
@patch('src.main.yf.download')
def test_check_usdcad_breakout_below_trigger(mock_yf_download, mock_send_notification):
    """
    Tests USD/CAD check when the price is BELOW the trigger.
    It should NOT send a notification.
    """
    # Arrange
    # Simulate yfinance returning data where the last price is below the trigger
    mock_df = pd.DataFrame({'Close': [1.3850, 1.3860, 1.3870]})
    mock_yf_download.return_value = mock_df
    
    # Act
    result = main.check_usdcad_breakout(already_triggered=False)

    # Assert
    assert result is False, "Should return False as the trigger condition is not met."
    mock_yf_download.assert_called_once_with(main.USDCAD_TICKER, period="1d", interval="1m")
    mock_send_notification.assert_not_called()

@patch('src.main.send_notification')
@patch('src.main.yf.download')
def test_check_usdcad_breakout_above_trigger(mock_yf_download, mock_send_notification):
    """
    Tests USD/CAD check when the price is ABOVE the trigger.
    It SHOULD send a notification.
    """
    # Arrange
    # Simulate yfinance returning data where the last price is above the trigger
    trigger_price = main.USDCAD_ENTRY_TRIGGER
    mock_df = pd.DataFrame({'Close': [trigger_price - 0.0010, trigger_price + 0.0010]})
    mock_yf_download.return_value = mock_df

    # Act
    result = main.check_usdcad_breakout(already_triggered=False)

    # Assert
    assert result is True, "Should return True as the trigger condition is met."
    mock_yf_download.assert_called_once_with(main.USDCAD_TICKER, period="1d", interval="1m")
    mock_send_notification.assert_called_once()

@patch('src.main.send_notification')
@patch('src.main.yf.download')
def test_check_usdcad_breakout_no_data(mock_yf_download, mock_send_notification):
    """
    Tests USD/CAD check when yfinance returns no data.
    It should handle the case gracefully and not send a notification.
    """
    # Arrange
    mock_yf_download.return_value = pd.DataFrame() # Empty dataframe

    # Act
    result = main.check_usdcad_breakout(already_triggered=False)

    # Assert
    assert result is False, "Should return False when no data is available."
    mock_send_notification.assert_not_called()

@patch('src.main.datetime', MagicMock())
@patch('src.main.send_notification')
def test_check_boe_announcement_before_alert_time(mock_send_notification):
    """
    Tests the BoE check when the current time is BEFORE the alert window.
    It should NOT send a notification.
    """
    # Arrange
    # Set the mocked "now" to be well before the announcement
    main.datetime.datetime.now.return_value = MOCK_NOW
    
    # Act
    result = main.check_boe_announcement(already_triggered=False)
    
    # Assert
    assert result is False, "Should return False as it's not time yet."
    mock_send_notification.assert_not_called()

@patch('src.main.datetime', MagicMock())
@patch('src.main.send_notification')
def test_check_boe_announcement_within_alert_time(mock_send_notification):
    """
    Tests the BoE check when the current time is WITHIN the alert window.
    It SHOULD send a notification.
    """
    # Arrange
    # Set the mocked "now" to be inside the 5-minute alert window
    alert_time = main.BOE_ANNOUNCEMENT_UTC - datetime.timedelta(minutes=4)
    main.datetime.datetime.now.return_value = alert_time

    # Act
    result = main.check_boe_announcement(already_triggered=False)

    # Assert
    assert result is True, "Should return True as it is now within the alert window."
    mock_send_notification.assert_called_once()
