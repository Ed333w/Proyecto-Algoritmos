"""Menú M08 · Asistente de decisiones del administrador."""

from modulos.comun import fechaATexto
from .consola import leer, leerEntero, confirmar, tabla, ejecutarMenu
from .menu_prestamos import informarAsignados


def mostrarVencimientos(sistema, dias=2):
    """RQF-051: también se muestra al abrir el programa."""
    proximos = sistema.asistente.vencimientosProximos(dias)
    if not proximos:
        print(f"  No hay préstamos que venzan en los próximos {dias} día(s).")
        return
    filas = []
    for p, restantes in proximos:
        usuario = sistema.usuarios.obtener(p.codigoUsuario)
        cuando = "HOY" if restantes == 0 else f"en {restantes} día(s)"
        filas.append((p.codigo, usuario.nombre, usuario.email, p.codigoRecurso, p.sede, cuando))
    tabla(("Préstamo", "Usuario", "Correo", "Recurso", "Sede", "Vence"), filas)


def mostrarNoOperativos(sistema):
    """RQF-051: aviso al abrir el programa con los recursos que no están operativos."""
    resumen = sistema.asistente.resumenNoOperativos()
    if not resumen:
        print("  Todos los recursos están operativos.")
        return
    print("  Recursos fuera de servicio: " + ", ".join(f"{n} {c.lower()}" for c, n in resumen)
          + ". Detalle en el asistente (M08) > Alertas priorizadas.")


def redistribucion(sesion):
    asistente = sesion.sistema.asistente
    codigo = leer("Código del recurso (Enter para todos): ") or None
    traslados = asistente.recomendarRedistribucion(codigo)
    tabla(("N°", "Recurso", "Desde", "Hacia", "Unidades"),
          [(i, t.codigoRecurso, t.origen, t.destino, t.unidades) for i, t in enumerate(traslados, 1)],
          vacio="(la distribución actual ya atiende la demanda)")
    if traslados and confirmar("\n  ¿Aplicar alguno de estos traslados?"):
        n = leerEntero("Número del traslado: ")
        if not 1 <= n <= len(traslados):
            raise ValueError("Número de traslado inválido")
        asignados = asistente.aplicarTraslado(traslados[n - 1])
        print(f"\n  Hecho: {traslados[n - 1]}")
        informarAsignados(sesion.sistema, asignados)


def compras(sesion):
    cantidad = leerEntero("¿Cuántos recursos mostrar? (Enter = 5): ", 5)
    tabla(("Recurso", "Nombre", "Índice", "En fila", "Préstamos 30 d", "Unidades", "Acción"),
          [(r.codigo, r.nombre, indice, fila, usos, unidades, accion)
           for r, indice, fila, usos, unidades, accion in sesion.sistema.asistente.priorizarCompras(cantidad)],
          vacio="(no hay demanda sin atender)")
    print("\n  Índice = (2 × personas en fila + préstamos de los últimos 30 días) / (unidades + 1)")
    print("  Un recurso dañado o en reparación cuenta con 0 unidades: se propone repararlo o reponerlo.")


def prediccion(sesion):
    p = sesion.sistema.asistente.predecirDisponibilidad(leer("Código del recurso: "))
    r = p["recurso"]
    print(f"\n  {r.codigo} {r.nombre}")
    if not p["operativo"]:
        print(f"  No está operativo ({p['condicion'].lower()}): no se presta ni se recomienda hasta que "
              f"vuelva a Operativo en Inventario (M07).")
        return
    print(f"  Duración promedio de sus préstamos: {p['promedioDias']} días "
          f"({p['muestras']} devoluciones, confianza {int(p['confianza'] * 100)}%)")
    if p["disponibleAhora"]:
        print(f"  Disponible ahora en: {', '.join(p['sedesConUnidades'])}")
    elif p["dias"] is None:
        print("  No tiene unidades ni préstamos activos: no se liberará solo (cargue unidades o compre).")
    else:
        print(f"  Se estima que se libera en {p['dias']} día(s), el {fechaATexto(p['fechaEstimada'])[:10]}, en {p['sede']}")


def alertas(sesion):
    lista = sesion.sistema.asistente.alertasPriorizadas()
    tabla(("Urgencia", "Tipo", "Detalle"), [(a.urgencia, a.tipo, a.mensaje) for a in lista], vacio="(sin alertas)")


def vencimientos(sesion):
    mostrarVencimientos(sesion.sistema, leerEntero("¿Cuántos días de anticipación? (Enter = 2): ", 2))


def menu(sesion):
    ejecutarMenu("M08 · ASISTENTE DE DECISIONES DEL ADMINISTRADOR", (
        ("Recomendar redistribución entre sedes", redistribucion),
        ("Priorizar compras", compras),
        ("Predecir disponibilidad de un recurso", prediccion),
        ("Alertas priorizadas", alertas),
        ("Préstamos próximos a vencer", vencimientos),
    ), sesion)
