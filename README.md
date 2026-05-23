# ImmoProjets

Projet POC de data engineering immobilier pour analyser les transactions foncières en France et préparer une base SQLite normalisée exploitable localement.

## Ce que contient le dépôt

- les sources de données brutes dans `data/`
- le schéma relationnel SQLite dans `sql/schema.sql`
- le pipeline de préparation dans `src/immo_projets/pipeline.py`
- le script d'exécution dans `scripts/build_database.py`
- les tests unitaires dans `tests/`
- une note métier détaillée dans `documentation/contexte_projet.md`

Le dossier `docus/` est ignoré volontairement via `.gitignore`.

## Mise en route

1. Créer un environnement isolé.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Installer les dépendances.

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. Construire la base SQLite.

```powershell
python .\scripts\build_database.py --database .\database\immo_projets.db
```

Le script lit automatiquement les classeurs Excel présents dans `data/`, prépare les tables `Region`, `Departement`, `Commune`, `Demographie`, `Bien` et `Vente`, puis génère une base SQLite complète.

4. Lancer les tests.

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
pytest
```

Si votre environnement charge un plugin pytest externe cassé, gardez la variable `PYTEST_DISABLE_PLUGIN_AUTOLOAD` avant le lancement des tests.

## Choix techniques

- Les identifiants métier sont stabilisés avant insertion: `id_bien` et `id_vente` suivent l'ordre des lignes nettoyées du jeu de transactions.
- La population est isolée dans `Demographie` pour garder un schéma normalisé et éviter de mélanger géographie et démographie.
- Le chargement SQLite est rejouable: la base est recréée à chaque exécution du script.
- Les noms de fichiers Excel sont détectés par motif, ce qui évite de dépendre des accents dans les chemins.
