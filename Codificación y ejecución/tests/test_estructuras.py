"""Pruebas de las estructuras propias: caso exitoso, de borde (vacía, un elemento o
error) y cuello de botella (volumen alto) para cada una."""

import random

import pytest

from estructuras import (VectorDinamico, ListaSimple, ListaDoble, Pila, ColaFIFO, TablaHash,
                         hashSumaAscii, ConjuntoHash, ArbolBinarioBusqueda, ArbolAVL, Monticulo, Grafo)
from estructuras.Algoritmos import (insercion, mergeSort, quickSort, busquedaSecuencial,
                                    busquedaBinaria, busquedaBinariaRecursiva)

N = 20000


# ---------------- Vector dinámico ----------------
def test_vector_exitoso(caso):
    caso.inicio("Vector dinámico", "Exitoso", "Agregar 3 elementos con capacidad inicial 2",
                "Conserva el orden y duplica la capacidad a 4")
    v = VectorDinamico(2)
    for x in "ABC":
        v.agregar(x)
    caso.resultado(f"{v.recorrer()}, capacidad {v.obtenerCapacidad()}")
    assert v.recorrer() == ["A", "B", "C"] and v.obtenerCapacidad() == 4


def test_vector_borde(caso):
    caso.inicio("Vector dinámico", "Borde", "Leer y borrar en un vector vacío; capacidad 0",
                "obtener devuelve None, eliminar devuelve False y capacidad 0 se rechaza")
    v = VectorDinamico()
    with pytest.raises(ValueError):
        VectorDinamico(0)
    caso.resultado(f"obtener(0)={v.obtener(0)}, eliminarxIndice(0)={v.eliminarxIndice(0)}, "
                   f"eliminarUltimo()={v.eliminarUltimo()}, VectorDinamico(0) -> ValueError")
    assert v.obtener(0) is None and v.eliminarxIndice(0) is False and v.eliminarUltimo() is None


def test_vector_cuello(caso, cronometro):
    caso.inicio("Vector dinámico", "Cuello de botella", f"Agregar {N:,} elementos desde capacidad 1",
                "Todos quedan en orden; agregar es O(1) amortizado")
    v = VectorDinamico(1)
    with cronometro() as t:
        for i in range(N):
            v.agregar(i)
    caso.resultado(f"{v.obtenerTamaño():,} elementos, capacidad {v.obtenerCapacidad():,}, {t.segundos:.3f} s")
    caso.nota("La capacidad se duplicó 15 veces; cada copia es O(n) pero ocurre pocas veces.")
    assert v.obtenerTamaño() == N and v.obtener(N - 1) == N - 1 and t.segundos < 2


# ---------------- Lista simple ----------------
def test_lista_simple_exitoso(caso):
    caso.inicio("Lista simple", "Exitoso", "Agregar al final y al inicio y eliminar uno del medio",
                "Orden [0, 1, 3] y tamaño 3")
    lista = ListaSimple()
    for x in (1, 2, 3):
        lista.agregarAlFinal(x)
    lista.agregarAlInicio(0)
    lista.eliminar(lambda x: x == 2)
    caso.resultado(f"{lista.recorrer()} tamaño {len(lista)}")
    assert lista.recorrer() == [0, 1, 3] and len(lista) == 3


def test_lista_simple_borde(caso):
    caso.inicio("Lista simple", "Borde", "Eliminar el único elemento y después agregar al final",
                "La cola se actualiza: queda [9]; eliminar en vacía devuelve None")
    lista = ListaSimple()
    lista.agregarAlFinal(1)
    lista.eliminar(lambda x: x == 1)
    vacia = lista.eliminarInicio()
    lista.agregarAlFinal(9)
    caso.resultado(f"eliminarInicio en vacía={vacia}, luego {lista.recorrer()}")
    assert vacia is None and lista.recorrer() == [9] and lista.cola.dato == 9


def test_lista_simple_cuello(caso, cronometro):
    caso.inicio("Lista simple", "Cuello de botella", f"Agregar {N:,} al final y buscar el último",
                "agregarAlFinal es O(1) gracias a la referencia a la cola")
    lista = ListaSimple()
    with cronometro() as t:
        for i in range(N):
            lista.agregarAlFinal(i)
        ultimo = lista.buscar(lambda x: x == N - 1)
    caso.resultado(f"{len(lista):,} nodos, último={ultimo}, {t.segundos:.3f} s")
    assert ultimo == N - 1 and t.segundos < 2


# ---------------- Lista doble ----------------
def test_lista_doble_exitoso(caso):
    caso.inicio("Lista doble", "Exitoso", "Recorrer hacia adelante y hacia atrás", "[1, 2, 3] y [3, 2, 1]")
    lista = ListaDoble()
    for x in (1, 2, 3):
        lista.agregarAlFinal(x)
    caso.resultado(f"{lista.recorrerAdelante()} y {lista.recorrerAtras()}")
    assert lista.recorrerAdelante() == [1, 2, 3] and lista.recorrerAtras() == [3, 2, 1]


def test_lista_doble_borde(caso):
    caso.inicio("Lista doble", "Borde", "Eliminar el final de una lista de un elemento y de una vacía",
                "Queda vacía con cabeza y cola en None; la segunda vez devuelve None")
    lista = ListaDoble()
    lista.agregarAlInicio("x")
    primero, segundo = lista.eliminarFinal(), lista.eliminarFinal()
    caso.resultado(f"{primero}, {segundo}, cabeza={lista.cabeza}, cola={lista.cola}")
    assert primero == "x" and segundo is None and lista.cabeza is None and lista.cola is None


def test_lista_doble_cuello(caso, cronometro):
    caso.inicio("Lista doble", "Cuello de botella", f"Recorrer {N:,} nodos en ambos sentidos con filtro",
                "Ambos recorridos devuelven los mismos pares, en orden inverso")
    lista = ListaDoble()
    for i in range(N):
        lista.agregarAlFinal(i)
    with cronometro() as t:
        adelante = lista.recorrerAdelante(lambda x: x % 2 == 0)
        atras = lista.recorrerAtras(lambda x: x % 2 == 0)
    caso.resultado(f"{len(adelante):,} pares en cada sentido, {t.segundos:.3f} s")
    assert adelante == atras[::-1] and len(adelante) == N // 2 and t.segundos < 2


# ---------------- Pila ----------------
def test_pila_exitoso(caso):
    caso.inicio("Pila", "Exitoso", "push de A, B, C y pop", "Sale C (último en entrar) y el tope queda en B")
    p = Pila()
    for x in "ABC":
        p.push(x)
    sale = p.pop()
    caso.resultado(f"pop={sale}, peek={p.peek()}")
    assert sale == "C" and p.peek() == "B"


def test_pila_borde(caso):
    caso.inicio("Pila", "Borde", "pop y peek en pila vacía", "Devuelven None sin error")
    p = Pila()
    caso.resultado(f"pop={p.pop()}, peek={p.peek()}, vacía={p.estaVacia()}")
    assert p.pop() is None and p.peek() is None and p.estaVacia()


def test_pila_cuello(caso, cronometro):
    caso.inicio("Pila", "Cuello de botella", f"{N:,} push y {N:,} pop", "Salen en orden inverso exacto")
    p = Pila(1)
    with cronometro() as t:
        for i in range(N):
            p.push(i)
        salida = [p.pop() for _ in range(N)]
    caso.resultado(f"primero en salir {salida[0]}, último {salida[-1]}, {t.segundos:.3f} s")
    assert salida == list(range(N - 1, -1, -1)) and t.segundos < 2


# ---------------- Cola circular ----------------
def test_cola_exitoso(caso):
    caso.inicio("Cola FIFO circular", "Exitoso", "Encolar 3 y desencolar", "Sale el primero que entró")
    c = ColaFIFO()
    for x in ("U1", "U2", "U3"):
        c.encolar(x)
    caso.resultado(f"sale {c.desencolar()}, frente {c.frente()}")
    assert c.recorrer() == ["U2", "U3"]


def test_cola_borde(caso):
    caso.inicio("Cola FIFO circular", "Borde", "Dar la vuelta al arreglo, crecer y quitar del medio",
                "Conserva el orden FIFO tras la vuelta, el crecimiento y eliminarSi")
    c = ColaFIFO(3)
    for x in (1, 2, 3):
        c.encolar(x)
    c.desencolar()
    c.encolar(4)                 # usa la casilla 0: dio la vuelta
    c.encolar(5)                 # se llena y crece
    c.encolarAlFrente(0)
    quitados = c.eliminarSi(lambda x: x == 3)
    caso.resultado(f"{c.recorrer()}, quitados={quitados}, desencolar en vacía={ColaFIFO().desencolar()}")
    assert c.recorrer() == [0, 2, 4, 5] and quitados == 1


def test_cola_cuello(caso, cronometro):
    caso.inicio("Cola FIFO circular", "Cuello de botella", f"{N:,} encolar/desencolar intercalados",
                "Todos salen en orden de llegada")
    c, salida = ColaFIFO(2), []
    with cronometro() as t:
        for i in range(N):
            c.encolar(i)
            if i % 3 == 0:
                salida.append(c.desencolar())
        while not c.estaVacia():
            salida.append(c.desencolar())
    caso.resultado(f"{len(salida):,} elementos en orden, {t.segundos:.3f} s")
    assert salida == list(range(N)) and t.segundos < 2


# ---------------- Tabla hash ----------------
def test_hash_exitoso(caso):
    caso.inicio("Tabla hash (djb2)", "Exitoso", "Insertar, actualizar, buscar y eliminar",
                "La actualización no duplica la clave; buscar tras eliminar da None")
    t = TablaHash()
    t.insertar("U001", "Ana")
    nueva = t.insertar("U001", "Ana María")
    t.insertar("U002", "Luis")
    t.eliminar("U002")
    caso.resultado(f"buscar U001={t.buscar('U001')}, era nueva={nueva}, U002={t.buscar('U002')}, tamaño={len(t)}")
    assert t.buscar("U001") == "Ana María" and t.buscar("U002") is None and len(t) == 1


def test_hash_borde(caso):
    caso.inicio("Tabla hash (djb2)", "Borde", "Tabla de capacidad 2 que debe crecer; eliminar inexistente",
                "Crece a un tamaño primo y no pierde claves; eliminar inexistente devuelve False")
    t = TablaHash(2)
    for i in range(10):
        t.insertar(i, i * i)
    caso.resultado(f"capacidad {t.capacidad}, factor {t.obtenerFactorCarga():.2f}, eliminar(99)={t.eliminar(99)}")
    assert all(t.buscar(i) == i * i for i in range(10)) and t.obtenerFactorCarga() <= 0.75


def test_hash_cuello(caso):
    caso.inicio("Tabla hash (djb2)", "Cuello de botella",
                "2.000 códigos R0001.. en 211 cubetas: djb2 frente a la suma ASCII de la Entrega 1",
                "djb2 reparte mejor: menos comparaciones promedio por búsqueda")
    djb2, ascii_ = TablaHash(211, redimensionar=False), TablaHash(211, hashSumaAscii, redimensionar=False)
    for i in range(2000):
        djb2.insertar(f"R{i:04d}", i)
        ascii_.insertar(f"R{i:04d}", i)
    a, b = djb2.estadisticas(), ascii_.estadisticas()
    caso.resultado(f"djb2: {a['cubetasOcupadas']} cubetas, cadena máx {a['cadenaMaxima']}, "
                   f"{a['comparacionesPromedio']} comp.; ASCII: {b['cubetasOcupadas']} cubetas, "
                   f"cadena máx {b['cadenaMaxima']}, {b['comparacionesPromedio']} comp.")
    caso.nota("Con la suma ASCII 'R0012' y 'R0021' caen en la misma cubeta; djb2 tiene en cuenta el orden.")
    assert a["comparacionesPromedio"] * 3 < b["comparacionesPromedio"]


# ---------------- Conjunto ----------------
def test_conjunto_exitoso(caso):
    caso.inicio("Conjunto hash", "Exitoso", "Agregar elementos distintos y consultar", "Contiene los agregados")
    c = ConjuntoHash()
    c.agregar("U001")
    c.agregar("U002")
    caso.resultado(f"elementos={sorted(c.elementos())}")
    assert "U001" in c and "U003" not in c and len(c) == 2


def test_conjunto_borde(caso):
    caso.inicio("Conjunto hash", "Borde", "Agregar un repetido y eliminar uno que no está",
                "El repetido no se agrega (False) y eliminar devuelve False")
    c = ConjuntoHash()
    c.agregar("C001")
    repetido, eliminar = c.agregar("C001"), c.eliminar("X")
    caso.resultado(f"agregar repetido={repetido}, eliminar inexistente={eliminar}, tamaño={len(c)}")
    assert repetido is False and eliminar is False and len(c) == 1


def test_conjunto_cuello(caso, cronometro):
    caso.inicio("Conjunto hash", "Cuello de botella", f"{N:,} inserciones con la mitad repetidas",
                f"Quedan {N // 2:,} elementos únicos")
    c = ConjuntoHash()
    with cronometro() as t:
        for i in range(N):
            c.agregar(i % (N // 2))
    caso.resultado(f"{len(c):,} únicos, {t.segundos:.3f} s")
    assert len(c) == N // 2 and t.segundos < 2


# ---------------- BST ----------------
def test_bst_exitoso(caso):
    caso.inicio("Árbol binario de búsqueda", "Exitoso", "Insertar C05 C02 C08 C01 C03 y recorrer en orden",
                "Inorden ordenado y búsqueda por clave")
    a = ArbolBinarioBusqueda()
    for k in ("C05", "C02", "C08", "C01", "C03"):
        a.insertar(k, k.lower())
    caso.resultado(f"inorden={a.clavesInorden()}, buscar C03={a.buscar('C03')}, altura={a.obtenerAltura()}")
    assert a.clavesInorden() == ["C01", "C02", "C03", "C05", "C08"] and a.buscar("C03") == "c03"


def test_bst_borde(caso):
    caso.inicio("Árbol binario de búsqueda", "Borde", "Eliminar la raíz con dos hijos, una hoja y una clave inexistente",
                "Sigue ordenado; eliminar inexistente devuelve False")
    a = ArbolBinarioBusqueda()
    for k in (50, 30, 70, 20, 40, 60, 80):
        a.insertar(k)
    resultados = (a.eliminar(50), a.eliminar(20), a.eliminar(99))
    caso.resultado(f"eliminar 50, 20, 99 -> {resultados}; inorden={a.clavesInorden()}")
    assert resultados == (True, True, False) and a.clavesInorden() == [30, 40, 60, 70, 80]


def test_bst_cuello(caso, cronometro):
    n = 3000
    caso.inicio("Árbol binario de búsqueda", "Cuello de botella", f"Insertar {n:,} claves ya ordenadas (peor caso)",
                "El árbol degenera en una lista (altura n) pero no desborda la pila")
    a = ArbolBinarioBusqueda()
    with cronometro() as t:
        for i in range(n):
            a.insertar(i)
    caso.resultado(f"altura {a.obtenerAltura():,}, {t.segundos:.3f} s")
    caso.nota("Por eso el índice de categorías usa AVL: con claves en orden el BST pierde el O(log n).")
    assert a.obtenerAltura() == n and a.clavesInorden() == list(range(n))


# ---------------- AVL ----------------
def test_avl_exitoso(caso):
    caso.inicio("Árbol AVL", "Exitoso", "Insertar 1, 2, 3 (caso RR)", "Una rotación: la raíz pasa a ser 2")
    a = ArbolAVL()
    for k in (1, 2, 3):
        a.insertar(k)
    caso.resultado(f"raíz={a.raiz.clave}, altura={a.obtenerAltura()}, rotaciones={a.rotaciones}")
    assert a.raiz.clave == 2 and a.obtenerAltura() == 2 and a.rotaciones == 1


def test_avl_borde(caso):
    caso.inicio("Árbol AVL", "Borde", "Casos dobles LR y RL y eliminación que desbalancea",
                "Después de cada operación sigue balanceado")
    a = ArbolAVL()
    for k in (30, 10, 20):        # LR
        a.insertar(k)
    lr = a.raiz.clave
    for k in (40, 50, 45, 60):    # incluye RL
        a.insertar(k)
    for k in (10, 20):
        a.eliminar(k)
    caso.resultado(f"raíz tras LR={lr}, inorden={a.clavesInorden()}, balanceado={a.estaBalanceado()}")
    assert lr == 20 and a.estaBalanceado() and a.clavesInorden() == [30, 40, 45, 50, 60]


def test_avl_cuello(caso, cronometro):
    n = N
    caso.inicio("Árbol AVL", "Cuello de botella", f"Insertar {n:,} claves en orden y borrar la mitad al azar",
                "Altura cerca de log2(n) (≈ 15) y balanceado")
    a = ArbolAVL()
    with cronometro() as t:
        for i in range(n):
            a.insertar(i)
        azar = random.Random(1)
        for k in azar.sample(range(n), n // 2):
            a.eliminar(k)
    caso.resultado(f"altura {a.obtenerAltura()} con {len(a):,} nodos, {a.rotaciones:,} rotaciones, {t.segundos:.3f} s")
    assert a.estaBalanceado() and a.obtenerAltura() <= 20 and t.segundos < 5


# ---------------- Montículo ----------------
def test_monticulo_exitoso(caso):
    caso.inicio("Montículo", "Exitoso", "Montículo de máximos con prioridades 3, 9, 1, 7", "Salen 9, 7, 3, 1")
    m = Monticulo(esMaximo=True)
    for p in (3, 9, 1, 7):
        m.insertar(p, f"p{p}")
    salida = [p for p, _ in m.extraerVarios()]
    caso.resultado(str(salida))
    assert salida == [9, 7, 3, 1]


def test_monticulo_borde(caso):
    caso.inicio("Montículo", "Borde", "Extraer de vacío y prioridades empatadas",
                "None en vacío; con empate sale primero el que entró primero")
    m = Monticulo()
    vacio = m.extraer()
    for nombre in ("a", "b", "c"):
        m.insertar(5, nombre)
    empates = [d for _, d in m.extraerVarios()]
    caso.resultado(f"extraer vacío={vacio}, empates={empates}")
    assert vacio is None and empates == ["a", "b", "c"]


def test_monticulo_cuello(caso, cronometro):
    caso.inicio("Montículo", "Cuello de botella", f"{N:,} prioridades al azar y extraer todas",
                "Salen ordenadas; insertar y extraer O(log n)")
    m, azar = Monticulo(), random.Random(3)
    datos = [azar.randint(0, 10 ** 6) for _ in range(N)]
    with cronometro() as t:
        for x in datos:
            m.insertar(x, x)
        salida = [p for p, _ in m.extraerVarios()]
    caso.resultado(f"{len(salida):,} en orden, {t.segundos:.3f} s")
    assert salida == sorted(datos) and t.segundos < 5


# ---------------- Grafo ----------------
def _grafoEjemplo():
    g = Grafo()
    for v in "ABCDEF":
        g.agregarVertice(v)
    for a, b in ("AB", "BC", "CD", "AD", "EF"):
        g.agregarArista(a, b)
    return g


def test_grafo_exitoso(caso):
    caso.inicio("Grafo (lista de adyacencia)", "Exitoso", "BFS, ruta más corta y caminos con backtracking de A a C",
                "Ruta de 2 tramos y dos caminos posibles")
    g = _grafoEjemplo()
    caso.resultado(f"ruta={g.caminoMasCorto('A', 'C')}, caminos={g.todosLosCaminos('A', 'C')}")
    assert len(g.caminoMasCorto("A", "C")) == 3 and len(g.todosLosCaminos("A", "C")) == 2


def test_grafo_borde(caso):
    caso.inicio("Grafo (lista de adyacencia)", "Borde", "Ruta entre componentes distintas, arista repetida, bucle y vértice inexistente",
                "Ruta vacía, False, ValueError y ValueError")
    g = _grafoEjemplo()
    sinRuta, repetida = g.caminoMasCorto("A", "E"), g.agregarArista("A", "B")
    with pytest.raises(ValueError):
        g.agregarArista("A", "A")
    with pytest.raises(ValueError):
        g.vecinos("Z")
    caso.resultado(f"ruta A-E={sinRuta}, arista repetida={repetida}, componentes={g.componentesConexas()}")
    assert sinRuta == [] and repetida is False and len(g.componentesConexas()) == 2


def test_grafo_cuello(caso, cronometro):
    n = 2000
    caso.inicio("Grafo (lista de adyacencia)", "Cuello de botella", f"Cadena de {n:,} vértices: BFS de extremo a extremo",
                f"Ruta de {n - 1:,} tramos en tiempo O(V + E)")
    g = Grafo()
    for i in range(n):
        g.agregarVertice(i)
    for i in range(n - 1):
        g.agregarArista(i, i + 1)
    with cronometro() as t:
        ruta = g.caminoMasCorto(0, n - 1)
    caso.resultado(f"{len(ruta) - 1:,} tramos, {t.segundos:.3f} s")
    assert len(ruta) == n and t.segundos < 2


# ---------------- Ordenamientos y búsquedas ----------------
def test_ordenamientos_exitoso(caso):
    datos = [5, 3, 8, 1, 9, 2]
    caso.inicio("Ordenamientos", "Exitoso", f"Ordenar {datos} con inserción, merge sort y quick sort",
                "Los tres dan [1, 2, 3, 5, 8, 9] y no modifican la lista original")
    resultados = [f(datos) for f in (insercion, mergeSort, quickSort)]
    caso.resultado(f"{resultados[0]} (los tres iguales: {resultados[0] == resultados[1] == resultados[2]})")
    assert all(r == [1, 2, 3, 5, 8, 9] for r in resultados) and datos == [5, 3, 8, 1, 9, 2]


def test_ordenamientos_borde(caso):
    caso.inicio("Ordenamientos", "Borde", "Lista vacía, un elemento y estabilidad con claves iguales",
                "Vacía y unitaria sin error; inserción y merge sort conservan el orden de los empates")
    pares = [("b", 1), ("a", 1), ("c", 0)]
    estables = [f(pares, clave=lambda x: x[1]) for f in (insercion, mergeSort)]
    caso.resultado(f"vacía={mergeSort([])}, uno={quickSort([7])}, estable={estables[0]}")
    assert mergeSort([]) == [] and quickSort([7]) == [7]
    assert all(e == [("c", 0), ("b", 1), ("a", 1)] for e in estables)


def test_ordenamientos_cuello(caso, cronometro):
    n = 5000
    azar = random.Random(5)
    datos = [azar.randint(0, 10 ** 6) for _ in range(n)]
    caso.inicio("Ordenamientos", "Cuello de botella", f"Ordenar {n:,} números al azar con los tres algoritmos",
                "Inserción O(n²) es mucho más lenta que merge sort y quick sort O(n log n)")
    tiempos = {}
    for f in (insercion, mergeSort, quickSort):
        with cronometro() as t:
            assert f(datos) == sorted(datos)
        tiempos[f.__name__] = t.segundos
    caso.resultado(", ".join(f"{k}: {v:.3f} s" for k, v in tiempos.items()))
    caso.nota("Por eso inserción solo se usa en listados pequeños (por categoría o estado).")
    assert tiempos["insercion"] > tiempos["mergeSort"] and tiempos["insercion"] > tiempos["quickSort"]


def test_busquedas_exitoso(caso):
    datos = [1, 3, 5, 7, 9]
    caso.inicio("Búsquedas", "Exitoso", "Buscar 7 en [1, 3, 5, 7, 9]", "Las tres búsquedas devuelven el índice 3")
    r = (busquedaSecuencial(datos, 7), busquedaBinaria(datos, 7), busquedaBinariaRecursiva(datos, 7))
    caso.resultado(str(r))
    assert r == (3, 3, 3)


def test_busquedas_borde(caso):
    caso.inicio("Búsquedas", "Borde", "Lista vacía, valor ausente y valor repetido",
                "-1, -1 y la primera posición del repetido")
    datos = [1, 2, 2, 2, 3]
    r = (busquedaBinaria([], 1), busquedaBinaria(datos, 9), busquedaBinaria(datos, 2), busquedaBinariaRecursiva(datos, 2))
    caso.resultado(str(r))
    assert r == (-1, -1, 1, 1)


def test_busquedas_cuello(caso, cronometro):
    n = 200000
    datos = list(range(0, 2 * n, 2))
    caso.inicio("Búsquedas", "Cuello de botella", f"1.000 búsquedas en {n:,} elementos ordenados",
                "Binaria O(log n) muy por debajo de la secuencial O(n)")
    objetivos = random.Random(9).sample(datos, 1000)
    with cronometro() as tb:
        indices = [busquedaBinaria(datos, x) for x in objetivos]
    with cronometro() as ts:
        for x in objetivos[:50]:
            busquedaSecuencial(datos, x)
    secuencialEstimada = ts.segundos * 20
    caso.resultado(f"binaria: {tb.segundos:.4f} s; secuencial (estimada para 1.000): {secuencialEstimada:.2f} s")
    assert all(datos[i] == x for i, x in zip(indices, objetivos)) and tb.segundos * 10 < secuencialEstimada
