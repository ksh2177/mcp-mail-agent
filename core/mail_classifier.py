import typer
import json
from pathlib import Path
from typing import Optional


app = typer.Typer()

def classify_mail(mail:dict) -> dict:
    tags = []
    subject = mail["subject"].lower()
    sender = mail["from_email"].lower()

    if "github" in sender or "gitlab" in sender:
        tags.append("dev")
    if "alert" in subject or "security" in subject:
        tags.append("alert")
    if any(word in subject for word in ["facture", "paiement", "stripe", "recu"]):
        tags.append("finance")

    score = 0
    if "alert" in tags:
        score = 8
    elif "finance" in tags:
        score = 6
    elif "dev" in tags:
        score = 5

    mail["tags"] = tags
    mail["score"] = score or None
    mail["summary"] = None

    return mail

@app.command()
def tag(
    input_file: Path = typer.Argument(..., help="Fichier .json à enrichir"),
    output_file: Optional[Path] = typer.Option(None, help="Fichier de sortie (.json)"),
):
    if not input_file.exists():
        typer.echo(f"❌ Fichier introuvable: {input_file}")
        raise typer.Exit(1)

    with input_file.open("r", encoding="utf-8") as f:
        mails = json.load(f)

    updated = [classify_mail(m) for m in mails]

    target_file = output_file or input_file

    with target_file.open("w", encoding="utf-8") as f:
        json.dump(updated, f, ensure_ascii=False, indent = 2)

    typer.echo(f"✅ Classifications ajoutées dans : {target_file}")

if __name__ == "__main__":
    app()

    #49B9C7 curseur
    #66DCDC