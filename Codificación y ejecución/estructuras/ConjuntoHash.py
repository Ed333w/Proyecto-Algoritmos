"""Conjunto sin repetidos implementado sobre la tabla hash propia.

agregar, contiene y eliminar en O(1) promedio.
"""

from .TablaHash import TablaHash


class ConjuntoHash:

    def __init__(self, capacidad=211):
        self._tabla = TablaHash(capacidad)

    def agregar(self, elemento):
        """Devuelve False si el elemento ya estaba."""
        return self._tabla.insertar(elemento, True)

    def contiene(self, elemento):
        return self._tabla.contiene(elemento)

    def eliminar(self, elemento):
        return self._tabla.eliminar(elemento)

    def elementos(self):
        return self._tabla.claves()

    def limpiar(self):
        self._tabla = TablaHash(self._tabla.capacidad)

    def __len__(self):
        return len(self._tabla)

    def __contains__(self, elemento):
        return self.contiene(elemento)

    def __iter__(self):
        return iter(self.elementos())

    def __str__(self):
        return f"ConjuntoHash(elementos={len(self)})"

    __repr__ = __str__
