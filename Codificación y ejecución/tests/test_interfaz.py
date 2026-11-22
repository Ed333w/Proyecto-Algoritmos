"""Interfaz de consola: recorre todas las opciones del menú como lo haría el usuario."""

import os
import shutil
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Cada bloque: opción del menú principal, entradas de sus opciones y "0" para volver.
# "" es el Enter de "Presione Enter para continuar".
RECORRIDO = [
    "",                                                         # aviso de vencimientos
    "1", "1", "Juan Diaz", "CC", "80.123.456", "juan@uni.edu", "", "2", "", "2", "CC", "80123456", "",
    "3", "U006", "juan.diaz@uni.edu", "", "4", "U006", "", "5", "", "1", "juan", "", "6", "", "7", "", "0",
    "2", "1", "Libro", "Calculo", "Stewart", "978-9", "2012", "C012", "", "2", "", "Libro", "calc", "",
    "2", "", "Equipo", "", "R0005", "",
    "3", "R0013", "2", "James Stewart", "", "4", "", "5", "", "6", "Equipo", "",
    "7", "C012", "s", "", "8", "Prestado", "", "9", "", "10", "Oriente", "", "11", "", "0",
    "7", "1", "", "2", "R0001", "", "", "2", "", "Libro", "python", "", "", "3", "R0013", "Centro", "2", "",
    "4", "R0003", "3", "",
    "5", "R0006", "5", "", "5", "R0011", "1", "", "6", "", "0",
    "3", "1", "U006", "R0013", "Centro", "", "1", "", "1", "luis", "", "Sala", "estudio", "Centro", "s", "", "2", "P0012", "",
    "3", "", "4", "", "5", "", "6", "P0007", "", "7", "Norte", "", "8", "U003", "2", "", "9", "R0001", "",
    "10", "1", "", "0",
    "4", "1", "U005", "R0004", "Norte", "", "2", "R0003", "Centro", "", "3", "R0003", "", "",
    "4", "T0001", "", "5", "T0002", "", "0",
    "5", "1", "C017", "Optica", "C016", "", "2", "C009", "", "3", "", "4", "", "0",
    "6", "1", "", "2", "", "3", "5", "", "4", "", "5", "Python 101", "", "6", "", "7", "2", "", "8", "", "9", "", "0",
    "8", "1", "n", "s", "1", "", "1", "s", "R0004", "", "2", "", "", "3", "R0003", "", "3", "", "Sala", "estudio", "",
    "4", "", "5", "3", "", "0",
    "9", "1", "Occidente", "Oriente", "", "2", "", "3", "R0004", "Norte", "", "3", "", "Libro", "python", "Sur", "",
    "4", "Norte", "Sur", "",
    "5", "", "6", "Occidente", "Oriente", "", "0",
    "10", "1", "", "3", "s", "", "2", "s", "", "4", "n", "", "0",
    "11", "",
    "0",
]


def _ejecutar(entradas, carpeta):
    entorno = dict(os.environ, DATOS_PROYECTO=str(carpeta), SIN_LIMPIAR="1", PYTHONIOENCODING="utf-8")
    proceso = subprocess.run([sys.executable, "main.py"], cwd=RAIZ, input="\n".join(entradas) + "\n",
                             capture_output=True, text=True, encoding="utf-8", env=entorno, timeout=120)
    return proceso.stdout + proceso.stderr, proceso.returncode


def test_interfaz_exitoso(caso, tmp_path):
    caso.inicio("Interfaz (menú)", "Exitoso", "Recorrer las 68 opciones (69 pasos) de los 11 menús con datos válidos, "
                "consultando usuarios por documento y recursos por tipo y nombre desde la lista, y cambiando "
                "la condición de recursos desde Inventario",
                "Ninguna opción falla; al salir se guardan los datos")
    salida, codigo = _ejecutar(RECORRIDO, tmp_path)
    errores = [linea.strip() for linea in salida.splitlines() if "Error:" in linea]
    caso.resultado(f"código de salida {codigo}; errores mostrados {len(errores)}; "
                   f"datos guardados={os.path.isfile(tmp_path / 'usuarios.txt')}")
    assert codigo == 0 and "Traceback" not in salida and not errores, errores
    for esperado in ("Usuario registrado con el código U006", "documento          CC 80123456",
                     "U006 Juan Diaz está activo de nuevo", "Libro registrado con el código R0013",
                     "nombre               Calculo", "Hay varios: escriba el código", "nombre               Portatil Dell",
                     "R0006 Fisica Universitaria ahora está dado de baja", "Recursos fuera de servicio: 1 dañado, 1 en reparación",
                     "R0011 Laptop Lenovo ahora está operativo", "Los recursos no se borran",
                     "Préstamo P0012 registrado", "Turno T0005 asignado", "Ruta más corta (1 tramo(s)): Norte -> Sur",
                     "Sedes aisladas: Occidente, Oriente", "Camino más corto: Norte -> Centro", "Se deshizo", "Hecho: Mover", "Se guardaron"):
        assert esperado in salida, esperado


def test_interfaz_borde(caso, tmp_path):
    caso.inicio("Interfaz (menú)", "Borde", "Opciones inexistentes, datos inválidos y fin de la entrada sin salir",
                "Muestra 'Opción inválida' o el error y sigue; al cortarse la entrada guarda y termina sin Traceback")
    entradas = ["", "x", "", "99", "", "1", "1", "", "", "", "", "", "2", "U999", "", "0",
                "2", "1", "Revista", "", "0", "3", "6", "P9999", ""]          # termina sin "0"
    salida, codigo = _ejecutar(entradas, tmp_path)
    invalidas, errores = salida.count("Opción inválida"), salida.count("Error:")
    caso.resultado(f"{invalidas} opciones inválidas y {errores} errores mostrados; código {codigo}; "
                   f"guardó={os.path.isfile(tmp_path / 'usuarios.txt')}")
    assert codigo == 0 and "Traceback" not in salida and invalidas == 2 and errores == 4
    assert "Entrada terminada" in salida and os.path.isfile(tmp_path / "usuarios.txt")


def test_interfaz_cuello(caso, tmp_path, cronometro):
    caso.inicio("Interfaz (menú)", "Cuello de botella", "Abrir el programa con los datos de prueba (más de 1.000 registros) y "
                "pedir listados, informes y alertas", "Carga, responde y guarda sin errores")
    shutil.copytree(os.path.join(RAIZ, "datos de prueba"), tmp_path, dirs_exist_ok=True)
    entradas = ["", "1", "6", "", "0", "6", "1", "", "3", "10", "", "0", "8", "4", "", "2", "10", "", "0", "0"]
    with cronometro() as t:
        salida, codigo = _ejecutar(entradas, tmp_path)
    resumen = salida.splitlines()[1].strip().replace(str(tmp_path), "<carpeta de datos>")
    caso.resultado(f"{resumen}; código {codigo}; {t.segundos:.2f} s")
    assert codigo == 0 and "Traceback" not in salida and "300 usuarios" in salida and "(300 registro(s))" in salida
