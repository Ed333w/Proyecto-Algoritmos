"""Menú M04 · Turnos y fila de espera."""

from modulos.comun import fechaATexto
from modulos.M07_Inventario import validarOperativo
from .consola import leer, tabla, ejecutarMenu


def solicitar(sesion):
    turnos = sesion.sistema.turnos
    usuario, recurso = leer("Código del usuario: "), leer("Código del recurso: ")
    validarOperativo(sesion.sistema.recursos, recurso)   # un recurso dañado no recibe turnos nuevos
    codigo = turnos.solicitarTurno(usuario, recurso, leer("Sede: "))
    print(f"\n  Turno {codigo} asignado, posición {turnos.posicion(codigo)} en la fila")


def verSiguiente(sesion):
    sistema = sesion.sistema
    recurso = sistema.recursos.obtener(leer("Código del recurso: ")).codigo
    sede = sistema.recursos.validarSede(leer("Sede: "))
    siguiente = sistema.turnos.verSiguiente(recurso, sede)
    print(f"\n  Sigue: {siguiente}" if siguiente else f"\n  Nadie espera {recurso} en {sede}")


def verFila(sesion):
    sistema = sesion.sistema
    recurso = sistema.recursos.obtener(leer("Código del recurso: ")).codigo
    sede = leer("Sede (Enter para todas): ")
    sede = sistema.recursos.validarSede(sede) if sede else None
    fila = sistema.turnos.obtenerFila(recurso, sede)
    tabla(("Turno", "Usuario", "Sede", "Desde"),
          [(s.codigo, s.codigoUsuario, s.sede, fechaATexto(s.fecha)) for s in fila],
          vacio="(nadie en espera)")


def cancelar(sesion):
    solicitud = sesion.sistema.turnos.cancelarSolicitud(leer("Código del turno: "))
    print(f"\n  Turno {solicitud.codigo} cancelado; la fila avanzó")


def consultar(sesion):
    turnos = sesion.sistema.turnos
    solicitud = turnos.buscarSolicitud(leer("Código del turno: "))
    if solicitud is None:
        raise ValueError("Ese turno no existe")
    print(f"\n  {solicitud}")
    if solicitud.estaEnEspera():
        print(f"  Posición en la fila: {turnos.posicion(solicitud.codigo)}")


def menu(sesion):
    ejecutarMenu("M04 · TURNOS Y FILA DE ESPERA", (
        ("Solicitar turno", solicitar),
        ("Ver quién sigue (sin sacarlo de la fila)", verSiguiente),
        ("Ver fila de un recurso", verFila),
        ("Cancelar turno", cancelar),
        ("Consultar turno", consultar),
    ), sesion)
