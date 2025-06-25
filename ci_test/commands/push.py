#!/usr/bin/env python3

"""
Implémentation de la commande push pour ci_test
"""

import os
import sys
import subprocess
from ci_test.utils import docker_utils, git_utils

def execute(args):
    """Exécute la commande push."""
    if not (hasattr(args, 'force') and args.force):
        print("🔍  Vérification du dernier commit...")

        # Vérifier que HEAD existe
        if not git_utils.verify_head():
            print("🚨  Erreur: Aucun commit trouvé (HEAD invalide)")
            return 1

        # Créer un tarball du dernier commit
        print("📦  Création de l'archive du dernier commit...")
        tarball_path = os.path.join(os.getcwd(), "project.tar")
        if not git_utils.create_tarball(tarball_path):
            print("🚨  Erreur: Impossible de créer l'archive du projet")
            return 1
        # Exécuter le conteneur Docker
        print("🐳  Lancement de la vérification dans Docker...")
        success, logs = docker_utils.run_container(os.getcwd(), args.debug)


        if not success:
            print("🚨  Échec de la compilation")
            print("\nLogs de compilation:")
            print(logs)
            # Nettoyer le tarball temporaire
            os.remove(tarball_path)
            return 1

        print("✅  Compilation réussie")

        if args.debug:
            print("\nLogs de compilation:")
            print(logs)

        success, logs = docker_utils.run_container(os.getcwd(), args.debug, type='tests')

        if not success:
            print("🚨  Échec des tests")
            print("\nLogs de tests:")
            print(logs)
            # Nettoyer le tarball temporaire
            os.remove(tarball_path)
            return 1

        if args.debug:
            print("\nLogs des tests:")
            print(logs)

        print("✅  Tests réussis")

        os.remove(tarball_path)  # Nettoyer le tarball temporaire

        # Amender le commit
        print("📝  Mise à jour du commit...")
        if not git_utils.amend_commit():
            print("🚨  Erreur: Impossible d'amender le commit")
            return 1

    # Pousser les modifications
    print("🚀  Envoi des modifications...")
    push_success, push_error = git_utils.push()

    if not push_success:
        print(f"⚠️   Warn: Push impossible\n{push_error}")
        force_push = input("Tenter un Force push ? (y/N) ").lower() == 'y'

        if force_push:
            print("🔥  Force push en cours...")
            force_success, force_error = git_utils.force_push()

            if not force_success:
                print(f"🚨  Erreur lors du force push: {force_error}")
                return 1
        else:
            print("❌  Push annulé")
            return 1

    print("✅  Push réussi")
    return 0
