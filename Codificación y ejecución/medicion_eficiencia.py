"""Medición empírica: estructuras propias frente a las nativas de Python.

Los lineamientos piden no reemplazar las estructuras exigidas por list, dict o set,
pero permiten usarlas como referencia de desempeño y reportar esa comparación en
el informe. Este script la hace con las mismas clases que usa el sistema.

Uso:  python medicion_eficiencia.py            (imprime la tabla)
      python medicion_eficiencia.py salida.json (además la guarda en JSON)

Cada medición se repite 5 veces y se reporta la mediana, en microsegundos por
operación (µs/op).
"""

import json
import random
import sys
import time
from statistics import median

from estructuras import (VectorDinamico, ListaSimple, Pila, ColaFIFO, TablaHash, ConjuntoHash,
                         ArbolBinarioBusqueda, ArbolAVL, Monticulo)
from estructuras.Algoritmos import insercion, mergeSort, quickSort, busquedaSecuencial, busquedaBinaria

REPETICIONES = 5


def medir(funcion, operaciones):
    """µs por operación (mediana de REPETICIONES ejecuciones)."""
    tiempos = []
    for _ in range(REPETICIONES):
        inicio = time.perf_counter()
        funcion()
        tiempos.append(time.perf_counter() - inicio)
    return median(tiempos) / operaciones * 1e6


def codigos(n):
    return [f"R{i:05d}" for i in range(1, n + 1)]


def busquedaPorCodigo(n, consultas=2000):
    claves = codigos(n)
    propia, nativa = TablaHash(), {}
    for i, c in enumerate(claves):
        propia.insertar(c, i)
        nativa[c] = i
    objetivos = random.Random(1).choices(claves, k=consultas)
    pocos = objetivos[:100]
    return [
        ("Búsqueda por código", f"Tabla hash propia (djb2), n={n:,}", medir(lambda: [propia.buscar(c) for c in objetivos], consultas)),
        ("Búsqueda por código", f"dict de Python, n={n:,}", medir(lambda: [nativa.get(c) for c in objetivos], consultas)),
        ("Búsqueda por código", f"Búsqueda secuencial, n={n:,}", medir(lambda: [busquedaSecuencial(claves, c) for c in pocos], len(pocos))),
        ("Búsqueda por código", f"Búsqueda binaria propia, n={n:,}", medir(lambda: [busquedaBinaria(claves, c) for c in objetivos], consultas)),
    ]


def insercionAlFinal(n=50000):
    def propio():
        v = VectorDinamico(1)
        for i in range(n):
            v.agregar(i)

    def nativo():
        v = []
        for i in range(n):
            v.append(i)
    return [("Agregar al final", f"VectorDinamico propio, n={n:,}", medir(propio, n)),
            ("Agregar al final", f"list.append, n={n:,}", medir(nativo, n))]


def pilaYCola(n=20000):
    def pila():
        p = Pila()
        for i in range(n):
            p.push(i)
        while not p.estaVacia():
            p.pop()

    def listaComoPila():
        p = []
        for i in range(n):
            p.append(i)
        while p:
            p.pop()

    def cola():
        c = ColaFIFO()
        for i in range(n):
            c.encolar(i)
        while not c.estaVacia():
            c.desencolar()

    def listaComoCola():
        c = []
        for i in range(n):
            c.append(i)
        while c:
            c.pop(0)
    return [("Pila (push + pop)", f"Pila propia, n={n:,}", medir(pila, n)),
            ("Pila (push + pop)", f"list.append / pop(), n={n:,}", medir(listaComoPila, n)),
            ("Cola (encolar + desencolar)", f"ColaFIFO circular propia, n={n:,}", medir(cola, n)),
            ("Cola (encolar + desencolar)", f"list.append / pop(0), n={n:,}", medir(listaComoCola, n))]


def conjuntos(n=20000):
    datos = list(range(n))
    propio, nativo = ConjuntoHash(), set()
    for x in datos:
        propio.agregar(x)
        nativo.add(x)
    consultas = random.Random(2).choices(range(2 * n), k=5000)
    return [("Pertenencia a un conjunto", f"ConjuntoHash propio, n={n:,}", medir(lambda: [propio.contiene(x) for x in consultas], 5000)),
            ("Pertenencia a un conjunto", f"set de Python, n={n:,}", medir(lambda: [x in nativo for x in consultas], 5000))]


def ordenamientos():
    filas = []
    for n in (1000, 5000, 20000):
        azar = random.Random(n)
        datos = [azar.randint(0, 10 ** 6) for _ in range(n)]
        if n <= 5000:
            filas.append(("Ordenar", f"Inserción propia, n={n:,}", medir(lambda: insercion(datos), n)))
        filas.append(("Ordenar", f"Merge sort propio, n={n:,}", medir(lambda: mergeSort(datos), n)))
        filas.append(("Ordenar", f"Quick sort propio, n={n:,}", medir(lambda: quickSort(datos), n)))
        filas.append(("Ordenar", f"sorted() de Python, n={n:,}", medir(lambda: sorted(datos), n)))
    return filas


def arboles(n=3000):
    claves = codigos(n)                       # llegan en orden, como los códigos C001, C002...
    filas = []
    for clase in (ArbolBinarioBusqueda, ArbolAVL):
        arbol = clase()

        def construir(arbol=arbol):
            arbol.limpiar()
            for c in claves:
                arbol.insertar(c)
        tiempo = medir(construir, n)
        objetivos = random.Random(3).choices(claves, k=500)
        filas.append(("Índice ordenado con claves en orden", f"{clase.__name__} insertar (altura {arbol.obtenerAltura()}), n={n:,}", tiempo))
        filas.append(("Índice ordenado con claves en orden", f"{clase.__name__} buscar, n={n:,}",
                      medir(lambda: [arbol.buscar(c) for c in objetivos], 500)))
    nativo = {c: c for c in claves}
    filas.append(("Índice ordenado con claves en orden", f"dict de Python buscar (sin orden), n={n:,}",
                  medir(lambda: [nativo.get(c) for c in claves[:500]], 500)))
    return filas


def colaPrioridad(n=20000):
    azar = random.Random(4)
    datos = [azar.randint(0, 10 ** 6) for _ in range(n)]

    def monticulo():
        m = Monticulo()
        for x in datos:
            m.insertar(x, x)
        while not m.estaVacio():
            m.extraer()

    def listaOrdenando():
        lista = list(datos)
        lista.sort()
        while lista:
            lista.pop(0)
    return [("Cola de prioridad (insertar + extraer todo)", f"Montículo propio, n={n:,}", medir(monticulo, n)),
            ("Cola de prioridad (insertar + extraer todo)", f"list ordenada + pop(0), n={n:,}", medir(listaOrdenando, n))]


def listaActivos(n=5000):
    def propia():
        lista = ListaSimple()
        for i in range(n):
            lista.agregarAlFinal(i)
        for i in range(0, n, 10):
            lista.eliminar(lambda x, i=i: x == i)

    def nativa():
        lista = list(range(n))
        for i in range(0, n, 10):
            lista.remove(i)
    return [("Lista de activos (altas + bajas)", f"ListaSimple propia, n={n:,}", medir(propia, n)),
            ("Lista de activos (altas + bajas)", f"list.remove, n={n:,}", medir(nativa, n))]


def medirTodo():
    filas = []
    for n in (1000, 10000, 50000):
        filas += busquedaPorCodigo(n)
    for parte in (insercionAlFinal, pilaYCola, conjuntos, ordenamientos, arboles, colaPrioridad, listaActivos):
        filas += parte()
    return [{"operacion": o, "variante": v, "microsegundosPorOperacion": round(t, 3)} for o, v, t in filas]


if __name__ == "__main__":
    resultados = medirTodo()
    actual = None
    for r in resultados:
        if r["operacion"] != actual:
            actual = r["operacion"]
            print(f"\n{actual}")
        print(f"  {r['variante']:<58} {r['microsegundosPorOperacion']:>12.3f} µs/op")
    if len(sys.argv) > 1:
        with open(sys.argv[1], "w", encoding="utf-8") as archivo:
            json.dump({"python": sys.version.split()[0], "plataforma": sys.platform,
                       "resultados": resultados}, archivo, ensure_ascii=False, indent=1)
