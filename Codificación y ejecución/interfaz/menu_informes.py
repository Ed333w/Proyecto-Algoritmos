"""Menú M06 · Informes y listados."""

import time

from modulos.comun import fechaATexto
from .consola import leer, leerEntero, tabla, ejecutarMenu
from .menu_recursos import mostrarRecursos
from .menu_usuarios import mostrarUsuarios


def reporteUso(sesion):
    tabla(("Indicador", "Valor"), sesion.sistema.informes.reporteUso().items())


def reporteInventario(sesion):
    tabla(("Tipo", "Registrados", "Operativos", "Unidades disponibles"), sesion.sistema.informes.reporteInventario())
    print("\n  El detalle por sede está en Inventario (M07).")


def masPrestados(sesion):
    cantidad = leerEntero("¿Cuántos mostrar? (Enter = 10): ", 10)
    tabla(("Puesto", "Código", "Nombre", "Préstamos"),
          [(i, r.codigo, r.nombre, r.cantidadPrestamos)
           for i, r in enumerate(sesion.sistema.informes.masPrestados(cantidad), 1)])


def porAntiguedad(sesion):
    tabla(("Código", "Nombre", "Registrado"),
          [(r.codigo, r.nombre, fechaATexto(r.fechaRegistro)) for r in sesion.sistema.informes.porAntiguedad()])


def buscarPorNombre(sesion):
    informes = sesion.sistema.informes
    nombre = leer("Nombre exacto del recurso: ")
    inicio = time.perf_counter()
    encontrados = informes.buscarPorNombre(nombre)
    binaria = time.perf_counter() - inicio
    inicio = time.perf_counter()
    informes.buscarPorNombreSecuencial(nombre)
    secuencial = time.perf_counter() - inicio
    mostrarRecursos(sesion.sistema, encontrados)
    print(f"\n  Búsqueda binaria sobre el catálogo ordenado: {binaria * 1e6:.1f} µs")
    print(f"  Búsqueda secuencial sobre el vector:         {secuencial * 1e6:.1f} µs")


def tasaDevolucion(sesion):
    t = sesion.sistema.informes.tasaDevolucion()
    print(f"  Devueltos a tiempo: {t['aTiempo']} de {t['total']} = {t['porcentaje']}%")
    print(f"  Tarde (devueltos tarde o vencidos sin devolver): {t['tarde']}")


def demandaPorCategoria(sesion):
    principal = leer("1 = por subcategoría, 2 = agrupado en la categoría principal: ") == "2"
    tabla(("Categoría", "Préstamos"), sesion.sistema.informes.demandaPorCategoria(principal))


def menu(sesion):
    ejecutarMenu("M06 · INFORMES Y LISTADOS", (
        ("Reporte de uso", reporteUso),
        ("Reporte de inventario", reporteInventario),
        ("Recursos más prestados (merge sort)", masPrestados),
        ("Recursos por antigüedad (quick sort)", porAntiguedad),
        ("Buscar recurso por nombre (binaria vs. secuencial)", buscarPorNombre),
        ("Tasa de devolución a tiempo", tasaDevolucion),
        ("Demanda por categoría", demandaPorCategoria),
        ("Usuarios por nombre (merge sort)", lambda s: mostrarUsuarios(s.sistema.informes.usuariosPorNombre())),
        ("Recursos por nombre (recorrido del BST)", lambda s: mostrarRecursos(s.sistema, s.sistema.informes.recursosPorNombre())),
    ), sesion)
