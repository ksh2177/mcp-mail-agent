# 📬 MCP Mail Agent

Un agent Python souverain et offline pour lire, classer, résumer et prioriser les emails ProtonMail en local, sans cloud, sans dépendance externe.

---

## 🧠 Objectif

Transformer votre messagerie ProtonMail en **centre de tri intelligent** via :

- Parsing IMAP
- Résumé par LLM local (Mistral via Ollama)
- Tagging contextuel (dev, alert, finance...)
- Scoring de priorité
- Génération de rapports `.md` et `.json`

---

## 🏗️ Stack technique

- **Langage** : Python 3.13
- **LLM local** : [Ollama](https://ollama.com) + `mistral`
- **Email** : ProtonMail Bridge (IMAP localhost)
- **Libs** : `imaplib`, `typer`, `requests`, `dotenv`, `jinja2`

Structure :

```
mcp-mail-agent/
├── core/
│   ├── imap_client.py          # Connexion IMAP + nettoyage
│	├── mail_classifier.py      # Tag + score par règles simples
│	└── llm_wrapper.py          # Résumé LLM via Ollama
├── reports/                    # Fichiers générés (md + json)
├── generate_report.py          # Génère les rapports quotidiens
├── main.py                     # Orchestrateur futur
├── requierment.txt             # Pré requis pour le .env
└── test_imap.py                # Test de connexion IMAP
```

---
## ✅ Fonctionnalités

-  Connexion IMAP via ProtonMail Bridge (auth `.env`, port local sécurisé)
-  Récupération des mails récents, nettoyage HTML, base64, quoted-printable
-  Filtrage automatique des mails techniques (notify, calendar, bridge)
-  Génération de rapports `.md` et `.json` horodatés dans `reports/`
-  Classification rule-based (`dev`, `alert`, `finance`) via `classifier.py`
-  Attribution de score de priorité (échelle de 0 à 8)
-  Résumé automatique par LLM local (Ollama + Mistral) via `llm_wrapper.py`
-  Interface CLI unifiée (via Typer) pour tous les modules
---

## 🔧 Utilisation

### Récupérer et générer un rapport brut

```bash
python generate_report.py
```

### Enrichir avec des tags / priorités

```bash
python classifier.py reports/report_2025-07-05.json
```

### Ajouter un résumé via LLM (Ollama)

```bash
python llm_wrapper.py reports/report_2025-07-05.json
```

---

## 🔐 Sécurité

- `.env` local avec credentials IMAP (non versionné)
- `.gitignore` strict (exclut rapports, secrets, .venv)
- Historique Git nettoyé (aucune fuite)

---

## 🔜 Prochaines étapes

-  Ajouter `--dry-run` pour `classifier.py` et `llm_wrapper.py`
-  Ajouter support `--output` pour générer un fichier `.json` à part
-  Générer un fichier `.summary.md` lisible humainement
-  Créer une intégration Plane.so (task auto pour `alert`, `finance`)
-  Publier alertes critiques sous forme de GitLab Issue
[text](about:blank#blocked)-  Intégration de notification via webhook (Matrix, Discord, etc.)
-  Ajouter une interface terminale via `textual` pour suivi/visualisation
-  Implémenter une auto-réponse (template + SMTP Proton Bridge)
-  Dockeriser le projet + ajouter `Makefile` ou `playbook.yml` pour orchestrer

---

## 🤝 Contrib

Projet personnel évolutif. Si tu veux jouer avec, cloner, fork, tester ou dockeriser, bienvenue. Tout tourne **100% offline**.

