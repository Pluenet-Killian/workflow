"""
Utilitaires pour interagir avec Git
"""

import subprocess
import os

def verify_head():
    """Vérifie que HEAD existe."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--verify', 'HEAD'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        return result.returncode == 0
    except Exception:
        return False

def create_tarball(output_path):
    """Crée un tarball du dernier commit."""
    try:
        with open(output_path, 'wb') as f:
            result = subprocess.run(
                ['git', 'archive', '--format=tar', 'HEAD'],
                stdout=f,
                stderr=subprocess.PIPE,
                check=True
            )
        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except Exception:
        return False

def amend_commit():
    """Amende le dernier commit pour ajouter le tag CI:Ok."""
    try:
        # Récupérer le message du dernier commit
        result = subprocess.run(
            ['git', 'log', '-1', '--pretty=%B'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            universal_newlines=True
        )
        commit_msg = result.stdout.strip()

        # Amender le commit avec le même message + CI:Ok
        if ("CI:Ok" in commit_msg):
            print("⚠️   Warn: Le commit avait déjà été validé par CI")
            return True
        new_msg = f"{commit_msg} | CI:Ok" if "CI:Ok" not in commit_msg else commit_msg
        subprocess.run(
            ['git', 'commit', '--amend', '--allow-empty', '--only', '-m', new_msg],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except Exception:
        return False

def push():
    """Pousse les modifications vers le dépôt distant."""
    try:
        result = subprocess.run(
            ['git', 'push'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )

        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, ""
    except Exception as e:
        return False, str(e)

def force_push():
    """Force le push des modifications vers le dépôt distant."""
    try:
        result = subprocess.run(
            ['git', 'push', '--force'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )

        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, ""
    except Exception as e:
        return False, str(e)

def clone(url):
    """Clone le dépôt distant."""
    try:
        result = subprocess.run(
            ['git', 'clone', url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )

        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, ""
    except Exception as e:
        return False, str(e)

def has_head():
    """Vérifie si HEAD existe dans le dépôt."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--verify', 'HEAD'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        return result.returncode == 0
    except Exception:
        return False

def has_remote():
    """Vérifie si le dépôt a un remote."""
    try:
        result = subprocess.run(
            ['git', 'remote', '-v'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        return result.returncode == 0 and bool(result.stdout)
    except Exception:
        return False

def has_remote_branches():
    """Vérifie si le dépôt a des branches distantes."""
    try:
        result = subprocess.run(
            ['git', 'branch', '-r'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        return result.returncode == 0 and bool(result.stdout)
    except Exception:
        return False

def init_empty_branch(name):
    """Initialise une nouvelle branche vide"""
    try:
        result = subprocess.run(
            ['git', 'commit', '--allow-empty', '-m', f"Initialization of {name}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )

        if result.returncode != 0:
            return False, result.stderr.strip()

        result = subprocess.run(
            ['git', 'push'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )

        if result.returncode != 0:
            return False, result.stderr.strip()

        return True, ""
    except Exception as e:
        return False, str(e)

def create_branch(name, orphan=False):
    """Crée une nouvelle branche"""
    try:
        if orphan:
            result = subprocess.run(
                ['git', 'checkout', '--orphan', name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
        else:
            result = subprocess.run(
                ['git', 'checkout', '-b', name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )

        if result.returncode != 0:
            return False
        return True
    except Exception:
        return False

def get_current_branch():
    """Récupère le nom de la branche courante."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception:
        return None

def branch_exists(remote, branch_name):
    """Vérifie si une branche existe localement ou à distance."""
    try:
        # Vérifier si la branche existe localement
        local_result = subprocess.run(
            ['git', 'show-ref', '--verify', f'refs/heads/{branch_name}'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        if local_result.returncode == 0:
            return True

        # Essayer de récupérer la branche distante
        fetch_success, _ = fetch_branch(remote, branch_name)

        # Si le fetch a réussi, la branche existe à distance
        return fetch_success
    except Exception:
        return False

def fetch_branch(remote, branch):
    """Met à jour une branche locale à partir d'une branche distante."""
    try:
        result = subprocess.run(
            ['git', 'fetch', remote, branch],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )
        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, ""
    except Exception as e:
        return False, str(e)

def push_branch(remote, branch, set_upstream=True):
    """Pousse une branche vers le dépôt distant."""
    try:
        cmd = ['git', 'push']
        if set_upstream:
            cmd.extend(['-u'])
        cmd.extend([remote, branch])

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )
        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, ""
    except Exception as e:
        return False, str(e)

def is_rebase_in_progress():
    """Vérifie si un rebase est en cours."""
    try:
        git_dir = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        ).stdout.strip()

        return os.path.exists(os.path.join(git_dir, "rebase-apply")) or \
               os.path.exists(os.path.join(git_dir, "rebase-merge"))
    except Exception:
        return False

def rebase_continue():
    """Continue un rebase en cours."""
    try:
        result = subprocess.run(
            ['git', 'rebase', '--continue'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )
        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, ""
    except Exception as e:
        return False, str(e)

def rebase_branch(target_branch):
    """Rebase la branche courante sur une branche cible."""
    try:
        result = subprocess.run(
            ['git', 'rebase', target_branch],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )
        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, ""
    except Exception as e:
        return False, str(e)

def is_ancestor(potential_ancestor, branch):
    """Vérifie si potential_ancestor est un ancêtre de branch."""
    try:
        result = subprocess.run(
            ['git', 'merge-base', '--is-ancestor', potential_ancestor, branch],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        return result.returncode == 0
    except Exception:
        return False

def checkout_branch(branch):
    """Checkout une branche."""
    try:
        result = subprocess.run(
            ['git', 'checkout', branch],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )
        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, ""
    except Exception as e:
        return False, str(e)

def merge_branch(branch):
    """Merge une branche."""
    try:
        result = subprocess.run(
            ['git', 'merge', '--no-ff', branch],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )
        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, ""
    except Exception as e:
        return False, str(e)

def get_remote_url(remote='origin'):
    """Récupère l'URL du dépôt distant."""
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', remote],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception:
        return None

def delete_branch(branch_name, force=False):
    """Supprime une branche locale."""
    try:
        cmd = ['git', 'branch']
        if force:
            cmd.append('-D')
        else:
            cmd.append('-d')
        cmd.append(branch_name)

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )
        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, ""
    except Exception as e:
        return False, str(e)

def delete_remote_branch(remote, branch_name):
    """Supprime une branche distante."""
    try:
        result = subprocess.run(
            ['git', 'push', remote, '--delete', branch_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )
        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, ""
    except Exception as e:
        return False, str(e)

def pull_branch(branch):
    """Pull une branche depuis le remote."""
    try:
        result = subprocess.run(
            ['git', 'pull', 'origin', branch],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )
        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, ""
    except Exception as e:
        return False, str(e)

def remove_all_cached():
    """Supprime tous les fichiers du cache git."""
    try:
        result = subprocess.run(
            ['git', 'rm', '-r', '--cached', '.'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )
        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, ""
    except Exception as e:
        return False, str(e)

def clean_working_directory():
    """Nettoie le répertoire de travail."""
    try:
        result = subprocess.run(
            ['git', 'clean', '-fdq'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )
        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, ""
    except Exception as e:
        return False, str(e)

def checkout_files_from_branch(branch):
    """Checkout tous les fichiers depuis une branche."""
    try:
        result = subprocess.run(
            ['git', 'checkout', branch, '--', '.'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )
        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, ""
    except Exception as e:
        return False, str(e)

def add_all():
    """Ajoute tous les fichiers au staging."""
    try:
        result = subprocess.run(
            ['git', 'add', '-A'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )
        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, ""
    except Exception as e:
        return False, str(e)

def commit(message):
    """Crée un commit avec le message donné."""
    try:
        result = subprocess.run(
            ['git', 'commit', '-m', message],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )
        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, ""
    except Exception as e:
        return False, str(e)

def create_tag(tag_name, tag_message):
    """Crée un tag annoté."""
    try:
        result = subprocess.run(
            ['git', 'tag', '-a', tag_name, '-m', tag_message],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )
        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, ""
    except Exception as e:
        return False, str(e)

def push_tag(tag_name):
    """Push un tag vers le remote."""
    try:
        result = subprocess.run(
            ['git', 'push', 'origin', tag_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )
        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, ""
    except Exception as e:
        return False, str(e)

def get_commit_history():
    """Récupère l'historique des commits."""
    try:
        result = subprocess.run(
            ['git', 'log', '--oneline'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True
        )
        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, result.stdout
    except Exception as e:
        return False, str(e)
