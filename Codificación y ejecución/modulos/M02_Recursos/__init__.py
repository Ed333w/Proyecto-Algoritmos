from .constantes import VIGENTE, DADO_DE_BAJA, DISPONIBLE, SIN_UNIDADES

from .recurso import Recurso
from .libro import Libro
from .equipo import Equipo
from .sala import Sala
from .sede import Sede
from .gestor_recurso import GestorRecursos

TIPOS = (Libro, Equipo, Sala)
ESTADOS = (DISPONIBLE, "Prestado", SIN_UNIDADES, DADO_DE_BAJA)


def claseDeTipo(tipo):
    """Devuelve la clase del tipo de recurso indicado, sin distinguir mayúsculas."""
    if isinstance(tipo, type) and tipo in TIPOS:
        return tipo
    nombre = str(tipo).strip().lower()
    for clase in TIPOS:
        if nombre in (clase.__name__.lower(), clase.__name__.lower() + "s"):
            return clase
    raise ValueError(f"Tipo de recurso no válido: {tipo}")

__all__ = [
    'Recurso',
    'Libro',
    'Equipo',
    'Sala',
    'Sede',
    'GestorRecursos',
    'VIGENTE',
    'DADO_DE_BAJA',
    'DISPONIBLE',
    'SIN_UNIDADES',
    'TIPOS',
    'ESTADOS',
    'claseDeTipo',
]
