# Maria Fernanda Morales

#M07 - Inventario

# El inventario se representa como una matriz de sedes x recursos, donde cada celda contiene la 
# cantidad de unidades disponibles de un recurso en una sede. Se usan tablas hash para mapear 
# nombres de sedes y códigos de recursos a índices de filas y columnas, respectivamente. 
# Se permite redimensionar la matriz cuando se agregan más recursos que la capacidad inicial.


from datetime import timedelta

from estructuras import TablaHash, VectorDinamico
from modulos.comun import validarEntero, ahoraSiFalta


class GestorInventario:

    def __init__(self, capacidadRecursos=50):
        self.capacidadRecursos = capacidadRecursos
        self.matriz = []                      # filas = sedes (arreglos de tamaño fijo)
        self.filaDeSede = TablaHash(53)
        self.columnaDeRecurso = TablaHash()
        self.sedes = VectorDinamico()         # nombre de la sede por fila
        self.recursos = VectorDinamico()      # código del recurso por columna

    # ---- estructura ----
    def _redimensionarColumnas(self):
        nueva = self.capacidadRecursos * 2
        for i, fila in enumerate(self.matriz):
            self.matriz[i] = fila + [0] * (nueva - self.capacidadRecursos)
        self.capacidadRecursos = nueva

    def registrarSede(self, nombreSede):
        if self.filaDeSede.contiene(nombreSede):
            return self.filaDeSede.buscar(nombreSede)
        self.filaDeSede.insertar(nombreSede, len(self.sedes))
        self.sedes.agregar(nombreSede)
        self.matriz.append([0] * self.capacidadRecursos)
        return len(self.sedes) - 1

    def registrarRecurso(self, codigoRecurso):
        if self.columnaDeRecurso.contiene(codigoRecurso):
            return self.columnaDeRecurso.buscar(codigoRecurso)
        if len(self.recursos) == self.capacidadRecursos:
            self._redimensionarColumnas()
        self.columnaDeRecurso.insertar(codigoRecurso, len(self.recursos))
        self.recursos.agregar(codigoRecurso)
        return len(self.recursos) - 1

    def _celda(self, codigoRecurso, sede):
        i = self.filaDeSede.buscar(sede)
        j = self.columnaDeRecurso.buscar(codigoRecurso)
        if i is None:
            raise ValueError(f"La sede '{sede}' no está en el inventario")
        if j is None:
            raise ValueError(f"El recurso {codigoRecurso} no está en el inventario")
        return i, j

    # ---- consultas ----
    def obtenerDisponibilidad(self, codigoRecurso, sede):
        """RQF-009: unidades disponibles de un recurso en una sede."""
        i, j = self._celda(codigoRecurso, sede)
        return self.matriz[i][j]

    def totalDisponible(self, codigoRecurso):
        j = self.columnaDeRecurso.buscar(codigoRecurso)
        if j is None:
            return 0
        return sum(fila[j] for fila in self.matriz)

    def disponibilidadPorSede(self, codigoRecurso):
        """[(sede, unidades)] de un recurso (columna de la matriz)."""
        j = self.columnaDeRecurso.buscar(codigoRecurso)
        if j is None:
            raise ValueError(f"El recurso {codigoRecurso} no está en el inventario")
        return [(self.sedes.obtener(i), self.matriz[i][j]) for i in range(len(self.sedes))]

    def sedesConUnidades(self, codigoRecurso):
        return [sede for sede, unidades in self.disponibilidadPorSede(codigoRecurso) if unidades > 0]

    # ---- cambios ----
    def fijarUnidades(self, codigoRecurso, sede, cantidad):
        """RQF-045: carga o corrige las unidades de un recurso en una sede."""
        cantidad = validarEntero(cantidad, "La cantidad de unidades", minimo=0)
        i, j = self._celda(codigoRecurso, sede)
        self.matriz[i][j] = cantidad

    def decrementar(self, codigoRecurso, sede):
        """Préstamo: resta una unidad. Devuelve False si no quedaban unidades."""
        i, j = self._celda(codigoRecurso, sede)
        if self.matriz[i][j] == 0:
            return False
        self.matriz[i][j] -= 1
        return True

    def incrementar(self, codigoRecurso, sede):
        """Devolución: suma una unidad."""
        i, j = self._celda(codigoRecurso, sede)
        self.matriz[i][j] += 1

    def trasladar(self, codigoRecurso, origen, destino, cantidad):
        """Mueve unidades entre sedes (lo usa la redistribución del M08)."""
        cantidad = validarEntero(cantidad, "La cantidad a trasladar", minimo=1)
        if origen == destino:
            raise ValueError("La sede de origen y la de destino son la misma")
        io, j = self._celda(codigoRecurso, origen)
        idest, _ = self._celda(codigoRecurso, destino)
        if self.matriz[io][j] < cantidad:
            raise ValueError(f"{origen} solo tiene {self.matriz[io][j]} unidad(es) de {codigoRecurso}")
        self.matriz[io][j] -= cantidad
        self.matriz[idest][j] += cantidad

    # ---- vistas ----
    def mostrarMatriz(self, codigos=None):
        """RQF-010 (sede × recurso): tabla de texto; 'codigos' limita las columnas."""
        columnas = codigos if codigos is not None else self.recursos.recorrer()
        ancho = max([16] + [len(s) + 2 for s in self.sedes])
        lineas = ["Sede \\ Recurso".ljust(ancho) + "".join(c.ljust(8) for c in columnas)]
        lineas.append("-" * len(lineas[0]))
        for i, sede in enumerate(self.sedes):
            celdas = "".join(str(self.matriz[i][self.columnaDeRecurso.buscar(c)]).ljust(8) for c in columnas)
            lineas.append(sede.ljust(ancho) + celdas)
        return "\n".join(lineas)

    def matrizSedeDia(self, codigoRecurso, prestamosActivos, dias=7, hoy=None):
        """RQF-010 (sede × día): unidades que habrá en cada sede cada día, sumando las
        que vuelven según la fecha límite de los préstamos activos del recurso.

        Devuelve (sedes, fechas, matriz) con matriz[sede][día]."""
        dias = validarEntero(dias, "Los días", minimo=1, maximo=60)
        hoy = ahoraSiFalta(hoy).date()
        fechas = [hoy + timedelta(days=d) for d in range(dias)]
        disponibles = self.disponibilidadPorSede(codigoRecurso)
        matriz = []
        for sede, unidades in disponibles:
            vencimientos = [p.fechaLimite().date() for p in prestamosActivos
                            if p.codigoRecurso == codigoRecurso and p.sede == sede]
            matriz.append([unidades + sum(1 for f in vencimientos if f <= dia) for dia in fechas])
        return [s for s, _ in disponibles], fechas, matriz

    def __str__(self):
        return f"GestorInventario({len(self.sedes)} sedes x {len(self.recursos)} recursos)"
