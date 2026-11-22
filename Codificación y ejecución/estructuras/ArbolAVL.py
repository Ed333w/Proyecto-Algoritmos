"""Árbol AVL: BST que se rebalancea después de cada inserción o eliminación.

Hereda insertar, buscar, eliminar y los recorridos del BST; solo redefine
_balancear con las cuatro rotaciones (LL, RR, LR, RL). Así la altura queda en
O(log n) aunque las claves lleguen ordenadas (C001, C002, ...).
"""

from .ArbolBinarioBusqueda import ArbolBinarioBusqueda, _altura


class ArbolAVL(ArbolBinarioBusqueda):

    def __init__(self):
        super().__init__()
        self.rotaciones = 0

    @staticmethod
    def _actualizar(nodo):
        nodo.altura = 1 + max(_altura(nodo.izquierda), _altura(nodo.derecha))

    @staticmethod
    def _factor(nodo):
        return _altura(nodo.izquierda) - _altura(nodo.derecha)

    def _rotarDerecha(self, y):
        x = y.izquierda
        y.izquierda = x.derecha
        x.derecha = y
        self._actualizar(y)
        self._actualizar(x)
        self.rotaciones += 1
        return x

    def _rotarIzquierda(self, x):
        y = x.derecha
        x.derecha = y.izquierda
        y.izquierda = x
        self._actualizar(x)
        self._actualizar(y)
        self.rotaciones += 1
        return y

    def _balancear(self, nodo):
        self._actualizar(nodo)
        factor = self._factor(nodo)
        if factor > 1:                                   # cargado a la izquierda
            if self._factor(nodo.izquierda) < 0:         # caso LR
                nodo.izquierda = self._rotarIzquierda(nodo.izquierda)
            return self._rotarDerecha(nodo)              # caso LL
        if factor < -1:                                  # cargado a la derecha
            if self._factor(nodo.derecha) > 0:           # caso RL
                nodo.derecha = self._rotarDerecha(nodo.derecha)
            return self._rotarIzquierda(nodo)            # caso RR
        return nodo

    def estaBalanceado(self):
        """Verifica la propiedad AVL en todos los nodos (se usa en las pruebas)."""
        def revisar(nodo):
            if nodo is None:
                return True
            return abs(self._factor(nodo)) <= 1 and revisar(nodo.izquierda) and revisar(nodo.derecha)
        return revisar(self.raiz)
