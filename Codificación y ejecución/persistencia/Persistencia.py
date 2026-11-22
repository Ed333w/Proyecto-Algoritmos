"""RQF-050 · Persistencia en archivos de texto plano (sin motor de base de datos).

Cada colección se guarda en su propio archivo .txt, con una línea por registro
y los campos separados por ';' (el módulo csv se encarga de las comillas si un
nombre trae ';'). Se guarda al salir y se carga al iniciar.

Orden de carga (cada archivo depende de los anteriores):
sedes -> conexiones -> categorias -> usuarios -> recursos -> inventario ->
solicitudes -> prestamos
"""

import csv
import os

from modulos import Sistema, Usuario, Prestamo, Solicitud
from modulos.M02_Recursos import claseDeTipo
from modulos.comun import fechaATexto, textoAFecha

SEPARADOR = ";"
ARCHIVOS = ("sedes", "conexiones", "categorias", "usuarios", "recursos",
            "inventario", "solicitudes", "prestamos")
MAX_DATOS_PROPIOS = 3   # el tipo con más datos propios (Libro y Equipo) tiene 3

ENCABEZADOS = {
    "sedes": ["codigo", "nombre"],
    "conexiones": ["sedeA", "sedeB"],
    "categorias": ["codigo", "nombre", "padre"],
    "usuarios": ["codigo", "nombre", "tipoDocumento", "numeroDocumento", "email", "fechaRegistro", "estado"],
    "recursos": ["codigo", "tipo", "nombre", "categoria", "fechaRegistro", "estado"] + [f"dato{i}" for i in range(1, MAX_DATOS_PROPIOS + 1)],
    "inventario": ["recurso", "sede", "unidades"],
    "solicitudes": ["codigo", "usuario", "recurso", "sede", "fecha", "estado"],
    "prestamos": ["codigo", "usuario", "recurso", "sede", "fechaPrestamo", "diasLimite",
                  "fechaDevolucion", "estado"],
}


def hayDatosGuardados(carpeta):
    return os.path.isfile(os.path.join(carpeta, "usuarios.txt"))


# ======================= Guardar =======================

def _filas(sistema):
    """Genera, por archivo, las filas a escribir (en el orden en que deben cargarse)."""
    yield "sedes", ([s.codigo, s.nombre] for s in sistema.recursos.listarSedes())
    yield "conexiones", (list(par) for par in sistema.red.conexiones())
    yield "categorias", ([c.codigo, c.nombre, c.padre.codigo if c.padre else ""]
                         for c, _ in sistema.categorias.arbolCompleto())
    yield "usuarios", ([u.codigo, u.nombre, u.tipoDocumento, u.numeroDocumento, u.email,
                        fechaATexto(u.fechaRegistro), u.estado]
                       for u in sistema.usuarios.listarTodos())
    yield "recursos", ([r.codigo, r.TIPO, r.nombre, r.categoria or "", fechaATexto(r.fechaRegistro),
                        r.estado] + [valor for _, valor in r.datosPropios()]
                       for r in sistema.recursos.listarTodos())
    yield "inventario", ([codigo, sede, unidades]
                         for codigo in sistema.inventario.recursos
                         for sede, unidades in sistema.inventario.disponibilidadPorSede(codigo)
                         if unidades)
    yield "solicitudes", ([s.codigo, s.codigoUsuario, s.codigoRecurso, s.sede, fechaATexto(s.fecha), s.estado]
                          for s in sistema.turnos.listarSolicitudes())
    yield "prestamos", ([p.codigo, p.codigoUsuario, p.codigoRecurso, p.sede, fechaATexto(p.fechaPrestamo),
                         p.diasLimite, fechaATexto(p.fechaDevolucion), p.estado]
                        for p in sistema.prestamos.listarTodos())


def guardar(sistema, carpeta):
    """Escribe cada archivo en uno temporal y luego lo reemplaza, para no dejar
    archivos a medias si el programa se interrumpe."""
    os.makedirs(carpeta, exist_ok=True)
    total = 0
    for nombre, filas in _filas(sistema):
        ruta = os.path.join(carpeta, f"{nombre}.txt")
        temporal = ruta + ".tmp"
        with open(temporal, "w", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo, delimiter=SEPARADOR)
            escritor.writerow(ENCABEZADOS[nombre])
            for fila in filas:
                escritor.writerow(fila)
                total += 1
        os.replace(temporal, ruta)
    return total


# ======================= Cargar =======================

def _leer(carpeta, nombre):
    ruta = os.path.join(carpeta, f"{nombre}.txt")
    if not os.path.isfile(ruta):
        return
    with open(ruta, newline="", encoding="utf-8") as archivo:
        lector = csv.reader(archivo, delimiter=SEPARADOR)
        encabezado = next(lector, None)
        if encabezado != ENCABEZADOS[nombre]:
            raise ValueError("el encabezado no es el esperado (¿archivo de otra versión?)")
        for numero, fila in enumerate(lector, start=2):
            if fila:
                yield numero, fila


def _cargarSedes(sistema, filas):
    for _, (codigo, nombre) in filas:
        sede = sistema.recursos.registrarSede(nombre)
        sede.codigo = codigo
        sistema.recursos.codigosSedes.registrarExistente(codigo)


def _cargarConexiones(sistema, filas):
    for _, (a, b) in filas:
        sistema.red.conectar(a, b)


def _cargarCategorias(sistema, filas):
    for _, (codigo, nombre, padre) in filas:
        sistema.categorias.registrarCategoria(codigo, nombre, padre or None)


def _cargarUsuarios(sistema, filas):
    for _, (codigo, nombre, tipo, numero, email, fecha, estado) in filas:
        sigla, numero = sistema.usuarios.validarDocumento(tipo, numero)
        sistema.usuarios.cargarExistente(Usuario(codigo, nombre, email, sigla, numero, textoAFecha(fecha), estado))


def _cargarRecursos(sistema, filas):
    for _, fila in filas:
        codigo, tipo, nombre, categoria, fecha, estado = fila[:6]
        clase = claseDeTipo(tipo)
        datos = {atributo: valor for (atributo, _, _), valor in zip(clase.CAMPOS, fila[6:])}
        recurso = clase(codigo, nombre, categoria or None, textoAFecha(fecha), **datos)
        recurso.estado = estado
        sistema.recursos.cargarExistente(recurso)


def _cargarInventario(sistema, filas):
    for _, (codigo, sede, unidades) in filas:
        sistema.inventario.fijarUnidades(codigo, sede, unidades)


def _cargarSolicitudes(sistema, filas):
    for _, (codigo, usuario, recurso, sede, fecha, estado) in filas:
        sistema.turnos.cargarExistente(Solicitud(codigo, usuario, recurso, sede, textoAFecha(fecha), estado))


def _cargarPrestamos(sistema, filas):
    for _, (codigo, usuario, recurso, sede, fecha, dias, devolucion, estado) in filas:
        prestamo = Prestamo(codigo, usuario, recurso, sede, textoAFecha(fecha), int(dias))
        if devolucion:
            prestamo.devolver(textoAFecha(devolucion))
        prestamo.estado = estado
        sistema.prestamos.cargarExistente(prestamo)


_CARGADORES = {
    "sedes": _cargarSedes, "conexiones": _cargarConexiones, "categorias": _cargarCategorias,
    "usuarios": _cargarUsuarios, "recursos": _cargarRecursos, "inventario": _cargarInventario,
    "solicitudes": _cargarSolicitudes, "prestamos": _cargarPrestamos,
}


def cargar(carpeta):
    """Construye un Sistema nuevo con lo guardado en 'carpeta'. Si un archivo trae un
    error, se informa el archivo y la línea y no se carga nada a medias."""
    if not hayDatosGuardados(carpeta):
        raise ValueError(f"No hay datos guardados en '{carpeta}'")
    sistema = Sistema()
    for nombre in ARCHIVOS:
        filas = _leer(carpeta, nombre)
        linea = [1]

        def conLinea(filas=filas):
            for numero, fila in filas:
                linea[0] = numero
                yield numero, fila

        try:
            _CARGADORES[nombre](sistema, conLinea())
        except (ValueError, TypeError, KeyError) as error:
            raise ValueError(f"{nombre}.txt, línea {linea[0]}: {error}") from None
    sistema.prestamos.reiniciarDeshacer()
    return sistema
