# CI Test - Utilitaire pour projets C/C++

Cet utilitaire fournit un ensemble de commandes pour faciliter le workflow de développement et d'intégration continue pour les projets C/C++.

## Installation

```bash
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

Workflow pour les modules:
1. Vérifie si un rebase est en cours et le continue si nécessaire
2. Met à jour la référence distante de la branche `dev`
3. Rebase la branche module sur la branche `dev` si nécessaire
4. Checkout de la branche `dev`
5. Merge fast-forward de la branche module dans la branche `dev`
6. Vérification du build avec `push`

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
# Fusionne le module dans dev
```

## Principes de conception

1. **Isolation des modifications**:
   - Chaque fonctionnalité (module) et correction (issue) bénéficie de sa propre branche

2. **Historique linéaire**:
   - Adoption du workflow rebase + fast-forward pour éviter les commits de merge parasites

3. **Local-first**:
   - Avant tout push, la compilation est validée localement

4. **Simplicité et idempotence**:
   - Les commandes sont réentrantes et simples à utiliser
