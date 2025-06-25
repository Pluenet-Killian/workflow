#!/usr/bin/env python3

"""
Implémentation de la commande release pour ci_test
"""

import re
from ci_test.utils import git_utils

def execute(args):
    """Exécute la commande release."""
    return implement_release()

def implement_release():
    """Implémentation de la logique de release."""
    # 1. Vérifier que l'utilisateur est sur la branche dev
    current_branch = git_utils.get_current_branch()
    if current_branch != "dev":
        print("🚨  Erreur: Vous devez être sur la branche dev pour créer une release")
        return 1

    # 2. Mettre à jour la branche dev locale
    print("🔄  Mise à jour de la branche dev...")
    fetch_success, fetch_error = git_utils.fetch_branch("origin", "dev")
    if not fetch_success:
        print(f"🚨  Erreur: Impossible de mettre à jour la branche dev\n{fetch_error}")
        return 1

    pull_success, pull_error = git_utils.pull_branch("dev")
    if not pull_success:
        print(f"🚨  Erreur: Impossible de pull la branche dev\n{pull_error}")
        return 1

    # 3. Checkout de la branche main
    print("🔄  Checkout de la branche main...")
    checkout_success, checkout_error = git_utils.checkout_branch("main")
    if not checkout_success:
        print(f"🚨  Erreur: Impossible de checkout main\n{checkout_error}")
        return 1

    # 4. Déterminer le numéro de version suivant
    print("🔍  Détermination du numéro de version...")
    next_version = get_next_version()
    if next_version is None:
        print("🚨  Erreur: Impossible de déterminer le numéro de version")
        return 1
    print(f"📦  Préparation de la release {next_version}.0...")

    # 5. Nettoyer le répertoire de travail
    print("🧹  Nettoyage du répertoire de travail...")
    clean_success, clean_error = git_utils.remove_all_cached()
    if not clean_success:
        print(f"🚨  Erreur: Impossible de nettoyer le cache\n{clean_error}")
        return 1

    clean_wd_success, clean_wd_error = git_utils.clean_working_directory()
    if not clean_wd_success:
        print(f"🚨  Erreur: Impossible de nettoyer le répertoire de travail\n{clean_wd_error}")
        return 1

    # 6. Copier le contenu de dev
    print("📋  Copie du contenu de dev...")
    copy_success, copy_error = git_utils.checkout_files_from_branch("dev")
    if not copy_success:
        print(f"🚨  Erreur: Impossible de copier les fichiers de dev\n{copy_error}")
        return 1

    # 7. Ajouter tous les fichiers
    print("➕  Ajout des fichiers...")
    add_success, add_error = git_utils.add_all()
    if not add_success:
        print(f"🚨  Erreur: Impossible d'ajouter les fichiers\n{add_error}")
        return 1

    # 8. Créer le commit de release
    commit_message = f"Release {next_version}.0 - snapshot of dev"
    print(f"💾  Création du commit: {commit_message}")
    commit_success, commit_error = git_utils.commit(commit_message)
    if not commit_success:
        print(f"🚨  Erreur: Impossible de créer le commit\n{commit_error}")
        return 1

    # 9. Créer le tag
    tag_name = f"{next_version}.0"
    tag_message = f"Release {next_version}.0"
    print(f"🏷️  Création du tag {tag_name}...")
    tag_success, tag_error = git_utils.create_tag(tag_name, tag_message)
    if not tag_success:
        print(f"🚨  Erreur: Impossible de créer le tag\n{tag_error}")
        return 1

    # 10. Push de la branche et du tag
    print("🚀  Push de la branche main...")
    push_success, push_error = git_utils.push()
    if not push_success:
        print(f"🚨  Erreur: Impossible de push la branche main\n{push_error}")
        return 1

    print(f"🚀  Push du tag {tag_name}...")
    push_tag_success, push_tag_error = git_utils.push_tag(tag_name)
    if not push_tag_success:
        print(f"🚨  Erreur: Impossible de push le tag\n{push_tag_error}")
        return 1

    print(f"✅  Release {next_version}.0 créée avec succès !")
    print(f"✅  Tag: {tag_name} créée avec succès 🏷️!")
    return 0

def get_next_version():
    """Détermine le numéro de version suivant en analysant l'historique des commits."""
    try:
        # Récupérer l'historique des commits de main
        commits_success, commits_output = git_utils.get_commit_history()
        if not commits_success:
            # Si aucun commit n'existe, commencer à la version 1
            return 1

        # Chercher le dernier commit de release
        release_pattern = r"Release (\d+)\.0 - snapshot of dev"

        for line in commits_output.split('\n'):
            match = re.search(release_pattern, line)
            if match:
                last_version = int(match.group(1))
                return last_version + 1

        # Si aucun commit de release trouvé, commencer à la version 1
        return 1
    except Exception:
        return None
