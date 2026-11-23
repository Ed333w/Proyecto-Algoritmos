# Proyecto Algoritmos · Sistema de Gestión de Recursos Comunitarios Compartidos

Línea 1 · Algoritmos y Estructuras de Datos · Universidad del Rosario

Red de bibliotecas universitarias con varias sedes: usuarios, libros, equipos y salas,
préstamos con fila de espera, categorías, informes, inventario por sede, red de sedes
y un asistente de decisiones para el administrador. Todo en Python con estructuras de
datos propias.

| Carpeta | Contenido |
|---|---|
| `Analisis y planeación/` | Informes de entrega y documentación de casos de prueba |
| `Diseño/` | Diagrama de clases y modelos |
| `Codificación y ejecución/` | Código, pruebas y datos de prueba — ver [COMO_EJECUTAR.md](Codificación%20y%20ejecución/COMO_EJECUTAR.md) |

```bash
cd "Codificación y ejecución"
python main.py              # programa
python -m pytest            # 200 pruebas
```

Equipo: Edward Castillo (M01, M06) · Santiago López (M02, M05) · Esteban Velásquez (M03, M04) ·
María Fernanda Morales (M07, M08, M09 y persistencia).

## Uso ético de la inteligencia artificial

En este proyecto usamos a **Claude** (Anthropic) como herramienta de apoyo, no como reemplazo del trabajo del equipo.

**Lo que hicimos nosotros**
- Las ideas del proyecto: el problema, el caso de la red de bibliotecas, los módulos, los requerimientos y las historias de usuario.
- Las decisiones de diseño: qué estructura usar en cada parte y por qué (tabla hash, listas, pila, cola, árboles, grafo, montículo).
- La programación de los módulos, que trabajamos en conjunto con la IA.
- Revisar todo lo que la IA propuso antes de aceptarlo.

**En qué nos ayudó Claude**
- Mejorar nuestras ideas y proponer alternativas (por ejemplo, el asistente de decisiones del M08).
- Encontrar y corregir errores, quitar código duplicado y ordenar el código.
- Proponer casos de prueba (exitoso, borde y cuello de botella).
- Dar formato y redacción a la documentación (informe, casos de prueba, Kanban).

**Cómo lo usamos de forma responsable**
- No entregamos nada que no entendamos: cada integrante puede explicar su módulo, las estructuras que usa y su complejidad.
- Todo el código se verificó con las 200 pruebas automáticas y ejecutando el programa.
- Las estructuras de datos son propias; no se usaron librerías externas para resolver el problema.
- Las decisiones finales y la responsabilidad por el proyecto son del equipo.
- Declaramos el uso de la IA aquí para ser transparentes con la docente.
