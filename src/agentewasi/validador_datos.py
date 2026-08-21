"""Validaciones de calidad para los datos de AgenteWasi."""

from collections.abc import Collection

import pandas as pd

from .cargador_csv import validar_columnas


class ErrorDatosCSV(ValueError):
    """Error generado cuando los datos incumplen una regla de calidad."""


def validar_campos_obligatorios(
    datos: pd.DataFrame,
    columnas_obligatorias: Collection[str],
    nombre_archivo: str = "archivo CSV",
) -> None:
    """Verifica columnas existentes y campos obligatorios no vacíos."""

    validar_columnas(
        datos,
        columnas_obligatorias,
        nombre_archivo,
    )

    errores: list[str] = []

    for columna in columnas_obligatorias:
        valores = datos[columna]
        vacios = valores.isna() | valores.astype("string").str.strip().eq("")

        if vacios.any():
            filas = (datos.index[vacios] + 2).tolist()
            detalle_filas = ", ".join(map(str, filas))
            errores.append(
                f"{columna} en filas {detalle_filas}"
            )

    if errores:
        detalle = "; ".join(errores)
        raise ErrorDatosCSV(
            f"Campos obligatorios vacíos en {nombre_archivo}: {detalle}"
        )


def _filas_csv(mascara: pd.Series) -> str:
    """Convierte índices de DataFrame en números de fila del CSV."""

    filas = (mascara.index[mascara] + 2).tolist()
    return ", ".join(map(str, filas))


def validar_fechas(
    datos: pd.DataFrame,
    columna: str = "fecha",
    fecha_minima: str | None = None,
    fecha_maxima: str | None = None,
    nombre_archivo: str = "archivo CSV",
) -> None:
    """Valida formato ISO y límites permitidos para una fecha."""

    valores = datos[columna].astype("string")
    formato_iso = valores.str.fullmatch(
        r"\d{4}-\d{2}-\d{2}",
        na=False,
    )
    fechas = pd.to_datetime(
        valores,
        format="%Y-%m-%d",
        errors="coerce",
    )

    invalidas = ~formato_iso | fechas.isna()

    if invalidas.any():
        filas = _filas_csv(invalidas)
        raise ErrorDatosCSV(
            f"Fechas inválidas en {nombre_archivo}, "
            f"columna {columna}, filas {filas}"
        )

    fuera_periodo = pd.Series(False, index=datos.index)

    if fecha_minima is not None:
        fuera_periodo |= fechas < pd.Timestamp(fecha_minima)

    if fecha_maxima is not None:
        fuera_periodo |= fechas > pd.Timestamp(fecha_maxima)

    if fuera_periodo.any():
        filas = _filas_csv(fuera_periodo)
        raise ErrorDatosCSV(
            f"Fechas fuera del periodo permitido en "
            f"{nombre_archivo}, filas {filas}"
        )


def validar_horas(
    datos: pd.DataFrame,
    columna: str = "hora",
    nombre_archivo: str = "archivo CSV",
) -> None:
    """Valida horas en formato de 24 horas HH:MM:SS."""

    valores = datos[columna].astype("string")
    formato_hora = valores.str.fullmatch(
        r"\d{2}:\d{2}:\d{2}",
        na=False,
    )
    horas = pd.to_datetime(
        valores,
        format="%H:%M:%S",
        errors="coerce",
    )

    invalidas = ~formato_hora | horas.isna()

    if invalidas.any():
        filas = _filas_csv(invalidas)
        raise ErrorDatosCSV(
            f"Horas inválidas en {nombre_archivo}, "
            f"columna {columna}, filas {filas}"
        )


def _convertir_numeros(
    datos: pd.DataFrame,
    columna: str,
    nombre_archivo: str,
) -> pd.Series:
    """Convierte una columna a número o informa las filas inválidas."""

    numeros = pd.to_numeric(
        datos[columna],
        errors="coerce",
    )
    invalidos = numeros.isna()

    if invalidos.any():
        filas = _filas_csv(invalidos)
        raise ErrorDatosCSV(
            f"Valores no numéricos en {nombre_archivo}, "
            f"columna {columna}, filas {filas}"
        )

    return numeros


def _validar_regla_numerica(
    mascara: pd.Series,
    regla: str,
    columna: str,
    nombre_archivo: str,
) -> None:
    """Genera un error indicando la regla numérica incumplida."""

    if mascara.any():
        filas = _filas_csv(mascara)
        raise ErrorDatosCSV(
            f"{regla} en {nombre_archivo}, "
            f"columna {columna}, filas {filas}"
        )


def _validar_maximo_dos_decimales(
    datos: pd.DataFrame,
    columna: str,
    nombre_archivo: str,
) -> None:
    """Valida números con un máximo de dos posiciones decimales."""

    valores = datos[columna].astype("string").str.strip()
    formato_valido = valores.str.fullmatch(
        r"-?\d+(?:\.\d{1,2})?",
        na=False,
    )
    invalidos = ~formato_valido

    _validar_regla_numerica(
        invalidos,
        "Se permiten como máximo dos decimales",
        columna,
        nombre_archivo,
    )


def validar_numeros_ventas(
    datos: pd.DataFrame,
    nombre_archivo: str = "ventas.csv",
) -> None:
    """Valida cantidad, precio y descuento de las ventas."""

    cantidad = _convertir_numeros(
        datos,
        "cantidad",
        nombre_archivo,
    )
    precio = _convertir_numeros(
        datos,
        "precio_unitario",
        nombre_archivo,
    )
    descuento = _convertir_numeros(
        datos,
        "descuento",
        nombre_archivo,
    )

    _validar_regla_numerica(
        cantidad.mod(1).ne(0),
        "La cantidad debe ser un entero",
        "cantidad",
        nombre_archivo,
    )
    _validar_regla_numerica(
        cantidad.le(0),
        "La cantidad debe ser mayor que cero",
        "cantidad",
        nombre_archivo,
    )
    _validar_regla_numerica(
        precio.le(0),
        "El precio debe ser mayor que cero",
        "precio_unitario",
        nombre_archivo,
    )
    _validar_regla_numerica(
        descuento.lt(0),
        "El descuento no puede ser negativo",
        "descuento",
        nombre_archivo,
    )

    _validar_maximo_dos_decimales(
        datos,
        "precio_unitario",
        nombre_archivo,
    )
    _validar_maximo_dos_decimales(
        datos,
        "descuento",
        nombre_archivo,
    )

    subtotal = cantidad * precio
    _validar_regla_numerica(
        descuento.ge(subtotal),
        "El descuento debe ser menor que el subtotal",
        "descuento",
        nombre_archivo,
    )


def validar_numeros_inventario(
    datos: pd.DataFrame,
    nombre_archivo: str = "inventario.csv",
) -> None:
    """Valida precios y cantidades del inventario."""

    precio = _convertir_numeros(
        datos,
        "precio_venta_actual",
        nombre_archivo,
    )
    stock_actual = _convertir_numeros(
        datos,
        "stock_actual",
        nombre_archivo,
    )
    stock_minimo = _convertir_numeros(
        datos,
        "stock_minimo",
        nombre_archivo,
    )

    _validar_regla_numerica(
        precio.le(0),
        "El precio debe ser mayor que cero",
        "precio_venta_actual",
        nombre_archivo,
    )
    _validar_maximo_dos_decimales(
        datos,
        "precio_venta_actual",
        nombre_archivo,
    )

    _validar_regla_numerica(
        stock_actual.mod(1).ne(0),
        "El stock actual debe ser un entero",
        "stock_actual",
        nombre_archivo,
    )
    _validar_regla_numerica(
        stock_actual.lt(0),
        "El stock actual no puede ser negativo",
        "stock_actual",
        nombre_archivo,
    )
    _validar_regla_numerica(
        stock_minimo.mod(1).ne(0),
        "El stock mínimo debe ser un entero",
        "stock_minimo",
        nombre_archivo,
    )
    _validar_regla_numerica(
        stock_minimo.le(0),
        "El stock mínimo debe ser mayor que cero",
        "stock_minimo",
        nombre_archivo,
    )


def validar_valores_permitidos(
    datos: pd.DataFrame,
    columna: str,
    valores_permitidos: Collection[str],
    nombre_archivo: str = "archivo CSV",
) -> None:
    """Valida una columna categórica contra valores permitidos."""

    valores = (
        datos[columna]
        .astype("string")
        .str.strip()
        .str.upper()
    )
    invalidos = ~valores.isin(valores_permitidos)

    if invalidos.any():
        filas = _filas_csv(invalidos)
        encontrados = sorted(
            set(valores[invalidos].dropna().tolist())
        )
        detalle = ", ".join(encontrados)

        raise ErrorDatosCSV(
            f"Valores no permitidos en {nombre_archivo}, "
            f"columna {columna}, filas {filas}: {detalle}"
        )


def validar_ventas(
    datos: pd.DataFrame,
    nombre_archivo: str = "ventas.csv",
) -> None:
    """Ejecuta todas las validaciones estructurales de ventas."""

    from .esquemas import COLUMNAS_VENTAS, METODOS_PAGO

    validar_campos_obligatorios(
        datos,
        COLUMNAS_VENTAS,
        nombre_archivo,
    )
    validar_fechas(
        datos,
        fecha_minima="2026-01-01",
        fecha_maxima="2026-08-21",
        nombre_archivo=nombre_archivo,
    )
    validar_horas(
        datos,
        nombre_archivo=nombre_archivo,
    )
    validar_numeros_ventas(
        datos,
        nombre_archivo,
    )
    validar_valores_permitidos(
        datos,
        "metodo_pago",
        METODOS_PAGO,
        nombre_archivo,
    )


def validar_inventario(
    datos: pd.DataFrame,
    nombre_archivo: str = "inventario.csv",
) -> None:
    """Ejecuta todas las validaciones estructurales del inventario."""

    from .esquemas import (
        CATEGORIAS_PRODUCTO,
        COLUMNAS_INVENTARIO,
        UNIDADES_MEDIDA,
        VALORES_BOOLEANOS,
    )

    validar_campos_obligatorios(
        datos,
        COLUMNAS_INVENTARIO,
        nombre_archivo,
    )
    validar_numeros_inventario(
        datos,
        nombre_archivo,
    )
    validar_valores_permitidos(
        datos,
        "categoria",
        CATEGORIAS_PRODUCTO,
        nombre_archivo,
    )
    validar_valores_permitidos(
        datos,
        "unidad_medida",
        UNIDADES_MEDIDA,
        nombre_archivo,
    )
    validar_valores_permitidos(
        datos,
        "activo",
        VALORES_BOOLEANOS,
        nombre_archivo,
    )
