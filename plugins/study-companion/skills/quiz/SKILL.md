---
name: quiz
description: Run the adaptive active-recall quiz loop for a subject. Pulls due items (interleaved across topics, weakest first), asks one question at a time, collects a confidence rating before revealing, grades 0–5, gives graduated hints and a theory explanation on misses, coins a keyword/association to memorize, and updates the SM-2 scheduler. Use when the learner says "quiz me", "test me", "let's practice", or during a study session.
---

# Quiz — the active-recall loop (the core)

This is where studying happens. Withhold answers by default; make the learner retrieve.

## Setup

- Resolve the subject dir: `${STUDY_HOME:-~/.claude/study-companion}/<subject-slug>/`.
- Scheduler: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sm2.py`.
- Get due items: `sm2.py due --state <subject>/state/items.json --limit 10 --json`.
  (Already interleaved across topics, weakest-mastery first. New items count as due.)
- If nothing is due and no items exist yet, generate a starter set (see "Creating items").

## Per-item loop

For each due item:

1. **Confidence first (metacognition).** Ask: "How confident are you on this — low / medium / high?"
2. **Ask the question.** One at a time. Phrase at the item's Bloom level (recall → understand → apply → analyze).
3. **Withhold.** Do NOT show the answer. Wait for their attempt.
4. **On a correct/partial answer:** confirm, tighten any gaps, ask a quick "why" (elaboration).
5. **On a miss:**
   - Give a **graduated hint** (a nudge, not the answer). Escalate only if still stuck.
   - Once resolved (or if they say "just tell me"), **explain the theory** clearly and briefly.
   - **Coin a keyword + association/mnemonic** to anchor it → hand to the `notebook` skill for `keywords.md`.
6. **Grade 0–5** (self-assess honestly; a struggled-but-correct = 3, clean = 4, instant/perfect = 5;
   hinted-heavily = 2, wrong = 1, blank = 0). Then:
   ```
   sm2.py grade --state <subject>/state/items.json --id <ID> --grade <q>
   ```
7. **Log the attempt** — append one line to `<subject>/state/quiz-history.jsonl`:
   ```json
   {"ts":"<ISO>","item":"<ID>","topic":"<t>","bloom":"<b>","confidence":"<low|med|high>","grade":<q>,"note":"<optional>"}
   ```

## Adaptivity within the session

- Miss + high confidence → call it out (a "known trap"); flag for the `notebook` profile update.
- Two misses on related items → create 1–2 easier questions on that sub-concept via
  `sm2.py add --id <new> --topic <t> --bloom recall --question "..." --answer "..." --keywords "..."`
  and drill them before moving up.
- Solid mastery → raise Bloom level or move on (mastery gating). Don't over-drill what's known.
- Keep sessions short and interleaved; stop when due items are exhausted or the learner is fatigued.

## Creating items (new subject or thin topic)

Generate atomic Q/A items (one fact/skill each), tag `topic` and `bloom`, and add each:
```
sm2.py add --state <subject>/state/items.json --id <slug> --topic <t> --bloom <recall|understand|apply|analyze> \
  --question "<q>" --answer "<a>" --keywords "<k1,k2>"
```
In **grounded mode**, draw items only from `corpus/`+`index.md` and store the source ref in the question/answer.

Hand off to `notebook` (write notes/keywords/profile) and `progress` (close-out) as you go.
