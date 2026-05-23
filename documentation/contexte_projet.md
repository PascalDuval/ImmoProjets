# Contexte du projet

Laplace Immo souhaite industrialiser l'exploitation des transactions immobilières françaises afin de suivre l'évolution des prix au mètre carré, d'identifier les zones les plus dynamiques et d'appuyer les futures décisions commerciales avec une base fiable.

Le projet est pensé comme un POC: il doit prouver la faisabilité du modèle de données, de la transformation et du chargement dans une base exploitable avant un passage à l'échelle.

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

## Comment lancer le projet

Le README détaille l'installation locale, le lancement du script de build et l'exécution des tests. Le résultat attendu est un fichier SQLite reproductible, prêt pour les analyses SQL et les captures de présentation.
