from __future__ import annotations

from pathlib import Path
import sqlite3
from typing import Iterable

import pandas as pd


TRANSACTIONS_PATTERN = "*Valeurs*.xlsx"
POPULATION_PATTERN = "*donnees_communes*.xlsx"
GEOGRAPHY_PATTERN = "*referentiel-geographique*.xlsx"
SCHEMA_FILENAME = "schema.sql"


def _normalize_code(value: object, width: int | None = None) -> str | None:
    if pd.isna(value):
        return None

    if isinstance(value, str):
        code = value.strip()
    else:
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            code = str(value).strip()
        else:
            if numeric_value.is_integer():
                code = str(int(numeric_value))
            else:
                code = str(numeric_value)

    if width is not None:
        code = code.zfill(width)
    return code


def _find_single_file(folder: Path, pattern: str) -> Path:
    matches = sorted(folder.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"Aucun fichier ne correspond au motif {pattern!r} dans {folder}")
    if len(matches) > 1:
        raise FileNotFoundError(
            f"Plusieurs fichiers correspondent au motif {pattern!r} dans {folder}: {matches}"
        )
    return matches[0]


def _load_workbook(folder: Path, pattern: str) -> pd.DataFrame:
    return pd.read_excel(_find_single_file(folder, pattern))


def load_source_workbooks(data_dir: Path) -> dict[str, pd.DataFrame]:
    return {
        "transactions": _load_workbook(data_dir, TRANSACTIONS_PATTERN),
        "population": _load_workbook(data_dir, POPULATION_PATTERN),
        "geography": _load_workbook(data_dir, GEOGRAPHY_PATTERN),
    }


def prepare_region_table(geography_df: pd.DataFrame) -> pd.DataFrame:
    region = (
        geography_df.loc[:, ["reg_code", "reg_nom"]]
        .dropna(subset=["reg_code", "reg_nom"])
        .drop_duplicates()
        .copy()
    )
    region["code_region"] = region["reg_code"].map(lambda value: _normalize_code(value, 2))
    region = region.rename(columns={"reg_nom": "nom_region"})
    return region.loc[:, ["code_region", "nom_region"]].drop_duplicates(subset=["code_region"])


def prepare_departement_table(geography_df: pd.DataFrame) -> pd.DataFrame:
    departement = (
        geography_df.loc[:, ["dep_code", "dep_nom", "reg_code"]]
        .dropna(subset=["dep_code", "dep_nom", "reg_code"])
        .drop_duplicates()
        .copy()
    )
    departement["code_departement"] = departement["dep_code"].map(lambda value: _normalize_code(value, 2))
    departement["code_region"] = departement["reg_code"].map(lambda value: _normalize_code(value, 2))
    departement = departement.rename(columns={"dep_nom": "nom_departement"})
    return departement.loc[:, ["code_departement", "nom_departement", "code_region"]].drop_duplicates(
        subset=["code_departement"]
    )


def prepare_commune_tables(
    transactions_df: pd.DataFrame,
    population_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    commune_source = (
        transactions_df.loc[:, ["Code departement", "Code commune", "Commune", "Code postal"]]
        .dropna(subset=["Code departement", "Code commune", "Commune"])
        .copy()
    )
    commune_source["code_departement"] = commune_source["Code departement"].map(
        lambda value: _normalize_code(value, 2)
    )
    commune_source["code_commune"] = pd.to_numeric(commune_source["Code commune"], errors="coerce").astype("Int64")
    commune_source["code_postal"] = pd.to_numeric(commune_source["Code postal"], errors="coerce").astype("Int64")
    commune_source["nom_commune"] = commune_source["Commune"]
    commune_source["id_coddep_codecommune"] = (
        commune_source["code_departement"].astype(str)
        + commune_source["code_commune"].map(lambda value: f"{int(value):03d}" if pd.notna(value) else None)
    )

    demographic_source = population_df.loc[:, ["CODDEP", "CODCOM", "PTOT"]].dropna(subset=["CODDEP", "CODCOM"])
    demographic_source = demographic_source.copy()
    demographic_source["code_departement"] = demographic_source["CODDEP"].map(lambda value: _normalize_code(value, 2))
    demographic_source["code_commune"] = pd.to_numeric(demographic_source["CODCOM"], errors="coerce").astype("Int64")
    demographic_source["population"] = pd.to_numeric(demographic_source["PTOT"], errors="coerce").astype("Int64")

    commune = commune_source.loc[
        :, ["id_coddep_codecommune", "code_departement", "code_commune", "code_postal", "nom_commune"]
    ].drop_duplicates(subset=["id_coddep_codecommune"])

    commune = commune.merge(
        demographic_source.loc[:, ["code_departement", "code_commune", "population"]],
        on=["code_departement", "code_commune"],
        how="left",
    )

    demographie = commune.loc[:, ["id_coddep_codecommune", "population"]].dropna(subset=["population"])
    demographie = demographie.drop_duplicates(subset=["id_coddep_codecommune"])
    commune = commune.loc[:, ["id_coddep_codecommune", "code_departement", "code_commune", "code_postal", "nom_commune"]]

    return commune, demographie


def _prepare_transaction_base(transactions_df: pd.DataFrame) -> pd.DataFrame:
    base = transactions_df.copy()
    base = base.dropna(subset=["Date mutation", "Code departement", "Code commune", "Commune"])
    base["date"] = pd.to_datetime(base["Date mutation"], errors="coerce").dt.strftime("%Y-%m-%d")
    base = base.dropna(subset=["date"]).reset_index(drop=True)
    base["id_bien"] = base.index + 1
    base["id_vente"] = base.index + 1
    return base


def prepare_bien_table(transactions_df: pd.DataFrame) -> pd.DataFrame:
    base = _prepare_transaction_base(transactions_df)
    bien = base.loc[
        :, 
        [
            "id_bien",
            "Code departement",
            "Code commune",
            "No voie",
            "B/T/Q",
            "Type de voie",
            "Voie",
            "Nombre pieces principales",
            "Surface Carrez du 1er lot",
            "Surface reelle bati",
            "Type local",
        ],
    ].copy()

    bien["code_departement"] = bien["Code departement"].map(lambda value: _normalize_code(value, 2))
    bien["code_commune"] = pd.to_numeric(bien["Code commune"], errors="coerce").astype("Int64")
    bien["id_coddep_codecommune"] = (
        bien["code_departement"].astype(str)
        + bien["code_commune"].map(lambda value: f"{int(value):03d}" if pd.notna(value) else None)
    )
    bien["no_voie"] = pd.to_numeric(bien["No voie"], errors="coerce").astype("Int64")
    bien["btq"] = bien["B/T/Q"]
    bien["type_voie"] = bien["Type de voie"]
    bien["voie"] = bien["Voie"]
    bien["total_piece"] = pd.to_numeric(bien["Nombre pieces principales"], errors="coerce").astype("Int64")
    bien["surface_carrez"] = pd.to_numeric(bien["Surface Carrez du 1er lot"], errors="coerce")
    bien["surface_local"] = pd.to_numeric(bien["Surface reelle bati"], errors="coerce").astype("Int64")
    bien["type_local"] = bien["Type local"]

    return bien.loc[
        :, 
        [
            "id_bien",
            "id_coddep_codecommune",
            "no_voie",
            "btq",
            "type_voie",
            "voie",
            "total_piece",
            "surface_carrez",
            "surface_local",
            "type_local",
        ],
    ].drop_duplicates(subset=["id_bien"])


def prepare_vente_table(transactions_df: pd.DataFrame) -> pd.DataFrame:
    base = _prepare_transaction_base(transactions_df)
    vente = base.loc[:, ["id_vente", "id_bien", "date", "Valeur fonciere"]].copy()
    vente["valeur"] = pd.to_numeric(vente["Valeur fonciere"], errors="coerce").round().astype("Int64")
    return vente.loc[:, ["id_vente", "id_bien", "date", "valeur"]].drop_duplicates(subset=["id_vente"])


def build_tables_from_sources(data_dir: Path) -> dict[str, pd.DataFrame]:
    sources = load_source_workbooks(data_dir)
    commune, demographie = prepare_commune_tables(sources["transactions"], sources["population"])
    return {
        "Region": prepare_region_table(sources["geography"]),
        "Departement": prepare_departement_table(sources["geography"]),
        "Commune": commune,
        "Demographie": demographie,
        "Bien": prepare_bien_table(sources["transactions"]),
        "Vente": prepare_vente_table(sources["transactions"]),
    }


def _schema_path() -> Path:
    return Path(__file__).resolve().parents[2] / "sql" / SCHEMA_FILENAME


def create_sqlite_database(database_path: Path, tables: dict[str, pd.DataFrame], schema_path: Path | None = None) -> None:
    schema_file = schema_path or _schema_path()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    if database_path.exists():
        database_path.unlink()

    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        connection.executescript(schema_file.read_text(encoding="utf-8"))
        for table_name in ["Region", "Departement", "Commune", "Demographie", "Bien", "Vente"]:
            tables[table_name].to_sql(table_name, connection, if_exists="append", index=False)


def build_project_database(data_dir: Path, database_path: Path, schema_path: Path | None = None) -> dict[str, pd.DataFrame]:
    tables = build_tables_from_sources(data_dir)
    create_sqlite_database(database_path, tables, schema_path=schema_path)
    return tables


def count_rows(connection: sqlite3.Connection, table_names: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    cursor = connection.cursor()
    for table_name in table_names:
        counts[table_name] = cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchone()[0]
    return counts
