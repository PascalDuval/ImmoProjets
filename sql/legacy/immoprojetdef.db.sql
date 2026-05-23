BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Bien" (
	"id_bien"	INTEGER,
	"id_coddep_codecommune"	TEXT NOT NULL,
	"no_voie"	INTEGER,
	"btq"	TEXT,
	"type_voie"	TEXT,
	"voie"	TEXT,
	"total_piece"	INTEGER,
	"surface_carrez"	REAL,
	"surface_local"	INTEGER,
	"type_local"	TEXT,
	PRIMARY KEY("id_bien"),
	FOREIGN KEY("id_coddep_codecommune") REFERENCES "Commune"("id_coddep_codecommune")
);
CREATE TABLE IF NOT EXISTS "Commune" (
	"id_coddep_codecommune"	TEXT,
	"code_departement"	TEXT NOT NULL,
	"code_commune"	INTEGER NOT NULL,
	"code_postal"	INTEGER,
	"nom_commune"	TEXT NOT NULL,
	"population"	INTEGER,
	PRIMARY KEY("id_coddep_codecommune"),
	FOREIGN KEY("code_departement") REFERENCES "Departement"("code_departement")
);
CREATE TABLE IF NOT EXISTS "Departement" (
	"code_departement"	TEXT,
	"nom_departement"	TEXT NOT NULL,
	"code_region"	TEXT NOT NULL,
	PRIMARY KEY("code_departement"),
	FOREIGN KEY("code_region") REFERENCES "Region"("code_region")
);
CREATE TABLE IF NOT EXISTS "Region" (
	"code_region"	TEXT,
	"nom_region"	TEXT NOT NULL,
	PRIMARY KEY("code_region")
);
CREATE TABLE IF NOT EXISTS "Vente" (
	"id_vente"	INTEGER,
	"id_bien"	INTEGER NOT NULL,
	"date"	TEXT NOT NULL,
	"valeur"	INTEGER,
	PRIMARY KEY("id_vente"),
	FOREIGN KEY("id_bien") REFERENCES "Bien"("id_bien")
);
COMMIT;
