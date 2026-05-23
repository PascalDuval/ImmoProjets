# Contexte du projet

Laplace Immo souhaite industrialiser l'exploitation des transactions immobilières françaises afin de suivre l'évolution des prix au mètre carré, d'identifier les zones les plus dynamiques et d'appuyer les futures décisions commerciales avec une base fiable.

Le projet est pensé comme un POC: il doit prouver la faisabilité du modèle de données, de la transformation et du chargement dans une base exploitable avant un passage à l'échelle.

## Problématique base de données

Le besoin ne se limite pas à "stocker" des transactions immobilières. L'enjeu est de construire une base qui permette des analyses fiables, comparables et rejouables.

Les difficultés principales sont:

- la dispersion des informations dans plusieurs fichiers hétérogènes;
- la qualité variable des types de données (codes, dates, valeurs);
- la nécessité de relier correctement chaque vente à son territoire;
- la conservation d'un modèle qui reste lisible pour les analyses SQL métier.

La réponse apportée par ce POC est un schéma relationnel normalisé avec des clés explicites, une chaîne de transformation reproductible et des contrôles unitaires. Ce triptyque garantit que le résultat final (la base SQLite) est utilisable pour la décision et pas seulement pour l'archivage.

## Données sources

- `Valeurs-foncières.xlsx` fournit les transactions, les adresses, la valeur foncière et les caractéristiques principales du bien.
- `donnees_communes.xlsx` apporte la population communale.
- `fr-esr-referentiel-geographique.xlsx` apporte les correspondances région / département / commune.

## Modèle de données

Le schéma retenu sépare les responsabilités de chaque entité:

- `Region` contient le référentiel régional.
- `Departement` rattache chaque département à sa région.
- `Commune` décrit l'identité géographique d'une commune.
- `Demographie` isole la population afin de respecter la normalisation.
- `Bien` porte les caractéristiques physiques du bien immobilier.
- `Vente` stocke la transaction: date et valeur de vente.

Cette structure permet de remonter proprement des requêtes analytiques du type: prix moyen par région, volume de ventes par commune, ou comparaison entre appartements et maisons.

### Lecture fonctionnelle du modèle

Le modèle peut se lire comme une chaîne logique métier:

1. une vente concerne un bien;
2. un bien est situé dans une commune;
3. une commune appartient à un département;
4. un département appartient à une région;
5. une commune est associée à un indicateur de population.

Cette décomposition permet de séparer clairement:

- les dimensions géographiques (région, département, commune);
- les faits immobiliers (bien, vente);
- les attributs démographiques (population).

En pratique, cela facilite la maintenance du pipeline: un changement de référentiel géographique n'oblige pas à modifier la logique transactionnelle, et inversement.

## Exemples de résultats

Les requêtes de contrôle sur la base chargée donnent des résultats exploitables pour une première présentation métier:

- Île-de-France: 15 054 ventes, prix moyen observé autour de 372 166 €.
- Provence-Alpes-Côte d'Azur: 3 929 ventes, prix moyen observé autour de 192 831 €.
- Auvergne-Rhône-Alpes: 3 485 ventes, prix moyen observé autour de 195 821 €.
- Paris 07: 135 ventes, prix moyen observé autour de 1 251 288 €.
- Paris 16: 394 ventes, prix moyen observé autour de 1 028 244 €.

Ces résultats illustrent immédiatement la différence entre territoires tendus et territoires plus accessibles, ce qui répond à l'objectif du POC.

## Implémentation

Le pipeline suit quatre étapes:

1. lecture des classeurs sources;
2. normalisation des codes géographiques et des types de colonnes;
3. création des tables relationnelles;
4. chargement dans SQLite avec contrainte de clés étrangères.

Les identifiants `id_bien` et `id_vente` sont générés de manière déterministe à partir de l'ordre des lignes nettoyées. La table des ventes n'est donc pas reconstruite à partir d'un ordre d'insertion fragile dans la base.

### Fonctionnement détaillé du traitement

Le traitement suit une orchestration simple et reproductible:

1. chargement des fichiers sources (transactions, population, référentiel géographique);
2. nettoyage des types (dates, numériques, codes géographiques);
3. fabrication des clés métier;
4. construction des tables cibles table par table;
5. recréation complète de la base SQLite;
6. insertion dans l'ordre compatible avec les contraintes relationnelles.

Ce choix rend le POC robuste pour une démonstration: le résultat peut être régénéré à l'identique en une commande, et les tests unitaires couvrent les points critiques (cohérence des identifiants, structure des tables, insertion en base).

## Comment lancer le projet

Le README détaille l'installation locale, le lancement du script de build et l'exécution des tests. Le résultat attendu est un fichier SQLite reproductible, prêt pour les analyses SQL et les captures de présentation.

### Commande principale et interpretation

Commande:

```powershell
python .\scripts\build_database.py --database .\database\immo_projets.db
```

Interpretation:

1. le script reconstruit la base complete a partir des sources du dossier data;
2. il applique le schema relationnel du projet;
3. il prepare la base pour la partie SQL (extraction des indicateurs demandes par Laplace Immo).

Cette commande est le pivot du perimetre technique: elle relie la partie modelisation (schema), la partie donnees (sources), et la partie exploitation (requetes SQL et resultats).
