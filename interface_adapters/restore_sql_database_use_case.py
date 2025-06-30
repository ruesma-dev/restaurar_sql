# interface_adapters/controllers/restore_sql_database_use_case.py
from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import pyodbc

logger = logging.getLogger(__name__)


class RestoreSQLDatabaseUseCase:
    """Restaura un archivo .bak en SQL Server con WITH REPLACE."""

    def __init__(
        self,
        *,
        bak_file_path: str | Path,
        database_name: str,
        sql_server: str,
        auth: Optional[Dict[str, str]] = None,
    ) -> None:
        self.bak_file = Path(bak_file_path)
        self.database_name = database_name
        self.sql_server = sql_server
        self.auth = auth

    # ------------- helpers -----------------------
    def _pyodbc_conn(self):
        if self.auth:
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.sql_server};"
                "DATABASE=master;UID={user};PWD={password};".format(**self.auth)
            )
        else:
            conn_str = (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                f"SERVER={self.sql_server};DATABASE=master;Trusted_Connection=yes;"
            )
        return pyodbc.connect(conn_str, autocommit=True)

    def _sqlcmd_base(self) -> List[str]:
        if self.auth:
            return ["sqlcmd", "-S", self.sql_server, "-U", self.auth["user"], "-P", self.auth["password"]]
        return ["sqlcmd", "-S", self.sql_server, "-E"]

    @staticmethod
    def _run(cmd: List[str]):
        logger.debug("Ejecutando: %s", " ".join(cmd))
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip())

    # ------------- lógica principal --------------
    def execute(self) -> bool:
        try:
            logical = self._logical_names()
            logger.info("Logical names: %s", logical)

            restore_sql = f"""
            ALTER DATABASE [{self.database_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
            RESTORE DATABASE [{self.database_name}] FROM DISK = '{self.bak_file}'
            WITH MOVE '{logical['data']}' TO '{self.database_name}.mdf',
                 MOVE '{logical['log']}'  TO '{self.database_name}Log.ldf',
                 REPLACE, STATS = 10;
            ALTER DATABASE [{self.database_name}] SET MULTI_USER;
            """
            self._run(self._sqlcmd_base() + ["-Q", restore_sql])
            logger.info("BD restaurada correctamente ✅")
            return True
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("❌ Restauración fallida: %s", exc)
            return False

    # ------------- utilidades --------------------
    def _logical_names(self):
        with self._pyodbc_conn() as con:
            cur = con.cursor()
            cur.execute("RESTORE FILELISTONLY FROM DISK = ?", (str(self.bak_file),))
            rows = cur.fetchall()
            logical = {"data": "", "log": ""}
            for r in rows:
                if r.Type == "D":
                    logical["data"] = r.LogicalName
                elif r.Type == "L":
                    logical["log"] = r.LogicalName
            if not all(logical.values()):
                raise ValueError("No se pudieron obtener nombres lógicos del .bak")
            return logical
