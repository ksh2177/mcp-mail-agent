
from textual.app import App, ComposeResult
from textual.widgets import Static, Header, Footer, DataTable
from textual.reactive import reactive
from textual.containers import Horizontal
import json
from pathlib import Path
import sys

class MailViewer(App):
    CSS_PATH = "viewer.tcss"
    BINDINGS = [("q", "quit", "Quitter")]

    mails = reactive([])

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = Path(file_path)

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            self.table = DataTable(id="mail_table")
            self.table.cursor_type = "row"
            yield self.table

            self.detail = Static("Sélectionne un mail pour voir le résumé", id="detail")
            yield self.detail
        yield Footer()

    def on_mount(self):
        if not self.file_path.exists():
            self.exit(f"❌ Fichier non trouvé : {self.file_path}")
            return

        with self.file_path.open("r", encoding="utf-8") as f:
            self.mails = json.load(f)

        self.table.add_columns("Date", "De", "Sujet", "Tags", "Score")
        for mail in self.mails:
            self.table.add_row(
                mail.get("date", ""),
                f"{mail.get('from_name', '')} <{mail.get('from_email', '')}>",
                mail.get("subject", "")[:40],
                ", ".join(mail.get("tags", [])),
                str(mail.get("score", "") or "")
            )

        self.table.focus()
        self.set_interval(0.1, self.refresh_detail)

    def refresh_detail(self):
        if not self.mails or not self.table.row_count:
            return
        row_idx = self.table.cursor_row
        if row_idx is None or row_idx >= len(self.mails):
            return

        mail = self.mails[row_idx]

        tag_colors = {
            "alert": "bold red",
            "finance": "bold green",
            "dev": "bold cyan"
        }

        colored_tags = []
        for tag in mail.get("tags", []):
            style = tag_colors.get(tag, "white")
            colored_tags.append(f"[{style}]{tag}[/]")

        score = mail.get("score", "?")
        score_color = "bold red" if score == 8 else ("green" if score else "dim")

        content = f"""
[bold violet]{mail.get("subject", "")}[/bold violet]
De : [italic]{mail.get("from_name", "")}[/] <{mail.get("from_email", "")}>
Date : {mail.get("date", "")}
Tags : {" | ".join(colored_tags) or "[dim]aucun[/]"}
Score : [{score_color}]{score}[/{score_color}]

[bold]Résumé :[/]
[italic]{mail.get("summary", "(pas de résumé)")}[/italic]

[dim]--- Corps brut (extrait) ---[/dim]
{mail.get("body", "")[:500]}...
"""
        self.detail.update(content)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python viewer.py <fichier.json>")
        sys.exit(1)

    app = MailViewer(sys.argv[1])
    app.run()