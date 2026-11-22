"""Datos de ejemplo para la exposición. Se cargan la primera vez que se abre el
programa (cuando todavía no hay nada guardado en la carpeta datos/).

Las fechas se calculan desde hoy, así siempre hay un préstamo atrasado, préstamos
por vencer, una fila de espera, un usuario que se atrasa seguido, una laptop
dañada que la gente sigue pidiendo y un computador que lleva días en reparación.

Categorías: las dos principales (Espacios de estudio y Material de estudio, ver
persistencia/categorias_base.py) y algunas subcategorías de Libros para mostrar la
profundidad arbitraria del árbol.
"""

from datetime import datetime, timedelta

from modulos import Sistema
from .categorias_base import crearCategoriasBase

USUARIOS = (("Carlos Lopez", "carlos@uni.edu", "CC", "1010203040"),       # U001
            ("Ana Garcia", "ana@uni.edu", "CC", "1020304050"),            # U002
            ("Luis Perez", "luis@uni.edu", "TI", "1098765432"),           # U003
            ("Maria Rojas", "maria@uni.edu", "CE", "456789"),             # U004
            ("Pedro Diaz", "pedro@uni.edu", "PA", "AB123456"))            # U005

SEDES = ("Centro", "Norte", "Sur", "Occidente")
CONEXIONES = (("Centro", "Norte"), ("Centro", "Sur"), ("Norte", "Sur"))  # Occidente queda aislada

# Subcategorías de Libros (C012) que se suman a las categorías base
CATEGORIAS = (("C013", "Ingenieria", "C012"), ("C014", "Programacion", "C013"),
              ("C015", "Ciencias", "C012"), ("C016", "Fisica", "C015"))

UNIDADES = (("R0001", "Centro", 5), ("R0001", "Norte", 1), ("R0002", "Centro", 2),
            ("R0003", "Centro", 1), ("R0004", "Centro", 3), ("R0004", "Norte", 1),
            ("R0005", "Centro", 2), ("R0007", "Centro", 1), ("R0008", "Norte", 1),
            ("R0009", "Centro", 1), ("R0010", "Centro", 4), ("R0012", "Centro", 1))
# R0011 (Laptop Lenovo) no tiene unidades: su única unidad está dañada y alguien la espera

# (usuario, recurso, sede, hace cuántos días se prestó, días que duró o None si sigue activo)
HISTORIAL = (("U005", "R0002", "Centro", 40, 20),   # devuelto tarde
             ("U002", "R0001", "Centro", 10, 6),
             ("U002", "R0004", "Centro", 5, 3),
             ("U003", "R0001", "Centro", 4, 2),
             ("U004", "R0002", "Centro", 2, 1),
             ("U004", "R0001", "Centro", 3, 2),
             ("U005", "R0001", "Centro", 20, None),  # atrasado 6 días
             ("U003", "R0004", "Centro", 2, None),
             ("U003", "R0005", "Centro", 1, None),
             ("U001", "R0003", "Centro", 13, None),  # vence mañana; la sala queda sin unidades
             ("U004", "R0004", "Norte", 12, None))   # vence en 2 días; Norte queda sin unidades

FILAS = (("U002", "R0003", "Centro"), ("U004", "R0003", "Centro"), ("U001", "R0004", "Norte"),
         ("U002", "R0011", "Centro"))   # espera la laptop que luego se marca dañada

# (recurso, condición, hace cuántos días). Se aplican al final, desde M07 · Inventario.
CONDICIONES = (("R0011", "Dañado", 1),          # dañada con gente esperando: alerta alta
               ("R0012", "En reparación", 20))  # más de 15 días en reparación: alerta


def crearSistemaDemo(hoy=None):
    hoy = hoy or datetime.now()
    s = Sistema()
    for nombre, correo, tipo, numero in USUARIOS:
        s.usuarios.registrar(nombre, correo, tipo, numero)
    for sede in SEDES:
        s.recursos.registrarSede(sede)
    for a, b in CONEXIONES:
        s.red.conectar(a, b)
    crearCategoriasBase(s)
    for codigo, nombre, padre in CATEGORIAS:
        s.categorias.registrarCategoria(codigo, nombre, padre)

    s.recursos.registrarLibro("Python 101", "Guido van Rossum", "978-123", 2020, "C014")       # R0001
    s.recursos.registrarEquipo("Proyector 1", "Proyector", "Epson", "Sala A", "C009")         # R0002
    s.recursos.registrarSala("Sala de Estudio", 30, "Tablero y 6 mesas", "C003")             # R0003
    s.recursos.registrarLibro("Estructuras de Datos", "Cormen", "978-456", 2009, "C013")     # R0004
    s.recursos.registrarEquipo("Portatil Dell", "Portatil", "Latitude", "Centro", "C011")    # R0005
    s.recursos.registrarLibro("Fisica Universitaria", "Sears", "978-789", 2015, "C016")      # R0006
    s.recursos.registrarSala("Sala de Conferencias 301", 60, "Video beam y sonido", "C002")  # R0007
    s.recursos.registrarSala("Sala TV 2", 8, "Televisor de 55 pulgadas", "C005")             # R0008
    s.recursos.registrarSala("Auditorio Central", 200, "Escenario y sonido", "C007")         # R0009
    s.recursos.registrarEquipo("Computador Lab 1", "Computador", "OptiPlex", "Sala de computo", "C010")  # R0010
    s.recursos.registrarEquipo("Laptop Lenovo", "Portatil", "ThinkPad", "Centro", "C011")    # R0011
    s.recursos.registrarEquipo("Computador Lab 2", "Computador", "OptiPlex", "Sala de computo", "C010")  # R0012

    for codigo, sede, unidades in UNIDADES:
        s.inventario.fijarUnidades(codigo, sede, unidades)

    for usuario, recurso, sede, haceDias, duracion in HISTORIAL:
        inicio = hoy - timedelta(days=haceDias)
        codigo = s.prestamos.registrarPrestamo(usuario, recurso, sede, fechaPrestamo=inicio)
        if duracion is not None:
            s.prestamos.registrarDevolucion(codigo, inicio + timedelta(days=duracion))

    for usuario, recurso, sede in FILAS:
        s.turnos.solicitarTurno(usuario, recurso, sede)

    for recurso, condicion, haceDias in CONDICIONES:
        s.cambiarCondicionRecurso(recurso, condicion, hoy - timedelta(days=haceDias))

    s.prestamos.reiniciarDeshacer()   # la precarga no se puede deshacer
    return s
