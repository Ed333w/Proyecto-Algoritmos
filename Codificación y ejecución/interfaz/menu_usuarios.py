"""Menú M01 · Usuarios."""

from modulos.M01_usuarios import TIPOS_DOCUMENTO
from .consola import leer, tabla, ejecutarMenu

OPCIONES_DOCUMENTO = ", ".join(f"{sigla} = {nombre}" for sigla, nombre in TIPOS_DOCUMENTO)


def mostrarUsuarios(usuarios):
    tabla(("Código", "Documento", "Nombre", "Correo", "Estado", "Préstamos activos"),
          [(u.codigo, u.documento(), u.nombre, u.email, u.estado, u.prestamosActivos) for u in usuarios])


def _leerDocumento():
    print(f"  Tipos de documento: {OPCIONES_DOCUMENTO}")
    return leer("Tipo de documento: "), leer("Número de documento: ")


def elegirUsuario(sesion):
    """Muestra la lista actual de usuarios (con su estado) y deja elegir por código
    o, si no se sabe, por tipo y número de documento."""
    usuarios = sesion.sistema.usuarios
    mostrarUsuarios(usuarios.listarTodos())
    codigo = leer("\nCódigo del usuario (Enter para buscar por documento): ")
    if codigo:
        return usuarios.obtener(codigo)
    return usuarios.obtenerPorDocumento(*_leerDocumento())


def registrar(sesion):
    nombre = leer("Nombre: ")
    tipo, numero = _leerDocumento()
    codigo = sesion.sistema.usuarios.registrar(nombre, leer("Correo: "), tipo, numero)
    print(f"\n  Usuario registrado con el código {codigo}")


def consultar(sesion):
    usuario = elegirUsuario(sesion)
    print()
    for campo, valor in usuario.obtenerInfo().items():
        print(f"  {campo:<18} {valor}")


def actualizarCorreo(sesion):
    usuario = elegirUsuario(sesion)
    print(f"\n  {usuario.nombre}, correo actual: {usuario.email}")
    sesion.sistema.usuarios.actualizarEmail(usuario.codigo, leer("Nuevo correo: "))
    print(f"\n  Correo de {usuario.codigo} actualizado a {usuario.email}")


def darDeBaja(sesion):
    usuario = elegirUsuario(sesion)
    sesion.sistema.usuarios.darDeBaja(usuario.codigo)
    print(f"\n  {usuario.codigo} {usuario.nombre} quedó inactivo. Su historial se conserva.")


def reactivar(sesion):
    usuario = elegirUsuario(sesion)
    sesion.sistema.usuarios.reactivar(usuario.codigo)
    print(f"\n  {usuario.codigo} {usuario.nombre} está activo de nuevo")


def menu(sesion):
    ejecutarMenu("M01 · USUARIOS", (
        ("Registrar usuario", registrar),
        ("Consultar usuario (lista, código o documento)", consultar),
        ("Actualizar correo", actualizarCorreo),
        ("Dar de baja usuario", darDeBaja),
        ("Reactivar usuario", reactivar),
        ("Listar todos", lambda s: mostrarUsuarios(s.sistema.usuarios.listarTodos())),
        ("Listar activos", lambda s: mostrarUsuarios(s.sistema.usuarios.listarActivos())),
    ), sesion)
