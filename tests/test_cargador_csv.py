"""Pruebas para la carga segura de archivos CSV."""

import pytest

from agentewasi import ErrorCargaCSV, cargar_csv


def test_cargar_csv_valido(tmp_path):
    archivo = tmp_path / "valido.csv"
    archivo.write_text(
        "producto_id,producto\nPROD-001,Arroz\n",
        encoding="utf-8",
    )

    datos = cargar_csv(archivo)

    assert datos.shape == (1, 2)
    assert list(datos.columns) == ["producto_id", "producto"]
    assert datos.iloc[0]["producto"] == "Arroz"


def test_cargar_csv_inexistente(tmp_path):
    archivo = tmp_path / "inexistente.csv"

    with pytest.raises(ErrorCargaCSV, match="no existe"):
        cargar_csv(archivo)


def test_rechazar_extension_incorrecta(tmp_path):
    archivo = tmp_path / "datos.txt"
    archivo.write_text("id,nombre\n1,Arroz\n", encoding="utf-8")

    with pytest.raises(ErrorCargaCSV, match="extensión .csv"):
        cargar_csv(archivo)


def test_rechazar_archivo_completamente_vacio(tmp_path):
    archivo = tmp_path / "vacio.csv"
    archivo.write_text("", encoding="utf-8")

    with pytest.raises(ErrorCargaCSV, match="está vacío"):
        cargar_csv(archivo)


def test_rechazar_csv_solo_con_encabezados(tmp_path):
    archivo = tmp_path / "solo_encabezados.csv"
    archivo.write_text("id,nombre\n", encoding="utf-8")

    with pytest.raises(ErrorCargaCSV, match="no contiene registros"):
        cargar_csv(archivo)


def test_validar_columnas_acepta_esquema_completo():
    import pandas as pd

    from agentewasi import validar_columnas

    datos = pd.DataFrame(
        {
            "producto_id": ["PROD-001"],
            "producto": ["Arroz"],
            "columna_extra": ["permitida"],
        }
    )

    validar_columnas(
        datos,
        ("producto_id", "producto"),
    )


def test_validar_columnas_informa_faltantes_ordenados():
    import pandas as pd

    from agentewasi import ErrorColumnasCSV, validar_columnas

    datos = pd.DataFrame(
        {
            "producto": ["Arroz"],
        }
    )

    with pytest.raises(
        ErrorColumnasCSV,
        match="cantidad, fecha",
    ):
        validar_columnas(
            datos,
            ("producto", "fecha", "cantidad"),
            nombre_archivo="ventas.csv",
        )


def test_cargar_ventas_reales_con_esquema():
    from pathlib import Path

    from agentewasi import COLUMNAS_VENTAS

    raiz = Path(__file__).resolve().parents[1]
    archivo = raiz / "data" / "ventas_ejemplo.csv"

    datos = cargar_csv(archivo, COLUMNAS_VENTAS)

    assert datos.shape == (10475, 10)


def test_rechazar_archivo_real_con_columna_faltante():
    from pathlib import Path

    from agentewasi import COLUMNAS_VENTAS, ErrorColumnasCSV

    raiz = Path(__file__).resolve().parents[1]
    archivo = raiz / "data" / "datos_invalidos_columnas.csv"

    with pytest.raises(ErrorColumnasCSV, match="cantidad"):
        cargar_csv(archivo, COLUMNAS_VENTAS)
