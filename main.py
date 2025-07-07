
import typer
import subprocess
from datetime import datetime
from pathlib import Path
import sys

app = typer.Typer(no_args_is_help=True)

def build_report_filename(label: str) -> Path:
    now = datetime.now().strftime("%Y-%m-%d")
    if label == "INBOX":
        return Path(f"reports/report_{now}.json")
    slug = label.replace("Labels/", "").replace("/", "_").replace(" ", "_")
    return Path(f"reports/label_{slug}_report_{now}.json")

@app.command("dump")
def dump(
    hours: int = 24,
    limit: int = 30,
    label: str = "INBOX"
):
    typer.echo(f"📥 Génération du rapport depuis : {label}")
    subprocess.run([
        "python", "generate_report.py",
        "--hours", str(hours),
        "--limit", str(limit),
        "--label", label
    ], check=True)

@app.command("classify")
def classify(
    file: Path = typer.Option(None, help="Fichier JSON à classifier"),
    label: str = "INBOX"
):
    json_file = file or build_report_filename(label)
    typer.echo("🏷️ Tagging & scoring...")
    subprocess.run([
        "python", "core/mail_classifier.py",
        str(json_file), "--output-file", str(json_file)
    ], check=True)

@app.command("summarize")
def summarize(
    file: Path = typer.Option(None, help="Fichier JSON à résumer"),
    label: str = "INBOX"
):
    json_file = file or build_report_filename(label)
    typer.echo("🧠 Résumés LLM...")
    subprocess.run([
        "python", "core/llm_wrapper.py",
        str(json_file)
    ], check=True)

@app.command("md")
def markdown(
    file: Path = typer.Option(None, help="Fichier JSON à transformer en résumé .md"),
    label: str = "INBOX"
):
    json_file = file or build_report_filename(label)
    typer.echo("📄 Génération Markdown résumé...")
    subprocess.run([
        "python", "core/generate_summary_md.py",
        str(json_file)
    ], check=True)

@app.command("run-all")
def run_all(
    hours: int = 24,
    limit: int = 30,
    label: str = "INBOX"
):
    json_file = build_report_filename(label)

    typer.echo(f"📥 Étape 1 : Dump depuis {label}...")
    subprocess.run([
        "python", "generate_report.py",
        "--hours", str(hours),
        "--limit", str(limit),
        "--label", label
    ], check=True)

    typer.echo("🏷️ Étape 2 : Tagging & scoring...")
    subprocess.run([
        "python", "core/mail_classifier.py",
        str(json_file), "--output-file", str(json_file)
    ], check=True)

    typer.echo("🧠 Étape 3 : Résumés LLM...")
    subprocess.run([
        "python", "core/llm_wrapper.py",
        str(json_file)
    ], check=True)

    typer.echo("📄 Étape 4 : Génération Markdown résumé...")
    subprocess.run([
        "python", "core/generate_summary_md.py",
        str(json_file)
    ], check=True)

    typer.echo("✅ Pipeline complet exécuté avec succès")

if __name__ == "__main__":
    app(prog_name="main", args=sys.argv[1:])