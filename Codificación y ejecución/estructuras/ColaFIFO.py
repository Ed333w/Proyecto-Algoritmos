"""Cola FIFO sobre un arreglo circular que crece al llenarse.

Complejidad: encolar, desencolar, frente y encolarAlFrente O(1) amortizado;
eliminarSi y recorrer O(n).
"""


class ColaFIFO:

    def __init__(self, capacidadInicial=10):
        if capacidadInicial < 1:
            raise ValueError("La capacidad inicial debe ser al menos 1")
        self.capacidad = capacidadInicial
        self.datos = [None] * capacidadInicial
        self.inicio = 0
        self.tamaño = 0

    def _indice(self, desplazamiento):
        return (self.inicio + desplazamiento) % self.capacidad

    def _redimensionar(self):
        nuevos = [None] * (self.capacidad * 2)
        for i in range(self.tamaño):
            nuevos[i] = self.datos[self._indice(i)]
        self.datos = nuevos
        self.inicio = 0
        self.capacidad *= 2

    def encolar(self, dato):
        if self.tamaño == self.capacidad:
            self._redimensionar()
        self.datos[self._indice(self.tamaño)] = dato
        self.tamaño += 1

    def encolarAlFrente(self, dato):
        """Devuelve un elemento al frente (se usa al deshacer una asignación)."""
        if self.tamaño == self.capacidad:
            self._redimensionar()
        self.inicio = (self.inicio - 1) % self.capacidad
        self.datos[self.inicio] = dato
        self.tamaño += 1

    def desencolar(self):
        if self.tamaño == 0:
            return None
        dato = self.datos[self.inicio]
        self.datos[self.inicio] = None
        self.inicio = self._indice(1)
        self.tamaño -= 1
        return dato

    def frente(self):
        return self.datos[self.inicio] if self.tamaño else None

    def eliminarSi(self, criterioFn):
        """Quita los elementos que cumplen el criterio conservando el orden. Devuelve cuántos quitó."""
        conservados = 0
        for i in range(self.tamaño):
            dato = self.datos[self._indice(i)]
            if not criterioFn(dato):
                self.datos[self._indice(conservados)] = dato
                conservados += 1
        quitados = self.tamaño - conservados
        for i in range(conservados, self.tamaño):
            self.datos[self._indice(i)] = None
        self.tamaño = conservados
        return quitados

    def contiene(self, criterioFn):
        return any(criterioFn(dato) for dato in self.recorrer())

    def recorrer(self):
        return [self.datos[self._indice(i)] for i in range(self.tamaño)]

    def estaVacia(self):
        return self.tamaño == 0

    def obtenerTamaño(self):
        return self.tamaño

    def limpiar(self):
        self.datos = [None] * self.capacidad
        self.inicio = 0
        self.tamaño = 0

    def __len__(self):
        return self.tamaño

    def __str__(self):
        return f"ColaFIFO(tamaño={self.tamaño}, capacidad={self.capacidad})"

    __repr__ = __str__
