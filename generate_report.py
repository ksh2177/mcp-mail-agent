import json
import typer
from datetime import datetime
from pathlib import Path
from email.utils import parsedate_to_datetime
from email.header import decode_header

from core.imap_client import IMAPClient

app = typer.Typer()

def decode_mime_header(value: str) -> str:
    decoded = decode_header(value)
    return "".join([
        part.decode(charset or "utf-8") if isinstance(part, bytes) else part
        for part, charset in decoded
    ])

def slugify(label: str) -> str:
    return label.replace("Labels/", "").replace("/", "_").replace(" ", "_")

@app.command()
def generate(
    label: str = typer.Option("INBOX", help="Nom du label IMAP à cibler (ex: Labels/ksh.proton)"),
    hours: int = typer.Option(24, help="Fenêtre de récupération en heures"),
    limit: int = typer.Option(30, help="Nombre maximum de mails"),
):
    client = IMAPClient()
    client.connect()

    mails = client.fetch_recent(limit=limit, hours=hours, folder=label)
    if not mails:
        typer.echo("⚠️ Aucun mail récupéré.")
        raise typer.Exit(0)

    lines = ["# Rapport de mails récents\\n"]

    for mail in mails:
        from_info = client._parse_from(mail["from"])
        try:
            dt = parsedate_to_datetime(mail["date"])
            short_date = dt.strftime("%d %b %H:%M")
        except Exception:
            short_date = mail["date"]

        subject = decode_mime_header(mail["subject"])
        preview = mail["body"][:300].replace("\\n", " ")

        lines.append(f"## [{short_date}] {from_info['name']} <{from_info['email']}>")
        lines.append(f"** Sujet :** {subject}\\n")
        lines.append(f"** Aperçu :** {preview}...\\n")

    date_str = datetime.now().strftime('%Y-%m-%d')
    base_name = (
        f"label_{slugify(label)}_report_{date_str}"
        if label != "INBOX" else f"report_{date_str}"
    )

    report_path = Path("reports")
    report_path.mkdir(exist_ok=True)

    md_file = report_path / f"{base_name}.md"
    with md_file.open("w", encoding="utf-8") as f:
        f.write("\\n".join(lines))
    typer.echo(f"✅ Rapport généré : {md_file}")

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
            "subject": decode_mime_header(mail["subject"]),
            "date": iso_date,
            "body": mail["body"].strip()
        })

    json_file = report_path / f"{base_name}.json"
    with json_file.open("w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    typer.echo(f"✅ JSON généré : {json_file}")

if __name__ == "__main__":
    app()