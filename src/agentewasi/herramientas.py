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


from .validador_datos import validar_inventario


class ErrorReferenciaProducto(ValueError):
    """Error generado cuando una venta referencia un producto inexistente."""


def _convertir_ranking_a_registros(
    ranking: pd.DataFrame,
) -> list[dict[str, object]]:
    """Convierte un ranking en una respuesta serializable."""

    registros: list[dict[str, object]] = []

    for fila in ranking.itertuples(index=False):
        registros.append(
            {
                "producto_id": str(fila.producto_id),
                "producto": str(fila.producto),
                "categoria": str(fila.categoria),
                "unidades_vendidas": int(fila.unidades_vendidas),
                "ingresos": round(float(fila.ingresos), 2),
            }
        )

    return registros


def obtener_productos_mas_vendidos(
    ventas: pd.DataFrame,
    inventario: pd.DataFrame,
    top_n: int = 5,
    fecha_inicio: str | None = None,
    fecha_fin: str | None = None,
) -> dict[str, object]:
    """Obtiene rankings de productos por unidades e ingresos."""

    validar_ventas(ventas, "ventas")
    validar_inventario(inventario, "inventario")

    if isinstance(top_n, bool) or not isinstance(top_n, int) or top_n <= 0:
        raise ValueError("top_n debe ser un entero mayor que cero")

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
            "top_n": top_n,
            "por_cantidad": [],
            "por_ingresos": [],
            "sin_datos": True,
        }

    productos_ventas = set(seleccion["producto_id"])
    productos_inventario = set(inventario["producto_id"])
    faltantes = sorted(
        productos_ventas - productos_inventario
    )

    if faltantes:
        detalle = ", ".join(faltantes)
        raise ErrorReferenciaProducto(
            f"Productos de ventas no encontrados en inventario: {detalle}"
        )

    seleccion["ingresos"] = (
        seleccion["cantidad"]
        * seleccion["precio_unitario"]
        - seleccion["descuento"]
    )

    resumen = (
        seleccion.groupby(
            "producto_id",
            as_index=False,
        )
        .agg(
            unidades_vendidas=("cantidad", "sum"),
            ingresos=("ingresos", "sum"),
        )
        .merge(
            inventario[
                [
                    "producto_id",
                    "producto",
                    "categoria",
                ]
            ],
            on="producto_id",
            how="left",
            validate="one_to_one",
        )
    )

    resumen["ingresos"] = resumen["ingresos"].round(2)

    por_cantidad = resumen.sort_values(
        [
            "unidades_vendidas",
            "ingresos",
            "producto_id",
        ],
        ascending=[False, False, True],
    ).head(top_n)

    por_ingresos = resumen.sort_values(
        [
            "ingresos",
            "unidades_vendidas",
            "producto_id",
        ],
        ascending=[False, False, True],
    ).head(top_n)

    return {
        "fecha_inicio": fecha_inicial_resultado,
        "fecha_fin": fecha_final_resultado,
        "top_n": top_n,
        "por_cantidad": _convertir_ranking_a_registros(
            por_cantidad
        ),
        "por_ingresos": _convertir_ranking_a_registros(
            por_ingresos
        ),
        "sin_datos": False,
    }


def detectar_stock_critico(
    inventario: pd.DataFrame,
    incluir_normales: bool = False,
) -> dict[str, object]:
    """Clasifica el inventario según su nivel de stock."""

    if not isinstance(incluir_normales, bool):
        raise ValueError(
            "incluir_normales debe ser un valor booleano."
        )

    validar_inventario(
        inventario,
        "inventario_ejemplo.csv",
    )

    resultado = inventario.copy()

    resultado["estado_stock"] = "NORMAL"

    condicion_bajo = (
        (resultado["stock_actual"] > resultado["stock_minimo"])
        & (
            resultado["stock_actual"]
            <= resultado["stock_minimo"] * 1.5
        )
    )

    condicion_critico = (
        (resultado["stock_actual"] > 0)
        & (
            resultado["stock_actual"]
            <= resultado["stock_minimo"]
        )
    )

    condicion_agotado = resultado["stock_actual"] == 0

    resultado.loc[condicion_bajo, "estado_stock"] = "BAJO"
    resultado.loc[condicion_critico, "estado_stock"] = "CRITICO"
    resultado.loc[condicion_agotado, "estado_stock"] = "AGOTADO"

    resultado["faltante_para_minimo"] = (
        resultado["stock_minimo"] - resultado["stock_actual"]
    ).clip(lower=0)

    cantidades = {
        estado: int(
            (resultado["estado_stock"] == estado).sum()
        )
        for estado in (
            "AGOTADO",
            "CRITICO",
            "BAJO",
            "NORMAL",
        )
    }

    prioridad = {
        "AGOTADO": 0,
        "CRITICO": 1,
        "BAJO": 2,
        "NORMAL": 3,
    }

    resultado["_prioridad"] = resultado[
        "estado_stock"
    ].map(prioridad)

    resultado["_proporcion_stock"] = (
        resultado["stock_actual"]
        / resultado["stock_minimo"]
    )

    resultado = resultado.sort_values(
        by=[
            "_prioridad",
            "_proporcion_stock",
            "producto_id",
        ],
        ascending=[True, True, True],
    )

    if not incluir_normales:
        resultado = resultado[
            resultado["estado_stock"] != "NORMAL"
        ]

    columnas_salida = [
        "producto_id",
        "producto",
        "categoria",
        "stock_actual",
        "stock_minimo",
        "estado_stock",
        "faltante_para_minimo",
    ]

    productos = resultado[columnas_salida].to_dict(
        orient="records"
    )

    return {
        "total_productos": int(len(inventario)),
        "total_alertas": int(
            cantidades["AGOTADO"]
            + cantidades["CRITICO"]
            + cantidades["BAJO"]
        ),
        "cantidades_por_estado": cantidades,
        "incluye_normales": incluir_normales,
        "productos": productos,
    }
