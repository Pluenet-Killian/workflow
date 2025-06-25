#!/usr/bin/env python3

"""
Interface CLI principale pour ci_test
"""

import argparse
import os
import sys
from ci_test.commands import push, clone_init, module, issue, finish, config, release, update


def main():
    """Point d'entrée principal de l'application CLI."""
    parser = argparse.ArgumentParser(
        description='Utilitaire CI pour projets C/C++',
        prog='ci_test'
    )
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')

    # Configuration du parseur pour la commande push
    push_parser = subparsers.add_parser('push', help='Vérifie la compilation et pousse le commit')
    push_parser.add_argument('--debug', action='store_true', help='Mode debug avec logs détaillés')
    push_parser.add_argument('--force', action='store_true', help='Ne lance pas les vérifications dans Docker')
    push_parser.set_defaults(func=push.execute)

    # Configuration du parseur pour la commande clone/init
    clone_parser = subparsers.add_parser('clone', help='Clone le dépôt et initialise le projet')
    clone_parser.add_argument('url', help='URL du dépôt à cloner')
    init_parser = subparsers.add_parser('init', help='Initialise le projet dans le répertoire de travail')
    clone_parser.set_defaults(func=clone_init.execute)
    init_parser.set_defaults(func=clone_init.execute)


    # Configuration du parseur pour la commande module
    module_parser = subparsers.add_parser('mod', help='Crée une nouvelle branche de module', aliases=['module'])
    module_parser.add_argument('name', help='Nom du module à créer')
    module_parser.set_defaults(func=module.execute)

    # Configuration du parseur pour la commande issue
    issue_parser = subparsers.add_parser('iss', help='Crée une nouvelle branche d\'issue', aliases=['issue'])
    issue_parser.add_argument('name', help='Nom de l\'issue à créer')
    issue_parser.set_defaults(func=issue.execute)

    # Configuration du parseur pour la commande finish
    finish_parser = subparsers.add_parser('finish', help='Termine la branche courante')
    finish_parser.add_argument('--debug', action='store_true', help='Mode debug avec logs détaillés')
    finish_parser.add_argument('--force', action='store_true', help='Ne lance pas les vérifications dans Docker')
    finish_parser.set_defaults(func=finish.execute)

    # Configuration du parseur pour la commande config
    config_parser = subparsers.add_parser('config', help='Configure les paramètres de ci_test')
    config_group = config_parser.add_mutually_exclusive_group(required=True)
    config_group.add_argument('--delete', type=str, choices=['true', 'false'],
                             help='Active/désactive la suppression automatique des branches mergées')
    config_group.add_argument('--list', action='store_true',
                             help='Affiche la configuration actuelle')
    config_parser.set_defaults(func=config.execute)

    # Configuration du parseur pour la commande release
    release_parser = subparsers.add_parser('release', help='Crée une release depuis dev vers main')
    release_parser.set_defaults(func=release.execute)

    # Configuration du parseur pour la commande update
    update_parser = subparsers.add_parser('update', help='Met à jour la branche courante par rebase')
    update_parser.add_argument('dev', nargs='?', default=None, help='Branche cible pour le rebase d\'une issue (dev)')
    update_parser.add_argument('--debug', action='store_true', help='Mode debug avec logs détaillés')
    update_parser.add_argument('--force', action='store_true', help='Ne lance pas les vérifications dans Docker')
    update_parser.set_defaults(func=update.execute)

    args = parser.parse_args()


    if args.command is None:
        parser.print_help()
        return 1

    if not hasattr(args, 'func'):
        print(f"🚨  Erreur: La commande {args.command} n'est pas encore implémentée")
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
