"""Árbol binario de búsqueda (BST) clave -> valor.

Las claves deben ser comparables (texto, números o tuplas).
Complejidad: insertar, buscar y eliminar O(h); h = log n en promedio y n en el
peor caso (claves insertadas en orden).

Insertar y eliminar bajan guardando el camino en una pila propia y luego suben
por ese camino llamando a _balancear. En el BST _balancear solo actualiza la
altura; el ArbolAVL hereda todo y redefine _balancear con las rotaciones.
Al no usar recursión, un BST degenerado de miles de nodos no desborda la pila
de llamadas de Python.
"""

from .Pila import Pila

_IZQ, _DER = 0, 1


class NodoArbol:
    __slots__ = ("clave", "valor", "izquierda", "derecha", "altura")

    def __init__(self, clave, valor):
        self.clave = clave
        self.valor = valor
        self.izquierda = None
        self.derecha = None
        self.altura = 1


def _altura(nodo):
    return nodo.altura if nodo is not None else 0


class ArbolBinarioBusqueda:

    def __init__(self):
        self.raiz = None
        self.tamaño = 0

    # ---- punto de extensión: el BST solo actualiza la altura ----
    def _balancear(self, nodo):
        nodo.altura = 1 + max(_altura(nodo.izquierda), _altura(nodo.derecha))
        return nodo

    def _reconstruir(self, camino, hijo):
        """Sube por el camino enlazando cada padre con su hijo y balanceando."""
        while not camino.estaVacia():
            padre, lado = camino.pop()
            if lado == _IZQ:
                padre.izquierda = hijo
            else:
                padre.derecha = hijo
            hijo = self._balancear(padre)
        self.raiz = hijo

    # ---- insertar ----
    def insertar(self, clave, valor=None):
        """Inserta la clave. Devuelve False (y actualiza el valor) si ya existía."""
        camino = Pila()
        nodo = self.raiz
        while nodo is not None:
            if clave == nodo.clave:
                nodo.valor = valor
                return False
            lado = _IZQ if clave < nodo.clave else _DER
            camino.push((nodo, lado))
            nodo = nodo.izquierda if lado == _IZQ else nodo.derecha
        self.tamaño += 1
        self._reconstruir(camino, NodoArbol(clave, valor))
        return True

    # ---- buscar ----
    def buscar(self, clave, defecto=None):
        nodo = self.raiz
        while nodo is not None:
            if clave < nodo.clave:
                nodo = nodo.izquierda
            elif clave > nodo.clave:
                nodo = nodo.derecha
            else:
                return nodo.valor
        return defecto

    def contiene(self, clave):
        centinela = object()
        return self.buscar(clave, centinela) is not centinela

    # ---- eliminar ----
    def eliminar(self, clave):
        camino = Pila()
        nodo = self.raiz
        while nodo is not None and clave != nodo.clave:
            lado = _IZQ if clave < nodo.clave else _DER
            camino.push((nodo, lado))
            nodo = nodo.izquierda if lado == _IZQ else nodo.derecha
        if nodo is None:
            return False
        if nodo.izquierda is not None and nodo.derecha is not None:
            # Dos hijos: se copia el sucesor (mínimo del subárbol derecho) y se borra el sucesor
            camino.push((nodo, _DER))
            sucesor = nodo.derecha
            while sucesor.izquierda is not None:
                camino.push((sucesor, _IZQ))
                sucesor = sucesor.izquierda
            nodo.clave, nodo.valor = sucesor.clave, sucesor.valor
            reemplazo = sucesor.derecha
        else:
            reemplazo = nodo.izquierda if nodo.izquierda is not None else nodo.derecha
        self.tamaño -= 1
        self._reconstruir(camino, reemplazo)
        return True

    # ---- recorridos (iterativos con pila propia) ----
    def _inordenNodos(self):
        pila = Pila()
        nodo = self.raiz
        while nodo is not None or not pila.estaVacia():
            while nodo is not None:
                pila.push(nodo)
                nodo = nodo.izquierda
            nodo = pila.pop()
            yield nodo
            nodo = nodo.derecha

    def recorridoInorden(self):
        """Valores ordenados por clave."""
        return [nodo.valor for nodo in self._inordenNodos()]

    def clavesInorden(self):
        return [nodo.clave for nodo in self._inordenNodos()]

    def recorridoPreorden(self):
        """Claves en preorden (raíz, izquierda, derecha)."""
        resultado = []
        pila = Pila()
        if self.raiz is not None:
            pila.push(self.raiz)
        while not pila.estaVacia():
            nodo = pila.pop()
            resultado.append(nodo.clave)
            if nodo.derecha is not None:
                pila.push(nodo.derecha)
            if nodo.izquierda is not None:
                pila.push(nodo.izquierda)
        return resultado

    def obtenerAltura(self):
        return _altura(self.raiz)

    def obtenerCantidad(self):
        return self.tamaño

    def estaVacio(self):
        return self.raiz is None

    def limpiar(self):
        self.raiz = None
        self.tamaño = 0

    def __len__(self):
        return self.tamaño

    def __contains__(self, clave):
        return self.contiene(clave)

    def __str__(self):
        return f"{self.__class__.__name__}(nodos={self.tamaño}, altura={self.obtenerAltura()})"

    __repr__ = __str__
