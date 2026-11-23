"""M02 · Clase base abstracta de los recursos (libros, equipos y salas).

Cada subclase declara TIPO y CAMPOS: (atributo, etiqueta, validador). Con esa
única descripción se construye, actualiza, muestra y guarda cualquier recurso,
así que no se repite código por tipo.
"""

from abc import ABC
from datetime import datetime

from modulos.comun import fechaATexto, validarTexto, validarEntero

VIGENTE, DADO_DE_BAJA = "Vigente", "Dado de baja"


def texto(etiqueta):
    return lambda valor: validarTexto(valor, etiqueta)


def entero(etiqueta, minimo=None, maximo=None):
    return lambda valor: validarEntero(valor, etiqueta, minimo, maximo)


class Recurso(ABC):

    TIPO = "Recurso"
    CAMPOS = ()

    def __init__(self, codigo, nombre, categoria=None, fechaRegistro=None, **datosPropios):
        if type(self) is Recurso:
            raise TypeError("Recurso es abstracta: cree un Libro, un Equipo o una Sala")
        self.codigo = codigo
        self.nombre = validarTexto(nombre, "El nombre")
        self.categoria = categoria or None
        self.fechaRegistro = fechaRegistro or datetime.now()
        self.estado = VIGENTE
        self.cantidadPrestamos = 0   # histórico: lo usa el informe de más prestados
        self.prestamosActivos = 0
        # Revisa que todos los datos propios estén presentes y sean validos
        faltantes = [etiqueta for atributo, etiqueta, _ in self.CAMPOS if atributo not in datosPropios] 
        if faltantes:
            raise ValueError(f"Faltan datos del {self.TIPO.lower()}: {', '.join(faltantes)}")
        for atributo, _, validar in self.CAMPOS:
            setattr(self, atributo, validar(datosPropios[atributo]))

    @classmethod
    # Devuele la lista de campos de la clase Recurso que se pueden editar.
    def camposEditables(cls):
        return (("nombre", "Nombre", texto("El nombre")),) + cls.CAMPOS
    # Permite actualizar un campo que sea editable.
    def actualizarCampo(self, atributo, valor):
        for campo, _, validar in self.camposEditables():
            if campo == atributo:
                setattr(self, atributo, validar(valor))
                return
        raise ValueError(f"El campo '{atributo}' no existe para un {self.TIPO.lower()}")
    # Devuelve TRUE si el recurso está vigente, es decir, disponible para prestamo
    def estaVigente(self):
        return self.estado == VIGENTE

    def darDeBaja(self):
        self.estado = DADO_DE_BAJA

    def registrarPrestamo(self):
        self.cantidadPrestamos += 1
        self.prestamosActivos += 1

    def anularPrestamo(self):
        """Deshacer un préstamo: se descuenta del histórico y de los activos."""
        self.cantidadPrestamos = max(0, self.cantidadPrestamos - 1)
        self.prestamosActivos = max(0, self.prestamosActivos - 1)
    # Descuenta un prestamo activo sin afectar el contador.
    def cerrarPrestamo(self):
        self.prestamosActivos = max(0, self.prestamosActivos - 1)
    def reabrirPrestamo(self):
        self.prestamosActivos += 1
    def datosPropios(self):
        return [(etiqueta, getattr(self, atributo)) for atributo, etiqueta, _ in self.CAMPOS]
    # Devuelve toda la informacion del recurso.
    def obtenerInfo(self):
        info = {
            "codigo": self.codigo,
            "tipo": self.TIPO,
            "nombre": self.nombre,
            "categoria": self.categoria or "-",
            "estado": self.estado,
            "fechaRegistro": fechaATexto(self.fechaRegistro),
            "cantidadPrestamos": self.cantidadPrestamos,
        }
        for etiqueta, valor in self.datosPropios():
            info[etiqueta] = valor
        return info
    # Permite comparar recursos mediante su codigo
    def __eq__(self, otro):
        return isinstance(otro, Recurso) and self.codigo == otro.codigo
    # permite usar recursos como claves de diccionario con el fin de agruparlos en categorias
    def __hash__(self):
        return hash(self.codigo)
    # Permie mostrar recurssi como texto
    def __str__(self):
        return f"{self.codigo}: {self.nombre} ({self.TIPO})"

    __repr__ = __str__
