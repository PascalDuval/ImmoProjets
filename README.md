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

## Problematique base de donnees

La difficulte principale du projet n'est pas seulement de stocker des ventes, mais de les rendre analysables sans ambiguite dans le temps et dans l'espace.

Le besoin metier se formule ainsi:

1. suivre l'evolution des prix immobiliers;
2. comparer les territoires entre eux (commune, departement, region);
3. fiabiliser la lecture des resultats pour la decision (zones porteuses, segmentation, ecarts de prix).

Si tout est conserve dans une seule table "plate", on obtient rapidement des problemes:

- redondance massive des informations geographiques;
- risque d'incoherence (orthographes et codes differents pour une meme commune);
- jointures analytiques plus complexes et plus fragiles;
- difficulte a faire evoluer le modele.

Le modele relationnel choisi traite ces points:

- les dimensions administratives sont separees des faits de vente;
- chaque niveau territorial a sa table dediee;
- les liens sont explicites via cles primaires/etrangeres;
- les requetes d'analyse restent lisibles et maintenables.

En resume: la base sert a passer d'un fichier transactionnel brut a un socle decisionnel coherent.

## Perimetre du projet (source: Laplace immo - projet3.pdf)

Le perimetre du POC est organise en 3 parties progressives:

1. comprehension des donnees et dictionnaire;
2. conception du schema relationnel normalise;
3. chargement des donnees et production des requetes SQL avec resultats.

Le projet doit couvrir un besoin metier clair: analyser le marche immobilier francais du 1er semestre 2020 pour produire des indicateurs actionnables (volumes de vente, prix moyens, prix au m2, comparaisons territoriales, evolution trimestrielle).

Les livrables attendus dans le perimetre sont:

1. un dictionnaire de donnees complet (format tableur);
2. un schema relationnel normalise et justifie;
3. une base SQLite chargee et verifiee;
4. un document SQL avec requetes et resultats;
5. un support de presentation qui synthétise la demarche et les conclusions.

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

Exemples de questions metier couvertes par le perimetre:

1. nombre total d'appartements vendus sur le semestre;
2. ventes par region;
3. top departements au prix/m2;
4. comparaison 2 pieces vs 3 pieces;
5. communes avec le plus de transactions rapportees a la population.

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
│  └─ Autre/
├─ database/
│  ├─ immo_projets.db
│  └─ legacy/
├─ documentation/
│  ├─ contexte_projet.md
│  ├─ CR_reunion.pdf
│  └─ legacy/
├─ notebooks/
│  └─ legacy/
├─ scripts/
│  └─ build_database.py
├─ sql/
│  ├─ schema.sql
│  └─ legacy/
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

## Ce que contient le depot

- les sources de données brutes dans `data/`
- le schéma relationnel SQLite dans `sql/schema.sql`
- le pipeline de préparation dans `src/immo_projets/pipeline.py`
- le script d'exécution dans `scripts/build_database.py`
- les tests unitaires dans `tests/`
- une note métier détaillée dans `documentation/contexte_projet.md`

Le dossier `docus/` est ignoré volontairement via `.gitignore`.

## Modele de donnees choisi

Le modele suit une logique en etoile normalisee autour de la transaction immobiliere:

- Region est le niveau territorial le plus haut.
- Departement depend de Region via code_region.
- Commune depend de Departement via code_departement.
- Demographie stocke uniquement la population par commune pour separer les faits demographiques de la description administrative.
- Bien represente l'actif immobilier (adresse, type, surfaces, pieces).
- Vente represente l'evenement de mutation (date et valeur) et pointe vers Bien.

Pourquoi ce choix:

- il evite les redondances (nom de region/departement non repete dans chaque ligne de vente);
- il simplifie les analyses multi-niveaux (commune -> departement -> region);
- il garantit l'integrite des liens grace aux cles etrangeres;
- il permet d'ajouter des dimensions futures (ex: indicateurs socio-economiques) sans casser les requetes existantes.

Relations principales:

- Region 1 -> N Departement
- Departement 1 -> N Commune
- Commune 1 -> N Bien
- Bien 1 -> N Vente
- Commune 1 -> 1 Demographie (dans ce POC)

Exemple de parcours analytique:

1. on part de Vente pour calculer un prix moyen;
2. on joint Bien pour retrouver la commune;
3. on joint Commune puis Departement puis Region pour agregation territoriale.

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

Le fichier `scripts/build_database.py` est le point d'entree du projet.

Ce script:

1. lit les arguments CLI (`--data-dir`, `--database`, `--schema`);
2. appelle le pipeline dans `src/immo_projets/pipeline.py`;
3. reconstruit entierement la base SQLite cible;
4. affiche les volumes de lignes par table en sortie.

Commande type:

```powershell
python .\scripts\build_database.py --database .\database\immo_projets.db
```

Explication detaillee de la commande:

1. python: lance l'interpreteur actif;
2. .\scripts\build_database.py: execute le point d'entree du pipeline;
3. --database .\database\immo_projets.db: indique le chemin de sortie de la base SQLite.

Ce que la commande fait concretement:

1. lit les 3 fichiers Excel de reference dans le dossier data;
2. normalise les formats (codes geographiques, dates, valeurs numeriques);
3. construit les tables Region, Departement, Commune, Demographie, Bien, Vente;
4. applique le schema SQL et charge les donnees;
5. affiche les volumes par table pour verification.

Quand relancer la commande:

1. apres modification de fichiers source dans data;
2. apres changement du schema SQL;
3. apres ajustement du pipeline de transformation.

Effet important:

La base de sortie est recreee a chaque execution. La commande est donc idempotente dans son intention (reconstruction propre), mais ecrase l'ancienne base cible.

### Pipeline de transformation

Le module `src/immo_projets/pipeline.py` est decoupe en fonctions metier claires:

- `load_source_workbooks`: charge les 3 classeurs sources par motifs de nom;
- `prepare_region_table`: fabrique le referentiel Region;
- `prepare_departement_table`: fabrique Departement;
- `prepare_commune_tables`: cree Commune et Demographie;
- `prepare_bien_table`: prepare les attributs des biens;
- `prepare_vente_table`: prepare les ventes (date, valeur, id_bien);
- `create_sqlite_database`: applique schema.sql et charge les tables;
- `build_project_database`: orchestre le tout.

Points de fiabilite importants:

- normalisation des codes geographiques en texte zero-padde;
- generation deterministe des ids metier (`id_bien`, `id_vente`);
- recreation complete de la base a chaque run (pas d'etat cache);
- chargement dans l'ordre des dependances de cles etrangeres.

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

## Comment utiliser les fichiers afferents

### Fichiers d'entree

- `data/Valeurs-foncieres.xlsx`: source principale des ventes et des caracteristiques de biens.
- `data/donnees_communes.xlsx`: source population par commune.
- `data/fr-esr-referentiel-geographique.xlsx`: referentiel region/departement/commune.

Ces trois fichiers sont lus par le pipeline et transformes en tables SQL.

### Fichiers de transformation

- `src/immo_projets/pipeline.py`: logique metier de nettoyage, normalisation et preparation.
- `scripts/build_database.py`: commande executable pour creer/recreer la base.

Quand vous lancez le script, il lit les fichiers d'entree, fabrique les tables cibles, puis ecrit la base SQLite complete.

### Fichiers de structure SQL

- `sql/schema.sql`: definition officielle des tables et des contraintes.

Ce fichier est la reference du schema relationnel. Si vous ajoutez une table, vous devez d'abord la declarer ici puis adapter le pipeline.

### Fichiers de sortie

- `database/immo_projets.db`: base construite automatiquement.

Vous pouvez l'ouvrir avec DB Browser for SQLite, SQLiteStudio, DBeaver, ou via Python/SQL pour lancer vos requetes.

### Fichiers de validation

- `tests/test_pipeline.py`: tests unitaires de transformation et d'insertion.

Ils servent a verifier qu'une modification n'introduit pas de regression sur les regles de nettoyage, les identifiants, ou la creation de base.

### Fichiers legacy

- `notebooks/legacy/`, `sql/legacy/`, `documentation/legacy/`, `database/legacy/`.

Ces dossiers conservent l'historique du projet (anciennes versions notebook/sql/base). Ils ne sont pas utilises par le pipeline courant, mais utiles pour tracer l'evolution du POC.

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

Le script lit automatiquement les classeurs Excel presents dans `data/`, prepare les tables `Region`, `Departement`, `Commune`, `Demographie`, `Bien` et `Vente`, puis genere une base SQLite complete.

4. Lancer les tests.

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
pytest
```

Si votre environnement charge un plugin pytest externe cassé, gardez la variable `PYTEST_DISABLE_PLUGIN_AUTOLOAD` avant le lancement des tests.

## Choix techniques

- Les identifiants metier sont stabilises avant insertion: `id_bien` et `id_vente` suivent l'ordre des lignes nettoyees du jeu de transactions.
- La population est isolee dans `Demographie` pour garder un schema normalise et eviter de melanger geographie et demographie.
- Le chargement SQLite est rejouable: la base est recreee a chaque execution du script.
- Les noms de fichiers Excel sont detectes par motif, ce qui evite de dependre des accents dans les chemins.

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
