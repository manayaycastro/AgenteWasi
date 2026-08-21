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
