"""Menú M07 · Inventario por sede."""

from modulos.M07_Inventario import CONDICIONES, condicionDe
from .consola import leer, leerEntero, confirmar, tabla, ejecutarMenu
from .menu_prestamos import informarAsignados
from .menu_recursos import elegirRecurso


def disponibilidad(sesion):
    sistema = sesion.sistema
    recurso = elegirRecurso(sesion)      # lista de códigos; Enter para buscar por tipo y nombre
    print(f"\n  {recurso.codigo} {recurso.nombre}")
    sede = leer("Sede (Enter para todas): ")
    if sede:
        sede = sistema.recursos.validarSede(sede)
        print(f"\n  {recurso.codigo} en {sede}: {sistema.inventario.obtenerDisponibilidad(recurso.codigo, sede)} unidad(es)")
    else:
        tabla(("Sede", "Unidades"), sistema.inventario.disponibilidadPorSede(recurso.codigo))


def fijarUnidades(sesion):
    sistema = sesion.sistema
    recurso = elegirRecurso(sesion).codigo
    sede = leer("Sede: ")
    asignados = sistema.fijarUnidades(recurso, sede, leer("Unidades disponibles: "))
    print("\n  Unidades actualizadas")
    informarAsignados(sistema, asignados)


def matrizSedeDia(sesion):
    sistema = sesion.sistema
    recurso = elegirRecurso(sesion)
    dias = leerEntero("Días a proyectar (Enter = 7): ", 7)
    sedes, fechas, matriz = sistema.inventario.matrizSedeDia(recurso.codigo, sistema.prestamos.listarActivos(), dias)
    print(f"\n  Unidades proyectadas de {recurso.codigo} {recurso.nombre} (suma las que vuelven en su fecha límite)\n")
    tabla(["Sede"] + [f.strftime("%d/%m") for f in fechas],
          [[sede] + fila for sede, fila in zip(sedes, matriz)])


def cambiarCondicion(sesion):
    """RQF-008: baja lógica. El recurso nunca se borra y puede volver a Operativo."""
    sistema = sesion.sistema
    recurso = elegirRecurso(sesion)
    print(f"\n  {recurso.codigo} {recurso.nombre}: condición actual {condicionDe(recurso)}")
    for i, condicion in enumerate(CONDICIONES, 1):
        print(f"  {i}. {condicion}")
    eleccion = leerEntero("Nueva condición: ")
    if not 1 <= eleccion <= len(CONDICIONES):
        raise ValueError("Condición inválida")
    nueva = CONDICIONES[eleccion - 1]
    espera = sistema.turnos.cantidadEspera(recurso.codigo)
    if espera and nueva in ("Sin uso", "Dado de baja") and not confirmar(
            f"  Hay {espera} persona(s) en fila; se cancelarán sus solicitudes. ¿Continuar?"):
        print("\n  No se hizo ningún cambio")
        return
    canceladas, asignados = sistema.cambiarCondicionRecurso(recurso.codigo, nueva)
    print(f"\n  {recurso.codigo} {recurso.nombre} ahora está {condicionDe(recurso).lower()}")
    if not recurso.estaVigente():
        print("  No se presta, no recibe turnos y el asistente deja de recomendarlo; su historial se conserva.")
    if canceladas:
        print(f"  Solicitudes canceladas: {canceladas}")
    informarAsignados(sistema, asignados)


def noOperativos(sesion):
    condiciones = sesion.sistema.condiciones
    tabla(("Código", "Tipo", "Nombre", "Condición", "Desde hace", "En fila"),
          [(r.codigo, r.TIPO, r.nombre, r.estado, f"{condiciones.diasEnCondicion(r.codigo)} día(s)",
            sesion.sistema.turnos.cantidadEspera(r.codigo)) for r in condiciones.listarNoOperativos()],
          vacio="(todos los recursos están operativos)")


def menu(sesion):
    ejecutarMenu("M07 · INVENTARIO", (
        ("Matriz sede × recurso", lambda s: print(s.sistema.inventario.mostrarMatriz())),
        ("Disponibilidad de un recurso por sede", disponibilidad),
        ("Fijar unidades de un recurso en una sede", fijarUnidades),
        ("Matriz sede × día (proyección)", matrizSedeDia),
        ("Cambiar condición de un recurso (dañado, en reparación, sin uso, de baja u operativo)", cambiarCondicion),
        ("Recursos que no están operativos", noOperativos),
    ), sesion)
