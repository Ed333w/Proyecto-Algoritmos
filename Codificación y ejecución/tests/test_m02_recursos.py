"""M02 · Recursos y sedes: RQF-005, 006, 007, 008, 020, 023, 042 y 052."""

import pytest

from estructuras.Algoritmos import busquedaSecuencial
from modulos import Sistema, Libro, Equipo, Sala, Recurso
from modulos.M02_Recursos import DADO_DE_BAJA, DISPONIBLE, SIN_UNIDADES


def _sistemaConRecursos(n, categorias=False):
    s = Sistema()
    s.recursos.registrarSede("Centro")
    if categorias:
        s.categorias.registrarCategoria("C001", "Ciencias")
    for i in range(n):
        s.recursos.registrarLibro(f"Libro {i:05d}", "Autor", f"978-{i}", 2000, "C001" if categorias else None)
    return s


# ---- RQF-005 Registrar recurso ----
def test_rqf005_exitoso(caso, demo):
    caso.inicio("RQF-005", "Exitoso", "Registrar un libro, un equipo y una sala con categoría",
                "Cada uno es de su clase, hereda de Recurso y queda con su categoría y una columna en el inventario")
    r = demo.recursos
    codigos = (r.registrarLibro("Calculo", "Stewart", "978-9", 2012, "C001"),
               r.registrarEquipo("Tablet", "Tablet", "Galaxy", "Bodega", "C002"),
               r.registrarSala("Sala 2", 8, "Tablero", "C003"))
    objetos = [r.obtener(c) for c in codigos]
    caso.resultado(", ".join(f"{o.codigo} {type(o).__name__} cat. {o.categoria}" for o in objetos))
    assert [type(o) for o in objetos] == [Libro, Equipo, Sala] and all(isinstance(o, Recurso) for o in objetos)
    assert all(demo.inventario.columnaDeRecurso.contiene(c) for c in codigos)


def test_rqf005_borde(caso, demo):
    caso.inicio("RQF-005", "Borde", "Año fuera de rango, capacidad 0, tipo inválido, categoría inexistente y clase abstracta",
                "Rechaza todos y no consume códigos")
    r, errores = demo.recursos, []
    intentos = (lambda: r.registrarLibro("X", "Y", "Z", 3000),
                lambda: r.registrarSala("S", 0),
                lambda: r.registrar("Revista", "X"),
                lambda: r.registrarLibro("X", "Y", "Z", 2000, "C999"))
    for intento in intentos:
        with pytest.raises(ValueError) as e:
            intento()
        errores.append(str(e.value))
    with pytest.raises(TypeError):
        Recurso("R9", "X")
    siguiente = r.registrarSala("Sala mínima", 1)
    caso.resultado("; ".join(errores) + f"; siguiente código válido {siguiente}")
    assert siguiente == "R0007"


def test_rqf005_cuello(caso, cronometro):
    n = 3000
    caso.inicio("RQF-005", "Cuello de botella", f"Registrar {n:,} recursos mezclando los tres tipos",
                "Todos registrados con código único; la matriz de inventario crece sola")
    s = Sistema()
    s.recursos.registrarSede("Centro")
    with cronometro() as t:
        for i in range(n):
            if i % 3 == 0:
                s.recursos.registrarLibro(f"L{i}", "A", f"I{i}", 2000)
            elif i % 3 == 1:
                s.recursos.registrarEquipo(f"E{i}", "Portatil", "M", "B")
            else:
                s.recursos.registrarSala(f"S{i}", 10)
    caso.resultado(f"{s.recursos.obtenerCantidad():,} recursos, columnas de la matriz {s.inventario.capacidadRecursos:,}, {t.segundos:.3f} s")
    assert s.recursos.obtenerCantidad() == n and len(s.inventario.recursos) == n


# ---- RQF-006 Consultar recurso (por código o por tipo y nombre) ----
def test_rqf006_exitoso(caso, demo):
    caso.inicio("RQF-006", "Exitoso", "Consultar R0004 por código y buscarlo como Libro con 'estructuras'",
                "Las dos dan el libro de Cormen; 2 unidades en Centro y 0 en Norte (prestado)")
    porCodigo = demo.recursos.obtener("R0004")
    porNombre = demo.recursos.buscarPorTipoYNombre("libro", "estructuras")
    info = porCodigo.obtenerInfo()
    por_sede = demo.inventario.disponibilidadPorSede("R0004")
    caso.resultado(f"{info['nombre']} de {info['Autor']}; búsqueda {porNombre}; {por_sede}")
    assert porNombre == [porCodigo] and por_sede[0] == ("Centro", 2) and por_sede[1] == ("Norte", 0)


def test_rqf006_borde(caso, demo):
    caso.inicio("RQF-006", "Borde", "Código inexistente, recurso dado de baja, solo tipo, solo parte del nombre, "
                "tipo inválido y búsqueda vacía",
                "Errores claros; el de baja se muestra con su estado; solo tipo lista los equipos; 'py' encuentra 'Python 101'")
    errores = []
    for consulta in (lambda: demo.recursos.obtener("R9999"),
                     lambda: demo.recursos.buscarPorTipoYNombre("Revista", "x"),
                     lambda: demo.recursos.buscarPorTipoYNombre(None, "  ")):
        with pytest.raises(ValueError) as e:
            consulta()
        errores.append(str(e.value))
    demo.darDeBajaRecurso("R0006")
    baja = demo.recursos.buscarPorTipoYNombre(None, "fisica")
    equipos = [r.codigo for r in demo.recursos.buscarPorTipoYNombre("Equipo")]
    parte = [r.codigo for r in demo.recursos.buscarPorTipoYNombre("", "PY")]
    caso.resultado("; ".join(errores) + f"; de baja: {baja} -> {demo.recursos.estadoDe(baja[0])}; "
                   f"equipos {equipos}; 'PY' -> {parte}")
    assert demo.recursos.estadoDe(baja[0]) == DADO_DE_BAJA and equipos == ["R0005", "R0002"] and parte == ["R0001"]


def test_rqf006_cuello(caso, masivo, cronometro):
    caso.inicio("RQF-006", "Cuello de botella", "Consultar los 1.500 recursos por código con su disponibilidad y "
                "hacer 100 búsquedas por tipo y nombre", "Todos responden; cada búsqueda trae solo recursos del tipo y nombre pedidos")
    with cronometro() as t:
        filas = [(r.obtenerInfo(), masivo.inventario.disponibilidadPorSede(r.codigo)) for r in masivo.recursos.listarTodos()]
        busquedas = [masivo.recursos.buscarPorTipoYNombre("Libro", f"{i + 1}") for i in range(100)]
    correctas = all(r.TIPO == "Libro" and f"{i + 1}" in r.nombre for i, lista in enumerate(busquedas) for r in lista)
    caso.resultado(f"{len(filas):,} consultas y {sum(map(len, busquedas)):,} resultados de búsqueda, "
                   f"correctos={correctas}, {t.segundos:.3f} s")
    assert len(filas) == 1500 and correctas and t.segundos < 5


# ---- RQF-007 Actualizar recurso ----
def test_rqf007_exitoso(caso, demo):
    caso.inicio("RQF-007", "Exitoso", "Cambiar autor, nombre y categoría de R0001",
                "Cambian los datos y el catálogo ordenado usa el nombre nuevo")
    r = demo.recursos
    r.actualizar("R0001", "autor", "G. van Rossum")
    r.actualizar("R0001", "nombre", "Aprende Python")
    r.actualizar("R0001", "categoria", "C004")
    libro = r.obtener("R0001")
    caso.resultado(f"{libro.nombre}, {libro.autor}, {libro.categoria}; primero del catálogo: {r.catalogoOrdenado()[0].nombre}")
    assert libro.nombre == "Aprende Python" and r.catalogoOrdenado()[0] is libro


def test_rqf007_borde(caso, demo):
    caso.inicio("RQF-007", "Borde", "Campo que no es del tipo, valor inválido y recurso de baja",
                "Rechaza los tres y no cambia nada")
    r, errores = demo.recursos, []
    demo.darDeBajaRecurso("R0006")
    for codigo, campo, valor in (("R0001", "capacidad", 3), ("R0003", "capacidad", "-1"), ("R0006", "nombre", "X")):
        with pytest.raises(ValueError) as e:
            r.actualizar(codigo, campo, valor)
        errores.append(str(e.value))
    caso.resultado("; ".join(errores))
    assert r.obtener("R0003").capacidad == 30


def test_rqf007_cuello(caso, cronometro):
    n = 2000
    caso.inicio("RQF-007", "Cuello de botella", f"Renombrar {n:,} libros (cada cambio reubica el nodo en el BST)",
                "El catálogo sigue ordenado y con los mismos elementos")
    s = _sistemaConRecursos(n)
    with cronometro() as t:
        for i, recurso in enumerate(s.recursos.listarTodos()):
            s.recursos.actualizar(recurso.codigo, "nombre", f"Titulo {(i * 7919) % n:05d}")
    nombres = [x.nombre for x in s.recursos.catalogoOrdenado()]
    caso.resultado(f"{len(nombres):,} en el catálogo, ordenado={nombres == sorted(nombres)}, {t.segundos:.3f} s")
    assert len(nombres) == n and nombres == sorted(nombres)


# ---- RQF-008 Dar de baja recurso ----
def test_rqf008_exitoso(caso, demo):
    caso.inicio("RQF-008", "Exitoso", "Dar de baja R0006 (sin préstamos)",
                "Queda dado de baja, sale del catálogo y no se puede prestar")
    demo.darDeBajaRecurso("R0006")
    with pytest.raises(ValueError) as e:
        demo.prestamos.registrarPrestamo("U001", "R0006", "Centro")
    en_catalogo = any(r.codigo == "R0006" for r in demo.recursos.catalogoOrdenado())
    caso.resultado(f"estado {demo.recursos.obtener('R0006').estado}, en catálogo={en_catalogo}; préstamo: {e.value}")
    assert not en_catalogo


def test_rqf008_borde(caso, demo):
    caso.inicio("RQF-008", "Borde", "Dar de baja R0004 (tiene préstamos activos) y una sala nueva que tiene gente en fila",
                "Rechaza la primera; la segunda se da de baja y cancela los turnos de su fila")
    with pytest.raises(ValueError) as e:
        demo.recursos.darDeBaja("R0004")
    demo.recursos.registrarSala("Sala B", 4)                  # R0007, sin unidades
    demo.turnos.solicitarTurno("U001", "R0007", "Centro")
    canceladas = demo.darDeBajaRecurso("R0007")
    caso.resultado(f"{e.value}; baja de R0007 canceló {canceladas} turno(s)")
    assert canceladas == 1 and demo.turnos.cantidadEspera("R0007") == 0


def test_rqf008_cuello(caso, cronometro):
    n = 2000
    caso.inicio("RQF-008", "Cuello de botella", f"Dar de baja la mitad de {n:,} recursos",
                "El catálogo (BST) queda con la otra mitad")
    s = _sistemaConRecursos(n)
    with cronometro() as t:
        for r in s.recursos.listarTodos()[::2]:
            s.darDeBajaRecurso(r.codigo)
    caso.resultado(f"catálogo {len(s.recursos.catalogo):,}, {t.segundos:.3f} s")
    assert len(s.recursos.catalogo) == n // 2


# ---- RQF-020 Búsqueda de recurso por código (tabla hash) ----
def test_rqf020_exitoso(caso, demo):
    caso.inicio("RQF-020", "Exitoso", "Buscar R0003", "Devuelve la Sala de Estudio")
    r = demo.recursos.buscarxCodigo("R0003")
    caso.resultado(str(r))
    assert r.nombre == "Sala de Estudio"


def test_rqf020_borde(caso):
    caso.inicio("RQF-020", "Borde", "Buscar en un sistema sin recursos y con minúsculas", "None sin error")
    s = Sistema()
    caso.resultado(f"R0001={s.recursos.buscarxCodigo('R0001')}, r0001={s.recursos.buscarxCodigo('r0001')}")
    assert s.recursos.buscarxCodigo("r0001") is None


def test_rqf020_cuello(caso, masivo, cronometro):
    caso.inicio("RQF-020", "Cuello de botella", "500 búsquedas: tabla hash vs. secuencial sobre 1.500 recursos",
                "La tabla hash es al menos 10 veces más rápida")
    todos = masivo.recursos.listarTodos()
    objetivos = [r.codigo for r in todos[-500:]]
    with cronometro() as th:
        for c in objetivos:
            masivo.recursos.buscarxCodigo(c)
    with cronometro() as ts:
        for c in objetivos:
            busquedaSecuencial(todos, c, clave=lambda r: r.codigo)
    caso.resultado(f"hash {th.segundos * 1000:.2f} ms vs. secuencial {ts.segundos * 1000:.1f} ms")
    assert ts.segundos > 10 * th.segundos


# ---- RQF-023 Listar por categoría o estado ----
def test_rqf023_exitoso(caso, demo):
    caso.inicio("RQF-023", "Exitoso", "Listar la categoría Ingenieria (con subcategorías) y los recursos Prestados",
                "Ingenieria: 4 recursos por nombre; Prestado: la Sala de Estudio")
    ingenieria = [r.codigo for r in demo.recursos.listarPorCategoria("C002")]
    prestados = [r.codigo for r in demo.recursos.listarPorEstado("prestado")]
    caso.resultado(f"Ingenieria={ingenieria}; Prestado={prestados}")
    assert ingenieria == ["R0004", "R0005", "R0002", "R0001"] and prestados == ["R0003"]


def test_rqf023_borde(caso, demo):
    caso.inicio("RQF-023", "Borde", "Categoría sin recursos, sin subcategorías, estado inválido y categoría inexistente",
                "Lista vacía, solo los directos y errores claros")
    vacia = demo.recursos.listarPorCategoria("C003")
    directos = [r.codigo for r in demo.recursos.listarPorCategoria("C002", incluirSubcategorias=False)]
    errores = []
    for llamada in (lambda: demo.recursos.listarPorEstado("roto"), lambda: demo.recursos.listarPorCategoria("C999")):
        with pytest.raises(ValueError) as e:
            llamada()
        errores.append(str(e.value))
    sinUnidades = [r.codigo for r in demo.recursos.listarPorEstado(SIN_UNIDADES)]
    caso.resultado(f"C003={vacia}; C002 directos={directos}; sin unidades={sinUnidades}; " + "; ".join(errores))
    assert vacia == [] and directos == ["R0002"] and sinUnidades == ["R0006"]


def test_rqf023_cuello(caso, masivo, cronometro):
    caso.inicio("RQF-023", "Cuello de botella", "Listar por cada categoría principal y por estado Disponible (1.500 recursos)",
                "Cada listado sale ordenado por nombre")
    with cronometro() as t:
        listados = [masivo.recursos.listarPorCategoria(c.codigo) for c in masivo.categorias.raices]
        disponibles = masivo.recursos.listarPorEstado(DISPONIBLE)
    ordenado = all([r.nombre.lower() for r in lista] == sorted(r.nombre.lower() for r in lista) for lista in listados + [disponibles])
    caso.resultado(f"{sum(map(len, listados)):,} por categoría, {len(disponibles):,} disponibles, ordenados={ordenado}, {t.segundos:.3f} s")
    caso.nota("Usa inserción (O(n²)); con miles de elementos sigue respondiendo en menos de un segundo.")
    assert ordenado and sum(map(len, listados)) == 1500


# ---- RQF-042 Registrar y listar sedes ----
def test_rqf042_exitoso(caso, demo):
    caso.inicio("RQF-042", "Exitoso", "Registrar la sede 'Oriente'",
                "Aparece en la lista con código S05 y tiene su fila en la matriz")
    sede = demo.recursos.registrarSede("Oriente")
    caso.resultado(f"{sede}; sedes={demo.recursos.nombresSedes()}; filas de la matriz={len(demo.inventario.matriz)}")
    assert sede.codigo == "S05" and len(demo.inventario.matriz) == 5


def test_rqf042_borde(caso, demo):
    caso.inicio("RQF-042", "Borde", "Registrar 'centro' (ya existe con otra mayúscula) y un nombre vacío",
                "Rechaza ambos; validarSede('centro') devuelve 'Centro'")
    errores = []
    for nombre in ("centro", "  "):
        with pytest.raises(ValueError) as e:
            demo.recursos.registrarSede(nombre)
        errores.append(str(e.value))
    caso.resultado("; ".join(errores) + f"; validarSede('centro')={demo.recursos.validarSede('centro')}")
    assert demo.recursos.validarSede("centro") == "Centro"


def test_rqf042_cuello(caso, cronometro):
    n = 300
    caso.inicio("RQF-042", "Cuello de botella", f"Registrar {n} sedes con 200 recursos ya creados",
                f"Matriz de {n} × 200 con todas las celdas en 0")
    s = _sistemaConRecursos(200)
    with cronometro() as t:
        for i in range(n - 1):
            s.recursos.registrarSede(f"Sede {i}")
    caso.resultado(f"{s.recursos.obtenerCantidadSedes()} sedes, {len(s.inventario.matriz)} filas, {t.segundos:.3f} s")
    assert len(s.inventario.matriz) == n and s.inventario.totalDisponible("R0200") == 0


# ---- RQF-052 Índice ordenado del catálogo (BST) ----
def test_rqf052_exitoso(caso, demo):
    caso.inicio("RQF-052", "Exitoso", "Recorrer en orden el catálogo de la demo",
                "Recursos vigentes en orden alfabético")
    nombres = [r.nombre for r in demo.recursos.catalogoOrdenado()]
    caso.resultado(str(nombres))
    assert nombres == sorted(nombres, key=str.lower)


def test_rqf052_borde(caso, demo):
    caso.inicio("RQF-052", "Borde", "Dos recursos con el mismo nombre y uno dado de baja",
                "Ambos homónimos quedan (la clave incluye el código) y el de baja sale")
    demo.recursos.registrarLibro("Python 101", "Otro autor", "978-0", 2021)
    demo.darDeBajaRecurso("R0006")
    nombres = [(r.nombre, r.codigo) for r in demo.recursos.catalogoOrdenado()]
    caso.resultado(str(nombres))
    assert ("Python 101", "R0001") in nombres and ("Python 101", "R0007") in nombres
    assert all(c != "R0006" for _, c in nombres)


def test_rqf052_cuello(caso, cronometro):
    n = 5000
    caso.inicio("RQF-052", "Cuello de botella", f"{n:,} recursos con nombres en orden al azar",
                "El recorrido en orden sale ordenado; altura muy por debajo de n")
    s = Sistema()
    with cronometro() as t:
        for i in range(n):
            s.recursos.registrarLibro(f"Titulo {(i * 7919) % n:05d}", "A", "I", 2000)
    nombres = [r.nombre for r in s.recursos.catalogoOrdenado()]
    caso.resultado(f"altura {s.recursos.catalogo.obtenerAltura()} con {n:,} nodos, {t.segundos:.3f} s")
    assert nombres == sorted(nombres) and s.recursos.catalogo.obtenerAltura() < n // 10
