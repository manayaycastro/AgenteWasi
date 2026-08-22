"""Respuestas estructuradas para las herramientas de AgenteWasi."""

import json
from collections.abc import Callable
from typing import Any


class ErrorRespuestaHerramienta(ValueError):
    """Error al construir una respuesta estructurada."""


def _validar_nombre_herramienta(
    herramienta: str,
) -> None:
    """Valida el nombre utilizado en la respuesta."""

    if not isinstance(herramienta, str):
        raise ErrorRespuestaHerramienta(
            "El nombre de la herramienta debe ser texto."
        )

    if not herramienta.strip():
        raise ErrorRespuestaHerramienta(
            "El nombre de la herramienta no puede estar vacío."
        )


def crear_respuesta_exitosa(
    herramienta: str,
    datos: dict[str, object],
) -> dict[str, object]:
    """Crea una respuesta uniforme para una ejecución exitosa."""

    _validar_nombre_herramienta(herramienta)

    if not isinstance(datos, dict):
        raise ErrorRespuestaHerramienta(
            "Los datos de la herramienta deben ser un diccionario."
        )

    respuesta: dict[str, object] = {
        "ok": True,
        "herramienta": herramienta,
        "datos": datos,
        "error": None,
    }

    try:
        json.dumps(
            respuesta,
            ensure_ascii=False,
        )
    except (TypeError, ValueError) as error:
        raise ErrorRespuestaHerramienta(
            "La respuesta contiene valores no serializables a JSON."
        ) from error

    return respuesta


def crear_respuesta_error(
    herramienta: str,
    error: Exception,
) -> dict[str, object]:
    """Crea una respuesta uniforme para un error controlado."""

    _validar_nombre_herramienta(herramienta)

    if not isinstance(error, Exception):
        raise ErrorRespuestaHerramienta(
            "El error recibido debe ser una excepción."
        )

    mensaje = str(error).strip()

    if not mensaje:
        mensaje = "La herramienta no pudo completar la operación."

    return {
        "ok": False,
        "herramienta": herramienta,
        "datos": None,
        "error": {
            "tipo": type(error).__name__,
            "mensaje": mensaje,
        },
    }


def ejecutar_herramienta_segura(
    herramienta: str,
    funcion: Callable[..., dict[str, object]],
    *argumentos: Any,
    **parametros: Any,
) -> dict[str, object]:
    """Ejecuta una herramienta y normaliza su resultado o error."""

    _validar_nombre_herramienta(herramienta)

    if not callable(funcion):
        raise ErrorRespuestaHerramienta(
            "La función de la herramienta debe ser ejecutable."
        )

    try:
        datos = funcion(
            *argumentos,
            **parametros,
        )
    except (ValueError, TypeError) as error:
        return crear_respuesta_error(
            herramienta,
            error,
        )

    return crear_respuesta_exitosa(
        herramienta,
        datos,
    )
