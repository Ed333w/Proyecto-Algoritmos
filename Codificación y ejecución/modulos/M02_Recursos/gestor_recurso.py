"""M02 · Gestión de recursos y sedes (RQF-005, 006, 007, 008, 020, 023, 042 y 052).

Estructuras:
- VectorDinamico: todos los recursos en orden de registro.
- TablaHash código -> Recurso: búsqueda por código en O(1) promedio (RQF-020).
- ArbolBinarioBusqueda (nombre, código) -> Recurso: catálogo ordenado por nombre
  (RQF-052). Su recorrido en orden alimenta los listados por nombre y la
  búsqueda binaria por nombre (RQF-024, M06).
- TablaHash nombre de sede -> Sede y VectorDinamico de sedes (RQF-042).
"""

from estructuras import VectorDinamico, TablaHash, ArbolBinarioBusqueda
from estructuras.Algoritmos import insercion, mergeSort
from modulos.comun import GeneradorCodigos, validarTexto
from .recurso import DADO_DE_BAJA
from .libro import Libro
from .equipo import Equipo
from .sala import Sala
from .sede import Sede

TIPOS = (Libro, Equipo, Sala)

# Estados para los listados del RQF-023
DISPONIBLE, PRESTADO, SIN_UNIDADES = "Disponible", "Prestado", "Sin unidades"
ESTADOS = (DISPONIBLE, PRESTADO, SIN_UNIDADES, DADO_DE_BAJA)

# Devuelve la clase de recurso según el tipo (Libro, Equipo o Sala) para no repetir código por tipo.
def claseDeTipo(tipo):
    for clase in TIPOS:
        if clase.TIPO.lower() == str(tipo).strip().lower():
            return clase
    raise ValueError(f"Tipo de recurso '{tipo}' no válido (use Libro, Equipo o Sala)")


def _claveCatalogo(recurso):
    return (recurso.nombre.lower(), recurso.codigo)


class GestorRecursos:

    def __init__(self, gestorInventario, gestorCategorias=None):
        self.inventario = gestorInventario
        self.categorias = gestorCategorias
        self.recursos = VectorDinamico(20)
        self.indice = TablaHash()
        self.catalogo = ArbolBinarioBusqueda()
        self._catalogoOrdenado = None          # arreglo en orden del BST; se rehace solo si cambia
        self.codigos = GeneradorCodigos("R", 4)
        self.sedes = VectorDinamico()
        self.indiceSedes = TablaHash(53)
        self.codigosSedes = GeneradorCodigos("S", 2)

    # ================= Recursos =================
    # Comprueba que la categoria exista
    def _validarCategoria(self, categoria):
        if not categoria:
            return None
        if self.categorias is None:
            raise ValueError("No hay módulo de categorías para asignar la categoría")
        return self.categorias.obtener(categoria).codigo
    # Agrega un recurso al gestor y estructuras de buscqueda mas no un recurso nuevo.
    def _indexar(self, recurso):
        self.recursos.agregar(recurso)
        self.indice.insertar(recurso.codigo, recurso)
        if recurso.estaVigente():
            self._agregarAlCatalogo(recurso)
        self.inventario.registrarRecurso(recurso.codigo)
    # agrega un recurso al catálogo.
    def _agregarAlCatalogo(self, recurso):
        self.catalogo.insertar(_claveCatalogo(recurso), recurso)
        self._catalogoOrdenado = None
    # elimina del catalogo.
    def _quitarDelCatalogo(self, clave):
        self.catalogo.eliminar(clave)
        self._catalogoOrdenado = None
    # Registra un nuevo recurso del tipo especificado, entre Libro, Equipo o Sala, con su categoría y datos propios.
    def registrar(self, tipo, nombre, categoria=None, **datosPropios):
        """RQF-005: crea el recurso del tipo pedido (herencia) con su categoría."""
        clase = claseDeTipo(tipo)
        categoria = self._validarCategoria(categoria)
        recurso = clase(self.codigos.formatear(self.codigos.contador + 1), nombre,
                        categoria, **datosPropios)
        self.codigos.siguiente()   # el código se consume solo si los datos eran válidos
        self._indexar(recurso)
        return recurso.codigo

    def registrarLibro(self, nombre, autor, isbn, añoPublicacion, categoria=None):
        return self.registrar("Libro", nombre, categoria, autor=autor, isbn=isbn,
                              añoPublicacion=añoPublicacion)

    def registrarEquipo(self, nombre, tipoEquipo, modelo, ubicacion, categoria=None):
        return self.registrar("Equipo", nombre, categoria, tipoEquipo=tipoEquipo,
                              modelo=modelo, ubicacion=ubicacion)

    def registrarSala(self, nombre, capacidad, dotacion="Sin dotación", categoria=None):
        return self.registrar("Sala", nombre, categoria, capacidad=capacidad, dotacion=dotacion)
    # Carga un recurso existente en el sistema.
    def cargarExistente(self, recurso):
        """Persistencia: agrega un recurso ya creado conservando su código."""
        if self.indice.contiene(recurso.codigo):
            raise ValueError(f"El recurso {recurso.codigo} está repetido en los datos")
        self.codigos.registrarExistente(recurso.codigo)
        self._indexar(recurso)
    # busca un recurso por su código (RQF-006 y RQF-020). Devuelve None si no existe.
    def buscarxCodigo(self, codigo):
        """RQF-006 y RQF-020: O(1) promedio. Devuelve None si no existe."""
        return self.indice.buscar(str(codigo).strip().upper())
    # Devuelve el recurso con el código dado o lanza error si no existe.
    def obtener(self, codigo):
        recurso = self.buscarxCodigo(codigo)
        if recurso is None:
            raise ValueError(f"El recurso {codigo} no existe")
        return recurso
    # Valida que el recurso exista y su vigencia, al final devuelve el recurso.
    def validarVigente(self, codigo):
        """Regla compartida por préstamos y turnos: el recurso existe y no está de baja."""
        recurso = self.obtener(codigo)
        if not recurso.estaVigente():
            raise ValueError(f"El recurso {recurso.codigo} está dado de baja")
        return recurso
    # busca un recurso por el tipo y nombre.
    def buscarPorTipoYNombre(self, tipo=None, nombre=""):
        """RQF-006: consulta sin conocer el código. Filtra por tipo (opcional) y por parte
        del nombre, sin importar mayúsculas; incluye los dados de baja. Ordenado por nombre."""
        clase = claseDeTipo(tipo) if tipo else None
        texto = str(nombre).strip().lower()
        if clase is None and not texto:
            raise ValueError("Indique el tipo, parte del nombre o ambos")
        encontrados = [r for r in self.recursos
                       if (clase is None or isinstance(r, clase)) and texto in r.nombre.lower()]
        return mergeSort(encontrados, clave=lambda r: (r.nombre.lower(), r.codigo))
    # Actualiza un campo del recurso.
    def actualizar(self, codigo, atributo, valor):
        """RQF-007: cambia un dato del recurso (comunes o propios de su tipo)."""
        recurso = self.validarVigente(codigo)
        if atributo == "categoria":
            recurso.categoria = self._validarCategoria(valor)
            return
        claveAnterior = _claveCatalogo(recurso)
        recurso.actualizarCampo(atributo, valor)
        if atributo == "nombre":
            self._quitarDelCatalogo(claveAnterior)
            self._agregarAlCatalogo(recurso)
    # se usa cuando no se usa mas un recurso, mno lo elimina del sistema
    def darDeBaja(self, codigo):
        """RQF-008: baja lógica. Sale del catálogo y ya no se puede prestar ni pedir en turno."""
        recurso = self.validarVigente(codigo)
        if recurso.prestamosActivos > 0:
            raise ValueError(f"No se puede dar de baja {recurso.codigo}: tiene "
                             f"{recurso.prestamosActivos} préstamo(s) activo(s)")
        recurso.darDeBaja()
        self._quitarDelCatalogo(_claveCatalogo(recurso))
        return recurso

    # ---- listados ----
    def listarTodos(self):
        return self.recursos.recorrer()

    def listarxTipo(self, tipo):
        clase = claseDeTipo(tipo)
        return [r for r in self.recursos if isinstance(r, clase)]

    def catalogoOrdenado(self):
        """RQF-052: recursos vigentes ordenados por nombre (recorrido en orden del BST).
        El arreglo se guarda y solo se rehace (O(n)) cuando el catálogo cambia, así la
        búsqueda binaria por nombre (RQF-024) cuesta O(log n) en las consultas seguidas."""
        if self._catalogoOrdenado is None:
            self._catalogoOrdenado = self.catalogo.recorridoInorden()
        return self._catalogoOrdenado

    def estadoDe(self, recurso):
        if not recurso.estaVigente():
            return DADO_DE_BAJA
        if self.inventario.totalDisponible(recurso.codigo) > 0:
            return DISPONIBLE
        return PRESTADO if recurso.prestamosActivos > 0 else SIN_UNIDADES

    def listarPorCategoria(self, codigoCategoria, incluirSubcategorias=True):
        """RQF-023: recursos de una categoría (y sus subcategorías), ordenados por nombre."""
        if self.categorias is None:
            raise ValueError("No hay módulo de categorías")
        if incluirSubcategorias:
            codigos = self.categorias.codigosSubarbol(codigoCategoria)
            filtrados = [r for r in self.recursos if r.categoria is not None and codigos.contiene(r.categoria)]
        else:
            codigo = self.categorias.obtener(codigoCategoria).codigo
            filtrados = [r for r in self.recursos if r.categoria == codigo]
        return insercion(filtrados, clave=lambda r: r.nombre.lower())

    def listarPorEstado(self, estado):
        """RQF-023: recursos en un estado (Disponible, Prestado, Sin unidades, Dado de baja)."""
        estadoValido = next((e for e in ESTADOS if e.lower() == str(estado).strip().lower()), None)
        if estadoValido is None:
            raise ValueError(f"Estado '{estado}' no válido. Opciones: {', '.join(ESTADOS)}")
        filtrados = [r for r in self.recursos if self.estadoDe(r) == estadoValido]
        return insercion(filtrados, clave=lambda r: r.nombre.lower())

    def obtenerCantidad(self):
        return len(self.recursos)

    # ================= Sedes =================
    def registrarSede(self, nombre):
        """RQF-042: la sede nueva agrega una fila a la matriz de inventario."""
        nombre = validarTexto(nombre, "El nombre de la sede")
        if self.indiceSedes.contiene(nombre.lower()):
            raise ValueError(f"La sede '{nombre}' ya existe")
        sede = Sede(self.codigosSedes.siguiente(), nombre)
        self.sedes.agregar(sede)
        self.indiceSedes.insertar(nombre.lower(), sede)
        self.inventario.registrarSede(nombre)
        return sede

    def buscarSede(self, nombre):
        return self.indiceSedes.buscar(str(nombre).strip().lower())

    def validarSede(self, nombre):
        """Devuelve el nombre oficial de la sede ('centro' -> 'Centro') o lanza error."""
        sede = self.buscarSede(nombre)
        if sede is None:
            raise ValueError(f"La sede '{nombre}' no existe")
        return sede.nombre

    def listarSedes(self):
        return self.sedes.recorrer()

    def nombresSedes(self):
        return [s.nombre for s in self.sedes]

    def obtenerCantidadSedes(self):
        return len(self.sedes)

    def __str__(self):
        return (f"GestorRecursos(libros={len(self.listarxTipo('Libro'))}, "
                f"equipos={len(self.listarxTipo('Equipo'))}, salas={len(self.listarxTipo('Sala'))})")
