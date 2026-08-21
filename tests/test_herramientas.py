"""Pruebas para las herramientas de análisis de AgenteWasi."""

from pathlib import Path

import pytest

from agentewasi import COLUMNAS_VENTAS, cargar_csv
from agentewasi.herramientas import (
    ErrorPeriodoVentas,
    calcular_ventas_totales,
)


@pytest.fixture(scope="module")
def ventas_reales():
    raiz = Path(__file__).resolve().parents[1]
    archivo = raiz / "data" / "ventas_ejemplo.csv"

    return cargar_csv(
        archivo,
        COLUMNAS_VENTAS,
    )


def test_calcular_total_de_todo_el_periodo(ventas_reales):
    resultado = calcular_ventas_totales(ventas_reales)

    assert resultado["fecha_inicio"] == "2026-01-01"
    assert resultado["fecha_fin"] == "2026-08-21"
    assert resultado["cantidad_ventas"] == 4571
    assert resultado["cantidad_lineas"] == 10475
    assert resultado["subtotal_bruto"] == pytest.approx(162130.55)
    assert resultado["descuentos"] == pytest.approx(1386.10)
    assert resultado["total_ventas"] == pytest.approx(160744.45)
    assert resultado["sin_datos"] is False


def test_calcular_total_de_un_dia(ventas_reales):
    resultado = calcular_ventas_totales(
        ventas_reales,
        fecha_inicio="2026-08-21",
        fecha_fin="2026-08-21",
    )

    assert resultado["cantidad_ventas"] == 20
    assert resultado["cantidad_lineas"] == 50
    assert resultado["total_ventas"] == pytest.approx(802.16)


def test_calcular_total_de_un_rango(ventas_reales):
    resultado = calcular_ventas_totales(
        ventas_reales,
        fecha_inicio="2026-08-01",
        fecha_fin="2026-08-21",
    )

    assert resultado["cantidad_ventas"] == 401
    assert resultado["cantidad_lineas"] == 949
    assert resultado["subtotal_bruto"] == pytest.approx(15956.30)
    assert resultado["descuentos"] == pytest.approx(139.77)
    assert resultado["total_ventas"] == pytest.approx(15816.53)


def test_periodo_sin_datos_devuelve_ceros(ventas_reales):
    resultado = calcular_ventas_totales(
        ventas_reales,
        fecha_inicio="2026-09-01",
        fecha_fin="2026-09-30",
    )

    assert resultado["cantidad_ventas"] == 0
    assert resultado["cantidad_lineas"] == 0
    assert resultado["total_ventas"] == 0.0
    assert resultado["sin_datos"] is True


def test_rechazar_formato_de_fecha_invalido(ventas_reales):
    with pytest.raises(
        ErrorPeriodoVentas,
        match="formato AAAA-MM-DD",
    ):
        calcular_ventas_totales(
            ventas_reales,
            fecha_inicio="21/08/2026",
        )


def test_rechazar_periodo_invertido(ventas_reales):
    with pytest.raises(
        ErrorPeriodoVentas,
        match="fecha_inicio no puede ser posterior",
    ):
        calcular_ventas_totales(
            ventas_reales,
            fecha_inicio="2026-08-21",
            fecha_fin="2026-08-01",
        )
