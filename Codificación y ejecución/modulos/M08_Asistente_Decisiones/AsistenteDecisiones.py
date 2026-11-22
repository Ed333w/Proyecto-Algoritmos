"""M08 · Asistente de decisiones del administrador (plus: RQF-046, 047, 048, 049 y 051).

El sistema lo usan solo los administradores, así que el asistente les ayuda a
decidir qué mover, qué comprar y qué atender primero. Todo se calcula con los
datos reales de los demás módulos (inventario, historial, filas y atrasos).

- RQF-046 Redistribución: algoritmo voraz con dos montículos de máximos
  (sedes con sobrante y sedes con faltante). Solo recursos operativos.
- RQF-047 Prioridad de compra: montículo de máximos por demanda insatisfecha.
  Un recurso dañado o en reparación con demanda aparece como "Reparar o reponer".
- RQF-048 Predicción: promedio de duración de los préstamos ya devueltos. Un
  recurso que no está operativo no se predice: se informa su condición.
- RQF-049 Alertas: cola de prioridad (montículo de máximos) por urgencia. Incluye
  los recursos dañados, en reparación demorada y sin uso.
- RQF-051 Vencimientos: montículo de mínimos por fecha límite; al abrir el
  programa también se resume cuántos recursos no están operativos.

Los recursos que no están operativos nunca se recomiendan (ni para mover ni para
comprar como si estuvieran sanos), pero tampoco se pierden de vista: el asistente
avisa de ellos para decidir qué reparar y qué retirar.
"""

from datetime import timedelta

from estructuras import Monticulo, TablaHash
from modulos.comun import validarEntero, ahoraSiFalta
from modulos.M07_Inventario import (OPERATIVO, DAÑADO, EN_REPARACION, SIN_USO, CONDICIONES_TEMPORALES,
                                    GestorCondiciones, validarOperativo)
from modulos.M03_Prestamos import DIAS_LIMITE

VENTANA_DIAS = 30           # "préstamos recientes" = últimos 30 días
PESO_FILA = 2               # una persona esperando pesa más que un préstamo ya atendido
MAX_MUESTRAS_CONFIANZA = 10
DIAS_REPARACION_DEMORADA = 15   # en reparación por más de esto -> alerta
COMPRAR, REPARAR = "Comprar más unidades", "Reparar o reponer"


class Traslado:
    __slots__ = ("codigoRecurso", "origen", "destino", "unidades")

    def __init__(self, codigoRecurso, origen, destino, unidades):
        self.codigoRecurso = codigoRecurso
        self.origen = origen
        self.destino = destino
        self.unidades = unidades

    def __str__(self):
        return f"Mover {self.unidades} de {self.codigoRecurso}: {self.origen} -> {self.destino}"

    __repr__ = __str__


class Alerta:
    __slots__ = ("urgencia", "tipo", "mensaje")

    def __init__(self, urgencia, tipo, mensaje):
        self.urgencia = urgencia
        self.tipo = tipo
        self.mensaje = mensaje

    def __str__(self):
        return f"[{self.tipo}] {self.mensaje}"

    __repr__ = __str__


ATRASO, SIN_UNIDADES, REINCIDENTE = "Atraso", "Sin unidades", "Usuario reincidente"
RECURSO_DAÑADO, REPARACION_DEMORADA, RECURSO_SIN_USO = (
    "Recurso dañado", "Reparación demorada", "Recurso sin uso")


def _desde(dias):
    return "desde hoy" if dias == 0 else f"hace {dias} día(s)"


class AsistenteDecisiones:

    def __init__(self, gestorUsuarios, gestorRecursos, gestorInventario, gestorPrestamos, gestorTurnos,
                 gestorCondiciones=None):
        self.usuarios = gestorUsuarios
        self.recursos = gestorRecursos
        self.inventario = gestorInventario
        self.prestamos = gestorPrestamos
        self.turnos = gestorTurnos
        self.condiciones = gestorCondiciones or GestorCondiciones(gestorRecursos, gestorPrestamos, gestorTurnos)

    # ---------- apoyo ----------
    def _prestamosRecientes(self, ahora, ventanaDias):
        """TablaHash 'recurso|sede' -> préstamos hechos en los últimos 'ventanaDias' días."""
        desde = ahora - timedelta(days=ventanaDias)
        conteo = TablaHash()
        for p in self.prestamos.listarTodos():
            if desde <= p.fechaPrestamo <= ahora:
                conteo.incrementar(f"{p.codigoRecurso}|{p.sede}")
        return conteo

    def _recursosAnalizar(self, codigoRecurso):
        """Solo los operativos: los demás nunca se recomiendan."""
        if codigoRecurso:
            return [validarOperativo(self.recursos, codigoRecurso)]
        return [r for r in self.recursos.listarTodos() if r.estaVigente()]

    def _demanda(self, recurso, recientes):
        """(personas en fila, préstamos recientes) del recurso en todas las sedes."""
        fila = self.turnos.cantidadEspera(recurso.codigo)
        usos = sum(recientes.buscar(f"{recurso.codigo}|{s}", 0) for s in self.recursos.nombresSedes())
        return fila, usos

    @staticmethod
    def _repartirProporcional(total, pesos):
        """Reparte 'total' unidades según 'pesos' (método del mayor residuo): suma exacta."""
        sumaPesos = sum(pesos)
        exactos = [total * p / sumaPesos for p in pesos]
        enteros = [int(x) for x in exactos]
        sobrantes = Monticulo(esMaximo=True)
        for i, x in enumerate(exactos):
            sobrantes.insertar(x - enteros[i], i)
        for _ in range(total - sum(enteros)):
            enteros[sobrantes.extraer()[1]] += 1
        return enteros

    # ---------- RQF-046 ----------
    def recomendarRedistribucion(self, codigoRecurso=None, ventanaDias=VENTANA_DIAS, ahora=None):
        """Propone traslados de sedes con sobrante a sedes con faltante (voraz)."""
        ahora = ahoraSiFalta(ahora)
        recientes = self._prestamosRecientes(ahora, ventanaDias)
        sedes = self.recursos.nombresSedes()
        traslados = []
        for recurso in self._recursosAnalizar(codigoRecurso):
            disponibles = [self.inventario.obtenerDisponibilidad(recurso.codigo, s) for s in sedes]
            total = sum(disponibles)
            demanda = [PESO_FILA * self.turnos.cantidadEspera(recurso.codigo, s)
                       + recientes.buscar(f"{recurso.codigo}|{s}", 0) for s in sedes]
            if total == 0 or sum(demanda) == 0:
                continue
            objetivo = self._repartirProporcional(total, demanda)
            donantes, receptores = Monticulo(esMaximo=True), Monticulo(esMaximo=True)
            for i, sede in enumerate(sedes):
                diferencia = disponibles[i] - objetivo[i]
                if diferencia > 0:
                    donantes.insertar(diferencia, sede)
                elif diferencia < 0:
                    receptores.insertar(-diferencia, sede)
            # Voraz: el que más le sobra le da al que más le falta, hasta cubrir
            while not donantes.estaVacio() and not receptores.estaVacio():
                sobra, origen = donantes.extraer()
                falta, destino = receptores.extraer()
                mover = min(sobra, falta)
                traslados.append(Traslado(recurso.codigo, origen, destino, mover))
                if sobra > mover:
                    donantes.insertar(sobra - mover, origen)
                if falta > mover:
                    receptores.insertar(falta - mover, destino)
        return traslados

    def aplicarTraslado(self, traslado):
        """Ejecuta el traslado y atiende la fila de la sede que recibe. Devuelve los préstamos asignados."""
        validarOperativo(self.recursos, traslado.codigoRecurso)
        self.inventario.trasladar(traslado.codigoRecurso, traslado.origen, traslado.destino, traslado.unidades)
        return self.prestamos.atenderFila(traslado.codigoRecurso, traslado.destino)

    # ---------- RQF-047 ----------
    def priorizarCompras(self, cantidad=5, ventanaDias=VENTANA_DIAS, ahora=None):
        """[(recurso, índice, personas en fila, préstamos recientes, unidades totales, acción)]
        de mayor a menor. Los operativos se proponen para comprar más unidades; los dañados
        o en reparación con demanda, para reparar o reponer (sus unidades no cuentan)."""
        cantidad = validarEntero(cantidad, "La cantidad", minimo=1)
        ahora = ahoraSiFalta(ahora)
        recientes = self._prestamosRecientes(ahora, ventanaDias)
        monticulo = Monticulo(esMaximo=True)
        for recurso in self.recursos.listarTodos():
            if recurso.estaVigente():
                accion = COMPRAR
                unidades = self.inventario.totalDisponible(recurso.codigo) + recurso.prestamosActivos
            elif recurso.estado in CONDICIONES_TEMPORALES:
                accion, unidades = REPARAR, 0
            else:
                continue                      # sin uso o dado de baja: no se recomienda
            fila, usos = self._demanda(recurso, recientes)
            indice = (PESO_FILA * fila + usos) / (unidades + 1)
            if indice > 0:
                monticulo.insertar(round(indice, 2), (recurso, fila, usos, unidades, accion))
        return [(r, indice, fila, usos, unidades, accion)
                for indice, (r, fila, usos, unidades, accion) in monticulo.extraerVarios(cantidad)]

    # ---------- RQF-048 ----------
    def predecirDisponibilidad(self, codigoRecurso, ahora=None):
        ahora = ahoraSiFalta(ahora)
        recurso = self.recursos.obtener(codigoRecurso)
        if not recurso.estaVigente():
            # No se recomienda ni se estima: no se presta hasta que vuelva a Operativo
            return {"recurso": recurso, "operativo": False, "condicion": recurso.estado,
                    "disponibleAhora": False, "sedesConUnidades": [], "muestras": 0,
                    "promedioDias": None, "confianza": 0.0, "dias": None,
                    "fechaEstimada": None, "sede": None}
        conUnidades = self.inventario.sedesConUnidades(recurso.codigo)
        duraciones = [p.duracionDias() for p in self.prestamos.historialRecurso(recurso.codigo)
                      if not p.estaActivo()]
        promedio = sum(duraciones) / len(duraciones) if duraciones else float(DIAS_LIMITE)
        resultado = {
            "recurso": recurso,
            "operativo": True,
            "condicion": OPERATIVO,
            "disponibleAhora": bool(conUnidades),
            "sedesConUnidades": conUnidades,
            "muestras": len(duraciones),
            "promedioDias": round(promedio, 1),
            "confianza": min(len(duraciones) / MAX_MUESTRAS_CONFIANZA, 1.0),
            "dias": 0 if conUnidades else None,
            "fechaEstimada": ahora if conUnidades else None,
            "sede": None,
        }
        if conUnidades:
            return resultado
        activos = [p for p in self.prestamos.listarActivos() if p.codigoRecurso == recurso.codigo]
        if not activos:
            return resultado     # sin unidades y sin préstamos: no se libera solo
        estimaciones = Monticulo()
        for p in activos:
            estimada = p.fechaPrestamo + timedelta(days=promedio)
            if estimada < ahora:                 # ya superó el promedio: se espera para su fecha límite
                estimada = max(ahora, p.fechaLimite())
            estimaciones.insertar(estimada, p)
        fecha, prestamo = estimaciones.extraer()
        resultado.update(dias=max(0, (fecha.date() - ahora.date()).days),
                         fechaEstimada=fecha, sede=prestamo.sede)
        return resultado

    # ---------- RQF-049 ----------
    def alertasPriorizadas(self, ahora=None, minimoAtrasos=2):
        """Alertas ordenadas de la más urgente a la menos urgente (cola de prioridad)."""
        ahora = ahoraSiFalta(ahora)
        cola = Monticulo(esMaximo=True)
        for p in self.prestamos.listarAtrasados(ahora):
            usuario = self.usuarios.obtener(p.codigoUsuario)
            dias = p.diasAtraso(ahora)
            cola.insertar(100 + dias, Alerta(100 + dias, ATRASO,
                          f"{p.codigo}: {usuario.nombre} ({usuario.email}) debe {p.codigoRecurso} "
                          f"en {p.sede} hace {dias} día(s)"))
        for recurso in self._recursosAnalizar(None):
            for sede in self.recursos.nombresSedes():
                espera = self.turnos.cantidadEspera(recurso.codigo, sede)
                if espera and self.inventario.obtenerDisponibilidad(recurso.codigo, sede) == 0:
                    cola.insertar(80 + espera, Alerta(80 + espera, SIN_UNIDADES,
                                  f"{recurso.codigo} {recurso.nombre}: sin unidades en {sede} "
                                  f"y {espera} persona(s) en fila"))
        self._alertasCondicion(cola, ahora)
        tardios = TablaHash()
        for p in self.prestamos.listarTodos():
            if p.fueTarde(ahora):
                tardios.incrementar(p.codigoUsuario)
        for codigo, veces in tardios.items():
            if veces >= minimoAtrasos:
                usuario = self.usuarios.obtener(codigo)
                cola.insertar(60 + veces, Alerta(60 + veces, REINCIDENTE,
                              f"{usuario.codigo} {usuario.nombre} se ha atrasado {veces} veces"))
        return [alerta for _, alerta in cola.extraerVarios()]

    def _alertasCondicion(self, cola, ahora, ventanaDias=VENTANA_DIAS):
        """Avisos de los recursos que no están operativos (parte del RQF-049).

        - Dañado con demanda (fila o préstamos recientes): 90 + demanda (hasta 99).
          Va justo debajo de los atrasos: hay gente que lo necesita y no se puede prestar.
        - Dañado sin demanda: 50.
        - En reparación por más de DIAS_REPARACION_DEMORADA días: 40 + días de más (hasta 49).
        - Sin uso: 20 (decidir si se retira o se pasa a otra sede).
        Los dados de baja ya están decididos y no generan alerta."""
        recientes = self._prestamosRecientes(ahora, ventanaDias)
        for recurso in self.condiciones.listarNoOperativos():
            dias = self.condiciones.diasEnCondicion(recurso.codigo, ahora)
            if recurso.estado == DAÑADO:
                fila, usos = self._demanda(recurso, recientes)
                demanda = PESO_FILA * fila + usos
                if demanda:
                    urgencia = 90 + min(demanda, 9)
                    detalle = (f"{recurso.codigo} {recurso.nombre}: dañado {_desde(dias)} con demanda "
                               f"({fila} en fila, {usos} préstamo(s) en {ventanaDias} días). Reparar o reponer")
                else:
                    urgencia = 50
                    detalle = f"{recurso.codigo} {recurso.nombre}: dañado {_desde(dias)}, sin demanda por ahora"
                cola.insertar(urgencia, Alerta(urgencia, RECURSO_DAÑADO, detalle))
            elif recurso.estado == EN_REPARACION and dias > DIAS_REPARACION_DEMORADA:
                urgencia = 40 + min(dias - DIAS_REPARACION_DEMORADA, 9)
                cola.insertar(urgencia, Alerta(urgencia, REPARACION_DEMORADA,
                              f"{recurso.codigo} {recurso.nombre}: lleva {dias} días en reparación"))
            elif recurso.estado == SIN_USO:
                cola.insertar(20, Alerta(20, RECURSO_SIN_USO,
                              f"{recurso.codigo} {recurso.nombre}: sin uso {_desde(dias)}; "
                              f"decidir si se retira o se pasa a otra sede"))

    # ---------- RQF-051 ----------
    def vencimientosProximos(self, dias=2, ahora=None):
        """[(préstamo, días restantes)] que vencen entre hoy y dentro de 'dias', del más próximo al más lejano."""
        dias = validarEntero(dias, "Los días de anticipación", minimo=0, maximo=30)
        ahora = ahoraSiFalta(ahora)
        monticulo = Monticulo()
        for p in self.prestamos.listarActivos():
            restantes = p.diasRestantes(ahora)
            if 0 <= restantes <= dias:
                monticulo.insertar(p.fechaLimite(), (p, restantes))
        return [dato for _, dato in monticulo.extraerVarios()]

    def resumenNoOperativos(self):
        """RQF-051 (aviso al abrir): [(condición, cantidad)] de los recursos que no están operativos
        (los dados de baja no se cuentan: ya están decididos)."""
        return [(c, n) for c, n in self.condiciones.resumen() if c in (DAÑADO, EN_REPARACION, SIN_USO)]
