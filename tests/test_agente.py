"""Pruebas del núcleo conversacional de AgenteWasi."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from agentewasi.agente import (
    AgenteWasi,
    HERRAMIENTAS_MODELO,
)
from agentewasi.configuracion import Configuracion
from agentewasi.instrucciones import INSTRUCCIONES_SISTEMA


def _crear_agente_sin_llamada_externa():
    raiz = Path(__file__).resolve().parents[1]

    configuracion = Configuracion(
        base_url=(
            "https://ejemplo.openai.azure.com/"
            "openai/v1/"
        ),
        api_key="clave-de-prueba",
        deployment="deployment-prueba",
        ventas_csv=raiz / "data" / "ventas_ejemplo.csv",
        inventario_csv=(
            raiz / "data" / "inventario_ejemplo.csv"
        ),
    )

    return AgenteWasi(configuracion)


def test_registrar_siete_herramientas():
    nombres = {
        herramienta["name"]
        for herramienta in HERRAMIENTAS_MODELO
    }

    assert nombres == {
        "calcular_ventas_totales",
        "obtener_productos_mas_vendidos",
        "detectar_stock_critico",
        "analizar_ventas_por_periodo",
        "recomendar_reposicion",
        "detectar_productos_poca_venta",
        "analizar_clientes",
    }


def test_instrucciones_contienen_limites_principales():
    assert "No calcules" in INSTRUCCIONES_SISTEMA
    assert "no generan pedidos" in INSTRUCCIONES_SISTEMA
    assert "Responde en español" in INSTRUCCIONES_SISTEMA
    assert "personas reales" in INSTRUCCIONES_SISTEMA


def test_agente_carga_los_archivos_reales():
    agente = _crear_agente_sin_llamada_externa()

    assert agente.ventas.shape == (10475, 10)
    assert agente.inventario.shape == (35, 8)


def test_agente_ejecuta_herramienta_local():
    agente = _crear_agente_sin_llamada_externa()

    resultado = agente._ejecutar_llamada(
        "calcular_ventas_totales",
        json.dumps(
            {
                "fecha_inicio": "2026-08-21",
                "fecha_fin": "2026-08-21",
            }
        ),
    )

    assert resultado["ok"] is True
    assert resultado["datos"]["total_ventas"] == 802.16
    assert resultado["error"] is None


def test_agente_controla_argumentos_json_invalidos():
    agente = _crear_agente_sin_llamada_externa()

    resultado = agente._ejecutar_llamada(
        "calcular_ventas_totales",
        "{json-invalido",
    )

    assert resultado["ok"] is False
    assert resultado["datos"] is None
    assert resultado["error"]["tipo"] == "JSONDecodeError"


def test_agente_rechaza_herramienta_desconocida():
    agente = _crear_agente_sin_llamada_externa()

    resultado = agente._ejecutar_llamada(
        "eliminar_inventario",
        "{}",
    )

    assert resultado["ok"] is False
    assert "no permitida" in resultado["error"]["mensaje"]


def test_agente_rechaza_pregunta_vacia():
    agente = _crear_agente_sin_llamada_externa()

    with pytest.raises(
        ValueError,
        match="no puede estar vacía",
    ):
        agente.preguntar("   ")


def test_ciclo_modelo_herramienta_respuesta():
    agente = _crear_agente_sin_llamada_externa()

    llamada = SimpleNamespace(
        type="function_call",
        name="calcular_ventas_totales",
        arguments=json.dumps(
            {
                "fecha_inicio": "2026-08-21",
                "fecha_fin": "2026-08-21",
            }
        ),
        call_id="call-prueba-1",
    )

    primera_respuesta = SimpleNamespace(
        output=[llamada],
        output_text="",
    )

    segunda_respuesta = SimpleNamespace(
        output=[],
        output_text=(
            "El total vendido fue S/ 802.16."
        ),
    )

    class RespuestasFalsas:
        def __init__(self):
            self.respuestas = [
                primera_respuesta,
                segunda_respuesta,
            ]
            self.llamadas = []

        def create(self, **parametros):
            self.llamadas.append(parametros)
            return self.respuestas.pop(0)

    respuestas_falsas = RespuestasFalsas()

    agente.cliente = SimpleNamespace(
        responses=respuestas_falsas
    )

    texto = agente.preguntar(
        "¿Cuánto se vendió el 21 de agosto de 2026?"
    )

    assert texto == "El total vendido fue S/ 802.16."
    assert len(respuestas_falsas.llamadas) == 2
    assert len(agente.historial) == 2
    assert agente.historial[-1]["role"] == "assistant"
