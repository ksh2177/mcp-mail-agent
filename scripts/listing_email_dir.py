import sys
from pathlib import Path
import imaplib
import re
import argparse
import base64
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich import print

sys.path.append(str(Path(__file__).resolve().parents[1]))
from core.imap_client import IMAPClient

def decode_utf7(name: str) -> str:
    try:
        return imaplib.IMAP4._decode_utf7(name)
    except Exception:
        return name

def encode_utf7_imap(folder: str) -> str:
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

def display_table(folders: list, filter_prefix: str = None):
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Nom", style="cyan")
    table.add_column("Flags", style="yellow")
    table.add_column("Séparateur", style="dim")

    for folder in folders:
        name = decode_utf7(folder["name"])
        if filter_prefix and not name.startswith(filter_prefix):
            continue
        flags = ", ".join(folder["flags"])
        table.add_row(name, flags, folder["separator"])

    console.print(table)

def display_tree(folders: list):
    console = Console()
    tree = Tree("[bold blue]Dossiers IMAP")

    nodes = {}
    for folder in sorted(folders, key=lambda f: f["name"]):
        path = decode_utf7(folder["name"]).split("/")
        current = tree
        for part in path:
            if (id(current), part) not in nodes:
                nodes[(id(current), part)] = current.add(part)
            current = nodes[(id(current), part)]

    console.print(tree)

def export_json(folders: list, output_file: str):
    import json
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(folders, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Export JSON créé : {output_file}")

def probe_hidden_folders(client: IMAPClient, folder_names: list):
    console = Console()
    console.print("\n[bold underline]🔍 Probing dossiers manuellement :\n")
    for folder in folder_names:
        encoded = encode_utf7_imap(folder)
        try:
            typ, _ = client.conn.select(encoded)
            if typ == "OK":
                console.print(f"[green]✅ Accessible :[/green] {folder}")
            else:
                console.print(f"[red]❌ SELECT KO :[/red] {folder} (type={typ})")
        except Exception as e:
            console.print(f"[red]❌ Erreur sur {folder} :[/red] {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lister les dossiers IMAP visibles")
    parser.add_argument("--filter", help="Filtrer par préfixe (ex: Labels/Proton)", default=None)
    parser.add_argument("--tree", action="store_true", help="Afficher en vue arborescente")
    parser.add_argument("--json", help="Exporter au format JSON (fichier)", default=None)
    parser.add_argument("--probe", action="store_true", help="Tenter d'accéder à certains dossiers manquants")
    args = parser.parse_args()

    client = IMAPClient()
    client.connect()
    folders = client.list_all_accessible_folders()

    if args.probe:
        hidden_targets = [
            "Folders/CS CONSULTING - PRO",
            "Folders/CS CONSULTING - PRO/URSSAF",
            "Folders/Mani - Perso",
            "Folders/ksh - Dev"
        ]
        probe_hidden_folders(client, hidden_targets)
    elif args.json:
        export_json(folders, args.json)
    elif args.tree:
        display_tree(folders)
    else:
        display_table(folders, filter_prefix=args.filter)
