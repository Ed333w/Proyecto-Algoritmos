"""M01 · Usuarios: RQF-001, 002, 003, 004, 019 y 035."""

import pytest

from estructuras.Algoritmos import busquedaSecuencial
from modulos import GestorUsuarios


# ---- RQF-001 Registrar usuario ----
def test_rqf001_exitoso(caso):
    caso.inicio("RQF-001", "Exitoso", "Registrar 'Ana Garcia' con cédula 1.020.304.050 y correo válido",
                "Código U001, estado Activo, documento CC 1020304050 y correo en minúsculas")
    g = GestorUsuarios()
    codigo = g.registrar("Ana Garcia", "Ana@Uni.edu", "cc", "1.020.304.050")
    u = g.buscarxCodigo(codigo)
    caso.resultado(f"{codigo}, {u.estado}, {u.documento()}, {u.email}")
    assert codigo == "U001" and u.esActivo() and u.documento() == "CC 1020304050" and u.email == "ana@uni.edu"


def test_rqf001_borde(caso):
    caso.inicio("RQF-001", "Borde", "Nombre de 1 letra y pasaporte con letras; luego nombre vacío, correo sin @, "
                "correo repetido, documento repetido, tipo de documento inválido y cédula con letras",
                "Acepta los dos primeros y rechaza los otros seis con un mensaje claro, sin gastar códigos")
    g = GestorUsuarios()
    g.registrar("A", "a@uni.edu", "CC", "12345")
    g.registrar("Pasaporte", "p@uni.edu", "PA", "AB12345")
    errores = []
    for datos in (("   ", "b@uni.edu", "CC", "55555"), ("Beto", "beto.uni.edu", "CC", "55555"),
                  ("Otra", "A@uni.edu", "CC", "55555"), ("Otra", "o@uni.edu", "CC", "12345"),
                  ("Otra", "o@uni.edu", "XX", "55555"), ("Otra", "o@uni.edu", "CC", "12A45")):
        with pytest.raises(ValueError) as e:
            g.registrar(*datos)
        errores.append(str(e.value))
    siguiente = g.registrar("Valida", "v@uni.edu", "TI", "99999")
    caso.resultado("; ".join(errores) + f"; siguiente código {siguiente}")
    assert g.obtenerCantidad() == 3 and siguiente == "U003" and "ya está registrado" in errores[2]
    assert "Ya hay un usuario con el documento CC 12345" in errores[3]


def test_rqf001_cuello(caso, cronometro):
    n = 5000
    caso.inicio("RQF-001", "Cuello de botella", f"Registrar {n:,} usuarios seguidos",
                f"Códigos consecutivos hasta U{n:03d} sin repetidos")
    g = GestorUsuarios()
    with cronometro() as t:
        for i in range(n):
            g.registrar(f"Usuario {i}", f"u{i}@uni.edu", "CC", str(1000000 + i))
    caso.resultado(f"{g.obtenerCantidad():,} usuarios, último {g.listarTodos()[-1].codigo}, {t.segundos:.3f} s")
    assert g.obtenerCantidad() == n and g.buscarxCodigo(f"U{n:03d}") is not None and t.segundos < 3


# ---- RQF-002 Consultar usuario (por código o por documento) ----
def test_rqf002_exitoso(caso, demo):
    caso.inicio("RQF-002", "Exitoso", "Consultar a Luis Perez por su código U003 y por su documento TI 1098765432",
                "Las dos consultas devuelven el mismo usuario con sus datos y 2 préstamos activos")
    porCodigo = demo.usuarios.obtener("U003")
    porDocumento = demo.usuarios.obtenerPorDocumento("ti", "1098765432")
    info = porDocumento.obtenerInfo()
    caso.resultado(f"{info['codigo']}, {info['nombre']}, {info['documento']}, {info['estado']}, "
                   f"{info['prestamosActivos']} activos; misma persona={porCodigo is porDocumento}")
    assert porCodigo is porDocumento and info["prestamosActivos"] == 2


def test_rqf002_borde(caso, demo):
    caso.inicio("RQF-002", "Borde", "Código ' u003 ' (minúscula y espacios), código U999, documento que no existe, "
                "mismo número con otro tipo y tipo inválido",
                "Encuentra U003; los otros cuatro informan el motivo")
    encontrado = demo.usuarios.obtener(" u003 ")
    errores = []
    for consulta in (lambda: demo.usuarios.obtener("U999"),
                     lambda: demo.usuarios.obtenerPorDocumento("CC", "99999999"),
                     lambda: demo.usuarios.obtenerPorDocumento("CC", "1098765432"),
                     lambda: demo.usuarios.obtenerPorDocumento("RC", "1098765432")):
        with pytest.raises(ValueError) as e:
            consulta()
        errores.append(str(e.value))
    caso.resultado(f"{encontrado.codigo}; " + "; ".join(errores))
    assert encontrado.codigo == "U003" and len(errores) == 4


def test_rqf002_cuello(caso, masivo, cronometro):
    caso.inicio("RQF-002", "Cuello de botella", "10.000 consultas por código y 10.000 por documento sobre 3.000 usuarios",
                "Todas encuentran al usuario; tiempo casi constante por consulta (tablas hash)")
    usuarios = (masivo.usuarios.listarTodos() * 4)[:10000]
    with cronometro() as t:
        porCodigo = sum(1 for u in usuarios if masivo.usuarios.obtener(u.codigo) is u)
        porDocumento = sum(1 for u in usuarios
                           if masivo.usuarios.obtenerPorDocumento(u.tipoDocumento, u.numeroDocumento) is u)
    caso.resultado(f"{porCodigo:,} por código y {porDocumento:,} por documento en {t.segundos:.3f} s "
                   f"({t.segundos / 20000 * 1e6:.1f} µs c/u)")
    assert porCodigo == porDocumento == 10000 and t.segundos < 3


# ---- RQF-003 Actualizar correo ----
def test_rqf003_exitoso(caso, demo):
    caso.inicio("RQF-003", "Exitoso", "Cambiar el correo de U001 a carlos.lopez@uni.edu",
                "El correo cambia y el anterior queda libre para otro usuario")
    demo.usuarios.actualizarEmail("U001", "carlos.lopez@uni.edu")
    nuevo = demo.usuarios.registrar("Otro Carlos", "carlos@uni.edu", "CC", "3000006")
    caso.resultado(f"U001 -> {demo.usuarios.obtener('U001').email}; el correo viejo lo tomó {nuevo}")
    assert demo.usuarios.obtener("U001").email == "carlos.lopez@uni.edu"


def test_rqf003_borde(caso, demo):
    caso.inicio("RQF-003", "Borde", "Correo vacío, correo de otro usuario y el mismo correo actual",
                "Rechaza los dos primeros; aceptar el propio correo no da error")
    errores = []
    for correo in ("", "ana@uni.edu"):
        with pytest.raises(ValueError) as e:
            demo.usuarios.actualizarEmail("U001", correo)
        errores.append(str(e.value))
    demo.usuarios.actualizarEmail("U001", "carlos@uni.edu")
    caso.resultado("; ".join(errores) + "; mismo correo aceptado")
    assert demo.usuarios.obtener("U001").email == "carlos@uni.edu"


def test_rqf003_cuello(caso, cronometro):
    n = 3000
    caso.inicio("RQF-003", "Cuello de botella", f"Actualizar el correo de {n:,} usuarios",
                "Todos actualizados y el índice de correos sigue sin repetidos")
    g = GestorUsuarios()
    for i in range(n):
        g.registrar(f"U {i}", f"viejo{i}@uni.edu", "CC", str(1000000 + i))
    with cronometro() as t:
        for u in g.listarTodos():
            g.actualizarEmail(u.codigo, u.email.replace("viejo", "nuevo"))
    caso.resultado(f"{len(g.indiceEmail):,} correos en el índice, {t.segundos:.3f} s")
    assert len(g.indiceEmail) == n and g.indiceEmail.buscar("viejo1@uni.edu") is None


# ---- RQF-004 Dar de baja ----
def test_rqf004_exitoso(caso, demo):
    caso.inicio("RQF-004", "Exitoso", "Dar de baja a U002 (sin préstamos activos)",
                "Queda Inactivo, sale del conjunto de activos y su historial se conserva")
    demo.usuarios.darDeBaja("U002")
    historial = demo.prestamos.historialUsuario("U002")
    caso.resultado(f"estado {demo.usuarios.obtener('U002').estado}, en activos={demo.usuarios.activos.contiene('U002')}, "
                   f"historial {len(historial)} préstamos")
    assert not demo.usuarios.obtener("U002").esActivo() and len(historial) == 2


def test_rqf004_borde(caso, demo):
    caso.inicio("RQF-004", "Borde", "Dar de baja a U003 (tiene préstamos activos) y a un usuario ya inactivo",
                "Rechaza ambos y explica el motivo")
    with pytest.raises(ValueError) as e1:
        demo.usuarios.darDeBaja("U003")
    demo.usuarios.darDeBaja("U002")
    with pytest.raises(ValueError) as e2:
        demo.usuarios.darDeBaja("U002")
    caso.resultado(f"{e1.value}; {e2.value}")
    assert "préstamo" in str(e1.value) and "ya está inactivo" in str(e2.value)


def test_rqf004_cuello(caso, cronometro):
    n = 3000
    caso.inicio("RQF-004", "Cuello de botella", f"Dar de baja a la mitad de {n:,} usuarios",
                "El conjunto de activos queda con la otra mitad")
    g = GestorUsuarios()
    for i in range(n):
        g.registrar(f"U {i}", f"u{i}@uni.edu", "CC", str(1000000 + i))
    with cronometro() as t:
        for u in g.listarTodos()[::2]:
            g.darDeBaja(u.codigo)
    caso.resultado(f"activos {g.obtenerCantidadActivos():,} de {g.obtenerCantidad():,}, {t.segundos:.3f} s")
    assert g.obtenerCantidadActivos() == n // 2 and len(g.listarActivos()) == n // 2


# ---- RQF-019 Búsqueda por código en tabla hash ----
def test_rqf019_exitoso(caso, demo):
    caso.inicio("RQF-019", "Exitoso", "Buscar U005 en la tabla hash", "Devuelve a Pedro Diaz")
    u = demo.usuarios.buscarxCodigo("U005")
    caso.resultado(str(u))
    assert u.nombre == "Pedro Diaz"


def test_rqf019_borde(caso):
    caso.inicio("RQF-019", "Borde", "Buscar en un gestor vacío y un código con formato raro",
                "Devuelve None sin error")
    g = GestorUsuarios()
    caso.resultado(f"U001={g.buscarxCodigo('U001')}, '###'={g.buscarxCodigo('###')}")
    assert g.buscarxCodigo("U001") is None and g.buscarxCodigo("###") is None


def test_rqf019_cuello(caso, masivo, cronometro):
    caso.inicio("RQF-019", "Cuello de botella", "Comparar tabla hash vs. búsqueda secuencial (3.000 usuarios, 500 búsquedas)",
                "La tabla hash es al menos 20 veces más rápida")
    todos = masivo.usuarios.listarTodos()
    objetivos = [u.codigo for u in todos[-500:]]
    with cronometro() as th:
        for c in objetivos:
            masivo.usuarios.buscarxCodigo(c)
    with cronometro() as ts:
        for c in objetivos:
            busquedaSecuencial(todos, c, clave=lambda u: u.codigo)
    caso.resultado(f"hash {th.segundos * 1000:.2f} ms vs. secuencial {ts.segundos * 1000:.1f} ms "
                   f"({ts.segundos / th.segundos:.0f} veces)")
    assert ts.segundos > 20 * th.segundos


# ---- RQF-035 Reactivar usuario ----
def test_rqf035_exitoso(caso, demo):
    caso.inicio("RQF-035", "Exitoso", "Dar de baja y reactivar a U002", "Vuelve a Activo y puede pedir préstamos")
    demo.usuarios.darDeBaja("U002")
    demo.usuarios.reactivar("U002")
    codigo = demo.prestamos.registrarPrestamo("U002", "R0001", "Centro")
    caso.resultado(f"estado {demo.usuarios.obtener('U002').estado}, préstamo {codigo}")
    assert demo.usuarios.obtener("U002").esActivo()


def test_rqf035_borde(caso, demo):
    caso.inicio("RQF-035", "Borde", "Reactivar a un usuario que ya está activo y a uno que no existe",
                "Rechaza ambos")
    errores = []
    for codigo in ("U001", "U777"):
        with pytest.raises(ValueError) as e:
            demo.usuarios.reactivar(codigo)
        errores.append(str(e.value))
    caso.resultado("; ".join(errores))
    assert "ya está activo" in errores[0] and "no existe" in errores[1]


def test_rqf035_cuello(caso, cronometro):
    n = 3000
    caso.inicio("RQF-035", "Cuello de botella", f"Dar de baja y reactivar {n:,} usuarios",
                "Todos quedan activos de nuevo")
    g = GestorUsuarios()
    for i in range(n):
        g.registrar(f"U {i}", f"u{i}@uni.edu", "CC", str(1000000 + i))
    with cronometro() as t:
        for u in g.listarTodos():
            g.darDeBaja(u.codigo)
        for u in g.listarTodos():
            g.reactivar(u.codigo)
    caso.resultado(f"activos {g.obtenerCantidadActivos():,}, {t.segundos:.3f} s")
    assert g.obtenerCantidadActivos() == n
