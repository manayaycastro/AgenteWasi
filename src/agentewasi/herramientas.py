"""Herramientas deterministas de análisis para AgenteWasi."""

from datetime import date

import pandas as pd

from .validador_datos import validar_ventas


class ErrorPeriodoVentas(ValueError):
    """Error generado cuando el periodo solicitado es inválido."""


def _convertir_fecha_parametro(
    valor: str | None,
    nombre: str,
) -> date | None:
    """Convierte un parámetro ISO a fecha de manera estricta."""

    if valor is None:
        return None

    if not isinstance(valor, str):
        raise ErrorPeriodoVentas(
            f"{nombre} debe ser texto con formato AAAA-MM-DD"
        )

    try:
        fecha = date.fromisoformat(valor)
    except ValueError as error:
        raise ErrorPeriodoVentas(
            f"{nombre} debe tener formato AAAA-MM-DD: {valor}"
        ) from error

    if fecha.isoformat() != valor:
        raise ErrorPeriodoVentas(
            f"{nombre} debe tener formato AAAA-MM-DD: {valor}"
        )

    return fecha


def calcular_ventas_totales(
    ventas: pd.DataFrame,
    fecha_inicio: str | None = None,
    fecha_fin: str | None = None,
) -> dict[str, object]:
    """Calcula importes y cantidades de ventas para un periodo."""

    validar_ventas(
        ventas,
        nombre_archivo="ventas",
    )

    inicio = _convertir_fecha_parametro(
        fecha_inicio,
        "fecha_inicio",
    )
    fin = _convertir_fecha_parametro(
        fecha_fin,
        "fecha_fin",
    )

    if inicio is not None and fin is not None and inicio > fin:
        raise ErrorPeriodoVentas(
            "fecha_inicio no puede ser posterior a fecha_fin"
        )

    fechas = pd.to_datetime(
        ventas["fecha"],
        format="%Y-%m-%d",
    ).dt.date

    mascara = pd.Series(True, index=ventas.index)

    if inicio is not None:
        mascara &= fechas >= inicio

    if fin is not None:
        mascara &= fechas <= fin

    seleccion = ventas.loc[mascara].copy()

    fecha_inicial_resultado = (
        fecha_inicio
        if fecha_inicio is not None
        else str(ventas["fecha"].min())
    )
    fecha_final_resultado = (
        fecha_fin
        if fecha_fin is not None
        else str(ventas["fecha"].max())
    )

    if seleccion.empty:
        return {
            "fecha_inicio": fecha_inicial_resultado,
            "fecha_fin": fecha_final_resultado,
            "cantidad_ventas": 0,
            "cantidad_lineas": 0,
            "subtotal_bruto": 0.0,
            "descuentos": 0.0,
            "total_ventas": 0.0,
            "sin_datos": True,
        }

    subtotal = (
        seleccion["cantidad"]
        * seleccion["precio_unitario"]
    )
    descuentos = seleccion["descuento"]
    total = subtotal - descuentos

    return {
        "fecha_inicio": fecha_inicial_resultado,
        "fecha_fin": fecha_final_resultado,
        "cantidad_ventas": int(
            seleccion["venta_id"].nunique()
        ),
        "cantidad_lineas": int(len(seleccion)),
        "subtotal_bruto": round(float(subtotal.sum()), 2),
        "descuentos": round(float(descuentos.sum()), 2),
        "total_ventas": round(float(total.sum()), 2),
        "sin_datos": False,
    }
