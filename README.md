
# Sentinel

Petit service de surveillance (monitoring) léger qui exécute des contrôles périodiques et envoie des alertes via Telegram.

## Fonctionnalités
- Surveillance système/processus configurable via `app.py` (`monitor_system`).
- Envoi d'alertes Telegram (`send_telegram_alert`).
- Conçu pour être exécuté localement ou en conteneur (Docker + docker-compose).

## Arborescence importante
- `app.py` — logique principale du service (contrôles, envoi d'alertes).
- `requirements.txt` — dépendances Python.
- `Dockerfile`, `.dockerignore`, `docker-compose.yml` — configuration conteneurisée.
- `.env.example` — exemple de variables d'environnement (ne pas committer de secrets).

## Prérequis
- Python 3.10+ recommandé.
- Docker & docker-compose pour exécution conteneurisée.
- Un token pour un bot Telegram et un `CHAT_ID` pour recevoir les alertes.

## Installation (local)
1. Cloner le dépôt :
	 ```bash
	 git clone <repo-url> /home/kpihx/Work/Homelab/sentinel
	 cd /home/kpihx/Work/Homelab/sentinel
	 ```
2. Créer un environnement virtuel et installer les dépendances :
	 ```bash
	 python -m venv .venv
	 source .venv/bin/activate
	 pip install -r requirements.txt
	 ```
3. Configuration :
	 - Copier l'exemple et remplir les valeurs :
		 ```bash
		 cp .env.example .env
		 # Éditer .env et renseigner TELEGRAM_TOKEN et CHAT_ID
		 ```
	 - S'assurer que `.env` est ignoré par git (ne pas committer les secrets) :
		 ```bash
		 git rm --cached .env || true
		 git add .gitignore
		 git commit -m "Stop tracking .env and ensure it's ignored" || true
		 ```
4. Lancer l'application :
	 ```bash
	 python app.py
	 ```

## Variables d'environnement
Remplir `.env` (ou utiliser un secret manager) avec les variables suivantes :

- `TELEGRAM_TOKEN` — token du bot Telegram.
- `CHAT_ID` — identifiant du chat destinataire des alertes.

Exemple minimal (fichier `.env.example` fourni) :
```
TELEGRAM_TOKEN=your_telegram_bot_token_here
CHAT_ID=your_chat_id_here
```

## Docker
- Build :
	```bash
	docker build -t sentinel .
	```
- Execution :
	```bash
	docker run --env-file .env --name sentinel sentinel
	```
- Avec `docker-compose` :
	```bash
	docker-compose up -d --build
	```

## Logs & debug
- Les logs sont envoyés sur la sortie standard ; utiliser `docker logs` pour les conteneurs.
- Vérifier les fichiers ignorés :
	```bash
	git ls-files --others --exclude-standard
	```

## Tests
- Aucun test automatisé détecté. Pour ajouter des tests : installer `pytest` et créer un dossier `tests/`.

## Contribution
- Ouvrir une issue ou PR. Ne pas committer de secrets : utilisez `.env.example` pour documenter les variables nécessaires.

## Licence
- Ce projet est distribué sous la licence MIT. Voir le fichier `LICENSE` pour le texte complet.

Badge de licence :

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

