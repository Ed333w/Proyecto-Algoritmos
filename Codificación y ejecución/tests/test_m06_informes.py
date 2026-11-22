"""M06 · Informes: RQF-021, 022, 024, 031, 032, 033, 034, 043 y 044."""

from datetime import datetime, timedelta

import pytest

from modulos import Sistema


def _recursosConFechas(n):
    s = Sistema()
    base = datetime(2020, 1, 1)
    for i in range(n):
        codigo = s.recursos.registrarLibro(f"Libro {(i * 7919) % n:05d}", "A", "I", 2000)
        s.recursos.obtener(codigo).fechaRegistro = base + timedelta(minutes=(i * 104729) % n)
    return s


# ---- RQF-021 Más prestados ----
def test_rqf021_exitoso(caso, demo):
    caso.inicio("RQF-021", "Exitoso", "Ordenar recursos por número de préstamos", "R0001 (4), R0004 (3), R0002 (2)...")
    top = [(r.codigo, r.cantidadPrestamos) for r in demo.informes.masPrestados(3)]
    caso.resultado(str(top))
    assert top == [("R0001", 4), ("R0004", 3), ("R0002", 2)]


def test_rqf021_borde(caso, demo):
    caso.inicio("RQF-021", "Borde", "Empates (R0003 y R0005 con 1) y cantidad 0",
                "En empate conserva el orden por código (merge sort estable); cantidad 0 se rechaza")
    unos = [r.codigo for r in demo.informes.masPrestados() if r.cantidadPrestamos == 1]
    with pytest.raises(ValueError) as e:
        demo.informes.masPrestados(0)
    caso.resultado(f"empatados {unos}; {e.value}")
    assert unos == ["R0003", "R0005"]


def test_rqf021_cuello(caso, masivo, cronometro):
    caso.inicio("RQF-021", "Cuello de botella", "Ordenar 1.500 recursos con 6.000 préstamos", "Orden no creciente")
    with cronometro() as t:
        lista = masivo.informes.masPrestados()
    valores = [r.cantidadPrestamos for r in lista]
    caso.resultado(f"máximo {valores[0]}, mínimo {valores[-1]}, {t.segundos:.3f} s")
    assert valores == sorted(valores, reverse=True)


# ---- RQF-022 Por antigüedad ----
def test_rqf022_exitoso(caso, demo):
    caso.inicio("RQF-022", "Exitoso", "Ordenar la demo por fecha de registro", "R0001 a R0006 (se registraron en ese orden)")
    codigos = [r.codigo for r in demo.informes.porAntiguedad()]
    caso.resultado(str(codigos))
    assert codigos == ["R0001", "R0002", "R0003", "R0004", "R0005", "R0006"]


def test_rqf022_borde(caso):
    caso.inicio("RQF-022", "Borde", "Sin recursos; y más recientes primero con fechas iguales",
                "Lista vacía; con fechas iguales desempata por código")
    s = Sistema()
    vacio = s.informes.porAntiguedad()
    for i in range(3):
        s.recursos.registrarLibro(f"L{i}", "A", "I", 2000)
    for r in s.recursos.listarTodos():
        r.fechaRegistro = datetime(2024, 1, 1)
    recientes = [r.codigo for r in s.informes.porAntiguedad(masAntiguosPrimero=False)]
    caso.resultado(f"vacío {vacio}; recientes primero {recientes}")
    assert vacio == [] and recientes == ["R0003", "R0002", "R0001"]


def test_rqf022_cuello(caso, cronometro):
    n = 5000
    caso.inicio("RQF-022", "Cuello de botella", f"Quick sort de {n:,} recursos con fechas desordenadas", "Fechas crecientes")
    s = _recursosConFechas(n)
    with cronometro() as t:
        lista = s.informes.porAntiguedad()
    fechas = [r.fechaRegistro for r in lista]
    caso.resultado(f"de {fechas[0]:%Y-%m-%d %H:%M} a {fechas[-1]:%Y-%m-%d %H:%M}, {t.segundos:.3f} s")
    assert fechas == sorted(fechas) and t.segundos < 3


# ---- RQF-024 Búsqueda por nombre ----
def test_rqf024_exitoso(caso, demo):
    caso.inicio("RQF-024", "Exitoso", "Buscar 'estructuras de datos' (binaria iterativa, recursiva y secuencial)",
                "Las tres encuentran R0004")
    a = demo.informes.buscarPorNombre("estructuras de datos")
    b = demo.informes.buscarPorNombre("Estructuras de Datos", recursiva=True)
    c = demo.informes.buscarPorNombreSecuencial("ESTRUCTURAS DE DATOS")
    caso.resultado(f"{a}, {b}, {c}")
    assert a[0].codigo == b[0].codigo == c.codigo == "R0004"


def test_rqf024_borde(caso, demo):
    caso.inicio("RQF-024", "Borde", "Nombre inexistente, nombre vacío y dos recursos con el mismo nombre",
                "Vacío, error y los dos homónimos")
    demo.recursos.registrarLibro("Python 101", "Otro", "978-0", 2022)
    homonimos = [r.codigo for r in demo.informes.buscarPorNombre("python 101")]
    with pytest.raises(ValueError) as e:
        demo.informes.buscarPorNombre(" ")
    caso.resultado(f"inexistente {demo.informes.buscarPorNombre('Quijote')}; {e.value}; homónimos {homonimos}")
    assert demo.informes.buscarPorNombre("Quijote") == [] and homonimos == ["R0001", "R0007"]


def test_rqf024_cuello(caso, cronometro):
    n = 5000
    caso.inicio("RQF-024", "Cuello de botella", f"300 búsquedas por nombre en {n:,} recursos: binaria vs. secuencial",
                "Mismos resultados; la binaria sobre el catálogo ordenado es mucho más rápida")
    s = _recursosConFechas(n)
    nombres = [f"libro {(i * 31) % n:05d}" for i in range(300)]
    s.informes.buscarPorNombre(nombres[0])            # arma el catálogo ordenado una vez (O(n))
    with cronometro() as tb:
        binarias = [s.informes.buscarPorNombre(x)[0].codigo for x in nombres]
    with cronometro() as ts:
        secuenciales = [s.informes.buscarPorNombreSecuencial(x).codigo for x in nombres]
    caso.resultado(f"binaria {tb.segundos * 1000:.1f} ms vs. secuencial {ts.segundos * 1000:.1f} ms "
                   f"({ts.segundos / tb.segundos:.0f} veces)")
    caso.nota("El arreglo del catálogo se rehace solo cuando se registra, renombra o da de baja un recurso.")
    assert binarias == secuenciales and tb.segundos * 10 < ts.segundos


# ---- RQF-031 Informe de más prestados ----
def test_rqf031_exitoso(caso, demo):
    caso.inicio("RQF-031", "Exitoso", "Informe con los 2 recursos de mayor demanda", "Python 101 y Estructuras de Datos")
    nombres = [r.nombre for r in demo.informes.masPrestados(2)]
    caso.resultado(str(nombres))
    assert nombres == ["Python 101", "Estructuras de Datos"]


def test_rqf031_borde(caso):
    caso.inicio("RQF-031", "Borde", "Pedir el top 10 con solo 2 recursos y sin préstamos", "Devuelve los 2 con 0 préstamos")
    s = Sistema()
    s.recursos.registrarLibro("A", "x", "1", 2000)
    s.recursos.registrarLibro("B", "x", "2", 2000)
    top = [(r.nombre, r.cantidadPrestamos) for r in s.informes.masPrestados(10)]
    caso.resultado(str(top))
    assert top == [("A", 0), ("B", 0)]


def test_rqf031_cuello(caso, masivo, cronometro):
    caso.inicio("RQF-031", "Cuello de botella", "Top 10 repetido 50 veces (1.500 recursos)", "Siempre el mismo resultado")
    with cronometro() as t:
        resultados = {tuple(r.codigo for r in masivo.informes.masPrestados(10)) for _ in range(50)}
    caso.resultado(f"{len(resultados)} resultado distinto, {t.segundos:.3f} s")
    assert len(resultados) == 1


# ---- RQF-032 Tasa de devolución ----
def test_rqf032_exitoso(caso, demo):
    caso.inicio("RQF-032", "Exitoso", "Tasa de la demo", "5 a tiempo de 7 evaluables = 71,4 %")
    t = demo.informes.tasaDevolucion()
    caso.resultado(f"{t['aTiempo']} de {t['total']} = {t['porcentaje']} %")
    assert (t["aTiempo"], t["total"], t["porcentaje"]) == (5, 7, 71.4)


def test_rqf032_borde(caso, base):
    caso.inicio("RQF-032", "Borde", "Sin préstamos; y un préstamo devuelto justo el día límite",
                "0 % sin división por cero; el del día límite cuenta a tiempo")
    vacio = base.informes.tasaDevolucion()
    inicio = datetime.now() - timedelta(days=20)
    codigo = base.prestamos.registrarPrestamo("U001", "R0001", "Centro", fechaPrestamo=inicio)
    base.prestamos.registrarDevolucion(codigo, inicio + timedelta(days=14))
    t = base.informes.tasaDevolucion()
    caso.resultado(f"vacío {vacio['porcentaje']} %; día límite -> {t['porcentaje']} %")
    assert vacio["porcentaje"] == 0.0 and t["porcentaje"] == 100.0


def test_rqf032_cuello(caso, masivo, cronometro):
    caso.inicio("RQF-032", "Cuello de botella", "Tasa sobre 6.000 préstamos", "a tiempo + tarde = total y 0–100 %")
    with cronometro() as t:
        r = masivo.informes.tasaDevolucion()
    caso.resultado(f"{r['aTiempo']:,} a tiempo de {r['total']:,} = {r['porcentaje']} %, {t.segundos:.3f} s")
    assert r["aTiempo"] + r["tarde"] == r["total"] and 0 <= r["porcentaje"] <= 100


# ---- RQF-033 Demanda por categoría ----
def test_rqf033_exitoso(caso, demo):
    caso.inicio("RQF-033", "Exitoso", "Demanda agrupada en la categoría principal",
                "Ingenieria 10 préstamos y 1 sin categoría (la sala)")
    r = demo.informes.demandaPorCategoria(agruparEnPrincipal=True)
    caso.resultado(str(r))
    assert r == [("Ingenieria", 10), ("Sin categoría", 1)]


def test_rqf033_borde(caso):
    caso.inicio("RQF-033", "Borde", "Sistema sin préstamos", "Lista vacía")
    caso.resultado(str(Sistema().informes.demandaPorCategoria()))
    assert Sistema().informes.demandaPorCategoria() == []


def test_rqf033_cuello(caso, masivo, cronometro):
    caso.inicio("RQF-033", "Cuello de botella", "Demanda por subcategoría con 6.000 préstamos y 30 categorías",
                "La suma por categoría es igual al total de préstamos")
    with cronometro() as t:
        r = masivo.informes.demandaPorCategoria()
    caso.resultado(f"{len(r)} categorías, mayor {r[0]}, {t.segundos:.3f} s")
    assert sum(n for _, n in r) == masivo.prestamos.obtenerCantidad()


# ---- RQF-034 Informe de inventario ----
def test_rqf034_exitoso(caso, demo):
    caso.inicio("RQF-034", "Exitoso", "Informe de inventario de la demo",
                "3 libros (7 unidades), 2 equipos (3) y 1 sala (0)")
    r = demo.informes.reporteInventario()
    caso.resultado(str(r))
    assert r == [("Libro", 3, 3, 7), ("Equipo", 2, 2, 3), ("Sala", 1, 1, 0)]


def test_rqf034_borde(caso, demo):
    caso.inicio("RQF-034", "Borde", "Un recurso dado de baja", "Cuenta como registrado pero no como vigente")
    demo.darDeBajaRecurso("R0006")
    libro = demo.informes.reporteInventario()[0]
    caso.resultado(str(libro))
    assert libro == ("Libro", 3, 2, 7)


def test_rqf034_cuello(caso, masivo, cronometro):
    caso.inicio("RQF-034", "Cuello de botella", "Informe con 1.500 recursos", "Los registrados suman 1.500")
    with cronometro() as t:
        r = masivo.informes.reporteInventario()
    caso.resultado(f"{r}, {t.segundos:.3f} s")
    assert sum(fila[1] for fila in r) == 1500


# ---- RQF-043 Reporte de uso ----
def test_rqf043_exitoso(caso, demo):
    caso.inicio("RQF-043", "Exitoso", "Reporte de uso de la demo", "11 préstamos: 5 activos, 6 devueltos, 1 atrasado")
    r = demo.informes.reporteUso()
    caso.resultado(str(r))
    assert (r["Préstamos registrados"], r["Préstamos activos"], r["Préstamos devueltos"], r["Préstamos atrasados"]) == (11, 5, 6, 1)


def test_rqf043_borde(caso):
    caso.inicio("RQF-043", "Borde", "Sistema vacío", "Todos los indicadores en 0")
    r = Sistema().informes.reporteUso()
    caso.resultado(str(r))
    assert all(v == 0 for v in r.values())


def test_rqf043_cuello(caso, masivo, cronometro):
    caso.inicio("RQF-043", "Cuello de botella", "Reporte con 6.000 préstamos", "Activos + devueltos = registrados")
    with cronometro() as t:
        r = masivo.informes.reporteUso()
    caso.resultado(f"{r}, {t.segundos:.3f} s")
    assert r["Préstamos activos"] + r["Préstamos devueltos"] == r["Préstamos registrados"]


# ---- RQF-044 Ordenados por nombre ----
def test_rqf044_exitoso(caso, demo):
    caso.inicio("RQF-044", "Exitoso", "Usuarios y recursos por nombre",
                "Ana, Carlos, Luis, Maria, Pedro; recursos en orden alfabético")
    usuarios = [u.nombre.split()[0] for u in demo.informes.usuariosPorNombre()]
    recursos = [r.nombre for r in demo.informes.recursosPorNombre()]
    caso.resultado(f"{usuarios}; {recursos}")
    assert usuarios == ["Ana", "Carlos", "Luis", "Maria", "Pedro"] and recursos == sorted(recursos, key=str.lower)


def test_rqf044_borde(caso):
    caso.inicio("RQF-044", "Borde", "Nombres que solo cambian en mayúsculas y nombres iguales",
                "Ignora mayúsculas y en empate ordena por código")
    s = Sistema()
    for i, (nombre, correo) in enumerate((("beto", "b1@x.co"), ("Ana", "a@x.co"), ("Beto", "b2@x.co"))):
        s.usuarios.registrar(nombre, correo, "CC", f"5000{i}")
    orden = [(u.nombre, u.codigo) for u in s.informes.usuariosPorNombre()]
    caso.resultado(str(orden))
    assert orden == [("Ana", "U002"), ("beto", "U001"), ("Beto", "U003")]


def test_rqf044_cuello(caso, masivo, cronometro):
    caso.inicio("RQF-044", "Cuello de botella", "3.000 usuarios con merge sort y 1.500 recursos por el BST",
                "Ambos listados ordenados")
    with cronometro() as t:
        usuarios = [u.nombre.lower() for u in masivo.informes.usuariosPorNombre()]
        recursos = [r.nombre.lower() for r in masivo.informes.recursosPorNombre()]
    caso.resultado(f"{len(usuarios):,} usuarios y {len(recursos):,} recursos, {t.segundos:.3f} s")
    assert usuarios == sorted(usuarios) and recursos == sorted(recursos)
