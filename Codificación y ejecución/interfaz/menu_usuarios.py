"""Menú M01 · Usuarios."""

import unicodedata

from estructuras.Algoritmos import mergeSort
from modulos.M01_usuarios import TIPOS_DOCUMENTO
from .consola import leer, tabla, ejecutarMenu

OPCIONES_DOCUMENTO = ", ".join(f"{sigla} = {nombre}" for sigla, nombre in TIPOS_DOCUMENTO)


def mostrarUsuarios(usuarios):
    tabla(("Código", "Nombre", "Tipo doc.", "Número doc.", "Estado", "Correo", "Préstamos activos"),
          [(u.codigo, u.nombre, u.tipoDocumento, u.numeroDocumento, u.estado, u.email, u.prestamosActivos)
           for u in usuarios])


def _sinTildes(texto):
    return "".join(c for c in unicodedata.normalize("NFD", str(texto).lower())
                   if unicodedata.category(c) != "Mn").strip()


def buscarPorNombre(gestorUsuarios, nombre):
    """Usuarios cuyo nombre contiene el texto (sin importar mayúsculas ni tildes), por nombre."""
    texto = _sinTildes(nombre)
    if not texto:
        raise ValueError("Escriba el nombre o parte del nombre")
    encontrados = [u for u in gestorUsuarios.listarTodos() if texto in _sinTildes(u.nombre)]
    return mergeSort(encontrados, clave=lambda u: (_sinTildes(u.nombre), u.codigo))


def _leerDocumento():
    print(f"  Tipos de documento: {OPCIONES_DOCUMENTO}")
    return leer("Tipo de documento: "), leer("Número de documento: ")


def elegirUsuario(sesion):
    """Muestra la lista de usuarios (código, nombre, tipo y número de documento y estado)
    y deja elegir por código o, si no se sabe, buscar por nombre o por tipo y número de
    documento. La usan todos los menús que piden un usuario."""
    usuarios = sesion.sistema.usuarios
    mostrarUsuarios(usuarios.listarTodos())
    codigo = leer("\nCódigo del usuario (Enter para buscar por nombre o documento): ")
    if codigo:
        return usuarios.obtener(codigo)
    forma = leer("Buscar por: 1 = nombre, 2 = tipo y número de documento: ")
    if forma == "2":
        usuario = usuarios.obtenerPorDocumento(*_leerDocumento())
        print(f"  Usuario: {usuario.codigo} {usuario.nombre}")
        return usuario
    if forma != "1":
        raise ValueError("Opción de búsqueda inválida (use 1 o 2)")
    encontrados = buscarPorNombre(usuarios, leer("Nombre o parte del nombre: "))
    if not encontrados:
        raise ValueError("No hay usuarios con ese nombre")
    if len(encontrados) == 1:
        print(f"  Usuario: {encontrados[0].codigo} {encontrados[0].nombre}")
        return encontrados[0]
    print()
    mostrarUsuarios(encontrados)
    return usuarios.obtener(leer("\nHay varios: escriba el código del que busca: "))


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
        ("Consultar usuario (lista, código, nombre o documento)", consultar),
        ("Actualizar correo", actualizarCorreo),
        ("Dar de baja usuario", darDeBaja),
        ("Reactivar usuario", reactivar),
        ("Listar todos", lambda s: mostrarUsuarios(s.sistema.usuarios.listarTodos())),
        ("Listar activos", lambda s: mostrarUsuarios(s.sistema.usuarios.listarActivos())),
    ), sesion)
