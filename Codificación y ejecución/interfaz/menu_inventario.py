"""Menú M07 · Inventario por sede."""

from .consola import leer, leerEntero, tabla, ejecutarMenu
from .menu_prestamos import informarAsignados


def disponibilidad(sesion):
    sistema = sesion.sistema
    recurso = sistema.recursos.obtener(leer("Código del recurso: "))
    sede = leer("Sede (Enter para todas): ")
    if sede:
        sede = sistema.recursos.validarSede(sede)
        print(f"\n  {recurso.codigo} en {sede}: {sistema.inventario.obtenerDisponibilidad(recurso.codigo, sede)} unidad(es)")
    else:
        tabla(("Sede", "Unidades"), sistema.inventario.disponibilidadPorSede(recurso.codigo))


def fijarUnidades(sesion):
    sistema = sesion.sistema
    recurso, sede = leer("Código del recurso: "), leer("Sede: ")
    asignados = sistema.fijarUnidades(recurso, sede, leer("Unidades disponibles: "))
    print("\n  Unidades actualizadas")
    informarAsignados(sistema, asignados)


def matrizSedeDia(sesion):
    sistema = sesion.sistema
    recurso = sistema.recursos.obtener(leer("Código del recurso: "))
    dias = leerEntero("Días a proyectar (Enter = 7): ", 7)
    sedes, fechas, matriz = sistema.inventario.matrizSedeDia(recurso.codigo, sistema.prestamos.listarActivos(), dias)
    print(f"\n  Unidades proyectadas de {recurso.codigo} {recurso.nombre} (suma las que vuelven en su fecha límite)\n")
    tabla(["Sede"] + [f.strftime("%d/%m") for f in fechas],
          [[sede] + fila for sede, fila in zip(sedes, matriz)])


def menu(sesion):
    ejecutarMenu("M07 · INVENTARIO", (
        ("Matriz sede × recurso", lambda s: print(s.sistema.inventario.mostrarMatriz())),
        ("Disponibilidad de un recurso por sede", disponibilidad),
        ("Fijar unidades de un recurso en una sede", fijarUnidades),
        ("Matriz sede × día (proyección)", matrizSedeDia),
    ), sesion)
