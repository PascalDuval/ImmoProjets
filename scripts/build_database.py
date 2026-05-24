from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from immo_projets.pipeline import build_project_database  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Construit la base SQLite du POC immobilier.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=PROJECT_ROOT / "data",
        help="Répertoire contenant les fichiers Excel sources.",
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=PROJECT_ROOT / "modele_donnees_sql" / "database" / "immo_projets.db",
        help="Chemin du fichier SQLite à générer.",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=PROJECT_ROOT / "modele_donnees_sql" / "sql" / "schema.sql",
        help="Chemin du schéma SQL à appliquer.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tables = build_project_database(args.data_dir, args.database, schema_path=args.schema)
    table_names = ["Region", "Departement", "Commune", "Demographie", "Bien", "Vente"]

    print(f"Base SQLite créée : {args.database}")
    for table_name in table_names:
        print(f"- {table_name}: {len(tables[table_name])} lignes")


if __name__ == "__main__":
    main()
