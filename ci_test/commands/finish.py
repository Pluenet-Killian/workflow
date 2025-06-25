#!/usr/bin/env python3

"""
Implémentation de la commande finish pour ci_test
"""

import os
import sys
from ci_test.utils import git_utils, config_utils
from ci_test.commands import push

def execute(args):
    """Exécute la commande finish."""
    # Structure principale de la fonction
    return implement_finish(args)

def implement_finish(args):
    """Implémentation de la logique de finish."""
    # 1. Vérifier si un rebase est en cours
    if git_utils.is_rebase_in_progress():
        print("🔄  Continuation du rebase en cours...")
        print("📝  Résolvez les conflits et relancez 'ci_test finish'")
        return 1
        """ rebase_success, rebase_error = git_utils.rebase_continue()
        if not rebase_success:
            print(f"🚨  Erreur: Impossible de continuer le rebase\n{rebase_error}") """ # Pourrait fonctionner mais nécessite que l'user change le nom du commit, etc. Plus simple de continue par le merge editor de vscode.

    # 2. Détection du type de branche
    branch_type = detect_branch_type()
    if branch_type is None:
        print("🚨  Erreur: Vous n'êtes pas sur une branche de travail (module ou issue)")
        return 1

    # 3. Exécution du workflow approprié selon le type de branche
    if branch_type == "issue":
        return finish_issue(args)
    elif branch_type == "module":
        return finish_module(args)

def detect_branch_type():
    """Détecte le type de branche courante (module, issue ou autre)."""
    current_branch = git_utils.get_current_branch()
    if current_branch is None:
        return None

    # Vérifier si c'est une branche issue (mod/*/*)
    if current_branch.startswith("mod/") and current_branch.count("/") == 2:
        parts = current_branch.split("/")
        if len(parts) == 3 and parts[2] != "main":
            return "issue"

    # Vérifier si c'est une branche module (mod/*/main)
    if current_branch.startswith("mod/") and current_branch.endswith("/main"):
        return "module"

    return None

def finish_issue(args):
    """Termine une branche issue en la fusionnant dans sa branche module."""
    current_branch = git_utils.get_current_branch()
    parts = current_branch.split("/")
    module_name = parts[1]
    issue_name = parts[2]

    # Branche cible (module)
    target_branch = f"mod/{module_name}/main"

    # 1. Mettre à jour la référence distante du module
    print(f"🔄  Mise à jour de la référence distante {target_branch}...")
    fetch_success, fetch_error = git_utils.fetch_branch("origin", target_branch)
    if not fetch_success:
        print(f"🚨  Erreur: Impossible de mettre à jour la référence distante\n{fetch_error}")
        return 1

    # 2. Vérifier si un rebase est nécessaire
    if not git_utils.is_ancestor(f"origin/{target_branch}", current_branch):
        print(f"🔄  Rebase de {current_branch} sur origin/{target_branch}...")
        rebase_success, rebase_error = git_utils.rebase_branch(f"origin/{target_branch}")
        if not rebase_success:
            print(f"🚨  Erreur: Impossible de rebase\n{rebase_error}")
            print("📝  Résolvez les conflits et relancez 'ci_test finish'")
            return 1

    if hasattr(args, 'force') and args.force:
        print("⚠️  Mode force activé, les vérifications de build ne seront pas effectuées")
        push_args = type('Args', (), {'debug': getattr(args, 'debug', False), 'force': True})
        push_result = push.execute(push_args)
        if push_result != 0:
            print("🚨  Erreur: La vérification du build a échoué")
            return push_result
    else:
        # 3. Vérifier le build avant fusion
        print(f"🔍  Vérification du build sur {current_branch} avant fusion...")
        push_args = type('Args', (), {'debug': getattr(args, 'debug', False)})
        push_result = push.execute(push_args)
        if push_result != 0:
            print("🚨  Erreur: La vérification du build a échoué")
            return push_result

    # 4. Checkout de la branche module
    print(f"🔄  Checkout de la branche {target_branch}...")
    checkout_success, checkout_error = git_utils.checkout_branch(target_branch)
    if not checkout_success:
        print(f"🚨  Erreur: Impossible de checkout {target_branch}\n{checkout_error}")
        return 1

    # 5. Merge
    print(f"🔄  Merge de {current_branch} dans {target_branch}...")
    merge_success, merge_error = git_utils.merge_branch(current_branch)
    if not merge_success:
        print(f"🚨  Erreur: Impossible de merger\n{merge_error}")
        return 1

    if hasattr(args, 'force') and args.force:
        print("⚠️  Mode force activé, les vérifications de build ne seront pas effectuées après le merge")
        push_args = type('Args', (), {'debug': getattr(args, 'debug', False), 'force': True})
        push_result = push.execute(push_args)
        if push_result != 0:
            print("🚨  Erreur: La vérification du build après le merge a échoué")
            return push_result
    else:
        # 6. Vérification du build avec push
        print("🔍  Vérification du build...")
        push_args = type('Args', (), {'debug': getattr(args, 'debug', False)})
        push_result = push.execute(push_args)
        if push_result != 0:
            print("🚨  Erreur: La vérification du build a échoué")
            return push_result

    # 7. Suppression optionnelle de la branche issue
    if config_utils.should_delete_merged_branches():
        print(f"🗑️  Suppression de la branche {current_branch}...")

        # Supprimer la branche locale
        delete_success, delete_error = git_utils.delete_branch(current_branch)
        if not delete_success:
            print(f"⚠️   Warn: Impossible de supprimer la branche locale {current_branch}: {delete_error}")

        # Supprimer la branche distante
        remote_delete_success, remote_delete_error = git_utils.delete_remote_branch("origin", current_branch)
        if not remote_delete_success:
            print(f"⚠️   Warn: Impossible de supprimer la branche distante {current_branch}: {remote_delete_error}")

        if delete_success and remote_delete_success:
            print(f"✅  Branche {current_branch} supprimée")

    print(f"✅  Issue {issue_name} fusionnée avec succès dans {target_branch}")
    return 0

def finish_module(args):
    """Termine une branche module en la fusionnant dans dev."""
    current_branch = git_utils.get_current_branch()
    parts = current_branch.split("/")
    module_name = parts[1]

    # Branche cible
    target_branch = "dev"

    # 1. Mettre à jour la référence distante de dev
    print(f"🔄  Mise à jour de la référence distante {target_branch}...")
    fetch_success, fetch_error = git_utils.fetch_branch("origin", target_branch)
    if not fetch_success:
        print(f"🚨  Erreur: Impossible de mettre à jour la référence distante\n{fetch_error}")
        return 1

    # 2. Vérifier si un rebase est nécessaire
    if not git_utils.is_ancestor(f"origin/{target_branch}", current_branch):
        print(f"🔄  Rebase de {current_branch} sur origin/{target_branch}...")
        rebase_success, rebase_error = git_utils.rebase_branch(f"origin/{target_branch}")
        if not rebase_success:
            print(f"🚨  Erreur: Impossible de rebase\n{rebase_error}")
            print("📝  Résolvez les conflits et relancez 'ci_test finish'")
            return 1

    if hasattr(args, 'force') and args.force:
        print("⚠️  Mode force activé, les vérifications de build ne seront pas effectuées")
        push_args = type('Args', (), {'debug': getattr(args, 'debug', False), 'force': True})
        push_result = push.execute(push_args)
        if push_result != 0:
            print("🚨  Erreur: La vérification du build a échoué")
            return push_result
    else:
        # 3. Vérifier le build avant fusion
        print(f"🔍  Vérification du build sur {current_branch}...")
        push_args = type('Args', (), {'debug': getattr(args, 'debug', False)})
        push_result = push.execute(push_args)
        if push_result != 0:
            print("🚨  Erreur: La vérification du build a échoué")
            return push_result

    print(f"✅  Module {module_name} prêt à la fusion dans {target_branch} | N'oubliez pas de faire une PR sur github.")
    git_url = git_utils.get_remote_url()
    if not git_url:
        print("🚨  Erreur: Impossible de récupérer l'URL du dépôt distant")
        return 1
    # Supprimer le préfixe git@github.com:
    if git_url.startswith("git@github.com:"):
        git_url = git_url[len("git@github.com:"):]
    if git_url.endswith(".git"):
        git_url = git_url[:-len(".git")]
    # Ajouter le suffixe pour la PR
    git_url += f"/compare/{target_branch}...{current_branch}"
    if not git_url.startswith("https://github.com/"):
        git_url = f"https://github.com/{git_url}"
    print(f"🔗  {git_url}")
    return 0
