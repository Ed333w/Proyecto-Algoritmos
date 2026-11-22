# Pruebas

Ejecutar: `python -m pytest` (desde esta carpeta). Cada RQF y cada estructura tiene un caso **exitoso**, uno de **borde** y uno de **cuello de botella**. Lo obtenido sale de la ejecución real (`tests/reporte/resultados_pruebas.json`).

Última ejecución: 2026-11-22 18:14, Python 3.13.18: **200 de 200 aprobadas**.

| Grupo | Casos | Exitoso | Borde | Cuello de botella | Aprobados |
|---|---|---|---|---|---|
| Estructuras de datos | 39 | 13 | 13 | 13 | 39 |
| Interfaz de consola | 3 | 1 | 1 | 1 | 3 |
| M01 · Usuarios | 18 | 6 | 6 | 6 | 18 |
| M02 · Recursos y sedes | 21 | 7 | 7 | 7 | 21 |
| M03 · Préstamos | 27 | 9 | 9 | 9 | 27 |
| M04 · Turnos | 15 | 5 | 5 | 5 | 15 |
| M05 · Categorías | 9 | 3 | 3 | 3 | 9 |
| M06 · Informes | 27 | 9 | 9 | 9 | 27 |
| M07 · Inventario | 12 | 4 | 4 | 4 | 12 |
| M08 · Asistente de decisiones | 15 | 5 | 5 | 5 | 15 |
| M09 · Red de sedes | 9 | 3 | 3 | 3 | 9 |
| Persistencia (RQF-050) | 5 | 1 | 2 | 2 | 5 |

## Estructuras de datos

| RQF | Tipo | Caso | Esperado | Obtenido | Resultado |
|---|---|---|---|---|---|
| Vector dinámico | Exitoso | Agregar 3 elementos con capacidad inicial 2 | Conserva el orden y duplica la capacidad a 4 | ['A', 'B', 'C'], capacidad 4 | ✓ |
| Vector dinámico | Borde | Leer y borrar en un vector vacío; capacidad 0 | obtener devuelve None, eliminar devuelve False y capacidad 0 se rechaza | obtener(0)=None, eliminarxIndice(0)=False, eliminarUltimo()=None, VectorDinamico(0) -> ValueError | ✓ |
| Vector dinámico | Cuello de botella | Agregar 20.000 elementos desde capacidad 1 | Todos quedan en orden; agregar es O(1) amortizado | 20.000 elementos, capacidad 32.768, 0,002 s | ✓ |
| Lista simple | Exitoso | Agregar al final y al inicio y eliminar uno del medio | Orden [0, 1, 3] y tamaño 3 | [0, 1, 3] tamaño 3 | ✓ |
| Lista simple | Borde | Eliminar el único elemento y después agregar al final | La cola se actualiza: queda [9]; eliminar en vacía devuelve None | eliminarInicio en vacía=None, luego [9] | ✓ |
| Lista simple | Cuello de botella | Agregar 20.000 al final y buscar el último | agregarAlFinal es O(1) gracias a la referencia a la cola | 20.000 nodos, último=19999, 0,004 s | ✓ |
| Lista doble | Exitoso | Recorrer hacia adelante y hacia atrás | [1, 2, 3] y [3, 2, 1] | [1, 2, 3] y [3, 2, 1] | ✓ |
| Lista doble | Borde | Eliminar el final de una lista de un elemento y de una vacía | Queda vacía con cabeza y cola en None; la segunda vez devuelve None | x, None, cabeza=None, cola=None | ✓ |
| Lista doble | Cuello de botella | Recorrer 20.000 nodos en ambos sentidos con filtro | Ambos recorridos devuelven los mismos pares, en orden inverso | 10.000 pares en cada sentido, 0,002 s | ✓ |
| Pila | Exitoso | push de A, B, C y pop | Sale C (último en entrar) y el tope queda en B | pop=C, peek=B | ✓ |
| Pila | Borde | pop y peek en pila vacía | Devuelven None sin error | pop=None, peek=None, vacía=True | ✓ |
| Pila | Cuello de botella | 20.000 push y 20.000 pop | Salen en orden inverso exacto | primero en salir 19999, último 0, 0,004 s | ✓ |
| Cola FIFO circular | Exitoso | Encolar 3 y desencolar | Sale el primero que entró | sale U1, frente U2 | ✓ |
| Cola FIFO circular | Borde | Dar la vuelta al arreglo, crecer y quitar del medio | Conserva el orden FIFO tras la vuelta, el crecimiento y eliminarSi | [0, 2, 4, 5], quitados=1, desencolar en vacía=None | ✓ |
| Cola FIFO circular | Cuello de botella | 20.000 encolar/desencolar intercalados | Todos salen en orden de llegada | 20.000 elementos en orden, 0,006 s | ✓ |
| Tabla hash (djb2) | Exitoso | Insertar, actualizar, buscar y eliminar | La actualización no duplica la clave; buscar tras eliminar da None | buscar U001=Ana María, era nueva=False, U002=None, tamaño=1 | ✓ |
| Tabla hash (djb2) | Borde | Tabla de capacidad 2 que debe crecer; eliminar inexistente | Crece a un tamaño primo y no pierde claves; eliminar inexistente devuelve False | capacidad 23, factor 0,43, eliminar(99)=False | ✓ |
| Tabla hash (djb2) | Cuello de botella | 2,000 códigos R0001.. en 211 cubetas: djb2 frente a la suma ASCII de la Entrega 1 | djb2 reparte mejor: menos comparaciones promedio por búsqueda | djb2: 211 cubetas, cadena máx 18, 6,393 comp.; ASCII: 29 cubetas, cadena máx 150, 55,499 comp. | ✓ |
| Conjunto hash | Exitoso | Agregar elementos distintos y consultar | Contiene los agregados | elementos=['U001', 'U002'] | ✓ |
| Conjunto hash | Borde | Agregar un repetido y eliminar uno que no está | El repetido no se agrega (False) y eliminar devuelve False | agregar repetido=False, eliminar inexistente=False, tamaño=1 | ✓ |
| Conjunto hash | Cuello de botella | 20.000 inserciones con la mitad repetidas | Quedan 10.000 elementos únicos | 10.000 únicos, 0,020 s | ✓ |
| Árbol binario de búsqueda | Exitoso | Insertar C05 C02 C08 C01 C03 y recorrer en orden | Inorden ordenado y búsqueda por clave | inorden=['C01', 'C02', 'C03', 'C05', 'C08'], buscar C03=c03, altura=3 | ✓ |
| Árbol binario de búsqueda | Borde | Eliminar la raíz con dos hijos, una hoja y una clave inexistente | Sigue ordenado; eliminar inexistente devuelve False | eliminar 50, 20, 99 -> (True, True, False); inorden=[30, 40, 60, 70, 80] | ✓ |
| Árbol binario de búsqueda | Cuello de botella | Insertar 3.000 claves ya ordenadas (peor caso) | El árbol degenera en una lista (altura n) pero no desborda la pila | altura 3.000, 1,572 s | ✓ |
| Árbol AVL | Exitoso | Insertar 1, 2, 3 (caso RR) | Una rotación: la raíz pasa a ser 2 | raíz=2, altura=2, rotaciones=1 | ✓ |
| Árbol AVL | Borde | Casos dobles LR y RL y eliminación que desbalancea | Después de cada operación sigue balanceado | raíz tras LR=20, inorden=[30, 40, 45, 50, 60], balanceado=True | ✓ |
| Árbol AVL | Cuello de botella | Insertar 20.000 claves en orden y borrar la mitad al azar | Altura cerca de log2(n) (≈ 15) y balanceado | altura 15 con 10.000 nodos, 21.700 rotaciones, 0,206 s | ✓ |
| Montículo | Exitoso | Montículo de máximos con prioridades 3, 9, 1, 7 | Salen 9, 7, 3, 1 | [9, 7, 3, 1] | ✓ |
| Montículo | Borde | Extraer de vacío y prioridades empatadas | None en vacío; con empate sale primero el que entró primero | extraer vacío=None, empates=['a', 'b', 'c'] | ✓ |
| Montículo | Cuello de botella | 20.000 prioridades al azar y extraer todas | Salen ordenadas; insertar y extraer O(log n) | 20.000 en orden, 0,181 s | ✓ |
| Grafo (lista de adyacencia) | Exitoso | BFS, ruta más corta y caminos con backtracking de A a C | Ruta de 2 tramos y dos caminos posibles | ruta=['A', 'B', 'C'], caminos=[['A', 'B', 'C'], ['A', 'D', 'C']] | ✓ |
| Grafo (lista de adyacencia) | Borde | Ruta entre componentes distintas, arista repetida, bucle y vértice inexistente | Ruta vacía, False, ValueError y ValueError | ruta A-E=[], arista repetida=False, componentes=[['A', 'B', 'C', 'D'], ['E', 'F']] | ✓ |
| Grafo (lista de adyacencia) | Cuello de botella | Cadena de 2.000 vértices: BFS de extremo a extremo | Ruta de 1.999 tramos en tiempo O(V + E) | 1.999 tramos, 0,007 s | ✓ |
| Ordenamientos | Exitoso | Ordenar [5, 3, 8, 1, 9, 2] con inserción, merge sort y quick sort | Los tres dan [1, 2, 3, 5, 8, 9] y no modifican la lista original | [1, 2, 3, 5, 8, 9] (los tres iguales: True) | ✓ |
| Ordenamientos | Borde | Lista vacía, un elemento y estabilidad con claves iguales | Vacía y unitaria sin error; inserción y merge sort conservan el orden de los empates | vacía=[], uno=[7], estable=[('c', 0), ('b', 1), ('a', 1)] | ✓ |
| Ordenamientos | Cuello de botella | Ordenar 5.000 números al azar con los tres algoritmos | Inserción O(n²) es mucho más lenta que merge sort y quick sort O(n log n) | insercion: 0,488 s, mergeSort: 0,009 s, quickSort: 0,006 s | ✓ |
| Búsquedas | Exitoso | Buscar 7 en [1, 3, 5, 7, 9] | Las tres búsquedas devuelven el índice 3 | (3, 3, 3) | ✓ |
| Búsquedas | Borde | Lista vacía, valor ausente y valor repetido | -1, -1 y la primera posición del repetido | (-1, -1, 1, 1) | ✓ |
| Búsquedas | Cuello de botella | 1,000 búsquedas en 200.000 elementos ordenados | Binaria O(log n) muy por debajo de la secuencial O(n) | binaria: 0,0025 s; secuencial (estimada para 1,000): 3,05 s | ✓ |

## Interfaz de consola

| RQF | Tipo | Caso | Esperado | Obtenido | Resultado |
|---|---|---|---|---|---|
| Interfaz (menú) | Exitoso | Recorrer las 68 opciones (69 pasos) de los 11 menús con datos válidos, consultando usuarios por documento y recursos por tipo y nombre desde la lista, y cambiando la condición de recursos desde Inventario | Ninguna opción falla; al salir se guardan los datos | código de salida 0; errores mostrados 0; datos guardados=True | ✓ |
| Interfaz (menú) | Borde | Opciones inexistentes, datos inválidos y fin de la entrada sin salir | Muestra 'Opción inválida' o el error y sigue; al cortarse la entrada guarda y termina sin Traceback | 2 opciones inválidas y 4 errores mostrados; código 0; guardó=True | ✓ |
| Interfaz (menú) | Cuello de botella | Abrir el programa con los datos de prueba (más de 1,000 registros) y pedir listados, informes y alertas | Carga, responde y guarda sin errores | Datos cargados desde <carpeta de datos>: 300 usuarios, 200 recursos, 6 sedes, 26 categorías, 600 préstamos, 39 en espera; código 0; 0,06 s | ✓ |

## M01 · Usuarios

| RQF | Tipo | Caso | Esperado | Obtenido | Resultado |
|---|---|---|---|---|---|
| RQF-001 | Exitoso | Registrar 'Ana Garcia' con cédula 1,020,304,050 y correo válido | Código U001, estado Activo, documento CC 1020304050 y correo en minúsculas | U001, Activo, CC 1020304050, ana@uni.edu | ✓ |
| RQF-001 | Borde | Nombre de 1 letra y pasaporte con letras; luego nombre vacío, correo sin @, correo repetido, documento repetido, tipo de documento inválido y cédula con letras | Acepta los dos primeros y rechaza los otros seis con un mensaje claro, sin gastar códigos | El nombre no puede estar vacío; El correo 'beto.uni.edu' no tiene un formato válido; El correo a@uni.edu ya está registrado por U001; Ya hay un usuario con el documento CC 12345: U001; Tipo de documento 'XX' no válido. Opciones: CC (Cédula de ciudadanía), TI (Tarjeta de identidad), CE (Cédula de extranjería), PA (Pasaporte); El número de documento debe tener entre 5 y 12 caracteres (solo números); siguiente código U003 | ✓ |
| RQF-001 | Cuello de botella | Registrar 5.000 usuarios seguidos | Códigos consecutivos hasta U5000 sin repetidos | 5.000 usuarios, último U5000, 0,070 s | ✓ |
| RQF-002 | Exitoso | Consultar a Luis Perez por su código U003 y por su documento TI 1098765432 | Las dos consultas devuelven el mismo usuario con sus datos y 2 préstamos activos | U003, Luis Perez, TI 1098765432, Activo, 2 activos; misma persona=True | ✓ |
| RQF-002 | Borde | Código ' u003 ' (minúscula y espacios), código U999, documento que no existe, mismo número con otro tipo y tipo inválido | Encuentra U003; los otros cuatro informan el motivo | U003; El usuario U999 no existe; No hay ningún usuario con el documento CC 99999999; No hay ningún usuario con el documento CC 1098765432; Tipo de documento 'RC' no válido. Opciones: CC (Cédula de ciudadanía), TI (Tarjeta de identidad), CE (Cédula de extranjería), PA (Pasaporte) | ✓ |
| RQF-002 | Cuello de botella | 10,000 consultas por código y 10,000 por documento sobre 3,000 usuarios | Todas encuentran al usuario; tiempo casi constante por consulta (tablas hash) | 10.000 por código y 10.000 por documento en 0,023 s (1,2 µs c/u) | ✓ |
| RQF-003 | Exitoso | Cambiar el correo de U001 a carlos.lopez@uni.edu | El correo cambia y el anterior queda libre para otro usuario | U001 -> carlos.lopez@uni.edu; el correo viejo lo tomó U006 | ✓ |
| RQF-003 | Borde | Correo vacío, correo de otro usuario y el mismo correo actual | Rechaza los dos primeros; aceptar el propio correo no da error | El correo no puede estar vacío; El correo ana@uni.edu ya está registrado por U002; mismo correo aceptado | ✓ |
| RQF-003 | Cuello de botella | Actualizar el correo de 3.000 usuarios | Todos actualizados y el índice de correos sigue sin repetidos | 3.000 correos en el índice, 0,019 s | ✓ |
| RQF-004 | Exitoso | Dar de baja a U002 (sin préstamos activos) | Queda Inactivo, sale del conjunto de activos y su historial se conserva | estado Inactivo, en activos=False, historial 2 préstamos | ✓ |
| RQF-004 | Borde | Dar de baja a U003 (tiene préstamos activos) y a un usuario ya inactivo | Rechaza ambos y explica el motivo | No se puede dar de baja a U003: tiene 2 préstamo(s) activo(s); El usuario U002 ya está inactivo | ✓ |
| RQF-004 | Cuello de botella | Dar de baja a la mitad de 3.000 usuarios | El conjunto de activos queda con la otra mitad | activos 1.500 de 3.000, 0,002 s | ✓ |
| RQF-019 | Exitoso | Buscar U005 en la tabla hash | Devuelve a Pedro Diaz | U005: Pedro Diaz (PA AB123456) <pedro@uni.edu> [Activo] | ✓ |
| RQF-019 | Borde | Buscar en un gestor vacío y un código con formato raro | Devuelve None sin error | U001=None, '###'=None | ✓ |
| RQF-019 | Cuello de botella | Comparar tabla hash vs. búsqueda secuencial (3,000 usuarios, 500 búsquedas) | La tabla hash es al menos 20 veces más rápida | hash 0,28 ms vs. secuencial 47,7 ms (168 veces) | ✓ |
| RQF-035 | Exitoso | Dar de baja y reactivar a U002 | Vuelve a Activo y puede pedir préstamos | estado Activo, préstamo P0012 | ✓ |
| RQF-035 | Borde | Reactivar a un usuario que ya está activo y a uno que no existe | Rechaza ambos | El usuario U001 ya está activo; El usuario U777 no existe | ✓ |
| RQF-035 | Cuello de botella | Dar de baja y reactivar 3.000 usuarios | Todos quedan activos de nuevo | activos 3.000, 0,009 s | ✓ |

## M02 · Recursos y sedes

| RQF | Tipo | Caso | Esperado | Obtenido | Resultado |
|---|---|---|---|---|---|
| RQF-005 | Exitoso | Registrar un libro, un equipo y una sala con categoría | Cada uno es de su clase, hereda de Recurso y queda con su categoría y una columna en el inventario | R0013 Libro cat. C001, R0014 Equipo cat. C002, R0015 Sala cat. C003 | ✓ |
| RQF-005 | Borde | Año fuera de rango, capacidad 0, tipo inválido, categoría inexistente y clase abstracta | Rechaza todos y no consume códigos | El año debe ser menor o igual a 2026; La capacidad debe ser mayor o igual a 1; Tipo de recurso 'Revista' no válido (use Libro, Equipo o Sala); La categoría C999 no existe; siguiente código válido R0013 | ✓ |
| RQF-005 | Cuello de botella | Registrar 3.000 recursos mezclando los tres tipos | Todos registrados con código único; la matriz de inventario crece sola | 3.000 recursos, columnas de la matriz 3.200, 0,047 s | ✓ |
| RQF-006 | Exitoso | Consultar R0004 por código y buscarlo como Libro con 'estructuras' | Las dos dan el libro de Cormen; 2 unidades en Centro y 0 en Norte (prestado) | Estructuras de Datos de Cormen; búsqueda [R0004: Estructuras de Datos (Libro)]; [('Centro', 2), ('Norte', 0), ('Sur', 0), ('Occidente', 0)] | ✓ |
| RQF-006 | Borde | Código inexistente, recurso dado de baja, solo tipo, solo parte del nombre, tipo inválido y búsqueda vacía | Errores claros; el de baja se muestra con su estado; solo tipo lista los equipos; 'py' encuentra 'Python 101' | El recurso R9999 no existe; Tipo de recurso 'Revista' no válido (use Libro, Equipo o Sala); Indique el tipo, parte del nombre o ambos; de baja: [R0006: Fisica Universitaria (Libro)] -> Dado de baja; equipos ['R0010', 'R0012', 'R0011', 'R0005', 'R0002']; 'PY' -> ['R0001'] | ✓ |
| RQF-006 | Cuello de botella | Consultar los 1,500 recursos por código con su disponibilidad y hacer 100 búsquedas por tipo y nombre | Todos responden; cada búsqueda trae solo recursos del tipo y nombre pedidos | 1.500 consultas y 2.362 resultados de búsqueda, correctos=True, 0,025 s | ✓ |
| RQF-007 | Exitoso | Cambiar autor, nombre y categoría de R0001 | Cambian los datos y el catálogo ordenado usa el nombre nuevo | Aprende Python, G. van Rossum, C004; primero del catálogo: Aprende Python | ✓ |
| RQF-007 | Borde | Campo que no es del tipo, valor inválido y recurso de baja | Rechaza los tres y no cambia nada | El campo 'capacidad' no existe para un libro; La capacidad debe ser mayor o igual a 1; El recurso R0006 está dado de baja | ✓ |
| RQF-007 | Cuello de botella | Renombrar 2.000 libros (cada cambio reubica el nodo en el BST) | El catálogo sigue ordenado y con los mismos elementos | 2.000 en el catálogo, ordenado=True, 0,741 s | ✓ |
| RQF-020 | Exitoso | Buscar R0003 | Devuelve la Sala de Estudio | R0003: Sala de Estudio (Sala) | ✓ |
| RQF-020 | Borde | Buscar en un sistema sin recursos y con minúsculas | None sin error | R0001=None, r0001=None | ✓ |
| RQF-020 | Cuello de botella | 500 búsquedas: tabla hash vs. secuencial sobre 1,500 recursos | La tabla hash es al menos 10 veces más rápida | hash 0,32 ms vs. secuencial 27,1 ms | ✓ |
| RQF-023 | Exitoso | Listar la categoría Libros (con subcategorías) y los recursos Prestados y Dañados | Libros: 3 recursos por nombre; Prestado: la Sala de Estudio; Dañado: la Laptop Lenovo | Libros=['R0004', 'R0006', 'R0001']; Prestado=['R0003']; Dañado=['R0011'] | ✓ |
| RQF-023 | Borde | Categoría sin recursos, sin subcategorías, estado inválido y categoría inexistente | Lista vacía, solo los directos y errores claros | C004=[]; C009 directos=['R0002']; sin unidades=['R0006']; Estado 'roto' no válido. Opciones: Disponible, Prestado, Sin unidades, Dado de baja; La categoría C999 no existe | ✓ |
| RQF-023 | Cuello de botella | Listar por cada categoría principal y por estado Disponible (1,500 recursos) | Cada listado sale ordenado por nombre | 1.500 por categoría, 1.445 disponibles, ordenados=True, 0,088 s | ✓ |
| RQF-042 | Exitoso | Registrar la sede 'Oriente' | Aparece en la lista con código S05 y tiene su fila en la matriz | S05: Oriente; sedes=['Centro', 'Norte', 'Sur', 'Occidente', 'Oriente']; filas de la matriz=5 | ✓ |
| RQF-042 | Borde | Registrar 'centro' (ya existe con otra mayúscula) y un nombre vacío | Rechaza ambos; validarSede('centro') devuelve 'Centro' | La sede 'centro' ya existe; El nombre de la sede no puede estar vacío; validarSede('centro')=Centro | ✓ |
| RQF-042 | Cuello de botella | Registrar 300 sedes con 200 recursos ya creados | Matriz de 300 × 200 con todas las celdas en 0 | 300 sedes, 300 filas, 0,002 s | ✓ |
| RQF-052 | Exitoso | Recorrer en orden el catálogo de la demo | Recursos vigentes en orden alfabético | ['Auditorio Central', 'Computador Lab 1', 'Estructuras de Datos', 'Fisica Universitaria', 'Portatil Dell', 'Proyector 1', 'Python 101', 'Sala de Conferencias 301', 'Sala de Estudio', 'Sala TV 2'] | ✓ |
| RQF-052 | Borde | Dos recursos con el mismo nombre y uno dado de baja | Ambos homónimos quedan (la clave incluye el código) y el de baja sale | [('Auditorio Central', 'R0009'), ('Computador Lab 1', 'R0010'), ('Estructuras de Datos', 'R0004'), ('Portatil Dell', 'R0005'), ('Proyector 1', 'R0002'), ('Python 101', 'R0001'), ('Python 101', 'R0013'), ('Sala de Conferencias 301', 'R0007'), ('Sala de Estudio', 'R0003'), ('Sala TV 2', 'R0008')] | ✓ |
| RQF-052 | Cuello de botella | 5.000 recursos con nombres en orden al azar | El recorrido en orden sale ordenado; altura muy por debajo de n | altura 30 con 5.000 nodos, 0,078 s | ✓ |

## M03 · Préstamos

| RQF | Tipo | Caso | Esperado | Obtenido | Resultado |
|---|---|---|---|---|---|
| RQF-011 | Exitoso | U001 pide R0001 en Centro (2 unidades) | Préstamo P0001 con plazo de 14 días; queda 1 unidad | P0001, sede Centro, vence en 14 días, quedan 1 | ✓ |
| RQF-011 | Borde | Pedir la última unidad, luego una más; usuario inactivo; sede inexistente; plazo 0 | La última se presta; después SinUnidadesError; los otros casos se rechazan | No hay unidades de R0001 en Centro; El usuario U003 está inactivo; La sede 'Marte' no existe; El plazo en días debe ser mayor o igual a 1 | ✓ |
| RQF-011 | Cuello de botella | Registrar 5.000 préstamos de un recurso con 5.000 unidades | Todos se registran y el inventario llega a 0 | 5.000 préstamos, unidades 0, 0,037 s | ✓ |
| RQF-012 | Exitoso | Devolver P0008 (U003 tenía R0004 en Centro) | Queda Devuelto con fecha, vuelve 1 unidad a Centro y U003 baja a 1 préstamo activo | Devuelto el 2026-11-22; unidades 2 -> 3; asignados [] | ✓ |
| RQF-012 | Borde | Devolver dos veces, un código inexistente y la sala con fila de espera | Los dos primeros fallan; la sala pasa sola al primero de la fila (U002) | El préstamo P0010 ya fue devuelto; El préstamo P9999 no existe; la sala quedó a U002 (P0012) | ✓ |
| RQF-012 | Cuello de botella | Devolver todos los préstamos activos de un sistema con 6,000 préstamos | No queda ningún activo y la fila de espera se atiende al volver las unidades | 1.805 devoluciones iniciales, activos al final 0, en espera 298, 0,013 s | ✓ |
| RQF-013 | Exitoso | Historial de U003 en ambos sentidos y sus activos | 3 préstamos; el recorrido hacia atrás es el inverso; 2 activos | adelante ['P0004', 'P0008', 'P0009'], atrás ['P0009', 'P0008', 'P0004'], activos ['P0008', 'P0009'] | ✓ |
| RQF-013 | Borde | Usuario recién creado sin préstamos y usuario inexistente | Historial vacío; el inexistente da error | U006: []; El usuario U999 no existe | ✓ |
| RQF-013 | Cuello de botella | Historial de 100 usuarios sobre 6,000 préstamos | Cada historial recorre la lista doble una vez (O(n)) | 200 préstamos encontrados, 0,034 s | ✓ |
| RQF-014 | Exitoso | Historial de R0001 | 4 préstamos: P0002, P0004, P0006 y P0007 | ['P0002', 'P0004', 'P0006', 'P0007'] | ✓ |
| RQF-014 | Borde | Recurso sin préstamos (R0006) y código inexistente | Lista vacía y error | R0006: []; El recurso R0099 no existe | ✓ |
| RQF-014 | Cuello de botella | Historial de los 100 recursos más prestados (6,000 préstamos) | La suma coincide con el contador de préstamos de cada recurso | coinciden=True, 0,031 s | ✓ |
| RQF-015 | Exitoso | Prestar y deshacer; devolver y deshacer | Cada deshacer deja inventario, usuario e historial como estaban | Se deshizo el préstamo P0001 -> (préstamos, unidades)=(0, 2); Se deshizo la devolución P0001 -> Activo, unidades 1 | ✓ |
| RQF-015 | Borde | Pila vacía; deshacer una devolución que reasignó la unidad a la fila | Sin operaciones devuelve None; hay que deshacer primero la asignación y el turno vuelve al frente | pila vacía -> None; Se deshizo el préstamo P0012; frente de la fila U002; Se deshizo la devolución P0010 | ✓ |
| RQF-015 | Cuello de botella | 3.000 préstamos y 3.000 deshacer seguidos | Vuelve exactamente al estado inicial; cada deshacer es O(1) salvo la búsqueda en la lista de activos | préstamos 0, unidades 3.000, siguiente código P0001, 0,171 s | ✓ |
| RQF-036 | Exitoso | Listar activos de la demo | 5 activos: P0007 a P0011 | ['P0007', 'P0008', 'P0009', 'P0010', 'P0011'] | ✓ |
| RQF-036 | Borde | Sin préstamos; luego prestar y devolver el único | Lista vacía en ambos momentos | antes [], después [], cola de la lista None | ✓ |
| RQF-036 | Cuello de botella | Listar los activos de 6,000 préstamos 100 veces | Coincide con contar los activos en el historial | 1.805 activos (historial dice 1.805), 0,005 s | ✓ |
| RQF-037 | Exitoso | Listar atrasados de la demo | P0007 de U005 con 6 días de atraso | P0007 U005 6 días | ✓ |
| RQF-037 | Borde | Préstamo que vence hoy y otro que venció ayer | El que vence hoy no está atrasado; el de ayer sí, con 1 día | P0001 vence hoy, P0002 venció ayer -> atrasados [('P0002', 1)] | ✓ |
| RQF-037 | Cuello de botella | Atrasados entre 6,000 préstamos, 100 veces | Todos los listados tienen más de 14 días desde el préstamo | 1.372 atrasados, 0,121 s | ✓ |
| RQF-038 | Exitoso | Consultar P0011 | U004, R0004, sede Norte, activo | U004, R0004, Norte, Activo, vence 2026-11-24 18:14 | ✓ |
| RQF-038 | Borde | Código en minúscula y un préstamo deshecho | Encuentra 'p0001'; el deshecho ya no existe | p0001 -> P0001; P0012 tras deshacer -> None | ✓ |
| RQF-038 | Cuello de botella | Consultar los 6,000 préstamos por código | Todos encontrados en tiempo casi constante | 6.000 en 0,003 s | ✓ |
| RQF-039 | Exitoso | Activos en Norte y en Centro | Norte: P0011; Centro: 4 | Norte ['P0011'], Centro 4 | ✓ |
| RQF-039 | Borde | Sede sin préstamos (Occidente) y sede inexistente | Lista vacía y error | Occidente []; La sede 'Marte' no existe | ✓ |
| RQF-039 | Cuello de botella | Activos por cada una de las 6 sedes (6,000 préstamos) | La suma por sede es igual al total de activos | suma 1.805 = activos 1.805, 0,001 s | ✓ |

## M04 · Turnos

| RQF | Tipo | Caso | Esperado | Obtenido | Resultado |
|---|---|---|---|---|---|
| RQF-016 | Exitoso | Sin unidades de R0001 en Centro, U003 pide turno | Turno T0001 en posición 1, guarda la sede pedida | T0001, posición 1, sede Centro | ✓ |
| RQF-016 | Borde | Pedir turno habiendo unidades; repetir turno; usuario inactivo | Los tres se rechazan con el motivo | Hay unidades de R0001 en Centro: registre el préstamo; U001 ya está en la fila de R0001 en Centro; El usuario U003 está inactivo | ✓ |
| RQF-016 | Cuello de botella | 3.000 usuarios hacen fila por el mismo recurso | Fila de 3.000 en orden de llegada; la validación de repetidos recorre la fila (O(n)) | 3.000 en fila, primero U003, último U3002, 0,530 s | ✓ |
| RQF-017 | Exitoso | Fila U003, U004; se devuelve una unidad | La unidad pasa automáticamente a U003; U004 queda primero | asignado P0003 a U003; sigue U004 | ✓ |
| RQF-017 | Borde | El primero de la fila quedó inactivo; devolución en otra sede | Se salta al inactivo (su turno se cancela); la fila de Centro no recibe unidades de Norte | tras devolver en Norte siguen 2 en fila de Centro; en Centro se asignó a U004; turno de U003: Cancelada | ✓ |
| RQF-017 | Cuello de botella | Fila de 2.000; se fijan 2.000 unidades de una vez | Toda la fila se atiende en orden de llegada | 2.000 asignados, fila restante 0, 0,019 s | ✓ |
| RQF-018 | Exitoso | Fila de R0003 (sala) en Centro | U002 y luego U004 | ['U002', 'U004'], total 2 | ✓ |
| RQF-018 | Borde | Recurso sin fila y fila de todas las sedes de R0004 | Vacía; R0004 solo tiene a U001 esperando en Norte | R0001 []; R0004 [('U001', 'Norte')] | ✓ |
| RQF-018 | Cuello de botella | Fila de los 1,500 recursos (6 sedes cada uno) | La suma coincide con el total en espera | 300 en espera, 0,012 s | ✓ |
| RQF-040 | Exitoso | Ver quién sigue en la sala (dos veces) | U002 las dos veces; la fila no cambia | U002, U002; en fila 2 | ✓ |
| RQF-040 | Borde | Ver siguiente de un recurso sin fila | None | None | ✓ |
| RQF-040 | Cuello de botella | 10,000 consultas del frente con 1,000 en fila | O(1) cada una | frente U003, 0,011 s | ✓ |
| RQF-041 | Exitoso | Cancelar el turno de U002 en la sala | U004 pasa al frente | T0001 Cancelada; sigue U004 | ✓ |
| RQF-041 | Borde | Cancelar dos veces y cancelar un turno inexistente | Ambos con error | La solicitud T0002 ya está cancelada; La solicitud T0999 no existe | ✓ |
| RQF-041 | Cuello de botella | Cancelar la mitad de una fila de 2.000 | Quedan los demás en el mismo orden | quedan 1.000, 0,175 s | ✓ |

## M05 · Categorías

| RQF | Tipo | Caso | Esperado | Obtenido | Resultado |
|---|---|---|---|---|---|
| RQF-025 | Exitoso | Crear 'Optica' dentro de Fisica (C016) | Queda en el nivel 4 con ruta Material de estudio > Libros > Ciencias > Fisica > Optica | Material de estudio > Libros > Ciencias > Fisica > Optica, nivel 4 | ✓ |
| RQF-025 | Borde | Código repetido, padre inexistente, nombre repetido bajo el mismo padre y código vacío | Rechaza los cuatro; el mismo nombre en otro padre sí se permite | La categoría C001 ya existe; La categoría C999 no existe; Ya existe 'laptops' dentro de Equipos; El código de la categoría no puede estar vacío; 'Laptops' dentro de Libros aceptada | ✓ |
| RQF-025 | Cuello de botella | Árbol de 10 niveles con 2 hijas por nodo (2,047 categorías) | Todas registradas con su nivel correcto | 2.047 categorías, nivel de la última hoja 10, 0,032 s | ✓ |
| RQF-026 | Exitoso | Consultar Equipos (C009) con todo lo que cuelga | Equipos > Computadores y Laptops, y sus 5 recursos (incluidos los que no están operativos) | [('Equipos', 0), ('Computadores', 1), ('Laptops', 1)]; recursos ['R0010', 'R0012', 'R0011', 'R0005', 'R0002'] | ✓ |
| RQF-026 | Borde | Consultar una hoja (C005, Sala con televisor) y un código inexistente | La hoja devuelve solo ella misma; el inexistente da error | [(C005: Sala con televisor, 0)]; La categoría C404 no existe | ✓ |
| RQF-026 | Cuello de botella | Subárbol de la raíz con 2,047 categorías (recursivo) | Las 2,047 en preorden | 2.047 nodos, profundidad máxima 10, 0,001 s | ✓ |
| RQF-027 | Exitoso | Índice de las 16 categorías de la demo | Recorrido en orden por código y AVL balanceado | ['C001', 'C002', 'C003', 'C004', 'C005', 'C006', 'C007', 'C008', 'C009', 'C010', 'C011', 'C012', 'C013', 'C014', 'C015', 'C016'], altura 5, balanceado True | ✓ |
| RQF-027 | Borde | Índice vacío y con una sola categoría | Altura 0 y 1 | vacío 0, uno 1 | ✓ |
| RQF-027 | Cuello de botella | 5.000 categorías con códigos en orden (C00001, C00002...) | Altura del AVL ≤ 1,44·log2(n) (≈ 18); un BST tendría altura 5,000 | altura 13, 4.987 rotaciones, 0,080 s | ✓ |

## M06 · Informes

| RQF | Tipo | Caso | Esperado | Obtenido | Resultado |
|---|---|---|---|---|---|
| RQF-021 | Exitoso | Ordenar recursos por número de préstamos | R0001 (4), R0004 (3), R0002 (2)... | [('R0001', 4), ('R0004', 3), ('R0002', 2)] | ✓ |
| RQF-021 | Borde | Empates (R0003 y R0005 con 1) y cantidad 0 | En empate conserva el orden por código (merge sort estable); cantidad 0 se rechaza | empatados ['R0003', 'R0005']; La cantidad debe ser mayor o igual a 1 | ✓ |
| RQF-021 | Cuello de botella | Ordenar 1,500 recursos con 6,000 préstamos | Orden no creciente | máximo 15, mínimo 0, 0,002 s | ✓ |
| RQF-022 | Exitoso | Ordenar la demo por fecha de registro | R0001 a R0012 (se registraron en ese orden) | ['R0001', 'R0002', 'R0003', 'R0004', 'R0005', 'R0006', 'R0007', 'R0008', 'R0009', 'R0010', 'R0011', 'R0012'] | ✓ |
| RQF-022 | Borde | Sin recursos; y más recientes primero con fechas iguales | Lista vacía; con fechas iguales desempata por código | vacío []; recientes primero ['R0003', 'R0002', 'R0001'] | ✓ |
| RQF-022 | Cuello de botella | Quick sort de 5.000 recursos con fechas desordenadas | Fechas crecientes | de 2020-01-01 00:00 a 2020-01-04 11:19, 0,007 s | ✓ |
| RQF-024 | Exitoso | Buscar 'estructuras de datos' (binaria iterativa, recursiva y secuencial) | Las tres encuentran R0004 | [R0004: Estructuras de Datos (Libro)], [R0004: Estructuras de Datos (Libro)], R0004: Estructuras de Datos (Libro) | ✓ |
| RQF-024 | Borde | Nombre inexistente, nombre vacío y dos recursos con el mismo nombre | Vacío, error y los dos homónimos | inexistente []; El nombre a buscar no puede estar vacío; homónimos ['R0001', 'R0013'] | ✓ |
| RQF-024 | Cuello de botella | 300 búsquedas por nombre en 5.000 recursos: binaria vs. secuencial | Mismos resultados; la binaria sobre el catálogo ordenado es mucho más rápida | binaria 0,6 ms vs. secuencial 112,3 ms (187 veces) | ✓ |
| RQF-031 | Exitoso | Informe con los 2 recursos de mayor demanda | Python 101 y Estructuras de Datos | ['Python 101', 'Estructuras de Datos'] | ✓ |
| RQF-031 | Borde | Pedir el top 10 con solo 2 recursos y sin préstamos | Devuelve los 2 con 0 préstamos | [('A', 0), ('B', 0)] | ✓ |
| RQF-031 | Cuello de botella | Top 10 repetido 50 veces (1,500 recursos) | Siempre el mismo resultado | 1 resultado distinto, 0,115 s | ✓ |
| RQF-032 | Exitoso | Tasa de la demo | 5 a tiempo de 7 evaluables = 71,4 % | 5 de 7 = 71,4 % | ✓ |
| RQF-032 | Borde | Sin préstamos; y un préstamo devuelto justo el día límite | 0 % sin división por cero; el del día límite cuenta a tiempo | vacío 0,0 %; día límite -> 100,0 % | ✓ |
| RQF-032 | Cuello de botella | Tasa sobre 6,000 préstamos | a tiempo + tarde = total y 0–100 % | 3.218 a tiempo de 5.567 = 57,8 %, 0,004 s | ✓ |
| RQF-033 | Exitoso | Demanda agrupada en la categoría principal | Material de estudio 10 préstamos y Espacios de estudio 1 (la sala) | [('Material de estudio', 10), ('Espacios de estudio', 1)] | ✓ |
| RQF-033 | Borde | Sistema sin préstamos | Lista vacía | [] | ✓ |
| RQF-033 | Cuello de botella | Demanda por subcategoría con 6,000 préstamos y 26 categorías | La suma por categoría es igual al total de préstamos | 22 categorías, mayor ('Material de estudio > Equipos > Laptops', 1007), 0,043 s | ✓ |
| RQF-034 | Exitoso | Informe de inventario de la demo | 3 libros (7 unidades); 5 equipos, 3 operativos (7); 4 salas (3) | [('Libro', 3, 3, 7), ('Equipo', 5, 3, 7), ('Sala', 4, 4, 3)] | ✓ |
| RQF-034 | Borde | Un recurso dado de baja | Cuenta como registrado pero no como operativo | ('Libro', 3, 2, 7) | ✓ |
| RQF-034 | Cuello de botella | Informe con 1,500 recursos | Los registrados suman 1,500 | [('Libro', 500, 491, 2325), ('Equipo', 500, 489, 2397), ('Sala', 500, 498, 2436)], 0,002 s | ✓ |
| RQF-043 | Exitoso | Reporte de uso de la demo | 11 préstamos: 5 activos, 6 devueltos, 1 atrasado | {'Préstamos registrados': 11, 'Préstamos activos': 5, 'Préstamos devueltos': 6, 'Préstamos atrasados': 1, 'Usuarios activos': 5, 'Usuarios con préstamos': 4} | ✓ |
| RQF-043 | Borde | Sistema vacío | Todos los indicadores en 0 | {'Préstamos registrados': 0, 'Préstamos activos': 0, 'Préstamos devueltos': 0, 'Préstamos atrasados': 0, 'Usuarios activos': 0, 'Usuarios con préstamos': 0} | ✓ |
| RQF-043 | Cuello de botella | Reporte con 6,000 préstamos | Activos + devueltos = registrados | {'Préstamos registrados': 6000, 'Préstamos activos': 1805, 'Préstamos devueltos': 4195, 'Préstamos atrasados': 1372, 'Usuarios activos': 3000, 'Usuarios con préstamos': 1359}, 0,002 s | ✓ |
| RQF-044 | Exitoso | Usuarios y recursos por nombre | Ana, Carlos, Luis, Maria, Pedro; recursos en orden alfabético | ['Ana', 'Carlos', 'Luis', 'Maria', 'Pedro']; ['Auditorio Central', 'Computador Lab 1', 'Estructuras de Datos', 'Fisica Universitaria', 'Portatil Dell', 'Proyector 1', 'Python 101', 'Sala de Conferencias 301', 'Sala de Estudio', 'Sala TV 2'] | ✓ |
| RQF-044 | Borde | Nombres que solo cambian en mayúsculas y nombres iguales | Ignora mayúsculas y en empate ordena por código | [('Ana', 'U002'), ('beto', 'U001'), ('Beto', 'U003')] | ✓ |
| RQF-044 | Cuello de botella | 3,000 usuarios con merge sort y 1,500 recursos por el BST | Ambos listados ordenados | 3.000 usuarios y 1.478 recursos, 0,009 s | ✓ |

## M07 · Inventario

| RQF | Tipo | Caso | Esperado | Obtenido | Resultado |
|---|---|---|---|---|---|
| RQF-008 | Exitoso | Marcar R0006 como Dañado (desde Inventario) y después volverlo a Operativo | Mientras está dañado: sale del catálogo, no se presta y sigue registrado con su historial; al volver a Operativo regresa al catálogo | dañado: en catálogo=False, sigue registrado=True; préstamo rechazado: El recurso R0006 está dado de baja; operativo de nuevo: en catálogo=True, estado Vigente | ✓ |
| RQF-008 | Borde | R0004 con préstamos activos; R0006 con una persona en fila marcado Dañado y luego Operativo; una sala con fila dada de baja; condición repetida y condición inválida | R0004 se rechaza; la fila de R0006 se conserva, no recibe turnos nuevos y se atiende al cargar unidades ya operativo; la baja de la sala cancela su fila; errores claros | fila de R0006 conservada 1; al cargar unidades se prestó a U001; baja de R0013 canceló 1; No se puede marcar R0004 como dañado: tiene 2 préstamo(s) activo(s); registre primero su devolución; El recurso R0006 ya está en condición Dañado; Condición 'Perdido' no válida. Opciones: Operativo, Dañado, En reparación, Sin uso, Dado de baja | ✓ |
| RQF-008 | Cuello de botella | Dar de baja la mitad de 2.000 recursos y marcar otro cuarto como Sin uso | El catálogo (BST) queda con la cuarta parte y ningún recurso se borra | catálogo 500, registrados 2.000, no operativos 1.500, 0,240 s | ✓ |
| RQF-009 | Exitoso | Consultar R0001 en Centro antes y después de prestar y devolver | 2 -> 1 -> 2 | 2 -> 1 -> 2 | ✓ |
| RQF-009 | Borde | Sede sin unidades, sede inexistente y recurso inexistente | 0 para la sede sin unidades; error claro para los otros dos | Norte=0; La sede 'Marte' no está en el inventario; El recurso R0099 no está en el inventario | ✓ |
| RQF-009 | Cuello de botella | 50,000 consultas sobre una matriz de 20 sedes × 2,000 recursos | O(1) por consulta (dos búsquedas en tabla hash y un acceso a la matriz) | 0,060 s (1,2 µs por consulta) | ✓ |
| RQF-010 | Exitoso | Matriz sede × recurso y proyección sede × día de la sala R0003 (3 días) | La sala está en 0 hoy y vuelve a 1 mañana en Centro (vence el préstamo de U001) | 4 filas en la matriz sede × recurso; Centro por día: [0, 1, 1] | ✓ |
| RQF-010 | Borde | Proyección de 1 día, de 0 días y de un recurso sin préstamos | 1 columna; 0 días se rechaza; sin préstamos la fila es constante | 1 columna; Los días debe ser mayor o igual a 1; R0006 [0, 0, 0, 0] | ✓ |
| RQF-010 | Cuello de botella | Matriz sede × recurso de 6 × 1,500 y proyección de 30 días del más prestado | Ambas se generan; la proyección nunca baja de un día al siguiente | 96.135 caracteres de matriz; proyección no decreciente=True; 0,009 s | ✓ |
| RQF-045 | Exitoso | Fijar 3 unidades de R0006 en Sur | Queda en 3 y se puede prestar | unidades 3 -> préstamo P0012 -> 2 | ✓ |
| RQF-045 | Borde | Cantidad negativa, texto y fijar unidades a un recurso con fila de espera | Rechaza los dos primeros; al poner 2 unidades a la sala se atiende la fila (U002 y U004) | La cantidad de unidades debe ser mayor o igual a 0; La cantidad de unidades debe ser un número entero; asignados a ['U002', 'U004'] | ✓ |
| RQF-045 | Cuello de botella | Fijar unidades en todas las celdas de 10 sedes × 2,000 recursos | 20,000 celdas actualizadas; el total coincide | total 60.000 unidades, 0,026 s | ✓ |

## M08 · Asistente de decisiones

| RQF | Tipo | Caso | Esperado | Obtenido | Resultado |
|---|---|---|---|---|---|
| RQF-046 | Exitoso | Recomendar traslados de R0004 (Norte tiene fila y 0 unidades) y aplicarlo | Mover 1 de Centro a Norte; al aplicarlo se presta a U001, que esperaba en Norte | [Mover 1 de R0004: Centro -> Norte]; asignado ['P0012'] a U001 | ✓ |
| RQF-046 | Borde | Recurso sin unidades en ninguna sede, sin demanda, y traslado de más unidades de las que hay | Sin recomendaciones en los dos primeros; el traslado imposible se rechaza | R0003 []; R0006 []; Centro solo tiene 2 unidad(es) de R0002 | ✓ |
| RQF-046 | Cuello de botella | Recomendación para los 1,500 recursos × 6 sedes | Ningún traslado deja una sede con unidades negativas | 1.678 traslados sugeridos, válidos=True, 0,055 s | ✓ |
| RQF-047 | Exitoso | Top 3 de compras de la demo | Primero la sala R0003 (2 personas en fila y 1 unidad): índice 2,5; después la laptop dañada R0011 (1 en fila) como 'Reparar o reponer' | R0003 índice 2,5 (Comprar más unidades), R0011 índice 2,0 (Reparar o reponer), R0004 índice 1,0 (Comprar más unidades) | ✓ |
| RQF-047 | Borde | Sin demanda y cantidad 0 | Lista vacía y error | []; La cantidad debe ser mayor o igual a 1 | ✓ |
| RQF-047 | Cuello de botella | Top 20 entre 1,500 recursos (montículo de máximos) | Índices en orden no creciente | mayor 4,0, menor 1,67, 0,039 s | ✓ |
| RQF-048 | Exitoso | Predecir la sala R0003 (sin unidades) y R0001 (con unidades) | Sala: 1 día en Centro (vence el préstamo de U001); R0001 disponible ahora, promedio 3,3 días | R0003 en 1 día(s) en Centro; R0001 ahora=True, promedio 3,3 con confianza 30% | ✓ |
| RQF-048 | Borde | Recurso sin unidades ni préstamos (R0006), recurso de baja y código inexistente | R0006: no se libera solo (días = None); el de baja no se predice (no operativo); el inexistente da error | días None, muestras 0; de baja: operativo=False (Dado de baja); El recurso R9999 no existe | ✓ |
| RQF-048 | Cuello de botella | Predicción para los 1,500 recursos | Cada predicción tiene confianza entre 0 y 1 y días ≥ 0 cuando aplica | 1.500 predicciones válidas=True, 0,467 s | ✓ |
| RQF-049 | Exitoso | Alertas de la demo en orden de urgencia | Atraso de P0007, laptop R0011 dañada con 1 en fila, sala sin unidades con 2 en fila, R0004 en Norte, U005 reincidente y computador R0012 con 20 días en reparación | 106 Atraso \| 92 Recurso dañado \| 82 Sin unidades \| 81 Sin unidades \| 62 Usuario reincidente \| 45 Reparación demorada | ✓ |
| RQF-049 | Borde | Sistema sin problemas; un usuario con 1 solo atraso; recursos dañado sin demanda, en reparación hace 3 días, sin uso y dado de baja | Sin alertas; atraso sí y reincidente no; dañado sin demanda con urgencia baja (50), sin uso (20); la reparación reciente y el dado de baja no generan alerta | vacío []; después ['Atraso']; por condición [(50, 'Recurso dañado'), (20, 'Recurso sin uso')] | ✓ |
| RQF-049 | Cuello de botella | Alertas con 6,000 préstamos, 1,500 recursos y 6 sedes | Urgencias en orden no creciente | 2.242 alertas, 0,049 s | ✓ |
| RQF-051 | Exitoso | Préstamos que vencen en los próximos 2 días | P0010 (mañana) y luego P0011 (en 2 días) | [('P0010', 1), ('P0011', 2)] | ✓ |
| RQF-051 | Borde | Uno vence hoy, uno ya venció y anticipación 0 y 31 días | Con 0 días solo el de hoy; el vencido no aparece (es atraso); 31 se rechaza | [('P0001', 0)]; Los días de anticipación debe ser menor o igual a 30 | ✓ |
| RQF-051 | Cuello de botella | Vencimientos de 7 días con 6,000 préstamos (montículo de mínimos) | Salen ordenados del más próximo al más lejano | 235 préstamos por vencer, 0,002 s | ✓ |

## M09 · Red de sedes

| RQF | Tipo | Caso | Esperado | Obtenido | Resultado |
|---|---|---|---|---|---|
| RQF-028 | Exitoso | Desde Norte, buscar R0004 (Norte no tiene unidades) | Centro, a 1 tramo, con 2 unidades | ('Centro', 1, 2) | ✓ |
| RQF-028 | Borde | La sede actual sí tiene; desde una sede aislada; sede inexistente | Distancia 0; None porque no alcanza ninguna; error | ('Centro', 0, 4); None; La sede 'Marte' no existe | ✓ |
| RQF-028 | Cuello de botella | Red en cadena de 1.000 sedes; el recurso solo está en la última | La encuentra a 999 tramos (BFS O(V + E)) | ('S999', 999, 1), 0,005 s | ✓ |
| RQF-029 | Exitoso | Ruta de Norte a Sur y rutas alternativas | Directa Norte -> Sur; alternativa Norte -> Centro -> Sur | ['Norte', 'Sur']; [['Norte', 'Sur'], ['Norte', 'Centro', 'Sur']] | ✓ |
| RQF-029 | Borde | Ruta a la misma sede y a una sede aislada | [Centro] y [] | ['Centro']; [] | ✓ |
| RQF-029 | Cuello de botella | Ruta de punta a punta en una cadena de 600 sedes con un atajo | BFS toma el atajo (300 tramos); las alternativas descartan la ruta de 599 tramos por la poda; sin poda el backtracking encuentra las 2 | 300 tramos (sin atajo serían 599); alternativas con poda 1, sin poda 2 (599 tramos la larga); 0,011 s | ✓ |
| RQF-030 | Exitoso | Detectar sedes aisladas en la demo | Occidente | ['Occidente'] | ✓ |
| RQF-030 | Borde | Conectar Occidente; luego quitar una conexión que no existe | Ya no hay aisladas; quitar una conexión inexistente da error | aisladas []; Occidente y Norte no están conectadas | ✓ |
| RQF-030 | Cuello de botella | 500 sedes: una red principal de 400 y 100 sedes sueltas | Encuentra las 100 aisladas | 100 aisladas, 0,002 s | ✓ |

## Persistencia (RQF-050)

| RQF | Tipo | Caso | Esperado | Obtenido | Resultado |
|---|---|---|---|---|---|
| RQF-050 | Exitoso | Guardar la demo, cargarla y volver a guardar | Los archivos quedan idénticos; filas, préstamos y contadores se recuperan | 6 usuarios, 12 recursos, 4 sedes, 16 categorías, 11 préstamos, 4 en espera; archivos idénticos=True; fila de la sala ['U002', 'U004']; siguiente usuario U006 | ✓ |
| RQF-050 | Borde | Guardar y cargar recursos fuera de servicio; cargar datos de la versión anterior (sin condiciones.txt) | La condición, su fecha, la fila del recurso dañado y el catálogo se recuperan; sin condiciones.txt carga igual (la condición viene en recursos.txt) | R0011 Dañado con 1 en fila, R0012 En reparación desde 2026-11-02; en catálogo []; sin condiciones.txt: 2 no operativos, fecha None | ✓ |
| RQF-050 | Borde | Carpeta vacía, sistema vacío, nombre con ';' y una fecha dañada en el archivo | Error claro en la carpeta vacía; el vacío y el ';' se guardan y cargan bien; la fecha dañada indica archivo y línea | No hay datos guardados en '<temporal>/nada'; vacío guardado=True; nombre 'Pérez; Ana'; usuarios.txt, línea 2: time data 'xx26-11-22 18:14' does not match format '%Y-%m-%d %H:%M' | ✓ |
| RQF-050 | Cuello de botella | Guardar y cargar 3,000 usuarios, 1,500 recursos y 6,000 préstamos | Se recuperan todos los registros | 14.025 filas; cargado: 3000 usuarios, 1500 recursos, 6 sedes, 26 categorías, 6000 préstamos, 300 en espera; 0,22 s | ✓ |
| RQF-050 | Cuello de botella | Cargar la carpeta «datos de prueba» incluida en el repositorio | Más de 500 registros, coherentes con el inventario | 1.172 registros: 300 usuarios, 200 recursos, 6 sedes, 26 categorías, 600 préstamos, 39 en espera | ✓ |
