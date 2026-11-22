# Cómo ejecutar el sistema

Sistema de Gestión de Recursos Comunitarios Compartidos (Línea 1). Solo usa la
biblioteca estándar de Python 3.9 o superior; las pruebas necesitan `pytest`.

## Ejecutar el programa

Abra una terminal en esta carpeta (la que contiene `main.py`):

```bash
python main.py
```

- **Primera vez:** carga los datos de demostración (5 usuarios, 12 recursos, 4 sedes, préstamos, filas, un préstamo atrasado, una laptop dañada y un computador en reparación).
- **Al abrir:** muestra los préstamos que vencen en los próximos 2 días y cuántos recursos están fuera de servicio (RQF-051).
- **Categorías:** dos principales, *Espacios de estudio* (Sala de conferencias, Sala de estudio grupal, Sala de estudio individual, Sala con televisor, Sala de cómputo, Auditorio) y *Material de estudio* (Equipos → Computadores y Laptops; Libros, con sus propias subcategorías).
- **Los recursos no se borran:** en Inventario (menú 7 → opción 5) se cambia su condición: Operativo, Dañado, En reparación, Sin uso o Dado de baja (baja lógica, RQF-008; código en `modulos/M07_Inventario/GestorCondiciones.py`). El recurso no puede tener préstamos activos. Si no está operativo no se presta, no recibe turnos y el asistente no lo recomienda, pero conserva su historial y puede volver a Operativo. Dañado y En reparación conservan la fila de espera; Sin uso y Dado de baja la cancelan. En Recursos (menú 2 → opción 4) solo se consultan. La fecha de cada condición se guarda en `condiciones.txt`.
- **Al salir (opción 0):** guarda todo en la carpeta `datos/` en archivos de texto (RQF-050). La próxima vez carga desde ahí.
- **Datos de prueba con más de 500 registros:** menú 10 → opción 3.
- **Consultar sin saber el código:** en Usuarios y en Recursos, consultar (y también actualizar, y en Usuarios dar de baja o reactivar) muestra primero la lista actual con el estado de cada uno. Se escribe el código o se oprime Enter para buscar al usuario por **tipo y número de documento** (CC, TI, CE o PA) o el material por **tipo y nombre** (basta una parte del nombre).

| Opción | Módulo | Responsable |
|---|---|---|
| 1 | M01 · Usuarios | Edward Castillo |
| 2 | M02 · Recursos y sedes | Santiago López |
| 3 | M03 · Préstamos y devoluciones | Esteban Velásquez |
| 4 | M04 · Turnos y fila de espera | Esteban Velásquez |
| 5 | M05 · Categorías | Santiago López |
| 6 | M06 · Informes y listados | Edward Castillo |
| 7 | M07 · Inventario por sede | María Fernanda Morales |
| 8 | M08 · Asistente de decisiones del administrador | María Fernanda Morales |
| 9 | M09 · Red de sedes | María Fernanda Morales |
| 10 | Guardar y cargar datos (persistencia) | María Fernanda Morales |
| 11 | Demostración de estructuras | — |

Variables de entorno opcionales: `DATOS_PROYECTO=<carpeta>` para usar otra carpeta de datos y `SIN_LIMPIAR=1` para no borrar la pantalla.

## Ejecutar las pruebas

```bash
python -m pip install pytest
python -m pytest            # 200 pruebas
python -m pytest -v         # con el nombre de cada caso
```

Cada RQF y cada estructura tiene tres casos: **exitoso**, **borde** y **cuello de botella**. Al terminar se genera `tests/reporte/resultados_pruebas.json` con lo esperado, lo obtenido y el tiempo de cada caso (ver `PRUEBAS.md`).

Para regenerar la carpeta `datos de prueba/`: `python -m persistencia.datos_masivos`.

Para medir las estructuras propias frente a `list`, `dict` y `set` de Python (comparación que pide el lineamiento): `python medicion_eficiencia.py resultado.json`.

## Estructura de paquetes

```
main.py                      arranque: carga, aviso de vencimientos, menú y guardado
medicion_eficiencia.py       medición de tiempos: estructuras propias vs. nativas
estructuras/                 estructuras propias (sin list, dict ni set como almacenamiento)
  VectorDinamico, ListaEnlazada (base), ListaSimple, ListaDoble, Pila, ColaFIFO,
  TablaHash (djb2), ConjuntoHash, ArbolBinarioBusqueda, ArbolAVL, Monticulo, Grafo,
  Algoritmos (inserción, merge sort, quick sort, búsquedas)
modulos/
  comun.py                   generador de códigos y validaciones compartidas
  sistema.py                 crea y conecta los gestores M01–M09 (un solo lugar)
  M01_usuarios/ ... M09_Red_Sedes/
persistencia/                guardar/cargar en .txt, datos de demostración y datos masivos
interfaz/                    un menú por módulo + consola.py (entrada/salida común)
tests/                       pruebas por módulo con reporte de casos
datos de prueba/             1.172 registros de prueba en texto plano
```

## Estructura de datos por requerimiento

| Estructura | Dónde se usa |
|---|---|
| Vector dinámico | Usuarios y recursos en orden de registro (M01, M02); base de la pila y del montículo |
| Lista enlazada simple | Préstamos activos (RQF-036) |
| Lista doble | Historial de préstamos en ambos sentidos (RQF-013, 014) |
| Pila | Deshacer (RQF-015); recorridos del BST/AVL y DFS sin recursión |
| Cola circular | Fila de espera por recurso y sede (RQF-016 a 018) |
| Tabla hash djb2 | Búsqueda por código de usuarios, recursos, préstamos y turnos (RQF-019, 020, 038) |
| Conjunto | Usuarios activos (RQF-004, 035), nombres de categorías sin repetir (RQF-025) |
| BST | Catálogo ordenado por nombre (RQF-052) |
| AVL | Índice de categorías por código (RQF-027) |
| Árbol n-ario | Categorías y subcategorías (RQF-025, 026) |
| Matriz | Inventario sede × recurso y proyección sede × día (RQF-009, 010) |
| Montículo | Redistribución, compras, alertas y vencimientos (RQF-046, 047, 049, 051) |
| Grafo (lista de adyacencia) | Red de sedes: BFS, ruta más corta, backtracking, aisladas (RQF-028 a 030) |
| Recursión | Subárbol de categorías, merge sort, quick sort, búsqueda binaria recursiva, backtracking |

## CI/CD (GitHub Actions)

El flujo `.github/workflows/ci_cd.yml` se ejecuta en cada push y pull request a `main`:

1. **Calidad:** compila todo y revisa estilo con flake8.
2. **Pruebas:** las 200 pruebas en Linux y Windows con Python 3.9, 3.11 y 3.13; sube el reporte de casos como artefacto.
3. **Ejecución:** abre el programa con los datos de prueba, recorre menús, verifica que guarda al salir y publica la medición de eficiencia.
4. **Entrega (CD):** al crear una etiqueta `v*`, si todo pasó, publica un Release con el ZIP del sistema.

```bash
git tag v3.0
git push origin v3.0
```
