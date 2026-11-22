"""Menú de datos · Persistencia (RQF-050)."""

import os

from persistencia import guardar, cargar
from persistencia.datos_demo import crearSistemaDemo
from .consola import confirmar, ejecutarMenu

CARPETA_PRUEBA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datos_prueba")


def guardarAhora(sesion):
    registros = guardar(sesion.sistema, sesion.carpetaDatos)
    print(f"\n  {registros} registros guardados en {sesion.carpetaDatos}")


def _reemplazar(sesion, nuevo, origen):
    if not confirmar("  Se reemplazarán los datos en uso (lo no guardado se pierde). ¿Continuar?"):
        print("\n  Operación cancelada")
        return
    sesion.sistema = nuevo
    print(f"\n  Datos cargados desde {origen}: {nuevo.resumen()}")


def recargar(sesion):
    _reemplazar(sesion, cargar(sesion.carpetaDatos), sesion.carpetaDatos)


def cargarPrueba(sesion):
    _reemplazar(sesion, cargar(CARPETA_PRUEBA), "datos_prueba (más de 500 registros)")


def restaurarDemo(sesion):
    _reemplazar(sesion, crearSistemaDemo(), "los datos de demostración")


def menu(sesion):
    ejecutarMenu("DATOS · GUARDAR Y CARGAR", (
        ("Guardar ahora", guardarAhora),
        ("Volver a cargar lo último guardado", recargar),
        ("Cargar datos de prueba (más de 500 registros)", cargarPrueba),
        ("Restaurar datos de demostración", restaurarDemo),
    ), sesion)
