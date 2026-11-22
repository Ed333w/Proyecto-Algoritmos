"""M04 · Turnos: RQF-016, 017, 018, 040 y 041."""

import pytest


def _agotar(s):
    """Presta las 2 unidades de R0001 en Centro para que haya que hacer fila."""
    s.prestamos.registrarPrestamo("U001", "R0001", "Centro")
    s.prestamos.registrarPrestamo("U002", "R0001", "Centro")


def _sistemaConFila(base, personas):
    _agotar(base)
    for i in range(personas):
        base.usuarios.registrar(f"Espera {i}", f"espera{i}@uni.edu", "CC", str(2000000 + i))
    for u in base.usuarios.listarTodos()[2:]:
        base.turnos.solicitarTurno(u.codigo, "R0001", "Centro")
    return base


# ---- RQF-016 Solicitar turno ----
def test_rqf016_exitoso(caso, base):
    caso.inicio("RQF-016", "Exitoso", "Sin unidades de R0001 en Centro, U003 pide turno",
                "Turno T0001 en posición 1, guarda la sede pedida")
    _agotar(base)
    base.usuarios.registrar("Carla", "carla@uni.edu", "CC", "3000001")
    codigo = base.turnos.solicitarTurno("U003", "R0001", "Centro")
    sol = base.turnos.buscarSolicitud(codigo)
    caso.resultado(f"{codigo}, posición {base.turnos.posicion(codigo)}, sede {sol.sede}")
    assert codigo == "T0001" and base.turnos.posicion(codigo) == 1 and sol.sede == "Centro"


def test_rqf016_borde(caso, base):
    caso.inicio("RQF-016", "Borde", "Pedir turno habiendo unidades; repetir turno; usuario inactivo",
                "Los tres se rechazan con el motivo")
    errores = []
    with pytest.raises(ValueError) as e:
        base.turnos.solicitarTurno("U001", "R0001", "Centro")
    errores.append(str(e.value))
    _agotar(base)
    base.turnos.solicitarTurno("U001", "R0001", "Centro")
    with pytest.raises(ValueError) as e:
        base.turnos.solicitarTurno("U001", "R0001", "Centro")
    errores.append(str(e.value))
    base.usuarios.registrar("Inactiva", "i@uni.edu", "CC", "3000002")
    base.usuarios.darDeBaja("U003")
    with pytest.raises(ValueError) as e:
        base.turnos.solicitarTurno("U003", "R0001", "Centro")
    errores.append(str(e.value))
    caso.resultado("; ".join(errores))
    assert base.turnos.cantidadEspera("R0001") == 1


def test_rqf016_cuello(caso, base, cronometro):
    n = 3000
    caso.inicio("RQF-016", "Cuello de botella", f"{n:,} usuarios hacen fila por el mismo recurso",
                f"Fila de {n:,} en orden de llegada; la validación de repetidos recorre la fila (O(n))")
    with cronometro() as t:
        _sistemaConFila(base, n)
    fila = base.turnos.obtenerFila("R0001", "Centro")
    caso.resultado(f"{len(fila):,} en fila, primero {fila[0].codigoUsuario}, último {fila[-1].codigoUsuario}, {t.segundos:.3f} s")
    caso.nota("Revisar repetidos recorre la fila; con miles de personas por recurso convendría un conjunto por fila.")
    assert len(fila) == n and t.segundos < 15


# ---- RQF-017 Asignar siguiente turno al devolver ----
def test_rqf017_exitoso(caso, base):
    caso.inicio("RQF-017", "Exitoso", "Fila U003, U004; se devuelve una unidad",
                "La unidad pasa automáticamente a U003; U004 queda primero")
    _sistemaConFila(base, 2)
    asignados = base.prestamos.registrarDevolucion("P0001")
    nuevo = base.prestamos.obtener(asignados[0])
    caso.resultado(f"asignado {nuevo.codigo} a {nuevo.codigoUsuario}; sigue {base.turnos.verSiguiente('R0001', 'Centro').codigoUsuario}")
    assert nuevo.codigoUsuario == "U003" and base.turnos.verSiguiente("R0001", "Centro").codigoUsuario == "U004"


def test_rqf017_borde(caso, base):
    caso.inicio("RQF-017", "Borde", "El primero de la fila quedó inactivo; devolución en otra sede",
                "Se salta al inactivo (su turno se cancela); la fila de Centro no recibe unidades de Norte")
    _sistemaConFila(base, 2)
    base.inventario.fijarUnidades("R0001", "Norte", 1)
    otro = base.prestamos.registrarPrestamo("U003", "R0001", "Norte")
    base.prestamos.registrarDevolucion(otro)                 # vuelve en Norte: no atiende la fila de Centro
    enFila = base.turnos.cantidadEspera("R0001", "Centro")
    base.usuarios.darDeBaja("U003")
    asignados = base.prestamos.registrarDevolucion("P0001")
    caso.resultado(f"tras devolver en Norte siguen {enFila} en fila de Centro; en Centro se asignó a "
                   f"{base.prestamos.obtener(asignados[0]).codigoUsuario}; turno de U003: {base.turnos.buscarSolicitud('T0001').estado}")
    assert enFila == 2 and base.prestamos.obtener(asignados[0]).codigoUsuario == "U004"


def test_rqf017_cuello(caso, base, cronometro):
    n = 2000
    caso.inicio("RQF-017", "Cuello de botella", f"Fila de {n:,}; se fijan {n:,} unidades de una vez",
                "Toda la fila se atiende en orden de llegada")
    _sistemaConFila(base, n)
    with cronometro() as t:
        asignados = base.fijarUnidades("R0001", "Centro", n)
    usuarios = [base.prestamos.obtener(c).codigoUsuario for c in asignados]
    caso.resultado(f"{len(asignados):,} asignados, fila restante {base.turnos.cantidadEspera('R0001')}, {t.segundos:.3f} s")
    assert usuarios == [u.codigo for u in base.usuarios.listarTodos()[2:]] and base.turnos.cantidadEspera("R0001") == 0


# ---- RQF-018 Consultar fila ----
def test_rqf018_exitoso(caso, demo):
    caso.inicio("RQF-018", "Exitoso", "Fila de R0003 (sala) en Centro", "U002 y luego U004")
    fila = [s.codigoUsuario for s in demo.turnos.obtenerFila("R0003", "Centro")]
    caso.resultado(f"{fila}, total {demo.turnos.cantidadEspera('R0003')}")
    assert fila == ["U002", "U004"]


def test_rqf018_borde(caso, demo):
    caso.inicio("RQF-018", "Borde", "Recurso sin fila y fila de todas las sedes de R0004",
                "Vacía; R0004 solo tiene a U001 esperando en Norte")
    vacia = demo.turnos.obtenerFila("R0001")
    todas = [(s.codigoUsuario, s.sede) for s in demo.turnos.obtenerFila("R0004")]
    caso.resultado(f"R0001 {vacia}; R0004 {todas}")
    assert vacia == [] and todas == [("U001", "Norte")]


def test_rqf018_cuello(caso, masivo, cronometro):
    caso.inicio("RQF-018", "Cuello de botella", "Fila de los 1.500 recursos (6 sedes cada uno)",
                "La suma coincide con el total en espera")
    with cronometro() as t:
        suma = sum(masivo.turnos.cantidadEspera(r.codigo) for r in masivo.recursos.listarTodos())
    caso.resultado(f"{suma} en espera, {t.segundos:.3f} s")
    assert suma == masivo.turnos.totalEnEspera()


# ---- RQF-040 Ver siguiente sin retirarlo ----
def test_rqf040_exitoso(caso, demo):
    caso.inicio("RQF-040", "Exitoso", "Ver quién sigue en la sala (dos veces)", "U002 las dos veces; la fila no cambia")
    a, b = demo.turnos.verSiguiente("R0003", "Centro"), demo.turnos.verSiguiente("R0003", "Centro")
    caso.resultado(f"{a.codigoUsuario}, {b.codigoUsuario}; en fila {demo.turnos.cantidadEspera('R0003')}")
    assert a is b and demo.turnos.cantidadEspera("R0003") == 2


def test_rqf040_borde(caso, demo):
    caso.inicio("RQF-040", "Borde", "Ver siguiente de un recurso sin fila", "None")
    caso.resultado(str(demo.turnos.verSiguiente("R0001", "Centro")))
    assert demo.turnos.verSiguiente("R0001", "Centro") is None


def test_rqf040_cuello(caso, base, cronometro):
    caso.inicio("RQF-040", "Cuello de botella", "10.000 consultas del frente con 1.000 en fila", "O(1) cada una")
    _sistemaConFila(base, 1000)
    with cronometro() as t:
        for _ in range(10000):
            frente = base.turnos.verSiguiente("R0001", "Centro")
    caso.resultado(f"frente {frente.codigoUsuario}, {t.segundos:.3f} s")
    assert frente.codigoUsuario == "U003" and t.segundos < 1


# ---- RQF-041 Cancelar solicitud ----
def test_rqf041_exitoso(caso, demo):
    caso.inicio("RQF-041", "Exitoso", "Cancelar el turno de U002 en la sala", "U004 pasa al frente")
    demo.turnos.cancelarSolicitud("T0001")
    caso.resultado(f"T0001 {demo.turnos.buscarSolicitud('T0001').estado}; sigue {demo.turnos.verSiguiente('R0003', 'Centro').codigoUsuario}")
    assert demo.turnos.verSiguiente("R0003", "Centro").codigoUsuario == "U004"


def test_rqf041_borde(caso, demo):
    caso.inicio("RQF-041", "Borde", "Cancelar dos veces y cancelar un turno inexistente", "Ambos con error")
    demo.turnos.cancelarSolicitud("T0002")
    errores = []
    for codigo in ("T0002", "T0999"):
        with pytest.raises(ValueError) as e:
            demo.turnos.cancelarSolicitud(codigo)
        errores.append(str(e.value))
    caso.resultado("; ".join(errores))
    assert demo.turnos.cantidadEspera("R0003") == 1


def test_rqf041_cuello(caso, base, cronometro):
    n = 2000
    caso.inicio("RQF-041", "Cuello de botella", f"Cancelar la mitad de una fila de {n:,}",
                "Quedan los demás en el mismo orden")
    _sistemaConFila(base, n)
    turnos = base.turnos.obtenerFila("R0001", "Centro")
    with cronometro() as t:
        for s in turnos[::2]:
            base.turnos.cancelarSolicitud(s.codigo)
    restantes = base.turnos.obtenerFila("R0001", "Centro")
    caso.resultado(f"quedan {len(restantes):,}, {t.segundos:.3f} s")
    assert restantes == turnos[1::2]
