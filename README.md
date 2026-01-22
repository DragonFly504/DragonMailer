# 📧 Email & SMS Messenger

A Python application to send emails and SMS messages via SMTP. Includes both a **Streamlit web UI** and a **command-line interface**.

## Features

- ✉️ **Send Emails** to multiple recipients
- 📱 **Send SMS** via carrier email-to-SMS gateways
- 🔧 **Custom SMTP Providers** - Add your own SMTP servers
- 🖥️ **Web UI** (Streamlit) and **CLI** versions
- 📋 **Pre-configured** for Gmail, Outlook, Yahoo, iCloud, and more

## Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/messaging-app.git
cd messaging-app

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Web Interface (Streamlit)

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

### Command Line Interface

```bash
# Send email
python cli.py email -p gmail -e you@gmail.com -t recipient@example.com -s "Subject" -m "Message"

# Send SMS
python cli.py sms -p gmail -e you@gmail.com -n 5551234567 -c att -m "Hello!"

# Send to multiple recipients
python cli.py email -p gmail -e you@gmail.com -t user1@test.com,user2@test.com -m "Hi all"

# Interactive mode (guided prompts)
python cli.py interactive

# List available carriers
python cli.py carriers

# List SMTP presets
python cli.py presets
```

## SMS Carriers Supported

| Carrier | Gateway |
|---------|---------|
| AT&T | txt.att.net |
| T-Mobile | tmomail.net |
| Verizon | vtext.com |
| Sprint | messaging.sprintpcs.com |
| US Cellular | email.uscc.net |
| Metro PCS | mymetropcs.com |
| Boost Mobile | sms.myboostmobile.com |
| Cricket | sms.cricketwireless.net |
| Virgin Mobile | vmobl.com |
| Google Fi | msg.fi.google.com |
| Mint Mobile | tmomail.net |

## SMTP Presets

- **Gmail** - smtp.gmail.com:587
- **Outlook/Hotmail** - smtp.office365.com:587
- **Yahoo** - smtp.mail.yahoo.com:587
- **iCloud** - smtp.mail.me.com:587
- **Zoho** - smtp.zoho.com:587
- **SendGrid** - smtp.sendgrid.net:587
- **Mailgun** - smtp.mailgun.org:587
- **Amazon SES** - email-smtp.us-east-1.amazonaws.com:587

## ⚠️ Important Notes

### Gmail App Password
For Gmail, you must use an **App Password** instead of your regular password:
1. Enable 2-Factor Authentication on your Google account
2. Go to [App Passwords](https://myaccount.google.com/apppasswords)
3. Generate a new app password for "Mail"
4. Use this 16-character password in the app

### Security
- Never commit your credentials to git
- The `smtp_configs.json` file is gitignored
- Use environment variables for production deployments

## License

MIT License
