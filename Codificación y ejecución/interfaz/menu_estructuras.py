"""Demostración rápida de las estructuras propias (útil en la sustentación)."""

import time

from estructuras import (VectorDinamico, ListaSimple, ListaDoble, Pila, ColaFIFO, TablaHash,
                         hashSumaAscii, ConjuntoHash, ArbolBinarioBusqueda, ArbolAVL, Monticulo, Grafo)
from .consola import tabla, titulo, pausa, limpiarPantalla


def _medir(funcion):
    inicio = time.perf_counter()
    funcion()
    return (time.perf_counter() - inicio) * 1000


def mostrar():
    v = VectorDinamico(2)
    for x in "ABC":
        v.agregar(x)
    print(f"  Vector dinámico: {v.recorrer()} capacidad {v.obtenerCapacidad()} (se duplicó al llenarse)")

    ls, ld = ListaSimple(), ListaDoble()
    for x in (1, 2, 3):
        ls.agregarAlFinal(x)
        ld.agregarAlFinal(x)
    print(f"  Lista simple: {ls.recorrer()}   Lista doble atrás: {ld.recorrerAtras()}")

    p, c = Pila(), ColaFIFO()
    for x in ("op1", "op2", "op3"):
        p.push(x)
        c.encolar(x)
    print(f"  Pila (LIFO) sale: {p.pop()}   Cola (FIFO) sale: {c.desencolar()}")

    conjunto = ConjuntoHash()
    print(f"  Conjunto: agregar 'C001' dos veces -> {conjunto.agregar('C001')}, {conjunto.agregar('C001')}")

    m = Monticulo(esMaximo=True)
    for prioridad in (3, 9, 1, 7):
        m.insertar(prioridad, f"p{prioridad}")
    print(f"  Montículo de máximos sale en orden: {[d for _, d in m.extraerVarios()]}")

    g = Grafo()
    for sede in ("A", "B", "C", "D"):
        g.agregarVertice(sede)
    for a, b in (("A", "B"), ("B", "C"), ("A", "C")):
        g.agregarArista(a, b)
    print(f"  Grafo: BFS {g.recorridoAmplitud('A')}, DFS {g.recorridoProfundidad('A')}")
    print(f"         ruta A->C {g.caminoMasCorto('A', 'C')}, todas {g.todosLosCaminos('A', 'C')}, "
          f"componentes {g.componentesConexas()}")

    print("\n  Hash djb2 vs. suma ASCII (Entrega 1) con 2.000 códigos R0001.. en 211 cubetas:")
    filas = []
    for nombre, funcion in (("djb2", None), ("Suma ASCII", hashSumaAscii)):
        t = TablaHash(211, funcion, redimensionar=False) if funcion else TablaHash(211, redimensionar=False)
        for i in range(2000):
            t.insertar(f"R{i:04d}", i)
        e = t.estadisticas()
        filas.append((nombre, e["cubetasOcupadas"], e["cadenaMaxima"], e["comparacionesPromedio"]))
    tabla(("Función", "Cubetas usadas", "Cadena más larga", "Comparaciones promedio"), filas)

    print("\n  BST vs. AVL con 2.000 claves que llegan en orden (C0001, C0002, ...):")
    filas = []
    for arbol in (ArbolBinarioBusqueda(), ArbolAVL()):
        ms = _medir(lambda: [arbol.insertar(f"C{i:04d}") for i in range(2000)])
        filas.append((arbol.__class__.__name__, arbol.obtenerAltura(), f"{ms:.1f} ms"))
    tabla(("Árbol", "Altura", "Tiempo de inserción"), filas)


def menu(_sesion):
    limpiarPantalla()
    titulo("DEMOSTRACIÓN DE ESTRUCTURAS PROPIAS")
    mostrar()
    pausa()
