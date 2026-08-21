"""Pruebas de validación de calidad de datos."""

from pathlib import Path

import pandas as pd
import pytest

from agentewasi import (
    COLUMNAS_INVENTARIO,
    COLUMNAS_VENTAS,
    cargar_csv,
)
from agentewasi.validador_datos import (
    ErrorDatosCSV,
    validar_campos_obligatorios,
)


def test_aceptar_campos_obligatorios_completos():
    datos = pd.DataFrame(
        {
            "producto_id": ["PROD-001"],
            "producto": ["Arroz"],
        }
    )

    validar_campos_obligatorios(
        datos,
        ("producto_id", "producto"),
    )


def test_informar_columnas_y_filas_vacias():
    datos = pd.DataFrame(
        {
            "producto_id": ["PROD-001", "", "PROD-003"],
            "producto": ["Arroz", "Azúcar", None],
        }
    )

    mensaje = (
        "producto_id en filas 3; "
        "producto en filas 4"
    )

    with pytest.raises(ErrorDatosCSV, match=mensaje):
        validar_campos_obligatorios(
            datos,
            ("producto_id", "producto"),
            "inventario_prueba.csv",
        )


@pytest.mark.parametrize(
    ("ruta_relativa", "columnas"),
    [
        ("data/ventas_ejemplo.csv", COLUMNAS_VENTAS),
        ("data/inventario_ejemplo.csv", COLUMNAS_INVENTARIO),
    ],
)
def test_archivos_reales_no_tienen_campos_vacios(
    ruta_relativa,
    columnas,
):
    raiz = Path(__file__).resolve().parents[1]
    archivo = raiz / ruta_relativa

    datos = cargar_csv(archivo, columnas)

    validar_campos_obligatorios(
        datos,
        columnas,
        archivo.name,
    )


def test_rechazar_fechas_imposibles_y_formato_incorrecto():
    from agentewasi.validador_datos import validar_fechas

    datos = pd.DataFrame(
        {
            "fecha": ["2026-02-30", "21/08/2026"],
        }
    )

    with pytest.raises(ErrorDatosCSV, match="filas 2, 3"):
        validar_fechas(
            datos,
            nombre_archivo="fechas_imposibles.csv",
        )


def test_rechazar_fechas_fuera_del_periodo():
    from agentewasi.validador_datos import validar_fechas

    datos = pd.DataFrame(
        {
            "fecha": ["2025-12-31", "2026-08-22"],
        }
    )

    with pytest.raises(ErrorDatosCSV, match="filas 2, 3"):
        validar_fechas(
            datos,
            fecha_minima="2026-01-01",
            fecha_maxima="2026-08-21",
            nombre_archivo="fechas_fuera.csv",
        )


def test_rechazar_horas_invalidas():
    from agentewasi.validador_datos import validar_horas

    datos = pd.DataFrame(
        {
            "hora": ["25:00:00", "09:61:00"],
        }
    )

    with pytest.raises(ErrorDatosCSV, match="filas 2, 3"):
        validar_horas(
            datos,
            nombre_archivo="horas_invalidas.csv",
        )


def test_fechas_y_horas_reales_son_validas():
    from agentewasi.validador_datos import validar_fechas, validar_horas

    raiz = Path(__file__).resolve().parents[1]
    archivo = raiz / "data" / "ventas_ejemplo.csv"
    datos = cargar_csv(archivo, COLUMNAS_VENTAS)

    validar_fechas(
        datos,
        fecha_minima="2026-01-01",
        fecha_maxima="2026-08-21",
        nombre_archivo=archivo.name,
    )
    validar_horas(
        datos,
        nombre_archivo=archivo.name,
    )


from agentewasi.validador_datos import (
    validar_numeros_inventario,
    validar_numeros_ventas,
)


@pytest.mark.parametrize(
    ("datos", "mensaje"),
    [
        (
            pd.DataFrame(
                {
                    "cantidad": [1.5],
                    "precio_unitario": [5.00],
                    "descuento": [0.00],
                }
            ),
            "cantidad debe ser un entero",
        ),
        (
            pd.DataFrame(
                {
                    "cantidad": [1],
                    "precio_unitario": [-5.00],
                    "descuento": [0.00],
                }
            ),
            "precio debe ser mayor que cero",
        ),
        (
            pd.DataFrame(
                {
                    "cantidad": [1],
                    "precio_unitario": ["4.567"],
                    "descuento": [0.00],
                }
            ),
            "dos decimales",
        ),
        (
            pd.DataFrame(
                {
                    "cantidad": [2],
                    "precio_unitario": [5.00],
                    "descuento": [10.00],
                }
            ),
            "descuento debe ser menor que el subtotal",
        ),
    ],
)
def test_rechazar_numeros_invalidos_de_ventas(
    datos,
    mensaje,
):
    with pytest.raises(
        ErrorDatosCSV,
        match=mensaje,
    ):
        validar_numeros_ventas(
            datos,
            "ventas_invalidas.csv",
        )


@pytest.mark.parametrize(
    ("datos", "mensaje"),
    [
        (
            pd.DataFrame(
                {
                    "precio_venta_actual": [5.00],
                    "stock_actual": [-1],
                    "stock_minimo": [5],
                }
            ),
            "stock actual no puede ser negativo",
        ),
        (
            pd.DataFrame(
                {
                    "precio_venta_actual": [5.00],
                    "stock_actual": [1],
                    "stock_minimo": [0],
                }
            ),
            "stock mínimo debe ser mayor que cero",
        ),
    ],
)
def test_rechazar_numeros_invalidos_de_inventario(
    datos,
    mensaje,
):
    with pytest.raises(
        ErrorDatosCSV,
        match=mensaje,
    ):
        validar_numeros_inventario(
            datos,
            "inventario_invalido.csv",
        )


@pytest.mark.parametrize(
    ("ruta_relativa", "columnas", "validador"),
    [
        (
            "data/ventas_ejemplo.csv",
            COLUMNAS_VENTAS,
            validar_numeros_ventas,
        ),
        (
            "data/inventario_ejemplo.csv",
            COLUMNAS_INVENTARIO,
            validar_numeros_inventario,
        ),
    ],
)
def test_numeros_reales_son_validos(
    ruta_relativa,
    columnas,
    validador,
):
    raiz = Path(__file__).resolve().parents[1]
    archivo = raiz / ruta_relativa
    datos = cargar_csv(archivo, columnas)

    validador(datos, archivo.name)


from agentewasi.esquemas import (
    CATEGORIAS_PRODUCTO,
    METODOS_PAGO,
    UNIDADES_MEDIDA,
    VALORES_BOOLEANOS,
)
from agentewasi.validador_datos import (
    validar_inventario,
    validar_valores_permitidos,
    validar_ventas,
)


@pytest.mark.parametrize(
    ("columna", "valor", "permitidos"),
    [
        ("metodo_pago", "TRANSFERENCIA", METODOS_PAGO),
        ("categoria", "ELECTRONICA", CATEGORIAS_PRODUCTO),
        ("unidad_medida", "KILO", UNIDADES_MEDIDA),
        ("activo", "SI", VALORES_BOOLEANOS),
    ],
)
def test_rechazar_valores_categoricos_no_permitidos(
    columna,
    valor,
    permitidos,
):
    datos = pd.DataFrame(
        {
            columna: [valor],
        }
    )

    with pytest.raises(
        ErrorDatosCSV,
        match=f"{valor}$",
    ):
        validar_valores_permitidos(
            datos,
            columna,
            permitidos,
            "datos_invalidos.csv",
        )


@pytest.mark.parametrize(
    ("ruta_relativa", "columnas", "validador"),
    [
        (
            "data/ventas_ejemplo.csv",
            COLUMNAS_VENTAS,
            validar_ventas,
        ),
        (
            "data/inventario_ejemplo.csv",
            COLUMNAS_INVENTARIO,
            validar_inventario,
        ),
    ],
)
def test_validacion_integral_de_archivos_reales(
    ruta_relativa,
    columnas,
    validador,
):
    raiz = Path(__file__).resolve().parents[1]
    archivo = raiz / ruta_relativa
    datos = cargar_csv(archivo, columnas)

    validador(datos, archivo.name)
