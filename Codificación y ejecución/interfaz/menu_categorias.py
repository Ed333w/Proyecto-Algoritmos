"""Menú M05 · Categorías y subcategorías."""

from .consola import leer, tabla, ejecutarMenu


def mostrarArbol(sistema, nodos):
    for categoria, profundidad in nodos:
        recursos = sistema.recursos.listarPorCategoria(categoria.codigo, incluirSubcategorias=False)
        print(f"  {'    ' * profundidad}{categoria.codigo} {categoria.nombre} ({len(recursos)} recurso(s))")
        for r in recursos:
            print(f"  {'    ' * profundidad}    - {r.codigo} {r.nombre}")


def registrar(sesion):
    categorias = sesion.sistema.categorias
    codigo = leer("Código (ej. C010): ")
    nombre = leer("Nombre: ")
    padre = leer("Código de la categoría padre (Enter si es principal): ") or None
    categorias.registrarCategoria(codigo, nombre, padre)
    print(f"\n  Categoría registrada: {categorias.obtener(codigo).ruta()}")


def consultarSubarbol(sesion):
    sistema = sesion.sistema
    categoria = sistema.categorias.obtener(leer("Código de la categoría: "))
    print(f"\n  Ruta: {categoria.ruta()}\n")
    mostrarArbol(sistema, sistema.categorias.subarbol(categoria.codigo))


def indiceAVL(sesion):
    categorias = sesion.sistema.categorias
    tabla(("Código", "Nombre", "Ruta"), [(c.codigo, c.nombre, c.ruta()) for c in categorias.listarPorCodigo()])
    print(f"\n  Altura del AVL: {categorias.alturaIndice()} con {categorias.obtenerCantidad()} categorías "
          f"({categorias.indice.rotaciones} rotaciones hechas para mantenerlo balanceado)")


def menu(sesion):
    ejecutarMenu("M05 · CATEGORÍAS", (
        ("Registrar categoría o subcategoría", registrar),
        ("Consultar categoría y todo lo que cuelga de ella", consultarSubarbol),
        ("Ver árbol completo", lambda s: mostrarArbol(s.sistema, s.sistema.categorias.arbolCompleto())),
        ("Índice por código (árbol AVL)", indiceAVL),
    ), sesion)
