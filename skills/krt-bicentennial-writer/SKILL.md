---
name: krt-bicentennial-writer
description: Guia de redaccion y revision para escribir textos naturales, especificos y contextuales, evitando patrones genericos asociados a escritura producida por IA. Usar cuando el usuario pida redactar, reescribir, humanizar, naturalizar, pulir, localizar o auditar texto para que suene menos formulaico; cuando trabaje tesis, articulos academicos, documentos de investigacion, razonamiento academico, postura critica o autoria asistida por IA; cuando mencione "suena a IA", "detector de IA", "humanizar texto", "redaccion natural", "tono humano", "AI writing tells", "Bicentennial Writer", or avoiding typical AI writing patterns in Spanish or English. Runtime aliases may expose this as krt:bicentennial-writer.
---

# Bicentennial Writer

Bicentennial Writer ayuda a redactar o revisar textos para que suenen concretos, situados y propios de una persona con una intencion real. El objetivo es mejorar la calidad editorial, no prometer evasion de detectores ni falsificar autoria.

## Load References

- Cargar `references/patrones-y-antidotos.md` al auditar o reescribir texto por tics comunes de IA.
- Cargar `references/base-investigacion.md` cuando el usuario pida justificar el enfoque, revisar la skill, discutir detectores de IA o trabajar autoria academica con IA.
- No cargar referencias extra para borradores cortos donde el usuario ya da audiencia, proposito y tono.

## Workflow

### Step 1 - Fijar El Encargo

Antes de escribir, identificar:

- audiencia;
- canal y formato;
- objetivo del texto;
- relacion entre emisor y lector;
- restricciones de longitud, registro, idioma, pais o sector;
- hechos que deben permanecer intactos.

Si el usuario da poco contexto y el riesgo es bajo, asumir lo razonable y declararlo brevemente. Preguntar solo cuando el contexto ausente cambie la voz, el contenido factual o el riesgo del texto.

### Step 2 - Separar Calidad De Camuflaje

Tratar "evitar que suene a IA" como un problema de calidad editorial:

- hacer el texto mas especifico;
- reducir relleno y elogio generico;
- variar el ritmo solo cuando sirva al sentido;
- preservar precision factual;
- mantener las restricciones y la voz real del autor.

No garantizar que un detector clasificara el texto como humano. No ayudar a tergiversar autoria cuando una regla, institucion, cliente o publicacion exige declarar uso de IA.

Cuando el contexto tenga normas de autoria, evaluacion academica o publicacion, priorizar transparencia y proceso: notas propias, fuentes, versiones, decisiones editoriales y declaracion de uso de IA cuando aplique.

### Step 3 - Diagnosticar Los Tics

Para texto existente, buscar:

- aperturas que dicen demasiado antes de aportar algo util;
- estructuras simetricas repetidas parrafo tras parrafo;
- adjetivos inflados sin evidencia;
- transiciones que anuncian la logica en vez de crearla;
- conclusiones que resumen en vez de cerrar con una idea;
- ejemplos que podrian aplicar a cualquier persona, empresa, pais o producto;
- neutralidad demasiado pulida donde un autor real tomaria posicion.

Cuando el texto sea largo, devolver un diagnostico corto antes de reescribir. Nombrar los dos o tres patrones mas daninos en vez de listar cada defecto.

No tratar automaticamente la escritura formal, concisa, de aprendices de una segunda lengua o de personas neurodivergentes como "sospechosa". Esos estilos pueden parecer regulares sin ser generados por IA.

### Step 4 - Construir Una Voz Plausible

Inferir o pedir un perfil de voz:

- **stance:** direct, cautious, skeptical, warm, technical, commercial, reflective;
- **texture:** plain, sharp, conversational, formal, editorial, practical;
- **evidence style:** examples, numbers, lived details, citations, tradeoffs, anecdotes;
- **risk level:** safe corporate prose, personal essay, sales copy, academic, legal-adjacent.

Preferir marcas de voz que surjan de elecciones y detalles, no de imperfecciones falsas. No anadir erratas, jerga, recuerdos personales ni afirmaciones emocionales salvo que el usuario las aporte o apruebe.

Si la autenticidad importa, pedir o usar materia prima del autor: notas desordenadas, ejemplos reales, restricciones, una opinion concreta, una muestra breve de voz o el motivo por el que escribe.

### Step 5 - Elevar Razonamiento Academico

Cuando el encargo sea una tesis, articulo, marco teorico, estado del arte, propuesta, informe o documento de investigacion, priorizar pensamiento verificable antes que fluidez superficial:

- formular una pregunta, problema o tension que pueda sostener el texto;
- distinguir descripcion, analisis, interpretacion y postura propia;
- conectar objetivos, metodo, evidencia, resultados y conclusiones sin saltos logicos;
- contrastar autores, teorias, contextos o datos en vez de encadenar resumenes;
- nombrar limites, supuestos, criterios de seleccion y alternativas razonables;
- convertir afirmaciones generales en inferencias apoyadas por fuentes, datos o decisiones metodologicas;
- pedir o conservar materia prima del investigador: notas, lecturas, decisiones de campo, hallazgos, dudas, corpus, datos o criterios.

Para construir documentos de investigacion:

- no redactar como si la tesis ya estuviera demostrada si faltan datos o fuentes;
- usar citas y referencias solo cuando el usuario las aporte o puedan verificarse;
- marcar huecos de evidencia como pendientes, no cubrirlos con prosa elegante;
- mantener la voz academica precisa sin hacerla impersonal por defecto;
- ayudar a que la autoria humana quede trazable: decisiones, versiones, notas, justificacion metodologica y declaracion de uso de IA cuando aplique.

Si el usuario pide "nivel humano", traducirlo a calidad intelectual: especificidad, criterio, tension argumental, dominio del tema y responsabilidad sobre las fuentes. No tratarlo como camuflaje ante detectores.

### Step 6 - Redactar O Reescribir

Aplicar estos movimientos:

- empezar mas cerca del punto;
- sustituir afirmaciones genericas por consecuencias, ejemplos, restricciones o implicaciones concretas;
- cortar arranques de relleno como "en el mundo actual" o "es importante destacar";
- mantener una idea por parrafo salvo que el genero premie densidad;
- usar transiciones que lleven significado, no conectores decorativos;
- dejar que algunas frases sean cortas cuando el punto merezca enfasis;
- elegir verbos antes que sustantivos abstractos;
- mantener terminologia consistente en contextos profesionales o tecnicos.

Al reescribir texto del usuario, preservar el significado por defecto. Si el original es debil porque la idea es vaga, senalar la sustancia que falta en vez de ocultarla con estilo.

### Step 7 - Entregar Con Criterio

Devolver primero el texto revisado cuando el usuario haya pedido una reescritura. Anadir una nota compacta solo si aporta valor:

```text
Cambios clave:
- <what changed>
- <what to customize if the user wants a stronger personal voice>
```

Para redactar desde cero, incluir solo el borrador final salvo que haya supuestos, huecos factuales o variantes opcionales que convenga mostrar.

## Output Modes

- **Revision ligera:** preservar estructura, corregir rigidez y relleno.
- **Reescritura natural:** reconstruir flujo sin perder intencion.
- **Diagnostico editorial:** identificar patrones tipo IA sin reescribir todo.
- **Construccion academica:** proponer problema, tesis, estructura, hilo argumental, vacios de evidencia y mejoras de razonamiento para documentos de investigacion.
- **Variantes de tono:** dar 2-3 versiones con perfiles de voz distintos.
- **Lista de cambios:** explicar que se altero y por que, util para escritura colaborativa.

## Guardrails

- No inventar detalles biograficos, resultados de clientes, metricas, citas ni experiencias vividas.
- No anadir errores deliberados como truco de "humanizacion".
- No convertir todo texto en prosa casual; un texto formal tambien puede ser natural.
- No sobreactuar con una voz extravagante, cinica o excesivamente coloquial.
- No eliminar precision legal, academica, medica o tecnica necesaria solo porque suena formal.
- No presentar una reescritura como metodo fiable para superar detectores; los detectores son falibles y editables.
- No fabricar fuentes, datos, resultados, posturas del investigador ni experiencia de campo para dar apariencia de razonamiento humano.
- Mantener visible la agencia del autor: sugerir cuando un punto de vista mas fuerte requiera una decision real del usuario.
