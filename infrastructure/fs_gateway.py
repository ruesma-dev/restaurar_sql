# etl_restore/infrastructure/fs_gateway.py
"""Gateway para mapear/desmapear la carpeta de red con `net use`."""
from __future__ import annotations

import subprocess
import contextlib
import logging


class NetworkShareGateway(contextlib.AbstractContextManager):
    """Context manager para montar y desmontar una carpeta compartida Windows."""

    def __init__(self, *, share: str, user: str | None = None, password: str | None = None):
        self.share = share
        self.user = user
        self.password = password

    # ---------------------------------------------
    def __enter__(self):
        logging.info("Mapeando %s", self.share)
        cmd = ["net", "use", self.share]
        if self.password and self.user:
            cmd += [self.password, "/user:" + self.user]
        result = subprocess.run(cmd, capture_output=True, text=True, shell=False)
        if result.returncode not in (0, 2):  # 2 = ya mapeado
            raise RuntimeError(f"Error al mapear: {result.stderr.strip()}")
        return self

    def __exit__(self, exc_type, exc, tb):  # noqa: D401
        logging.info("Desmapeando %s", self.share)
        cmd = ["net", "use", self.share, "/delete", "/y"]
        subprocess.run(cmd, capture_output=True, text=True, shell=False)
        # No sueltes excepción para permitir restaurar
        return False