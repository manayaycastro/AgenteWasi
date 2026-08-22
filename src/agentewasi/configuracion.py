"""Configuración segura de AgenteWasi."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


class ErrorConfiguracion(ValueError):
    """Error en la configuración local del agente."""


@dataclass(frozen=True)
class Configuracion:
    """Configuración necesaria para ejecutar AgenteWasi."""

    base_url: str
    api_key: str
    deployment: str
    ventas_csv: Path
    inventario_csv: Path

    @classmethod
    def desde_entorno(cls) -> "Configuracion":
        """Carga y valida la configuración desde .env."""

        load_dotenv(dotenv_path=".env")

        requeridas = (
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_DEPLOYMENT",
            "VENTAS_CSV_PATH",
            "INVENTARIO_CSV_PATH",
        )

        faltantes = [
            variable
            for variable in requeridas
            if not os.getenv(variable, "").strip()
        ]

        if faltantes:
            raise ErrorConfiguracion(
                "Faltan variables de entorno: "
                + ", ".join(faltantes)
            )

        endpoint = os.environ[
            "AZURE_OPENAI_ENDPOINT"
        ].strip().rstrip("/")

        return cls(
            base_url=f"{endpoint}/",
            api_key=os.environ[
                "AZURE_OPENAI_API_KEY"
            ].strip(),
            deployment=os.environ[
                "AZURE_OPENAI_DEPLOYMENT"
            ].strip(),
            ventas_csv=Path(
                os.environ["VENTAS_CSV_PATH"]
            ),
            inventario_csv=Path(
                os.environ["INVENTARIO_CSV_PATH"]
            ),
        )
