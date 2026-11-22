"""Tabla hash con encadenamiento separado.

- Función hash djb2 (h = h*33 + c) sobre la representación en texto de la clave.
- Capacidad siempre prima y redimensionamiento al superar factor de carga 0.75.
- Complejidad: insertar, buscar y eliminar O(1) promedio, O(n) peor caso.

La suma ASCII de la Entrega 1 se conserva como función (hashSumaAscii) para poder
comparar la calidad de las dos funciones con la misma tabla (ver pruebas).
"""


def _esPrimo(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def primoSiguiente(n):
    candidato = max(2, n)
    while not _esPrimo(candidato):
        candidato += 1
    return candidato


def hashDjb2(clave):
    h = 5381
    for ch in str(clave):
        h = ((h << 5) + h + ord(ch)) & 0xFFFFFFFF
    return h


def hashSumaAscii(clave):
    """Función de la Entrega 1: agrupa claves parecidas (R0012 y R0021 chocan)."""
    return sum(ord(ch) for ch in str(clave))


class _Nodo:
    __slots__ = ("clave", "valor", "sig")

    def __init__(self, clave, valor, sig=None):
        self.clave = clave
        self.valor = valor
        self.sig = sig


class TablaHash:

    FACTOR_MAX = 0.75

    def __init__(self, capacidad=211, funcionHash=hashDjb2, redimensionar=True):
        self.capacidad = primoSiguiente(capacidad)
        self.cubetas = [None] * self.capacidad
        self.tamaño = 0
        self._hash = funcionHash
        self._redimensiona = redimensionar

    def _indice(self, clave):
        return self._hash(clave) % self.capacidad

    def _nodo(self, clave):
        nodo = self.cubetas[self._indice(clave)]
        while nodo is not None:
            if nodo.clave == clave:
                return nodo
            nodo = nodo.sig
        return None

    def insertar(self, clave, valor):
        """Inserta o actualiza. Devuelve True si la clave era nueva."""
        nodo = self._nodo(clave)
        if nodo is not None:
            nodo.valor = valor
            return False
        i = self._indice(clave)
        self.cubetas[i] = _Nodo(clave, valor, self.cubetas[i])
        self.tamaño += 1
        if self._redimensiona and self.tamaño / self.capacidad > self.FACTOR_MAX:
            self._redimensionar()
        return True

    def buscar(self, clave, defecto=None):
        nodo = self._nodo(clave)
        return nodo.valor if nodo is not None else defecto

    def contiene(self, clave):
        return self._nodo(clave) is not None

    def eliminar(self, clave):
        i = self._indice(clave)
        previo, nodo = None, self.cubetas[i]
        while nodo is not None:
            if nodo.clave == clave:
                if previo is None:
                    self.cubetas[i] = nodo.sig
                else:
                    previo.sig = nodo.sig
                self.tamaño -= 1
                return True
            previo, nodo = nodo, nodo.sig
        return False

    def incrementar(self, clave, cantidad=1):
        """Suma 'cantidad' al valor numérico de la clave (0 si no existía)."""
        nuevo = self.buscar(clave, 0) + cantidad
        self.insertar(clave, nuevo)
        return nuevo

    def _redimensionar(self):
        viejas = self.cubetas
        self.capacidad = primoSiguiente(self.capacidad * 2)
        self.cubetas = [None] * self.capacidad
        for nodo in viejas:
            while nodo is not None:
                sig = nodo.sig
                i = self._indice(nodo.clave)
                nodo.sig = self.cubetas[i]
                self.cubetas[i] = nodo
                nodo = sig

    def items(self):
        for nodo in self.cubetas:
            while nodo is not None:
                yield nodo.clave, nodo.valor
                nodo = nodo.sig

    def claves(self):
        return [clave for clave, _ in self.items()]

    def valores(self):
        return [valor for _, valor in self.items()]

    def obtenerCantidad(self):
        return self.tamaño

    def obtenerFactorCarga(self):
        return self.tamaño / self.capacidad

    def estadisticas(self):
        """Datos de colisiones para el informe de eficiencia."""
        ocupadas = maxima = comparaciones = 0
        for nodo in self.cubetas:
            largo = 0
            while nodo is not None:
                largo += 1
                comparaciones += largo  # buscar el k-ésimo de la cadena cuesta k
                nodo = nodo.sig
            if largo:
                ocupadas += 1
                maxima = max(maxima, largo)
        return {
            "capacidad": self.capacidad,
            "elementos": self.tamaño,
            "factorCarga": round(self.obtenerFactorCarga(), 3),
            "cubetasOcupadas": ocupadas,
            "cadenaMaxima": maxima,
            "comparacionesPromedio": round(comparaciones / self.tamaño, 3) if self.tamaño else 0,
        }

    def __len__(self):
        return self.tamaño

    def __contains__(self, clave):
        return self.contiene(clave)

    def __str__(self):
        return f"TablaHash(elementos={self.tamaño}, capacidad={self.capacidad})"

    __repr__ = __str__
