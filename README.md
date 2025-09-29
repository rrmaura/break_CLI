# Break Tracker CLI

A simple terminal-based break tracker with desktop notifications and optional daily email reports. Perfect for managing work breaks and maintaining healthy productivity habits.

## Features

- ⏰ Customizable break timers with desktop notifications
- 🔄 Snooze functionality for extended breaks
- 📊 Daily break statistics and history
- 📧 Optional daily email reports
- 💾 Persistent data storage
- 🔧 YAML-based configuration

## Installation

1. Clone or download this repository
2. Install required Python packages:
   ```bash
   pip install pyyaml
   ```
3. For desktop notifications on Fedora/RHEL:
   ```bash
   sudo dnf install libnotify
   ```

## Quick Start

1. Run the program for the first time to create the configuration:
   ```bash
   python3 break_tracker.py 5
   ```

2. This will create a config file at `~/.config/break_tracker/config.yaml`

3. Edit the configuration file if you want email notifications (see Configuration section below)

## Usage

### Start a Break Timer
```bash
python3 break_tracker.py [minutes]
```

Examples:
```bash
python3 break_tracker.py 7     # 7-minute break
python3 break_tracker.py 15    # 15-minute break
```

### View Today's Statistics
```bash
python3 break_tracker.py       # Show stats and usage
python3 break_tracker.py stats # Show detailed stats
```

### During a Break

When your break timer ends, you'll get a desktop notification and see options:

- **[Enter]** - End break and return to work
- **[number]** - Snooze for X minutes (e.g., type `3` for 3 more minutes)
- **[s/S]** - Quick snooze for default duration (5 minutes)
- **[Ctrl+C]** - End break early

## Configuration

The configuration file is located at `~/.config/break_tracker/config.yaml`. Here's how to set it up:

### Basic Configuration

```yaml
email:
  enabled: false
  smtp_server: smtp.gmail.com
  smtp_port: 587
  from_email: your_email@gmail.com
  to_email: your_email@gmail.com
  password: your_app_password
default_snooze_minutes: 5
```

### Email Notifications Setup

To enable daily email reports with your break statistics:

1. **For Gmail users:**
   - Enable 2-factor authentication on your Google account
   - Generate an App Password: [Google App Passwords](https://myaccount.google.com/apppasswords)
   - Use this App Password (not your regular password) in the config

2. **Edit your config file:**
   ```yaml
   email:
     enabled: true
     smtp_server: smtp.gmail.com
     smtp_port: 587
     from_email: youremail@gmail.com
     to_email: youremail@gmail.com  # Can be different email
     password: your_16_character_app_password
   default_snooze_minutes: 5  # Default snooze duration in minutes
   ```

3. **For other email providers:**
   - Update `smtp_server` and `smtp_port` accordingly
   - Common settings:
     - **Outlook/Hotmail:** `smtp-mail.outlook.com:587`
     - **Yahoo:** `smtp.mail.yahoo.com:587`
     - **Custom SMTP:** Contact your email provider

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `email.enabled` | Enable/disable email reports | `false` |
| `email.smtp_server` | SMTP server address | `smtp.gmail.com` |
| `email.smtp_port` | SMTP server port | `587` |
| `email.from_email` | Sender email address | `your_email@gmail.com` |
| `email.to_email` | Recipient email address | `your_email@gmail.com` |
| `email.password` | Email password (use App Password for Gmail) | `your_app_password` |
| `default_snooze_minutes` | Default snooze duration | `5` |

## Data Storage

The program stores data in `~/.config/break_tracker/`:
- `config.yaml` - Your configuration settings
- `break_data.json` - Daily break data and statistics

## Example Workflow

1. **Start your work session:**
   ```bash
   python3 break_tracker.py stats  # Check yesterday's stats
   ```

2. **Take a break:**
   ```bash
   python3 break_tracker.py 7      # 7-minute break
   ```

3. **When timer ends:**
   - Get desktop notification
   - Choose to end break or snooze
   - Snooze if needed: type `3` for 3 more minutes

4. **End of day:**
   - Check stats: `python3 break_tracker.py stats`
   - Receive email report (if enabled) the next morning

## Troubleshooting

### Desktop Notifications Not Working
```bash
# Install libnotify
sudo dnf install libnotify  # Fedora/RHEL
sudo apt install libnotify-bin  # Ubuntu/Debian
```

### Email Reports Not Sending
1. Check your email credentials in `config.yaml`
2. For Gmail, ensure you're using an App Password, not your regular password
3. Verify SMTP settings for your email provider
4. Check firewall/network settings

### Configuration File Issues
- Delete `~/.config/break_tracker/config.yaml` and run the program again to recreate it
- Ensure YAML syntax is correct (proper indentation, no tabs)

## Tips

- **Regular breaks:** Use 5-7 minute breaks every 25-30 minutes (Pomodoro technique)
- **Eye rest:** Take breaks away from screens
- **Movement:** Use break time for stretching or short walks
- **Consistency:** Check daily stats to build healthy break habits

## License

This project is open source. Feel free to modify and distribute as needed.
