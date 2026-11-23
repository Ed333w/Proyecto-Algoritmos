from estructuras import TablaHash
from estructuras.Algoritmos import (mergeSort, quickSort, busquedaSecuencial,
                                    busquedaBinaria, busquedaBinariaRecursiva)
from modulos.comun import validarTexto, validarEntero

SIN_CATEGORIA = "Sin categoría"


def _nombre(recurso):
    return recurso.nombre.lower()


class GeneradorInformes:

    def __init__(self, gestorUsuarios, gestorRecursos, gestorPrestamos, gestorCategorias):
        self.usuarios = gestorUsuarios
        self.recursos = gestorRecursos
        self.prestamos = gestorPrestamos
        self.categorias = gestorCategorias

    # ---- RQF-043 ----
    def reporteUso(self, ahora=None):
        todos = self.prestamos.listarTodos()
        return {
            "Préstamos registrados": len(todos),
            "Préstamos activos": self.prestamos.obtenerCantidadActivos(),
            "Préstamos devueltos": sum(1 for p in todos if not p.estaActivo()),
            "Préstamos atrasados": len(self.prestamos.listarAtrasados(ahora)),
            "Usuarios activos": self.usuarios.obtenerCantidadActivos(),
            "Usuarios con préstamos": sum(1 for u in self.usuarios.listarTodos() if u.prestamosActivos),
        }

    # ---- RQF-034 ----
    def reporteInventario(self):  # Recursos por tipo y unidades disponibles por tipo(el detalle por sede esta en M07)
        filas = []
        for tipo in ("Libro", "Equipo", "Sala"):
            recursos = self.recursos.listarxTipo(tipo)
            vigentes = [r for r in recursos if r.estaVigente()]
            unidades = sum(self.recursos.inventario.totalDisponible(r.codigo) for r in vigentes)
            filas.append((tipo, len(recursos), len(vigentes), unidades))
        return filas

    # ---- RQF-021 y RQF-031 ----
    def masPrestados(self, cantidad=None):
        ordenados = mergeSort(self.recursos.listarTodos(),
                              clave=lambda r: r.cantidadPrestamos, reverso=True)
        return ordenados if cantidad is None else ordenados[:validarEntero(cantidad, "La cantidad", 1)]

    # ---- RQF-022 ----
    def porAntiguedad(self, masAntiguosPrimero=True):
        return quickSort(self.recursos.listarTodos(),
                         clave=lambda r: (r.fechaRegistro, r.codigo),
                         reverso=not masAntiguosPrimero)

    # ---- RQF-024 ----
    # Búsqueda binaria sobre el catálogo ordenado del BST. Devuelve los recursos con ese nombre (puede haber varios con el mismo nombre)
    def buscarPorNombre(self, nombre, recursiva=False):
        objetivo = validarTexto(nombre, "El nombre a buscar").lower()
        catalogo = self.recursos.catalogoOrdenado()
        buscar = busquedaBinariaRecursiva if recursiva else busquedaBinaria
        i = buscar(catalogo, objetivo, _nombre)
        if i == -1:
            return []
        encontrados = []
        while i < len(catalogo) and _nombre(catalogo[i]) == objetivo:
            encontrados.append(catalogo[i])
            i += 1
        return encontrados

    def buscarPorNombreSecuencial(self, nombre):  # Misma búsqueda pero secuencial sobre el vector sin ordenar (para comparar).
        objetivo = validarTexto(nombre, "El nombre a buscar").lower()
        vigentes = [r for r in self.recursos.listarTodos() if r.estaVigente()]
        i = busquedaSecuencial(vigentes, objetivo, clave=_nombre)
        return vigentes[i] if i != -1 else None

    # ---- RQF-032 ----
    # Préstamos devueltos a tiempo frente al total de préstamos ya vencidos o cerrados (los activos que aún están dentro del plazo no se cuentan).
    def tasaDevolucion(self, ahora=None):
        aTiempo = tarde = 0
        for p in self.prestamos.listarTodos():
            if p.estaActivo() and not p.estaAtrasado(ahora):
                continue
            if p.fueTarde(ahora):
                tarde += 1
            else:
                aTiempo += 1
        total = aTiempo + tarde
        return {"aTiempo": aTiempo, "tarde": tarde, "total": total,
                "porcentaje": round(100 * aTiempo / total, 1) if total else 0.0}

    # ---- RQF-033 ----
    def demandaPorCategoria(self, agruparEnPrincipal=False):  # [(nombre de categoría, préstamos)] de mayor a menor demanda.
        conteo = TablaHash()
        for p in self.prestamos.listarTodos():
            codigoCategoria = self.recursos.obtener(p.codigoRecurso).categoria
            if codigoCategoria is None:
                nombre = SIN_CATEGORIA
            elif agruparEnPrincipal:
                nombre = self.categorias.raizDe(codigoCategoria).ruta()
            else:
                nombre = self.categorias.obtener(codigoCategoria).ruta()
            conteo.incrementar(nombre)
        return mergeSort(list(conteo.items()), clave=lambda par: par[1], reverso=True)

    # ---- RQF-044 ----
    def usuariosPorNombre(self):
        return mergeSort(self.usuarios.listarTodos(), clave=lambda u: (u.nombre.lower(), u.codigo))

    def recursosPorNombre(self):  # El catálogo ya está ordenado: es el recorrido en orden del BST (RQF-052).
        return self.recursos.catalogoOrdenado()
