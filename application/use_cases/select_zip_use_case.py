# application/use_cases/select_zip_use_case.py
from __future__ import annotations

from pathlib import Path
from datetime import datetime
import logging


class SelectZipUseCase:
    """Selecciona el ZIP más reciente que NO contenga 'rep'."""

    def __init__(self, shared_folder: Path) -> None:
        self.shared_folder = shared_folder

    # ---------------------------------------------
    def execute(self) -> Path:
        logging.info("Buscando ZIPs en %s", self.shared_folder)
        zip_files = [
            p
            for p in self.shared_folder.glob("*.zip")
            if "rep" not in p.stem.lower()
        ]
        if not zip_files:
            raise FileNotFoundError("No hay ZIPs válidos en la carpeta compartida")

        def timestamp(path: Path) -> datetime:
            digits = "".join(filter(str.isdigit, path.stem))
            return datetime.strptime(digits, "%Y%m%d%H%M")

        chosen = max(zip_files, key=timestamp)
        return chosen