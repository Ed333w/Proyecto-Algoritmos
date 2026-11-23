"""M02 · Sede de la red. Cada sede es una fila de la matriz de inventario (M07)
y un vértice del grafo de la red (M09)."""


class Sede:

    def __init__(self, codigo, nombre):
        self.codigo = codigo
        self.nombre = nombre

    def __str__(self):
        return f"{self.codigo}: {self.nombre}"

    __repr__ = __str__
