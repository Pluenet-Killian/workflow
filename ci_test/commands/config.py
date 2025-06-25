#!/usr/bin/env python3

"""
Implémentation de la commande config pour ci_test
"""

from ci_test.utils import config_utils

def execute(args):
    """Exécute la commande config."""
    if hasattr(args, 'delete') and args.delete is not None:
        return set_delete_config(args.delete)
    elif hasattr(args, 'list') and args.list:
        return list_config()
    else:
        print("🚨  Erreur: Option de configuration manquante")
        print("Usage: ci_test config --delete=true|false ou ci_test config --list")
        return 1

def set_delete_config(delete_value):
    """Configure la suppression automatique des branches mergées."""
    try:
        # Convertir la chaîne en booléen
        if isinstance(delete_value, str):
            delete_bool = delete_value.lower() in ('true', '1', 'yes', 'on')
        else:
            delete_bool = bool(delete_value)

        success = config_utils.set_setting("delete_merged_branches", delete_bool)

        if success:
            status = "activée" if delete_bool else "désactivée"
            print(f"✅  Suppression automatique des branches mergées {status}")
            return 0
        else:
            print("🚨  Erreur: Impossible de sauvegarder la configuration")
            return 1
    except Exception as e:
        print(f"🚨  Erreur: {e}")
        return 1

def list_config():
    """Affiche la configuration actuelle."""
    try:
        config = config_utils.load_config()
        print("📋  Configuration actuelle:")
        for key, value in config.items():
            if key == "delete_merged_branches":
                status = "activée" if value else "désactivée"
                print(f"  • Suppression automatique des branches mergées: {status}")
            else:
                print(f"  • {key}: {value}")
        return 0
    except Exception as e:
        print(f"🚨  Erreur: {e}")
        return 1
