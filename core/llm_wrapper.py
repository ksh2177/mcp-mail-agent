import json
import requests
from pathlib import Path
import typer

app = typer.Typer()

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

def summarize_text(text: str) -> str:
    prompt = f"Tu es un assistant francophone. Résume le mail ci-dessous en **français** et en **une seul phrase courte**. Ignore les signatures et pieds de page.n\n{text}"

    response = requests.post(OLLAMA_URL, json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    })

    if response.status_code != 200:
        typer.echo(f"❌ Erreur Ollama : {response.status_code} - {response.text}")
        return None

    data = response.json()
    return data.get("response", "")


@app.command()
def enrich_summary(
    input_file: Path = typer.Argument(..., help="Fichier .json à enrichir avec un résumé"),
):
    if not input_file.exists():
        typer.echo("❌ Fichier introuvable")
        raise typer.Exit(1)

    with input_file.open("r", encoding="utf-8") as f:
        mails = json.load(f)

    for mail in mails:
        if not mail.get("summary"):
            mail["summary"] = summarize_text(mail["body"])

    with input_file.open("w", encoding="utf-8") as f:
        json.dump(mails, f, ensure_ascii=False, indent=2)

    typer.echo(f"✅ Résumés ajoutés dans : {input_file}")


if __name__ == "__main__":
    app()
