from pathlib import Path
import sqlite3

import pandas as pd

from immo_projets.pipeline import (
    build_tables_from_sources,
    create_sqlite_database,
    prepare_bien_table,
    prepare_commune_tables,
    prepare_departement_table,
    prepare_region_table,
    prepare_vente_table,
)


def test_prepare_region_and_departement_tables():
    geography = pd.DataFrame(
        [
            {"reg_code": 84, "reg_nom": "Auvergne-Rhône-Alpes", "dep_code": 1, "dep_nom": "Ain"},
            {"reg_code": 84, "reg_nom": "Auvergne-Rhône-Alpes", "dep_code": 2, "dep_nom": "Aisne"},
        ]
    )

    region = prepare_region_table(geography)
    departement = prepare_departement_table(geography)

    assert region.to_dict(orient="records") == [{"code_region": "84", "nom_region": "Auvergne-Rhône-Alpes"}]
    assert departement["code_departement"].tolist() == ["01", "02"]
    assert departement["code_region"].tolist() == ["84", "84"]


def test_prepare_commune_and_demographie_tables():
    transactions = pd.DataFrame(
        [
            {
                "Code departement": "01",
                "Code commune": 103,
                "Commune": "CHEVRY",
                "Code postal": 1170,
                "Date mutation": "2020-01-02",
                "Valeur fonciere": 165000,
                "No voie": 347,
                "B/T/Q": None,
                "Type de voie": "RUE",
                "Voie": "DU CHATEAU",
                "Nombre pieces principales": 3,
                "Surface Carrez du 1er lot": 48.22,
                "Surface reelle bati": 48,
                "Type local": "Appartement",
            }
        ]
    )
    population = pd.DataFrame(
        [
            {"CODDEP": "01", "CODCOM": 103, "PTOT": 2196},
        ]
    )

    commune, demographie = prepare_commune_tables(transactions, population)

    assert commune.to_dict(orient="records") == [
        {
            "id_coddep_codecommune": "01103",
            "code_departement": "01",
            "code_commune": 103,
            "code_postal": 1170,
            "nom_commune": "CHEVRY",
        }
    ]
    assert demographie.to_dict(orient="records") == [
        {"id_coddep_codecommune": "01103", "population": 2196}
    ]


def test_prepare_bien_and_vente_share_same_ids():
    transactions = pd.DataFrame(
        [
            {
                "Code departement": "01",
                "Code commune": 103,
                "Commune": "CHEVRY",
                "Code postal": 1170,
                "Date mutation": "2020-01-02",
                "Valeur fonciere": 165000,
                "No voie": 347,
                "B/T/Q": None,
                "Type de voie": "RUE",
                "Voie": "DU CHATEAU",
                "Nombre pieces principales": 3,
                "Surface Carrez du 1er lot": 48.22,
                "Surface reelle bati": 48,
                "Type local": "Appartement",
            },
            {
                "Code departement": "06",
                "Code commune": 4,
                "Commune": "ANTIBES",
                "Code postal": 6160,
                "Date mutation": "2020-01-02",
                "Valeur fonciere": 355680,
                "No voie": 4,
                "B/T/Q": None,
                "Type de voie": "BD",
                "Voie": "EDOUARD BAUDOIN",
                "Nombre pieces principales": 1,
                "Surface Carrez du 1er lot": 39.11,
                "Surface reelle bati": 40,
                "Type local": "Appartement",
            },
        ]
    )

    bien = prepare_bien_table(transactions)
    vente = prepare_vente_table(transactions)

    assert bien["id_bien"].tolist() == [1, 2]
    assert bien["id_coddep_codecommune"].tolist() == ["01103", "06004"]
    assert vente["id_vente"].tolist() == [1, 2]
    assert vente["id_bien"].tolist() == [1, 2]
    assert vente["date"].tolist() == ["2020-01-02", "2020-01-02"]


def test_create_sqlite_database_roundtrip(tmp_path: Path):
    tables = {
        "Region": pd.DataFrame([{"code_region": "84", "nom_region": "Auvergne-Rhône-Alpes"}]),
        "Departement": pd.DataFrame(
            [{"code_departement": "01", "nom_departement": "Ain", "code_region": "84"}]
        ),
        "Commune": pd.DataFrame(
            [
                {
                    "id_coddep_codecommune": "01103",
                    "code_departement": "01",
                    "code_commune": 103,
                    "code_postal": 1170,
                    "nom_commune": "CHEVRY",
                }
            ]
        ),
        "Demographie": pd.DataFrame([{"id_coddep_codecommune": "01103", "population": 2196}]),
        "Bien": pd.DataFrame(
            [
                {
                    "id_bien": 1,
                    "id_coddep_codecommune": "01103",
                    "no_voie": 347,
                    "btq": None,
                    "type_voie": "RUE",
                    "voie": "DU CHATEAU",
                    "total_piece": 3,
                    "surface_carrez": 48.22,
                    "surface_local": 48,
                    "type_local": "Appartement",
                }
            ]
        ),
        "Vente": pd.DataFrame([{"id_vente": 1, "id_bien": 1, "date": "2020-01-02", "valeur": 165000}]),
    }

    database_path = tmp_path / "immo.db"
    schema_path = Path(__file__).resolve().parents[1] / "modele_donnees_sql" / "sql" / "schema.sql"
    create_sqlite_database(database_path, tables, schema_path=schema_path)

    with sqlite3.connect(database_path) as connection:
        counts = {
            table: connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            for table in tables
        }

    assert counts == {name: 1 for name in tables}
