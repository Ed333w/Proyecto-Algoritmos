"""M07 · Condición de los recursos: baja lógica (RQF-008).

Un recurso nunca se borra. Desde Inventario se cambia su condición:

- Operativo: se presta, recibe turnos y el asistente lo tiene en cuenta.
- Dañado / En reparación: temporales. No se presta ni recibe turnos nuevos,
  pero se conserva su fila de espera; al volver a Operativo, la fila se atiende sola.
- Sin uso / Dado de baja: retiran el recurso y cancelan su fila.

Para cualquier condición distinta de Operativo el recurso no puede tener
préstamos activos (primero se registran las devoluciones).

Cómo se integra sin modificar M02, M03 ni M04: la condición se guarda en
recurso.estado. M02 solo reconoce "Vigente" como prestable, así que préstamos (M03),
turnos (M04) y la red de sedes (M09) rechazan el recurso por sí solos. Aquí se
lleva además una tabla hash código -> fecha desde la que está en esa condición.

Estructuras: TablaHash propia (código -> fecha de la condición), O(1) promedio.
"""

from datetime import datetime

from estructuras import TablaHash
from estructuras.Algoritmos import insercion
from modulos.M02_Recursos import VIGENTE, DADO_DE_BAJA
from modulos.M02_Recursos.gestor_recurso import _claveCatalogo

OPERATIVO, DAÑADO, EN_REPARACION, SIN_USO = "Operativo", "Dañado", "En reparación", "Sin uso"
CONDICIONES = (OPERATIVO, DAÑADO, EN_REPARACION, SIN_USO, DADO_DE_BAJA)
CONDICIONES_TEMPORALES = (DAÑADO, EN_REPARACION)    # conservan la fila de espera
CONDICIONES_RETIRO = (SIN_USO, DADO_DE_BAJA)        # cancelan la fila de espera


def _normal(texto):
    return str(texto).strip().lower().replace("ñ", "n").replace("ó", "o")


def validarCondicion(condicion):
    """'dañado', 'DANADO' -> 'Dañado'. 'Vigente' (nombre de M02) -> 'Operativo'."""
    if _normal(condicion) == _normal(VIGENTE):
        return OPERATIVO
    for c in CONDICIONES:
        if _normal(c) == _normal(condicion):
            return c
    raise ValueError(f"Condición '{condicion}' no válida. Opciones: {', '.join(CONDICIONES)}")


def condicionDe(recurso):
    """Condición del recurso con el nombre de M07 ('Vigente' de M02 se muestra como 'Operativo')."""
    return OPERATIVO if recurso.estaVigente() else recurso.estado


def validarOperativo(gestorRecursos, codigoRecurso):
    """Como validarVigente de M02, pero el mensaje dice la condición real (dañado, sin uso...)."""
    recurso = gestorRecursos.obtener(codigoRecurso)
    if not recurso.estaVigente():
        raise ValueError(f"El recurso {recurso.codigo} no está operativo ({recurso.estado.lower()})")
    return recurso


class GestorCondiciones:

    def __init__(self, gestorRecursos, gestorPrestamos, gestorTurnos):
        self.recursos = gestorRecursos
        self.prestamos = gestorPrestamos
        self.turnos = gestorTurnos
        self.desde = TablaHash()          # código -> fecha en que entró a su condición actual

    def cambiar(self, codigoRecurso, condicion, fecha=None):
        """RQF-008. Devuelve (condición anterior, solicitudes canceladas, préstamos asignados)."""
        recurso = self.recursos.obtener(codigoRecurso)
        nueva = validarCondicion(condicion)
        anterior = condicionDe(recurso)
        if nueva == anterior:
            raise ValueError(f"El recurso {recurso.codigo} ya está en condición {anterior}")
        if nueva != OPERATIVO and recurso.prestamosActivos > 0:
            raise ValueError(f"No se puede marcar {recurso.codigo} como {nueva.lower()}: tiene "
                             f"{recurso.prestamosActivos} préstamo(s) activo(s); registre primero su devolución")
        canceladas, asignados = 0, []
        if anterior == OPERATIVO:
            # sale del catálogo ordenado (BST de M02), igual que en la baja de M02
            self.recursos._quitarDelCatalogo(_claveCatalogo(recurso))
        if nueva == OPERATIVO:
            recurso.estado = VIGENTE
            self.recursos._agregarAlCatalogo(recurso)
            self.desde.eliminar(recurso.codigo)
            for sede in self.recursos.nombresSedes():
                asignados += self.prestamos.atenderFila(recurso.codigo, sede)
        else:
            recurso.estado = nueva
            self.desde.insertar(recurso.codigo, fecha or datetime.now())
            if nueva in CONDICIONES_RETIRO:
                canceladas = self.turnos.cancelarPorRecurso(recurso.codigo)
        return anterior, canceladas, asignados

    def cargarExistente(self, codigoRecurso, fecha):
        """Persistencia: la condición ya viene en recursos.txt; aquí solo se recupera su fecha."""
        recurso = self.recursos.obtener(codigoRecurso)
        if not recurso.estaVigente():
            self.desde.insertar(recurso.codigo, fecha)

    def fechaCondicion(self, codigoRecurso):
        return self.desde.buscar(codigoRecurso)

    def diasEnCondicion(self, codigoRecurso, ahora=None):
        fecha = self.desde.buscar(codigoRecurso)
        if fecha is None:
            return 0
        return max(0, ((ahora or datetime.now()).date() - fecha.date()).days)

    def listarNoOperativos(self):
        """Recursos que no están operativos, por condición y nombre."""
        return insercion([r for r in self.recursos.listarTodos() if not r.estaVigente()],
                         clave=lambda r: (r.estado, r.nombre.lower()))

    def listarPorCondicion(self, condicion):
        condicion = validarCondicion(condicion)
        if condicion == OPERATIVO:
            return [r for r in self.recursos.listarTodos() if r.estaVigente()]
        return [r for r in self.listarNoOperativos() if r.estado == condicion]

    def resumen(self):
        """[(condición, cantidad)] de los que no están operativos (para el aviso al abrir)."""
        conteo = TablaHash(11)
        for r in self.listarNoOperativos():
            conteo.incrementar(r.estado)
        return [(c, conteo.buscar(c)) for c in CONDICIONES[1:] if conteo.buscar(c)]
