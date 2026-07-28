# Revisión consolidada de la cartera KRT

Estado de la revisión: 2026-07-27

Rama revisada: `feat/skill-portfolio-corrections`

Base integrada: `origin/main` (`6da13b4`)

HEAD de partida: `001a4f9`; las correcciones descritas permanecen sin commit en
el working tree para revisión del usuario.

## Resultado ejecutivo

La cartera queda compuesta por 27 skills KRT con identidad canónica, metadata de
autocompletado y validación estructural correctas. Veinte se clasifican como
`safety_critical` y cargan un contrato de seguridad local indexado desde
`docs/safety.md`.

La revisión no se limitó a reescribir prompts. Se comprobaron los contratos
entre skills, los límites de autoridad, los efectos externos, la recuperación
tras interrupciones, los scripts deterministas, los tests y la correspondencia
entre lo que cada `SKILL.md` promete y lo que sus herramientas ejecutan.

Resultados verificables:

- 27 de 27 skills pasan `quick_validate.py`.
- 19 archivos de test, con 219 métodos `test_*`, terminan sin fallos.
- El corpus de Skill Arbiter contiene 12 casos estructuralmente válidos en seis
  categorías; este check no equivale a ejecutarlos contra modelos ni a un pass
  rate.
- El catálogo reconoce 27 skills y 20 skills críticas.
- `git diff --check` no detecta errores de whitespace en el diff tracked; los
  archivos nuevos se comprobaron además de forma explícita.
- La prueba de render real de Word queda pendiente en este host porque no están
  instalados LibreOffice, `pdftoppm` ni PyMuPDF. El preflight lo detecta y
  bloquea correctamente una falsa declaración de documento final.

## Criterios de revisión

La evaluación usó estas dimensiones:

1. Activación: descripción concreta, límites negativos y routing no ambiguo.
2. Divulgación progresiva: `SKILL.md` operativo y detalle reutilizable en
   `references/`, `scripts/`, `schemas/` o `assets/`.
3. Autoridad: lectura antes de mutación, aprobaciones explícitas y ausencia de
   permisos implícitos para push, merge, Jira, despliegue o borrado.
4. Determinismo: validadores y scripts para contratos comprobables, sin delegar
   invariantes críticas al juicio del modelo.
5. Reinicio y estado: artefactos versionables, esquemas y reconciliación cuando
   una operación puede quedar a medias.
6. Seguridad: secretos redactados, inputs no confiables, rutas y outputs
   acotados, y contratos locales para las skills críticas.
7. Evaluabilidad: casos positivos, negativos, routing, permisos, fallback,
   reinicio y resultado observable.
8. Simplicidad: eliminación de duplicación, referencias cargadas solo cuando
   son necesarias y separación clara entre orquestadores y especialistas.

## Base de investigación actual

Las decisiones se contrastaron con documentación vigente de diseño, seguridad
y evaluación de skills:

- OpenAI, [Build skills](https://learn.chatgpt.com/docs/build-skills) y
  [Agent approvals & security](https://learn.chatgpt.com/docs/agent-approvals-security).
- Agent Skills,
  [Specification](https://agentskills.io/specification),
  [Best practices for skill creators](https://agentskills.io/skill-creation/best-practices)
  y
  [Evaluating skill output quality](https://agentskills.io/skill-creation/evaluating-skills).
- Anthropic,
  [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview),
  [Skills for enterprise](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/enterprise),
  [Define success criteria and build evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
  y [Mitigate jailbreaks and prompt injections](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks).
- Agent Skills,
  [Adding skills support to your agent](https://agentskills.io/client-implementation/adding-skills-support),
  para colisiones, recarga, deduplicación y preservación tras compaction.
- Anthropic,
  [Permission policies](https://platform.claude.com/docs/en/managed-agents/permission-policies).
- OWASP,
  [LLM01:2025 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/).
- Microsoft,
  [Macros from the internet are blocked by default in Office](https://learn.microsoft.com/en-us/microsoft-365-apps/security/internet-macros-blocked).

El consenso respalda metadata concisa, `SKILL.md` operativo, carga progresiva,
scripts para invariantes mecánicas, evals con negativos, sandbox separado de
aprobaciones y contenido externo tratado como datos. También motivó clasificar
Document Forge como crítica: el texto convertido puede contener prompt
injection aunque la conversión técnica sea correcta.

## Cambios transversales aplicados

### Autoridad y efectos externos

- Se separaron planificación, autorización local y mutaciones remotas.
- Rebase, push, merge, comentarios, transiciones Jira y despliegues requieren
  una autoridad visible y específica.
- Los modos autónomos quedan ligados a un ledger versionado y a validadores
  deterministas; una etiqueta de autonomía no amplía permisos por sí sola.
- Jira Server/Data Center y Jira Cloud se resuelven por proveedor y entorno, sin
  imprimir tokens ni mezclar APIs.

### Evidencia y publicación

- Document Forge conserva fuentes y sidecars privados; no publica resúmenes
  directamente.
- Harness Wise promociona evidencia solo después de validación determinista y
  cribado de secretos.
- Los artefactos de staging, procedencia y render se mantienen separados de los
  entregables versionables.

### Gobernanza de la cartera

- Se creó `krt-skill-arbiter`, nombre KRT único que no reutiliza “forge”.
- Su catálogo comprueba identidad, metadata, wiring de seguridad y cobertura de
  las 27 carpetas `krt-*`.
- Su corpus versionado mide routing, negative triggers, permisos, reinicio,
  fallback y resultado, y mantiene `pass`, `fail` e `inconclusive` separados.

### Simplificación

- Compound Master coordina especialistas sin copiar sus procedimientos.
- Swarm Seneschal mantiene una autoridad documental y una cola acotada, pero no
  suplanta los gates de Compound Master o Release Marshal.
- Los helpers de Jira, evidencia y mutación reutilizan contratos pequeños en
  vez de ramas paralelas con reglas distintas.

## Matriz de las 27 skills

| Skill | Veredicto | Resultado de la revisión |
|---|---|---|
| `krt-bicentennial-writer` | Apta | Mantiene referencias editoriales progresivas y un scope textual sin efectos externos. |
| `krt-ci-questor` | Corregida | Carga explícitamente seguridad antes de consultar logs, credenciales o recomendar bypasses. |
| `krt-compound-master` | Corregida | Autoridad, ledger, roles, gates de revisión/seguridad/CI y handoff quedaron alineados sin duplicar especialistas. |
| `krt-delivery-navigator` | Corregida | Preflight y seguridad son obligatorios antes de producir planes que puedan derivar en ejecución. |
| `krt-deploy-summoner` | Corregida | Se distingue inspección de mutación y se carga el contrato de seguridad antes de operaciones de despliegue. |
| `krt-docs-chronicler` | Corregida | Seguridad y publicación evitan incorporar secretos o evidencia privada a documentación durable. |
| `krt-document-forge` | Corregida | Conversión, staging, procedencia privada y promoción quedan separados; documentos y texto extraído son evidencia no confiable, y la skill pasa a safety-critical. |
| `krt-frontend-ux-guardian` | Apta | Scope funcional, accesibilidad, responsive y verificación en navegador permanecen bien delimitados. |
| `krt-gitflow-knight` | Corregida | Guards de branch/commit y actualización segura de ignores locales reducen commits accidentales de credenciales. |
| `krt-harness-wise` | Corregida | Evidencia privada se valida y promociona mediante un gate determinista con comprobaciones de publicación. |
| `krt-interaction-polisher` | Apta | Se mantiene como especialista temporal/táctil, separado del diseño visual y del gate funcional. |
| `krt-interface-inquisitor` | Corregida | Metadata canónica y routing de crítica visual quedan alineados con el ID formal. |
| `krt-interface-warden` | Corregida | Metadata canónica y límites frente a Guardian/Inquisitor evitan solapamiento de responsabilidades. |
| `krt-jira-cloud-scribe` | Corregida | Preflight de entorno, redacción de token, contrato de autonomía y API Cloud v3 quedan explícitos. |
| `krt-jira-scribe` | Corregida | Preflight de entorno, redacción de token y routing Server/Data Center evitan usar el proveedor equivocado. |
| `krt-product-polish-council` | Corregida | Metadata canónica y especialistas opcionales preservan una auditoría integral sin bloquear por ausencias. |
| `krt-rebase-smith` | Corregida | Árbol limpio, rama/base explícitas, un gate de plan y autorización separada para push con lease. |
| `krt-release-marshal` | Corregida | Jira, commits, rebase, PR, reviewers y merge tienen autoridad y validadores separados; no heredan permisos ambiguos. |
| `krt-repo-medic` | Corregida | Diagnóstico de salud se conecta con Skill Arbiter para checks reproducibles sin convertirse en otro orquestador. |
| `krt-requirements-weaver` | Corregida | Safety preflight y evidencia mantienen la clarificación separada de planificación o implementación. |
| `krt-review-herald` | Corregida | Triage, aplicación de fixes y respuestas remotas distinguen lectura, cambios locales y mutaciones en GitHub. |
| `krt-roadmap-cartographer` | Corregida | Context gate, procedencia y safety preflight limitan el output a un único roadmap/readiness report. |
| `krt-security-sentinel` | Corregida | Threat model agentic, rubric y conexión con evaluaciones cubren inputs, secretos, permisos y efectos externos. |
| `krt-skill-arbiter` | Nueva | Añade catálogo determinista, corpus versionado, scoring supervisor-captured y wiring de seguridad. |
| `krt-state-archivist` | Corregida | Metadata y seguridad preservan historia completa sin convertir el archivo en autoridad ejecutiva. |
| `krt-swarm-seneschal` | Corregida | Cola, blockers, reconciliación y contrato de autoridad evitan que el swarm salte planes, gates o release ownership. |
| `krt-word-illuminator` | Corregida | Incorporada tras integrar `origin/main`; añade seguridad OOXML, QA ligada por hashes, privacidad estricta y routing frente a Document Forge. |

## Revisión específica de `krt-word-illuminator`

Word Illuminator era la skill ausente de la primera pasada porque llegó a
`origin/main` en una línea de historia paralela. Tras el rebase se revisaron
`SKILL.md`, metadata, referencias, schemas, template, librerías y los nueve
scripts originales.

Correcciones aplicadas:

- Preflight previo a `python-docx`, `zipfile` y LibreOffice.
- Límites configurables de miembros y tamaños ZIP, tamaño por miembro y ratio de
  compresión, más límites físicos y del directorio central antes de `ZipFile`;
  rechazo de cifrado, duplicados y traversal.
- Rechazo por defecto de macros, tipos MIME macro-enabled, ActiveX, OLE,
  embeddings y relaciones externas recuperables, incluidas formas XML
  codificadas; los hyperlinks pasivos se conservan como datos y no se abren.
- Render report ligado al SHA-256 del DOCX, PDF y cada PNG.
- Validación final que exige exactamente una imagen por página, cobertura
  completa, estado `passed`, hashes vigentes y cero bloqueantes abiertos.
- Edición de párrafo limitada a texto simple de un único run; los párrafos con
  formato, hyperlinks, campos, dibujos o referencias abortan en vez de perder
  semántica silenciosamente.
- `--final --privacy` convierte propiedades custom y posible PII en errores,
  salvo excepción explícita; inspecciona stories completas, alt text, notas,
  propiedades extendidas y metadata ZIP. Los reportes muestran campos y
  conteos, no autores ni valores originales.
- Inspección y comparación redactan contenido por defecto; `--include-content`
  queda como opt-in para artefactos de trabajo protegidos.
- Outputs no-clobber se publican atómicamente y rechazan componentes symlink;
  rutas embebidas en request/patch no pueden escapar de las raíces aprobadas.
- Cada consumidor abre el DOCX con `O_NOFOLLOW`, copia desde ese mismo
  descriptor a un snapshot privado, comprueba que no cambió durante la copia y
  consume solo la versión admitida; sustituir después la ruta original no altera
  lo inspeccionado, editado, comparado, scrubbed, validado o renderizado.
- Creación publica DOCX y sidecar como una transacción recuperable; el render
  prepara PDF, PNG e informe completos en staging y conserva la evidencia
  anterior si un overwrite autorizado falla. Solo reemplaza directorios con su
  marcador/manifiesto válido y rechaza entradas desconocidas para no borrar
  artefactos ajenos.
- LibreOffice usa perfil efímero y namespace sin red. Un preview explícitamente
  conectado puede generarse, pero su informe no supera validación final. Como
  un JSON editable no autentica su propia procedencia, el gate final exige
  reconocer explícitamente la afirmación de aislamiento y solo permite hacerlo
  cuando el agente controló directamente la ejecución y conservó la evidencia.
- El escaneo de privacidad cuenta comentarios y revisiones por namespace y
  local-name, incluidos prefijos XML alternativos, y rechaza partes sensibles
  renombradas mediante tipos de relación o contenido.
- Tras scrub se exige render, inspección y QA nuevos para esa variante.
- `check_runtime.py` comprueba dependencias sin instalarlas.
- Contrato `references/safety.md`, registro como `safety_critical` y routing
  inequívoco: Document Forge convierte fuentes a Markdown; Word Illuminator
  produce entregables DOCX.

## Evidencia de validación

Comandos principales:

```bash
rtk python3 skills/krt-word-illuminator/scripts/test_word_illuminator.py
rtk python3 skills/krt-word-illuminator/scripts/test_package_safety.py
rtk python3 skills/krt-word-illuminator/scripts/test_check_runtime.py
rtk python3 skills/krt-skill-arbiter/scripts/check_portfolio.py --repo-root .
rtk python3 skills/krt-skill-arbiter/scripts/check_corpus.py \
  skills/krt-skill-arbiter/references/cases.json \
  skills/krt-skill-arbiter/references/expectations.json \
  --skills-root skills
rtk git diff --check
```

Resultado:

| Check | Resultado |
|---|---|
| Suites Python | 19 archivos, 219 métodos de test, sin fallos |
| Word Illuminator | 30 workflow + 13 package safety + 2 runtime tests |
| Quick validation | 27/27 |
| Portfolio | 27 skills, 20 safety-critical |
| Corpus | 12 casos, seis categorías, estructura válida; no ejecutados contra modelos |
| Runtime de render real | Bloqueado correctamente por herramientas ausentes |

## Riesgo residual y siguiente ciclo

Tras corregir los dos P1 y el P2 encontrados en la última revisión adversarial,
no quedan defectos conocidos que justifiquen bloquear la cartera. Permanecen
limitaciones explícitas y mejoras para el siguiente ciclo:

1. Ejecutar periódicamente los 12 casos de Skill Arbiter con varios modelos y
   versiones, conservando resultados supervisor-captured por separado y
   registrando modelo, runtime, host, tokens, tiempo y repetición.
2. Añadir un baseline A/B contra la versión anterior o sin skill para medir
   mejora real, no solo cumplimiento absoluto.
3. Añadir CI con LibreOffice y un rasterizador para probar render DOCX real,
   además de los fixtures rápidos existentes.
4. Ejecutar LibreOffice en un sandbox sin red y con límites de CPU, memoria,
   procesos y tiempo definidos por el runtime.
5. Añadir al portfolio checker un presupuesto agregado de metadata: algunos
   hosts limitan el catálogo inicial al 2 % del contexto o 8.000 caracteres.
6. Probar colisiones y coexistencia de triggers entre ámbitos repo, usuario,
   plugin y sistema, no solo cada skill de forma aislada.
7. Añadir casos de runtime para actualización de una skill durante una sesión,
   instalación de plugin, cambios de permisos y expectativa de reinicio.
8. Ampliar el corpus cuando un incidente real revele una nueva clase de fallo;
   no aumentar casos solo para inflar cobertura.
9. Revisar trimestralmente descripciones y negative triggers a partir de
   confusiones de routing observadas, no por cambios cosméticos de tendencia.
10. Ejecutar cada evaluación en una sesión limpia, manteniendo constantes
    corpus, modelo y runtime al comparar versiones.
11. Ampliar el portfolio checker con indicadores declarados y observados de
    ejecución de código, red, MCP, credenciales y alcance de filesystem.

## Conclusión

La cartera ya no depende solo de instrucciones persuasivas. Sus zonas críticas
combinan contratos escritos, límites de autoridad, scripts deterministas,
fixtures negativos y checks de portfolio. La mejora más importante no es una
skill aislada, sino el bucle de mantenimiento: diagnosticar, corregir, evaluar y
volver a revisar con evidencia.
