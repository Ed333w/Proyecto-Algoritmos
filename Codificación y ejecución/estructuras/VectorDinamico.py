"""Vector dinámico: arreglo que duplica su capacidad cuando se llena.

Complejidad: agregar O(1) amortizado, obtener/asignar O(1),
eliminar por índice O(n), buscar O(n).
"""


class VectorDinamico:

    def __init__(self, capacidadInicial=10):
        if capacidadInicial < 1:
            raise ValueError("La capacidad inicial debe ser al menos 1")
        self._capacidadInicial = capacidadInicial
        self.datos = [None] * capacidadInicial
        self.tamaño = 0
        self.capacidad = capacidadInicial

    def _redimensionar(self):
        nuevaCapacidad = self.capacidad * 2
        nuevosDatos = [None] * nuevaCapacidad
        for i in range(self.tamaño):
            nuevosDatos[i] = self.datos[i]
        self.datos = nuevosDatos
        self.capacidad = nuevaCapacidad

    def _validarIndice(self, indice):
        if not 0 <= indice < self.tamaño:
            raise IndexError(f"Índice {indice} fuera de rango (tamaño {self.tamaño})")

    def agregar(self, elemento):
        if self.tamaño == self.capacidad:
            self._redimensionar()
        self.datos[self.tamaño] = elemento
        self.tamaño += 1

    def obtener(self, indice):
        if 0 <= indice < self.tamaño:
            return self.datos[indice]
        return None

    def asignar(self, indice, elemento):
        self._validarIndice(indice)
        self.datos[indice] = elemento

    def intercambiar(self, i, j):
        self._validarIndice(i)
        self._validarIndice(j)
        self.datos[i], self.datos[j] = self.datos[j], self.datos[i]

    def eliminarxIndice(self, indice):
        if not 0 <= indice < self.tamaño:
            return False
        for i in range(indice, self.tamaño - 1):
            self.datos[i] = self.datos[i + 1]
        self.datos[self.tamaño - 1] = None
        self.tamaño -= 1
        return True

    def eliminarUltimo(self):
        if self.tamaño == 0:
            return None
        self.tamaño -= 1
        dato = self.datos[self.tamaño]
        self.datos[self.tamaño] = None
        return dato

    def eliminarxValor(self, elemento):
        return self.eliminarxIndice(self.buscar(elemento))

    def buscar(self, elemento):
        for i in range(self.tamaño):
            if self.datos[i] == elemento:
                return i
        return -1

    def recorrer(self):
        return [self.datos[i] for i in range(self.tamaño)]

    def estaVacio(self):
        return self.tamaño == 0

    def obtenerTamaño(self):
        return self.tamaño

    def obtenerCapacidad(self):
        return self.capacidad

    def limpiar(self):
        self.datos = [None] * self._capacidadInicial
        self.tamaño = 0
        self.capacidad = self._capacidadInicial

    def __len__(self):
        return self.tamaño

    def __iter__(self):
        for i in range(self.tamaño):
            yield self.datos[i]

    def __str__(self):
        return f"VectorDinamico(tamaño={self.tamaño}, capacidad={self.capacidad})"

    __repr__ = __str__
