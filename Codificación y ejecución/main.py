"""Sistema de Gestión de Recursos Comunitarios Compartidos (Línea 1).

Al iniciar carga lo guardado en la carpeta datos/ (o los datos de demostración
la primera vez), avisa los préstamos que vencen pronto y abre el menú.
Al salir guarda todo en archivos de texto.

Variables de entorno opcionales:
- DATOS_PROYECTO: otra carpeta de datos (las pruebas usan una temporal).
- SIN_LIMPIAR=1: no borra la pantalla entre menús.
"""

import os
import sys

from interfaz.consola import Sesion, FinDeEntrada, titulo, pausa
from interfaz import menu_principal
from interfaz.menu_asistente import mostrarVencimientos
from persistencia import guardar, cargar, hayDatosGuardados
from persistencia.datos_demo import crearSistemaDemo

CARPETA_DATOS = os.environ.get("DATOS_PROYECTO") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "datos")
DIAS_AVISO = 2


def iniciarSistema(carpeta):
    if hayDatosGuardados(carpeta):
        try:
            return cargar(carpeta), f"Datos cargados desde {carpeta}"
        except ValueError as error:
            print(f"  No se pudieron cargar los datos guardados ({error}).")
    return crearSistemaDemo(), "Primera ejecución: se cargaron los datos de demostración"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # tildes en la consola de Windows
    sistema, origen = iniciarSistema(CARPETA_DATOS)
    sesion = Sesion(sistema, CARPETA_DATOS)
    print(f"\n  {origen}: {sistema.resumen()}")

    try:
        titulo(f"AVISO: préstamos que vencen en los próximos {DIAS_AVISO} días")
        mostrarVencimientos(sistema, DIAS_AVISO)
        pausa()
        menu_principal.ejecutar(sesion)
    except (FinDeEntrada, KeyboardInterrupt):
        print("\n\n  Entrada terminada.")
    finally:
        registros = guardar(sesion.sistema, CARPETA_DATOS)
        print(f"\n  Se guardaron {registros} registros en {CARPETA_DATOS}. ¡Hasta luego!\n")


if __name__ == "__main__":
    main()
