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


def analizar_ventas_por_periodo(
    ventas: pd.DataFrame,
    inventario: pd.DataFrame,
    fecha_inicio: str | None = None,
    fecha_fin: str | None = None,
) -> dict[str, object]:
    """Analiza las ventas por categoría, método de pago y día."""

    validar_ventas(ventas, "ventas")
    validar_inventario(inventario, "inventario")

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
            "resumen": {
                "cantidad_ventas": 0,
                "cantidad_lineas": 0,
                "unidades_vendidas": 0,
                "subtotal_bruto": 0.0,
                "descuentos": 0.0,
                "total_ventas": 0.0,
            },
            "por_categoria": [],
            "por_metodo_pago": [],
            "por_dia": [],
            "categoria_lider": None,
            "dia_mayor_venta": None,
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
            "Productos de ventas no encontrados en "
            f"inventario: {detalle}"
        )

    seleccion["subtotal_bruto"] = (
        seleccion["cantidad"]
        * seleccion["precio_unitario"]
    )
    seleccion["total_ventas"] = (
        seleccion["subtotal_bruto"]
        - seleccion["descuento"]
    )

    seleccion = seleccion.merge(
        inventario[
            [
                "producto_id",
                "producto",
                "categoria",
            ]
        ],
        on="producto_id",
        how="left",
        validate="many_to_one",
    )

    resumen_categoria = (
        seleccion.groupby(
            "categoria",
            as_index=False,
        )
        .agg(
            cantidad_ventas=("venta_id", "nunique"),
            unidades_vendidas=("cantidad", "sum"),
            total_ventas=("total_ventas", "sum"),
        )
        .sort_values(
            [
                "total_ventas",
                "unidades_vendidas",
                "categoria",
            ],
            ascending=[False, False, True],
        )
    )

    total_periodo = float(
        seleccion["total_ventas"].sum()
    )

    categorias: list[dict[str, object]] = []

    for fila in resumen_categoria.itertuples(
        index=False
    ):
        categorias.append(
            {
                "categoria": str(fila.categoria),
                "cantidad_ventas": int(
                    fila.cantidad_ventas
                ),
                "unidades_vendidas": int(
                    fila.unidades_vendidas
                ),
                "total_ventas": round(
                    float(fila.total_ventas),
                    2,
                ),
                "porcentaje_ventas": round(
                    float(fila.total_ventas)
                    / total_periodo
                    * 100,
                    2,
                ),
            }
        )

    resumen_pago = (
        seleccion.groupby(
            "metodo_pago",
            as_index=False,
        )
        .agg(
            cantidad_ventas=("venta_id", "nunique"),
            total_ventas=("total_ventas", "sum"),
        )
        .sort_values(
            [
                "total_ventas",
                "metodo_pago",
            ],
            ascending=[False, True],
        )
    )

    metodos_pago: list[dict[str, object]] = []

    for fila in resumen_pago.itertuples(
        index=False
    ):
        metodos_pago.append(
            {
                "metodo_pago": str(fila.metodo_pago),
                "cantidad_ventas": int(
                    fila.cantidad_ventas
                ),
                "total_ventas": round(
                    float(fila.total_ventas),
                    2,
                ),
                "porcentaje_ventas": round(
                    float(fila.total_ventas)
                    / total_periodo
                    * 100,
                    2,
                ),
            }
        )

    resumen_diario = (
        seleccion.groupby(
            "fecha",
            as_index=False,
        )
        .agg(
            cantidad_ventas=("venta_id", "nunique"),
            unidades_vendidas=("cantidad", "sum"),
            total_ventas=("total_ventas", "sum"),
        )
        .sort_values("fecha")
    )

    dias: list[dict[str, object]] = []

    for fila in resumen_diario.itertuples(
        index=False
    ):
        dias.append(
            {
                "fecha": str(fila.fecha),
                "cantidad_ventas": int(
                    fila.cantidad_ventas
                ),
                "unidades_vendidas": int(
                    fila.unidades_vendidas
                ),
                "total_ventas": round(
                    float(fila.total_ventas),
                    2,
                ),
            }
        )

    mejor_dia = resumen_diario.sort_values(
        [
            "total_ventas",
            "cantidad_ventas",
            "fecha",
        ],
        ascending=[False, False, True],
    ).iloc[0]

    resumen = {
        "cantidad_ventas": int(
            seleccion["venta_id"].nunique()
        ),
        "cantidad_lineas": int(len(seleccion)),
        "unidades_vendidas": int(
            seleccion["cantidad"].sum()
        ),
        "subtotal_bruto": round(
            float(seleccion["subtotal_bruto"].sum()),
            2,
        ),
        "descuentos": round(
            float(seleccion["descuento"].sum()),
            2,
        ),
        "total_ventas": round(total_periodo, 2),
    }

    return {
        "fecha_inicio": fecha_inicial_resultado,
        "fecha_fin": fecha_final_resultado,
        "resumen": resumen,
        "por_categoria": categorias,
        "por_metodo_pago": metodos_pago,
        "por_dia": dias,
        "categoria_lider": categorias[0],
        "dia_mayor_venta": {
            "fecha": str(mejor_dia["fecha"]),
            "cantidad_ventas": int(
                mejor_dia["cantidad_ventas"]
            ),
            "unidades_vendidas": int(
                mejor_dia["unidades_vendidas"]
            ),
            "total_ventas": round(
                float(mejor_dia["total_ventas"]),
                2,
            ),
        },
        "sin_datos": False,
    }


from math import ceil


def recomendar_reposicion(
    ventas: pd.DataFrame,
    inventario: pd.DataFrame,
    fecha_inicio: str | None = None,
    fecha_fin: str | None = None,
) -> dict[str, object]:
    """Recomienda cantidades informativas de reposición."""

    validar_ventas(ventas, "ventas")
    validar_inventario(inventario, "inventario")

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
        if inicio is not None and fin is not None:
            dias_periodo = (fin - inicio).days + 1
        else:
            dias_periodo = 0
    else:
        inicio_efectivo = (
            inicio
            if inicio is not None
            else fechas.loc[seleccion.index].min()
        )
        fin_efectivo = (
            fin
            if fin is not None
            else fechas.loc[seleccion.index].max()
        )
        dias_periodo = (
            fin_efectivo - inicio_efectivo
        ).days + 1

    productos_ventas = set(seleccion["producto_id"])
    productos_inventario = set(inventario["producto_id"])
    faltantes = sorted(
        productos_ventas - productos_inventario
    )

    if faltantes:
        detalle = ", ".join(faltantes)
        raise ErrorReferenciaProducto(
            "Productos de ventas no encontrados en "
            f"inventario: {detalle}"
        )

    unidades = (
        seleccion.groupby(
            "producto_id",
            as_index=False,
        )
        .agg(
            unidades_vendidas=("cantidad", "sum"),
        )
    )

    stock = detectar_stock_critico(
        inventario,
        incluir_normales=True,
    )

    estados = pd.DataFrame(stock["productos"])

    resultado = (
        inventario[
            [
                "producto_id",
                "producto",
                "categoria",
                "stock_actual",
                "stock_minimo",
            ]
        ]
        .merge(
            estados[
                [
                    "producto_id",
                    "estado_stock",
                ]
            ],
            on="producto_id",
            how="left",
            validate="one_to_one",
        )
        .merge(
            unidades,
            on="producto_id",
            how="left",
            validate="one_to_one",
        )
    )

    resultado["unidades_vendidas"] = (
        resultado["unidades_vendidas"]
        .fillna(0)
        .astype(int)
    )

    if dias_periodo > 0:
        resultado["venta_promedio_diaria"] = (
            resultado["unidades_vendidas"]
            / dias_periodo
        )
    else:
        resultado["venta_promedio_diaria"] = 0.0

    resultado = resultado[
        resultado["estado_stock"].isin(
            ["AGOTADO", "CRITICO", "BAJO"]
        )
    ].copy()

    resultado["stock_objetivo"] = resultado.apply(
        lambda fila: ceil(
            max(
                float(fila["stock_minimo"]) * 2,
                float(
                    fila["venta_promedio_diaria"]
                ) * 7,
            )
        ),
        axis=1,
    )

    resultado["cantidad_sugerida"] = (
        resultado["stock_objetivo"]
        - resultado["stock_actual"]
    ).clip(lower=0).astype(int)

    prioridad = {
        "AGOTADO": 0,
        "CRITICO": 1,
        "BAJO": 2,
    }

    resultado["_prioridad"] = resultado[
        "estado_stock"
    ].map(prioridad)

    resultado = resultado.sort_values(
        [
            "_prioridad",
            "venta_promedio_diaria",
            "producto_id",
        ],
        ascending=[True, False, True],
    )

    recomendaciones: list[dict[str, object]] = []

    for fila in resultado.itertuples(index=False):
        recomendaciones.append(
            {
                "producto_id": str(fila.producto_id),
                "producto": str(fila.producto),
                "categoria": str(fila.categoria),
                "estado_stock": str(fila.estado_stock),
                "stock_actual": int(fila.stock_actual),
                "stock_minimo": int(fila.stock_minimo),
                "unidades_vendidas": int(
                    fila.unidades_vendidas
                ),
                "venta_promedio_diaria": round(
                    float(fila.venta_promedio_diaria),
                    4,
                ),
                "stock_objetivo": int(
                    fila.stock_objetivo
                ),
                "cantidad_sugerida": int(
                    fila.cantidad_sugerida
                ),
            }
        )

    return {
        "fecha_inicio": fecha_inicial_resultado,
        "fecha_fin": fecha_final_resultado,
        "dias_periodo": int(dias_periodo),
        "total_recomendaciones": int(
            len(recomendaciones)
        ),
        "sin_datos_ventas": seleccion.empty,
        "advertencia": (
            "Recomendación informativa; no genera pedidos "
            "ni modifica el inventario."
        ),
        "productos": recomendaciones,
    }


from math import ceil


def recomendar_reposicion(
    ventas: pd.DataFrame,
    inventario: pd.DataFrame,
    fecha_inicio: str | None = None,
    fecha_fin: str | None = None,
) -> dict[str, object]:
    """Recomienda cantidades informativas de reposición."""

    validar_ventas(ventas, "ventas")
    validar_inventario(inventario, "inventario")

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
        if inicio is not None and fin is not None:
            dias_periodo = (fin - inicio).days + 1
        else:
            dias_periodo = 0
    else:
        inicio_efectivo = (
            inicio
            if inicio is not None
            else fechas.loc[seleccion.index].min()
        )
        fin_efectivo = (
            fin
            if fin is not None
            else fechas.loc[seleccion.index].max()
        )
        dias_periodo = (
            fin_efectivo - inicio_efectivo
        ).days + 1

    productos_ventas = set(seleccion["producto_id"])
    productos_inventario = set(inventario["producto_id"])
    faltantes = sorted(
        productos_ventas - productos_inventario
    )

    if faltantes:
        detalle = ", ".join(faltantes)
        raise ErrorReferenciaProducto(
            "Productos de ventas no encontrados en "
            f"inventario: {detalle}"
        )

    unidades = (
        seleccion.groupby(
            "producto_id",
            as_index=False,
        )
        .agg(
            unidades_vendidas=("cantidad", "sum"),
        )
    )

    stock = detectar_stock_critico(
        inventario,
        incluir_normales=True,
    )

    estados = pd.DataFrame(stock["productos"])

    resultado = (
        inventario[
            [
                "producto_id",
                "producto",
                "categoria",
                "stock_actual",
                "stock_minimo",
            ]
        ]
        .merge(
            estados[
                [
                    "producto_id",
                    "estado_stock",
                ]
            ],
            on="producto_id",
            how="left",
            validate="one_to_one",
        )
        .merge(
            unidades,
            on="producto_id",
            how="left",
            validate="one_to_one",
        )
    )

    resultado["unidades_vendidas"] = (
        resultado["unidades_vendidas"]
        .fillna(0)
        .astype(int)
    )

    if dias_periodo > 0:
        resultado["venta_promedio_diaria"] = (
            resultado["unidades_vendidas"]
            / dias_periodo
        )
    else:
        resultado["venta_promedio_diaria"] = 0.0

    resultado = resultado[
        resultado["estado_stock"].isin(
            ["AGOTADO", "CRITICO", "BAJO"]
        )
    ].copy()

    resultado["stock_objetivo"] = resultado.apply(
        lambda fila: ceil(
            max(
                float(fila["stock_minimo"]) * 2,
                float(
                    fila["venta_promedio_diaria"]
                ) * 7,
            )
        ),
        axis=1,
    )

    resultado["cantidad_sugerida"] = (
        resultado["stock_objetivo"]
        - resultado["stock_actual"]
    ).clip(lower=0).astype(int)

    prioridad = {
        "AGOTADO": 0,
        "CRITICO": 1,
        "BAJO": 2,
    }

    resultado["_prioridad"] = resultado[
        "estado_stock"
    ].map(prioridad)

    resultado = resultado.sort_values(
        [
            "_prioridad",
            "venta_promedio_diaria",
            "producto_id",
        ],
        ascending=[True, False, True],
    )

    recomendaciones: list[dict[str, object]] = []

    for fila in resultado.itertuples(index=False):
        recomendaciones.append(
            {
                "producto_id": str(fila.producto_id),
                "producto": str(fila.producto),
                "categoria": str(fila.categoria),
                "estado_stock": str(fila.estado_stock),
                "stock_actual": int(fila.stock_actual),
                "stock_minimo": int(fila.stock_minimo),
                "unidades_vendidas": int(
                    fila.unidades_vendidas
                ),
                "venta_promedio_diaria": round(
                    float(fila.venta_promedio_diaria),
                    4,
                ),
                "stock_objetivo": int(
                    fila.stock_objetivo
                ),
                "cantidad_sugerida": int(
                    fila.cantidad_sugerida
                ),
            }
        )

    return {
        "fecha_inicio": fecha_inicial_resultado,
        "fecha_fin": fecha_final_resultado,
        "dias_periodo": int(dias_periodo),
        "total_recomendaciones": int(
            len(recomendaciones)
        ),
        "sin_datos_ventas": seleccion.empty,
        "advertencia": (
            "Recomendación informativa; no genera pedidos "
            "ni modifica el inventario."
        ),
        "productos": recomendaciones,
    }


def detectar_productos_poca_venta(
    ventas: pd.DataFrame,
    inventario: pd.DataFrame,
    fecha_inicio: str | None = None,
    fecha_fin: str | None = None,
    umbral_promedio_diario: float = 1.0,
) -> dict[str, object]:
    """Detecta productos activos con poca o ninguna venta."""

    validar_ventas(ventas, "ventas")
    validar_inventario(inventario, "inventario")

    if isinstance(umbral_promedio_diario, bool):
        raise ValueError(
            "umbral_promedio_diario debe ser un número mayor que cero"
        )

    if not isinstance(
        umbral_promedio_diario,
        (int, float),
    ) or umbral_promedio_diario <= 0:
        raise ValueError(
            "umbral_promedio_diario debe ser un número mayor que cero"
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
        if inicio is not None and fin is not None:
            dias_periodo = (fin - inicio).days + 1
        else:
            dias_periodo = 0
    else:
        inicio_efectivo = (
            inicio
            if inicio is not None
            else fechas.loc[seleccion.index].min()
        )
        fin_efectivo = (
            fin
            if fin is not None
            else fechas.loc[seleccion.index].max()
        )
        dias_periodo = (
            fin_efectivo - inicio_efectivo
        ).days + 1

    productos_ventas = set(seleccion["producto_id"])
    productos_inventario = set(inventario["producto_id"])
    faltantes = sorted(
        productos_ventas - productos_inventario
    )

    if faltantes:
        detalle = ", ".join(faltantes)
        raise ErrorReferenciaProducto(
            "Productos de ventas no encontrados en "
            f"inventario: {detalle}"
        )

    unidades = (
        seleccion.groupby(
            "producto_id",
            as_index=False,
        )
        .agg(
            unidades_vendidas=("cantidad", "sum"),
        )
    )

    productos_activos = inventario[
        inventario["activo"] == True  # noqa: E712
    ][
        [
            "producto_id",
            "producto",
            "categoria",
        ]
    ].copy()

    resultado = productos_activos.merge(
        unidades,
        on="producto_id",
        how="left",
        validate="one_to_one",
    )

    resultado["unidades_vendidas"] = (
        resultado["unidades_vendidas"]
        .fillna(0)
        .astype(int)
    )

    if dias_periodo > 0:
        resultado["venta_promedio_diaria"] = (
            resultado["unidades_vendidas"]
            / dias_periodo
        )
    else:
        resultado["venta_promedio_diaria"] = 0.0

    resultado["estado_venta"] = "VENTA_ADECUADA"

    resultado.loc[
        (
            resultado["unidades_vendidas"] > 0
        )
        & (
            resultado["venta_promedio_diaria"]
            < float(umbral_promedio_diario)
        ),
        "estado_venta",
    ] = "POCA_VENTA"

    resultado.loc[
        resultado["unidades_vendidas"] == 0,
        "estado_venta",
    ] = "SIN_VENTAS"

    cantidades = {
        estado: int(
            (resultado["estado_venta"] == estado).sum()
        )
        for estado in (
            "SIN_VENTAS",
            "POCA_VENTA",
            "VENTA_ADECUADA",
        )
    }

    alertas = resultado[
        resultado["estado_venta"].isin(
            ["SIN_VENTAS", "POCA_VENTA"]
        )
    ].copy()

    prioridad = {
        "SIN_VENTAS": 0,
        "POCA_VENTA": 1,
    }

    alertas["_prioridad"] = alertas[
        "estado_venta"
    ].map(prioridad)

    alertas = alertas.sort_values(
        [
            "_prioridad",
            "venta_promedio_diaria",
            "producto_id",
        ],
        ascending=[True, True, True],
    )

    productos: list[dict[str, object]] = []

    for fila in alertas.itertuples(index=False):
        productos.append(
            {
                "producto_id": str(fila.producto_id),
                "producto": str(fila.producto),
                "categoria": str(fila.categoria),
                "unidades_vendidas": int(
                    fila.unidades_vendidas
                ),
                "venta_promedio_diaria": round(
                    float(fila.venta_promedio_diaria),
                    4,
                ),
                "estado_venta": str(fila.estado_venta),
            }
        )

    return {
        "fecha_inicio": fecha_inicial_resultado,
        "fecha_fin": fecha_final_resultado,
        "dias_periodo": int(dias_periodo),
        "umbral_promedio_diario": float(
            umbral_promedio_diario
        ),
        "productos_analizados": int(len(resultado)),
        "total_alertas": int(len(productos)),
        "cantidades_por_estado": cantidades,
        "sin_datos_ventas": seleccion.empty,
        "productos": productos,
    }


class ErrorReferenciaCliente(ValueError):
    """Error cuando un cliente tiene referencias inconsistentes."""


def analizar_clientes(
    ventas: pd.DataFrame,
    top_n: int = 5,
    fecha_inicio: str | None = None,
    fecha_fin: str | None = None,
) -> dict[str, object]:
    """Calcula indicadores de clientes ficticios por periodo."""

    validar_ventas(ventas, "ventas")

    if isinstance(top_n, bool) or not isinstance(top_n, int) or top_n <= 0:
        raise ValueError(
            "top_n debe ser un entero mayor que cero"
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
            "top_n": top_n,
            "cantidad_clientes": 0,
            "clientes_recurrentes": 0,
            "porcentaje_clientes_recurrentes": 0.0,
            "cantidad_compras": 0,
            "gasto_total": 0.0,
            "ticket_promedio_general": 0.0,
            "por_numero_compras": [],
            "por_gasto_acumulado": [],
            "clientes": [],
            "sin_datos": True,
        }

    nombres_por_cliente = (
        seleccion.groupby("cliente_id")[
            "cliente_nombre"
        ]
        .nunique()
    )

    inconsistentes = sorted(
        nombres_por_cliente[
            nombres_por_cliente > 1
        ].index.tolist()
    )

    if inconsistentes:
        detalle = ", ".join(inconsistentes)
        raise ErrorReferenciaCliente(
            "Clientes con más de un nombre asociado: "
            f"{detalle}"
        )

    seleccion["gasto"] = (
        seleccion["cantidad"]
        * seleccion["precio_unitario"]
        - seleccion["descuento"]
    )

    resumen = (
        seleccion.groupby(
            [
                "cliente_id",
                "cliente_nombre",
            ],
            as_index=False,
        )
        .agg(
            numero_compras=("venta_id", "nunique"),
            gasto_acumulado=("gasto", "sum"),
        )
    )

    resumen["ticket_promedio"] = (
        resumen["gasto_acumulado"]
        / resumen["numero_compras"]
    )

    resumen["es_recurrente"] = (
        resumen["numero_compras"] >= 2
    )

    resumen["gasto_acumulado"] = (
        resumen["gasto_acumulado"].round(2)
    )
    resumen["ticket_promedio"] = (
        resumen["ticket_promedio"].round(2)
    )

    def convertir_clientes(
        datos: pd.DataFrame,
    ) -> list[dict[str, object]]:
        registros: list[dict[str, object]] = []

        for fila in datos.itertuples(index=False):
            registros.append(
                {
                    "cliente_id": str(fila.cliente_id),
                    "cliente_nombre": str(
                        fila.cliente_nombre
                    ),
                    "numero_compras": int(
                        fila.numero_compras
                    ),
                    "gasto_acumulado": round(
                        float(fila.gasto_acumulado),
                        2,
                    ),
                    "ticket_promedio": round(
                        float(fila.ticket_promedio),
                        2,
                    ),
                    "es_recurrente": bool(
                        fila.es_recurrente
                    ),
                }
            )

        return registros

    por_compras = resumen.sort_values(
        [
            "numero_compras",
            "gasto_acumulado",
            "cliente_id",
        ],
        ascending=[False, False, True],
    ).head(top_n)

    por_gasto = resumen.sort_values(
        [
            "gasto_acumulado",
            "numero_compras",
            "cliente_id",
        ],
        ascending=[False, False, True],
    ).head(top_n)

    todos_clientes = resumen.sort_values(
        "cliente_id"
    )

    cantidad_compras = int(
        seleccion["venta_id"].nunique()
    )
    gasto_total = round(
        float(seleccion["gasto"].sum()),
        2,
    )
    clientes_recurrentes = int(
        resumen["es_recurrente"].sum()
    )
    cantidad_clientes = int(len(resumen))

    porcentaje_recurrentes = round(
        clientes_recurrentes
        / cantidad_clientes
        * 100,
        2,
    )

    ticket_promedio_general = round(
        gasto_total / cantidad_compras,
        2,
    )

    return {
        "fecha_inicio": fecha_inicial_resultado,
        "fecha_fin": fecha_final_resultado,
        "top_n": top_n,
        "cantidad_clientes": cantidad_clientes,
        "clientes_recurrentes": clientes_recurrentes,
        "porcentaje_clientes_recurrentes": (
            porcentaje_recurrentes
        ),
        "cantidad_compras": cantidad_compras,
        "gasto_total": gasto_total,
        "ticket_promedio_general": (
            ticket_promedio_general
        ),
        "por_numero_compras": convertir_clientes(
            por_compras
        ),
        "por_gasto_acumulado": convertir_clientes(
            por_gasto
        ),
        "clientes": convertir_clientes(
            todos_clientes
        ),
        "sin_datos": False,
    }
