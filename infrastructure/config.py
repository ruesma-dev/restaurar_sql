# etl_restore/infrastructure/config.py
"""Carga las variables de entorno del archivo .env."""
from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar .env (busca hacia arriba desde el cwd)
load_dotenv()


class Config:  # pylint: disable=too-few-public-methods
    # --- SQL Server ---
    SQL_SERVER = os.getenv("SQL_SERVER")
    SQL_DATABASE = os.getenv("SQL_DATABASE", "TemporaryDB")
    SQL_DRIVER = os.getenv("SQL_DRIVER", "ODBC Driver 17 for SQL Server")
    SQL_USER = os.getenv("SQL_USER")
    SQL_PASSWORD = os.getenv("SQL_PASSWORD")
    SQL_PORT = os.getenv("SQL_PORT", "1433")
    INTEGRATED_AUTH = os.getenv("INTEGRATED_AUTH", "false").lower() == "true"

    # --- Carpetas ---
    LOCAL_BAK_FOLDER = os.getenv("LOCAL_BAK_FOLDER", r"C:\SQLBackups")
    SHARED_ZIP_FOLDER = os.getenv("SHARED_ZIP_FOLDER")

    # --- Red ---
    NETWORK_SHARE_USER = os.getenv("NETWORK_SHARE_USER")
    NETWORK_SHARE_PASSWORD = os.getenv("NETWORK_SHARE_PASSWORD")
