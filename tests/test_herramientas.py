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


from agentewasi.herramientas import detectar_stock_critico


def test_detectar_stock_critico_con_inventario_real():
    raiz = Path(__file__).resolve().parents[1]
    inventario = cargar_csv(
        raiz / "data" / "inventario_ejemplo.csv",
        COLUMNAS_INVENTARIO,
    )

    resultado = detectar_stock_critico(inventario)

    assert resultado["total_productos"] == 35
    assert resultado["total_alertas"] == 23
    assert resultado["incluye_normales"] is False
    assert len(resultado["productos"]) == 23

    assert resultado["cantidades_por_estado"] == {
        "AGOTADO": 6,
        "CRITICO": 8,
        "BAJO": 9,
        "NORMAL": 12,
    }


def test_ocultar_productos_normales_por_defecto():
    raiz = Path(__file__).resolve().parents[1]
    inventario = cargar_csv(
        raiz / "data" / "inventario_ejemplo.csv",
        COLUMNAS_INVENTARIO,
    )

    resultado = detectar_stock_critico(inventario)

    estados = {
        producto["estado_stock"]
        for producto in resultado["productos"]
    }

    assert "NORMAL" not in estados
    assert estados == {"AGOTADO", "CRITICO", "BAJO"}


def test_incluir_productos_normales():
    raiz = Path(__file__).resolve().parents[1]
    inventario = cargar_csv(
        raiz / "data" / "inventario_ejemplo.csv",
        COLUMNAS_INVENTARIO,
    )

    resultado = detectar_stock_critico(
        inventario,
        incluir_normales=True,
    )

    assert resultado["incluye_normales"] is True
    assert len(resultado["productos"]) == 35

    estados = [
        producto["estado_stock"]
        for producto in resultado["productos"]
    ]

    assert estados.count("NORMAL") == 12


def test_ordenar_productos_por_prioridad_de_stock():
    raiz = Path(__file__).resolve().parents[1]
    inventario = cargar_csv(
        raiz / "data" / "inventario_ejemplo.csv",
        COLUMNAS_INVENTARIO,
    )

    resultado = detectar_stock_critico(
        inventario,
        incluir_normales=True,
    )

    prioridad = {
        "AGOTADO": 0,
        "CRITICO": 1,
        "BAJO": 2,
        "NORMAL": 3,
    }

    prioridades = [
        prioridad[producto["estado_stock"]]
        for producto in resultado["productos"]
    ]

    assert prioridades == sorted(prioridades)


def test_clasificar_limites_de_stock():
    raiz = Path(__file__).resolve().parents[1]
    inventario = cargar_csv(
        raiz / "data" / "inventario_ejemplo.csv",
        COLUMNAS_INVENTARIO,
    ).copy()

    inventario.loc[0:3, "stock_minimo"] = 10
    inventario.loc[0:3, "stock_actual"] = [0, 10, 15, 16]

    resultado = detectar_stock_critico(
        inventario,
        incluir_normales=True,
    )

    estados = {
        producto["producto_id"]: producto["estado_stock"]
        for producto in resultado["productos"]
    }

    identificadores = inventario.loc[0:3, "producto_id"].tolist()

    assert estados[identificadores[0]] == "AGOTADO"
    assert estados[identificadores[1]] == "CRITICO"
    assert estados[identificadores[2]] == "BAJO"
    assert estados[identificadores[3]] == "NORMAL"


def test_resultado_incluye_codigo_y_nombre_del_producto():
    raiz = Path(__file__).resolve().parents[1]
    inventario = cargar_csv(
        raiz / "data" / "inventario_ejemplo.csv",
        COLUMNAS_INVENTARIO,
    )

    resultado = detectar_stock_critico(inventario)
    producto = resultado["productos"][0]

    assert producto["producto_id"]
    assert producto["producto"]
    assert "categoria" in producto
    assert "estado_stock" in producto


def test_rechazar_incluir_normales_no_booleano():
    raiz = Path(__file__).resolve().parents[1]
    inventario = cargar_csv(
        raiz / "data" / "inventario_ejemplo.csv",
        COLUMNAS_INVENTARIO,
    )

    with pytest.raises(
        ValueError,
        match="incluir_normales debe ser un valor booleano",
    ):
        detectar_stock_critico(
            inventario,
            incluir_normales="sí",
        )


from agentewasi.herramientas import analizar_ventas_por_periodo


def _cargar_datos_para_analisis():
    raiz = Path(__file__).resolve().parents[1]

    ventas = cargar_csv(
        raiz / "data" / "ventas_ejemplo.csv",
        COLUMNAS_VENTAS,
    )
    inventario = cargar_csv(
        raiz / "data" / "inventario_ejemplo.csv",
        COLUMNAS_INVENTARIO,
    )

    return ventas, inventario


def test_analizar_periodo_completo():
    ventas, inventario = _cargar_datos_para_analisis()

    resultado = analizar_ventas_por_periodo(
        ventas,
        inventario,
    )

    assert resultado["fecha_inicio"] == "2026-01-01"
    assert resultado["fecha_fin"] == "2026-08-21"
    assert resultado["sin_datos"] is False

    assert resultado["resumen"]["cantidad_ventas"] == 4571
    assert resultado["resumen"]["cantidad_lineas"] == 10475
    assert resultado["resumen"]["total_ventas"] == 160744.45
    assert len(resultado["por_dia"]) == 233

    assert resultado["categoria_lider"]["categoria"] == "ABARROTES"
    assert resultado["categoria_lider"]["total_ventas"] == 40111.48

    assert resultado["dia_mayor_venta"]["fecha"] == "2026-07-17"
    assert resultado["dia_mayor_venta"]["total_ventas"] == 1224.14


def test_analizar_un_solo_dia():
    ventas, inventario = _cargar_datos_para_analisis()

    resultado = analizar_ventas_por_periodo(
        ventas,
        inventario,
        fecha_inicio="2026-08-21",
        fecha_fin="2026-08-21",
    )

    assert resultado["resumen"]["cantidad_ventas"] == 20
    assert resultado["resumen"]["cantidad_lineas"] == 50
    assert resultado["resumen"]["unidades_vendidas"] == 186
    assert resultado["resumen"]["total_ventas"] == 802.16
    assert len(resultado["por_dia"]) == 1

    assert resultado["categoria_lider"]["categoria"] == "ABARROTES"
    assert resultado["categoria_lider"]["total_ventas"] == 190.31


def test_desglose_por_metodo_de_pago():
    ventas, inventario = _cargar_datos_para_analisis()

    resultado = analizar_ventas_por_periodo(
        ventas,
        inventario,
    )

    metodos = resultado["por_metodo_pago"]

    assert [fila["metodo_pago"] for fila in metodos] == [
        "EFECTIVO",
        "YAPE",
        "PLIN",
        "TARJETA",
    ]

    assert metodos[0]["cantidad_ventas"] == 2047
    assert metodos[0]["total_ventas"] == 71538.67
    assert metodos[0]["porcentaje_ventas"] == 44.5


def test_porcentajes_de_categorias_suman_cien():
    ventas, inventario = _cargar_datos_para_analisis()

    resultado = analizar_ventas_por_periodo(
        ventas,
        inventario,
    )

    porcentaje = sum(
        fila["porcentaje_ventas"]
        for fila in resultado["por_categoria"]
    )

    assert porcentaje == pytest.approx(
        100.0,
        abs=0.05,
    )


def test_resumen_diario_esta_ordenado():
    ventas, inventario = _cargar_datos_para_analisis()

    resultado = analizar_ventas_por_periodo(
        ventas,
        inventario,
    )

    fechas = [
        fila["fecha"]
        for fila in resultado["por_dia"]
    ]

    assert fechas == sorted(fechas)
    assert fechas[0] == "2026-01-01"
    assert fechas[-1] == "2026-08-21"


def test_periodo_sin_datos_devuelve_listas_vacias():
    ventas, inventario = _cargar_datos_para_analisis()

    resultado = analizar_ventas_por_periodo(
        ventas,
        inventario,
        fecha_inicio="2027-01-01",
        fecha_fin="2027-01-31",
    )

    assert resultado["sin_datos"] is True
    assert resultado["resumen"]["total_ventas"] == 0.0
    assert resultado["por_categoria"] == []
    assert resultado["por_metodo_pago"] == []
    assert resultado["por_dia"] == []
    assert resultado["categoria_lider"] is None
    assert resultado["dia_mayor_venta"] is None


def test_analisis_rechaza_producto_sin_referencia():
    ventas, inventario = _cargar_datos_para_analisis()
    ventas_invalidas = ventas.copy()

    ventas_invalidas.loc[
        ventas_invalidas.index[0],
        "producto_id",
    ] = "PROD-999"

    with pytest.raises(
        ErrorReferenciaProducto,
        match="PROD-999",
    ):
        analizar_ventas_por_periodo(
            ventas_invalidas,
            inventario,
        )


from agentewasi.herramientas import recomendar_reposicion


def test_recomendar_reposicion_periodo_completo():
    ventas, inventario = _cargar_datos_para_analisis()

    resultado = recomendar_reposicion(
        ventas,
        inventario,
    )

    assert resultado["fecha_inicio"] == "2026-01-01"
    assert resultado["fecha_fin"] == "2026-08-21"
    assert resultado["dias_periodo"] == 233
    assert resultado["total_recomendaciones"] == 23
    assert resultado["sin_datos_ventas"] is False
    assert "no genera pedidos" in resultado["advertencia"]

    primera = resultado["productos"][0]

    assert primera["producto_id"] == "PROD-005"
    assert primera["producto"] == "Atún en lata 170 g"
    assert primera["estado_stock"] == "AGOTADO"
    assert primera["venta_promedio_diaria"] == 3.5451
    assert primera["stock_objetivo"] == 25
    assert primera["cantidad_sugerida"] == 25


def test_reposicion_incluye_codigo_y_nombre():
    ventas, inventario = _cargar_datos_para_analisis()

    resultado = recomendar_reposicion(
        ventas,
        inventario,
    )

    for producto in resultado["productos"]:
        assert producto["producto_id"]
        assert producto["producto"]
        assert producto["categoria"]
        assert producto["cantidad_sugerida"] >= 0


def test_reposicion_critica_de_leche():
    ventas, inventario = _cargar_datos_para_analisis()

    resultado = recomendar_reposicion(
        ventas,
        inventario,
    )

    leche = next(
        producto
        for producto in resultado["productos"]
        if producto["producto_id"] == "PROD-011"
    )

    assert leche["producto"] == "Leche evaporada 400 g"
    assert leche["estado_stock"] == "CRITICO"
    assert leche["unidades_vendidas"] == 1979
    assert leche["venta_promedio_diaria"] == 8.4936
    assert leche["stock_objetivo"] == 60
    assert leche["cantidad_sugerida"] == 52


def test_reposicion_respeta_prioridad_y_promedio():
    ventas, inventario = _cargar_datos_para_analisis()

    resultado = recomendar_reposicion(
        ventas,
        inventario,
    )

    prioridad = {
        "AGOTADO": 0,
        "CRITICO": 1,
        "BAJO": 2,
    }

    productos = resultado["productos"]

    prioridades = [
        prioridad[producto["estado_stock"]]
        for producto in productos
    ]

    assert prioridades == sorted(prioridades)

    for estado in ("AGOTADO", "CRITICO", "BAJO"):
        promedios = [
            producto["venta_promedio_diaria"]
            for producto in productos
            if producto["estado_stock"] == estado
        ]

        assert promedios == sorted(
            promedios,
            reverse=True,
        )


def test_recomendar_reposicion_de_un_dia():
    ventas, inventario = _cargar_datos_para_analisis()

    resultado = recomendar_reposicion(
        ventas,
        inventario,
        fecha_inicio="2026-08-21",
        fecha_fin="2026-08-21",
    )

    assert resultado["dias_periodo"] == 1
    assert resultado["total_recomendaciones"] == 23

    primera = resultado["productos"][0]

    assert primera["producto_id"] == "PROD-030"
    assert primera["producto"] == "Maní salado 100 g"
    assert primera["unidades_vendidas"] == 6
    assert primera["venta_promedio_diaria"] == 6.0
    assert primera["stock_objetivo"] == 42
    assert primera["cantidad_sugerida"] == 42


def test_reposicion_sin_ventas_usa_stock_minimo():
    ventas, inventario = _cargar_datos_para_analisis()

    resultado = recomendar_reposicion(
        ventas,
        inventario,
        fecha_inicio="2027-01-01",
        fecha_fin="2027-01-31",
    )

    assert resultado["dias_periodo"] == 31
    assert resultado["sin_datos_ventas"] is True
    assert resultado["total_recomendaciones"] == 23

    atun = next(
        producto
        for producto in resultado["productos"]
        if producto["producto_id"] == "PROD-005"
    )

    assert atun["unidades_vendidas"] == 0
    assert atun["venta_promedio_diaria"] == 0.0
    assert atun["stock_objetivo"] == 20
    assert atun["cantidad_sugerida"] == 20


def test_reposicion_rechaza_producto_sin_referencia():
    ventas, inventario = _cargar_datos_para_analisis()
    ventas_invalidas = ventas.copy()

    ventas_invalidas.loc[
        ventas_invalidas.index[0],
        "producto_id",
    ] = "PROD-999"

    with pytest.raises(
        ErrorReferenciaProducto,
        match="PROD-999",
    ):
        recomendar_reposicion(
            ventas_invalidas,
            inventario,
        )


from agentewasi.herramientas import detectar_productos_poca_venta


def test_detectar_productos_poca_venta_periodo_completo():
    ventas, inventario = _cargar_datos_para_analisis()

    resultado = detectar_productos_poca_venta(
        ventas,
        inventario,
    )

    assert resultado["fecha_inicio"] == "2026-01-01"
    assert resultado["fecha_fin"] == "2026-08-21"
    assert resultado["dias_periodo"] == 233
    assert resultado["productos_analizados"] == 35
    assert resultado["total_alertas"] == 5
    assert resultado["sin_datos_ventas"] is False

    assert resultado["cantidades_por_estado"] == {
        "SIN_VENTAS": 2,
        "POCA_VENTA": 3,
        "VENTA_ADECUADA": 30,
    }


def test_productos_con_alerta_coinciden_con_referencia():
    ventas, inventario = _cargar_datos_para_analisis()

    resultado = detectar_productos_poca_venta(
        ventas,
        inventario,
    )

    identificadores = [
        producto["producto_id"]
        for producto in resultado["productos"]
    ]

    assert identificadores == [
        "PROD-025",
        "PROD-035",
        "PROD-030",
        "PROD-021",
        "PROD-024",
    ]


def test_alertas_incluyen_codigo_nombre_y_categoria():
    ventas, inventario = _cargar_datos_para_analisis()

    resultado = detectar_productos_poca_venta(
        ventas,
        inventario,
    )

    for producto in resultado["productos"]:
        assert producto["producto_id"]
        assert producto["producto"]
        assert producto["categoria"]
        assert producto["estado_venta"] in {
            "SIN_VENTAS",
            "POCA_VENTA",
        }


def test_deteccion_de_poca_venta_en_un_dia():
    ventas, inventario = _cargar_datos_para_analisis()

    resultado = detectar_productos_poca_venta(
        ventas,
        inventario,
        fecha_inicio="2026-08-21",
        fecha_fin="2026-08-21",
    )

    assert resultado["dias_periodo"] == 1
    assert resultado["total_alertas"] == 11

    assert resultado["cantidades_por_estado"] == {
        "SIN_VENTAS": 11,
        "POCA_VENTA": 0,
        "VENTA_ADECUADA": 24,
    }


def test_periodo_sin_ventas_clasifica_productos_activos():
    ventas, inventario = _cargar_datos_para_analisis()

    resultado = detectar_productos_poca_venta(
        ventas,
        inventario,
        fecha_inicio="2027-01-01",
        fecha_fin="2027-01-31",
    )

    assert resultado["dias_periodo"] == 31
    assert resultado["sin_datos_ventas"] is True
    assert resultado["productos_analizados"] == 35
    assert resultado["total_alertas"] == 35

    assert resultado["cantidades_por_estado"] == {
        "SIN_VENTAS": 35,
        "POCA_VENTA": 0,
        "VENTA_ADECUADA": 0,
    }


def test_umbral_personalizado_detecta_mas_productos():
    ventas, inventario = _cargar_datos_para_analisis()

    resultado_base = detectar_productos_poca_venta(
        ventas,
        inventario,
    )

    resultado_ampliado = detectar_productos_poca_venta(
        ventas,
        inventario,
        umbral_promedio_diario=3.0,
    )

    assert resultado_ampliado["umbral_promedio_diario"] == 3.0
    assert (
        resultado_ampliado["total_alertas"]
        > resultado_base["total_alertas"]
    )


@pytest.mark.parametrize(
    "umbral_invalido",
    [
        0,
        True,
        "1",
    ],
)
def test_rechazar_umbral_invalido(
    umbral_invalido,
):
    ventas, inventario = _cargar_datos_para_analisis()

    with pytest.raises(
        ValueError,
        match="debe ser un número mayor que cero",
    ):
        detectar_productos_poca_venta(
            ventas,
            inventario,
            umbral_promedio_diario=umbral_invalido,
        )


def test_poca_venta_rechaza_producto_sin_referencia():
    ventas, inventario = _cargar_datos_para_analisis()
    ventas_invalidas = ventas.copy()

    ventas_invalidas.loc[
        ventas_invalidas.index[0],
        "producto_id",
    ] = "PROD-999"

    with pytest.raises(
        ErrorReferenciaProducto,
        match="PROD-999",
    ):
        detectar_productos_poca_venta(
            ventas_invalidas,
            inventario,
        )
