"""Pruebas de la interfaz de consola."""

from agentewasi.cli import (
    MENSAJE_INICIO,
    ejecutar_cli,
)


class AgenteFalso:
    def __init__(
        self,
        respuesta="Respuesta calculada.",
        error=None,
    ):
        self.respuesta = respuesta
        self.error = error
        self.preguntas = []

    def preguntar(self, pregunta):
        self.preguntas.append(pregunta)

        if self.error is not None:
            raise self.error

        return self.respuesta


def _crear_lector(entradas):
    iterador = iter(entradas)

    def leer(_mensaje):
        return next(iterador)

    return leer


def test_cli_responde_y_permite_salir():
    agente = AgenteFalso(
        "El total vendido fue S/ 802.16."
    )
    salidas = []

    ejecutar_cli(
        agente=agente,
        leer=_crear_lector(
            [
                "¿Cuánto se vendió?",
                "salir",
            ]
        ),
        escribir=salidas.append,
    )

    assert agente.preguntas == [
        "¿Cuánto se vendió?"
    ]
    assert any(
        "S/ 802.16" in salida
        for salida in salidas
    )
    assert any(
        "Conversación finalizada" in salida
        for salida in salidas
    )


def test_cli_controla_pregunta_vacia():
    agente = AgenteFalso()
    salidas = []

    ejecutar_cli(
        agente=agente,
        leer=_crear_lector(
            [
                "   ",
                "salir",
            ]
        ),
        escribir=salidas.append,
    )

    assert agente.preguntas == []
    assert any(
        "Escribe una pregunta" in salida
        for salida in salidas
    )


def test_cli_muestra_error_controlado():
    agente = AgenteFalso(
        error=ValueError("Periodo inválido")
    )
    salidas = []

    ejecutar_cli(
        agente=agente,
        leer=_crear_lector(
            [
                "consulta inválida",
                "salir",
            ]
        ),
        escribir=salidas.append,
    )

    assert any(
        "Periodo inválido" in salida
        for salida in salidas
    )


def test_cli_controla_fin_de_entrada():
    agente = AgenteFalso()
    salidas = []

    def finalizar(_mensaje):
        raise EOFError

    ejecutar_cli(
        agente=agente,
        leer=finalizar,
        escribir=salidas.append,
    )

    assert MENSAJE_INICIO in salidas
    assert any(
        "Conversación finalizada" in salida
        for salida in salidas
    )
