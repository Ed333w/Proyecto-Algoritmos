"""Lista doblemente enlazada: cada nodo conoce al siguiente y al anterior, así se
recorre hacia adelante y hacia atrás sin invertir nada.

Complejidad: insertar y eliminar en los extremos O(1), recorrer O(n).
"""

from .ListaEnlazada import ListaEnlazada


class NodoDoble:
    __slots__ = ("dato", "siguiente", "anterior")

    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None
        self.anterior = None


class ListaDoble(ListaEnlazada):

    def agregarAlInicio(self, dato):
        nodo = NodoDoble(dato)
        nodo.siguiente = self.cabeza
        if self.cabeza is None:
            self.cola = nodo
        else:
            self.cabeza.anterior = nodo
        self.cabeza = nodo
        self.tamaño += 1

    def agregarAlFinal(self, dato):
        nodo = NodoDoble(dato)
        nodo.anterior = self.cola
        if self.cola is None:
            self.cabeza = nodo
        else:
            self.cola.siguiente = nodo
        self.cola = nodo
        self.tamaño += 1

    def _desenlazar(self, nodo):
        if nodo.anterior is None:
            self.cabeza = nodo.siguiente
        else:
            nodo.anterior.siguiente = nodo.siguiente
        if nodo.siguiente is None:
            self.cola = nodo.anterior
        else:
            nodo.siguiente.anterior = nodo.anterior
        self.tamaño -= 1
        return nodo.dato

    def eliminarInicio(self):
        return self._desenlazar(self.cabeza) if self.cabeza is not None else None

    def eliminarFinal(self):
        return self._desenlazar(self.cola) if self.cola is not None else None

    def recorrerAdelante(self, criterioFn=None):
        return self.recorrer(criterioFn)

    def recorrerAtras(self, criterioFn=None):
        """Del último al primero usando el enlace 'anterior'."""
        resultado = []
        actual = self.cola
        while actual is not None:
            if criterioFn is None or criterioFn(actual.dato):
                resultado.append(actual.dato)
            actual = actual.anterior
        return resultado
