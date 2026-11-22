"""Funciones de entrada y salida por consola que comparten todos los menús."""

import os
import sys


class FinDeEntrada(Exception):
    """Se terminó la entrada (Ctrl+D / Ctrl+Z o fin del archivo de pruebas)."""


class Sesion:
    """Lo que comparten los menús: el sistema en uso y la carpeta donde se guarda."""

    def __init__(self, sistema, carpetaDatos):
        self.sistema = sistema
        self.carpetaDatos = carpetaDatos


def limpiarPantalla():
    if sys.stdout.isatty() and not os.environ.get("SIN_LIMPIAR"):
        os.system("cls" if os.name == "nt" else "clear")


def leer(mensaje):
    try:
        return input(mensaje).strip()
    except EOFError:
        raise FinDeEntrada() from None


def leerEntero(mensaje, defecto=None):
    texto = leer(mensaje)
    if not texto and defecto is not None:
        return defecto
    try:
        return int(texto)
    except ValueError:
        raise ValueError(f"'{texto}' no es un número entero") from None


def confirmar(mensaje):
    return leer(f"{mensaje} (s/n): ").lower() in ("s", "si", "sí")


def pausa():
    leer("\nPresione Enter para continuar...")


def titulo(texto):
    print(f"\n  {texto}\n  " + "=" * len(texto))


def tabla(encabezados, filas, vacio="(sin resultados)"):
    filas = [[str(c) for c in fila] for fila in filas]
    if not filas:
        print(f"  {vacio}")
        return
    anchos = [max(len(encabezados[i]), *(len(f[i]) for f in filas)) for i in range(len(encabezados))]
    formato = "  " + "  ".join(f"{{:<{a}}}" for a in anchos)
    print(formato.format(*encabezados))
    print("  " + "  ".join("-" * a for a in anchos))
    for fila in filas:
        print(formato.format(*fila))
    print(f"  ({len(filas)} registro(s))")


def ejecutarMenu(nombre, opciones, sesion, textoSalir="Volver", esPrincipal=False):
    """Bucle común de todos los submenús. 'opciones' es una secuencia de
    (texto, función que recibe la sesión). Los errores de validación se muestran
    sin cerrar el programa. En el menú principal no se hace pausa al volver de un submenú."""
    while True:
        limpiarPantalla()
        titulo(nombre)
        for numero, (texto, _) in enumerate(opciones, 1):
            print(f"  {numero:>2}. {texto}")
        print(f"   0. {textoSalir}")
        opcion = leer("\nSeleccione una opción: ")
        if opcion == "0":
            return
        if not opcion.isdigit() or not 1 <= int(opcion) <= len(opciones):
            print("\n  Opción inválida")
            pausa()
            continue
        texto, accion = opciones[int(opcion) - 1]
        if esPrincipal:
            accion(sesion)
            continue
        titulo(texto)
        try:
            accion(sesion)
        except ValueError as error:
            print(f"\n  Error: {error}")
        pausa()
