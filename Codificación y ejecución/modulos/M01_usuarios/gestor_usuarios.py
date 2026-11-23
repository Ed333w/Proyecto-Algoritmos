from estructuras import VectorDinamico, TablaHash, ConjuntoHash
from modulos.comun import GeneradorCodigos, validarTexto, validarEmail
from .usuario import Usuario, TIPOS_DOCUMENTO


class GestorUsuarios:

    def __init__(self):
        self.usuarios = VectorDinamico()
        self.indice = TablaHash()
        self.indiceEmail = TablaHash()
        self.indiceDocumento = TablaHash()
        self.activos = ConjuntoHash()
        self.codigos = GeneradorCodigos("U", 3)

    # ---- altas ----
    def _validarEmailLibre(self, email, codigoPropio=None):
        dueño = self.indiceEmail.buscar(email)
        if dueño is not None and dueño != codigoPropio:
            raise ValueError(f"El correo {email} ya está registrado por {dueño}")

    @staticmethod
    # devuelve (sigla, número) normalizados. CC, TI y CE solo llevan dígitos (5 a 12); el pasaporte admite letras y dígitos (5 a 12).
    def validarDocumento(tipo, numero):
        sigla = validarTexto(tipo, "El tipo de documento").upper()
        if not any(sigla == s for s, _ in TIPOS_DOCUMENTO):
            opciones = ", ".join(f"{s} ({n})" for s, n in TIPOS_DOCUMENTO)
            raise ValueError(f"Tipo de documento '{tipo}' no válido. Opciones: {opciones}")
        numero = validarTexto(str(numero), "El número de documento").replace(".", "").replace(" ", "").upper()
        valido = numero.isalnum() if sigla == "PA" else numero.isdigit()
        if not valido or not 5 <= len(numero) <= 12:
            detalle = "letras y números" if sigla == "PA" else "solo números"
            raise ValueError(f"El número de documento debe tener entre 5 y 12 caracteres ({detalle})")
        return sigla, numero

    @staticmethod
    def _claveDocumento(sigla, numero):
        return f"{sigla}|{numero}"

    def _indexar(self, usuario):
        clave = self._claveDocumento(usuario.tipoDocumento, usuario.numeroDocumento)
        if self.indiceDocumento.contiene(clave):
            raise ValueError(f"Ya hay un usuario con el documento {usuario.documento()}: "
                             f"{self.indiceDocumento.buscar(clave).codigo}")
        self.indiceDocumento.insertar(clave, usuario)
        self.usuarios.agregar(usuario)
        self.indice.insertar(usuario.codigo, usuario)
        self.indiceEmail.insertar(usuario.email, usuario.codigo)
        if usuario.esActivo():
            self.activos.agregar(usuario.codigo)

    # RQF-001: alta con código automático. Rechaza datos vacíos, correos repetidos y documentos ya registrados.
    def registrar(self, nombre, email, tipoDocumento, numeroDocumento):
        nombre = validarTexto(nombre, "El nombre")
        sigla, numero = self.validarDocumento(tipoDocumento, numeroDocumento)
        email = validarEmail(email)
        self._validarEmailLibre(email)
        usuario = Usuario(self.codigos.formatear(self.codigos.contador + 1), nombre, email, sigla, numero)
        self._indexar(usuario)          # rechaza el documento repetido antes de guardar nada
        self.codigos.siguiente()
        return usuario.codigo

    def cargarExistente(self, usuario):  # Persistencia: agrega un usuario ya creado conservando su código.
        if self.indice.contiene(usuario.codigo):
            raise ValueError(f"El usuario {usuario.codigo} está repetido en los datos")
        self.codigos.registrarExistente(usuario.codigo)
        self._indexar(usuario)

    # ---- consultas ----
    def buscarxCodigo(self, codigo):  # RQF-002 y RQF-019: O(1) promedio. Devuelve None si no existe.
        return self.indice.buscar(str(codigo).strip().upper())

    # RQF-002: consulta por tipo y número de documento, O(1) promedio. None si no existe.
    def buscarPorDocumento(self, tipoDocumento, numeroDocumento):
        sigla, numero = self.validarDocumento(tipoDocumento, numeroDocumento)
        return self.indiceDocumento.buscar(self._claveDocumento(sigla, numero))

    def obtenerPorDocumento(self, tipoDocumento, numeroDocumento):
        usuario = self.buscarPorDocumento(tipoDocumento, numeroDocumento)
        if usuario is None:
            raise ValueError(f"No hay ningún usuario con el documento {tipoDocumento.upper()} {numeroDocumento}")
        return usuario

    def obtener(self, codigo):
        usuario = self.buscarxCodigo(codigo)
        if usuario is None:
            raise ValueError(f"El usuario {codigo} no existe")
        return usuario

    def validarActivo(self, codigo):  # regla compartida por préstamos y turnos: el usuario existe y está activo.
        usuario = self.obtener(codigo)
        if not usuario.esActivo():
            raise ValueError(f"El usuario {usuario.codigo} está inactivo")
        return usuario

    def listarTodos(self):
        return self.usuarios.recorrer()

    def listarActivos(self):
        return [u for u in self.usuarios if self.activos.contiene(u.codigo)]

    def obtenerCantidad(self):
        return len(self.usuarios)

    def obtenerCantidadActivos(self):
        return len(self.activos)

    # ---- modificaciones ----
    # RQF-003: el nombre no cambia porque identifica al usuario en el historial. Rechaza correos repetidos.
    def actualizarEmail(self, codigo, nuevoEmail):
        usuario = self.obtener(codigo)
        email = validarEmail(nuevoEmail)
        self._validarEmailLibre(email, usuario.codigo)
        self.indiceEmail.eliminar(usuario.email)
        usuario.email = email
        self.indiceEmail.insertar(email, usuario.codigo)

    def darDeBaja(self, codigo):  # RQF-004: baja lógica; conserva el historial. Exige no tener préstamos activos.
        usuario = self.obtener(codigo)
        if not usuario.esActivo():
            raise ValueError(f"El usuario {usuario.codigo} ya está inactivo")
        if usuario.prestamosActivos > 0:
            raise ValueError(f"No se puede dar de baja a {usuario.codigo}: "
                             f"tiene {usuario.prestamosActivos} préstamo(s) activo(s)")
        usuario.darDeBaja()
        self.activos.eliminar(usuario.codigo)

    def reactivar(self, codigo):  # RQF-035: reactiva un usuario inactivo. Exige que no esté activo y que exista.
        usuario = self.obtener(codigo)
        if usuario.esActivo():
            raise ValueError(f"El usuario {usuario.codigo} ya está activo")
        usuario.reactivar()
        self.activos.agregar(usuario.codigo)

    def __str__(self):
        return f"GestorUsuarios(total={self.obtenerCantidad()}, activos={self.obtenerCantidadActivos()})"
