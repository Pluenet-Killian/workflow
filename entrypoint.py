#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
import tarfile
import logging
import re

def setup_logging(verbose):
    """Configure le système de logging selon le niveau de verbosité."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger('ci_entrypoint')

def parse_arguments():
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(description='CI Test Docker Entrypoint')
    parser.add_argument('type', type=str, choices=['build', 'tests'], default='build',
                        help='Type d\'opération à effectuer: build ou tests')
    parser.add_argument('--verbose', type=bool, default=False,
                        help='Mode verbeux pour afficher tous les logs')
    parser.add_argument('--workdir', type=str, default='/workspace',
                        help='Répertoire de travail pour l\'extraction et la compilation')

    # Structure extensible pour ajouter facilement d'autres arguments à l'avenir
    return parser.parse_args()

def extract_tarball(input_path, output_path, logger):
    """Extrait le tarball Git vers le répertoire de travail."""
    logger.info(f"Extraction du tarball {input_path} vers {output_path}")
    try:
        with tarfile.open(input_path) as t:
            t.extractall(output_path)
        logger.debug("Extraction réussie")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction: {e}")
        return False

def get_binary_names_from_makefile(workdir, logger):
    """Extrait les noms des binaires depuis le Makefile."""
    logger.info("Recherche des noms de binaires dans le Makefile")
    makefile_path = os.path.join(workdir, "Makefile")

    if not os.path.exists(makefile_path):
        logger.error("Makefile introuvable")
        return None

    try:
        with open(makefile_path, 'r') as f:
            makefile_content = f.read()

        # Recherche de la variable NAME dans le Makefile (support pour plusieurs binaires)
        match = re.search(r'NAME\s*=\s*(.+)', makefile_content)
        if match:
            binary_names_str = match.group(1).strip()
            # Diviser la chaîne par les espaces pour obtenir plusieurs noms
            binary_names = binary_names_str.split()
            if binary_names:
                logger.info(f"Nom(s) de binaire(s) trouvé(s): {', '.join(binary_names)}")
                return binary_names
            else:
                logger.error("Variable NAME vide dans le Makefile")
                return None
        else:
            logger.error("Variable NAME non trouvée dans le Makefile")
            return None
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du Makefile: {e}")
        return None

def run_build(workdir, verbose, logger):
    """Exécute la commande de build dans le répertoire de travail."""
    logger.info("Lancement de la compilation (make re)")

    cmd = ['make', 're']
    # Ne jamais utiliser --quiet, même en mode non-verbose
    # pour pouvoir afficher les sorties complètes en cas d'échec

    try:
        if verbose:
            # En mode verbose, afficher tous les logs en temps réel
            ret = subprocess.call(cmd, cwd=workdir)
        else:
            # En mode non-verbose, capturer les logs pour les afficher uniquement en cas d'erreur
            # mais ne pas utiliser --quiet pour avoir les sorties complètes
            process = subprocess.Popen(
                cmd,
                cwd=workdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            stdout, stderr = process.communicate()
            ret = process.returncode

            if ret != 0:
                logger.error("Échec de la compilation")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")

        if ret != 0:
            return ret, None

        # Vérifier que les binaires ont bien été créés
        binary_names = get_binary_names_from_makefile(workdir, logger)
        if not binary_names:
            logger.error("Impossible de déterminer les noms des binaires")
            return 1, None

        missing_binaries = []
        for binary_name in binary_names:
            binary_path = os.path.join(workdir, binary_name)
            if not os.path.exists(binary_path):
                missing_binaries.append(binary_name)

        if missing_binaries:
            logger.error(f"Les binaires suivants n'ont pas été créés: {', '.join(missing_binaries)}")
            return 1, None

        logger.info(f"Binaire(s) {', '.join(binary_names)} créé(s) avec succès")
        return 0, binary_names
    except Exception as e:
        logger.error(f"Erreur lors de la compilation: {e}")
        return 1, None

def run_tests(workdir, verbose, logger):
    """Exécute les tests dans le répertoire de travail."""
    logger.info("Lancement des tests (make tests_run)")
    cmd = ['make', 'tests_run']
    # Ne jamais utiliser --quiet, même en mode non-verbose
    try:
        if verbose:
            # En mode verbose, afficher tous les logs en temps réel
            ret = subprocess.call(cmd, cwd=workdir)
        else:
            # En mode non-verbose, capturer les logs pour les afficher uniquement en cas d'erreur
            process = subprocess.Popen(
                cmd,
                cwd=workdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            stdout, stderr = process.communicate()
            ret = process.returncode

            if ret != 0:
                logger.error("Échec des tests")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")

        return ret
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution des tests: {e}")
        return 1

def run_clean(workdir, verbose, logger):
    """Exécute la commande make fclean dans le répertoire de travail."""
    logger.info("Nettoyage du projet (make fclean)")

    cmd = ['make', 'fclean']
    # Ne jamais utiliser --quiet, même en mode non-verbose

    try:
        if verbose:
            # En mode verbose, afficher tous les logs en temps réel
            ret = subprocess.call(cmd, cwd=workdir)
        else:
            # En mode non-verbose, capturer les logs pour les afficher uniquement en cas d'erreur
            process = subprocess.Popen(
                cmd,
                cwd=workdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            stdout, stderr = process.communicate()
            ret = process.returncode

            if ret != 0:
                logger.error("Échec du nettoyage")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")

        return ret
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage: {e}")
        return 1

def main():
    """Fonction principale du script."""
    args = parse_arguments()
    logger = setup_logging(args.verbose)

    logger.info("Démarrage du processus CI")
    # Extraction du tarball
    if not extract_tarball('/mnt/project.tar', args.workdir, logger):
        return 1

    if args.type == 'build':
        # Exécution de la compilation
        build_result, binary_names = run_build(args.workdir, args.verbose, logger)

        if build_result != 0:
            logger.error("La compilation a échoué")
            return build_result

        if len(binary_names) == 1:
            logger.info(f"Compilation réussie, binaire '{binary_names[0]}' créé")
        else:
            logger.info(f"Compilation réussie, binaires '{', '.join(binary_names)}' créés")

    elif args.type == 'tests':
        # Exécution des tests
        tests_result = run_tests(args.workdir, args.verbose, logger)
        if tests_result != 0:
            logger.error("Les tests ont échoué")
            return tests_result

        logger.info("Tous les tests ont réussi")

    # Exécution du nettoyage
    clean_result = run_clean(args.workdir, args.verbose, logger)

    if clean_result != 0:
        logger.warning("Le nettoyage a échoué, mais la compilation a réussi")
        # On ne fait pas échouer le processus si seul le nettoyage échoue

    return 0

if __name__ == "__main__":
    sys.exit(main())
