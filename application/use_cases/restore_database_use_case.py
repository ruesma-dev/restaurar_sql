# application/use_cases/restore_database_use_case.py
from __future__ import annotations

from pathlib import Path
import logging

from interface_adapters.restore_sql_database_use_case import RestoreSQLDatabaseUseCase


class RestoreDatabaseUseCase:
    """Envuelve RestoreSQLDatabaseUseCase para integrarlo en el pipeline."""

    def __init__(self, sql_instance: str, database_name: str, auth: dict | None):
        self.sql_instance = sql_instance
        self.database_name = database_name
        self.auth = auth

    # ---------------------------------------------
    def execute(self, bak_file: Path) -> None:
        logging.info("Restaurando BD %s desde %s", self.database_name, bak_file)
        restorer = RestoreSQLDatabaseUseCase(
            bak_file_path=bak_file,
            database_name=self.database_name,
            sql_server=self.sql_instance,
            auth=self.auth,
        )
        if not restorer.execute():
            raise RuntimeError("Fallo al restaurar la base de datos")
