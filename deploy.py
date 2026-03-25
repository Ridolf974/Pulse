#!/usr/bin/env python3
"""
Script de déploiement automatique vers GitHub Pages
Usage : python3 deploy.py
"""

import urllib.request
import urllib.error
import json
import base64
import os

# ============================================================
# CONFIGURATION
# Définir la variable d'environnement avant d'exécuter :
#   export GITHUB_TOKEN="ghp_votre_token_ici"
# ============================================================
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_USER  = "ridolf974"
GITHUB_REPO  = "ManAlert"
BRANCH       = "main"
# ============================================================

API = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json",
    "User-Agent": "pulse-deploy"
}

def get_sha(path):
    url = f"{API}/{path}?ref={BRANCH}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read())
            return data.get("sha")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise

def push_file(local_path, remote_path, message):
    print(f"  → {remote_path}...", end=" ")
    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode()
    sha = get_sha(remote_path)
    payload = {"message": message, "content": content, "branch": BRANCH}
    if sha:
        payload["sha"] = sha
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{API}/{remote_path}",
        data=data,
        headers=HEADERS,
        method="PUT"
    )
    try:
        with urllib.request.urlopen(req) as r:
            print("✓")
            return True
    except urllib.error.HTTPError as e:
        print(f"✗ Erreur {e.code}: {e.read().decode()}")
        return False

def main():
    if not GITHUB_TOKEN:
        print("ERREUR : variable d'environnement GITHUB_TOKEN non définie.")
        print("  export GITHUB_TOKEN=\"ghp_votre_token_ici\"")
        return
    print("=" * 50)
    print("Déploiement Pulse")
    print("=" * 50)

    files = [
        ("index.html",    "index.html",    "Mise à jour index.html"),
        ("manifest.json", "manifest.json", "Mise à jour manifest.json"),
        ("sw.js",         "sw.js",         "Mise à jour sw.js"),
    ]

    print("\nFichiers à déployer :")
    success = 0
    for local, remote, msg in files:
        if os.path.exists(local):
            if push_file(local, remote, msg):
                success += 1
        else:
            print(f"  ⚠️  {local} introuvable — ignoré")

    print(f"\n{'='*50}")
    print(f"Déploiement terminé : {success}/{len(files)} fichiers")
    print(f"Pulse sera disponible dans 1-2 min sur :")
    print(f"https://{GITHUB_USER}.github.io/{GITHUB_REPO}/")
    print("=" * 50)

if __name__ == "__main__":
    main()
