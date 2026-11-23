"""M07 · Inventario: RQF-008 (condición del recurso, baja lógica), 009, 010 y 045."""

import pytest

from modulos import Sistema


def _matrizGrande(sedes, recursos):
    s = Sistema()
    for i in range(sedes):
        s.recursos.registrarSede(f"Sede {i}")
    for i in range(recursos):
        s.recursos.registrarLibro(f"L{i}", "A", "I", 2000)
    return s


# ---- RQF-008 Dar de baja recurso: cambio de condición desde Inventario; nunca se borra ----
def test_rqf008_exitoso(caso, demo):
    caso.inicio("RQF-008", "Exitoso", "Marcar R0006 como Dañado (desde Inventario) y después volverlo a Operativo",
                "Mientras está dañado: sale del catálogo, no se presta y sigue registrado con su historial; "
                "al volver a Operativo regresa al catálogo")
    total = demo.recursos.obtenerCantidad()
    demo.cambiarCondicionRecurso("R0006", "Dañado")
    with pytest.raises(ValueError) as e:
        demo.prestamos.registrarPrestamo("U001", "R0006", "Centro")
    en_catalogo = any(r.codigo == "R0006" for r in demo.recursos.catalogoOrdenado())
    sigue = demo.recursos.buscarxCodigo("R0006") is not None and demo.recursos.obtenerCantidad() == total
    demo.cambiarCondicionRecurso("R0006", "operativo")
    vuelve = any(r.codigo == "R0006" for r in demo.recursos.catalogoOrdenado())
    caso.resultado(f"dañado: en catálogo={en_catalogo}, sigue registrado={sigue}; préstamo rechazado: {e.value}; "
                   f"operativo de nuevo: en catálogo={vuelve}, estado {demo.recursos.obtener('R0006').estado}")
    assert not en_catalogo and sigue and vuelve and demo.recursos.obtener("R0006").estaVigente()


def test_rqf008_borde(caso, demo):
    caso.inicio("RQF-008", "Borde", "R0004 con préstamos activos; R0006 con una persona en fila marcado Dañado y luego "
                "Operativo; una sala con fila dada de baja; condición repetida y condición inválida",
                "R0004 se rechaza; la fila de R0006 se conserva, no recibe turnos nuevos y se atiende al cargar "
                "unidades ya operativo; la baja de la sala cancela su fila; errores claros")
    errores = []
    with pytest.raises(ValueError) as e:
        demo.cambiarCondicionRecurso("R0004", "Dañado")
    errores.append(str(e.value))
    demo.turnos.solicitarTurno("U001", "R0006", "Centro")
    demo.cambiarCondicionRecurso("R0006", "Dañado")
    filaConservada = demo.turnos.cantidadEspera("R0006", "Centro")
    with pytest.raises(ValueError):
        demo.turnos.solicitarTurno("U003", "R0006", "Centro")
    for llamada in (lambda: demo.cambiarCondicionRecurso("R0006", "dañado"),
                    lambda: demo.cambiarCondicionRecurso("R0006", "Perdido")):
        with pytest.raises(ValueError) as e:
            llamada()
        errores.append(str(e.value))
    demo.cambiarCondicionRecurso("R0006", "Operativo")
    asignados = demo.fijarUnidades("R0006", "Centro", 1)
    sala = demo.recursos.registrarSala("Sala B", 4, categoria="C003")
    demo.turnos.solicitarTurno("U001", sala, "Centro")
    canceladas = demo.darDeBajaRecurso(sala)
    caso.resultado(f"fila de R0006 conservada {filaConservada}; al cargar unidades se prestó a "
                   f"{demo.prestamos.obtener(asignados[0]).codigoUsuario}; baja de {sala} canceló {canceladas}; "
                   + "; ".join(errores))
    assert filaConservada == 1 and demo.prestamos.obtener(asignados[0]).codigoUsuario == "U001" and canceladas == 1


def test_rqf008_cuello(caso, cronometro):
    n = 2000
    caso.inicio("RQF-008", "Cuello de botella", f"Dar de baja la mitad de {n:,} recursos y marcar otro cuarto como Sin uso",
                "El catálogo (BST) queda con la cuarta parte y ningún recurso se borra")
    s = Sistema()
    for i in range(n):
        s.recursos.registrarLibro(f"Libro {i:05d}", "Autor", f"978-{i}", 2000)
    todos = s.recursos.listarTodos()
    with cronometro() as t:
        for r in todos[::2]:
            s.darDeBajaRecurso(r.codigo)
        for r in todos[1::4]:
            s.cambiarCondicionRecurso(r.codigo, "Sin uso")
    caso.resultado(f"catálogo {len(s.recursos.catalogo):,}, registrados {s.recursos.obtenerCantidad():,}, "
                   f"no operativos {len(s.condiciones.listarNoOperativos()):,}, {t.segundos:.3f} s")
    assert len(s.recursos.catalogo) == n // 4 and s.recursos.obtenerCantidad() == n


# ---- RQF-009 Disponibilidad por sede ----
def test_rqf009_exitoso(caso, base):
    caso.inicio("RQF-009", "Exitoso", "Consultar R0001 en Centro antes y después de prestar y devolver",
                "2 -> 1 -> 2")
    antes = base.inventario.obtenerDisponibilidad("R0001", "Centro")
    codigo = base.prestamos.registrarPrestamo("U001", "R0001", "Centro")
    durante = base.inventario.obtenerDisponibilidad("R0001", "Centro")
    base.prestamos.registrarDevolucion(codigo)
    despues = base.inventario.obtenerDisponibilidad("R0001", "Centro")
    caso.resultado(f"{antes} -> {durante} -> {despues}")
    assert (antes, durante, despues) == (2, 1, 2)


def test_rqf009_borde(caso, base):
    caso.inicio("RQF-009", "Borde", "Sede sin unidades, sede inexistente y recurso inexistente",
                "0 para la sede sin unidades; error claro para los otros dos")
    errores = []
    for recurso, sede in (("R0001", "Marte"), ("R0099", "Centro")):
        with pytest.raises(ValueError) as e:
            base.inventario.obtenerDisponibilidad(recurso, sede)
        errores.append(str(e.value))
    caso.resultado(f"Norte={base.inventario.obtenerDisponibilidad('R0001', 'Norte')}; " + "; ".join(errores))
    assert base.inventario.obtenerDisponibilidad("R0001", "Norte") == 0


def test_rqf009_cuello(caso, cronometro):
    caso.inicio("RQF-009", "Cuello de botella", "50.000 consultas sobre una matriz de 20 sedes × 2.000 recursos",
                "O(1) por consulta (dos búsquedas en tabla hash y un acceso a la matriz)")
    s = _matrizGrande(20, 2000)
    sedes, recursos = s.recursos.nombresSedes(), [r.codigo for r in s.recursos.listarTodos()]
    with cronometro() as t:
        for i in range(50000):
            s.inventario.obtenerDisponibilidad(recursos[i % 2000], sedes[i % 20])
    caso.resultado(f"{t.segundos:.3f} s ({t.segundos / 50000 * 1e6:.1f} µs por consulta)")
    assert t.segundos < 3


# ---- RQF-010 Matrices sede × recurso y sede × día ----
def test_rqf010_exitoso(caso, demo):
    caso.inicio("RQF-010", "Exitoso", "Matriz sede × recurso y proyección sede × día de la sala R0003 (3 días)",
                "La sala está en 0 hoy y vuelve a 1 mañana en Centro (vence el préstamo de U001)")
    texto = demo.inventario.mostrarMatriz()
    sedes, fechas, matriz = demo.inventario.matrizSedeDia("R0003", demo.prestamos.listarActivos(), 3)
    _, filas = demo.inventario.filasPorRecurso(["R0001"])
    caso.resultado(f"{len(texto.splitlines()) - 2} recursos (filas) por {len(sedes)} sedes (columnas) en la matriz "
                   f"sede × recurso; R0001 por sede {filas[0][1]}, total {filas[0][2]}; Centro por día: {matriz[0]}")
    assert sedes[0] == "Centro" and matriz[0] == [0, 1, 1] and len(fechas) == 3
    assert len(texto.splitlines()) - 2 == 12 and filas[0][1][:2] == [4, 1] and filas[0][2] == 5


def test_rqf010_borde(caso, demo):
    caso.inicio("RQF-010", "Borde", "Proyección de 1 día, de 0 días y de un recurso sin préstamos",
                "1 columna; 0 días se rechaza; sin préstamos la fila es constante")
    _, fechas, _ = demo.inventario.matrizSedeDia("R0001", demo.prestamos.listarActivos(), 1)
    with pytest.raises(ValueError) as e:
        demo.inventario.matrizSedeDia("R0001", [], 0)
    _, _, matriz = demo.inventario.matrizSedeDia("R0006", demo.prestamos.listarActivos(), 4)
    caso.resultado(f"{len(fechas)} columna; {e.value}; R0006 {matriz[0]}")
    assert len(fechas) == 1 and matriz[0] == [0, 0, 0, 0]


def test_rqf010_cuello(caso, masivo, cronometro):
    caso.inicio("RQF-010", "Cuello de botella", "Matriz sede × recurso de 6 × 1.500 y proyección de 30 días del más prestado",
                "Ambas se generan; la proyección nunca baja de un día al siguiente")
    with cronometro() as t:
        texto = masivo.inventario.mostrarMatriz()
        top = masivo.informes.masPrestados(1)[0]
        _, _, matriz = masivo.inventario.matrizSedeDia(top.codigo, masivo.prestamos.listarActivos(), 30)
    crece = all(fila[i] <= fila[i + 1] for fila in matriz for i in range(29))
    caso.resultado(f"{len(texto):,} caracteres de matriz; proyección no decreciente={crece}; {t.segundos:.3f} s")
    assert crece


# ---- RQF-045 Fijar unidades ----
def test_rqf045_exitoso(caso, demo):
    caso.inicio("RQF-045", "Exitoso", "Fijar 3 unidades de R0006 en Sur", "Queda en 3 y se puede prestar")
    demo.fijarUnidades("R0006", "sur", 3)
    codigo = demo.prestamos.registrarPrestamo("U001", "R0006", "Sur")
    caso.resultado(f"unidades 3 -> préstamo {codigo} -> {demo.inventario.obtenerDisponibilidad('R0006', 'Sur')}")
    assert demo.inventario.obtenerDisponibilidad("R0006", "Sur") == 2


def test_rqf045_borde(caso, demo):
    caso.inicio("RQF-045", "Borde", "Cantidad negativa, texto y fijar unidades a un recurso con fila de espera",
                "Rechaza los dos primeros; al poner 2 unidades a la sala se atiende la fila (U002 y U004)")
    errores = []
    for cantidad in (-1, "dos"):
        with pytest.raises(ValueError) as e:
            demo.fijarUnidades("R0003", "Centro", cantidad)
        errores.append(str(e.value))
    asignados = demo.fijarUnidades("R0003", "Centro", 2)
    usuarios = [demo.prestamos.obtener(c).codigoUsuario for c in asignados]
    caso.resultado("; ".join(errores) + f"; asignados a {usuarios}")
    assert usuarios == ["U002", "U004"] and demo.inventario.obtenerDisponibilidad("R0003", "Centro") == 0


def test_rqf045_cuello(caso, cronometro):
    caso.inicio("RQF-045", "Cuello de botella", "Fijar unidades en todas las celdas de 10 sedes × 2.000 recursos",
                "20.000 celdas actualizadas; el total coincide")
    s = _matrizGrande(10, 2000)
    with cronometro() as t:
        for r in s.recursos.listarTodos():
            for sede in s.recursos.nombresSedes():
                s.inventario.fijarUnidades(r.codigo, sede, 3)
    total = sum(s.inventario.totalDisponible(r.codigo) for r in s.recursos.listarTodos())
    caso.resultado(f"total {total:,} unidades, {t.segundos:.3f} s")
    assert total == 60000
