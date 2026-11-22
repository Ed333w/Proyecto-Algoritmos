"""Configuración común de las pruebas.

Cada prueba documenta su caso con el fixture 'caso':

    caso.inicio("RQF-001", "Exitoso", "Qué se prueba", "Qué se espera")
    ...
    caso.resultado("Qué se obtuvo")
    caso.nota("Observación opcional")

Al terminar, se escribe tests/reporte/resultados_pruebas.json con todos los casos
(esperado, obtenido, estado y duración). Con ese archivo se arma el documento de
casos de prueba, así lo obtenido sale de la ejecución real.
"""

import json
import os
import re
import sys
import time
from datetime import datetime

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from modulos import Sistema                                      # noqa: E402
from persistencia.datos_demo import crearSistemaDemo             # noqa: E402
from persistencia.datos_masivos import crearSistemaMasivo        # noqa: E402

REPORTE = os.environ.get("REPORTE_PRUEBAS") or os.path.join(RAIZ, "tests", "reporte", "resultados_pruebas.json")
_casos = []


def formatoEspañol(texto):
    """3,000.5 -> 3.000,5 (separadores de miles y decimales en español)."""
    texto = re.sub(r"(?<=\d)\.(?=\d)", "\x00", texto)
    texto = re.sub(r"(?<=\d),(?=\d{3}(?!\d))", ".", texto)
    return texto.replace("\x00", ",")


class Caso:
    def __init__(self, nodo):
        archivo = os.path.basename(str(nodo.fspath))
        self.datos = {"prueba": nodo.name, "archivo": archivo,
                      "modulo": archivo[:-3].replace("test_", "").split("_")[0].upper(),
                      "rqf": "", "tipo": "", "descripcion": "", "esperado": "",
                      "obtenido": "", "observacion": "", "estado": "", "duracion": 0.0}

    def inicio(self, rqf, tipo, descripcion, esperado):
        self.datos.update(rqf=rqf, tipo=tipo, descripcion=formatoEspañol(descripcion),
                          esperado=formatoEspañol(esperado))

    def resultado(self, obtenido):
        self.datos["obtenido"] = formatoEspañol(obtenido)

    def nota(self, observacion):
        self.datos["observacion"] = formatoEspañol(observacion)


@pytest.fixture
def caso(request):
    registro = Caso(request.node)
    request.node._caso = registro
    return registro


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    reporte = (yield).get_result()
    registro = getattr(item, "_caso", None)
    if registro is None or reporte.when != "call":
        return
    registro.datos["duracion"] = round(reporte.duration, 4)
    registro.datos["estado"] = "Aprobado" if reporte.passed else "Fallido"
    if reporte.failed:
        mensaje = str(call.excinfo.value).strip().splitlines()[0] if call.excinfo else "falló"
        registro.datos["obtenido"] = registro.datos["obtenido"] or f"Error: {mensaje}"
    _casos.append(registro.datos)


def pytest_sessionfinish(session, exitstatus):
    if not _casos:
        return
    os.makedirs(os.path.dirname(REPORTE), exist_ok=True)
    with open(REPORTE, "w", encoding="utf-8") as archivo:
        json.dump({"fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                   "python": sys.version.split()[0], "plataforma": sys.platform,
                   "casos": _casos}, archivo, ensure_ascii=False, indent=1)


# ---------------- Datos para las pruebas ----------------

class Cronometro:
    def __enter__(self):
        self._inicio = time.perf_counter()
        return self

    def __exit__(self, *_):
        self.segundos = time.perf_counter() - self._inicio


@pytest.fixture
def cronometro():
    return Cronometro


def crearSistemaBase():
    """3 sedes conectadas en cadena, 2 usuarios y un libro con 2 unidades en Centro."""
    s = Sistema()
    for sede in ("Centro", "Norte", "Sur"):
        s.recursos.registrarSede(sede)
    s.red.conectar("Centro", "Norte")
    s.red.conectar("Norte", "Sur")
    s.usuarios.registrar("Ana Garcia", "ana@uni.edu", "CC", "1111111")       # U001
    s.usuarios.registrar("Luis Perez", "luis@uni.edu", "CC", "2222222")      # U002
    s.recursos.registrarLibro("Python 101", "Guido", "978-1", 2020)   # R0001
    s.inventario.fijarUnidades("R0001", "Centro", 2)
    return s


@pytest.fixture
def base():
    return crearSistemaBase()


@pytest.fixture
def demo():
    return crearSistemaDemo()


@pytest.fixture(scope="session")
def masivo():
    """Volumen para los cuellos de botella: 3.000 usuarios, 1.500 recursos y 6.000 préstamos.
    Es de solo lectura: las pruebas que modifican datos crean su propio sistema."""
    return crearSistemaMasivo(usuarios=3000, recursos=1500, prestamos=6000, solicitudes=300)
