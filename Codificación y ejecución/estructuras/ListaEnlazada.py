"""Base común de las listas enlazadas simple y doble.

Ambas guardan cabeza, cola y tamaño y se recorren igual desde la cabeza, así
que esas operaciones se escriben una sola vez aquí. Cada lista hija solo
implementa cómo enlazar y desenlazar sus nodos.
"""


class ListaEnlazada:

    def __init__(self):
        self.cabeza = None
        self.cola = None
        self.tamaño = 0

    def __iter__(self):
        actual = self.cabeza
        while actual is not None:
            yield actual.dato
            actual = actual.siguiente

    def recorrer(self, criterioFn=None):
        """Del primero al último; si hay criterio, solo los que lo cumplen. O(n)."""
        return [dato for dato in self if criterioFn is None or criterioFn(dato)]

    def buscar(self, criterioFn):
        for dato in self:
            if criterioFn(dato):
                return dato
        return None

    def ultimo(self):
        return self.cola.dato if self.cola is not None else None

    def obtenerTamaño(self):
        return self.tamaño

    def estaVacia(self):
        return self.tamaño == 0

    def limpiar(self):
        self.cabeza = self.cola = None
        self.tamaño = 0

    def __len__(self):
        return self.tamaño

    def __str__(self):
        return f"{self.__class__.__name__}(tamaño={self.tamaño})"

    __repr__ = __str__
