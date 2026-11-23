from datetime import datetime

from .recurso import Recurso, texto, entero


class Libro(Recurso):
    TIPO = "Libro"
    CAMPOS = (
        ("autor", "Autor", texto("El autor")),
        ("isbn", "ISBN", texto("El ISBN")),
        ("añoPublicacion", "Año de publicación", entero("El año", 1450, datetime.now().year)),
    )
