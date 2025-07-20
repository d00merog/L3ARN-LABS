from typing import List
import smtplib
from email.mime.text import MIMEText


def send_email(
    host: str,
    port: int,
    username: str,
    password: str,
    recipients: List[str],
    subject: str,
    body: str,
):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = username
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP(host, port) as server:
        if username or password:
            server.starttls()
            server.login(username, password)
        server.sendmail(username, recipients, msg.as_string())
