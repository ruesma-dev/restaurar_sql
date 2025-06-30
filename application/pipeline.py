# application/pipeline.py
from __future__ import annotations

from pathlib import Path
import logging

from application.use_cases.select_zip_use_case import SelectZipUseCase
from application.use_cases.copy_and_extract_use_case import (
    CopyAndExtractUseCase,
)
from application.use_cases.restore_database_use_case import (
    RestoreDatabaseUseCase,
)
from infrastructure.fs_gateway import NetworkShareGateway
from infrastructure.config import Config


class RestorePipeline:
    """Encadena los tres pasos del proceso de restauración."""

    def __init__(
        self,
        *,
        shared_folder: Path,
        local_folder: Path,
        sql_instance: str,
        database_name: str,
        auth: dict | None,
    ) -> None:
        self.shared_folder = shared_folder
        self.local_folder = local_folder
        self.sql_instance = sql_instance
        self.database_name = database_name
        self.auth = auth

        self.select_zip = SelectZipUseCase(shared_folder)
        self.copy_extract = CopyAndExtractUseCase(local_folder)
        self.restore_db = RestoreDatabaseUseCase(sql_instance, database_name, auth)

        self._net_use = NetworkShareGateway(
            share=str(shared_folder),
            user=Config.NETWORK_SHARE_USER,
            password=Config.NETWORK_SHARE_PASSWORD,
        )

    # ---------------------------------------------------------
    def run(self) -> None:  # noqa: D401
        logging.info("===== INICIO PIPELINE RESTORE (.bak) =====")

        # 0️⃣ Mapear unidad/red (si procede)
        with self._net_use:
            # 1️⃣ Seleccionar ZIP válido
            zip_path = self.select_zip.execute()
            logging.info("ZIP seleccionado: %s", zip_path.name)

            # 2️⃣ Copiar + extraer
            bak_path = self.copy_extract.execute(zip_path)
            logging.info(".bak extraído en %s", bak_path)

        # 3️⃣ Restaurar BD (fuera del contexto – la unidad ya no es necesaria)
        self.restore_db.execute(bak_path)

        logging.info("===== PIPELINE COMPLETADO ✅ =====")