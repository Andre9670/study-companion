---
name: study-plan
description: Start a new subject and build a dated study plan. Sets up the subject folder, optionally ingests the learner's own material (grounded mode) into a searchable manifest, defines topics and acceptance criteria, and seeds the first set of quiz items. Use when the learner says "I want to study X", "prepare me for [exam] by [date]", "set up a new subject", or points you at study material.
---

# Study plan — start a subject

## 1. Scope it (ask, briefly)

- Subject + goal (understand / pass an exam / interview prep). Deadline, if any.
- **Material?** If they have files/a folder → **grounded mode**. If not → **open mode**.
- Rough starting level (beginner / refresher).

## 2. Create the subject folder

Root = `${STUDY_HOME:-~/.claude/study-companion}`. Slugify the subject → `<root>/<slug>/`.
Create: `corpus/ state/ artifacts/` and empty `notes.md`, `keywords.md`, `learner-profile.md`, `plan.md`.
Initialize the scheduler:
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sm2.py init --state <slug>/state/items.json
```

## 3. Ingest material (grounded mode only) — RAG-lite, no vector DB

Copy/point sources into `corpus/`. Build `index.md` as a **section manifest** so retrieval is
just grep+Read (Claude Code's Read/Grep *is* the retriever — no embeddings needed for normal sizes):

```
# Index — <subject>
- corpus/<file> › <heading>  (lines A–B) — <one-line summary>   [topic: <t>]
...
```
At quiz/explain time, grep `index.md` for the topic, then Read the cited line range and
answer *from it*, citing `file › heading`. Only consider embeddings if the corpus exceeds a
few hundred KB and grep stops being enough.

## 3b. Source policy (record it in `plan.md` — critical for open mode)

When you fill gaps from public knowledge, sources are not equal. Ask the learner for a
**source policy** and write it at the top of `plan.md`; obey it whenever you search or answer:

- **Freshness** — prefer the most *recent* official version. Guidance is often revised
  (e.g. a 2025/2026 guide can change vs. earlier editions); flag when a topic has a newer version.
- **Geography / authority ranking** — for a regional/national exam, rank sources: local/regional
  official → national official → European → other. Prefer the exam's own jurisdiction; explicitly
  **exclude** sources the learner rules out (e.g. "not US guidance on this clinical topic").
- **Primary over secondary** — the official convocatoria / temario / regulation beats summaries.

Example policy line: *"Prefer Galician (Xunta/SERGAS) 2025–2026 official docs → then Spanish →
then European; exclude US clinical guidance; official convocatoria is the source of truth for scope."*

## 4. Define topics + acceptance criteria → `plan.md`

- Break the subject into 5–12 topics. For an exam, mirror the official domains/weights.
- Write dated sessions (topics × days) up to the deadline (reuse a 7-day shape if short).
- **Acceptance criteria** — make "done" measurable, e.g.:
  - Every topic reaches mastery ≥ 0.8 at `apply` Bloom level.
  - No item overdue > 3 days.
  - Weak-area cheat sheet generated and reviewed once.

## 5. Seed initial items

Generate the first batch of atomic Q/A items across topics (start mostly at `recall`,
a few `understand`) and add them with `sm2.py add` (see the `quiz` skill). In grounded mode,
draw only from the corpus and keep the source ref.

Then hand to `quiz` to begin, and update `learner-profile.md` (via `notebook`) with the goal,
deadline, and starting level.
