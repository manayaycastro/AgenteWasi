"""Pruebas de las respuestas estructuradas de AgenteWasi."""

import json

import pytest

from agentewasi.respuestas import (
    ErrorRespuestaHerramienta,
    crear_respuesta_error,
    crear_respuesta_exitosa,
    ejecutar_herramienta_segura,
)


def test_crear_respuesta_exitosa():
    respuesta = crear_respuesta_exitosa(
        "herramienta_prueba",
        {
            "total": 100.50,
            "cantidad": 4,
        },
    )

    assert respuesta == {
        "ok": True,
        "herramienta": "herramienta_prueba",
        "datos": {
            "total": 100.50,
            "cantidad": 4,
        },
        "error": None,
    }


def test_respuesta_exitosa_es_serializable():
    respuesta = crear_respuesta_exitosa(
        "herramienta_prueba",
        {
            "producto": "Leche evaporada",
            "cantidad": 10,
        },
    )

    contenido = json.dumps(
        respuesta,
        ensure_ascii=False,
    )

    assert "Leche evaporada" in contenido


def test_crear_respuesta_de_error():
    error = ValueError("Periodo inválido")

    respuesta = crear_respuesta_error(
        "analizar_ventas",
        error,
    )

    assert respuesta == {
        "ok": False,
        "herramienta": "analizar_ventas",
        "datos": None,
        "error": {
            "tipo": "ValueError",
            "mensaje": "Periodo inválido",
        },
    }


def test_ejecutar_herramienta_exitosa():
    def sumar(valor_a, valor_b):
        return {
            "resultado": valor_a + valor_b,
        }

    respuesta = ejecutar_herramienta_segura(
        "sumar",
        sumar,
        4,
        6,
    )

    assert respuesta["ok"] is True
    assert respuesta["datos"]["resultado"] == 10
    assert respuesta["error"] is None


def test_ejecutar_herramienta_controla_value_error():
    def operacion_invalida():
        raise ValueError("Dato inválido")

    respuesta = ejecutar_herramienta_segura(
        "operacion_invalida",
        operacion_invalida,
    )

    assert respuesta["ok"] is False
    assert respuesta["datos"] is None
    assert respuesta["error"]["tipo"] == "ValueError"
    assert respuesta["error"]["mensaje"] == "Dato inválido"


def test_rechazar_nombre_de_herramienta_vacio():
    with pytest.raises(
        ErrorRespuestaHerramienta,
        match="no puede estar vacío",
    ):
        crear_respuesta_exitosa(
            "   ",
            {},
        )


def test_rechazar_datos_no_serializables():
    with pytest.raises(
        ErrorRespuestaHerramienta,
        match="no serializables",
    ):
        crear_respuesta_exitosa(
            "herramienta_prueba",
            {
                "valores": {1, 2, 3},
            },
        )


def test_no_ocultar_errores_inesperados():
    def error_inesperado():
        raise RuntimeError(
            "Fallo interno inesperado"
        )

    with pytest.raises(
        RuntimeError,
        match="Fallo interno inesperado",
    ):
        ejecutar_herramienta_segura(
            "error_inesperado",
            error_inesperado,
        )
