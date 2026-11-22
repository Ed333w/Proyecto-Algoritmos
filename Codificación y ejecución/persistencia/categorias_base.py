"""Categorías base del catálogo (se crean con M05, sin modificarlo).

Dos categorías principales:
- Espacios de estudio, con los tipos de sala.
- Material de estudio, con Equipos (Computadores y Laptops) y Libros.

Los datos de demostración y los datos de prueba las crean al empezar; cada uno
agrega debajo de Libros las subcategorías que necesite (profundidad arbitraria).
"""

# (código, nombre, código del padre)
CATEGORIAS_BASE = (
    ("C001", "Espacios de estudio", None),
    ("C002", "Sala de conferencias", "C001"),
    ("C003", "Sala de estudio grupal", "C001"),
    ("C004", "Sala de estudio individual", "C001"),
    ("C005", "Sala con televisor", "C001"),
    ("C006", "Sala de computo", "C001"),
    ("C007", "Auditorio", "C001"),
    ("C008", "Material de estudio", None),
    ("C009", "Equipos", "C008"),
    ("C010", "Computadores", "C009"),
    ("C011", "Laptops", "C009"),
    ("C012", "Libros", "C008"),
)
ESPACIOS, MATERIAL, EQUIPOS, COMPUTADORES, LAPTOPS, LIBROS = "C001", "C008", "C009", "C010", "C011", "C012"


def crearCategoriasBase(sistema):
    for codigo, nombre, padre in CATEGORIAS_BASE:
        sistema.categorias.registrarCategoria(codigo, nombre, padre)
