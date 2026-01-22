"""
Streamlit Messaging App - Send Email and SMS via SMTP
Supports multiple recipients for both email and SMS
"""

import streamlit as st
import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

# Config file path
CONFIG_FILE = Path(__file__).parent / "smtp_configs.json"

# SMS Gateway domains for major carriers
SMS_GATEWAYS = {
    "AT&T": "txt.att.net",
    "T-Mobile": "tmomail.net",
    "Verizon": "vtext.com",
    "Sprint": "messaging.sprintpcs.com",
    "US Cellular": "email.uscc.net",
    "Metro PCS": "mymetropcs.com",
    "Boost Mobile": "sms.myboostmobile.com",
    "Cricket": "sms.cricketwireless.net",
    "Virgin Mobile": "vmobl.com",
    "Google Fi": "msg.fi.google.com",
    "Republic Wireless": "text.republicwireless.com",
    "Straight Talk": "vtext.com",
    "Mint Mobile": "tmomail.net",
    "Xfinity Mobile": "vtext.com",
    "Visible": "vtext.com",
}

# Default SMTP presets
DEFAULT_SMTP_PRESETS = {
    "Gmail": {
        "server": "smtp.gmail.com",
        "port": 587,
        "use_tls": True,
        "use_ssl": False,
        "description": "Google Gmail - requires App Password"
    },
    "Outlook/Hotmail": {
        "server": "smtp.office365.com",
        "port": 587,
        "use_tls": True,
        "use_ssl": False,
        "description": "Microsoft Outlook/Hotmail"
    },
    "Yahoo": {
        "server": "smtp.mail.yahoo.com",
        "port": 587,
        "use_tls": True,
        "use_ssl": False,
        "description": "Yahoo Mail - requires App Password"
    },
    "iCloud": {
        "server": "smtp.mail.me.com",
        "port": 587,
        "use_tls": True,
        "use_ssl": False,
        "description": "Apple iCloud Mail"
    },
    "Zoho": {
        "server": "smtp.zoho.com",
        "port": 587,
        "use_tls": True,
        "use_ssl": False,
        "description": "Zoho Mail"
    },
    "ProtonMail Bridge": {
        "server": "127.0.0.1",
        "port": 1025,
        "use_tls": False,
        "use_ssl": False,
        "description": "ProtonMail via Bridge (local)"
    },
    "SendGrid": {
        "server": "smtp.sendgrid.net",
        "port": 587,
        "use_tls": True,
        "use_ssl": False,
        "description": "SendGrid SMTP Relay"
    },
    "Mailgun": {
        "server": "smtp.mailgun.org",
        "port": 587,
        "use_tls": True,
        "use_ssl": False,
        "description": "Mailgun SMTP"
    },
    "Amazon SES": {
        "server": "email-smtp.us-east-1.amazonaws.com",
        "port": 587,
        "use_tls": True,
        "use_ssl": False,
        "description": "Amazon SES (update region as needed)"
    },
}


def load_custom_configs() -> dict:
    """Load custom SMTP configurations from file."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_custom_configs(configs: dict):
    """Save custom SMTP configurations to file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(configs, f, indent=2)


def get_all_smtp_configs() -> dict:
    """Get all SMTP configs (default + custom)."""
    all_configs = DEFAULT_SMTP_PRESETS.copy()
    custom = load_custom_configs()
    all_configs.update(custom)
    return all_configs

def send_email(smtp_server: str, smtp_port: int, sender_email: str, 
               sender_password: str, recipient_emails: list[str], 
               subject: str, message: str, use_tls: bool = True,
               use_ssl: bool = False) -> list[tuple[str, bool, str]]:
    """
    Send emails to multiple recipients using SMTP.
    
    Returns:
        list of tuples: [(recipient, success: bool, message: str), ...]
    """
    results = []
    
    try:
        # Connect once for all recipients
        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            if use_tls:
                server.starttls()
        
        server.login(sender_email, sender_password)
        
        for recipient in recipient_emails:
            recipient = recipient.strip()
            if not recipient:
                continue
            try:
                # Create message for each recipient
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = recipient
                msg['Subject'] = subject
                msg.attach(MIMEText(message, 'plain'))
                
                server.sendmail(sender_email, recipient, msg.as_string())
                results.append((recipient, True, "Sent successfully"))
            except Exception as e:
                results.append((recipient, False, str(e)))
        
        server.quit()
        
    except smtplib.SMTPAuthenticationError:
        return [(r.strip(), False, "Authentication failed") for r in recipient_emails if r.strip()]
    except smtplib.SMTPException as e:
        return [(r.strip(), False, f"SMTP error: {str(e)}") for r in recipient_emails if r.strip()]
    except Exception as e:
        return [(r.strip(), False, f"Error: {str(e)}") for r in recipient_emails if r.strip()]
    
    return results


def send_sms_via_gateway(smtp_server: str, smtp_port: int, sender_email: str,
                         sender_password: str, phone_entries: list[tuple[str, str]], 
                         message: str, use_tls: bool = True,
                         use_ssl: bool = False) -> list[tuple[str, bool, str]]:
    """
    Send SMS to multiple phone numbers via carrier's email-to-SMS gateway.
    
    Args:
        phone_entries: list of (phone_number, carrier) tuples
    
    Returns:
        list of tuples: [(phone, success: bool, message: str), ...]
    """
    results = []
    
    try:
        # Connect once for all recipients
        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            if use_tls:
                server.starttls()
        
        server.login(sender_email, sender_password)
        
        for phone_number, carrier in phone_entries:
            phone_number = phone_number.strip()
            if not phone_number:
                continue
                
            try:
                # Clean phone number (remove non-digits)
                clean_number = ''.join(filter(str.isdigit, phone_number))
                
                if len(clean_number) < 10:
                    results.append((phone_number, False, "Invalid phone number (less than 10 digits)"))
                    continue
                
                # Get the last 10 digits (US phone numbers)
                clean_number = clean_number[-10:]
                
                # Get the gateway domain
                gateway_domain = SMS_GATEWAYS.get(carrier)
                if not gateway_domain:
                    results.append((phone_number, False, f"Unknown carrier: {carrier}"))
                    continue
                
                sms_email = f"{clean_number}@{gateway_domain}"
                
                # SMS messages should be short and have no subject
                msg = MIMEText(message, 'plain')
                msg['From'] = sender_email
                msg['To'] = sms_email
                msg['Subject'] = ""
                
                server.sendmail(sender_email, sms_email, msg.as_string())
                results.append((phone_number, True, f"Sent to {sms_email}"))
            except Exception as e:
                results.append((phone_number, False, str(e)))
        
        server.quit()
        
    except smtplib.SMTPAuthenticationError:
        return [(p[0].strip(), False, "Authentication failed") for p in phone_entries if p[0].strip()]
    except smtplib.SMTPException as e:
        return [(p[0].strip(), False, f"SMTP error: {str(e)}") for p in phone_entries if p[0].strip()]
    except Exception as e:
        return [(p[0].strip(), False, f"Error: {str(e)}") for p in phone_entries if p[0].strip()]
    
    return results


def main():
    st.set_page_config(
        page_title="Email & SMS Messenger",
        page_icon="📧",
        layout="wide"
    )
    
    st.title("📧 Email & SMS Messenger")
    st.markdown("Send emails and SMS messages to multiple recipients using SMTP")
    
    # Initialize session state for recipients
    if 'email_recipients' not in st.session_state:
        st.session_state.email_recipients = [""]
    if 'sms_recipients' not in st.session_state:
        st.session_state.sms_recipients = [{"phone": "", "carrier": "AT&T"}]
    
    # Sidebar for SMTP Configuration
    st.sidebar.header("⚙️ SMTP Configuration")
    
    # Get all SMTP configs
    all_configs = get_all_smtp_configs()
    custom_configs = load_custom_configs()
    
    # Add "Custom" option and "➕ Add New Provider" option
    provider_options = list(all_configs.keys()) + ["Custom", "➕ Add New Provider"]
    preset = st.sidebar.selectbox("Email Provider", provider_options)
    
    # Handle "Add New Provider"
    if preset == "➕ Add New Provider":
        st.sidebar.subheader("Create New SMTP Provider")
        new_name = st.sidebar.text_input("Provider Name", placeholder="My Email Provider")
        new_server = st.sidebar.text_input("SMTP Server", placeholder="smtp.example.com")
        new_port = st.sidebar.number_input("SMTP Port", value=587, min_value=1, max_value=65535)
        new_tls = st.sidebar.checkbox("Use STARTTLS", value=True, key="new_tls")
        new_ssl = st.sidebar.checkbox("Use SSL/TLS (implicit)", value=False, key="new_ssl")
        new_desc = st.sidebar.text_input("Description (optional)", placeholder="My custom mail server")
        
        if st.sidebar.button("💾 Save Provider", type="primary"):
            if new_name and new_server:
                custom_configs[new_name] = {
                    "server": new_server,
                    "port": new_port,
                    "use_tls": new_tls,
                    "use_ssl": new_ssl,
                    "description": new_desc
                }
                save_custom_configs(custom_configs)
                st.sidebar.success(f"Saved '{new_name}'! Refresh to use it.")
                st.rerun()
            else:
                st.sidebar.error("Please enter provider name and server.")
        
        # Use default values for sending
        smtp_server = new_server if new_server else "smtp.gmail.com"
        smtp_port = new_port
        use_tls = new_tls
        use_ssl = new_ssl
    
    elif preset == "Custom":
        smtp_server = st.sidebar.text_input("SMTP Server", placeholder="smtp.example.com")
        smtp_port = st.sidebar.number_input("SMTP Port", value=587, min_value=1, max_value=65535)
        use_tls = st.sidebar.checkbox("Use STARTTLS", value=True)
        use_ssl = st.sidebar.checkbox("Use SSL/TLS (implicit)", value=False)
    else:
        config = all_configs[preset]
        smtp_server = config["server"]
        smtp_port = config["port"]
        use_tls = config.get("use_tls", True)
        use_ssl = config.get("use_ssl", False)
        st.sidebar.info(f"**{preset}**\n\n{config.get('description', '')}\n\nServer: `{smtp_server}:{smtp_port}`")
        
        # Option to delete custom providers
        if preset in custom_configs:
            if st.sidebar.button("🗑️ Delete This Provider"):
                del custom_configs[preset]
                save_custom_configs(custom_configs)
                st.rerun()
    
    st.sidebar.divider()
    
    # Sender credentials
    st.sidebar.subheader("🔐 Sender Credentials")
    sender_email = st.sidebar.text_input("Your Email", placeholder="your.email@gmail.com")
    sender_password = st.sidebar.text_input("App Password", type="password", 
                                            help="For Gmail/Yahoo, use an App Password")
    
    if preset == "Gmail":
        st.sidebar.caption("💡 [How to create Gmail App Password](https://support.google.com/accounts/answer/185833)")
    elif preset == "Yahoo":
        st.sidebar.caption("💡 [How to create Yahoo App Password](https://help.yahoo.com/kb/generate-app-password-sln15241.html)")
    
    # Main content - Tabs for Email, SMS, and Settings
    tab1, tab2, tab3 = st.tabs(["📧 Send Email", "📱 Send SMS", "ℹ️ Info & Help"])
    
    # Email Tab
    with tab1:
        st.subheader("Send Email to Multiple Recipients")
        
        subject = st.text_input("Subject", placeholder="Enter email subject")
        
        # Multiple recipients section
        st.markdown("**Recipients** (one email per line or comma-separated)")
        recipients_text = st.text_area(
            "Email Addresses",
            placeholder="recipient1@example.com\nrecipient2@example.com\nor: email1@test.com, email2@test.com",
            height=100,
            key="email_recipients_input",
            label_visibility="collapsed"
        )
        
        # Parse recipients
        if recipients_text:
            # Split by newlines and commas
            recipients = []
            for line in recipients_text.split('\n'):
                for email in line.split(','):
                    email = email.strip()
                    if email:
                        recipients.append(email)
            st.caption(f"📬 {len(recipients)} recipient(s)")
        else:
            recipients = []
        
        email_message = st.text_area("Message", placeholder="Type your message here...", 
                                     height=200, key="email_message")
        
        if st.button("📤 Send Emails", type="primary", key="send_email_btn"):
            if not sender_email or not sender_password:
                st.error("Please configure your sender credentials in the sidebar.")
            elif not recipients:
                st.error("Please enter at least one recipient email address.")
            elif not email_message:
                st.error("Please enter a message.")
            else:
                with st.spinner(f"Sending emails to {len(recipients)} recipient(s)..."):
                    results = send_email(
                        smtp_server=smtp_server,
                        smtp_port=smtp_port,
                        sender_email=sender_email,
                        sender_password=sender_password,
                        recipient_emails=recipients,
                        subject=subject,
                        message=email_message,
                        use_tls=use_tls,
                        use_ssl=use_ssl
                    )
                    
                    # Display results
                    success_count = sum(1 for r in results if r[1])
                    fail_count = len(results) - success_count
                    
                    if success_count > 0:
                        st.success(f"✅ Successfully sent to {success_count} recipient(s)")
                    if fail_count > 0:
                        st.error(f"❌ Failed to send to {fail_count} recipient(s)")
                    
                    # Show detailed results
                    with st.expander("📋 Detailed Results"):
                        for recipient, success, msg in results:
                            if success:
                                st.markdown(f"✅ **{recipient}**: {msg}")
                            else:
                                st.markdown(f"❌ **{recipient}**: {msg}")
    
    # SMS Tab
    with tab2:
        st.subheader("Send SMS to Multiple Recipients")
        st.info("📱 SMS messages are sent through carrier email-to-SMS gateways. Works for US carriers.")
        
        # Multiple SMS recipients
        st.markdown("**Add Recipients**")
        
        # Dynamic recipient list using session state
        recipients_container = st.container()
        
        with recipients_container:
            sms_entries = []
            
            # Show input for each recipient
            for i in range(len(st.session_state.sms_recipients)):
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    phone = st.text_input(
                        f"Phone #{i+1}",
                        value=st.session_state.sms_recipients[i]["phone"],
                        placeholder="(555) 123-4567",
                        key=f"phone_{i}",
                        label_visibility="collapsed" if i > 0 else "visible"
                    )
                with col2:
                    carrier = st.selectbox(
                        f"Carrier #{i+1}",
                        list(SMS_GATEWAYS.keys()),
                        key=f"carrier_{i}",
                        label_visibility="collapsed" if i > 0 else "visible"
                    )
                with col3:
                    if i > 0:  # Don't allow removing the first one
                        if st.button("🗑️", key=f"remove_{i}"):
                            st.session_state.sms_recipients.pop(i)
                            st.rerun()
                
                if phone:
                    sms_entries.append((phone, carrier))
                    st.session_state.sms_recipients[i] = {"phone": phone, "carrier": carrier}
        
        # Add more button
        if st.button("➕ Add Another Recipient"):
            st.session_state.sms_recipients.append({"phone": "", "carrier": "AT&T"})
            st.rerun()
        
        st.caption(f"📱 {len(sms_entries)} recipient(s)")
        
        sms_message = st.text_area("Message", placeholder="Type your SMS message here...", 
                                   height=150, key="sms_message",
                                   max_chars=160,
                                   help="SMS messages are limited to 160 characters")
        
        char_count = len(sms_message) if sms_message else 0
        st.caption(f"Characters: {char_count}/160")
        
        if st.button("📤 Send SMS", type="primary", key="send_sms_btn"):
            if not sender_email or not sender_password:
                st.error("Please configure your sender credentials in the sidebar.")
            elif not sms_entries:
                st.error("Please enter at least one phone number.")
            elif not sms_message:
                st.error("Please enter a message.")
            else:
                with st.spinner(f"Sending SMS to {len(sms_entries)} recipient(s)..."):
                    results = send_sms_via_gateway(
                        smtp_server=smtp_server,
                        smtp_port=smtp_port,
                        sender_email=sender_email,
                        sender_password=sender_password,
                        phone_entries=sms_entries,
                        message=sms_message,
                        use_tls=use_tls,
                        use_ssl=use_ssl
                    )
                    
                    # Display results
                    success_count = sum(1 for r in results if r[1])
                    fail_count = len(results) - success_count
                    
                    if success_count > 0:
                        st.success(f"✅ Successfully sent to {success_count} recipient(s)")
                    if fail_count > 0:
                        st.error(f"❌ Failed to send to {fail_count} recipient(s)")
                    
                    # Show detailed results
                    with st.expander("📋 Detailed Results"):
                        for phone, success, msg in results:
                            if success:
                                st.markdown(f"✅ **{phone}**: {msg}")
                            else:
                                st.markdown(f"❌ **{phone}**: {msg}")
        
        # SMS Gateway Reference
        with st.expander("📋 SMS Gateway Reference"):
            st.markdown("### Carrier Email-to-SMS Gateways")
            cols = st.columns(2)
            carriers = list(SMS_GATEWAYS.items())
            mid = len(carriers) // 2
            with cols[0]:
                for carrier_name, domain in carriers[:mid]:
                    st.markdown(f"- **{carrier_name}**: `[phone]@{domain}`")
            with cols[1]:
                for carrier_name, domain in carriers[mid:]:
                    st.markdown(f"- **{carrier_name}**: `[phone]@{domain}`")
    
    # Info Tab
    with tab3:
        st.subheader("ℹ️ Information & Help")
        
        st.markdown("""
        ### 📝 How to Use
        
        1. **Select Email Provider**: Choose from presets or add your own SMTP server
        2. **Enter Credentials**: Use your email and app password
        3. **Add Recipients**: Enter multiple email addresses or phone numbers
        4. **Send Messages**: Click send to deliver to all recipients
        
        ### 🔐 Security Notes
        
        - **Gmail**: Requires an [App Password](https://support.google.com/accounts/answer/185833) (2FA must be enabled)
        - **Yahoo**: Requires an [App Password](https://help.yahoo.com/kb/generate-app-password-sln15241.html)
        - **Outlook**: May require enabling "Less secure apps" or using App Password
        - Never share your app passwords
        - Your credentials are not stored - you must enter them each session
        
        ### 📱 SMS via Email Gateway
        
        SMS messages are delivered through carrier email-to-SMS gateways:
        - Works with most US carriers
        - No special API or service required
        - May have slight delays (seconds to minutes)
        - Not all carriers support this feature
        - Message delivery is not guaranteed
        
        ### 🔧 Adding Custom SMTP Providers
        
        You can add any SMTP server by selecting "➕ Add New Provider":
        
        - **STARTTLS**: Use port 587 with STARTTLS (most common)
        - **SSL/TLS**: Use port 465 with implicit SSL
        - **No encryption**: Use port 25 (not recommended)
        """)
        
        # Show saved custom configs
        if custom_configs:
            st.markdown("### 💾 Your Saved Providers")
            for name, config in custom_configs.items():
                st.markdown(f"- **{name}**: `{config['server']}:{config['port']}`")


if __name__ == "__main__":
    main()
