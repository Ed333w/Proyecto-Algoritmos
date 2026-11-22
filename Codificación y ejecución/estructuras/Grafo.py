"""Grafo no dirigido y no ponderado con lista de adyacencia propia.

- Vértices: tabla hash  id -> lista enlazada simple de vecinos.
- BFS con cola FIFO propia y conjunto propio de visitados: O(V + E).
- Camino más corto en número de tramos con BFS y reconstrucción por padres.
- DFS con pila propia y búsqueda de caminos con backtracking recursivo.
"""

from .TablaHash import TablaHash
from .ConjuntoHash import ConjuntoHash
from .ListaSimple import ListaSimple
from .ColaFIFO import ColaFIFO
from .VectorDinamico import VectorDinamico
from .Pila import Pila
from .Algoritmos import mergeSort


class Grafo:

    def __init__(self):
        self._adyacencia = TablaHash(53)
        self._orden = VectorDinamico()  # orden de alta, para recorrer de forma predecible
        self.cantidadAristas = 0

    # ---- construcción ----
    def agregarVertice(self, vertice):
        if self._adyacencia.contiene(vertice):
            return False
        self._adyacencia.insertar(vertice, ListaSimple())
        self._orden.agregar(vertice)
        return True

    def existeVertice(self, vertice):
        return self._adyacencia.contiene(vertice)

    def _vecinosDe(self, vertice):
        lista = self._adyacencia.buscar(vertice)
        if lista is None:
            raise ValueError(f"El vértice '{vertice}' no existe")
        return lista

    def existeArista(self, a, b):
        return self.existeVertice(a) and self._vecinosDe(a).buscar(lambda v: v == b) is not None

    def agregarArista(self, a, b):
        if a == b:
            raise ValueError("Una sede no se puede conectar consigo misma")
        self._vecinosDe(a)
        self._vecinosDe(b)
        if self.existeArista(a, b):
            return False
        self._vecinosDe(a).agregarAlFinal(b)
        self._vecinosDe(b).agregarAlFinal(a)
        self.cantidadAristas += 1
        return True

    def eliminarArista(self, a, b):
        if not self.existeArista(a, b):
            return False
        self._vecinosDe(a).eliminar(lambda v: v == b)
        self._vecinosDe(b).eliminar(lambda v: v == a)
        self.cantidadAristas -= 1
        return True

    # ---- consultas ----
    def vecinos(self, vertice):
        return self._vecinosDe(vertice).recorrer()

    def vertices(self):
        return self._orden.recorrer()

    def aristas(self):
        """Cada arista una sola vez, como (a, b)."""
        vistas = ConjuntoHash()
        resultado = []
        for a in self.vertices():
            for b in self.vecinos(a):
                if not vistas.contiene((b, a)):
                    vistas.agregar((a, b))
                    resultado.append((a, b))
        return resultado

    def cantidadVertices(self):
        return len(self._orden)

    # ---- BFS ----
    def recorridoAmplitud(self, inicio):
        """Devuelve [(vértice, distancia en tramos)] en orden BFS."""
        self._vecinosDe(inicio)
        distancias = TablaHash()
        distancias.insertar(inicio, 0)
        cola = ColaFIFO()
        cola.encolar(inicio)
        resultado = []
        while not cola.estaVacia():
            actual = cola.desencolar()
            resultado.append((actual, distancias.buscar(actual)))
            for vecino in self._vecinosDe(actual):
                if not distancias.contiene(vecino):
                    distancias.insertar(vecino, distancias.buscar(actual) + 1)
                    cola.encolar(vecino)
        return resultado

    def caminoMasCorto(self, origen, destino):
        """Lista de vértices de origen a destino con el menor número de tramos, o [] si no hay ruta."""
        self._vecinosDe(origen)
        self._vecinosDe(destino)
        padres = TablaHash()
        padres.insertar(origen, None)
        cola = ColaFIFO()
        cola.encolar(origen)
        while not cola.estaVacia():
            actual = cola.desencolar()
            if actual == destino:
                camino = []
                while actual is not None:
                    camino.append(actual)
                    actual = padres.buscar(actual)
                return camino[::-1]
            for vecino in self._vecinosDe(actual):
                if not padres.contiene(vecino):
                    padres.insertar(vecino, actual)
                    cola.encolar(vecino)
        return []

    # ---- DFS (con pila propia) ----
    def recorridoProfundidad(self, inicio):
        self._vecinosDe(inicio)
        visitados = ConjuntoHash()
        return self._dfs(inicio, visitados)

    def _dfs(self, inicio, visitados):
        """DFS iterativo: la pila propia reemplaza a la pila de llamadas, así una red
        larga no supera el límite de recursión de Python. Visita en el mismo orden
        que la versión recursiva (los vecinos se apilan al revés)."""
        resultado = []
        pila = Pila()
        pila.push(inicio)
        while not pila.estaVacia():
            actual = pila.pop()
            if visitados.contiene(actual):
                continue
            visitados.agregar(actual)
            resultado.append(actual)
            for vecino in self.vecinos(actual)[::-1]:
                if not visitados.contiene(vecino):
                    pila.push(vecino)
        return resultado

    def componentesConexas(self):
        """Grupos de vértices conectados entre sí, del más grande al más pequeño."""
        visitados = ConjuntoHash()
        componentes = [self._dfs(v, visitados) for v in self.vertices() if not visitados.contiene(v)]
        return mergeSort(componentes, clave=len, reverso=True)

    # ---- Backtracking (recursivo) ----
    def todosLosCaminos(self, origen, destino, maximo=10, maxTramos=None):
        """Caminos simples de origen a destino, del más corto al más largo.
        Backtracking: avanza a un vecino, explora y deshace la elección. 'maxTramos'
        poda los caminos demasiado largos (y limita la profundidad de la recursión)."""
        self._vecinosDe(origen)
        self._vecinosDe(destino)
        if maxTramos is None:
            maxTramos = self.cantidadVertices() - 1
        caminos = []
        self._backtracking(origen, destino, VectorDinamico(), ConjuntoHash(), caminos,
                           maximo * 5, maxTramos)
        return mergeSort(caminos, clave=len)[:maximo]

    def _backtracking(self, actual, destino, camino, enCamino, caminos, limite, maxTramos):
        if len(caminos) >= limite or len(camino) > maxTramos:
            return
        camino.agregar(actual)
        enCamino.agregar(actual)
        if actual == destino:
            caminos.append(camino.recorrer())
        else:
            for vecino in self._vecinosDe(actual):
                if not enCamino.contiene(vecino):
                    self._backtracking(vecino, destino, camino, enCamino, caminos, limite, maxTramos)
        camino.eliminarUltimo()      # deshacer la elección (backtracking)
        enCamino.eliminar(actual)

    def __str__(self):
        return f"Grafo(V={self.cantidadVertices()}, E={self.cantidadAristas})"

    __repr__ = __str__
