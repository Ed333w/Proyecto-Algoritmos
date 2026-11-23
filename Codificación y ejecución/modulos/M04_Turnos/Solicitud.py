"""M04 · Solicitud de turno: un usuario espera un recurso en una sede."""

from datetime import datetime

EN_ESPERA, OTORGADA, CANCELADA = "En espera", "Otorgada", "Cancelada"


class Solicitud:

    def __init__(self, codigo, codigoUsuario, codigoRecurso, sede, fecha=None, estado=EN_ESPERA):
        self.codigo = codigo
        self.codigoUsuario = codigoUsuario
        self.codigoRecurso = codigoRecurso
        self.sede = sede
        self.fecha = fecha or datetime.now()
        self.estado = estado

    def estaEnEspera(self):
        return self.estado == EN_ESPERA

    def otorgar(self):
        self.estado = OTORGADA

    def cancelar(self):
        self.estado = CANCELADA

    def reiniciar(self):
        self.estado = EN_ESPERA

    def __str__(self):
        return f"{self.codigo}: {self.codigoUsuario} espera {self.codigoRecurso} en {self.sede} [{self.estado}]"

    __repr__ = __str__
