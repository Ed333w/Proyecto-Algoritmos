from estructuras import VectorDinamico, TablaHash, ConjuntoHash
from modulos.comun import GeneradorCodigos, validarTexto, validarEmail
from .usuario import Usuario

class GestorUsuarios:
    def __init__(self):
        self.usuarios = VectorDinamico()
        self.indice = TablaHash()
        self.indiceEmail = TablaHash()
        self.indiceDocumento = TablaHash()
        self.activos = ConjuntoHash()
        self.codigos = GeneradorCodigos("U", 3)

    #---- altas ----
    def _validarEmailLibre(self, email, codigoPropio=None):
        dueño = self.indiceEmail.buscar(email)
        if dueño is not None and dueño != codigoPropio:
            raise ValueError(f"El correo {email} ya está registrado por {dueño}")

    @staticmethod
    def validarDocumento(tipo, numero):         #devuelve (sigla, número) normalizados. CC, TI y CE solo llevan dígitos (5 a 12); el pasaporte admite letras y dígitos (5 a 12).
        sigla = validarTexto(tipo, "El tipo de documento").upper()
        if not any(sigla == s for s, _ in Usuario.TIPOS_DOCUMENTO):
            opciones = ", ".join(f"{s} ({n})" for s, n in Usuario.TIPOS_DOCUMENTO)
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
            raise ValueError(f"Ya hay un usuario con el documento {usuario.documento()}: {self.indiceDocumento.buscar(clave).codigo}")
        self.indiceDocumento.insertar(clave, usuario)
        self.usuarios.agregar(usuario)
        self.indice.insertar(usuario.codigo, usuario)
        self.indiceEmail.insertar(usuario.email, usuario.codigo)
        if usuario.esActivo():
            self.activos.agregar(usuario.codigo)

    def registrar(self, nombre, email, tipoDocumento, numeroDocumento):
        """RQF-001: alta con código automático. Rechaza datos vacíos, correos repetidos
        y documentos ya registrados."""
        nombre = validarTexto(nombre, "El nombre")
        sigla, numero = self.validarDocumento(tipoDocumento, numeroDocumento)
        email = validarEmail(email)
        self._validarEmailLibre(email)
        usuario = Usuario(self.codigos.formatear(self.codigos.contador + 1), nombre, email, sigla, numero)
        self._indexar(usuario)          # rechaza el documento repetido antes de guardar nada
        self.codigos.siguiente()
        return usuario.codigo

    def cargarExistente(self, usuario):
        """Persistencia: agrega un usuario ya creado conservando su código."""
        if self.indice.contiene(usuario.codigo):
            raise ValueError(f"El usuario {usuario.codigo} está repetido en los datos")
        self.codigos.registrarExistente(usuario.codigo)
        self._indexar(usuario)
        
        #generar un código único para el usuario
        self.contadorCodigos += 1
        codigo = f"U{self.contadorCodigos:03d}"  # Formato: U001, U002, etc.

        #crear un nuevo usuario
        usuario = Usuario(codigo, nombre, email)

        #almacenar el usuario en el vector dinámico
        self.usuarios.agregar(usuario)
        self.codigosUsados.add(codigo)
        self.indice.insertar(codigo, usuario)

        return codigo  # Devolver el código del usuario registrado

    def buscarUsuario(self, codigo):
        # Entrega 2: búsqueda en la tabla hash, O(1) promedio
        return self.indice.buscar(codigo)

    def buscarxCodigo(self, codigo):
        # Mismo nombre que en GestorRecursos (lo usan Préstamos y Turnos)
        return self.buscarUsuario(codigo)

    def buscarUsuarioLineal(self, codigo):
        # Versión de la Entrega 1 (recorre el vector, O(n)); se deja para comparar
        for usuario in self.usuarios.recorrer():
            if usuario.codigo == codigo:
                return usuario
        return None

    def actualizar(self, codigo, nuevoEmail):
        usuario = self.buscarUsuario(codigo)
        if usuario:
            usuario.email = nuevoEmail
            return True  # Actualización exitosa
        return False  # Usuario no encontrado

    def darDeBaja(self, codigo):
        usuario = self.buscarUsuario(codigo)
        if usuario:
            if usuario.cantidadPrestamos > 0:
                raise ValueError(f"No se puede dar de baja al usuario {codigo}: tiene {usuario.cantidadPrestamos} préstamos activos.")
            usuario.darDeBaja()
            return True  # Baja exitosa
        return False  # Usuario no encontrado

    def reactivar(self, codigo):
        usuario = self.buscarUsuario(codigo)
        if usuario and not usuario.esActivo():
            usuario.reactivar()
            return True  # Reactivación exitosa
        return False  # Usuario no encontrado o ya activo

    def listarTodos(self):
        return self.usuarios.recorrer()  # Devolver la lista de todos los usuarios

    def listarActivos(self):
        todos = self.usuarios.recorrer()
        return [u for u in todos if u.esActivo()]  # Devolver solo los usuarios activos

    def codigoExiste(self, codigo):
        return codigo in self.codigosUsados  

    def obtenerCantidad(self):
        return self.usuarios.obtenerTamaño()

    def obtenerCantidadActivos(self):
        return len(self.listarActivos())

    def limpiar(self):
        self.usuarios.limpiar()
        self.contadorCodigos = 0
        self.codigosUsados.clear()
        self.indice = TablaHash(211)

    def __str__(self):
        activos = self.obtenerCantidadActivos()
        total = self.obtenerCantidad()
        return f"GestorUsuarios(total={total}, activos={activos})"
           
    
