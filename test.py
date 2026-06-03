#test notebook to check if gmail credentials are correct, before running the application

import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()
GMAIL_USER   = os.getenv("GMAIL_USER")
GMAIL_PASS   = os.getenv("GMAIL_PASS")
print(f"DEBUG: Attempting login for: {GMAIL_USER}")
if not GMAIL_PASS or len(GMAIL_PASS) != 16:
    print(f"DEBUG ERROR: GMAIL_PASS is either missing or wrong length! Current length: {len(GMAIL_PASS) if GMAIL_PASS else 0}")
def test_mail():
    msg = MIMEText("Test body")
    msg["Subject"] = "Test"
    msg["From"] = os.getenv("GMAIL_USER")
    msg["To"] = os.getenv("UNI_EMAIL")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(os.getenv("GMAIL_USER"), os.getenv("GMAIL_PASS"))
            s.send_message(msg)
        print("Test email sent!")
    except Exception as e:
        print(f"Test failed: {e}")

test_mail()