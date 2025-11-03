import requests, time, datetime, ssl, socket, smtplib, os
from email.mime.text import MIMEText

# === CONFIG ===
API_URLS = [
    "https://www.botguardpro.com",
    "https://www.botguardpro.com/api/v1/rules",
    "https://www.botguardpro.com/ping123",
]

# always write log to same folder as script
LOG_FILE = os.path.join(os.path.dirname(__file__), "botguard_status.log")

ALERT_EMAIL = "sarduine13@gmail.com"
ALERT_PASS = "odol lqss rrra caec"  # Gmail App Password
ALERT_TO = ["sarduine13@gmail.com"]  # add phone gateway here if wanted
CHECK_INTERVAL = 60  # seconds


def send_alert(subject, body):
    msg = MIMEText(body)
    msg["From"] = ALERT_EMAIL
    msg["To"] = ", ".join(ALERT_TO)
    msg["Subject"] = subject
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(ALERT_EMAIL, ALERT_PASS)
            server.send_message(msg)
        print(f"[ALERT SENT] {subject}")
    except Exception as e:
        print(f"[ALERT ERROR] {e}")


def check_ssl(host):
    context = ssl.create_default_context()
    with socket.create_connection((host, 443)) as sock:
        with context.wrap_socket(sock, server_hostname=host) as ssock:
            cert = ssock.getpeercert()
            exp = datetime.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
            days_left = (exp - datetime.datetime.utcnow()).days
            return days_left


def check_api(url):
    try:
        start = time.time()
        r = requests.get(url, timeout=10)
        elapsed = round((time.time() - start) * 1000)
        return r.status_code, elapsed
    except Exception as e:
        return str(e), None


def log(msg):
    t = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{t} {msg}\n")
    print(f"{t} {msg}")


def monitor():
    log("=== BotGuard Pro Alert Monitor Started ===")
    while True:
        for url in API_URLS:
            status, elapsed = check_api(url)
            if elapsed:
                log(f"{url} → {status} ({elapsed}ms)")
                if str(status)[0] not in ["2", "3"]:
                    send_alert("BotGuard Pro ALERT", f"{url} returned status {status}")
            else:
                log(f"{url} → ERROR: {status}")
                send_alert("BotGuard Pro DOWN", f"{url} unreachable: {status}")

        try:
            ssl_days = check_ssl("www.botguardpro.com")
            log(f"SSL valid for {ssl_days} days.")
            if ssl_days < 10:
                send_alert("SSL Expiry Warning", f"SSL expires in {ssl_days} days.")
        except Exception as e:
            log(f"SSL check failed: {e}")
            send_alert("SSL Check Failed", str(e))

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    monitor()
