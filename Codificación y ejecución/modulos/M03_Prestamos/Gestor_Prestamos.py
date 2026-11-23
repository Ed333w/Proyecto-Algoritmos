"""M03 · Préstamos, devoluciones e historial (RQF-011 a 015 y 036 a 039).

Estructuras:
- ListaDoble historial: todos los préstamos en orden; se recorre en ambos sentidos
  y se filtra por usuario (RQF-013) o por recurso (RQF-014).
- ListaSimple activos: préstamos sin devolver (RQF-036); altas y bajas frecuentes.
- TablaHash código -> Prestamo: consulta por código en O(1) promedio (RQF-038).
- Pila: deshacer el último préstamo o devolución (RQF-015).
"""

from estructuras import ListaDoble, ListaSimple, TablaHash, Pila
from modulos.comun import GeneradorCodigos, validarEntero, ahoraSiFalta
from .Prestamo import Prestamo, DIAS_LIMITE


class SinUnidadesError(ValueError):
    """No hay unidades en la sede: el menú ofrece pedir turno (RQF-011 -> RQF-016)."""


_PRESTAMO, _DEVOLUCION = "el préstamo", "la devolución"


class GestorPrestamos:

    def __init__(self, gestorUsuarios, gestorRecursos, gestorInventario, gestorTurnos):
        self.usuarios = gestorUsuarios
        self.recursos = gestorRecursos
        self.inventario = gestorInventario
        self.turnos = gestorTurnos
        self.historial = ListaDoble()
        self.activos = ListaSimple()
        self.indice = TablaHash()
        self.pilaDeshacer = Pila()
        self.codigos = GeneradorCodigos("P", 4)

    def _indexar(self, prestamo):
        self.historial.agregarAlFinal(prestamo)
        self.indice.insertar(prestamo.codigo, prestamo)
        if prestamo.estaActivo():
            self.activos.agregarAlFinal(prestamo)

    def _quitarDeActivos(self, prestamo):
        self.activos.eliminar(lambda p: p is prestamo)

    # ---- RQF-011 ----
    def registrarPrestamo(self, codigoUsuario, codigoRecurso, sede,
                          fechaPrestamo=None, diasLimite=DIAS_LIMITE, _solicitud=None):
        usuario = self.usuarios.validarActivo(codigoUsuario)
        recurso = self.recursos.validarVigente(codigoRecurso)
        sede = self.recursos.validarSede(sede)
        diasLimite = validarEntero(diasLimite, "El plazo en días", minimo=1, maximo=365)
        if not self.inventario.decrementar(recurso.codigo, sede):
            raise SinUnidadesError(f"No hay unidades de {recurso.codigo} en {sede}")
        prestamo = Prestamo(self.codigos.siguiente(), usuario.codigo, recurso.codigo,
                            sede, fechaPrestamo, diasLimite)
        self._indexar(prestamo)
        usuario.sumarPrestamo()
        recurso.registrarPrestamo()
        self.pilaDeshacer.push((_PRESTAMO, prestamo, _solicitud))
        return prestamo.codigo

    # ---- RQF-012 y RQF-017 ----
    def registrarDevolucion(self, codigoPrestamo, fechaDevolucion=None):
        """Cierra el préstamo, devuelve la unidad a su sede y la asigna al siguiente
        de la fila de esa sede. Devuelve los códigos de los préstamos asignados."""
        prestamo = self.obtener(codigoPrestamo)
        if not prestamo.estaActivo():
            raise ValueError(f"El préstamo {prestamo.codigo} ya fue devuelto")
        fecha = ahoraSiFalta(fechaDevolucion)
        if fecha < prestamo.fechaPrestamo:
            raise ValueError("La fecha de devolución no puede ser anterior al préstamo")
        prestamo.devolver(fecha)
        self._quitarDeActivos(prestamo)
        self.inventario.incrementar(prestamo.codigoRecurso, prestamo.sede)
        self.usuarios.obtener(prestamo.codigoUsuario).restarPrestamo()
        self.recursos.obtener(prestamo.codigoRecurso).cerrarPrestamo()
        self.pilaDeshacer.push((_DEVOLUCION, prestamo, None))
        return self.atenderFila(prestamo.codigoRecurso, prestamo.sede)

    def atenderFila(self, codigoRecurso, sede):
        """Mientras haya unidades y gente en la fila, presta en orden de llegada.
        Si quien sigue ya no puede recibir el préstamo (p. ej. quedó inactivo), se cancela."""
        asignados = []
        while self.inventario.obtenerDisponibilidad(codigoRecurso, sede) > 0:
            solicitud = self.turnos.obtenerSiguiente(codigoRecurso, sede)
            if solicitud is None:
                break
            try:
                asignados.append(self.registrarPrestamo(solicitud.codigoUsuario, codigoRecurso,
                                                        sede, _solicitud=solicitud))
            except ValueError:
                solicitud.cancelar()
        return asignados

    # ---- RQF-015 ----
    def deshacer(self):
        """Revierte la última operación. Devuelve una descripción o None si no hay nada."""
        operacion = self.pilaDeshacer.pop()
        if operacion is None:
            return None
        tipo, prestamo, solicitud = operacion
        try:
            if tipo == _PRESTAMO:
                self._deshacerPrestamo(prestamo, solicitud)
            else:
                self._deshacerDevolucion(prestamo)
        except ValueError:
            self.pilaDeshacer.push(operacion)
            raise
        return f"Se deshizo {tipo} {prestamo.codigo}"

    def _deshacerPrestamo(self, prestamo, solicitud):
        # Por ser LIFO, el préstamo a deshacer es el último del historial
        if self.historial.ultimo() is not prestamo:
            raise ValueError(f"El préstamo {prestamo.codigo} ya no es la última operación")
        self.historial.eliminarFinal()
        self._quitarDeActivos(prestamo)
        self.indice.eliminar(prestamo.codigo)
        self.inventario.incrementar(prestamo.codigoRecurso, prestamo.sede)
        self.usuarios.obtener(prestamo.codigoUsuario).restarPrestamo()
        self.recursos.obtener(prestamo.codigoRecurso).anularPrestamo()
        self.codigos.retroceder(prestamo.codigo)
        if solicitud is not None:
            self.turnos.reinsertarAlFrente(solicitud)

    def _deshacerDevolucion(self, prestamo):
        usuario = self.usuarios.validarActivo(prestamo.codigoUsuario)
        recurso = self.recursos.validarVigente(prestamo.codigoRecurso)
        if not self.inventario.decrementar(prestamo.codigoRecurso, prestamo.sede):
            raise ValueError(f"No se puede deshacer la devolución de {prestamo.codigo}: la unidad "
                             f"ya se prestó de nuevo (deshaga primero ese préstamo)")
        prestamo.reactivar()
        self.activos.agregarAlFinal(prestamo)
        usuario.sumarPrestamo()
        recurso.reabrirPrestamo()

    def reiniciarDeshacer(self):
        """Los datos cargados al iniciar no se pueden deshacer."""
        self.pilaDeshacer.limpiar()

    def cargarExistente(self, prestamo):
        """Persistencia: agrega un préstamo guardado sin tocar el inventario (ya viene guardado)."""
        if self.indice.contiene(prestamo.codigo):
            raise ValueError(f"El préstamo {prestamo.codigo} está repetido en los datos")
        usuario = self.usuarios.obtener(prestamo.codigoUsuario)
        recurso = self.recursos.obtener(prestamo.codigoRecurso)
        self.codigos.registrarExistente(prestamo.codigo)
        self._indexar(prestamo)
        recurso.registrarPrestamo()
        if prestamo.estaActivo():
            usuario.sumarPrestamo()
        else:
            recurso.cerrarPrestamo()

    # ---- consultas ----
    def buscarPrestamo(self, codigo):
        """RQF-038: O(1) promedio."""
        return self.indice.buscar(str(codigo).strip().upper())

    def obtener(self, codigo):
        prestamo = self.buscarPrestamo(codigo)
        if prestamo is None:
            raise ValueError(f"El préstamo {codigo} no existe")
        return prestamo

    def listarActivos(self):
        """RQF-036."""
        return self.activos.recorrer()

    def listarAtrasados(self, ahora=None):
        """RQF-037."""
        return self.activos.recorrer(lambda p: p.estaAtrasado(ahora))

    def activosDeUsuario(self, codigoUsuario):
        codigo = self.usuarios.obtener(codigoUsuario).codigo
        return self.activos.recorrer(lambda p: p.codigoUsuario == codigo)

    def activosDeSede(self, sede):
        """RQF-039."""
        sede = self.recursos.validarSede(sede)
        return self.activos.recorrer(lambda p: p.sede == sede)

    def historialUsuario(self, codigoUsuario, haciaAtras=False):
        """RQF-013: recorre la lista doble en el sentido pedido filtrando por usuario."""
        codigo = self.usuarios.obtener(codigoUsuario).codigo
        return self._historial(lambda p: p.codigoUsuario == codigo, haciaAtras)

    def historialRecurso(self, codigoRecurso, haciaAtras=False):
        """RQF-014."""
        codigo = self.recursos.obtener(codigoRecurso).codigo
        return self._historial(lambda p: p.codigoRecurso == codigo, haciaAtras)

    def _historial(self, criterio=None, haciaAtras=False):
        if haciaAtras:
            return self.historial.recorrerAtras(criterio)
        return self.historial.recorrerAdelante(criterio)

    def listarTodos(self, haciaAtras=False):
        return self._historial(None, haciaAtras)

    def obtenerCantidad(self):
        return len(self.historial)

    def obtenerCantidadActivos(self):
        return len(self.activos)

    def __str__(self):
        return f"GestorPrestamos(total={self.obtenerCantidad()}, activos={self.obtenerCantidadActivos()})"
