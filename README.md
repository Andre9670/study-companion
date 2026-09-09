# Study Companion — an adaptive AI tutor for Claude Code

An AI **tutor** that helps you actually learn a subject, not just get answers. It quizzes
you with active recall, **adapts to what you get wrong**, explains the theory, gives you
keywords and associations to memorize, and tracks your mastery over time with spaced
repetition (SM-2). It works from **your own material** (grounded, with citations) or from
**public knowledge** — or both, when you only have part of the material.

**No material required.** The default is *open mode*: just name a subject or exam and it
teaches, quizzes, and tracks you from public knowledge. Giving it your own notes, slides, or
PDFs is **optional** — it just switches to *grounded mode* (answers only from your sources,
cited). Most learners start with nothing but a topic.

It keeps its own notebook: theory notes, a keyword bank, and a profile of *you* as a
learner (your weak spots, recurring mistakes, and false-confidence traps) — so it gets
smarter about you every session.

## What it does

- **Active-recall quizzing** — one question at a time; asks your confidence first; withholds
  the answer and gives graduated hints instead of just telling you.
- **Adapts to your path** — a wrong answer resurfaces soon, drops in the schedule, gets a
  fresh easier question, and an explanation + a keyword to anchor it. Mastered topics get
  harder questions or step aside.
- **Spaced repetition** — a tested SM-2 scheduler decides what's due; state lives in plain files.
- **Self-maintained notebook** — `notes.md`, `keywords.md`, `learner-profile.md`.
- **Two modes** — *grounded* (answers only from your sources, cited) and *open* (public knowledge).
- **Artifacts** — gap cheat sheets and Anki-importable flashcard decks.

## Install

```
/plugin marketplace add Andre9670/study-companion
/plugin install study-companion@study-companion-marketplace
/reload-plugins
```

Then just talk to it: *"study me for the Spanish oposición"*, *"quiz me on X"*,
*"prepare me for [exam] by [date]"*. The `tutor` agent runs the show; the skills
(`study-plan`, `quiz`, `notebook`, `progress`) do the work.

## Pre-tuned resource packs (optional)

The plugin is generic, but it can ship **resource packs** — a subject already tuned on a
topic (exam plan, full official temario, source policy, and an ingested index of the material)
so the tutor starts already calibrated. Packs ship **no pre-made questions** — the tutor
generates them on demand when you want to practice. This build includes:

- **`sergas-dietista-nutricionista`** — SERGAS Dietista-Nutricionista oposición (Galicia):
  Anexo III exam structure + full verbatim temario (8 común + 46 específica) + source policy,
  with Temas 35–36 (psicología del comportamiento alimentario + TCA) ingested for grounded practice.

On first run the tutor lists packs and loads the relevant one for you:
```
python3 <plugin>/scripts/install_pack.py --list
python3 <plugin>/scripts/install_pack.py --pack sergas-dietista-nutricionista
```
It materializes into your study root, then you just say *"quiz me"*. Packs are optional
extras — remove or add folders under `resources/packs/` to change what ships.

## Where your data lives

Your progress and notes are stored **outside this plugin**, under
`~/.claude/study-companion/<subject>/` (override with the `STUDY_HOME` env var).
Nothing personal is written into the installed plugin, and the repo ships only an
example progress file — **your study data is never committed**.

## Local development

```
claude --plugin-dir ./plugins/study-companion
/reload-plugins
python3 ./plugins/study-companion/scripts/sm2.py selftest
```

## License

MIT — see [LICENSE](./LICENSE). Plugins run code with your privileges; only install
marketplaces and plugins you trust.
