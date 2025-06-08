import sqlite3
import json
from datetime import datetime
from pathlib import Path
import os
from typing import Optional


class SqliteDB_Agent:
    def __init__(self, db_folder, db_name):
        db_name = db_name + ".db" if not db_name.endswith(".db") else db_name
        self.db_path = os.path.join(db_folder, db_name)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def __repr__(self):
        return f"<SqliteDB path='{self.db_path}'>"

    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def create_table(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    symptoms TEXT,
                    ehr_text TEXT,
                    medications TEXT,
                    question TEXT,
                    patient_profile TEXT,
                    final_state TEXT
                )
            """
            )
            conn.commit()

    def save_run(self, initial_state: dict, final_state: dict):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO runs (timestamp, symptoms, ehr_text, medications, question, patient_profile, final_state)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    datetime.utcnow().isoformat(),
                    initial_state.get("symptoms"),
                    initial_state.get("ehr_text"),
                    json.dumps(initial_state.get("medications")),
                    initial_state.get("question"),
                    json.dumps(initial_state.get("patient_profile")),
                    json.dumps(final_state),
                ),
            )
            conn.commit()

    def get_all_runs(self) -> list[dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM runs ORDER BY id DESC")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    def get_run_by_id(self, run_id: int) -> Optional[dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM runs WHERE id = ?", (run_id,))
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None

    def delete_run(self, run_id: int) -> bool:
        """Deletes a run by its ID. Returns True if deleted, False if not found."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM runs WHERE id = ?", (run_id,))
            conn.commit()
            return cursor.rowcount > 0

    def search_runs(self, keyword: str) -> list[dict]:
        """
        Searches runs by keyword in symptoms, question, or final_state fields.
        Returns matching rows as list of dicts.
        """
        like_keyword = f"%{keyword.lower()}%"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM runs
                WHERE LOWER(symptoms) LIKE ?
                   OR LOWER(question) LIKE ?
                   OR LOWER(final_state) LIKE ?
                ORDER BY id DESC
            """,
                (like_keyword, like_keyword, like_keyword),
            )
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
