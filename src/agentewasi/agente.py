"""Agente conversacional conectado con Microsoft Foundry."""

import json
from typing import Any

from openai import OpenAI

from .cargador_csv import cargar_csv
from .configuracion import Configuracion
from .esquemas import (
    COLUMNAS_INVENTARIO,
    COLUMNAS_VENTAS,
)
from .herramientas import (
    analizar_clientes,
    analizar_ventas_por_periodo,
    calcular_ventas_totales,
    detectar_productos_poca_venta,
    detectar_stock_critico,
    obtener_productos_mas_vendidos,
    recomendar_reposicion,
)
from .instrucciones import INSTRUCCIONES_SISTEMA
from .respuestas import ejecutar_herramienta_segura


def _parametros_periodo() -> dict[str, object]:
    return {
        "fecha_inicio": {
            "type": "string",
            "description": "Fecha inicial AAAA-MM-DD.",
        },
        "fecha_fin": {
            "type": "string",
            "description": "Fecha final AAAA-MM-DD.",
        },
    }


HERRAMIENTAS_MODELO = [
    {
        "type": "function",
        "name": "calcular_ventas_totales",
        "description": (
            "Calcula ventas, descuentos y total para un periodo."
        ),
        "parameters": {
            "type": "object",
            "properties": _parametros_periodo(),
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "obtener_productos_mas_vendidos",
        "description": (
            "Obtiene productos líderes por unidades e ingresos."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "top_n": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Cantidad de productos.",
                },
                **_parametros_periodo(),
            },
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "detectar_stock_critico",
        "description": (
            "Clasifica productos agotados, críticos, bajos y normales."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "incluir_normales": {
                    "type": "boolean",
                    "description": (
                        "Indica si se incluyen productos normales."
                    ),
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "analizar_ventas_por_periodo",
        "description": (
            "Analiza ventas por categoría, pago y día."
        ),
        "parameters": {
            "type": "object",
            "properties": _parametros_periodo(),
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "recomendar_reposicion",
        "description": (
            "Recomienda cantidades informativas de reposición."
        ),
        "parameters": {
            "type": "object",
            "properties": _parametros_periodo(),
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "detectar_productos_poca_venta",
        "description": (
            "Detecta productos con poca o ninguna venta."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "umbral_promedio_diario": {
                    "type": "number",
                    "exclusiveMinimum": 0,
                    "description": (
                        "Umbral diario; por defecto es 1."
                    ),
                },
                **_parametros_periodo(),
            },
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "analizar_clientes",
        "description": (
            "Calcula rankings, gasto, ticket y recurrencia de clientes."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "top_n": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Cantidad de clientes.",
                },
                **_parametros_periodo(),
            },
            "additionalProperties": False,
        },
    },
]


class AgenteWasi:
    """Orquesta el modelo y las herramientas deterministas."""

    def __init__(
        self,
        configuracion: Configuracion | None = None,
    ) -> None:
        self.configuracion = (
            configuracion
            if configuracion is not None
            else Configuracion.desde_entorno()
        )

        self.cliente = OpenAI(
            api_key=self.configuracion.api_key,
            base_url=self.configuracion.base_url,
        )

        self.ventas = cargar_csv(
            self.configuracion.ventas_csv,
            COLUMNAS_VENTAS,
        )
        self.inventario = cargar_csv(
            self.configuracion.inventario_csv,
            COLUMNAS_INVENTARIO,
        )

        self.historial: list[dict[str, str]] = []

    def _funcion_y_argumentos(
        self,
        nombre: str,
        argumentos: dict[str, Any],
    ) -> tuple[Any, tuple[Any, ...], dict[str, Any]]:
        funciones = {
            "calcular_ventas_totales": (
                calcular_ventas_totales,
                (self.ventas,),
            ),
            "obtener_productos_mas_vendidos": (
                obtener_productos_mas_vendidos,
                (self.ventas, self.inventario),
            ),
            "detectar_stock_critico": (
                detectar_stock_critico,
                (self.inventario,),
            ),
            "analizar_ventas_por_periodo": (
                analizar_ventas_por_periodo,
                (self.ventas, self.inventario),
            ),
            "recomendar_reposicion": (
                recomendar_reposicion,
                (self.ventas, self.inventario),
            ),
            "detectar_productos_poca_venta": (
                detectar_productos_poca_venta,
                (self.ventas, self.inventario),
            ),
            "analizar_clientes": (
                analizar_clientes,
                (self.ventas,),
            ),
        }

        if nombre not in funciones:
            raise ValueError(
                f"Herramienta no permitida: {nombre}"
            )

        funcion, argumentos_base = funciones[nombre]

        return funcion, argumentos_base, argumentos

    def _ejecutar_llamada(
        self,
        nombre: str,
        argumentos_json: str,
    ) -> dict[str, object]:
        try:
            argumentos = json.loads(
                argumentos_json or "{}"
            )
        except json.JSONDecodeError as error:
            return {
                "ok": False,
                "herramienta": nombre,
                "datos": None,
                "error": {
                    "tipo": type(error).__name__,
                    "mensaje": (
                        "Los argumentos enviados por el modelo "
                        "no son JSON válido."
                    ),
                },
            }

        try:
            funcion, base, parametros = (
                self._funcion_y_argumentos(
                    nombre,
                    argumentos,
                )
            )
        except ValueError as error:
            return {
                "ok": False,
                "herramienta": nombre,
                "datos": None,
                "error": {
                    "tipo": type(error).__name__,
                    "mensaje": str(error),
                },
            }

        return ejecutar_herramienta_segura(
            nombre,
            funcion,
            *base,
            **parametros,
        )

    def preguntar(self, pregunta: str) -> str:
        """Responde una pregunta utilizando el modelo y herramientas."""

        if not isinstance(pregunta, str) or not pregunta.strip():
            raise ValueError(
                "La pregunta no puede estar vacía."
            )

        entrada: list[Any] = [
            *self.historial,
            {
                "role": "user",
                "content": pregunta.strip(),
            },
        ]

        for _ in range(5):
            respuesta = self.cliente.responses.create(
                model=self.configuracion.deployment,
                instructions=INSTRUCCIONES_SISTEMA,
                input=entrada,
                tools=HERRAMIENTAS_MODELO,
            )

            llamadas = [
                elemento
                for elemento in respuesta.output
                if elemento.type == "function_call"
            ]

            if not llamadas:
                texto = respuesta.output_text.strip()

                if not texto:
                    raise RuntimeError(
                        "El modelo no devolvió una respuesta."
                    )

                self.historial.extend(
                    [
                        {
                            "role": "user",
                            "content": pregunta.strip(),
                        },
                        {
                            "role": "assistant",
                            "content": texto,
                        },
                    ]
                )

                return texto

            entrada.extend(respuesta.output)

            for llamada in llamadas:
                resultado = self._ejecutar_llamada(
                    llamada.name,
                    llamada.arguments,
                )

                entrada.append(
                    {
                        "type": "function_call_output",
                        "call_id": llamada.call_id,
                        "output": json.dumps(
                            resultado,
                            ensure_ascii=False,
                        ),
                    }
                )

        raise RuntimeError(
            "Se alcanzó el límite de ejecuciones de herramientas."
        )
