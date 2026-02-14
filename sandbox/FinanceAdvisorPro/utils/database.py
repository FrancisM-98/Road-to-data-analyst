"""
Couche de base de données SQLite pour Finance Advisor Pro.
Gère les clients, simulations et paramètres du conseiller.
"""

import sqlite3
import json
import uuid
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

DB_PATH = Path(__file__).parent.parent / "data" / "finance_advisor.db"


@contextmanager
def get_db():
    """Context manager pour les connexions SQLite."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialise les tables de la base de données."""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS clients (
                id TEXT PRIMARY KEY,
                advisor_id TEXT NOT NULL,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                email TEXT DEFAULT '',
                telephone TEXT DEFAULT '',
                date_naissance TEXT DEFAULT '',
                age INTEGER DEFAULT 30,
                situation_familiale TEXT DEFAULT 'Célibataire',
                enfants INTEGER DEFAULT 0,
                canton TEXT DEFAULT 'Vaud (VD)',
                commune TEXT DEFAULT '',
                salaire_annuel REAL DEFAULT 0,
                capital_lpp REAL DEFAULT 0,
                capital_3a REAL DEFAULT 0,
                statut TEXT DEFAULT 'prospect',
                tags TEXT DEFAULT '[]',
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS simulations (
                id TEXT PRIMARY KEY,
                client_id TEXT NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
                advisor_id TEXT NOT NULL,
                module TEXT NOT NULL,
                nom TEXT NOT NULL,
                parametres TEXT DEFAULT '{}',
                resultats TEXT DEFAULT '{}',
                created_at TEXT NOT NULL,
                version INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS advisor_settings (
                advisor_id TEXT PRIMARY KEY,
                logo_path TEXT DEFAULT '',
                primary_color TEXT DEFAULT '#6C63FF',
                secondary_color TEXT DEFAULT '#00D4AA',
                cabinet_name TEXT DEFAULT '',
                cabinet_address TEXT DEFAULT '',
                cabinet_phone TEXT DEFAULT '',
                cabinet_email TEXT DEFAULT '',
                cabinet_website TEXT DEFAULT '',
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS email_logs (
                id TEXT PRIMARY KEY,
                client_id TEXT REFERENCES clients(id),
                advisor_id TEXT NOT NULL,
                subject TEXT NOT NULL,
                sent_at TEXT NOT NULL,
                status TEXT DEFAULT 'sent'
            );

            CREATE INDEX IF NOT EXISTS idx_clients_advisor ON clients(advisor_id);
            CREATE INDEX IF NOT EXISTS idx_clients_statut ON clients(statut);
            CREATE INDEX IF NOT EXISTS idx_simulations_client ON simulations(client_id);
            CREATE INDEX IF NOT EXISTS idx_simulations_module ON simulations(module);
        """)


# ════════════════════════════════════════════════════════════
# CLIENTS — CRUD
# ════════════════════════════════════════════════════════════

def create_client(advisor_id: str, **kwargs) -> str:
    """Crée un nouveau client. Retourne l'ID du client."""
    client_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()

    fields = {
        "id": client_id,
        "advisor_id": advisor_id,
        "nom": kwargs.get("nom", ""),
        "prenom": kwargs.get("prenom", ""),
        "email": kwargs.get("email", ""),
        "telephone": kwargs.get("telephone", ""),
        "date_naissance": kwargs.get("date_naissance", ""),
        "age": kwargs.get("age", 30),
        "situation_familiale": kwargs.get("situation_familiale", "Célibataire"),
        "enfants": kwargs.get("enfants", 0),
        "canton": kwargs.get("canton", "Vaud (VD)"),
        "commune": kwargs.get("commune", ""),
        "salaire_annuel": kwargs.get("salaire_annuel", 0),
        "capital_lpp": kwargs.get("capital_lpp", 0),
        "capital_3a": kwargs.get("capital_3a", 0),
        "statut": kwargs.get("statut", "prospect"),
        "tags": json.dumps(kwargs.get("tags", [])),
        "notes": kwargs.get("notes", ""),
        "created_at": now,
        "updated_at": now,
    }

    placeholders = ", ".join(["?"] * len(fields))
    columns = ", ".join(fields.keys())

    with get_db() as conn:
        conn.execute(
            f"INSERT INTO clients ({columns}) VALUES ({placeholders})",
            list(fields.values()),
        )

    return client_id


def get_clients(advisor_id: str, statut: str | None = None, search: str | None = None) -> list[dict]:
    """Récupère la liste des clients d'un conseiller."""
    query = "SELECT * FROM clients WHERE advisor_id = ?"
    params = [advisor_id]

    if statut and statut != "Tous":
        query += " AND statut = ?"
        params.append(statut.lower())

    if search:
        query += " AND (nom LIKE ? OR prenom LIKE ? OR email LIKE ?)"
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern, search_pattern])

    query += " ORDER BY updated_at DESC"

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
        clients = []
        for row in rows:
            client = dict(row)
            client["tags"] = json.loads(client.get("tags", "[]"))
            clients.append(client)
        return clients


def get_client(client_id: str) -> dict | None:
    """Récupère un client par son ID."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
        if row:
            client = dict(row)
            client["tags"] = json.loads(client.get("tags", "[]"))
            return client
    return None


def update_client(client_id: str, **kwargs) -> bool:
    """Met à jour un client. Retourne True si succès."""
    if "tags" in kwargs and isinstance(kwargs["tags"], list):
        kwargs["tags"] = json.dumps(kwargs["tags"])

    kwargs["updated_at"] = datetime.now().isoformat()

    set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [client_id]

    with get_db() as conn:
        result = conn.execute(
            f"UPDATE clients SET {set_clause} WHERE id = ?",
            values,
        )
        return result.rowcount > 0


def delete_client(client_id: str) -> bool:
    """Supprime un client et toutes ses simulations."""
    with get_db() as conn:
        result = conn.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        return result.rowcount > 0


def get_client_count(advisor_id: str) -> dict:
    """Retourne les statistiques des clients."""
    with get_db() as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM clients WHERE advisor_id = ?", (advisor_id,)
        ).fetchone()[0]
        prospects = conn.execute(
            "SELECT COUNT(*) FROM clients WHERE advisor_id = ? AND statut = 'prospect'",
            (advisor_id,),
        ).fetchone()[0]
        actifs = conn.execute(
            "SELECT COUNT(*) FROM clients WHERE advisor_id = ? AND statut = 'actif'",
            (advisor_id,),
        ).fetchone()[0]
        return {"total": total, "prospects": prospects, "actifs": actifs, "inactifs": total - prospects - actifs}


# ════════════════════════════════════════════════════════════
# SIMULATIONS
# ════════════════════════════════════════════════════════════

def save_simulation(
    client_id: str,
    advisor_id: str,
    module: str,
    nom: str,
    parametres: dict,
    resultats: dict,
) -> str:
    """Sauvegarde une simulation. Retourne l'ID."""
    sim_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()

    # Calculer la version (incrémentale par client+module)
    with get_db() as conn:
        max_version = conn.execute(
            "SELECT COALESCE(MAX(version), 0) FROM simulations WHERE client_id = ? AND module = ?",
            (client_id, module),
        ).fetchone()[0]

        conn.execute(
            """INSERT INTO simulations (id, client_id, advisor_id, module, nom, parametres, resultats, created_at, version)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (sim_id, client_id, advisor_id, module, nom, json.dumps(parametres), json.dumps(resultats), now, max_version + 1),
        )

    return sim_id


def get_simulations(client_id: str, module: str | None = None) -> list[dict]:
    """Récupère les simulations d'un client."""
    query = "SELECT * FROM simulations WHERE client_id = ?"
    params = [client_id]

    if module:
        query += " AND module = ?"
        params.append(module)

    query += " ORDER BY created_at DESC"

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
        simulations = []
        for row in rows:
            sim = dict(row)
            sim["parametres"] = json.loads(sim.get("parametres", "{}"))
            sim["resultats"] = json.loads(sim.get("resultats", "{}"))
            simulations.append(sim)
        return simulations


def delete_simulation(sim_id: str) -> bool:
    """Supprime une simulation."""
    with get_db() as conn:
        result = conn.execute("DELETE FROM simulations WHERE id = ?", (sim_id,))
        return result.rowcount > 0


# ════════════════════════════════════════════════════════════
# ADVISOR SETTINGS (White-label)
# ════════════════════════════════════════════════════════════

def get_advisor_settings(advisor_id: str) -> dict:
    """Récupère les paramètres d'un conseiller."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM advisor_settings WHERE advisor_id = ?", (advisor_id,)
        ).fetchone()
        if row:
            return dict(row)

    # Retourner les valeurs par défaut
    return {
        "advisor_id": advisor_id,
        "logo_path": "",
        "primary_color": "#6C63FF",
        "secondary_color": "#00D4AA",
        "cabinet_name": "",
        "cabinet_address": "",
        "cabinet_phone": "",
        "cabinet_email": "",
        "cabinet_website": "",
    }


def save_advisor_settings(advisor_id: str, **kwargs) -> bool:
    """Sauvegarde les paramètres d'un conseiller (upsert)."""
    now = datetime.now().isoformat()
    kwargs["updated_at"] = now

    with get_db() as conn:
        existing = conn.execute(
            "SELECT 1 FROM advisor_settings WHERE advisor_id = ?", (advisor_id,)
        ).fetchone()

        if existing:
            set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
            values = list(kwargs.values()) + [advisor_id]
            conn.execute(f"UPDATE advisor_settings SET {set_clause} WHERE advisor_id = ?", values)
        else:
            kwargs["advisor_id"] = advisor_id
            placeholders = ", ".join(["?"] * len(kwargs))
            columns = ", ".join(kwargs.keys())
            conn.execute(
                f"INSERT INTO advisor_settings ({columns}) VALUES ({placeholders})",
                list(kwargs.values()),
            )
    return True


# ════════════════════════════════════════════════════════════
# EMAIL LOGS
# ════════════════════════════════════════════════════════════

def log_email(client_id: str, advisor_id: str, subject: str) -> str:
    """Log un envoi d'email."""
    log_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()

    with get_db() as conn:
        conn.execute(
            "INSERT INTO email_logs (id, client_id, advisor_id, subject, sent_at) VALUES (?, ?, ?, ?, ?)",
            (log_id, client_id, advisor_id, subject, now),
        )
    return log_id
