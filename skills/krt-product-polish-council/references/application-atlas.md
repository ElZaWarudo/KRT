# Atlas versionable de la aplicación

## Contenido

1. Propósito y autoridad
2. Preflight de frescura
3. Entrevista de intención
4. Procedimiento del Cartógrafo
5. Esquema del archivo
6. Puerta de cobertura
7. Estrategia según tamaño
8. Mantenimiento

## 1. Propósito y autoridad

Crear un mapa factual y compartido de lo que la aplicación pretende hacer y de lo que realmente expone. Guardarlo por defecto en `docs/product/application-atlas.md`.

Separar siempre:

- **Declared**: intención confirmada por una fuente con autoridad.
- **Observed**: comportamiento reproducido en la aplicación o demostrado por evidencia directa.
- **Code**: capacidad o ruta presente en código/configuración, aunque no se haya reproducido.
- **Inferred**: hipótesis útil pendiente de confirmación.
- **Unverified**: zona conocida que no pudo examinarse.

El atlas no es un informe de auditoría. No incluir calificativos como “malo”, severidades ni recomendaciones. Registrar diferencias entre intención y observación como hechos neutrales; el consejo decidirá después si constituyen un hallazgo.

## 2. Preflight de frescura

El primer acto al usar la skill es comprobar el atlas contra el commit actual.

El frontmatter conserva:

- `verified_source_commit`: commit presente al realizar la última exploración completa;
- `application_fingerprint`: SHA-256 del listado de objetos Git cubiertos en el commit;
- `tracked_paths`: rutas cuyo cambio puede volver obsoleto el atlas;
- `excluded_paths`: artefactos que no describen la aplicación, incluido el propio atlas;
- `last_verified_at`: fecha ISO de la última verificación sustantiva.

Ejecutar:

```bash
rtk python3 <skill-path>/scripts/check_atlas_freshness.py \
  --atlas docs/product/application-atlas.md
```

Interpretar:

- `fresh`: el contenido cubierto coincide con `HEAD` y no hay cambios relevantes sin confirmar;
- `stale`: cambió al menos un archivo cubierto o el working tree contiene cambios relevantes;
- `missing`: no existe el atlas;
- `invalid`: faltan metadatos o el esquema no se puede leer.

No exigir que `verified_source_commit` sea idéntico a `HEAD`: un commit que añade el propio atlas cambiaría el SHA y crearía una autorreferencia imposible. Exigir en su lugar que el fingerprint del árbol cubierto coincida. Usar el commit como procedencia y el fingerprint como prueba.

Para obtener el fingerprint que debe copiarse al atlas después de una exploración sobre un commit limpio:

```bash
rtk python3 <skill-path>/scripts/check_atlas_freshness.py \
  --atlas docs/product/application-atlas.md \
  --compute
```

## 3. Entrevista de intención

Revisar antes los documentos existentes. Preguntar solo lo que siga sin respuesta: omitir por completo cada dato ya declarado y reformular preguntas compuestas para no pedirlo de nuevo. Hacer una única ronda, mantenerla corta y esperar antes de fijar la intención declarada.

Preguntas base:

1. ¿Quién es el usuario principal y qué problema viene a resolver?
2. ¿Qué tarea debe poder completar con confianza en una sesión normal?
3. ¿Cuál es la acción principal y qué señal confirma que terminó bien?
4. ¿Qué roles, plataformas o contextos de uso siguen sin documentar y están realmente soportados?
5. ¿Qué errores o resultados serían inaceptables: pérdida de trabajo, exposición, cobro, publicación, bloqueo u otros?
6. ¿Qué límites, ausencias o fricciones son deliberados y no deben interpretarse como defectos?
7. ¿Qué flujos son más frecuentes, valiosos o críticos para el negocio y para el usuario?

Registrar cada respuesta con fuente y fecha. Si dos fuentes autorizadas se contradicen, no resolverlo por intuición: anotar el conflicto y pedir decisión.

Si el usuario pide continuar sin responder, registrar las respuestas provisionales como `Inferred`. No usar esas inferencias para emitir P0/P1 por falta de alineación de producto.

## 4. Procedimiento del Cartógrafo

Explorar de ancho a profundidad:

1. Inventariar plataformas, puntos de entrada, rutas, ventanas, pestañas y superficies principales.
2. Identificar actores, roles, permisos, estados de sesión y diferencias por plan o tenant.
3. Recorrer navegación global y local; registrar entradas, salidas, retorno y enlaces profundos.
4. Definir los flujos importantes con precondiciones, acción principal, resultado, datos modificados y recuperación.
5. Catalogar por superficie los estados ideal, vacío, carga, progreso, éxito, validación, error, offline, permiso, sesión expirada, contenido extremo y volumen alto cuando apliquen.
6. Mapear persistencia: borradores, autoguardado, selección, filtros, scroll, historial y estado entre sesiones.
7. Registrar integraciones, trabajos asíncronos, archivos, notificaciones, pagos u otros límites externos.
8. Señalar acciones destructivas, irreversibles, financieras, públicas o sensibles sin ejecutarlas fuera de un entorno seguro.
9. Registrar convenciones de entrada y plataforma: teclado, táctil, lector de pantalla, back/forward, deep links, ventanas, archivos y responsive.
10. Mantener un ledger de cobertura con evidencia y huecos.

Preferir comportamiento reproducido en runtime. Usar rutas, componentes, pruebas y configuración para descubrir zonas ocultas; usar documentación para explicar intención. No copiar secretos ni datos personales al atlas.

## 5. Esquema del archivo

Usar esta estructura y conservar IDs entre versiones:

```markdown
---
atlas_schema_version: 1
status: "draft"
verified_source_commit: "<full-sha>"
application_fingerprint: "sha256:<digest>"
tracked_paths: ["app", "src", "config", "docs/product-requirements"]
excluded_paths: ["docs/product/application-atlas.md", "docs/audits/"]
last_verified_at: "YYYY-MM-DD"
---

# Application Atlas

## 1. Intent
- Product promise [Declared]:
- Primary user [Declared]:
- Primary job [Declared]:
- Primary action [Declared]:
- Success signal [Declared]:
- Deliberate constraints [Declared]:
- Unacceptable outcomes [Declared]:
- Sources:

## 2. Platforms and environments
| ID | Platform/environment | Supported | Inputs | Constraints | Evidence |

## 3. Actors and permissions
| ID | Actor/role | Goal | Can | Cannot | Evidence |

## 4. Surface and navigation map
| ID | Surface | Entry | Exits/return | Roles | Route/window | Evidence |

## 5. Flow registry
| ID | Flow | Actor | Frequency | Consequence | Entry | Completion | Surfaces | Evidence |

### FLOW-01 — <name>
- Preconditions:
- Before:
- During:
- After:
- Failure and recovery:
- Real conditions:
- Data written or exposed:
- Context that must survive:
- Evidence:

## 6. State catalog
| ID | Surface/flow | State | Expected behavior | Observed/code/unverified | Evidence |

## 7. Data and context lifecycle
| Data/context | Created | Persisted | Restored | Cleared | Risk | Evidence |

## 8. External and asynchronous boundaries
| Boundary | Trigger | Pending signal | Success | Failure/retry | Evidence |

## 9. Destructive and high-consequence actions
| Action | Consequence | Reversible | Protection | Safe test path | Evidence |

## 10. Content and scale envelopes
| Surface | Empty | Typical | Long/extreme | High volume | File/input limits | Evidence |

## 11. Platform, input and accessibility expectations
| Platform/flow | Keyboard | Touch | Focus | Back/deep link | Reduced motion | Assistive tech | Evidence |

## 12. Coverage ledger
| Item | Status | Evidence | Last checked | Gap/next probe |

## 13. Open intent questions and conflicts
- <question or conflict; source; owner>

## 14. Change log
- YYYY-MM-DD: <factual atlas change and reason>
```

Usar `status: "validated"` únicamente cuando pase la puerta de cobertura. Usar `status: "stale"` en cuanto se detecte un cambio relevante que aún no se haya cartografiado.

## 6. Puerta de cobertura

Abrir el consejo solo si:

- la promesa, el usuario, la tarea, la acción principal y la señal de éxito están declarados o marcados como hipótesis;
- todas las plataformas y roles conocidos tienen disposición;
- todas las superficies alcanzables dentro del alcance aparecen en el mapa;
- cada flujo principal o de alta consecuencia tiene entrada, final, datos, estados y recuperación;
- permisos, sesión, integraciones y acciones destructivas tienen cobertura o hueco explícito;
- existen muestras para vacío, carga, error, contenido extremo, volumen, viewport e input cuando aplican;
- el ledger distingue `covered`, `partial`, `unverified` y `out-of-scope`;
- el fingerprint corresponde al commit actual y no hay cambios relevantes sin confirmar.

Si falta evidencia, el Líder puede continuar solo con alcance reducido y debe declarar la limitación. Nunca presentar una muestra parcial como auditoría exhaustiva.

## 7. Estrategia según tamaño

- **Aplicación pequeña**: cubrir todas las superficies, roles y estados alcanzables.
- **Aplicación mediana**: cubrir todas las superficies; profundizar en todos los flujos principales y de alta consecuencia.
- **Aplicación grande**: inventariar toda la amplitud; profundizar por riesgo y representatividad, incluyendo al menos un flujo por rol, plataforma, patrón de interacción e integración crítica.

“Todos los recovecos” significa que cada zona conocida tiene una disposición de cobertura, no que se afirme haber ejecutado combinaciones imposibles o inaccesibles.

## 8. Mantenimiento

Actualizar el atlas en el mismo cambio que altere:

- rutas, navegación o superficies;
- roles, permisos o estados de sesión;
- inicio, resultado o recuperación de un flujo;
- persistencia, borradores o contexto conservado;
- integraciones o trabajos asíncronos;
- plataformas soportadas o convenciones de entrada;
- límites de datos, archivos o volumen;
- intención de producto o restricciones deliberadas.

Preservar IDs y filas no afectadas. Añadir una entrada breve al change log. Volver a calcular el fingerprint sobre un commit limpio y ejecutar el preflight antes de una nueva auditoría.
