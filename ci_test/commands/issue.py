#!/usr/bin/env python3

"""
Implémentation de la commande issue pour ci_test
"""

from ci_test.utils import git_utils

def execute(args):
    """Exécute la commande issue."""
    # 1. Vérifier que l'utilisateur est sur une branche module
    current_branch = git_utils.get_current_branch()
    if not current_branch.startswith("mod/") and current_branch.endswith("main"):
        print("🚨  Erreur: Vous devez être sur une branche module (mod/*/main) pour créer une issue")
        return 1

    # 2. Extraire le nom du module
    module_name = current_branch.split("/")[1]

    # 3. Vérifier si la branche issue existe déjà
    issue_name = f"mod/{module_name}/{args.name}"
    if git_utils.branch_exists("origin", issue_name):
        print(f"ℹ️  La branche {issue_name} existe déjà")
        return 0

    # 4. Créer la branche issue
    print(f"🔍  Création de la branche {issue_name}...")
    if not git_utils.create_branch(issue_name):
        print(f"🚨  Erreur: Impossible de créer la branche {issue_name}")
        return 1

    # 5. Publier la branche issue
    print(f"🚀  Publication de la branche {issue_name}...")
    push_success, push_error = git_utils.push_branch("origin", issue_name)
    if not push_success:
        print(f"🚨  Erreur: Impossible de publier la branche {issue_name}\n{push_error}")
        return 1

    print(f"✅  Branche {issue_name} créée et publiée")
    return 0
