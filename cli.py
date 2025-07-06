import typer
import subprocess
from datetime import datetime
from pathlib import Path
import sys

app = typer.Typer(no_args_is_help=True)

@app.command("run-all")
def run_all(hours: int = 24, limit: int = 30):
    now = datetime.now().strftime("%Y-%m-%d")
    json_file = Path(f"reports/report_{now}.json")

    typer.echo("📥 Étape 1 : Génération du rapport...")
    subprocess.run(["python", "generate_report.py"], check=True)

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
