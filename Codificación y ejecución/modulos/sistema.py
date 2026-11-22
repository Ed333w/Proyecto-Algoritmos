"""Punto único donde se crean y conectan los gestores M01 a M09.

main.py, la persistencia y las pruebas construyen el sistema desde aquí, así la
forma de conectar los módulos está escrita una sola vez. También reúne las dos
operaciones que cruzan módulos.
"""

from .M01_usuarios import GestorUsuarios
from .M02_Recursos import GestorRecursos
from .M03_Prestamos import GestorPrestamos
from .M04_Turnos import GestorTurnos
from .M05_Categoria import GestorCategorias
from .M06_informes import GeneradorInformes
from .M07_Inventario import GestorInventario
from .M08_Asistente_Decisiones import AsistenteDecisiones
from .M09_Red_Sedes import GestorRedSedes


class Sistema:

    def __init__(self):
        self.inventario = GestorInventario()                                         # M07
        self.categorias = GestorCategorias()                                         # M05
        self.usuarios = GestorUsuarios()                                             # M01
        self.recursos = GestorRecursos(self.inventario, self.categorias)             # M02
        self.turnos = GestorTurnos(self.usuarios, self.recursos, self.inventario)    # M04
        self.prestamos = GestorPrestamos(self.usuarios, self.recursos,
                                         self.inventario, self.turnos)               # M03
        self.informes = GeneradorInformes(self.usuarios, self.recursos,
                                          self.prestamos, self.categorias)           # M06
        self.asistente = AsistenteDecisiones(self.usuarios, self.recursos, self.inventario,
                                             self.prestamos, self.turnos)            # M08
        self.red = GestorRedSedes(self.recursos, self.inventario)                    # M09

    def fijarUnidades(self, codigoRecurso, sede, cantidad):
        """RQF-045: fija las unidades y, si quedan disponibles, atiende la fila de esa sede."""
        recurso = self.recursos.validarVigente(codigoRecurso)
        sede = self.recursos.validarSede(sede)
        self.inventario.fijarUnidades(recurso.codigo, sede, cantidad)
        return self.prestamos.atenderFila(recurso.codigo, sede)

    def darDeBajaRecurso(self, codigoRecurso):
        """RQF-008: baja del recurso y cancelación de quienes lo esperaban."""
        recurso = self.recursos.darDeBaja(codigoRecurso)
        return self.turnos.cancelarPorRecurso(recurso.codigo)

    def resumen(self):
        return (f"{self.usuarios.obtenerCantidad()} usuarios, {self.recursos.obtenerCantidad()} recursos, "
                f"{self.recursos.obtenerCantidadSedes()} sedes, {self.categorias.obtenerCantidad()} categorías, "
                f"{self.prestamos.obtenerCantidad()} préstamos, {self.turnos.totalEnEspera()} en espera")
