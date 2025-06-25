#!/usr/bin/env python3

"""
Implémentation de la commande clone pour ci_test
"""

import os
from ci_test.utils import git_utils

def execute(args):
    orig_dir = os.getcwd()
    if hasattr(args, 'url') and args.url:
        print("🔍  Clonage du repo...")
        clone_success, clone_error = git_utils.clone(args.url)
        if not clone_success:
            print(f"🚨  Erreur: Clonage impossible\n{clone_error}")
            return 1
        print("✅  Clonage réussi")
        os.chdir(os.path.join(orig_dir, args.url.split('/')[-1].replace('.git', '')))
    print("🔄  Initialisation du projet...")

    if not git_utils.has_remote():
        print("🚨  Erreur: Aucun remote configuré")
        return 1

    if git_utils.has_head() or git_utils.has_remote_branches():
        print("ℹ️  Dépôt non vide. Aucune initialisation nécessaire.")
        return 1

    initMain_success, initMain_error = git_utils.init_empty_branch("main")
    if not initMain_success:
        print(f"🚨  Erreur: Impossible d'initialiser la branche main\n{initMain_error}")
        return 1

    if not git_utils.create_branch("dev", True):
        print("🚨  Erreur: Impossible de créer la branche dev")
        return 1

    initDev_success, initDev_error = git_utils.init_empty_branch("dev")
    if not initDev_success:
        print(f"🚨  Erreur: Impossible d'initialiser la branche dev\n{initDev_error}")
        return 1
    print("✅  Initialisation réussie | N'oubliez pas de créer un makefile valide et de le pusher !")
