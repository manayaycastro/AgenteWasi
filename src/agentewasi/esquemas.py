"""Columnas obligatorias de los archivos utilizados por AgenteWasi."""

COLUMNAS_VENTAS = (
    "venta_id",
    "fecha",
    "hora",
    "cliente_id",
    "cliente_nombre",
    "producto_id",
    "cantidad",
    "precio_unitario",
    "descuento",
    "metodo_pago",
)

COLUMNAS_INVENTARIO = (
    "producto_id",
    "producto",
    "categoria",
    "unidad_medida",
    "precio_venta_actual",
    "stock_actual",
    "stock_minimo",
    "activo",
)


METODOS_PAGO = frozenset(
    {
        "EFECTIVO",
        "YAPE",
        "PLIN",
        "TARJETA",
    }
)

CATEGORIAS_PRODUCTO = frozenset(
    {
        "ABARROTES",
        "BEBIDAS",
        "CUIDADO_PERSONAL",
        "LACTEOS",
        "LIMPIEZA",
        "PANADERIA",
        "SNACKS",
    }
)

UNIDADES_MEDIDA = frozenset(
    {
        "UNIDAD",
        "PAQUETE",
        "BOTELLA",
        "BOLSA",
        "LATA",
        "CAJA",
    }
)

VALORES_BOOLEANOS = frozenset(
    {
        "TRUE",
        "FALSE",
    }
)
