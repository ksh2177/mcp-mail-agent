
import os
import re
import quopri
import imaplib
import base64
from dotenv import load_dotenv
from email.header import decode_header
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup

load_dotenv()

IMAP_HOST = os.getenv("IMAP_HOST", "127.0.0.1")
IMAP_PORT = int(os.getenv("IMAP_PORT", "1143"))
IMAP_USER = os.getenv("IMAP_USER")
IMAP_PASS = os.getenv("IMAP_PASS")

class IMAPClient:
    def __init__(self, host=IMAP_HOST, port=IMAP_PORT, user=IMAP_USER, password=IMAP_PASS):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.conn = None

    def connect(self):
        try:
            self.conn = imaplib.IMAP4(self.host, self.port)
            self.conn.starttls()
            self.conn.login(self.user, self.password)
            print(f"✅ IMAP connecté à {self.host}:{self.port}")
        except Exception as e:
            print(f"❌ Echec de connexion IMAP : {e}")
            self.conn = None

    def list_all_accessible_folders(self) -> list:
        if not self.conn:
            self.connect()
            if not self.conn:
                return []

        folders = []
        seen = set()

        typ, data = self.conn.list("", "*")
        if typ != "OK":
            return []

        for raw in data:
            decoded = raw.decode()
            if decoded in seen:
                continue
            seen.add(decoded)

            parts = re.search(r'\((.*?)\)\s+"?([^"]+)"?\s+"?([^"]+)"?', decoded)
            if parts:
                flags, separator, name = parts.groups()
                try:
                    self.conn.select(name)
                    folders.append({
                        "name": name,
                        "separator": separator,
                        "flags": flags.split()
                    })
                except:
                    continue

        return folders

    def fetch_recent(self, limit=10, hours=24, folder="INBOX"):
        if not self.conn:
            print("❌ Pas de connexion active")
            return []

        messages = []
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

        try:
            encoded_folder = self.encode_utf7(folder)
            self.conn.select(encoded_folder)
            typ, data = self.conn.search(None, 'ALL')
            ids = data[0].split()

            for num in reversed(ids):
                typ, msg_data = self.conn.fetch(num, '(BODY[HEADER.FIELDS (FROM SUBJECT DATE)])')
                raw = msg_data[0][1].decode()
                headers = self._parse_header(raw)

                from_email = headers["from"].lower()
                proton_blacklist = [
                    "@notify.proton.me",
                    "@calendar.proton.me",
                    "@mail.proton.me",
                    "@support.proton.me",
                ]
                if any(bad in from_email for bad in proton_blacklist):
                    print(f"⏭️ Mail Proton technique ignoré : {from_email}")
                    continue

                typ, body_data = self.conn.fetch(num, '(BODY[TEXT])')
                body_raw = body_data[0][1]

                try:
                    body = base64.b64decode(body_raw).decode("utf-8")
                except Exception:
                    try:
                        body = quopri.decodestring(body_raw).decode("utf-8", errors="replace")
                    except Exception:
                        body = body_raw.decode("utf-8", errors="replace")

                body = self._clean_body(self._html_to_text(body))

                if "BEGIN:VCALENDAR" in body or "PRODID:-//ProtonCalendar//" in body:
                    continue

                headers["body"] = body

                try:
                    msg_date = parsedate_to_datetime(headers["date"])
                    if msg_date >= cutoff:
                        messages.append(headers)
                        if len(messages) >= limit:
                            break
                except Exception:
                    continue

        except Exception as e:
            print(f"❌ Erreur fetch IMAP (recent) : {e}")
        return messages

    def _parse_header(self, raw: str) -> dict:
        headers = {}
        for line in raw.splitlines():
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip().lower()] = value.strip()
        return {
            "from": headers.get("from", ""),
            "subject": headers.get("subject", ""),
            "date": headers.get("date", "")
        }

    def _parse_from(self, raw_from: str) -> dict:
        match = re.match(r'(.*)<(.+?)>', raw_from)
        if match:
            name = match.group(1).strip().strip('"')
            email = match.group(2).strip()
            return {"name": name, "email": email}
        else:
            return {"name": "", "email": raw_from.strip()}

    def _html_to_text(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator=" ", strip=True)

    def _clean_body(self, raw_body: str) -> str:
        lines = raw_body.splitlines()
        clean = []
        skip = False

        for line in lines:
            l = line.lower()
            if any(
                l.startswith(prefix)
                for prefix in ("content-", "mime-version", "x-", "boundary=", "--", "begin", "encoded", "calendar", "charset")
            ):
                skip = True
            elif skip and line.strip() == "":
                skip = False
            elif not skip:
                clean.append(line)

        return "\n".join(clean).strip()

    @staticmethod
    def encode_utf7(folder: str) -> str:
        res = []
        buffer = ""
        def flush():
            nonlocal buffer
            if buffer:
                b64 = base64.b64encode(buffer.encode("utf-16be")).decode("ascii")
                res.append("&" + b64.rstrip('=') + "-")
                buffer = ""
        for c in folder:
            if ord(c) in range(0x20, 0x7f) and c != "&":
                flush()
                res.append(c)
            elif c == "&":
                flush()
                res.append("&-")
            else:
                buffer += c
        flush()
        return "".join(res)

if __name__ == "__main__":
    client = IMAPClient()
    client.connect()
    mails = client.fetch_recent(limit=5, hours=2, folder="Labels/ksh - Dev")

    for mail in mails:
        from_info = client._parse_from(mail['from'])
        try:
            dt = parsedate_to_datetime(mail["date"])
            short_date = dt.strftime("%d %b %H:%M")
        except Exception:
            short_date = mail["date"]
        print(f"[{short_date}] {from_info['name']} <{from_info['email']}> - {mail['subject']}")