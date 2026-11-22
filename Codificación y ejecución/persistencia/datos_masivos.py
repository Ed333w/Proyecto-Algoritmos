"""Conjunto de datos de prueba con más de 500 registros (lineamiento del proyecto).

Se genera siempre igual (semilla fija). Para crear la carpeta datos_prueba/:

    python -m persistencia.datos_masivos

El menú "Datos" del programa la carga, y las pruebas de cuello de botella usan
crearSistemaMasivo() con volúmenes más grandes.
"""

import os
import random
import sys
from datetime import datetime, timedelta

from modulos import Sistema
from modulos.M03_Prestamos import SinUnidadesError

NOMBRES = ("Ana", "Luis", "Maria", "Carlos", "Sofia", "Juan", "Valentina", "Andres", "Camila",
           "Diego", "Laura", "Mateo", "Paula", "Santiago", "Daniela", "Felipe")
APELLIDOS = ("Garcia", "Rodriguez", "Martinez", "Lopez", "Gomez", "Perez", "Diaz", "Rojas",
             "Torres", "Ramirez", "Castro", "Vargas", "Moreno", "Ortiz")
TEMAS = ("Algebra", "Calculo", "Python", "Redes", "Bases de Datos", "Fisica", "Quimica",
         "Historia", "Economia", "Estadistica", "Biologia", "Literatura", "Arte", "Robotica")
SEDES = ("Centro", "Norte", "Sur", "Occidente", "Oriente", "Chapinero")


def crearSistemaMasivo(usuarios=300, recursos=200, prestamos=600, solicitudes=40, semilla=7, hoy=None):
    azar = random.Random(semilla)
    hoy = hoy or datetime.now()
    s = Sistema()

    for sede in SEDES:
        s.recursos.registrarSede(sede)
    for i in range(len(SEDES) - 2):                      # una cadena; Chapinero queda aislada
        s.red.conectar(SEDES[i], SEDES[i + 1])
    s.red.conectar("Centro", "Sur")

    raices = ("Ciencias", "Ingenieria", "Humanidades", "Artes", "Economia")
    numero = 0
    for raiz in raices:
        numero += 1
        codigoRaiz = f"C{numero:03d}"
        s.categorias.registrarCategoria(codigoRaiz, raiz)
        for j in range(5):
            numero += 1
            s.categorias.registrarCategoria(f"C{numero:03d}", f"{raiz} {j + 1}", codigoRaiz)
    codigosCategorias = s.categorias.indice.clavesInorden()

    for i in range(usuarios):
        nombre = f"{azar.choice(NOMBRES)} {azar.choice(APELLIDOS)}"
        s.usuarios.registrar(nombre, f"usuario{i + 1}@uni.edu", "CC" if i % 10 else "TI", str(1000000000 + i))

    for i in range(recursos):
        tema, categoria = azar.choice(TEMAS), azar.choice(codigosCategorias)
        tipo = i % 3
        if tipo == 0:
            codigo = s.recursos.registrarLibro(f"{tema} {i + 1}", f"Autor {i % 40}", f"978-{i:05d}",
                                               azar.randint(1980, 2024), categoria)
        elif tipo == 1:
            codigo = s.recursos.registrarEquipo(f"Equipo {tema} {i + 1}", "Portatil", f"M{i}", "Bodega", categoria)
        else:
            codigo = s.recursos.registrarSala(f"Sala {tema} {i + 1}", azar.randint(4, 40), "Tablero", categoria)
        for sede in azar.sample(SEDES, 3):
            s.inventario.fijarUnidades(codigo, sede, azar.randint(0, 4))

    codigosUsuarios = [u.codigo for u in s.usuarios.listarTodos()]
    codigosRecursos = [r.codigo for r in s.recursos.listarTodos()]
    hechos = 0
    while hechos < prestamos:
        usuario, recurso, sede = azar.choice(codigosUsuarios), azar.choice(codigosRecursos), azar.choice(SEDES)
        inicio = hoy - timedelta(days=azar.randint(0, 60), hours=azar.randint(0, 23))
        try:
            codigo = s.prestamos.registrarPrestamo(usuario, recurso, sede, fechaPrestamo=inicio)
        except SinUnidadesError:
            if solicitudes > 0 and not s.turnos.estaEnEspera(usuario, recurso, sede):
                s.turnos.solicitarTurno(usuario, recurso, sede)
                solicitudes -= 1
            continue
        hechos += 1
        if azar.random() < 0.7:
            devolucion = inicio + timedelta(days=azar.randint(1, 20))
            s.prestamos.registrarDevolucion(codigo, min(devolucion, hoy))
    s.prestamos.reiniciarDeshacer()
    return s


def contarRegistros(s):
    return (s.usuarios.obtenerCantidad() + s.recursos.obtenerCantidad() + s.prestamos.obtenerCantidad()
            + s.categorias.obtenerCantidad() + s.recursos.obtenerCantidadSedes() + len(s.turnos.listarSolicitudes()))


if __name__ == "__main__":
    from persistencia import guardar
    carpeta = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "datos_prueba")
    sistema = crearSistemaMasivo()
    guardar(sistema, carpeta)
    print(f"Datos de prueba en {os.path.abspath(carpeta)}: {contarRegistros(sistema)} registros "
          f"({sistema.resumen()})")
