"""Ordenamientos y búsquedas propios.

Todos los ordenamientos reciben 'clave' (qué comparar) y 'reverso' (de mayor a
menor) y devuelven una lista nueva sin modificar la original.

- insercion: básico, O(n²); estable. Rápido con listas pequeñas o casi ordenadas.
- mergeSort: avanzado, O(n log n) siempre; estable.
- quickSort: avanzado, O(n log n) promedio, O(n²) peor caso; pivote central.

Búsquedas (devuelven el índice o -1):
- busquedaSecuencial: O(n), no necesita orden.
- busquedaBinaria / busquedaBinariaRecursiva: O(log n), requieren la lista
  ordenada por la misma clave; con claves repetidas devuelven la primera.
"""


def _identidad(x):
    return x


def _antes(a, b, reverso):
    """True si la clave a debe ir estrictamente antes que la clave b."""
    return a > b if reverso else a < b


# ---------------- Ordenamientos ----------------

def insercion(datos, clave=_identidad, reverso=False):
    a = list(datos)
    for i in range(1, len(a)):
        actual = a[i]
        k = clave(actual)
        j = i - 1
        while j >= 0 and _antes(k, clave(a[j]), reverso):
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = actual
    return a


def mergeSort(datos, clave=_identidad, reverso=False):
    a = list(datos)
    if len(a) <= 1:
        return a
    medio = len(a) // 2
    izq = mergeSort(a[:medio], clave, reverso)
    der = mergeSort(a[medio:], clave, reverso)
    resultado = []
    i = j = 0
    while i < len(izq) and j < len(der):
        # solo toma de la derecha si va estrictamente antes: así es estable
        if _antes(clave(der[j]), clave(izq[i]), reverso):
            resultado.append(der[j])
            j += 1
        else:
            resultado.append(izq[i])
            i += 1
    resultado.extend(izq[i:])
    resultado.extend(der[j:])
    return resultado


def quickSort(datos, clave=_identidad, reverso=False):
    a = list(datos)
    _quickSort(a, 0, len(a) - 1, clave, reverso)
    return a


def _quickSort(a, inicio, fin, clave, reverso):
    while inicio < fin:
        pivote = clave(a[(inicio + fin) // 2])
        i, j = inicio, fin
        while i <= j:
            while _antes(clave(a[i]), pivote, reverso):
                i += 1
            while _antes(pivote, clave(a[j]), reverso):
                j -= 1
            if i <= j:
                a[i], a[j] = a[j], a[i]
                i += 1
                j -= 1
        # recursión sobre la parte pequeña y ciclo sobre la grande: profundidad O(log n)
        if j - inicio < fin - i:
            _quickSort(a, inicio, j, clave, reverso)
            inicio = i
        else:
            _quickSort(a, i, fin, clave, reverso)
            fin = j


# ---------------- Búsquedas ----------------

def busquedaSecuencial(datos, objetivo, clave=_identidad):
    for i, elemento in enumerate(datos):
        if clave(elemento) == objetivo:
            return i
    return -1


def busquedaBinaria(datos, objetivo, clave=_identidad):
    inicio, fin = 0, len(datos)
    while inicio < fin:                      # primera posición con clave >= objetivo
        medio = (inicio + fin) // 2
        if clave(datos[medio]) < objetivo:
            inicio = medio + 1
        else:
            fin = medio
    if inicio < len(datos) and clave(datos[inicio]) == objetivo:
        return inicio
    return -1


def busquedaBinariaRecursiva(datos, objetivo, clave=_identidad, inicio=0, fin=None):
    if fin is None:
        fin = len(datos)
    if inicio >= fin:
        return inicio if inicio < len(datos) and clave(datos[inicio]) == objetivo else -1
    medio = (inicio + fin) // 2
    if clave(datos[medio]) < objetivo:
        return busquedaBinariaRecursiva(datos, objetivo, clave, medio + 1, fin)
    return busquedaBinariaRecursiva(datos, objetivo, clave, inicio, medio)
