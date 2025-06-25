"""
Utilitaires pour gérer la configuration de ci_test
"""

import os
import json
from pathlib import Path

def get_config_file_path():
    """Récupère le chemin du fichier de configuration."""
    # Utiliser le répertoire home de l'utilisateur
    home_dir = Path.home()
    config_dir = home_dir / ".ci_test"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "config.json"

def load_config():
    """Charge la configuration depuis le fichier."""
    config_file = get_config_file_path()
    default_config = {
        "delete_merged_branches": False  # Par défaut, ne pas supprimer les branches mergées
    }

    if not config_file.exists():
        return default_config

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        # Fusionner avec la config par défaut pour les nouvelles clés
        return {**default_config, **config}
    except Exception:
        return default_config

def save_config(config):
    """Sauvegarde la configuration dans le fichier."""
    config_file = get_config_file_path()
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception:
        return False

def get_setting(key, default=None):
    """Récupère une valeur de configuration."""
    config = load_config()
    return config.get(key, default)

def set_setting(key, value):
    """Définit une valeur de configuration."""
    config = load_config()
    config[key] = value
    return save_config(config)

def should_delete_merged_branches():
    """Vérifie si les branches mergées doivent être supprimées."""
    return get_setting("delete_merged_branches", False)
