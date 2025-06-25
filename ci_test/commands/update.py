#!/usr/bin/env python3
"""
Implémentation de la commande update pour ci_test
"""

from ci_test.utils import git_utils
from ci_test.commands import push

def execute(args):
    """Exécute la commande update."""
    return implement_update(args)

def implement_update(args):
    current_branch = git_utils.get_current_branch()
    if current_branch is None:
        print("🚨  Erreur: Impossible de déterminer la branche courante")
        return 1

    # Cas 1 : branche module (mod/*/main)
    if current_branch.startswith("mod/") and current_branch.endswith("/main"):
        # Si un argument est donné, c'est une erreur pour les branches module
        if hasattr(args, 'dev') and args.dev:
            print("🚨  Erreur: Vous ne pouvez pas spécifier de branche cible sur une branche module")
            print("💡  Utilisez simplement: ci_test update")
            return 1

        target = "dev"
        print(f"🔄  Rebase de {current_branch} sur {target}...")
        fetch_success, fetch_error = git_utils.fetch_branch("origin", target)
        if not fetch_success:
            print(f"🚨  Erreur: Impossible de mettre à jour la branche {target}\n{fetch_error}")
            return 1
        rebase_success, rebase_error = git_utils.rebase_branch(f"origin/{target}")
        if not rebase_success:
            print(f"🚨  Erreur: Impossible de rebase\n{rebase_error}")
            print("📝  Résolvez les conflits et relancez 'ci_test update'")
            return 1

        # Vérification du build et push
        if hasattr(args, 'force') and args.force:
            print("⚠️  Mode force activé, les vérifications de build ne seront pas effectuées")
            push_args = type('Args', (), {'debug': getattr(args, 'debug', False), 'force': True})
        else:
            print("🔍  Vérification du build...")
            push_args = type('Args', (), {'debug': getattr(args, 'debug', False)})

        push_result = push.execute(push_args)
        if push_result != 0:
            print("🚨  Erreur: La vérification du build ou le push a échoué")
            return push_result

        print(f"✅  Branche {current_branch} mise à jour sur {target}")
        return 0

    # Cas 2 : branche issue (mod/*/issue)
    if current_branch.startswith("mod/") and current_branch.count("/") == 2 and not current_branch.endswith("/main"):
        parts = current_branch.split("/")
        module_branch = f"mod/{parts[1]}/main"
        # Si un argument est donné, update module + issue
        if hasattr(args, 'dev') and args.dev and args.dev == "dev":
            target = args.dev
            print(f"🔄  Rebase de {module_branch} sur {target}...")
            fetch_success, fetch_error = git_utils.fetch_branch("origin", target)
            if not fetch_success:
                print(f"🚨  Erreur: Impossible de mettre à jour la branche {target}\n{fetch_error}")
                return 1
            checkout_success, checkout_error = git_utils.checkout_branch(module_branch)
            if not checkout_success:
                print(f"🚨  Erreur: Impossible de checkout {module_branch}\n{checkout_error}")
                return 1
            rebase_success, rebase_error = git_utils.rebase_branch(f"origin/{target}")
            if not rebase_success:
                print(f"🚨  Erreur: Impossible de rebase {module_branch} sur {target}\n{rebase_error}")
                print("📝  Résolvez les conflits et relancez 'ci_test update'")
                return 1

            # Vérifier le build et push de la branche module
            if hasattr(args, 'force') and args.force:
                print("⚠️  Mode force activé, les vérifications de build ne seront pas effectuées")
                push_args = type('Args', (), {'debug': getattr(args, 'debug', False), 'force': True})
            else:
                print("🔍  Vérification du build...")
                push_args = type('Args', (), {'debug': getattr(args, 'debug', False)})

            push_result = push.execute(push_args)
            if push_result != 0:
                print("🚨  Erreur: La vérification du build ou le push de la branche module a échoué")
                return push_result

            # Retour sur la branche issue
            checkout_success, checkout_error = git_utils.checkout_branch(current_branch)
            if not checkout_success:
                print(f"🚨  Erreur: Impossible de revenir sur {current_branch}\n{checkout_error}")
                return 1
            print(f"🔄  Rebase de {current_branch} sur {module_branch}...")
            rebase_success, rebase_error = git_utils.rebase_branch(module_branch)
            if not rebase_success:
                print(f"🚨  Erreur: Impossible de rebase {current_branch} sur {module_branch}\n{rebase_error}")
                print("📝  Résolvez les conflits et relancez 'ci_test update'")
                return 1

            # Vérifier le build et push de la branche issue
            if hasattr(args, 'force') and args.force:
                print("⚠️  Mode force activé, les vérifications de build ne seront pas effectuées")
                push_args = type('Args', (), {'debug': getattr(args, 'debug', False), 'force': True})
            else:
                print("🔍  Vérification du build...")
                push_args = type('Args', (), {'debug': getattr(args, 'debug', False)})

            push_result = push.execute(push_args)
            if push_result != 0:
                print("🚨  Erreur: La vérification du build ou le push de la branche issue a échoué")
                return push_result

            print(f"✅  Branche {current_branch} mise à jour sur {module_branch} (et {module_branch} sur {target})")
            return 0
        else:
            # Sinon, rebase issue sur module
            print(f"🔄  Rebase de {current_branch} sur {module_branch}...")
            fetch_success, fetch_error = git_utils.fetch_branch("origin", module_branch)
            if not fetch_success:
                print(f"🚨  Erreur: Impossible de mettre à jour la branche {module_branch}\n{fetch_error}")
                return 1
            rebase_success, rebase_error = git_utils.rebase_branch(f"origin/{module_branch}")
            if not rebase_success:
                print(f"🚨  Erreur: Impossible de rebase\n{rebase_error}")
                print("📝  Résolvez les conflits et relancez 'ci_test update'")
                return 1

            # Vérifier le build et push
            if hasattr(args, 'force') and args.force:
                print("⚠️  Mode force activé, les vérifications de build ne seront pas effectuées")
                push_args = type('Args', (), {'debug': getattr(args, 'debug', False), 'force': True})
            else:
                print("🔍  Vérification du build...")
                push_args = type('Args', (), {'debug': getattr(args, 'debug', False)})

            push_result = push.execute(push_args)
            if push_result != 0:
                print("🚨  Erreur: La vérification du build ou le push a échoué")
                return push_result

            print(f"✅  Branche {current_branch} mise à jour sur {module_branch}")
            return 0

    print("🚨  Erreur: Vous n'êtes pas sur une branche module ou issue")
    return 1
