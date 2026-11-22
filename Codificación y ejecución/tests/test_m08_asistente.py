"""M08 · Asistente de decisiones del administrador: RQF-046, 047, 048, 049 y 051."""

from datetime import datetime, timedelta

import pytest

from modulos.M08_Asistente_Decisiones import ATRASO, SIN_UNIDADES, REINCIDENTE
from persistencia.datos_masivos import crearSistemaMasivo


# ---- RQF-046 Redistribución ----
def test_rqf046_exitoso(caso, demo):
    caso.inicio("RQF-046", "Exitoso", "Recomendar traslados de R0004 (Norte tiene fila y 0 unidades) y aplicarlo",
                "Mover 1 de Centro a Norte; al aplicarlo se presta a U001, que esperaba en Norte")
    traslados = demo.asistente.recomendarRedistribucion("R0004")
    asignados = demo.asistente.aplicarTraslado(traslados[0])
    caso.resultado(f"{traslados}; asignado {asignados} a {demo.prestamos.obtener(asignados[0]).codigoUsuario}")
    assert (traslados[0].origen, traslados[0].destino, traslados[0].unidades) == ("Centro", "Norte", 1)
    assert demo.prestamos.obtener(asignados[0]).codigoUsuario == "U001"


def test_rqf046_borde(caso, demo):
    caso.inicio("RQF-046", "Borde", "Recurso sin unidades en ninguna sede, sin demanda, y traslado de más unidades de las que hay",
                "Sin recomendaciones en los dos primeros; el traslado imposible se rechaza")
    sinUnidades = demo.asistente.recomendarRedistribucion("R0003")
    sinDemanda = demo.asistente.recomendarRedistribucion("R0006")
    with pytest.raises(ValueError) as e:
        demo.inventario.trasladar("R0002", "Centro", "Sur", 5)
    caso.resultado(f"R0003 {sinUnidades}; R0006 {sinDemanda}; {e.value}")
    assert sinUnidades == [] and sinDemanda == []


def test_rqf046_cuello(caso, masivo, cronometro):
    caso.inicio("RQF-046", "Cuello de botella", "Recomendación para los 1.500 recursos × 6 sedes",
                "Ningún traslado deja una sede con unidades negativas")
    with cronometro() as t:
        traslados = masivo.asistente.recomendarRedistribucion()
    movido = {}
    for tr in traslados:
        clave = (tr.codigoRecurso, tr.origen)
        movido[clave] = movido.get(clave, 0) + tr.unidades
    valido = all(masivo.inventario.obtenerDisponibilidad(r, s) >= n for (r, s), n in movido.items())
    caso.resultado(f"{len(traslados):,} traslados sugeridos, válidos={valido}, {t.segundos:.3f} s")
    assert valido and t.segundos < 5


# ---- RQF-047 Prioridad de compras ----
def test_rqf047_exitoso(caso, demo):
    caso.inicio("RQF-047", "Exitoso", "Top 3 de compras de la demo",
                "Primero la sala R0003 (2 personas en fila y 1 unidad): índice 2,5")
    top = demo.asistente.priorizarCompras(3)
    caso.resultado(", ".join(f"{r.codigo} índice {i}" for r, i, *_ in top))
    assert top[0][0].codigo == "R0003" and top[0][1] == 2.5


def test_rqf047_borde(caso, base):
    caso.inicio("RQF-047", "Borde", "Sin demanda y cantidad 0", "Lista vacía y error")
    vacio = base.asistente.priorizarCompras(5)
    with pytest.raises(ValueError) as e:
        base.asistente.priorizarCompras(0)
    caso.resultado(f"{vacio}; {e.value}")
    assert vacio == []


def test_rqf047_cuello(caso, masivo, cronometro):
    caso.inicio("RQF-047", "Cuello de botella", "Top 20 entre 1.500 recursos (montículo de máximos)",
                "Índices en orden no creciente")
    with cronometro() as t:
        top = masivo.asistente.priorizarCompras(20)
    indices = [i for _, i, *_ in top]
    caso.resultado(f"mayor {indices[0]}, menor {indices[-1]}, {t.segundos:.3f} s")
    assert len(top) == 20 and indices == sorted(indices, reverse=True)


# ---- RQF-048 Predicción ----
def test_rqf048_exitoso(caso, demo):
    caso.inicio("RQF-048", "Exitoso", "Predecir la sala R0003 (sin unidades) y R0001 (con unidades)",
                "Sala: 1 día en Centro (vence el préstamo de U001); R0001 disponible ahora, promedio 3,3 días")
    sala = demo.asistente.predecirDisponibilidad("R0003")
    libro = demo.asistente.predecirDisponibilidad("R0001")
    caso.resultado(f"R0003 en {sala['dias']} día(s) en {sala['sede']}; R0001 ahora={libro['disponibleAhora']}, "
                   f"promedio {libro['promedioDias']} con confianza {libro['confianza']:.0%}")
    assert sala["dias"] == 1 and sala["sede"] == "Centro" and libro["disponibleAhora"] and libro["promedioDias"] == 3.3


def test_rqf048_borde(caso, demo):
    caso.inicio("RQF-048", "Borde", "Recurso sin unidades ni préstamos (R0006) y recurso de baja",
                "R0006: no se libera solo (días = None); el de baja da error")
    r = demo.asistente.predecirDisponibilidad("R0006")
    demo.darDeBajaRecurso("R0006")
    with pytest.raises(ValueError) as e:
        demo.asistente.predecirDisponibilidad("R0006")
    caso.resultado(f"días {r['dias']}, muestras {r['muestras']}; {e.value}")
    assert r["dias"] is None and not r["disponibleAhora"]


def test_rqf048_cuello(caso, masivo, cronometro):
    caso.inicio("RQF-048", "Cuello de botella", "Predicción para los 1.500 recursos",
                "Cada predicción tiene confianza entre 0 y 1 y días ≥ 0 cuando aplica")
    with cronometro() as t:
        preds = [masivo.asistente.predecirDisponibilidad(r.codigo) for r in masivo.recursos.listarTodos()]
    validas = all(0 <= p["confianza"] <= 1 and (p["dias"] is None or p["dias"] >= 0) for p in preds)
    caso.resultado(f"{len(preds):,} predicciones válidas={validas}, {t.segundos:.3f} s")
    caso.nota("Cada predicción recorre el historial del recurso; con 6.000 préstamos tarda unos segundos en total.")
    assert validas and t.segundos < 30


# ---- RQF-049 Alertas priorizadas ----
def test_rqf049_exitoso(caso, demo):
    caso.inicio("RQF-049", "Exitoso", "Alertas de la demo en orden de urgencia",
                "Atraso de P0007, sala sin unidades con 2 en fila, R0004 en Norte y U005 reincidente")
    alertas = demo.asistente.alertasPriorizadas()
    caso.resultado(" | ".join(f"{a.urgencia} {a.tipo}" for a in alertas))
    assert [a.tipo for a in alertas] == [ATRASO, SIN_UNIDADES, SIN_UNIDADES, REINCIDENTE]


def test_rqf049_borde(caso, base):
    caso.inicio("RQF-049", "Borde", "Sistema sin problemas; luego un usuario con 1 solo atraso",
                "Sin alertas; con 1 atraso aparece la alerta de atraso pero no la de reincidente")
    vacio = base.asistente.alertasPriorizadas()
    base.prestamos.registrarPrestamo("U001", "R0001", "Centro", fechaPrestamo=datetime.now() - timedelta(days=16))
    tipos = [a.tipo for a in base.asistente.alertasPriorizadas()]
    caso.resultado(f"vacío {vacio}; después {tipos}")
    assert vacio == [] and tipos == [ATRASO]


def test_rqf049_cuello(caso, masivo, cronometro):
    caso.inicio("RQF-049", "Cuello de botella", "Alertas con 6.000 préstamos, 1.500 recursos y 6 sedes",
                "Urgencias en orden no creciente")
    with cronometro() as t:
        alertas = masivo.asistente.alertasPriorizadas()
    urgencias = [a.urgencia for a in alertas]
    caso.resultado(f"{len(alertas):,} alertas, {t.segundos:.3f} s")
    assert urgencias == sorted(urgencias, reverse=True) and t.segundos < 5


# ---- RQF-051 Préstamos próximos a vencer ----
def test_rqf051_exitoso(caso, demo):
    caso.inicio("RQF-051", "Exitoso", "Préstamos que vencen en los próximos 2 días",
                "P0010 (mañana) y luego P0011 (en 2 días)")
    proximos = [(p.codigo, d) for p, d in demo.asistente.vencimientosProximos(2)]
    caso.resultado(str(proximos))
    assert proximos == [("P0010", 1), ("P0011", 2)]


def test_rqf051_borde(caso, base):
    caso.inicio("RQF-051", "Borde", "Uno vence hoy, uno ya venció y anticipación 0 y 31 días",
                "Con 0 días solo el de hoy; el vencido no aparece (es atraso); 31 se rechaza")
    hoy = datetime.now()
    venceHoy = base.prestamos.registrarPrestamo("U001", "R0001", "Centro", fechaPrestamo=hoy - timedelta(days=14))
    base.prestamos.registrarPrestamo("U002", "R0001", "Centro", fechaPrestamo=hoy - timedelta(days=15))
    lista = [(p.codigo, d) for p, d in base.asistente.vencimientosProximos(0)]
    with pytest.raises(ValueError) as e:
        base.asistente.vencimientosProximos(31)
    caso.resultado(f"{lista}; {e.value}")
    assert lista == [(venceHoy, 0)]


def test_rqf051_cuello(caso, cronometro):
    caso.inicio("RQF-051", "Cuello de botella", "Vencimientos de 7 días con 6.000 préstamos (montículo de mínimos)",
                "Salen ordenados del más próximo al más lejano")
    s = crearSistemaMasivo(usuarios=3000, recursos=1500, prestamos=6000, solicitudes=0)
    with cronometro() as t:
        lista = s.asistente.vencimientosProximos(7)
    fechas = [p.fechaLimite() for p, _ in lista]
    caso.resultado(f"{len(lista)} préstamos por vencer, {t.segundos:.3f} s")
    assert fechas == sorted(fechas) and all(0 <= d <= 7 for _, d in lista)
