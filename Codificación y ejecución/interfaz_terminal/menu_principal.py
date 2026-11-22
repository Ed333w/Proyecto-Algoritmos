"""Menú principal: reúne los submenús de cada módulo."""

from . import (menu_usuarios, menu_recursos, menu_prestamos, menu_turnos, menu_categorias,
               menu_informes, menu_inventario, menu_asistente, menu_red, menu_datos, menu_estructuras)
from .consola import ejecutarMenu

OPCIONES = (
    ("Usuarios (M01)", menu_usuarios.menu),
    ("Recursos y sedes (M02)", menu_recursos.menu),
    ("Préstamos y devoluciones (M03)", menu_prestamos.menu),
    ("Turnos y fila de espera (M04)", menu_turnos.menu),
    ("Categorías (M05)", menu_categorias.menu),
    ("Informes y listados (M06)", menu_informes.menu),
    ("Inventario por sede (M07)", menu_inventario.menu),
    ("Asistente de decisiones (M08)", menu_asistente.menu),
    ("Red de sedes (M09)", menu_red.menu),
    ("Guardar y cargar datos", menu_datos.menu),
    ("Demostración de estructuras", menu_estructuras.menu),
)


def ejecutar(sesion):
    ejecutarMenu("SISTEMA DE GESTIÓN DE RECURSOS COMUNITARIOS · Red de bibliotecas", OPCIONES, sesion,
                 textoSalir="Salir (guarda los datos)", esPrincipal=True)
