# utils/email_utils.py
import os
import smtplib
from email.mime.text import MIMEText
from config.env import GMAIL_USER, GMAIL_APP_PASSWORD

def send_email(subject: str, body: str, to_emails, html=False):

    if isinstance(to_emails, str):
        to_emails = [to_emails]

    msg = MIMEText(body, "html" if html else "plain")
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = ", ".join(to_emails)
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False