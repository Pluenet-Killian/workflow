"""
Utilitaires pour interagir avec Docker
"""

import subprocess
import os
import sys

def run_container(tarball_path, debug_mode, type='build'):
    """Exécute le conteneur Docker avec le tarball monté."""
    try:
        # Construire la commande Docker
        cmd = [
            'docker', 'run', '--rm',
            '-v', f"{tarball_path}:/mnt/",
            'ci_image',
            type,
            f"--verbose={str(debug_mode).lower()}",
        ]
        # Exécuter la commande
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )

        # Combiner stdout et stderr pour les logs
        logs = result.stdout + "\n" + result.stderr
        # Retourner le succès (code 0) et les logs
        return result.returncode == 0, logs
    except Exception as e:
        return False, str(e)

def check_image_exists():
    """Vérifie si l'image Docker existe déjà."""
    try:
        result = subprocess.run(
            ['docker', 'image', 'inspect', 'ci_image'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        return result.returncode == 0
    except Exception:
        return False
