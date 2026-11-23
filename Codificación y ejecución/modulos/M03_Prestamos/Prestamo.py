"""M03 · Préstamo de una unidad de un recurso en una sede."""

from datetime import datetime, timedelta

from modulos.comun import fechaATexto, ahoraSiFalta

ACTIVO, DEVUELTO = "Activo", "Devuelto"
DIAS_LIMITE = 14


class Prestamo:

    def __init__(self, codigo, codigoUsuario, codigoRecurso, sede,
                 fechaPrestamo=None, diasLimite=DIAS_LIMITE):
        self.codigo = codigo
        self.codigoUsuario = codigoUsuario
        self.codigoRecurso = codigoRecurso
        self.sede = sede
        self.fechaPrestamo = fechaPrestamo or datetime.now()
        self.diasLimite = diasLimite
        self.fechaDevolucion = None
        self.estado = ACTIVO

    def estaActivo(self):
        return self.estado == ACTIVO

    def fechaLimite(self):
        return self.fechaPrestamo + timedelta(days=self.diasLimite)

    def devolver(self, fecha=None):
        self.fechaDevolucion = ahoraSiFalta(fecha)
        self.estado = DEVUELTO

    def reactivar(self):
        self.fechaDevolucion = None
        self.estado = ACTIVO

    def diasRestantes(self, ahora=None):
        """Días que faltan para la fecha límite (negativo si ya pasó)."""
        return (self.fechaLimite().date() - ahoraSiFalta(ahora).date()).days

    def diasAtraso(self, ahora=None):
        if not self.estaActivo():
            return 0
        return max(0, -self.diasRestantes(ahora))

    def estaAtrasado(self, ahora=None):
        return self.diasAtraso(ahora) > 0

    def devueltoATiempo(self):
        return (not self.estaActivo()) and self.fechaDevolucion.date() <= self.fechaLimite().date()

    def fueTarde(self, ahora=None):
        """Atrasado ahora mismo o devuelto después de la fecha límite."""
        if self.estaActivo():
            return self.estaAtrasado(ahora)
        return not self.devueltoATiempo()

    def duracionDias(self):
        if self.fechaDevolucion is None:
            return None
        return max(0, (self.fechaDevolucion - self.fechaPrestamo).days)

    def obtenerInfo(self):
        return {
            "codigo": self.codigo,
            "usuario": self.codigoUsuario,
            "recurso": self.codigoRecurso,
            "sede": self.sede,
            "fechaPrestamo": fechaATexto(self.fechaPrestamo),
            "fechaLimite": fechaATexto(self.fechaLimite()),
            "fechaDevolucion": fechaATexto(self.fechaDevolucion) or "-",
            "estado": self.estado,
        }

    def __str__(self):
        return f"{self.codigo}: {self.codigoUsuario} -> {self.codigoRecurso} en {self.sede} [{self.estado}]"

    __repr__ = __str__
