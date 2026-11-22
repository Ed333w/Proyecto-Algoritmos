"""Menú M09 · Red de sedes (grafo)."""

from .consola import leer, tabla, ejecutarMenu


def conectar(sesion):
    a, b = sesion.sistema.red.conectar(leer("Sede A: "), leer("Sede B: "))
    print(f"\n  {a} y {b} quedaron conectadas")


def desconectar(sesion):
    sesion.sistema.red.desconectar(leer("Sede A: "), leer("Sede B: "))
    print("\n  Conexión eliminada")


def conexiones(sesion):
    red = sesion.sistema.red
    tabla(("Sede", "Sede"), red.conexiones(), vacio="(sin conexiones)")
    print("\n  Grupos conectados: " + " | ".join(", ".join(grupo) for grupo in red.componentes()))


def masCercana(sesion):
    sede, recurso = leer("Sede actual: "), leer("Código del recurso: ")
    resultado = sesion.sistema.red.sedeMasCercanaConRecurso(sede, recurso)
    if resultado is None:
        print("\n  Ninguna sede alcanzable tiene unidades de ese recurso")
    elif resultado[1] == 0:
        print(f"\n  Hay {resultado[2]} unidad(es) en la misma sede ({resultado[0]})")
    else:
        ruta = sesion.sistema.red.rutaMasCorta(sede, resultado[0])
        print(f"\n  {resultado[0]}, a {resultado[1]} tramo(s), tiene {resultado[2]} unidad(es)")
        print(f"  Camino más corto: {' -> '.join(ruta)}")


def ruta(sesion):
    red = sesion.sistema.red
    origen, destino = leer("Sede de origen: "), leer("Sede de destino: ")
    camino = red.rutaMasCorta(origen, destino)
    if not camino:
        print("\n  No hay ruta: las sedes no están conectadas")
        return
    print(f"\n  Ruta más corta ({len(camino) - 1} tramo(s)): {' -> '.join(camino)}")
    print("\n  Rutas alternativas (backtracking):")
    for alternativa in red.rutasAlternativas(origen, destino):
        print(f"    {' -> '.join(alternativa)}")


def aisladas(sesion):
    sedes = sesion.sistema.red.sedesAisladas()
    print("\n  Sedes aisladas: " + (", ".join(sedes) if sedes else "ninguna, toda la red está conectada"))


def menu(sesion):
    ejecutarMenu("M09 · RED DE SEDES", (
        ("Conectar dos sedes", conectar),
        ("Ver conexiones", conexiones),
        ("Sede más cercana con un recurso disponible", masCercana),
        ("Ruta más corta entre sedes", ruta),
        ("Detectar sedes aisladas", aisladas),
        ("Eliminar una conexión", desconectar),
    ), sesion)
