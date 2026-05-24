# ImmoProjets

Projet POC de data engineering immobilier pour analyser les transactions foncières en France et préparer une base SQLite normalisée exploitable localement.

## Résumé académique

Ce projet s'inscrit dans un cadre de preuve de concept (POC) pour Laplace Immo. L'objectif est de démontrer qu'un corpus hétérogène de données immobilières peut être transformé en une base relationnelle cohérente, interrogeable et reproductible, afin de soutenir l'analyse du marché résidentiel.

La démarche mobilise les principes de modélisation relationnelle (1NF, 2NF, 3NF), de qualité de données (normalisation des formats, contrôles de cohérence), et de reproductibilité (pipeline relançable, schéma versionné, tests unitaires).

## Sommaire

1. Problématique base de données
2. Périmètre du projet
3. Arborescence du projet
4. Modèle de données choisi
5. Méthodologie d'implémentation
6. Fonctionnement des scripts
7. Utilisation des fichiers afférents
8. Mise en route
9. Validation et qualité
10. Limites et perspectives

## Problématique base de données

La difficulté principale du projet n'est pas seulement de stocker des ventes, mais de les rendre analysables sans ambiguïté dans le temps et dans l'espace.

Le besoin métier se formule ainsi:

1. suivre l'évolution des prix immobiliers;
2. comparer les territoires entre eux (commune, département, région);
3. fiabiliser la lecture des résultats pour la décision (zones porteuses, segmentation, écarts de prix).

Si tout est conservé dans une seule table "plate", on obtient rapidement des problèmes:

- redondance massive des informations géographiques;
- risque d'incohérence (orthographes et codes différents pour une même commune);
- jointures analytiques plus complexes et plus fragiles;
- difficulté à faire évoluer le modèle.

Le modèle relationnel choisi traite ces points:

- les dimensions administratives sont séparées des faits de vente;
- chaque niveau territorial a sa table dédiée;
- les liens sont explicites via clés primaires/étrangères;
- les requêtes d'analyse restent lisibles et maintenables.

En résumé: la base sert à passer d'un fichier transactionnel brut à un socle décisionnel cohérent.

## Périmètre du projet (source: Laplace immo - projet3.pdf)

Le périmètre du POC est organisé en 3 parties progressives:

1. compréhension des données et dictionnaire;
2. conception du schéma relationnel normalisé;
3. chargement des données et production des requêtes SQL avec résultats.

Le projet doit couvrir un besoin métier clair: analyser le marché immobilier français du 1er semestre 2020 pour produire des indicateurs actionnables (volumes de vente, prix moyens, prix au m2, comparaisons territoriales, évolution trimestrielle).

Les livrables attendus dans le périmètre sont:

1. un dictionnaire de données complet (format tableur);
2. un schéma relationnel normalisé et justifié;
3. une base SQLite chargée et vérifiée;
4. un document SQL avec requêtes et résultats;
5. un support de présentation qui synthétise la démarche et les conclusions.

### Périmètre inclus

- préparation des sources et dictionnaire des données;
- modélisation relationnelle normalisée;
- création et chargement d'une base SQLite;
- rédaction des requêtes SQL d'analyse et interprétation des résultats.

### Périmètre non inclus

- industrialisation cloud (orchestration type Airflow/DBT en production);
- ingestion incrémentale temps réel;
- exposition BI en production multi-utilisateur;
- gouvernance de données à l'échelle SI complet.

Exemples de questions métier couvertes par le périmètre:

1. nombre total d'appartements vendus sur le semestre;
2. ventes par région;
3. top départements au prix/m2;
4. comparaison 2 pièces vs 3 pièces;
5. communes avec le plus de transactions rapportées à la population.

## Arborescence du projet

```text
dataprojet3/
├─ data/
│  ├─ Valeurs-foncieres.xlsx
│  ├─ donnees_communes.xlsx
│  ├─ fr-esr-referentiel-geographique.xlsx
│  ├─ Bien.csv
│  ├─ Commune.csv
│  ├─ Departement.csv
│  ├─ Region.csv
│  ├─ Vente.csv
├─ modele_donnees_sql/
│  ├─ ImmoLapeyre.architect
│  ├─ immoprojet3.sqbpro
│  ├─ database/
│  │  ├─ immo_projets.db
│  │  └─ legacy/
│  └─ sql/
│     ├─ schema.sql
│     └─ legacy/
├─ documentation/
│  ├─ contexte_projet.md
│  ├─ CR_reunion.pdf
│  └─ legacy/
├─ notebooks/
│  └─ legacy/
├─ scripts/
│  └─ build_database.py
├─ src/
│  └─ immo_projets/
│     ├─ __init__.py
│     └─ pipeline.py
├─ tests/
│  ├─ conftest.py
│  └─ test_pipeline.py
├─ .gitignore
├─ requirements.txt
└─ README.md
```

## Ce que contient le dépôt

- les sources de données brutes dans `data/`
- le schéma relationnel SQLite dans `modele_donnees_sql/sql/schema.sql`
- les artefacts de modélisation dans `modele_donnees_sql/` (`.architect`, `.sqbpro`)
- le pipeline de préparation dans `src/immo_projets/pipeline.py`
- le script d'exécution dans `scripts/build_database.py`
- les tests unitaires dans `tests/`
- une note métier détaillée dans `documentation/contexte_projet.md`

Le dossier `docus/` est ignoré volontairement via `.gitignore`.

## Dossier spécial modèle de données et SQL

Tous les éléments liés au modèle de données et au SQL sont maintenant centralisés dans `modele_donnees_sql/`:

- `modele_donnees_sql/sql/schema.sql`: schéma relationnel de référence.
- `modele_donnees_sql/sql/legacy/`: anciens scripts SQL conservés pour historique.
- `modele_donnees_sql/database/immo_projets.db`: base SQLite générée.
- `modele_donnees_sql/database/legacy/`: anciennes bases de travail.
- `modele_donnees_sql/*.architect` et `modele_donnees_sql/*.sqbpro`: fichiers de modélisation.

Impact pratique:

1. Les commandes de build utilisent désormais `modele_donnees_sql/database/` pour la sortie SQLite.
2. Le script de build utilise `modele_donnees_sql/sql/schema.sql` comme schéma par défaut.
3. Les anciens chemins `sql/` et `database/` à la racine ne sont plus utilisés.

## Modèle de données choisi

Le modèle suit une logique en étoile normalisée autour de la transaction immobilière:

- Region est le niveau territorial le plus haut.
- Departement dépend de Region via code_region.
- Commune dépend de Departement via code_departement.
- Demographie stocke uniquement la population par commune pour séparer les faits démographiques de la description administrative.
- Bien représente l'actif immobilier (adresse, type, surfaces, pièces).
- Vente représente l'événement de mutation (date et valeur) et pointe vers Bien.

Pourquoi ce choix:

- il évite les redondances (nom de région/département non répété dans chaque ligne de vente);
- il simplifie les analyses multi-niveaux (commune -> département -> région);
- il garantit l'intégrité des liens grâce aux clés étrangères;
- il permet d'ajouter des dimensions futures (ex: indicateurs socio-économiques) sans casser les requêtes existantes.

Relations principales:

- Region 1 -> N Departement
- Departement 1 -> N Commune
- Commune 1 -> N Bien
- Bien 1 -> N Vente
- Commune 1 -> 1 Demographie (dans ce POC)

Exemple de parcours analytique:

1. on part de Vente pour calculer un prix moyen;
2. on joint Bien pour retrouver la commune;
3. on joint Commune puis Departement puis Region pour agrégation territoriale.

## Méthodologie d'implémentation

La méthodologie suit une logique de recherche appliquée en ingénierie des données:

1. analyse des sources et des contraintes de qualité;
2. formulation d'un schéma cible normalisé;
3. implémentation du pipeline de transformation;
4. vérification par tests unitaires et contrôles d'intégrité;
5. validation des sorties par requêtes métier.

### Principes méthodologiques retenus

- traçabilité: séparation claire entre sources, transformation, schéma et sortie;
- reproductibilité: une commande unique permet de reconstruire la base;
- explicabilité: le modèle favorise des jointures lisibles pour les analyses;
- robustesse: les règles de normalisation sont testées automatiquement.

## Fonctionnement des scripts

### Script principal

Le fichier `scripts/build_database.py` est le point d'entrée du projet.

Ce script:

1. lit les arguments CLI (`--data-dir`, `--database`, `--schema`);
2. appelle le pipeline dans `src/immo_projets/pipeline.py`;
3. reconstruit entièrement la base SQLite cible;
4. affiche les volumes de lignes par table en sortie.

Commande type:

```powershell
python .\scripts\build_database.py --database .\modele_donnees_sql\database\immo_projets.db
```

Explication détaillée de la commande:

1. python: lance l'interpréteur actif;
2. .\scripts\build_database.py: exécute le point d'entrée du pipeline;
3. --database .\modele_donnees_sql\database\immo_projets.db: indique le chemin de sortie de la base SQLite.

Ce que la commande fait concrètement:

1. lit les 3 fichiers Excel de référence dans le dossier data;
2. normalise les formats (codes géographiques, dates, valeurs numériques);
3. construit les tables Region, Departement, Commune, Demographie, Bien, Vente;
4. applique le schema SQL et charge les donnees;
5. affiche les volumes par table pour vérification.

Quand relancer la commande:

1. après modification de fichiers source dans data;
2. après changement du schéma SQL;
3. après ajustement du pipeline de transformation.

Effet important:

La base de sortie est recréée à chaque exécution. La commande est donc idempotente dans son intention (reconstruction propre), mais écrase l'ancienne base cible.

### Pipeline de transformation

Le module `src/immo_projets/pipeline.py` est découpé en fonctions métier claires:

- `load_source_workbooks`: charge les 3 classeurs sources par motifs de nom;
- `prepare_region_table`: fabrique le référentiel Region;
- `prepare_departement_table`: fabrique Departement;
- `prepare_commune_tables`: crée Commune et Demographie;
- `prepare_bien_table`: prépare les attributs des biens;
- `prepare_vente_table`: prépare les ventes (date, valeur, id_bien);
- `create_sqlite_database`: applique schema.sql et charge les tables;
- `build_project_database`: orchestre le tout.

Points de fiabilité importants:

- normalisation des codes géographiques en texte zero-padde;
- génération déterministe des ids métier (`id_bien`, `id_vente`);
- recréation complète de la base à chaque run (pas d'état cache);
- chargement dans l'ordre des dépendances de clés étrangères.

## Validation et qualité

La validation repose sur deux niveaux complémentaires:

1. validation technique
- exécution des tests unitaires sur le pipeline;
- vérification de la création de la base sans erreur;
- contrôle des volumes de lignes par table.

2. validation analytique
- exécution de requêtes métier représentatives;
- contrôle de cohérence des agrégations territoriales;
- comparaison des résultats avec les attentes du cahier des charges.

Commande recommandée pour les tests dans cet environnement:

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
pytest
```

## Comment utiliser les fichiers afférents

### Fichiers d'entrée

- `data/Valeurs-foncieres.xlsx`: source principale des ventes et des caractéristiques de biens.
- `data/donnees_communes.xlsx`: source population par commune.
- `data/fr-esr-referentiel-geographique.xlsx`: référentiel region/departement/commune.

Ces trois fichiers sont lus par le pipeline et transformés en tables SQL.

### Fichiers de transformation

- `src/immo_projets/pipeline.py`: logique métier de nettoyage, normalisation et préparation.
- `scripts/build_database.py`: commande exécutable pour créer/recréer la base.

Quand vous lancez le script, il lit les fichiers d'entrée, fabrique les tables cibles, puis écrit la base SQLite complète.

### Fichiers de structure SQL

- `modele_donnees_sql/sql/schema.sql`: définition officielle des tables et des contraintes.

Ce fichier est la référence du schéma relationnel. Si vous ajoutez une table, vous devez d'abord la déclarer ici puis adapter le pipeline.

### Fichiers de sortie

- `modele_donnees_sql/database/immo_projets.db`: base construite automatiquement.

Vous pouvez l'ouvrir avec DB Browser for SQLite, SQLiteStudio, DBeaver, ou via Python/SQL pour lancer vos requêtes.

### Fichiers de validation

- `tests/test_pipeline.py`: tests unitaires de transformation et d'insertion.

Ils servent à vérifier qu'une modification n'introduit pas de régression sur les règles de nettoyage, les identifiants, ou la création de base.

### Fichiers legacy

- `notebooks/legacy/`, `modele_donnees_sql/sql/legacy/`, `documentation/legacy/`, `modele_donnees_sql/database/legacy/`.

Ces dossiers conservent l'historique du projet (anciennes versions notebook/sql/base). Ils ne sont pas utilisés par le pipeline courant, mais utiles pour tracer l'évolution du POC.

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
python .\scripts\build_database.py --database .\modele_donnees_sql\database\immo_projets.db
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

## Limites et perspectives

### Limites du POC

- périmètre temporel centré sur les ventes 2020 disponibles;
- base locale SQLite, adaptée au prototypage mais non destinée à la montée en charge;
- transformations orientées batch complet, sans stratégie incrémentale.

### Perspectives d'évolution

1. migration vers un moteur SQL orienté production (PostgreSQL);
2. ingestion incrémentale et historisation des chargements;
3. enrichissement des dimensions (socio-économie, typologies territoriales);
4. publication d'indicateurs via tableau de bord BI.
