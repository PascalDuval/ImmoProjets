-- =========================================
-- TABLE : Region
-- =========================================
CREATE TABLE Region (
    code_region TEXT PRIMARY KEY,
    nom_region TEXT NOT NULL
);

-- =========================================
-- TABLE : Departement
-- =========================================
CREATE TABLE Departement (
    code_departement TEXT PRIMARY KEY,
    nom_departement TEXT NOT NULL,
    code_region TEXT NOT NULL,
    FOREIGN KEY (code_region) REFERENCES Region(code_region)
);

-- =========================================
-- TABLE : Commune
-- =========================================
CREATE TABLE Commune (
    id_coddep_codecommune TEXT PRIMARY KEY,  -- ex: '75056'
    code_departement TEXT NOT NULL,
    code_commune INTEGER NOT NULL,
    code_postal INTEGER,
    nom_commune TEXT NOT NULL,
    FOREIGN KEY (code_departement) REFERENCES Departement(code_departement)
);

-- =========================================
-- TABLE : Demographie
-- =========================================
CREATE TABLE Demographie (
    id_coddep_codecommune TEXT PRIMARY KEY,
    population INTEGER NOT NULL,
    FOREIGN KEY (id_coddep_codecommune) REFERENCES Commune(id_coddep_codecommune)
);

-- =========================================
-- TABLE : Bien
-- =========================================
CREATE TABLE Bien (
    id_bien INTEGER PRIMARY KEY,
    id_coddep_codecommune TEXT NOT NULL,
    no_voie INTEGER,
    btq TEXT,
    type_voie TEXT,
    voie TEXT,
    total_piece INTEGER,
    surface_carrez REAL,
    surface_local INTEGER,
    type_local TEXT,
    FOREIGN KEY (id_coddep_codecommune) REFERENCES Commune(id_coddep_codecommune)
);

-- =========================================
-- TABLE : Vente
-- =========================================
CREATE TABLE Vente (
    id_vente INTEGER PRIMARY KEY,
    id_bien INTEGER NOT NULL,
    date TEXT NOT NULL, -- format : YYYY-MM-DD
    valeur INTEGER,
    FOREIGN KEY (id_bien) REFERENCES Bien(id_bien)
);
