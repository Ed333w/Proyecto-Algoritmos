"""Pila LIFO sobre el vector dinámico. push, pop y peek en O(1) amortizado."""

from .VectorDinamico import VectorDinamico


class Pila:

    def __init__(self, capacidadInicial=10):
        self._datos = VectorDinamico(capacidadInicial)

    def push(self, dato):
        self._datos.agregar(dato)

    def pop(self):
        return self._datos.eliminarUltimo()

    def peek(self):
        return self._datos.obtener(self._datos.obtenerTamaño() - 1)

    def estaVacia(self):
        return self._datos.estaVacio()

    def obtenerTamaño(self):
        return self._datos.obtenerTamaño()

    def limpiar(self):
        self._datos.limpiar()

    def recorrer(self):
        """Del tope hacia el fondo."""
        return self._datos.recorrer()[::-1]

    def __len__(self):
        return self.obtenerTamaño()

    def __str__(self):
        return f"Pila(tamaño={self.obtenerTamaño()})"

    __repr__ = __str__
