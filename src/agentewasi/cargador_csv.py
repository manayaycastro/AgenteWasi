"""Carga y validación segura de archivos CSV para AgenteWasi."""

from collections.abc import Collection
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError, ParserError


class ErrorCargaCSV(ValueError):
    """Error controlado durante la carga de un archivo CSV."""


class ErrorColumnasCSV(ErrorCargaCSV):
    """Error generado cuando faltan columnas obligatorias."""


def validar_columnas(
    datos: pd.DataFrame,
    columnas_obligatorias: Collection[str],
    nombre_archivo: str = "archivo CSV",
) -> None:
    """Verifica que un DataFrame contenga todas las columnas requeridas."""

    columnas_actuales = set(map(str, datos.columns))
    faltantes = sorted(set(columnas_obligatorias) - columnas_actuales)

    if faltantes:
        detalle = ", ".join(faltantes)
        raise ErrorColumnasCSV(
            f"Faltan columnas obligatorias en {nombre_archivo}: {detalle}"
        )


def cargar_csv(
    ruta: str | Path,
    columnas_obligatorias: Collection[str] | None = None,
) -> pd.DataFrame:
    """Carga un CSV válido y opcionalmente verifica sus columnas."""

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

    if columnas_obligatorias is not None:
        validar_columnas(
            datos,
            columnas_obligatorias,
            nombre_archivo=archivo.name,
        )

    return datos
