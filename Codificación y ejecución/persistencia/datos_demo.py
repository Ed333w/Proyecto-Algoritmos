"""Datos de ejemplo para la exposición. Se cargan la primera vez que se abre el
programa (cuando todavía no hay nada guardado en la carpeta datos/).

Las fechas se calculan desde hoy, así siempre hay un préstamo atrasado, préstamos
por vencer, una fila de espera y un usuario que se atrasa seguido.
"""

from datetime import datetime, timedelta

from modulos import Sistema

USUARIOS = (("Carlos Lopez", "carlos@uni.edu", "CC", "1010203040"),       # U001
            ("Ana Garcia", "ana@uni.edu", "CC", "1020304050"),            # U002
            ("Luis Perez", "luis@uni.edu", "TI", "1098765432"),           # U003
            ("Maria Rojas", "maria@uni.edu", "CE", "456789"),             # U004
            ("Pedro Diaz", "pedro@uni.edu", "PA", "AB123456"))            # U005

SEDES = ("Centro", "Norte", "Sur", "Occidente")
CONEXIONES = (("Centro", "Norte"), ("Centro", "Sur"), ("Norte", "Sur"))  # Occidente queda aislada

CATEGORIAS = (("C001", "Ciencias", None), ("C002", "Ingenieria", None), ("C003", "Literatura", None),
              ("C004", "Computacion", "C002"), ("C005", "Programacion", "C004"),
              ("C006", "Fisica", "C001"))

UNIDADES = (("R0001", "Centro", 5), ("R0001", "Norte", 1), ("R0002", "Centro", 2),
            ("R0003", "Centro", 1), ("R0004", "Centro", 3), ("R0004", "Norte", 1),
            ("R0005", "Centro", 2))

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

FILAS = (("U002", "R0003", "Centro"), ("U004", "R0003", "Centro"), ("U001", "R0004", "Norte"))


def crearSistemaDemo(hoy=None):
    hoy = hoy or datetime.now()
    s = Sistema()
    for nombre, correo, tipo, numero in USUARIOS:
        s.usuarios.registrar(nombre, correo, tipo, numero)
    for sede in SEDES:
        s.recursos.registrarSede(sede)
    for a, b in CONEXIONES:
        s.red.conectar(a, b)
    for codigo, nombre, padre in CATEGORIAS:
        s.categorias.registrarCategoria(codigo, nombre, padre)

    s.recursos.registrarLibro("Python 101", "Guido van Rossum", "978-123", 2020, "C005")       # R0001
    s.recursos.registrarEquipo("Proyector 1", "Proyector", "Epson", "Sala A", "C002")         # R0002
    s.recursos.registrarSala("Sala de Estudio", 30, "Tablero y 6 mesas")                     # R0003
    s.recursos.registrarLibro("Estructuras de Datos", "Cormen", "978-456", 2009, "C004")     # R0004
    s.recursos.registrarEquipo("Portatil Dell", "Portatil", "Latitude", "Centro", "C004")    # R0005
    s.recursos.registrarLibro("Fisica Universitaria", "Sears", "978-789", 2015, "C006")      # R0006

    for codigo, sede, unidades in UNIDADES:
        s.inventario.fijarUnidades(codigo, sede, unidades)

    for usuario, recurso, sede, haceDias, duracion in HISTORIAL:
        inicio = hoy - timedelta(days=haceDias)
        codigo = s.prestamos.registrarPrestamo(usuario, recurso, sede, fechaPrestamo=inicio)
        if duracion is not None:
            s.prestamos.registrarDevolucion(codigo, inicio + timedelta(days=duracion))

    for usuario, recurso, sede in FILAS:
        s.turnos.solicitarTurno(usuario, recurso, sede)

    s.prestamos.reiniciarDeshacer()   # la precarga no se puede deshacer
    return s
