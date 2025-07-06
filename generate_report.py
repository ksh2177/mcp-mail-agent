import json
from core.imap_client import IMAPClient
from email.utils import parsedate_to_datetime
from email.header import decode_header
from datetime import datetime
from pathlib import Path

client = IMAPClient()
client.connect()
mails = client.fetch_recent(limit=20, hours=48)

lines = ["# Rapport de mails récents\n"]

def decode_mime_header(value: str) -> str:
    decoded = decode_header(value)
    return "".join([
        part.decode(charset or "utf-8") if isinstance(part, bytes) else part
        for part, charset in decoded
    ])

# Création du fichier .md
for mail in mails:
    from_info = client._parse_from(mail["from"])

    try:
        dt = parsedate_to_datetime(mail["date"])
        short_date = dt.strftime("%d %b %H:%M")
    except Exception:
        short_date = mail["date"]

    lines.append(f"## [{short_date}] {from_info['name']} <{from_info['email']}>")
    
    subject = decode_mime_header(mail["subject"])
    lines.append(f"** Sujet :** {subject}\n")

    preview = mail["body"][:300].replace("\n", " ")
    lines.append(f"** Aperçu :** {preview}...\n")

report_path = Path("reports")
report_path.mkdir(exist_ok=True)
filename = report_path / f"report_{datetime.now().strftime('%Y-%m-%d')}.md"

with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

print(f"✅ Rapport généré : {filename}")

# Création du fichier .json
json_data = []
for mail in mails:
    from_info = client._parse_from(mail["from"])
    try:
        dt = parsedate_to_datetime(mail["date"])
        iso_date = dt.isoformat()
    except Exception:
        iso_date = mail["date"]

    json_data.append({
        "from_name": from_info["name"],
        "from_email": from_info["email"],
        "subject" : decode_mime_header(mail["subject"]),
        "date": iso_date,
        "body": mail["body"].strip()
    })

# Ecriture du fichier .json
json_filename = report_path / f"report_{datetime.now().strftime('%Y-%m-%d')}.json"
with open(json_filename, "w", encoding="utf-8") as f:
    json.dump(json_data, f, ensure_ascii=False, indent=2)

print(f"✅ JSON généré : {json_filename}")
