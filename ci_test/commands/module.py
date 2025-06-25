#!/usr/bin/env python3

"""
Implémentation de la commande module pour ci_test
"""

from ci_test.utils import git_utils

def execute(args):
    """Exécute la commande module."""
    # 1. Vérifier que l'utilisateur est sur la branche dev
    current_branch = git_utils.get_current_branch()
    if current_branch != "dev":
        print("🚨  Erreur: Vous devez être sur la branche dev pour créer un module")
        return 1

    # 2. Mettre à jour la branche dev locale par rapport à la référence distante
    print("🔄  Mise à jour de la branche dev...")
    fetch_success, fetch_error = git_utils.fetch_branch("origin", "dev")
    if not fetch_success:
        print(f"🚨  Erreur: Impossible de mettre à jour la branche dev\n{fetch_error}")
        return 1

    # 3. Vérifier si la branche module existe déjà
    module_name = f"mod/{args.name}/main"
    if git_utils.branch_exists("origin", module_name):
        print(f"ℹ️  La branche {module_name} existe déjà")
        return 0

    # 4. Créer la branche module
    print(f"🔍  Création de la branche {module_name}...")
    if not git_utils.create_branch(module_name):
        print(f"🚨  Erreur: Impossible de créer la branche {module_name}")
        return 1

    # 5. Publier la branche module
    print(f"🚀  Publication de la branche {module_name}...")
    push_success, push_error = git_utils.push_branch("origin", module_name)
    if not push_success:
        print(f"🚨  Erreur: Impossible de publier la branche {module_name}\n{push_error}")
        return 1

    print(f"✅  Branche {module_name} créée et publiée")
    return 0
