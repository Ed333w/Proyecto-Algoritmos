"""Menú M02 · Recursos y sedes."""

from modulos.M02_Recursos import TIPOS, ESTADOS, claseDeTipo
from .consola import leer, leerEntero, tabla, ejecutarMenu


def mostrarRecursos(sistema, recursos):
    tabla(("Código", "Tipo", "Nombre", "Categoría", "Estado", "Unidades"),
          [(r.codigo, r.TIPO, r.nombre, r.categoria or "-", sistema.recursos.estadoDe(r),
            sistema.inventario.totalDisponible(r.codigo)) for r in recursos])


def _leerTipo():
    opciones = ", ".join(c.TIPO for c in TIPOS)
    return claseDeTipo(leer(f"Tipo ({opciones}): "))


def elegirRecurso(sesion):
    """Muestra la lista actual de recursos (con su estado y unidades) y deja elegir por
    código o, si no se sabe, buscando por tipo y nombre."""
    sistema = sesion.sistema
    mostrarRecursos(sistema, sistema.recursos.listarTodos())
    codigo = leer("\nCódigo del recurso (Enter para buscar por tipo y nombre): ")
    if codigo:
        return sistema.recursos.obtener(codigo)
    opciones = ", ".join(c.TIPO for c in TIPOS)
    tipo = leer(f"Tipo ({opciones}; Enter para cualquiera): ")
    encontrados = sistema.recursos.buscarPorTipoYNombre(tipo, leer("Nombre o parte del nombre: "))
    if not encontrados:
        raise ValueError("No hay recursos con ese tipo y nombre")
    if len(encontrados) == 1:
        return encontrados[0]
    print()
    mostrarRecursos(sistema, encontrados)
    return sistema.recursos.obtener(leer("\nHay varios: escriba el código del que busca: "))


def registrar(sesion):
    clase = _leerTipo()
    nombre = leer("Nombre: ")
    datos = {atributo: leer(f"{etiqueta}: ") for atributo, etiqueta, _ in clase.CAMPOS}
    categoria = leer("Código de categoría (Enter para ninguna): ") or None
    codigo = sesion.sistema.recursos.registrar(clase.TIPO, nombre, categoria, **datos)
    print(f"\n  {clase.TIPO} registrado con el código {codigo}")
    print("  Cargue sus unidades por sede en el menú de Inventario (M07).")


def consultar(sesion):
    sistema = sesion.sistema
    recurso = elegirRecurso(sesion)
    print()
    for campo, valor in recurso.obtenerInfo().items():
        print(f"  {campo:<20} {valor}")
    print(f"  {'situación':<20} {sistema.recursos.estadoDe(recurso)}")
    print("\n  Unidades disponibles por sede:")
    tabla(("Sede", "Unidades"), sistema.inventario.disponibilidadPorSede(recurso.codigo))


def actualizar(sesion):
    recursos = sesion.sistema.recursos
    recurso = recursos.validarVigente(elegirRecurso(sesion).codigo)
    campos = recurso.camposEditables() + (("categoria", "Categoría", None),)
    for i, (atributo, etiqueta, _) in enumerate(campos, 1):
        valor = recurso.categoria if atributo == "categoria" else getattr(recurso, atributo)
        print(f"  {i}. {etiqueta}: {valor or '-'}")
    eleccion = leerEntero("Campo a modificar: ")
    if not 1 <= eleccion <= len(campos):
        raise ValueError("Campo inválido")
    atributo, etiqueta, _ = campos[eleccion - 1]
    recursos.actualizar(recurso.codigo, atributo, leer(f"Nuevo valor de {etiqueta}: "))
    print(f"\n  {recurso.codigo} actualizado")


def darDeBaja(sesion):
    recurso = elegirRecurso(sesion)
    canceladas = sesion.sistema.darDeBajaRecurso(recurso.codigo)
    print(f"\n  {recurso.codigo} {recurso.nombre} dado de baja. Solicitudes canceladas: {canceladas}")


def listarPorTipo(sesion):
    mostrarRecursos(sesion.sistema, sesion.sistema.recursos.listarxTipo(_leerTipo().TIPO))


def listarPorCategoria(sesion):
    codigo = leer("Código de la categoría: ")
    sub = leer("¿Incluir subcategorías? (s/n): ").lower() != "n"
    mostrarRecursos(sesion.sistema, sesion.sistema.recursos.listarPorCategoria(codigo, sub))


def listarPorEstado(sesion):
    estado = leer(f"Estado ({', '.join(ESTADOS)}): ")
    mostrarRecursos(sesion.sistema, sesion.sistema.recursos.listarPorEstado(estado))


def registrarSede(sesion):
    sede = sesion.sistema.recursos.registrarSede(leer("Nombre de la sede: "))
    print(f"\n  Sede {sede} registrada. Ya tiene su fila en la matriz de inventario.")
    print("  Conéctela con otras sedes en el menú Red de sedes (M09).")


def listarSedes(sesion):
    tabla(("Código", "Sede"), [(s.codigo, s.nombre) for s in sesion.sistema.recursos.listarSedes()])


def menu(sesion):
    ejecutarMenu("M02 · RECURSOS Y SEDES", (
        ("Registrar recurso (libro, equipo o sala)", registrar),
        ("Consultar recurso (lista, código o tipo y nombre)", consultar),
        ("Actualizar datos de un recurso", actualizar),
        ("Dar de baja recurso", darDeBaja),
        ("Listar todos", lambda s: mostrarRecursos(s.sistema, s.sistema.recursos.listarTodos())),
        ("Listar por tipo", listarPorTipo),
        ("Listar por categoría", listarPorCategoria),
        ("Listar por estado", listarPorEstado),
        ("Catálogo ordenado por nombre (BST)", lambda s: mostrarRecursos(s.sistema, s.sistema.recursos.catalogoOrdenado())),
        ("Registrar sede", registrarSede),
        ("Listar sedes", listarSedes),
    ), sesion)
