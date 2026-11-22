"""Menú M03 · Préstamos y devoluciones."""

from modulos.M03_Prestamos import SinUnidadesError
from modulos.comun import fechaATexto
from .consola import leer, confirmar, tabla, ejecutarMenu


def mostrarPrestamos(prestamos, ahora=None):
    tabla(("Código", "Usuario", "Recurso", "Sede", "Prestado", "Vence", "Estado"),
          [(p.codigo, p.codigoUsuario, p.codigoRecurso, p.sede, fechaATexto(p.fechaPrestamo),
            fechaATexto(p.fechaLimite())[:10],
            f"Atrasado {p.diasAtraso(ahora)} d" if p.estaAtrasado(ahora) else p.estado)
           for p in prestamos])


def informarAsignados(sistema, asignados):
    for codigo in asignados:
        p = sistema.prestamos.buscarPrestamo(codigo)
        print(f"  Asignado al siguiente de la fila: {codigo} para {p.codigoUsuario} en {p.sede}")


def registrar(sesion):
    sistema = sesion.sistema
    usuario, recurso, sede = leer("Código del usuario: "), leer("Código del recurso: "), leer("Sede: ")
    try:
        codigo = sistema.prestamos.registrarPrestamo(usuario, recurso, sede)
    except SinUnidadesError as error:
        print(f"\n  {error}")
        cercana = sistema.red.sedeMasCercanaConRecurso(sede, recurso)
        if cercana:
            ruta = " -> ".join(sistema.red.rutaMasCorta(sede, cercana[0]))
            print(f"  Sede más cercana con unidades: {cercana[0]} a {cercana[1]} tramo(s) "
                  f"({cercana[2]} unidades). Camino: {ruta}")
        if confirmar("  ¿Desea pedir turno en la fila de esta sede?"):
            turno = sistema.turnos.solicitarTurno(usuario, recurso, sede)
            print(f"\n  Turno {turno} asignado, posición {sistema.turnos.posicion(turno)}")
        return
    p = sistema.prestamos.buscarPrestamo(codigo)
    print(f"\n  Préstamo {codigo} registrado. Fecha límite: {fechaATexto(p.fechaLimite())[:10]}")


def devolver(sesion):
    sistema = sesion.sistema
    codigo = leer("Código del préstamo: ")
    asignados = sistema.prestamos.registrarDevolucion(codigo)
    print(f"\n  Devolución de {codigo.upper()} registrada")
    informarAsignados(sistema, asignados)


def deshacer(sesion):
    resultado = sesion.sistema.prestamos.deshacer()
    print(f"\n  {resultado or 'No hay operaciones para deshacer'}")


def consultar(sesion):
    p = sesion.sistema.prestamos.obtener(leer("Código del préstamo: "))
    for campo, valor in p.obtenerInfo().items():
        print(f"  {campo:<16} {valor}")
    if p.estaAtrasado():
        print(f"  {'atraso':<16} {p.diasAtraso()} día(s)")


def deUsuario(sesion):
    prestamos = sesion.sistema.prestamos
    codigo = leer("Código del usuario: ")
    print("\n  Préstamos activos:")
    mostrarPrestamos(prestamos.activosDeUsuario(codigo))
    atras = leer("\n  Historial: 1 = del más antiguo al más reciente, 2 = al revés: ") == "2"
    mostrarPrestamos(prestamos.historialUsuario(codigo, haciaAtras=atras))


def deRecurso(sesion):
    codigo = leer("Código del recurso: ")
    mostrarPrestamos(sesion.sistema.prestamos.historialRecurso(codigo))


def historialCompleto(sesion):
    atras = leer("1 = del más antiguo al más reciente, 2 = al revés: ") == "2"
    mostrarPrestamos(sesion.sistema.prestamos.listarTodos(haciaAtras=atras))


def menu(sesion):
    ejecutarMenu("M03 · PRÉSTAMOS Y DEVOLUCIONES", (
        ("Registrar préstamo", registrar),
        ("Registrar devolución", devolver),
        ("Deshacer última operación (pila)", deshacer),
        ("Listar préstamos activos", lambda s: mostrarPrestamos(s.sistema.prestamos.listarActivos())),
        ("Listar préstamos atrasados", lambda s: mostrarPrestamos(s.sistema.prestamos.listarAtrasados())),
        ("Consultar préstamo por código", consultar),
        ("Préstamos activos por sede", lambda s: mostrarPrestamos(s.sistema.prestamos.activosDeSede(leer("Sede: ")))),
        ("Préstamos e historial de un usuario", deUsuario),
        ("Historial de un recurso", deRecurso),
        ("Historial completo (lista doble)", historialCompleto),
    ), sesion)
