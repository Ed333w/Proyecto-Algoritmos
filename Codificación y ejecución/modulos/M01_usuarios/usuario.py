from datetime import datetime

from modulos.comun import fechaATexto

ACTIVO, INACTIVO = "Activo", "Inactivo"

# Tipos de documento aceptados (sigla -> nombre)
TIPOS_DOCUMENTO = (("CC", "Cédula de ciudadanía"), ("TI", "Tarjeta de identidad"),
                   ("CE", "Cédula de extranjería"), ("PA", "Pasaporte"))

class Usuario:
    def __init__(self, codigo, nombre, email, tipoDocumento, numeroDocumento,
                 fechaRegistro=None, estado=ACTIVO):
        self.codigo = codigo
        self.nombre = nombre
        self.email = email
        self.tipoDocumento = tipoDocumento
        self.numeroDocumento = numeroDocumento
        self.fechaRegistro = fechaRegistro or datetime.now()
        self.estado = estado
        self.prestamosActivos = 0

    def esActivo(self):
        return self.estado == ACTIVO

    def darDeBaja(self):
        self.estado = INACTIVO

    def reactivar(self):
        self.estado = ACTIVO

    def sumarPrestamo(self):
        self.prestamosActivos += 1

    def restarPrestamo(self):
        self.prestamosActivos = max(0, self.prestamosActivos - 1)

    def documento(self):
        return f"{self.tipoDocumento} {self.numeroDocumento}"

    def obtenerInfo(self):
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "documento": self.documento(),
            "email": self.email,
            "fechaRegistro": fechaATexto(self.fechaRegistro),
            "estado": self.estado,
            "prestamosActivos": self.prestamosActivos,
        }

    def __eq__(self, otro):
        return isinstance(otro, Usuario) and self.codigo == otro.codigo

    def __hash__(self):
        return hash(self.codigo)

    def __str__(self):
        return f"{self.codigo}: {self.nombre} ({self.documento()}) <{self.email}> [{self.estado}]"

    __repr__ = __str__
