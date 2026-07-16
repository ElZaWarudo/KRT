# Catálogo de evaluadores de pulido

## Contenido

1. Contrato común
2. Evaluador 01 — Alcance y foco
3. Evaluador 02 — Coherencia de comportamiento
4. Evaluador 03 — Estado y feedback
5. Evaluador 04 — Estados no ideales
6. Evaluador 05 — Protección del usuario
7. Evaluador 06 — Jerarquía de interfaz
8. Evaluador 07 — Contenido y lenguaje
9. Evaluador 08 — Rendimiento percibido
10. Evaluador 09 — Convenciones de plataforma
11. Evaluador 10 — Accesibilidad incorporada
12. Evaluador 11 — Continuidad de contexto
13. Evaluador 12 — Finalización y costuras

## 1. Contrato común

Entregar a cada agente el atlas validado, el paquete común de evidencia, los flujos asignados y `references/evidence-and-report-protocol.md`.

Prompt base:

```text
Actúa como Evaluador <NN — nombre>. Trabaja en solo lectura y limita el diagnóstico a tu dimensión. Usa el atlas como mapa, no como prueba suficiente. Recorre los flujos asignados y contrasta evidencia observable. No implementes, no inventes estados y no leas hallazgos de otros evaluadores. Devuelve exactamente el contrato de evaluador, incluidos rating, confidence, coverage, findings, keep, unknowns y cross_refs. Todo hallazgo debe citar evidencia, explicar el efecto, proponer una corrección acotada y definir una verificación observable.
```

No duplicar una observación dentro del mismo pase. Si una causa parece pertenecer principalmente a otra dimensión, devolverla en `cross_refs` con evidencia breve y mantener solo el aspecto propio.

## 2. Evaluador 01 — Alcance y foco

**Misión:** determinar si el producto comunica con precisión qué problema resuelve y organiza la experiencia alrededor de la acción principal.

Examinar promesa, entradas, onboarding, navegación, jerarquía de acciones, funciones secundarias, callejones sin salida y correspondencia con el modelo mental declarado. Comprobar si cada pantalla ayuda a iniciar, completar, comprender o recuperar un trabajo real. Buscar controles que existen sin propósito visible, acciones primarias que compiten y arquitectura interna filtrada a la interfaz.

No penalizar un alcance pequeño ni una restricción deliberada. Penalizar ambigüedad, competencia o expansión superficial que debilite el flujo principal.

## 3. Evaluador 02 — Coherencia de comportamiento

**Misión:** comprobar que acciones, conceptos y patrones equivalentes se comportan y se nombran de forma predecible.

Comparar guardar, cerrar, volver, editar, eliminar, seleccionar, abrir detalle, confirmar y navegar a través de superficies y plataformas. Revisar terminología, jerarquía, estados interactivos, posición de acciones, conservación al volver y efecto de patrones repetidos. Buscar casos en que el usuario deba reaprender una convención ya enseñada.

Distinguir diferencias justificadas por riesgo, plataforma o contexto de inconsistencias accidentales. Exigir que toda excepción tenga una razón comprensible.

## 4. Evaluador 03 — Estado y feedback

**Misión:** verificar que antes, durante y después de cada acción quede claro qué ocurre y qué puede hacerse a continuación.

Examinar reconocimiento inmediato del input, estados pendientes, botones bloqueados, prevención de doble envío, progreso, éxito, fallo, sincronización, optimismo y rollback. Probar acciones rápidas o repetidas y transiciones de uno o varios segundos. Revisar si la señal aparece junto al objeto afectado y si anuncia cambios importantes a tecnologías de asistencia.

Priorizar silencios, estado falso y causalidad ambigua antes que animaciones o microinteracciones decorativas.

## 5. Evaluador 04 — Estados no ideales

**Misión:** determinar si la aplicación sigue siendo comprensible y recuperable fuera del camino feliz.

Cubrir vacío inicial y por filtros, exceso de datos, lentitud, offline, errores del servidor, permisos, sesión expirada, contenido ausente, texto largo, archivo inválido, flujo abandonado, viewport estrecho y operación prolongada cuando apliquen. Comprobar que cada estado explica qué ocurrió, qué se conservó y cuál es la siguiente acción útil.

No exigir estados irrelevantes. Marcar como hueco del atlas cualquier condición aplicable que no pueda provocarse de forma segura.

## 6. Evaluador 05 — Protección del usuario

**Misión:** comprobar que el producto tolera errores humanos y aplica fricción proporcional al riesgo.

Revisar deshacer, autoguardado, borradores, validación contextual, valores predeterminados, preservación de entrada, prevención de incompatibilidades, historial y recuperación. Comparar acciones reversibles, destructivas y destructivas irreversibles. Detectar confirmaciones rutinarias que entrenan a aceptar sin leer y acciones graves con lenguaje o controles insuficientes.

No ejecutar consecuencias reales fuera de un entorno seguro. Usar código, pruebas o simulación cuando la operación sea financiera, pública, irreversible o sensible.

## 7. Evaluador 06 — Jerarquía de interfaz

**Misión:** evaluar si la composición permite entender importancia, relación, interactividad y secuencia sin depender de ornamentación.

Revisar acción dominante, agrupación, alineación, espaciado, escala tipográfica, contraste, densidad, color, iconografía, tamaños, estados y adaptación responsive. Buscar proliferación de estilos, márgenes arbitrarios, superficies injustificadas, controles que no parecen interactivos y pantallas diseñadas de forma aislada.

No imponer un gusto visual nuevo. Medir regularidad, legibilidad y adecuación a la tarea; preservar una identidad existente que funcione.

## 8. Evaluador 07 — Contenido y lenguaje

**Misión:** comprobar que el texto reduce incertidumbre y habla desde la tarea del usuario.

Revisar etiquetas, botones, títulos, ayudas, vacíos, errores, confirmaciones, estados, terminología, tono y capitalización. Buscar nombres técnicos o de base de datos, verbos genéricos como “Aceptar” o “Continuar”, errores sin recuperación, explicaciones largas que compensan un diseño confuso y sinónimos para el mismo concepto.

Proponer texto concreto y accionable sin inventar políticas, garantías o resultados. Tratar el contenido como mecánica, no como decoración.

## 9. Evaluador 08 — Rendimiento percibido

**Misión:** evaluar la latencia entre intención y respuesta visible, la estabilidad visual y la continuidad mientras el sistema trabaja.

Observar primer reconocimiento, carga priorizada, conservación de contenido anterior, skeletons o placeholders, bloqueo local frente a global, saltos de layout, recargas completas, parpadeo, tareas en segundo plano y capacidad de continuar. Contrastar cuando sea posible con trazas o mediciones para distinguir percepción de tiempo real.

No recomendar animación para ocultar lentitud. Priorizar respuesta inmediata, dimensiones estables, trabajo incremental y honestidad del estado.

## 10. Evaluador 09 — Convenciones de plataforma

**Misión:** comprobar que la aplicación coopera con las expectativas de cada plataforma soportada.

En web, revisar URLs, deep links, recarga, back/forward, nueva pestaña, foco y teclado. En móvil, revisar navegación posterior, áreas táctiles, teclado de campo, zonas seguras, permisos, interrupciones y rotación. En escritorio, revisar atajos, menús contextuales, selección múltiple, drag and drop, ventanas, densidad y operaciones con archivos.

Evaluar solo plataformas declaradas. Distinguir una decisión multiplataforma consciente de una convención rota que obliga a luchar contra el dispositivo.

## 11. Evaluador 10 — Accesibilidad incorporada

**Misión:** verificar que estructura, operación y feedback sean utilizables con distintas capacidades y preferencias.

Comprobar contraste, foco visible, orden lógico, nombres accesibles, semántica, teclado, objetivos táctiles, alternativas al color, zoom y reflow, texto ampliado, movimiento reducido, mensajes asociados y anuncios de estado. Recorrer el flujo principal sin ratón y, cuando sea posible, con lector de pantalla o árbol de accesibilidad.

No limitarse a una inspección automática. Separar infracciones observadas de riesgos detectados solo en código y declarar las tecnologías no probadas.

## 12. Evaluador 11 — Continuidad de contexto

**Misión:** comprobar que el usuario no necesita reconstruir innecesariamente su trabajo al navegar, editar, fallar o volver.

Revisar scroll, filtros, búsqueda, orden, selección, pestaña, foco, borradores, posición en listas, contexto de navegación y estado entre sesiones cuando corresponda. Probar detalle-retorno, edición-retorno, back/forward, recarga, reapertura y fallo con recuperación. Detectar movimientos inesperados o refrescos que sustituyen una actualización local.

No exigir persistencia de datos sensibles o efímeros cuando borrarlos sea una decisión de seguridad o privacidad declarada.

## 13. Evaluador 12 — Finalización y costuras

**Misión:** localizar señales de implementación parcial que impiden que el producto se perciba como una unidad terminada.

Recorrer los flujos completos buscando botones muertos, enlaces sin salida, texto provisional, datos falsos, estilos o iconos discordantes, elementos inestables, animaciones cortadas, formularios sin capacidades esperadas, contenido real que rompe componentes, errores de consola y funciones a medias. Revisar transiciones entre módulos y no solo cada pantalla aislada.

No convertir preferencias menores en defectos. Priorizar costuras reproducibles que dañan confianza, comprensión o conclusión del trabajo.
