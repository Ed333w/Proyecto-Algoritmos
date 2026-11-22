"""Utilidades compartidas por todos los módulos (una sola implementación de cada una)."""

from datetime import datetime

FORMATO_FECHA = "%Y-%m-%d %H:%M"


class GeneradorCodigos:
    """Genera códigos consecutivos con prefijo: U001, R0001, P0001..."""

    def __init__(self, prefijo, digitos):
        self.prefijo = prefijo
        self.digitos = digitos
        self.contador = 0

    def siguiente(self):
        self.contador += 1
        return self.formatear(self.contador)

    def formatear(self, numero):
        return f"{self.prefijo}{numero:0{self.digitos}d}"

    def numero(self, codigo):
        return int(str(codigo)[len(self.prefijo):])

    def registrarExistente(self, codigo):
        """Al cargar datos guardados, el contador sigue desde el código más alto."""
        self.contador = max(self.contador, self.numero(codigo))

    def retroceder(self, codigo):
        """Al deshacer el último alta, el código vuelve a quedar libre."""
        if self.numero(codigo) == self.contador:
            self.contador -= 1


def validarTexto(valor, campo):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} no puede estar vacío")
    return valor.strip()


def validarEmail(valor):
    email = validarTexto(valor, "El correo").lower()
    usuario, arroba, dominio = email.partition("@")
    if not arroba or not usuario or "." not in dominio or dominio.startswith(".") \
            or dominio.endswith(".") or " " in email:
        raise ValueError(f"El correo '{valor}' no tiene un formato válido")
    return email


def validarEntero(valor, campo, minimo=None, maximo=None):
    try:
        numero = int(str(valor).strip())
    except (TypeError, ValueError):
        raise ValueError(f"{campo} debe ser un número entero") from None
    if minimo is not None and numero < minimo:
        raise ValueError(f"{campo} debe ser mayor o igual a {minimo}")
    if maximo is not None and numero > maximo:
        raise ValueError(f"{campo} debe ser menor o igual a {maximo}")
    return numero


def fechaATexto(fecha):
    return fecha.strftime(FORMATO_FECHA) if fecha is not None else ""


def textoAFecha(texto):
    return datetime.strptime(texto, FORMATO_FECHA) if texto else None


def ahoraSiFalta(ahora):
    return ahora if ahora is not None else datetime.now()
