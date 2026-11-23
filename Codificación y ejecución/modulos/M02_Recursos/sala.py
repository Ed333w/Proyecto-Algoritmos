from .recurso import Recurso, texto, entero


class Sala(Recurso):
    TIPO = "Sala"
    CAMPOS = (
        ("capacidad", "Capacidad", entero("La capacidad", 1)),
        ("dotacion", "Dotación", texto("La dotación")),
    )
