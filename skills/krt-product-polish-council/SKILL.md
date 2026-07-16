---
name: krt-product-polish-council
description: Orquesta una auditoría integral y basada en evidencia del pulido de aplicaciones web, móviles y de escritorio mediante un atlas versionable, un cartógrafo y doce evaluadores especializados en alcance, coherencia, feedback, estados no ideales, protección, jerarquía, contenido, rendimiento percibido, convenciones de plataforma, accesibilidad, continuidad y finalización. Usar cuando se pida pulir una aplicación, evaluar su madurez de producto, recorrer flujos de extremo a extremo, detectar costuras o comportamiento amateur, producir un backlog priorizado de mejoras o verificar que una ronda de cambios elevó la calidad percibida.
---

# krt-product-polish-council

Evaluar la aplicación como un sistema de comportamiento, no como una colección de pantallas. Tratar la calidad percibida como una relación casi multiplicativa entre coherencia, fiabilidad, claridad, respuesta y cuidado: una dimensión muy débil limita el conjunto aunque el promedio sea alto.

## Principios de operación

- Usar `docs/product/application-atlas.md` como contexto compartido y versionable, salvo que el repositorio ya tenga una convención equivalente.
- Separar intención declarada, comportamiento observado e inferencias. No convertir una inferencia en requisito ni en defecto.
- Auditar flujos reales de extremo a extremo. Usar capturas como evidencia parcial, nunca como sustituto automático del comportamiento.
- Hacer que los doce evaluadores trabajen en modo de solo lectura y con el mismo paquete de evidencia.
- Reservar al agente líder la síntesis, deduplicación, priorización y decisión sobre cobertura.
- Tratar una solicitud de revisión como auditoría, no como autorización para cambiar código. Implementar solo cuando el usuario lo pida.

## Elegir el modo

- **Atlas**: crear, actualizar o validar únicamente el atlas versionable.
- **Auditoría**: construir o validar el atlas, ejecutar el consejo y entregar diagnóstico y backlog. Modo predeterminado.
- **Auditoría y corrección**: completar primero la auditoría; después implementar cambios autorizados y verificarlos.
- **Regresión de pulido**: comparar una versión nueva con un atlas y una auditoría anteriores, actualizar evidencia y reabrir solo los hallazgos afectados.

## Cargar referencias

- Leer `references/application-atlas.md` antes de comprobar, crear o actualizar el atlas.
- Leer `references/evaluator-catalog.md` antes de despachar o ejecutar cualquiera de los doce roles.
- Leer `references/evidence-and-report-protocol.md` antes de calificar hallazgos o sintetizar el informe.

## Flujo de trabajo

### 1. Verificar la frescura del atlas

Hacer de esta comprobación el primer paso de toda invocación:

1. Resolver la raíz del repositorio, el `HEAD` actual y la ruta del atlas.
2. Si el atlas no existe, marcarlo como `missing` y pasar a la entrevista de intención.
3. Si existe, ejecutar `scripts/check_atlas_freshness.py` desde esta skill contra `docs/product/application-atlas.md`.
4. Considerar el atlas `fresh` solo cuando el fingerprint de los archivos cubiertos coincide con el árbol del commit actual y no existen cambios relevantes sin confirmar.
5. Si el resultado es `stale`, actualizar el atlas antes de lanzar evaluadores. No confundir un atlas desactualizado con un defecto del producto.

Usar el SHA como procedencia y el fingerprint de los archivos cubiertos como autoridad de frescura. El propio atlas debe quedar fuera del fingerprint para evitar autorreferencia.

### 2. Resolver la intención del producto

Leer primero briefs, requisitos, decisiones, analítica disponible y documentación de producto. Si no responden las preguntas de intención definidas en `references/application-atlas.md`, hacer una única ronda compacta al responsable y esperar su respuesta.

No preguntar por hechos que puedan descubrirse en el repositorio o en la aplicación. Preguntar por propósito, usuario, resultado esperado, riesgos y límites deliberados. Si el usuario exige continuar sin responder, registrar hipótesis y reducir la confianza; no penalizar como fallo una discrepancia contra una intención no confirmada.

### 3. Construir o actualizar el atlas

Asignar al **Cartógrafo** la exploración factual de la aplicación. Inventariar plataformas, actores, roles, superficies, navegación, flujos, estados, datos, permisos, integraciones, acciones destructivas, condiciones reales y huecos de evidencia.

Mantener IDs estables como `ROLE-01`, `SURF-03`, `FLOW-07` y `STATE-12`. Actualizar por diff; no reordenar ni regenerar todo el archivo sin necesidad. No incluir conclusiones de calidad ni recomendaciones dentro del atlas.

No abrir el consejo hasta que pase la puerta de cobertura descrita en la referencia o los huecos queden explícitamente aceptados.

### 4. Preparar el paquete común de evidencia

Entregar a todos los evaluadores la misma instantánea:

- ruta y fingerprint del atlas;
- commit, entorno, plataforma, viewport y métodos de entrada examinados;
- flujos y roles dentro y fuera de alcance;
- credenciales o datos de prueba permitidos, sin copiar secretos;
- capturas, grabaciones, trazas, archivos y observaciones disponibles;
- restricciones para red, mutaciones, acciones destructivas y servicios externos;
- huecos y zonas no observadas.

No entregar a un evaluador los hallazgos de otro antes de que termine su pase; evitar anclaje y consenso artificial.

### 5. Ejecutar el consejo de doce evaluadores

Usar un agente independiente por dimensión cuando el runtime permita subagentes. Ejecutarlos en olas si hay menos de doce espacios. Mantenerlos en solo lectura y sin archivos compartidos mutables. Si no hay subagentes, ejecutar los doce contratos secuencialmente en el hilo principal sin omitir ninguno.

Cada evaluador debe:

1. Recorrer los flujos del atlas desde su lente exclusiva.
2. Contrastar camino ideal, transición, fallo y condición real cuando sean relevantes.
3. Citar evidencia exacta y etiquetarla como `observed`, `code`, `declared`, `inferred` o `unverified`.
4. Devolver calificación, confianza, hallazgos, aspectos que conviene conservar y huecos.
5. Proponer para cada hallazgo una corrección acotada y una comprobación observable.

### 6. Sintetizar sin diluir los puntos débiles

Aplicar el protocolo común. Asignar cada problema a una dimensión primaria y usar referencias cruzadas para las demás. Fusionar duplicados por causa y flujo, no por coincidencia de palabras.

No promediar las doce calificaciones para declarar éxito. Identificar el eslabón más débil, los fallos sistémicos y los flujos de mayor frecuencia o consecuencia. Priorizar operabilidad, pérdida de trabajo, confianza y recuperación antes que ornamentación.

Entregar un único informe coherente, no doce miniinformes yuxtapuestos.

### 7. Corregir y volver a verificar cuando esté autorizado

Convertir el backlog aceptado en unidades pequeñas con archivos, criterio de aceptación y prueba. Reutilizar las convenciones y componentes de la aplicación. Para una profundización opcional, usar `krt-frontend-ux-guardian` en UX funcional, `krt-interface-inquisitor` en composición visual o `krt-interaction-polisher` en respuesta temporal cuando estén disponibles; su ausencia no debe bloquear el flujo.

Después de cambiar rutas, roles, navegación, estados o flujos, actualizar el atlas y su fingerprint. Volver a ejecutar los evaluadores afectados y hacer un pase corto por las doce dimensiones para detectar regresiones cruzadas.

## Topología de agentes

- **Líder**: fija alcance, protege restricciones, acepta la puerta de cobertura y sintetiza.
- **Cartógrafo**: entrevista por intención cuando haga falta y mantiene el atlas factual.
- **Evaluadores 01-12**: aplican de forma independiente los contratos de `references/evaluator-catalog.md`.
- **Verificador**: en modo de corrección, reproduce criterios de aceptación sin reabrir decisiones de producto.

El Líder no debe delegar la síntesis final ni permitir que un evaluador implemente durante su pase diagnóstico.

## No negociables

- No inventar rutas, estados, roles, permisos, datos ni comportamiento que no se haya observado o declarado.
- No calificar como fallo una zona no accesible; marcarla `unverified` y explicar qué falta.
- No probar acciones destructivas, financieras, externas o sobre producción sin autorización y datos seguros.
- No ocultar el eslabón débil con un promedio, una puntuación estética o una lista larga de mejoras menores.
- No recomendar funcionalidades nuevas cuando una corrección de claridad, consistencia, feedback o recuperación resuelve el problema.
- No aceptar un hallazgo sin evidencia, efecto sobre el usuario, corrección concreta y verificación observable.
- No declarar la aplicación pulida si el atlas está ausente, desactualizado o materialmente incompleto.
