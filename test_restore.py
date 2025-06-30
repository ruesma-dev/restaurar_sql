
"""
Smoke-test de restauración con autenticación integrada:
  1. Comprueba driver y conecta.
  2. Usa el .bak más reciente de C:\\SQLBackups.
  3. Restaura sobre TemporaryDB.
"""

from __future__ import annotations
import logging, os
from pathlib import Path
from datetime import datetime

import pyodbc
from dotenv import load_dotenv

from interface_adapters.restore_sql_database_use_case import (
    RestoreSQLDatabaseUseCase,
)

# --------------------------------------------------------------------------- #
# Config (.env)
# --------------------------------------------------------------------------- #
load_dotenv()

SQL_SERVER       = os.getenv("SQL_SERVER", r"localhost\MSSQLSERVER01")
SQL_DATABASE     = os.getenv("SQL_DATABASE", "TemporaryDB")
SQL_DRIVER       = os.getenv("SQL_DRIVER", "ODBC Driver 17 for SQL Server")
INTEGRATED_AUTH  = True   # forzamos auth integrada

LOCAL_BAK_FOLDER = Path(os.getenv("LOCAL_BAK_FOLDER", r"C:\SQLBackups"))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s  [%(levelname)s]  %(message)s"
)

# --------------------------------------------------------------------------- #
def test_sql_connection() -> None:
    if SQL_DRIVER not in pyodbc.drivers():
        raise RuntimeError(
            f"Driver '{SQL_DRIVER}' no instalado. Instala «ODBC Driver 17 for SQL Server»."
        )

    conn_str = (
        f"DRIVER={{{SQL_DRIVER}}};"
        f"SERVER={SQL_SERVER};"
        "DATABASE=master;"
        "Trusted_Connection=yes;"
    )

    with pyodbc.connect(conn_str, timeout=5):
        logging.info("✅ Conexión integrada a SQL Server correcta")

# --------------------------------------------------------------------------- #
def latest_bak() -> Path:
    try:
        return max(LOCAL_BAK_FOLDER.glob("*.bak"), key=lambda p: p.stat().st_mtime)
    except ValueError:
        raise FileNotFoundError(f"No hay .bak en {LOCAL_BAK_FOLDER}")

# --------------------------------------------------------------------------- #
def restore(bak_file: Path) -> None:
    restorer = RestoreSQLDatabaseUseCase(
        bak_file_path=bak_file,
        database_name=SQL_DATABASE,
        sql_server=SQL_SERVER,
        auth=None,                      # autenticación integrada
    )
    if restorer.execute():
        logging.info("🎉 Restauración completada con éxito")
    else:
        raise RuntimeError("❌ La restauración falló — revisa logs anteriores")

# --------------------------------------------------------------------------- #

# --------------------------------------------------------------------------- #
# 4. Listar las tablas de la BD restaurada
# --------------------------------------------------------------------------- #
def list_tables() -> None:
    conn_str = (
        f"DRIVER={{{SQL_DRIVER}}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        "Trusted_Connection=yes;"
    )
    with pyodbc.connect(conn_str) as cn:
        cur = cn.cursor()
        cur.execute(
            """
            SELECT TABLE_SCHEMA, TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_SCHEMA, TABLE_NAME;
            """
        )
        rows = cur.fetchall()
        logging.info("Tablas en %s:", SQL_DATABASE)
        for schema_, name in rows:
            print(f"{schema_}.{name}")

# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    test_sql_connection()
    bak_file = latest_bak()
    restore(bak_file)
    list_tables()          # ← nueva llamada

