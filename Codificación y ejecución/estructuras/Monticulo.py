"""Montículo binario (heap) sobre el vector dinámico. Sirve como cola de prioridad.

- esMaximo=False: sale primero la menor prioridad (montículo de mínimos).
- esMaximo=True: sale primero la mayor prioridad (montículo de máximos).
- Con prioridades iguales sale primero el que entró primero (estable).

Complejidad: insertar y extraer O(log n), verTope O(1), construir con n
inserciones O(n log n).
"""

from .VectorDinamico import VectorDinamico


class Monticulo:

    def __init__(self, esMaximo=False):
        self._datos = VectorDinamico()
        self._esMaximo = esMaximo
        self._contador = 0  # desempate por orden de llegada

    def _antes(self, a, b):
        """True si la entrada a debe salir antes que b. Entradas: (prioridad, orden, dato)."""
        if a[0] != b[0]:
            return a[0] > b[0] if self._esMaximo else a[0] < b[0]
        return a[1] < b[1]

    def _subir(self, i):
        while i > 0:
            padre = (i - 1) // 2
            if not self._antes(self._datos.obtener(i), self._datos.obtener(padre)):
                break
            self._datos.intercambiar(i, padre)
            i = padre

    def _bajar(self, i):
        n = len(self._datos)
        while True:
            mejor = i
            for hijo in (2 * i + 1, 2 * i + 2):
                if hijo < n and self._antes(self._datos.obtener(hijo), self._datos.obtener(mejor)):
                    mejor = hijo
            if mejor == i:
                return
            self._datos.intercambiar(i, mejor)
            i = mejor

    def insertar(self, prioridad, dato):
        self._datos.agregar((prioridad, self._contador, dato))
        self._contador += 1
        self._subir(len(self._datos) - 1)

    def extraer(self):
        """Saca el elemento de mayor urgencia. Devuelve (prioridad, dato) o None."""
        if self._datos.estaVacio():
            return None
        tope = self._datos.obtener(0)
        ultimo = self._datos.eliminarUltimo()
        if not self._datos.estaVacio():
            self._datos.asignar(0, ultimo)
            self._bajar(0)
        return tope[0], tope[2]

    def extraerVarios(self, cantidad=None):
        """Extrae hasta 'cantidad' elementos (todos si es None) en orden de prioridad."""
        resultado = []
        while not self.estaVacio() and (cantidad is None or len(resultado) < cantidad):
            resultado.append(self.extraer())
        return resultado

    def verTope(self):
        tope = self._datos.obtener(0)
        return (tope[0], tope[2]) if tope is not None else None

    def estaVacio(self):
        return self._datos.estaVacio()

    def esValido(self):
        """Comprueba la propiedad de montículo (se usa en las pruebas)."""
        n = len(self._datos)
        for i in range(1, n):
            if self._antes(self._datos.obtener(i), self._datos.obtener((i - 1) // 2)):
                return False
        return True

    def __len__(self):
        return len(self._datos)

    def __str__(self):
        tipo = "máximos" if self._esMaximo else "mínimos"
        return f"Monticulo({tipo}, elementos={len(self)})"

    __repr__ = __str__
