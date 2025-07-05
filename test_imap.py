import imaplib
import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("IMAP_HOST", "127.0.0.1")
port = int(os.getenv("IMAP_PORT", "1143"))
user = os.getenv("IMAP_USER")
password = os.getenv("IMAP_PASS")

print(f"🔐 Connexion à {host}:{port} avec {user}...")

try:
    conn = imaplib.IMAP4(host, port)
    conn.starttls()
    conn.login(user, password)
    print("✅ Connecté")

    conn.select("INBOX")
    typ, data = conn.search(None, 'UNSEEN')
    for num in data[0].split()[:5]:
        typ, msg_data = conn.fetch(num, '(BODY[HEADER.FIELDS (FROM SUBJECT DATE)])')
        print(msg_data[0][1].decode())

    conn.logout()
except Exception as e:
    print(f"❌ Erreur IMAP : {e}")

