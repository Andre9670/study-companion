---
name: progress
description: Review progress and close out a study session. Aggregates mastery by topic and Bloom level, surfaces the biggest weak areas and confidence-vs-correctness gaps, checks the plan's acceptance criteria, and can generate a targeted gap cheat sheet or an Anki-importable flashcard deck. Use at the end of a session, or when the learner asks "how am I doing", "what should I focus on", "make me a cheat sheet", or "export flashcards".
---

# Progress — review, weak areas, close-out

Subject dir = `${STUDY_HOME:-~/.claude/study-companion}/<subject-slug>/`.
Scheduler: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sm2.py`.

## 1. Mastery snapshot

Read state and history:
- `sm2.py show --state <subject>/state/items.json --json` → per-item mastery/due/reps.
- Aggregate mastery by **topic** and by **Bloom level** (mean mastery, # items, # overdue).
- Present a compact table: topic → mastery bar → due count. Highlight anything < 0.6.

## 2. Weak-area analysis (the actionable part)

- **Lowest-mastery topics/items** → these are the drill targets.
- **Confidence-vs-correctness gaps** — scan `quiz-history.jsonl` for attempts where
  `confidence` was high but `grade` < 3. These are the highest-value fixes (false confidence).
- **Recurring misconceptions** — cross-check `learner-profile.md` weak spots.

## 3. Acceptance criteria check

Compare against `plan.md`'s criteria (e.g. all topics ≥ 0.8 at apply, nothing overdue > 3d).
State plainly what's met and what's left, with days-to-deadline if set.

## 4. Artifacts (on request)

- **Gap cheat sheet** → `artifacts/cheatsheet-<date>.md`: the weak topics only, with the crisp
  explanation from `notes.md` + the keyword associations from `keywords.md`. One page, dense.
- **Flashcard export (Anki-importable)** → `artifacts/deck-<date>.txt`, tab-separated
  `front<TAB>back` from `keywords.md` / low-mastery items. (Anki: File → Import, field-separated by Tab.)
  Optionally push to a running Anki via AnkiConnect if the learner uses it.

## 5. Close-out

- 2–3 line summary: what improved, the one thing to fix next, what's due next session.
- Make sure `notebook` has captured today's observations into `learner-profile.md`.
