import json
from pathlib import Path
from datetime import datetime
import typer

app = typer.Typer()

@app.command()
def summary(input_file: Path = typer.Argument(..., help="Fichier JSON enrichi")):
    if not input_file.exists():
        typer.echo("❌ Fichier introuvable")
        raise typer.Exit(1)
    
    with input_file.open("r", encoding="utf-8") as f:
        mails = json.load(f)

    lines = [f"# Résumé du {datetime.now().strftime('%d %B %Y')}\n"]
    
    for mail in mails:
        name = mail.get("from_name", "")
        email = mail.get("from_email", "")
        subject = mail.get("subject", "")
        tags = ", ".join(mail.get("tags", [])) or "aucun tag"
        summary = mail.get("summary") or "(pas de résumé)"

        try:
            dt = datetime.fromisoformat(mail["date"])
            short_date = dt.strftime("%d %b %H:%M")
        except Exception:
            short_date = mail["date"]

        lines.append(f"## {name} <{email}>")
        lines.append(f"🕒 {short_date} - 📌 {tags}")
        lines.append(f"🧠 {summary}\n")

    output_file = input_file.parent / f"{input_file.stem}.summary.md"
    with output_file.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    typer.echo(f"✅ Résumé Markdown généré : {output_file}")

if __name__ == "__main__":
    app()
