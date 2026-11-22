"""M09 · Red de sedes con grafo (RQF-028, 029 y 030).

Cada sede registrada en M02 es un vértice; cada conexión entre sedes es una
arista no dirigida. La distancia se mide en tramos (número de conexiones).

- RQF-028 Sede más cercana con unidades: BFS desde la sede actual.
- RQF-029 Ruta más corta: BFS con padres; rutas alternativas con DFS y backtracking.
- RQF-030 Sedes aisladas: componentes conexas con DFS.
"""

from estructuras import Grafo
from modulos.M07_Inventario import validarOperativo

HOLGURA_TRAMOS = 3


class GestorRedSedes:

    def __init__(self, gestorRecursos, gestorInventario):
        self.recursos = gestorRecursos
        self.inventario = gestorInventario
        self.grafo = Grafo()

    def _sincronizar(self):
        """Toda sede registrada en M02 es un vértice, aunque aún no tenga conexiones."""
        for nombre in self.recursos.nombresSedes():
            self.grafo.agregarVertice(nombre)

    def conectar(self, sedeA, sedeB):
        self._sincronizar()
        a, b = self.recursos.validarSede(sedeA), self.recursos.validarSede(sedeB)
        if not self.grafo.agregarArista(a, b):
            raise ValueError(f"{a} y {b} ya están conectadas")
        return a, b

    def desconectar(self, sedeA, sedeB):
        a, b = self.recursos.validarSede(sedeA), self.recursos.validarSede(sedeB)
        if not self.grafo.eliminarArista(a, b):
            raise ValueError(f"{a} y {b} no están conectadas")

    def conexiones(self):
        self._sincronizar()
        return self.grafo.aristas()

    # ---- RQF-028 ----
    def sedeMasCercanaConRecurso(self, sedeActual, codigoRecurso):
        """(sede, tramos, unidades) de la sede alcanzable más cercana con unidades, o None."""
        self._sincronizar()
        origen = self.recursos.validarSede(sedeActual)
        recurso = validarOperativo(self.recursos, codigoRecurso)   # un recurso dañado no se busca en otra sede
        for sede, tramos in self.grafo.recorridoAmplitud(origen):
            unidades = self.inventario.obtenerDisponibilidad(recurso.codigo, sede)
            if unidades > 0:
                return sede, tramos, unidades
        return None

    # ---- RQF-029 ----
    def rutaMasCorta(self, origen, destino):
        self._sincronizar()
        a, b = self.recursos.validarSede(origen), self.recursos.validarSede(destino)
        return self.grafo.caminoMasCorto(a, b)

    def rutasAlternativas(self, origen, destino, maximo=5, holgura=HOLGURA_TRAMOS):
        """Rutas sin repetir sedes de hasta 'holgura' tramos más que la más corta (backtracking)."""
        corta = self.rutaMasCorta(origen, destino)
        if not corta:
            return []
        return self.grafo.todosLosCaminos(corta[0], corta[-1], maximo, len(corta) - 1 + holgura)

    # ---- RQF-030 ----
    def sedesAisladas(self):
        """Sedes que no están en la red principal (la componente conexa más grande)."""
        self._sincronizar()
        componentes = self.grafo.componentesConexas()
        return [sede for grupo in componentes[1:] for sede in grupo]

    def componentes(self):
        self._sincronizar()
        return self.grafo.componentesConexas()
