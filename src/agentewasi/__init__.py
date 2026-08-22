"""Herramientas de análisis del proyecto AgenteWasi."""

from .cargador_csv import (
    ErrorCargaCSV,
    ErrorColumnasCSV,
    cargar_csv,
    validar_columnas,
)
from .esquemas import (
    CATEGORIAS_PRODUCTO,
    COLUMNAS_INVENTARIO,
    COLUMNAS_VENTAS,
    METODOS_PAGO,
    UNIDADES_MEDIDA,
    VALORES_BOOLEANOS,
)
from .validador_datos import (
    ErrorDatosCSV,
    validar_campos_obligatorios,
    validar_fechas,
    validar_horas,
    validar_inventario,
    validar_numeros_inventario,
    validar_numeros_ventas,
    validar_valores_permitidos,
    validar_ventas,
)

__all__ = [
    "CATEGORIAS_PRODUCTO",
    "COLUMNAS_INVENTARIO",
    "COLUMNAS_VENTAS",
    "ErrorCargaCSV",
    "ErrorColumnasCSV",
    "ErrorDatosCSV",
    "METODOS_PAGO",
    "UNIDADES_MEDIDA",
    "VALORES_BOOLEANOS",
    "cargar_csv",
    "validar_campos_obligatorios",
    "validar_columnas",
    "validar_fechas",
    "validar_horas",
    "validar_inventario",
    "validar_numeros_inventario",
    "validar_numeros_ventas",
    "validar_valores_permitidos",
    "validar_ventas",
]


from .herramientas import (
    ErrorPeriodoVentas,
    calcular_ventas_totales,
)

__all__.extend(
    [
        "ErrorPeriodoVentas",
        "calcular_ventas_totales",
    ]
)


from .herramientas import (
    ErrorReferenciaProducto,
    obtener_productos_mas_vendidos,
)

__all__.extend(
    [
        "ErrorReferenciaProducto",
        "obtener_productos_mas_vendidos",
    ]
)


from .herramientas import detectar_stock_critico

__all__.append("detectar_stock_critico")


from .herramientas import analizar_ventas_por_periodo

__all__.append("analizar_ventas_por_periodo")


from .herramientas import recomendar_reposicion

__all__.append("recomendar_reposicion")
