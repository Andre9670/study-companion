---
name: notebook
description: The tutor's self-maintained study notebook. Writes and refines theory notes, a keyword/association bank, and a learner profile that captures strengths, weak spots, recurring misconceptions, pace, and confidence gaps — so the tutor gets smarter about the learner every session. Use continuously during a session (especially after explaining something or spotting an error pattern), not just at the end.
---

# Notebook — write things down (so the tutor remembers)

The tutor keeps its own notes. Update these files with the Write/Edit tools throughout a
session — they are what make the tutor adaptive *across* sessions. Keep them tight and
append/refine rather than rewrite from scratch.

Subject dir = `${STUDY_HOME:-~/.claude/study-companion}/<subject-slug>/`.

## `notes.md` — theory notes

Fold every explanation you give (especially on a miss) into durable notes so you never
re-derive from zero. Organize by topic; use tables/ASCII diagrams for dual coding.
```
## <topic>
- <concept>: <crisp explanation>   (source: file › heading, if grounded)
- Common trap: <the misconception + the correction>
```

## `keywords.md` — key terms + associations

Every keyword you coin during quizzing lands here. Each entry = term → plain meaning →
an **association/mnemonic** that anchors it (link to prior knowledge, imagery, acronym).
These double as flashcard fronts/backs later.
```
- **<term>** — <meaning>. 🔗 <association/mnemonic>   [topic: <t>]
```

## `learner-profile.md` — what you know about THIS learner

The most important file for adaptivity. Update whenever you observe something:
```
# Learner profile — <subject>
Goal / deadline / starting level: ...
Updated: <date>

## Strengths (mastered / clicks fast)
- <topic/concept> — <evidence>

## Weak spots (re-drill)
- <topic/concept> — <the specific misconception>, seen <n>×

## Confidence gaps (sure but wrong = high value)
- <item/topic> — was "high" confidence, missed on <date>

## Pace & preferences
- <e.g. "prefers worked examples", "fades after ~20 min", "responds to analogies">
```

## Rules

- **Write during the session**, not only at the end — an insight not written is lost
  (same lesson as the tracking hooks: a step that depends on remembering later gets skipped).
- Content only — never touch `state/items.json` schedule fields here (that's `sm2.py`'s job).
- On session resume, the tutor reads these first. Keep them current so that read is worth it.
