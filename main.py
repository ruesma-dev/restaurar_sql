# main.py
"""
Micro-servicio 1 - Restauración de BD
────────────────────────────────────
0. Mapea la carpeta compartida.
1. Selecciona el ZIP más reciente (≠ 'rep') y lo copia.
2. Limpia .bak antiguos, extrae el nuevo y borra el ZIP.
3. Restaura TemporaryDB usando *solo* autenticación integrada.
"""

from __future__ import annotations
import logging
from pathlib import Path
import sys

from application.pipeline import RestorePipeline
from infrastructure.config import Config

# --- configuración de logging ----------------------------------------------
LOG_FMT = "%(asctime)s  [%(levelname)s]  %(name)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FMT)
logger = logging.getLogger("main")

# --- entry-point ------------------------------------------------------------
def main() -> None:  # noqa: D401
    try:
        pipeline = RestorePipeline(
            shared_folder=Path(Config.SHARED_ZIP_FOLDER),
            local_folder=Path(Config.LOCAL_BAK_FOLDER),
            sql_instance=Config.SQL_SERVER,
            database_name=Config.SQL_DATABASE,
            # siempre auth integrada → auth=None
            auth=None,
        )
        pipeline.run()
        logger.info("🏁 Proceso de restauración COMPLETADO sin errores")
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("🔥 Restauración abortada: %s", exc, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
