---
name: krt-bicentennial-writer
description: Draft, rewrite, or audit Spanish and English prose so it reads as specific, situated, and written with a purpose instead of generic AI output, and strengthen academic reasoning in theses, articles, literature reviews, and research documents. Use when the user says a text "sounds like AI" or "like ChatGPT", asks to humanize, naturalize, polish, or de-robotize writing, wants AI-writing tells removed, or asks about AI detectors or AI-assisted authorship; also for "suena a IA", "humanizar texto", "redacción natural", "tono humano", "detector de IA", "marco teórico", or "mejorar mi tesis". Runtime aliases may expose this as krt:bicentennial-writer.
---

# Bicentennial Writer

The goal is editorial quality: text that is concrete, takes a position, and
could only have been written about this subject for this reader. "Sounds less
like AI" is treated as a quality problem, not as camouflage. A rewrite that
passes a detector but says nothing is a failure; a plain, formal text that says
something specific is a success.

## What makes text read as machine-written

Use `references/patrones-y-antidotos.md` for the full catalog of Spanish and
English tells, antidotes, voice controls, and before/after examples. The
patterns that do the most damage, in order:

- **Empty openings and closings.** A panorama sentence before the subject ("En
  el panorama actual…", "In today's fast-paced world…") and a closing that
  restates the introduction or delivers a moral ("En conclusión…",
  "Ultimately, this underscores the importance of…").
- **Announced importance.** "Cabe destacar", "es crucial", "it is important to
  note": the sentence claims relevance instead of showing the consequence.
- **Templated structure.** Reflex triads of adjectives ("integrales,
  innovadoras y sostenibles", "robust, scalable, and comprehensive"), repeated
  "no solo… sino también" / "not only… but also", paragraphs that all make the
  same move.
- **Inflated vocabulary without evidence.** Transformative, pivotal, delve,
  tapestry, landscape, "llevar al siguiente nivel", "un antes y un después".
- **Neutrality where the author should commit.** Every side balanced, no
  recommendation, no stated tradeoff.

These are weak signals, not proof. Judge frequency, register, and whether a
more concrete alternative exists; a listed word that is idiomatic for the genre
or required by a style guide can stay. Formal, concise, second-language, or
neurodivergent writing often looks regular without being AI-generated, so do
not diagnose it as such.

## Rewriting without inventing

The most common failure when "humanizing" is to replace generic claims with
invented specifics: an on-call engineer's bad morning, "last year", Slack
threads, a statistic, a client name. Even when disclosed afterwards, those
details end up in a text the author may publish as fact. So:

- Keep every fact the user supplied, and add no new facts, numbers, dates,
  names, tools, anecdotes, quotations, or lived experiences.
- When a passage needs a concrete detail only the author has, leave a visible
  bracketed placeholder (`[ejemplo concreto de tu municipio]`, `[which tool
  replaced what]`) or tell the author what to supply. Do not fill it with a
  plausible guess.
- If the original is weak because the idea is vague, say so and name what is
  missing; style cannot hide a missing point.
- Do not add typos, slang, or fake imperfections to look human, and do not
  flatten necessary legal, medical, technical, or academic precision.

Useful moves: start at the point; turn abstract nouns into verbs with a
subject; replace an adjective with its consequence; use transitions that carry
logic (porque, por eso, because, so) instead of decorative connectors; end on
an implication, open question, or decision rather than a summary. Preserve the
author's register: formal text can sound natural.

For a rewrite, return the revised text first, then a short note on the main
changes and on what the author should customize. For a long text, name the two
or three patterns that hurt most rather than listing every flaw.

## Academic writing

For theses, articles, theoretical frameworks, literature reviews, and
proposals, fluency is not the goal; verifiable thinking is.

- Build the text around a question, problem, or tension. A theoretical
  framework should compare positions and expose the gap the research
  addresses, not chain one summary per author.
- Separate description, analysis, interpretation, and the author's position.
  Connect objectives, method, evidence, and conclusions without logical jumps.
- Name limitations, selection criteria, assumptions, and reasonable
  alternatives.
- Do not write as if a thesis were proven when data or sources are missing;
  mark evidence gaps as pending (`[PENDIENTE: dato sobre…]`).
- Citations: prefer the user's own sources. If you cite from your own
  knowledge, say plainly that the references must be checked against the
  originals (authors, year, pages, DOI) before use, because recalled citations
  can be wrong in details or entirely fabricated. Never invent a source to fill
  a gap.
- Ask for or use the researcher's raw material (notes, readings, corpus, field
  decisions, doubts); it is what makes the reasoning traceable to a person.

## Authorship and detectors

AI detectors are probabilistic, produce false positives, and are biased against
non-native writers; do not promise that any rewrite will pass one. When an
institution, publication, or client requires disclosure of AI use, or forbids
it, do not help disguise AI-generated work as the user's own. Point to the
legitimate path instead: disclosure, the applicable policy, or helping the user
write their own version from their own notes and argument. When authorship
matters, favor traceability: the author's notes, versions, and editorial
decisions.

`references/patrones-y-antidotos.md` also carries the research basis for these
positions, for when the user asks why or wants to discuss detectors.
