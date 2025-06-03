# CI Test - Utilitaire pour projets C/C++

Cet utilitaire fournit un ensemble de commandes pour faciliter le workflow de développement et d'intégration continue pour les projets C/C++.

## Installation

```bash
# Configurer git pour accepter l'automatisation
git config --global --add --bool push.autoSetupRemote true
# Installer l'utilitaire
pip install --break-system-packages -e . && docker build -t ci_image .
```

## Commandes disponibles

### `ci_test push [--debug]`

Vérifie la compilation du projet dans un environnement Docker isolé et pousse le commit.

Options:
- `--debug`: Affiche les logs détaillés même en cas de succès

Exemple:
```bash
ci_test push
```

### `ci_test clone <url>`

Clone le dépôt distant et initialise le projet.

Exemple:
```bash
ci_test clone https://github.com/user/repo.git
```

### `ci_test init`

Initialise le projet dans le répertoire de travail actuel.

Exemple:
```bash
ci_test init
```

### `ci_test mod <modName>`

Crée une nouvelle branche de module à partir de la branche `dev`.

Conditions préalables:
- L'utilisateur doit être sur la branche `dev`

Workflow:
1. Met à jour la branche `dev` locale par rapport à la référence distante
2. Crée une nouvelle branche `mod/<modName>/main`
3. Publie la branche sur le dépôt distant

Exemple:
```bash
ci_test mod auth
# Crée et publie la branche mod/auth/main
```

### `ci_test iss <issueName>`

Crée une nouvelle branche d'issue à partir de la branche module courante.

Conditions préalables:
- L'utilisateur doit être sur une branche module (`mod/*/main`)

Workflow:
1. Extrait le nom du module depuis la branche courante
2. Crée une nouvelle branche `mod/<modName>/<issueName>`
3. Publie la branche sur le dépôt distant

Exemple:
```bash
# En étant sur la branche mod/auth/main
ci_test iss login
# Crée et publie la branche mod/auth/login
```

### `ci_test finish [--debug]`

Termine la branche courante en la fusionnant dans sa branche cible.

Conditions préalables:
- L'utilisateur doit être sur une branche issue (`mod/<modName>/<issueName>`) ou module (`mod/<modName>/main`)

Workflow pour les issues:
1. Vérifie si un rebase est en cours et le continue si nécessaire
2. Met à jour la référence distante de la branche module
3. Rebase la branche issue sur la branche module si nécessaire
4. Checkout de la branche module
5. Merge fast-forward de la branche issue dans la branche module
6. Vérification du build avec `push`
7. Suppression optionnelle de la branche issue (selon configuration)

Workflow pour les modules:
1. Vérifie si un rebase est en cours et le continue si nécessaire
2. Met à jour la référence distante de la branche `dev`
3. Rebase la branche module sur la branche `dev` si nécessaire
4. Vérification du build avec `push`
5. Affiche le lien pour créer une Pull Request sur GitHub

Options:
- `--debug`: Affiche les logs détaillés du build

Gestion des conflits:
- Si un conflit survient pendant le rebase, la commande s'arrête
- L'utilisateur doit résoudre les conflits manuellement
- Après résolution, l'utilisateur relance `ci_test finish` pour continuer

Exemple:
```bash
# En étant sur une branche issue
ci_test finish
# Fusionne l'issue dans sa branche module

# En étant sur une branche module
ci_test finish
# Prépare le module pour la fusion dans dev et affiche le lien PR GitHub
```

### `ci_test config --delete=true|false` ou `ci_test config --list`

Configure les paramètres de comportement de l'utilitaire.

Options:
- `--delete=true|false`: Active ou désactive la suppression automatique des branches mergées lors de `ci_test finish`
- `--list`: Affiche la configuration actuelle

Configuration stockée dans `~/.ci_test/config.json`.

Exemples:
```bash
# Activer la suppression automatique (par défaut)
ci_test config --delete=true

# Désactiver la suppression automatique
ci_test config --delete=false

# Voir la configuration actuelle
ci_test config --list
```

### `ci_test release`

Automatise la création d'une release depuis la branche `dev` vers la branche `main` avec versioning automatique.

Conditions préalables:
- L'utilisateur doit être sur la branche `dev`
- La branche `dev` doit contenir les modifications prêtes pour la release
- Les branches `dev` et `main` doivent exister sur le dépôt distant

Workflow automatisé:
1. **Vérification**: Contrôle que l'utilisateur est sur la branche `dev`
2. **Mise à jour**: Met à jour la branche `dev` locale depuis le dépôt distant
3. **Checkout**: Bascule sur la branche `main`
4. **Versioning**: Détermine automatiquement le numéro de version suivant
5. **Nettoyage**: Nettoie le répertoire de travail et le cache git
6. **Snapshot**: Copie l'intégralité du contenu de `dev` vers `main`
7. **Commit**: Crée un commit de release avec le message standardisé
8. **Tag**: Crée un tag git avec le numéro de version
9. **Publication**: Pousse la branche `main` et le tag vers le dépôt distant
10. **Confirmation**: Affiche le résumé de la release créée

**Versioning automatique**:
- Analyse l'historique des commits de `main` pour trouver la dernière release
- Incrémente automatiquement le numéro de version majeure
- Format des versions: `X.0` (ex: `1.0`, `2.0`, `3.0`)
- Si aucune release précédente, démarre à `1.0`

**Format des commits de release**:
```
Release X.0 - snapshot of dev
```

**Format des tags**:
```
X.0
```

Exemple:
```bash
# En étant sur la branche dev avec des modifications prêtes
ci_test release
# Sortie exemple :
# 🔄  Mise à jour de la branche dev...
# 🔄  Checkout de la branche main...
# 🔍  Détermination du numéro de version...
# 📦  Préparation de la release 2.0...
# 🧹  Nettoyage du répertoire de travail...
# 📋  Copie du contenu de dev...
# ➕  Ajout des fichiers...
# 💾  Création du commit: Release 2.0 - snapshot of dev
# 🏷️  Création du tag 2.0...
# 🚀  Push de la branche main...
# 🚀  Push du tag 2.0...
# ✅  Release 2.0 créée avec succès !
# ✅  Tag: 2.0 créée avec succès 🏷️!
```

**Avantages du workflow de release**:
- **Automatisation complète**: Aucune intervention manuelle requise
- **Versioning cohérent**: Numérotation séquentielle automatique
- **Traçabilité**: Tags git pour chaque release
- **Sécurité**: Vérifications multiples avant publication
- **Reproductibilité**: Snapshot exact de l'état dev

## Principes de conception

1. **Isolation des modifications**:
   - Chaque fonctionnalité (module) et correction (issue) bénéficie de sa propre branche

2. **Historique linéaire**:
   - Adoption du workflow rebase + fast-forward pour éviter les commits de merge parasites

3. **Local-first**:
   - Avant tout push, la compilation est validée localement

4. **Simplicité et idempotence**:
   - Les commandes sont réentrantes et simples à utiliser
