"""M05 · Categorías y subcategorías del catálogo (RQF-025, 026 y 027).

- Árbol n-ario: cada Categoria guarda sus hijas en un vector dinámico, con
  profundidad arbitraria (Ciencias > Física > Óptica ...).
- ArbolAVL código -> Categoria: índice balanceado, búsqueda O(log n) aunque los
  códigos lleguen en orden (C001, C002, ...) (RQF-027).
- ConjuntoHash: impide dos subcategorías con el mismo nombre bajo el mismo padre.
- La consulta del subárbol es recursiva (RQF-026).
"""

from estructuras import ArbolAVL, ConjuntoHash, VectorDinamico
from modulos.comun import validarTexto


class Categoria:

    def __init__(self, codigo, nombre, padre=None):
        self.codigo = codigo
        self.nombre = nombre
        self.padre = padre                 # Categoria o None si es raíz
        self.hijas = VectorDinamico(4)

    def nivel(self):
        return 0 if self.padre is None else self.padre.nivel() + 1

    def ruta(self):
        return self.nombre if self.padre is None else f"{self.padre.ruta()} > {self.nombre}"

    def __str__(self):
        return f"{self.codigo}: {self.nombre}"

    __repr__ = __str__


class GestorCategorias:

    def __init__(self):
        self.indice = ArbolAVL()
        self.raices = VectorDinamico()
        self.nombresPorPadre = ConjuntoHash()

    @staticmethod
    def _normalizar(codigo):
        return validarTexto(codigo, "El código de la categoría").upper()

    def registrarCategoria(self, codigo, nombre, codigoPadre=None):
        """RQF-025: crea una categoría raíz o una subcategoría de 'codigoPadre'."""
        codigo = self._normalizar(codigo)
        nombre = validarTexto(nombre, "El nombre de la categoría")
        if self.indice.contiene(codigo):
            raise ValueError(f"La categoría {codigo} ya existe")
        padre = self.obtener(codigoPadre) if codigoPadre else None
        claveNombre = (padre.codigo if padre else "", nombre.lower())
        if self.nombresPorPadre.contiene(claveNombre):
            ubicacion = f"dentro de {padre.nombre}" if padre else "como categoría principal"
            raise ValueError(f"Ya existe '{nombre}' {ubicacion}")
        categoria = Categoria(codigo, nombre, padre)
        self.indice.insertar(codigo, categoria)
        self.nombresPorPadre.agregar(claveNombre)
        (padre.hijas if padre else self.raices).agregar(categoria)
        return codigo

    def buscar(self, codigo):
        """RQF-026: O(log n) en el AVL. Devuelve None si no existe."""
        return self.indice.buscar(str(codigo).strip().upper())

    def obtener(self, codigo):
        categoria = self.buscar(codigo)
        if categoria is None:
            raise ValueError(f"La categoría {codigo} no existe")
        return categoria

    def subarbol(self, codigo):
        """RQF-026: [(categoria, profundidad relativa)] en preorden, recursivo."""
        resultado = []
        self._recorrer(self.obtener(codigo), 0, resultado)
        return resultado

    def _recorrer(self, categoria, profundidad, resultado):
        resultado.append((categoria, profundidad))
        for hija in categoria.hijas:
            self._recorrer(hija, profundidad + 1, resultado)

    def arbolCompleto(self):
        resultado = []
        for raiz in self.raices:
            self._recorrer(raiz, 0, resultado)
        return resultado

    def codigosSubarbol(self, codigo):
        """Conjunto con el código de la categoría y los de todas sus descendientes."""
        codigos = ConjuntoHash()
        for categoria, _ in self.subarbol(codigo):
            codigos.agregar(categoria.codigo)
        return codigos

    def raizDe(self, codigo):
        categoria = self.obtener(codigo)
        while categoria.padre is not None:
            categoria = categoria.padre
        return categoria

    def listarPorCodigo(self):
        """Recorrido en orden del AVL: categorías ordenadas por código."""
        return self.indice.recorridoInorden()

    def obtenerCantidad(self):
        return len(self.indice)

    def alturaIndice(self):
        return self.indice.obtenerAltura()

    def __str__(self):
        return f"GestorCategorias(categorias={self.obtenerCantidad()}, alturaAVL={self.alturaIndice()})"
