"""Lista enlazada simple (cada nodo apunta al siguiente) con referencia a la cola.

Complejidad: agregar al inicio o al final O(1), eliminar al inicio O(1),
buscar y eliminar por criterio O(n).
"""

from .ListaEnlazada import ListaEnlazada


class NodoSimple:
    __slots__ = ("dato", "siguiente")

    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None


class ListaSimple(ListaEnlazada):

    def agregarAlInicio(self, dato):
        nodo = NodoSimple(dato)
        nodo.siguiente = self.cabeza
        self.cabeza = nodo
        if self.cola is None:
            self.cola = nodo
        self.tamaño += 1

    def agregarAlFinal(self, dato):
        nodo = NodoSimple(dato)
        if self.cola is None:
            self.cabeza = nodo
        else:
            self.cola.siguiente = nodo
        self.cola = nodo
        self.tamaño += 1

    def eliminarInicio(self):
        return self.eliminar(lambda _: True)

    def eliminar(self, criterioFn):
        """Quita el primer elemento que cumple el criterio y lo devuelve (o None)."""
        previo, actual = None, self.cabeza
        while actual is not None:
            if criterioFn(actual.dato):
                if previo is None:
                    self.cabeza = actual.siguiente
                else:
                    previo.siguiente = actual.siguiente
                if actual is self.cola:
                    self.cola = previo
                self.tamaño -= 1
                return actual.dato
            previo, actual = actual, actual.siguiente
        return None
