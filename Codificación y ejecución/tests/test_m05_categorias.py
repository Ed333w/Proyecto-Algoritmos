"""M05 · Categorías: RQF-025, 026 y 027."""

import pytest

from modulos import GestorCategorias


def _arbolProfundo(niveles, hijasPorNivel=2):
    g = GestorCategorias()
    g.registrarCategoria("C0", "Raiz")
    actuales, numero = ["C0"], 0
    for nivel in range(niveles):
        nuevas = []
        for padre in actuales:
            for _ in range(hijasPorNivel):
                numero += 1
                g.registrarCategoria(f"C{numero}", f"Cat {numero}", padre)
                nuevas.append(f"C{numero}")
        actuales = nuevas
    return g


# ---- RQF-025 Crear categoría o subcategoría ----
def test_rqf025_exitoso(caso, demo):
    caso.inicio("RQF-025", "Exitoso", "Crear 'Optica' dentro de Fisica (C016)",
                "Queda en el nivel 4 con ruta Material de estudio > Libros > Ciencias > Fisica > Optica")
    demo.categorias.registrarCategoria("C017", "Optica", "C016")
    c = demo.categorias.obtener("C017")
    caso.resultado(f"{c.ruta()}, nivel {c.nivel()}")
    assert c.ruta() == "Material de estudio > Libros > Ciencias > Fisica > Optica" and c.nivel() == 4


def test_rqf025_borde(caso, demo):
    caso.inicio("RQF-025", "Borde", "Código repetido, padre inexistente, nombre repetido bajo el mismo padre y código vacío",
                "Rechaza los cuatro; el mismo nombre en otro padre sí se permite")
    errores = []
    for args in (("C001", "Otra"), ("C020", "X", "C999"), ("C020", "laptops", "C009"), ("", "X")):
        with pytest.raises(ValueError) as e:
            demo.categorias.registrarCategoria(*args)
        errores.append(str(e.value))
    demo.categorias.registrarCategoria("C020", "Laptops", "C012")
    caso.resultado("; ".join(errores) + "; 'Laptops' dentro de Libros aceptada")
    assert demo.categorias.obtenerCantidad() == 17


def test_rqf025_cuello(caso, cronometro):
    caso.inicio("RQF-025", "Cuello de botella", "Árbol de 10 niveles con 2 hijas por nodo (2.047 categorías)",
                "Todas registradas con su nivel correcto")
    with cronometro() as t:
        g = _arbolProfundo(10)
    hoja = g.obtener("C2046")
    caso.resultado(f"{g.obtenerCantidad():,} categorías, nivel de la última hoja {hoja.nivel()}, {t.segundos:.3f} s")
    assert g.obtenerCantidad() == 2047 and hoja.nivel() == 10


# ---- RQF-026 Consultar subárbol ----
def test_rqf026_exitoso(caso, demo):
    caso.inicio("RQF-026", "Exitoso", "Consultar Equipos (C009) con todo lo que cuelga",
                "Equipos > Computadores y Laptops, y sus 5 recursos (incluidos los que no están operativos)")
    nodos = [(c.nombre, p) for c, p in demo.categorias.subarbol("C009")]
    recursos = [r.codigo for r in demo.recursos.listarPorCategoria("C009")]
    caso.resultado(f"{nodos}; recursos {recursos}")
    assert nodos == [("Equipos", 0), ("Computadores", 1), ("Laptops", 1)] and len(recursos) == 5


def test_rqf026_borde(caso, demo):
    caso.inicio("RQF-026", "Borde", "Consultar una hoja (C005, Sala con televisor) y un código inexistente",
                "La hoja devuelve solo ella misma; el inexistente da error")
    hoja = demo.categorias.subarbol("c005")
    with pytest.raises(ValueError) as e:
        demo.categorias.subarbol("C404")
    caso.resultado(f"{hoja}; {e.value}")
    assert len(hoja) == 1


def test_rqf026_cuello(caso, cronometro):
    caso.inicio("RQF-026", "Cuello de botella", "Subárbol de la raíz con 2.047 categorías (recursivo)",
                "Las 2.047 en preorden")
    g = _arbolProfundo(10)
    with cronometro() as t:
        nodos = g.subarbol("C0")
    caso.resultado(f"{len(nodos):,} nodos, profundidad máxima {max(p for _, p in nodos)}, {t.segundos:.3f} s")
    assert len(nodos) == 2047


# ---- RQF-027 Índice AVL ----
def test_rqf027_exitoso(caso, demo):
    caso.inicio("RQF-027", "Exitoso", "Índice de las 16 categorías de la demo",
                "Recorrido en orden por código y AVL balanceado")
    codigos = [c.codigo for c in demo.categorias.listarPorCodigo()]
    caso.resultado(f"{codigos}, altura {demo.categorias.alturaIndice()}, balanceado {demo.categorias.indice.estaBalanceado()}")
    assert codigos == sorted(codigos) and demo.categorias.indice.estaBalanceado()


def test_rqf027_borde(caso):
    caso.inicio("RQF-027", "Borde", "Índice vacío y con una sola categoría", "Altura 0 y 1")
    g = GestorCategorias()
    vacio = g.alturaIndice()
    g.registrarCategoria("C1", "Una")
    caso.resultado(f"vacío {vacio}, uno {g.alturaIndice()}")
    assert vacio == 0 and g.alturaIndice() == 1


def test_rqf027_cuello(caso, cronometro):
    n = 5000
    caso.inicio("RQF-027", "Cuello de botella", f"{n:,} categorías con códigos en orden (C00001, C00002...)",
                "Altura del AVL ≤ 1,44·log2(n) (≈ 18); un BST tendría altura 5.000")
    g = GestorCategorias()
    with cronometro() as t:
        for i in range(n):
            g.registrarCategoria(f"C{i:05d}", f"Categoria {i}")
    caso.resultado(f"altura {g.alturaIndice()}, {g.indice.rotaciones:,} rotaciones, {t.segundos:.3f} s")
    assert g.alturaIndice() <= 18 and g.indice.estaBalanceado()
