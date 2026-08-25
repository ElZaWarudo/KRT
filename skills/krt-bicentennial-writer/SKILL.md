---
name: krt-bicentennial-writer
description: Writing and editing guidance for natural, specific, contextual prose that avoids generic patterns associated with AI-generated writing. Use when the user asks to draft, rewrite, humanize, naturalize, polish, localize, or audit text so it sounds less formulaic; when working on theses, academic articles, research documents, academic reasoning, critical argument, or AI-assisted authorship; or when they mention "sounds like AI," "AI detector," "humanize text," "natural writing," "human tone," "AI writing tells," "Bicentennial Writer," "suena a IA," "detector de IA," "humanizar texto," "redacción natural," or "tono humano," or want to avoid typical AI-writing patterns in Spanish or English. Runtime aliases may expose this as krt:bicentennial-writer.
---

# Bicentennial Writer

Bicentennial Writer helps draft or revise prose so it sounds concrete, situated, and written by someone with a real purpose. The goal is editorial quality, not evading detectors or misrepresenting authorship.

## Load References

- Load `references/patrones-y-antidotos.md` when auditing or rewriting text for common AI-writing tells.
- Load `references/base-investigacion.md` when the user asks for the rationale behind the approach, requests a review of the skill, wants to discuss AI detectors, or is working on academic authorship involving AI.
- Do not load extra references for short drafts when the user has already supplied the audience, purpose, and tone.

## Workflow

### Step 1 - Define the Assignment

Before writing, identify:

- audience;
- channel and format;
- purpose of the text;
- relationship between writer and reader;
- constraints on length, register, language, country, or sector;
- facts that must remain unchanged.

If the user provides little context and the risk is low, make reasonable assumptions and state them briefly. Ask only when missing context would change the voice, factual content, or risk of the text.

### Step 2 - Separate Quality from Camouflage

Treat “avoid sounding like AI” as an editorial-quality problem:

- make the text more specific;
- reduce filler and generic praise;
- vary rhythm only when it serves the meaning;
- preserve factual accuracy;
- keep the author's real constraints and voice.

Do not guarantee that a detector will classify the text as human-written. Do not help misrepresent authorship when a rule, institution, client, or publication requires disclosure of AI use.

When the context has authorship, academic-assessment, or publication rules, prioritize transparency and process: the author's own notes, sources, versions, editorial decisions, and disclosure of AI use when applicable.

### Step 3 - Diagnose the Tells

For existing text, look for:

- openings that say too much before contributing anything useful;
- symmetrical structures repeated paragraph after paragraph;
- inflated adjectives unsupported by evidence;
- transitions that announce the logic instead of creating it;
- conclusions that summarize instead of ending on an idea;
- examples that could apply to any person, company, country, or product;
- overly polished neutrality where a real author would take a position.

For long text, return a short diagnosis before rewriting. Name the two or three most damaging patterns instead of listing every flaw.

Do not automatically treat formal, concise, second-language, or neurodivergent writing as “suspicious.” Those styles can appear regular without being AI-generated.

### Step 4 - Build a Plausible Voice

Infer or request a voice profile:

- **stance:** direct, cautious, skeptical, warm, technical, commercial, reflective;
- **texture:** plain, sharp, conversational, formal, editorial, practical;
- **evidence style:** examples, numbers, lived details, citations, tradeoffs, anecdotes;
- **risk level:** safe corporate prose, personal essay, sales copy, academic, legal-adjacent.

Prefer signs of voice that arise from choices and details, not fake imperfections. Do not add typos, slang, personal memories, or emotional claims unless the user supplies or approves them.

When authenticity matters, ask for or use the author's raw material: rough notes, real examples, constraints, a specific opinion, a short voice sample, or the reason they are writing.

### Step 5 - Strengthen Academic Reasoning

When the assignment is a thesis, article, theoretical framework, literature review, proposal, report, or research document, prioritize verifiable thinking over superficial fluency:

- formulate a question, problem, or tension capable of sustaining the text;
- distinguish description, analysis, interpretation, and the author's own position;
- connect objectives, method, evidence, results, and conclusions without logical gaps;
- compare authors, theories, contexts, or data instead of chaining summaries;
- name limitations, assumptions, selection criteria, and reasonable alternatives;
- turn broad claims into inferences supported by sources, data, or methodological decisions;
- request or preserve the researcher's raw material: notes, readings, field decisions, findings, doubts, corpus, data, or criteria.

When building research documents:

- do not write as if a thesis has already been proven when data or sources are missing;
- use citations and references only when supplied by the user or independently verifiable;
- mark evidence gaps as pending instead of covering them with polished prose;
- keep the academic voice precise without making it impersonal by default;
- help keep human authorship traceable through decisions, versions, notes, methodological justification, and disclosure of AI use when applicable.

If the user asks for “human-level” writing, translate that request into intellectual quality: specificity, judgment, argumentative tension, command of the subject, and responsibility for sources. Do not treat it as camouflage from detectors.

### Step 6 - Draft or Rewrite

Apply these moves:

- start closer to the point;
- replace generic claims with consequences, examples, constraints, or concrete implications;
- cut filler openings such as “in today's world” or “it is important to note”;
- keep one idea per paragraph unless the genre rewards density;
- use transitions that carry meaning, not decorative connectors;
- let some sentences stay short when the point deserves emphasis;
- choose verbs over abstract nouns;
- keep terminology consistent in professional or technical contexts.

When rewriting user text, preserve its meaning by default. If the original is weak because the idea itself is vague, identify the missing substance instead of hiding it with style.

### Step 7 - Deliver with Judgment

Return the revised text first when the user asked for a rewrite. Add a compact note only when it helps:

```text
Key changes:
- <what changed>
- <what to customize if the user wants a stronger personal voice>
```

When drafting from scratch, include only the final draft unless assumptions, factual gaps, or useful alternatives should be shown.

## Output Modes

- **Light edit:** preserve the structure while correcting stiffness and filler.
- **Natural rewrite:** rebuild the flow without losing the intent.
- **Editorial diagnosis:** identify AI-like patterns without rewriting everything.
- **Academic construction:** propose a problem, thesis, structure, argument, evidence gaps, and reasoning improvements for research documents.
- **Tone variants:** provide two or three versions with different voice profiles.
- **Change list:** explain what changed and why; useful for collaborative writing.

## Guardrails

- Do not invent biographical details, client results, metrics, quotations, or lived experiences.
- Do not add deliberate errors as a “humanization” trick.
- Do not turn all text into casual prose; formal writing can also sound natural.
- Do not overplay an extravagant, cynical, or excessively colloquial voice.
- Do not remove necessary legal, academic, medical, or technical precision merely because it sounds formal.
- Do not present a rewrite as a reliable way to beat detectors; detectors are fallible and changeable.
- Do not fabricate sources, data, results, the researcher's views, or field experience to create the appearance of human reasoning.
- Keep the author's agency visible: flag places where a stronger point of view requires a real decision from the user.
