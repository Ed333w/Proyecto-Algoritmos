"""Persistencia en archivos de texto: RQF-050."""

import filecmp
import os

import pytest

from modulos import Sistema
from persistencia import guardar, cargar, hayDatosGuardados
from persistencia.Persistencia import ARCHIVOS
from persistencia.datos_masivos import crearSistemaMasivo, contarRegistros

CARPETA_PRUEBA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datos_prueba")


def test_rqf050_exitoso(caso, demo, tmp_path):
    caso.inicio("RQF-050", "Exitoso", "Guardar la demo, cargarla y volver a guardar",
                "Los archivos quedan idénticos; filas, préstamos y contadores se recuperan")
    guardar(demo, tmp_path / "a")
    cargado = cargar(tmp_path / "a")
    guardar(cargado, tmp_path / "b")
    iguales = all(filecmp.cmp(tmp_path / "a" / f"{n}.txt", tmp_path / "b" / f"{n}.txt", shallow=False) for n in ARCHIVOS)
    fila = [s.codigoUsuario for s in cargado.turnos.obtenerFila("R0003", "Centro")]
    nuevo = cargado.usuarios.registrar("Nueva", "nueva@uni.edu", "CC", "3000005")
    caso.resultado(f"{cargado.resumen()}; archivos idénticos={iguales}; fila de la sala {fila}; siguiente usuario {nuevo}")
    assert iguales and fila == ["U002", "U004"] and nuevo == "U006"
    assert cargado.prestamos.deshacer() is None          # lo cargado no se deshace
    assert cargado.recursos.obtener("R0001").cantidadPrestamos == 4


def test_rqf050_borde(caso, tmp_path):
    caso.inicio("RQF-050", "Borde", "Carpeta vacía, sistema vacío, nombre con ';' y una fecha dañada en el archivo",
                "Error claro en la carpeta vacía; el vacío y el ';' se guardan y cargan bien; la fecha dañada indica archivo y línea")
    with pytest.raises(ValueError) as vacia:
        cargar(tmp_path / "nada")
    guardar(Sistema(), tmp_path / "vacio")
    s = Sistema()
    s.usuarios.registrar("Pérez; Ana", "ana@uni.edu", "PA", "XZ9876543")
    guardar(s, tmp_path / "raro")
    nombre = cargar(tmp_path / "raro").usuarios.obtener("U001").nombre
    ruta = tmp_path / "raro" / "usuarios.txt"
    ruta.write_text(ruta.read_text(encoding="utf-8").replace("20", "xx", 1), encoding="utf-8")
    with pytest.raises(ValueError) as danado:
        cargar(tmp_path / "raro")
    mensajeVacia = str(vacia.value).replace(str(tmp_path), "<temporal>")
    caso.resultado(f"{mensajeVacia}; vacío guardado={hayDatosGuardados(tmp_path / 'vacio')}; nombre '{nombre}'; {danado.value}")
    assert nombre == "Pérez; Ana" and "usuarios.txt, línea 2" in str(danado.value)


def test_rqf050_cuello(caso, tmp_path, cronometro):
    caso.inicio("RQF-050", "Cuello de botella", "Guardar y cargar 3.000 usuarios, 1.500 recursos y 6.000 préstamos",
                "Se recuperan todos los registros")
    s = crearSistemaMasivo(usuarios=3000, recursos=1500, prestamos=6000, solicitudes=300)
    with cronometro() as t:
        guardados = guardar(s, tmp_path)
        cargado = cargar(tmp_path)
    caso.resultado(f"{guardados:,} filas; cargado: {cargado.resumen()}; {t.segundos:.2f} s")
    assert contarRegistros(cargado) == contarRegistros(s) and t.segundos < 15


def test_datos_prueba_mas_de_500(caso):
    caso.inicio("RQF-050", "Cuello de botella", "Cargar la carpeta datos_prueba incluida en el repositorio",
                "Más de 500 registros, coherentes con el inventario")
    s = cargar(CARPETA_PRUEBA)
    caso.resultado(f"{contarRegistros(s):,} registros: {s.resumen()}")
    assert contarRegistros(s) > 500
