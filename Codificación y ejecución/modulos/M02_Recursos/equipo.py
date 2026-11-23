from .recurso import Recurso, texto


class Equipo(Recurso):
    TIPO = "Equipo"
    CAMPOS = (
        ("tipoEquipo", "Tipo de equipo", texto("El tipo de equipo")),
        ("modelo", "Modelo", texto("El modelo")),
        ("ubicacion", "Ubicación", texto("La ubicación")),
    )
