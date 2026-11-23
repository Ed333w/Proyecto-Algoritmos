"""M04 · Turnos y lista de espera (RQF-016, 017, 018, 040 y 041).

Hay una cola FIFO circular por cada par (recurso, sede), guardada en una tabla
hash. Así, cuando vuelve una unidad a una sede, se atiende en estricto orden de
llegada a quien la pidió en esa misma sede (RQF-017, lo ejecuta M03).
"""

from estructuras import ColaFIFO, TablaHash
from modulos.comun import GeneradorCodigos
from .Solicitud import Solicitud


def _clave(codigoRecurso, sede):
    return f"{codigoRecurso}|{sede}"


class GestorTurnos:

    def __init__(self, gestorUsuarios, gestorRecursos, gestorInventario):
        self.usuarios = gestorUsuarios
        self.recursos = gestorRecursos
        self.inventario = gestorInventario
        self.colas = TablaHash()          # "R0001|Centro" -> ColaFIFO de solicitudes
        self.solicitudes = TablaHash()    # código -> Solicitud (todas, para consultarlas)
        self.codigos = GeneradorCodigos("T", 4)

    def _cola(self, codigoRecurso, sede, crear=False):
        cola = self.colas.buscar(_clave(codigoRecurso, sede))
        if cola is None and crear:
            cola = ColaFIFO()
            self.colas.insertar(_clave(codigoRecurso, sede), cola)
        return cola

    def _encolar(self, solicitud):
        self._cola(solicitud.codigoRecurso, solicitud.sede, crear=True).encolar(solicitud)
        self.solicitudes.insertar(solicitud.codigo, solicitud)

    # ---- RQF-016 ----
    def solicitarTurno(self, codigoUsuario, codigoRecurso, sede):
        usuario = self.usuarios.validarActivo(codigoUsuario)
        recurso = self.recursos.validarVigente(codigoRecurso)
        sede = self.recursos.validarSede(sede)
        if self.inventario.obtenerDisponibilidad(recurso.codigo, sede) > 0:
            raise ValueError(f"Hay unidades de {recurso.codigo} en {sede}: registre el préstamo")
        if self.estaEnEspera(usuario.codigo, recurso.codigo, sede):
            raise ValueError(f"{usuario.codigo} ya está en la fila de {recurso.codigo} en {sede}")
        solicitud = Solicitud(self.codigos.siguiente(), usuario.codigo, recurso.codigo, sede)
        self._encolar(solicitud)
        return solicitud.codigo

    def cargarExistente(self, solicitud):
        """Persistencia: las que estaban en espera vuelven a su fila en el mismo orden."""
        self.codigos.registrarExistente(solicitud.codigo)
        if solicitud.estaEnEspera():
            self._encolar(solicitud)
        else:
            self.solicitudes.insertar(solicitud.codigo, solicitud)

    def estaEnEspera(self, codigoUsuario, codigoRecurso, sede):
        cola = self._cola(codigoRecurso, sede)
        return cola is not None and cola.contiene(lambda s: s.codigoUsuario == codigoUsuario)

    def posicion(self, codigoSolicitud):
        solicitud = self.buscarSolicitud(codigoSolicitud)
        if solicitud is None or not solicitud.estaEnEspera():
            return 0
        fila = self.obtenerFila(solicitud.codigoRecurso, solicitud.sede)
        return next(i for i, s in enumerate(fila, 1) if s is solicitud)

    # ---- RQF-017 (M03 llama a obtenerSiguiente al devolver) ----
    def verSiguiente(self, codigoRecurso, sede):
        """RQF-040: quién sigue, sin sacarlo de la fila."""
        cola = self._cola(codigoRecurso, sede)
        return cola.frente() if cola is not None else None

    def obtenerSiguiente(self, codigoRecurso, sede):
        cola = self._cola(codigoRecurso, sede)
        if cola is None or cola.estaVacia():
            return None
        solicitud = cola.desencolar()
        solicitud.otorgar()
        return solicitud

    def reinsertarAlFrente(self, solicitud):
        """Deshacer una asignación: la solicitud recupera el primer lugar."""
        solicitud.reiniciar()
        self._cola(solicitud.codigoRecurso, solicitud.sede, crear=True).encolarAlFrente(solicitud)

    # ---- RQF-018 ----
    def obtenerFila(self, codigoRecurso, sede=None):
        """Solicitudes en espera en orden de llegada (de una sede o de todas)."""
        if sede is not None:
            cola = self._cola(codigoRecurso, sede)
            return cola.recorrer() if cola is not None else []
        fila = []
        for nombreSede in self.recursos.nombresSedes():
            fila.extend(self.obtenerFila(codigoRecurso, nombreSede))
        return fila

    def cantidadEspera(self, codigoRecurso, sede=None):
        if sede is not None:
            cola = self._cola(codigoRecurso, sede)
            return cola.obtenerTamaño() if cola is not None else 0
        return sum(self.cantidadEspera(codigoRecurso, s) for s in self.recursos.nombresSedes())

    # ---- RQF-041 ----
    def cancelarSolicitud(self, codigoSolicitud):
        solicitud = self.buscarSolicitud(codigoSolicitud)
        if solicitud is None:
            raise ValueError(f"La solicitud {codigoSolicitud} no existe")
        if not solicitud.estaEnEspera():
            raise ValueError(f"La solicitud {solicitud.codigo} ya está {solicitud.estado.lower()}")
        self._cola(solicitud.codigoRecurso, solicitud.sede).eliminarSi(lambda s: s is solicitud)
        solicitud.cancelar()
        return solicitud

    def cancelarPorRecurso(self, codigoRecurso):
        """Cuando un recurso se da de baja, sus filas se cancelan."""
        canceladas = 0
        for solicitud in self.obtenerFila(codigoRecurso):
            self.cancelarSolicitud(solicitud.codigo)
            canceladas += 1
        return canceladas

    def buscarSolicitud(self, codigo):
        return self.solicitudes.buscar(str(codigo).strip().upper())

    def listarSolicitudes(self):
        """Primero las que esperan, en el orden de su fila; luego las cerradas.
        Ese orden es el que se guarda en disco para reconstruir las filas igual."""
        enEspera = [s for cola in self.colas.valores() for s in cola.recorrer()]
        cerradas = [s for s in self.solicitudes.valores() if not s.estaEnEspera()]
        return enEspera + cerradas

    def totalEnEspera(self):
        return sum(cola.obtenerTamaño() for cola in self.colas.valores())

    def __str__(self):
        return f"GestorTurnos(en espera={self.totalEnEspera()})"
