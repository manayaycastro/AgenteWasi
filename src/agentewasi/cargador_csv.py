"""Carga segura de archivos CSV para AgenteWasi."""

from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError, ParserError


class ErrorCargaCSV(ValueError):
    """Error controlado durante la carga de un archivo CSV."""


def cargar_csv(ruta: str | Path) -> pd.DataFrame:
    """Carga un CSV válido y devuelve su contenido como DataFrame."""

    archivo = Path(ruta)

    if archivo.suffix.lower() != ".csv":
        raise ErrorCargaCSV(
            f"El archivo debe tener extensión .csv: {archivo}"
        )

    if not archivo.exists():
        raise ErrorCargaCSV(
            f"El archivo no existe: {archivo}"
        )

    if not archivo.is_file():
        raise ErrorCargaCSV(
            f"La ruta no corresponde a un archivo: {archivo}"
        )

    try:
        datos = pd.read_csv(archivo, encoding="utf-8")
    except EmptyDataError as error:
        raise ErrorCargaCSV(
            f"El archivo CSV está vacío: {archivo}"
        ) from error
    except UnicodeDecodeError as error:
        raise ErrorCargaCSV(
            f"El archivo no utiliza codificación UTF-8: {archivo}"
        ) from error
    except ParserError as error:
        raise ErrorCargaCSV(
            f"El archivo CSV tiene un formato inválido: {archivo}"
        ) from error
    except OSError as error:
        raise ErrorCargaCSV(
            f"No se pudo leer el archivo CSV: {archivo}"
        ) from error

    if datos.empty:
        raise ErrorCargaCSV(
            f"El archivo CSV no contiene registros: {archivo}"
        )

    return datos
