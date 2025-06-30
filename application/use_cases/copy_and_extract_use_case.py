# application/use_cases/copy_and_extract_use_case.py
from __future__ import annotations

from pathlib import Path
import shutil
import zipfile
import logging


class CopyAndExtractUseCase:
    """Copia ZIP → limpia .bak viejos → extrae .bak → borra ZIP."""

    def __init__(self, local_folder: Path) -> None:
        self.local_folder = local_folder

    # ---------------------------------------------
    def execute(self, zip_path: Path) -> Path:
        # 1) Asegurar carpeta local
        self.local_folder.mkdir(parents=True, exist_ok=True)
        logging.info("Carpeta local preparada: %s", self.local_folder)

        # 2) Borrar .bak previos
        deleted = 0
        for bak in self.local_folder.glob("*.bak"):
            bak.unlink()
            deleted += 1
        if deleted:
            logging.info("Borrados %s .bak antiguos", deleted)

        # 3) Copiar ZIP
        local_zip = self.local_folder / zip_path.name
        shutil.copy2(zip_path, local_zip)
        logging.info("ZIP copiado a %s", local_zip)

        # 4) Extraer .bak
        with zipfile.ZipFile(local_zip) as zf:
            bak_members = [m for m in zf.namelist() if m.lower().endswith(".bak")]
            if not bak_members:
                raise ValueError("El ZIP no contiene ningún .bak")
            member = bak_members[0]
            zf.extract(member, path=self.local_folder)
            logging.info("Extraído %s", member)

        # 5) Borrar ZIP
        local_zip.unlink()
        logging.info("ZIP original eliminado")

        return self.local_folder / Path(member).name