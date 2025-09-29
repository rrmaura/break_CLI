#!/usr/bin/env python3
"""
Test script for email functionality in break_tracker.py

This script provides both mocked tests (safe to run) and real email tests.
Run with: python3 test_email.py [--real-email]
"""

import unittest
from unittest.mock import patch, MagicMock
import smtplib
import tempfile
import os
import yaml
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Import the functions we want to test
from break_tracker import send_daily_email, load_config, CONFIG_FILE, DEFAULT_CONFIG


class TestEmailFunctionality(unittest.TestCase):
    """Test the email sending functionality with mocked SMTP."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary config for testing
        self.test_config = {
            "email": {
                "enabled": True,
                "smtp_server": "smtp.test.com",
                "smtp_port": 587,
                "from_email": "test@example.com",
                "to_email": "recipient@example.com",
                "password": "test_password",
            }
        }

    @patch("break_tracker.load_config")
    @patch("smtplib.SMTP")
    def test_send_daily_email_success(self, mock_smtp, mock_load_config):
        """Test successful email sending."""
        # Setup mocks
        mock_load_config.return_value = self.test_config
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Test the function
        with patch("builtins.print") as mock_print:
            send_daily_email(120)  # 120 minutes

        # Verify SMTP calls
        mock_smtp.assert_called_once_with("smtp.test.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@example.com", "test_password")
        mock_server.send_message.assert_called_once()

        # Verify success message was printed
        mock_print.assert_called_with("✉️  Daily report sent: 120 minutes")

        # Verify the email message
        sent_message = mock_server.send_message.call_args[0][0]
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        expected_subject = f"Break time {yesterday}: 120 minutes"

        self.assertEqual(sent_message["Subject"], expected_subject)
        self.assertEqual(sent_message["From"], "test@example.com")
        self.assertEqual(sent_message["To"], "recipient@example.com")

    @patch("break_tracker.load_config")
    def test_send_daily_email_disabled(self, mock_load_config):
        """Test that email is not sent when disabled."""
        # Setup config with email disabled
        disabled_config = self.test_config.copy()
        disabled_config["email"]["enabled"] = False
        mock_load_config.return_value = disabled_config

        with patch("smtplib.SMTP") as mock_smtp:
            send_daily_email(60)

        # Verify SMTP was never called
        mock_smtp.assert_not_called()

    @patch("break_tracker.load_config")
    @patch("smtplib.SMTP")
    def test_send_daily_email_connection_error(self, mock_smtp, mock_load_config):
        """Test email sending with connection error."""
        mock_load_config.return_value = self.test_config
        mock_smtp.side_effect = smtplib.SMTPConnectError("Connection failed")

        with patch("builtins.print") as mock_print:
            send_daily_email(30)

        # Verify error message was printed
        mock_print.assert_called_with("❌ Failed to send email: Connection failed")

    @patch("break_tracker.load_config")
    @patch("smtplib.SMTP")
    def test_send_daily_email_auth_error(self, mock_smtp, mock_load_config):
        """Test email sending with authentication error."""
        mock_load_config.return_value = self.test_config
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(
            535, "Authentication failed"
        )

        with patch("builtins.print") as mock_print:
            send_daily_email(45)

        # Verify error message was printed
        error_call = mock_print.call_args_list[-1][0][0]
        self.assertIn("❌ Failed to send email:", error_call)
        self.assertIn("Authentication failed", error_call)


class TestRealEmailSending(unittest.TestCase):
    """Test real email sending (only run with --real-email flag)."""

    def setUp(self):
        """Check if real email testing is enabled."""
        self.real_email_enabled = "--real-email" in sys.argv
        if not self.real_email_enabled:
            self.skipTest(
                "Real email testing disabled. Use --real-email flag to enable."
            )

    def test_real_email_with_current_config(self):
        """Test sending a real email with current configuration."""
        if not CONFIG_FILE.exists():
            self.skipTest("No config file found. Please create config.yaml first.")

        config = load_config()
        if not config.get("email", {}).get("enabled", False):
            self.skipTest(
                "Email is disabled in config. Enable it to test real email sending."
            )

        print("\n🧪 Testing real email sending...")
        print("⚠️  This will send an actual email!")

        # Send a test email
        try:
            send_daily_email(123)  # Test with 123 minutes
            print("✅ Real email test completed - check your inbox!")
        except Exception as e:
            self.fail(f"Real email test failed: {e}")


def run_email_test_suite():
    """Run a comprehensive email test with user-friendly output."""
    print("🧪 Break Tracker Email Test Suite")
    print("=" * 40)

    # Check if config exists
    if CONFIG_FILE.exists():
        config = load_config()
        email_config = config.get("email", {})
        print(f"📧 Email enabled: {email_config.get('enabled', False)}")
        print(f"📮 SMTP server: {email_config.get('smtp_server', 'Not set')}")
        print(f"📫 From email: {email_config.get('from_email', 'Not set')}")
        print(f"📬 To email: {email_config.get('to_email', 'Not set')}")
    else:
        print("⚠️  No config file found")

    print("\n🔍 Running mocked email tests...")

    # Run mocked tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEmailFunctionality)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if "--real-email" in sys.argv:
        print("\n🚀 Running real email test...")
        real_suite = unittest.TestLoader().loadTestsFromTestCase(TestRealEmailSending)
        real_result = runner.run(real_suite)

        if real_result.wasSuccessful():
            print("\n✅ All tests passed! Check your email inbox.")
        else:
            print("\n❌ Real email test failed. Check your configuration.")
    else:
        print(
            "\n💡 To test real email sending, run: python3 test_email.py --real-email"
        )

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_email_test_suite()
    sys.exit(0 if success else 1)
