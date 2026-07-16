# Protocolo de evidencia, calificación e informe

## Contenido

1. Etiquetas de evidencia
2. Calificación por dimensión
3. Severidad de hallazgos
4. Contrato de retorno del evaluador
5. Reglas de síntesis
6. Formato del informe final
7. Regresión después de corregir

## 1. Etiquetas de evidencia

- `observed`: reproducido directamente en runtime, grabación o artefacto equivalente.
- `code`: demostrado por código, configuración o prueba, pero no reproducido en runtime.
- `declared`: intención confirmada en el atlas con una fuente autorizada.
- `inferred`: conclusión razonable todavía no confirmada.
- `unverified`: condición o superficie conocida sin evidencia suficiente.

Preferir `observed` para comportamiento y `declared` para intención. El código no demuestra por sí solo que una interacción sea alcanzable o comprensible. Una inferencia nunca debe sostener por sí sola un P0 o P1.

## 2. Calificación por dimensión

Usar una escala corta y acompañarla siempre de confianza:

- **0 — Roto o ausente**: impide completar o comprender flujos materiales, o expone pérdida grave.
- **1 — Frágil**: funciona en el camino ideal, pero falla de forma frecuente, incoherente o difícil de recuperar.
- **2 — Sólido**: cubre el uso normal y los riesgos principales; conserva huecos concretos de calidad.
- **3 — Pulido**: resulta predecible, tolerante y consistente en los flujos y condiciones examinados.
- **NA — Sin evidencia/aplicación**: la dimensión o condición no aplica al alcance o no pudo verificarse.

Confianza:

- `high`: evidencia directa en todos los flujos materiales asignados;
- `medium`: evidencia directa parcial más código o documentación coherente;
- `low`: predominan inferencias, capturas aisladas o zonas inaccesibles.

No calcular una media global. Mostrar el perfil completo y destacar la calificación material más baja. Un `NA` no equivale a cero.

## 3. Severidad de hallazgos

- **P0 — Bloqueo o daño grave**: flujo principal imposible, pérdida/corrupción de trabajo, estado engañoso con consecuencia grave, inaccesibilidad total del flujo o acción irreversible sin control suficiente.
- **P1 — Fallo de confianza o recuperación**: alta probabilidad de error, repetición, desorientación, abandono o incapacidad de recuperarse en un flujo importante.
- **P2 — Fricción sistemática**: inconsistencia, lentitud percibida, ambigüedad o deuda de calidad que dificulta el uso pero conserva la tarea.
- **P3 — Costura o refinamiento**: defecto real de acabado con impacto limitado; oportunidad de pulido después de P0-P2.

Dentro de una severidad, ordenar por frecuencia, centralidad del flujo, número de roles/plataformas afectados y reversibilidad. Estimar esfuerzo `S`, `M` o `L` solo después de definir una corrección; no reducir severidad porque arreglar sea costoso.

## 4. Contrato de retorno del evaluador

Devolver YAML o Markdown estructurado con estos campos:

```text
evaluator: <NN — name>
dimension: <canonical dimension>
rating: <0|1|2|3|NA>
confidence: <high|medium|low>
coverage:
  flows: [FLOW-...]
  surfaces: [SURF-...]
  platforms: [PLAT-...]
  gaps: [<unverified item>]

findings:
- id: POL-<NN>-<sequence>
  severity: <P0|P1|P2|P3>
  title: <specific failure>
  evidence_type: <observed|code|declared|inferred|unverified>
  evidence: <exact behavior, location, condition and source>
  user_effect: <confidence, completion, speed, recovery or error impact>
  correction: <smallest concrete product/code/content change>
  verify: <observable acceptance check>
  affected: [FLOW-..., SURF-..., ROLE-..., platform]
  frequency: <frequent|occasional|rare|unknown>
  effort: <S|M|L|unknown>

keep:
- <successful behavior that should survive fixes>

unknowns:
- <missing evidence and exact next probe>

cross_refs:
- <dimension and evidence for another evaluator/lead>
```

Permitir `findings: []`. No inventar deuda para llenar el contrato.

## 5. Reglas de síntesis

1. Validar que cada hallazgo tiene evidencia, efecto, corrección y verificación.
2. Rechazar o degradar afirmaciones cuya evidencia no sostenga la severidad.
3. Asignar una dimensión primaria por causa; conservar dimensiones secundarias como referencias.
4. Fusionar hallazgos cuando comparten causa, flujo y criterio de corrección. Mantener separadas causas distintas aunque aparezcan en la misma pantalla.
5. Detectar patrones sistémicos: una misma convención rota en tres superficies vale más que tres tickets cosméticos aislados.
6. Identificar el eslabón más débil por severidad, centralidad y calificación; no por promedio.
7. Formar un backlog:
   - `Now`: P0/P1 y causas sistémicas que bloquean confianza o recuperación;
   - `Next`: P2 frecuentes o transversales;
   - `Later`: P3 y refinamientos acotados.
8. Conservar una lista `Keep` para evitar que la corrección destruya patrones que ya funcionan.
9. Separar deuda confirmada de huecos de verificación.

## 6. Formato del informe final

```text
# Product Polish Audit

## Verdict
<one paragraph: perceived maturity, weakest link and consequence>

## Scope and freshness
- Atlas: <path, status, fingerprint>
- Commit/environment:
- Flows, roles and platforms covered:
- Material gaps:

## Quality profile
| # | Dimension | Rating | Confidence | Strongest evidence | Main gap |

## Weakest links
1. <cause spanning findings/flows>
2. <cause>
3. <cause>

## Prioritized findings
### Now
- [P1] <finding with evidence, effect, correction and verify>
### Next
...
### Later
...

## Flow lifecycle matrix
| Flow | Before | During | After | Failure | Real conditions |

## Keep
- <working behavior to preserve>

## Verification gaps
- <unknown, why and exact next probe>

## Remediation slices
| Slice | Findings | Expected outcome | Effort | Acceptance checks |

## Handoff
<audit complete | implementation authorized | blocked by named evidence>
```

Mantener trazabilidad desde cada slice a IDs `POL-*`, `FLOW-*` y `SURF-*`. Evitar tablas gigantes: si el detalle es extenso, dejar el resumen en el informe y enlazar evidencia versionada.

## 7. Regresión después de corregir

1. Actualizar el atlas si cambió un elemento cartografiado.
2. Ejecutar el preflight de frescura.
3. Reproducir cada criterio `verify` de los hallazgos corregidos.
4. Reejecutar las dimensiones primarias y las referencias cruzadas afectadas.
5. Hacer un smoke pass por los doce evaluadores sobre el flujo modificado.
6. Marcar cada hallazgo `resolved`, `partially-resolved`, `not-reproduced` o `open` con evidencia nueva.
7. No elevar la calificación de una dimensión por un cambio de código que no se haya verificado en el comportamiento cuando el runtime esté disponible.
