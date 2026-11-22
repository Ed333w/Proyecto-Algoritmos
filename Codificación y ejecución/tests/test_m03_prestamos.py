"""M03 · Préstamos: RQF-011, 012, 013, 014, 015, 036, 037, 038 y 039."""

from datetime import datetime, timedelta

import pytest

from modulos.M03_Prestamos import SinUnidadesError
from persistencia.datos_masivos import crearSistemaMasivo


def _cargarUnidades(s, cantidad):
    s.inventario.fijarUnidades("R0001", "Centro", cantidad)


# ---- RQF-011 Registrar préstamo ----
def test_rqf011_exitoso(caso, base):
    caso.inicio("RQF-011", "Exitoso", "U001 pide R0001 en Centro (2 unidades)",
                "Préstamo P0001 con plazo de 14 días; queda 1 unidad")
    codigo = base.prestamos.registrarPrestamo("U001", "R0001", "centro")
    p = base.prestamos.obtener(codigo)
    caso.resultado(f"{codigo}, sede {p.sede}, vence en {p.diasRestantes()} días, quedan "
                   f"{base.inventario.obtenerDisponibilidad('R0001', 'Centro')}")
    assert codigo == "P0001" and p.diasRestantes() == 14 and base.inventario.obtenerDisponibilidad("R0001", "Centro") == 1


def test_rqf011_borde(caso, base):
    caso.inicio("RQF-011", "Borde", "Pedir la última unidad, luego una más; usuario inactivo; sede inexistente; plazo 0",
                "La última se presta; después SinUnidadesError; los otros casos se rechazan")
    base.prestamos.registrarPrestamo("U001", "R0001", "Centro")
    base.prestamos.registrarPrestamo("U002", "R0001", "Centro")
    with pytest.raises(SinUnidadesError) as sin:
        base.prestamos.registrarPrestamo("U001", "R0001", "Centro")
    base.usuarios.registrar("Inactivo", "x@uni.edu", "CC", "3000003")
    base.usuarios.darDeBaja("U003")
    errores = []
    for args, kwargs in ((("U003", "R0001", "Norte"), {}), (("U001", "R0001", "Marte"), {}),
                         (("U001", "R0001", "Norte"), {"diasLimite": 0})):
        with pytest.raises(ValueError) as e:
            base.prestamos.registrarPrestamo(*args, **kwargs)
        errores.append(str(e.value))
    caso.resultado(f"{sin.value}; " + "; ".join(errores))
    assert base.prestamos.obtenerCantidad() == 2


def test_rqf011_cuello(caso, base, cronometro):
    n = 5000
    caso.inicio("RQF-011", "Cuello de botella", f"Registrar {n:,} préstamos de un recurso con {n:,} unidades",
                "Todos se registran y el inventario llega a 0")
    s = base
    _cargarUnidades(s, n)
    with cronometro() as t:
        for i in range(n):
            s.prestamos.registrarPrestamo("U001" if i % 2 else "U002", "R0001", "Centro")
    unidades = s.inventario.obtenerDisponibilidad("R0001", "Centro")
    caso.resultado(f"{s.prestamos.obtenerCantidad():,} préstamos, unidades {unidades}, {t.segundos:.3f} s")
    assert s.prestamos.obtenerCantidadActivos() == n and s.inventario.obtenerDisponibilidad("R0001", "Centro") == 0


# ---- RQF-012 Registrar devolución ----
def test_rqf012_exitoso(caso, demo):
    caso.inicio("RQF-012", "Exitoso", "Devolver P0008 (U003 tenía R0004 en Centro)",
                "Queda Devuelto con fecha, vuelve 1 unidad a Centro y U003 baja a 1 préstamo activo")
    antes = demo.inventario.obtenerDisponibilidad("R0004", "Centro")
    asignados = demo.prestamos.registrarDevolucion("P0008")
    p = demo.prestamos.obtener("P0008")
    caso.resultado(f"{p.estado} el {p.fechaDevolucion:%Y-%m-%d}; unidades {antes} -> "
                   f"{demo.inventario.obtenerDisponibilidad('R0004', 'Centro')}; asignados {asignados}")
    assert p.estado == "Devuelto" and demo.usuarios.obtener("U003").prestamosActivos == 1


def test_rqf012_borde(caso, demo):
    caso.inicio("RQF-012", "Borde", "Devolver dos veces, un código inexistente y la sala con fila de espera",
                "Los dos primeros fallan; la sala pasa sola al primero de la fila (U002)")
    demo.prestamos.registrarDevolucion("P0010")
    errores = []
    for codigo in ("P0010", "P9999"):
        with pytest.raises(ValueError) as e:
            demo.prestamos.registrarDevolucion(codigo)
        errores.append(str(e.value))
    asignado = demo.prestamos.listarTodos()[-1]
    caso.resultado("; ".join(errores) + f"; la sala quedó a {asignado.codigoUsuario} ({asignado.codigo})")
    assert asignado.codigoUsuario == "U002" and asignado.codigoRecurso == "R0003"


def test_rqf012_cuello(caso, cronometro):
    caso.inicio("RQF-012", "Cuello de botella", "Devolver todos los préstamos activos de un sistema con 6.000 préstamos",
                "No queda ningún activo y la fila de espera se atiende al volver las unidades")
    s = crearSistemaMasivo(usuarios=3000, recursos=1500, prestamos=6000, solicitudes=300)
    activos = s.prestamos.listarActivos()
    with cronometro() as t:
        for p in activos:
            if p.estaActivo():
                s.prestamos.registrarDevolucion(p.codigo)
        while s.prestamos.obtenerCantidadActivos():
            s.prestamos.registrarDevolucion(s.prestamos.listarActivos()[0].codigo)
    caso.resultado(f"{len(activos):,} devoluciones iniciales, activos al final {s.prestamos.obtenerCantidadActivos()}, "
                   f"en espera {s.turnos.totalEnEspera()}, {t.segundos:.3f} s")
    assert s.prestamos.obtenerCantidadActivos() == 0 and t.segundos < 10


# ---- RQF-013 Historial de un usuario ----
def test_rqf013_exitoso(caso, demo):
    caso.inicio("RQF-013", "Exitoso", "Historial de U003 en ambos sentidos y sus activos",
                "3 préstamos; el recorrido hacia atrás es el inverso; 2 activos")
    adelante = [p.codigo for p in demo.prestamos.historialUsuario("U003")]
    atras = [p.codigo for p in demo.prestamos.historialUsuario("U003", haciaAtras=True)]
    activos = [p.codigo for p in demo.prestamos.activosDeUsuario("U003")]
    caso.resultado(f"adelante {adelante}, atrás {atras}, activos {activos}")
    assert adelante == ["P0004", "P0008", "P0009"] and atras == adelante[::-1] and len(activos) == 2


def test_rqf013_borde(caso, demo):
    caso.inicio("RQF-013", "Borde", "Usuario recién creado sin préstamos y usuario inexistente",
                "Historial vacío; el inexistente da error")
    nuevo = demo.usuarios.registrar("Nuevo", "nuevo@uni.edu", "CC", "3000004")
    with pytest.raises(ValueError) as e:
        demo.prestamos.historialUsuario("U999")
    caso.resultado(f"{nuevo}: {demo.prestamos.historialUsuario(nuevo)}; {e.value}")
    assert demo.prestamos.historialUsuario(nuevo) == []


def test_rqf013_cuello(caso, masivo, cronometro):
    caso.inicio("RQF-013", "Cuello de botella", "Historial de 100 usuarios sobre 6.000 préstamos",
                "Cada historial recorre la lista doble una vez (O(n))")
    usuarios = masivo.usuarios.listarTodos()[:100]
    with cronometro() as t:
        total = sum(len(masivo.prestamos.historialUsuario(u.codigo)) for u in usuarios)
    caso.resultado(f"{total} préstamos encontrados, {t.segundos:.3f} s")
    assert total > 0 and t.segundos < 5


# ---- RQF-014 Historial de un recurso ----
def test_rqf014_exitoso(caso, demo):
    caso.inicio("RQF-014", "Exitoso", "Historial de R0001", "4 préstamos: P0002, P0004, P0006 y P0007")
    codigos = [p.codigo for p in demo.prestamos.historialRecurso("R0001")]
    caso.resultado(str(codigos))
    assert codigos == ["P0002", "P0004", "P0006", "P0007"]


def test_rqf014_borde(caso, demo):
    caso.inicio("RQF-014", "Borde", "Recurso sin préstamos (R0006) y código inexistente", "Lista vacía y error")
    with pytest.raises(ValueError) as e:
        demo.prestamos.historialRecurso("R0099")
    caso.resultado(f"R0006: {demo.prestamos.historialRecurso('R0006')}; {e.value}")
    assert demo.prestamos.historialRecurso("R0006") == []


def test_rqf014_cuello(caso, masivo, cronometro):
    caso.inicio("RQF-014", "Cuello de botella", "Historial de los 100 recursos más prestados (6.000 préstamos)",
                "La suma coincide con el contador de préstamos de cada recurso")
    recursos = masivo.informes.masPrestados(100)
    with cronometro() as t:
        coincide = all(len(masivo.prestamos.historialRecurso(r.codigo)) == r.cantidadPrestamos for r in recursos)
    caso.resultado(f"coinciden={coincide}, {t.segundos:.3f} s")
    assert coincide


# ---- RQF-015 Deshacer ----
def test_rqf015_exitoso(caso, base):
    caso.inicio("RQF-015", "Exitoso", "Prestar y deshacer; devolver y deshacer",
                "Cada deshacer deja inventario, usuario e historial como estaban")
    codigo = base.prestamos.registrarPrestamo("U001", "R0001", "Centro")
    msg1 = base.prestamos.deshacer()
    estado1 = (base.prestamos.obtenerCantidad(), base.inventario.obtenerDisponibilidad("R0001", "Centro"))
    codigo = base.prestamos.registrarPrestamo("U001", "R0001", "Centro")
    base.prestamos.registrarDevolucion(codigo)
    msg2 = base.prestamos.deshacer()
    p = base.prestamos.obtener(codigo)
    caso.resultado(f"{msg1} -> (préstamos, unidades)={estado1}; {msg2} -> {p.estado}, unidades "
                   f"{base.inventario.obtenerDisponibilidad('R0001', 'Centro')}")
    assert estado1 == (0, 2) and codigo == "P0001" and p.estaActivo()


def test_rqf015_borde(caso, demo):
    caso.inicio("RQF-015", "Borde", "Pila vacía; deshacer una devolución que reasignó la unidad a la fila",
                "Sin operaciones devuelve None; hay que deshacer primero la asignación y el turno vuelve al frente")
    vacio = demo.prestamos.deshacer()
    demo.prestamos.registrarDevolucion("P0010")             # la sala pasa a U002
    conFila = demo.prestamos.deshacer()                    # deshace la asignación a U002
    frente = demo.turnos.verSiguiente("R0003", "Centro")
    segundo = demo.prestamos.deshacer()                      # deshace la devolución
    caso.resultado(f"pila vacía -> {vacio}; {conFila}; frente de la fila {frente.codigoUsuario}; {segundo}")
    assert vacio is None and frente.codigoUsuario == "U002" and demo.prestamos.obtener("P0010").estaActivo()


def test_rqf015_cuello(caso, base, cronometro):
    n = 3000
    caso.inicio("RQF-015", "Cuello de botella", f"{n:,} préstamos y {n:,} deshacer seguidos",
                "Vuelve exactamente al estado inicial; cada deshacer es O(1) salvo la búsqueda en la lista de activos")
    _cargarUnidades(base, n)
    with cronometro() as t:
        for _ in range(n):
            base.prestamos.registrarPrestamo("U001", "R0001", "Centro")
        for _ in range(n):
            base.prestamos.deshacer()
    caso.resultado(f"préstamos {base.prestamos.obtenerCantidad()}, unidades {base.inventario.obtenerDisponibilidad('R0001', 'Centro'):,}, "
                   f"siguiente código {base.prestamos.codigos.formatear(base.prestamos.codigos.contador + 1)}, {t.segundos:.3f} s")
    assert base.prestamos.obtenerCantidad() == 0 and base.inventario.obtenerDisponibilidad("R0001", "Centro") == n


# ---- RQF-036 Préstamos activos (lista simple) ----
def test_rqf036_exitoso(caso, demo):
    caso.inicio("RQF-036", "Exitoso", "Listar activos de la demo", "5 activos: P0007 a P0011")
    activos = [p.codigo for p in demo.prestamos.listarActivos()]
    caso.resultado(str(activos))
    assert activos == ["P0007", "P0008", "P0009", "P0010", "P0011"]


def test_rqf036_borde(caso, base):
    caso.inicio("RQF-036", "Borde", "Sin préstamos; luego prestar y devolver el único", "Lista vacía en ambos momentos")
    vacia = base.prestamos.listarActivos()
    codigo = base.prestamos.registrarPrestamo("U001", "R0001", "Centro")
    base.prestamos.registrarDevolucion(codigo)
    caso.resultado(f"antes {vacia}, después {base.prestamos.listarActivos()}, cola de la lista {base.prestamos.activos.cola}")
    assert vacia == [] and base.prestamos.listarActivos() == [] and base.prestamos.activos.cola is None


def test_rqf036_cuello(caso, masivo, cronometro):
    caso.inicio("RQF-036", "Cuello de botella", "Listar los activos de 6.000 préstamos 100 veces",
                "Coincide con contar los activos en el historial")
    with cronometro() as t:
        for _ in range(100):
            activos = masivo.prestamos.listarActivos()
    esperados = sum(1 for p in masivo.prestamos.listarTodos() if p.estaActivo())
    caso.resultado(f"{len(activos):,} activos (historial dice {esperados:,}), {t.segundos:.3f} s")
    assert len(activos) == esperados


# ---- RQF-037 Préstamos atrasados ----
def test_rqf037_exitoso(caso, demo):
    caso.inicio("RQF-037", "Exitoso", "Listar atrasados de la demo", "P0007 de U005 con 6 días de atraso")
    atrasados = demo.prestamos.listarAtrasados()
    caso.resultado(", ".join(f"{p.codigo} {p.codigoUsuario} {p.diasAtraso()} días" for p in atrasados))
    assert [(p.codigo, p.diasAtraso()) for p in atrasados] == [("P0007", 6)]


def test_rqf037_borde(caso, base):
    caso.inicio("RQF-037", "Borde", "Préstamo que vence hoy y otro que venció ayer",
                "El que vence hoy no está atrasado; el de ayer sí, con 1 día")
    hoy = datetime.now()
    a = base.prestamos.registrarPrestamo("U001", "R0001", "Centro", fechaPrestamo=hoy - timedelta(days=14))
    b = base.prestamos.registrarPrestamo("U002", "R0001", "Centro", fechaPrestamo=hoy - timedelta(days=15))
    atrasados = [(p.codigo, p.diasAtraso()) for p in base.prestamos.listarAtrasados()]
    caso.resultado(f"{a} vence hoy, {b} venció ayer -> atrasados {atrasados}")
    assert atrasados == [(b, 1)]


def test_rqf037_cuello(caso, masivo, cronometro):
    caso.inicio("RQF-037", "Cuello de botella", "Atrasados entre 6.000 préstamos, 100 veces",
                "Todos los listados tienen más de 14 días desde el préstamo")
    with cronometro() as t:
        for _ in range(100):
            atrasados = masivo.prestamos.listarAtrasados()
    caso.resultado(f"{len(atrasados):,} atrasados, {t.segundos:.3f} s")
    assert all(p.diasRestantes() < 0 for p in atrasados)


# ---- RQF-038 Consultar préstamo por código ----
def test_rqf038_exitoso(caso, demo):
    caso.inicio("RQF-038", "Exitoso", "Consultar P0011", "U004, R0004, sede Norte, activo")
    info = demo.prestamos.obtener("P0011").obtenerInfo()
    caso.resultado(f"{info['usuario']}, {info['recurso']}, {info['sede']}, {info['estado']}, vence {info['fechaLimite']}")
    assert (info["usuario"], info["recurso"], info["sede"]) == ("U004", "R0004", "Norte")


def test_rqf038_borde(caso, demo):
    caso.inicio("RQF-038", "Borde", "Código en minúscula y un préstamo deshecho",
                "Encuentra 'p0001'; el deshecho ya no existe")
    encontrado = demo.prestamos.buscarPrestamo("p0001")
    codigo = demo.prestamos.registrarPrestamo("U001", "R0001", "Centro")
    demo.prestamos.deshacer()
    caso.resultado(f"p0001 -> {encontrado.codigo}; {codigo} tras deshacer -> {demo.prestamos.buscarPrestamo(codigo)}")
    assert encontrado.codigo == "P0001" and demo.prestamos.buscarPrestamo(codigo) is None


def test_rqf038_cuello(caso, masivo, cronometro):
    caso.inicio("RQF-038", "Cuello de botella", "Consultar los 6.000 préstamos por código",
                "Todos encontrados en tiempo casi constante")
    codigos = [p.codigo for p in masivo.prestamos.listarTodos()]
    with cronometro() as t:
        encontrados = sum(1 for c in codigos if masivo.prestamos.buscarPrestamo(c))
    caso.resultado(f"{encontrados:,} en {t.segundos:.3f} s")
    assert encontrados == len(codigos)


# ---- RQF-039 Préstamos activos por sede ----
def test_rqf039_exitoso(caso, demo):
    caso.inicio("RQF-039", "Exitoso", "Activos en Norte y en Centro", "Norte: P0011; Centro: 4")
    norte = [p.codigo for p in demo.prestamos.activosDeSede("norte")]
    centro = demo.prestamos.activosDeSede("Centro")
    caso.resultado(f"Norte {norte}, Centro {len(centro)}")
    assert norte == ["P0011"] and len(centro) == 4


def test_rqf039_borde(caso, demo):
    caso.inicio("RQF-039", "Borde", "Sede sin préstamos (Occidente) y sede inexistente", "Lista vacía y error")
    with pytest.raises(ValueError) as e:
        demo.prestamos.activosDeSede("Marte")
    caso.resultado(f"Occidente {demo.prestamos.activosDeSede('Occidente')}; {e.value}")
    assert demo.prestamos.activosDeSede("Occidente") == []


def test_rqf039_cuello(caso, masivo, cronometro):
    caso.inicio("RQF-039", "Cuello de botella", "Activos por cada una de las 6 sedes (6.000 préstamos)",
                "La suma por sede es igual al total de activos")
    with cronometro() as t:
        suma = sum(len(masivo.prestamos.activosDeSede(s)) for s in masivo.recursos.nombresSedes())
    caso.resultado(f"suma {suma:,} = activos {masivo.prestamos.obtenerCantidadActivos():,}, {t.segundos:.3f} s")
    assert suma == masivo.prestamos.obtenerCantidadActivos()
