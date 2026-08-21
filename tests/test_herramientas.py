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


from agentewasi import COLUMNAS_INVENTARIO
from agentewasi.herramientas import (
    ErrorReferenciaProducto,
    obtener_productos_mas_vendidos,
)


@pytest.fixture(scope="module")
def inventario_real():
    raiz = Path(__file__).resolve().parents[1]
    archivo = raiz / "data" / "inventario_ejemplo.csv"

    return cargar_csv(
        archivo,
        COLUMNAS_INVENTARIO,
    )


def test_ranking_completo_incluye_codigo_y_nombre(
    ventas_reales,
    inventario_real,
):
    resultado = obtener_productos_mas_vendidos(
        ventas_reales,
        inventario_real,
        top_n=5,
    )

    primero_cantidad = resultado["por_cantidad"][0]
    primero_ingresos = resultado["por_ingresos"][0]

    assert primero_cantidad["producto_id"] == "PROD-031"
    assert primero_cantidad["producto"] == "Pan francés"
    assert primero_cantidad["unidades_vendidas"] == 7964

    assert primero_ingresos["producto_id"] == "PROD-003"
    assert primero_ingresos["producto"] == "Aceite vegetal 1 L"
    assert primero_ingresos["ingresos"] == pytest.approx(13549.75)


def test_ranking_diario_respeta_top_n(
    ventas_reales,
    inventario_real,
):
    resultado = obtener_productos_mas_vendidos(
        ventas_reales,
        inventario_real,
        top_n=3,
        fecha_inicio="2026-08-21",
        fecha_fin="2026-08-21",
    )

    nombres = [
        fila["producto"]
        for fila in resultado["por_cantidad"]
    ]

    assert nombres == [
        "Azúcar rubia 1 kg",
        "Gaseosa cola 500 ml",
        "Papas fritas 45 g",
    ]
    assert len(resultado["por_ingresos"]) == 3


def test_ranking_sin_datos_devuelve_listas_vacias(
    ventas_reales,
    inventario_real,
):
    resultado = obtener_productos_mas_vendidos(
        ventas_reales,
        inventario_real,
        fecha_inicio="2026-09-01",
        fecha_fin="2026-09-30",
    )

    assert resultado["por_cantidad"] == []
    assert resultado["por_ingresos"] == []
    assert resultado["sin_datos"] is True


@pytest.mark.parametrize("top_n", [0, True])
def test_rechazar_top_n_invalido(
    ventas_reales,
    inventario_real,
    top_n,
):
    with pytest.raises(
        ValueError,
        match="top_n debe ser un entero mayor que cero",
    ):
        obtener_productos_mas_vendidos(
            ventas_reales,
            inventario_real,
            top_n=top_n,
        )


def test_rechazar_producto_sin_referencia(
    ventas_reales,
    inventario_real,
):
    ventas_invalidas = ventas_reales.copy()
    ventas_invalidas.loc[
        ventas_invalidas.index[0],
        "producto_id",
    ] = "PROD-999"

    with pytest.raises(
        ErrorReferenciaProducto,
        match="PROD-999",
    ):
        obtener_productos_mas_vendidos(
            ventas_invalidas,
            inventario_real,
        )
