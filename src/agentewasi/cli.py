"""Interfaz de consola de AgenteWasi."""

from collections.abc import Callable

from openai import OpenAIError

from .agente import AgenteWasi


MENSAJE_INICIO = """
AgenteWasi - Analista del minimarket
------------------------------------
Puedes preguntar por ventas, productos, inventario, reposición,
categorías y clientes ficticios.

Ejemplos:
- ¿Cuánto se vendió el 21 de agosto de 2026?
- ¿Cuáles fueron los productos más vendidos?
- ¿Qué productos tienen stock crítico?
- ¿Qué productos debo reponer?
- ¿Quiénes son los clientes con más compras?

Escribe salir para finalizar.
""".strip()


def ejecutar_cli(
    agente: AgenteWasi | None = None,
    leer: Callable[[str], str] = input,
    escribir: Callable[[str], None] = print,
) -> None:
    """Ejecuta una conversación interactiva por consola."""

    instancia = (
        agente
        if agente is not None
        else AgenteWasi()
    )

    escribir(MENSAJE_INICIO)

    while True:
        try:
            pregunta = leer("\nTú: ").strip()
        except (EOFError, KeyboardInterrupt):
            escribir("\nAgenteWasi: Conversación finalizada.")
            return

        if pregunta.lower() in {
            "salir",
            "exit",
            "quit",
        }:
            escribir("AgenteWasi: Conversación finalizada.")
            return

        if not pregunta:
            escribir(
                "AgenteWasi: Escribe una pregunta "
                "o utiliza salir."
            )
            continue

        try:
            respuesta = instancia.preguntar(pregunta)
        except OpenAIError:
            escribir(
                "AgenteWasi: No se pudo contactar al servicio "
                "de inteligencia artificial. Inténtalo nuevamente."
            )
            continue
        except ValueError as error:
            escribir(f"AgenteWasi: {error}")
            continue
        except RuntimeError as error:
            escribir(
                "AgenteWasi: No se pudo completar la consulta. "
                f"{error}"
            )
            continue

        escribir(f"\nAgenteWasi: {respuesta}")


def main() -> None:
    """Punto de entrada de la aplicación."""

    try:
        ejecutar_cli()
    except Exception as error:
        print(
            "No se pudo iniciar AgenteWasi: "
            f"{error}"
        )


if __name__ == "__main__":
    main()
