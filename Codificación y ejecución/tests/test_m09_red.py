"""M09 · Red de sedes: RQF-028, 029 y 030."""

import pytest

from modulos import Sistema


def _cadena(n):
    s = Sistema()
    for i in range(n):
        s.recursos.registrarSede(f"S{i}")
    for i in range(n - 1):
        s.red.conectar(f"S{i}", f"S{i + 1}")
    s.recursos.registrarLibro("Libro", "A", "I", 2000)
    return s


# ---- RQF-028 Sede más cercana con unidades ----
def test_rqf028_exitoso(caso, demo):
    caso.inicio("RQF-028", "Exitoso", "Desde Norte, buscar R0004 (Norte no tiene unidades)",
                "Centro, a 1 tramo, con 2 unidades")
    r = demo.red.sedeMasCercanaConRecurso("Norte", "R0004")
    caso.resultado(str(r))
    assert r == ("Centro", 1, 2)


def test_rqf028_borde(caso, demo):
    caso.inicio("RQF-028", "Borde", "La sede actual sí tiene; desde una sede aislada; sede inexistente",
                "Distancia 0; None porque no alcanza ninguna; error")
    mismo = demo.red.sedeMasCercanaConRecurso("Centro", "R0001")
    aislada = demo.red.sedeMasCercanaConRecurso("Occidente", "R0001")
    with pytest.raises(ValueError) as e:
        demo.red.sedeMasCercanaConRecurso("Marte", "R0001")
    caso.resultado(f"{mismo}; {aislada}; {e.value}")
    assert mismo[1] == 0 and aislada is None


def test_rqf028_cuello(caso, cronometro):
    n = 1000
    caso.inicio("RQF-028", "Cuello de botella", f"Red en cadena de {n:,} sedes; el recurso solo está en la última",
                f"La encuentra a {n - 1} tramos (BFS O(V + E))")
    s = _cadena(n)
    s.inventario.fijarUnidades("R0001", f"S{n - 1}", 1)
    with cronometro() as t:
        r = s.red.sedeMasCercanaConRecurso("S0", "R0001")
    caso.resultado(f"{r}, {t.segundos:.3f} s")
    assert r == (f"S{n - 1}", n - 1, 1)


# ---- RQF-029 Ruta más corta ----
def test_rqf029_exitoso(caso, demo):
    caso.inicio("RQF-029", "Exitoso", "Ruta de Norte a Sur y rutas alternativas",
                "Directa Norte -> Sur; alternativa Norte -> Centro -> Sur")
    ruta = demo.red.rutaMasCorta("Norte", "Sur")
    alternativas = demo.red.rutasAlternativas("Norte", "Sur")
    caso.resultado(f"{ruta}; {alternativas}")
    assert ruta == ["Norte", "Sur"] and alternativas == [["Norte", "Sur"], ["Norte", "Centro", "Sur"]]


def test_rqf029_borde(caso, demo):
    caso.inicio("RQF-029", "Borde", "Ruta a la misma sede y a una sede aislada", "[Centro] y []")
    misma = demo.red.rutaMasCorta("Centro", "Centro")
    sinRuta = demo.red.rutaMasCorta("Centro", "Occidente")
    caso.resultado(f"{misma}; {sinRuta}")
    assert misma == ["Centro"] and sinRuta == []


def test_rqf029_cuello(caso, cronometro):
    n = 600
    caso.inicio("RQF-029", "Cuello de botella", f"Ruta de punta a punta en una cadena de {n} sedes con un atajo",
                "BFS toma el atajo (300 tramos); las alternativas descartan la ruta de 599 tramos por la poda; "
                "sin poda el backtracking encuentra las 2")
    s = _cadena(n)
    s.red.conectar("S0", f"S{n // 2}")
    with cronometro() as t:
        ruta = s.red.rutaMasCorta("S0", f"S{n - 1}")
        alternativas = s.red.rutasAlternativas("S0", f"S{n - 1}")
        sinPoda = s.red.grafo.todosLosCaminos("S0", f"S{n - 1}")
    caso.resultado(f"{len(ruta) - 1} tramos (sin atajo serían {n - 1}); alternativas con poda {len(alternativas)}, "
                   f"sin poda {len(sinPoda)} ({len(sinPoda[-1]) - 1} tramos la larga); {t.segundos:.3f} s")
    caso.nota("Con una cadena de 1.000 sedes el backtracking superaba el límite de recursión de Python; "
              "se corrigió podando rutas de más de 3 tramos extra sobre la más corta y haciendo el DFS con pila propia.")
    assert len(ruta) - 1 == 300 and alternativas == [ruta] and len(sinPoda) == 2


# ---- RQF-030 Sedes aisladas ----
def test_rqf030_exitoso(caso, demo):
    caso.inicio("RQF-030", "Exitoso", "Detectar sedes aisladas en la demo", "Occidente")
    caso.resultado(str(demo.red.sedesAisladas()))
    assert demo.red.sedesAisladas() == ["Occidente"]


def test_rqf030_borde(caso, demo):
    caso.inicio("RQF-030", "Borde", "Conectar Occidente; luego quitar una conexión que no existe",
                "Ya no hay aisladas; quitar una conexión inexistente da error")
    demo.red.conectar("Occidente", "Sur")
    with pytest.raises(ValueError) as e:
        demo.red.desconectar("Occidente", "Norte")
    caso.resultado(f"aisladas {demo.red.sedesAisladas()}; {e.value}")
    assert demo.red.sedesAisladas() == []


def test_rqf030_cuello(caso, cronometro):
    caso.inicio("RQF-030", "Cuello de botella", "500 sedes: una red principal de 400 y 100 sedes sueltas",
                "Encuentra las 100 aisladas")
    s = Sistema()
    for i in range(500):
        s.recursos.registrarSede(f"S{i}")
    for i in range(399):
        s.red.conectar(f"S{i}", f"S{i + 1}")
    with cronometro() as t:
        aisladas = s.red.sedesAisladas()
    caso.resultado(f"{len(aisladas)} aisladas, {t.segundos:.3f} s")
    assert len(aisladas) == 100
