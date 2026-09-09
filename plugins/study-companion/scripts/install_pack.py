#!/usr/bin/env python3
"""
install_pack.py — materialize a read-only resource pack into the writable study root.

Resource packs ship inside the plugin (read-only) at
`resources/packs/<slug>/` and carry a subject pre-tuned on a topic: plan.md, index.md,
an optional corpus/, and items.seed.json. This script copies that into the learner's
writable study root so the tutor works, already calibrated, from first run.

The plugin stays generic; packs are pluggable extras — today SERGAS, tomorrow others.

Usage:
  install_pack.py --list                       # list packs bundled in the plugin
  install_pack.py --pack <slug|dir> [--study-home DIR] [--force]

Study root resolution: --study-home → $STUDY_HOME → ~/.claude/study-companion
Pack resolution for --pack <slug>: looks under <this script>/../resources/packs/<slug>.
"""
import argparse, json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PACKS_DIR = os.path.normpath(os.path.join(HERE, "..", "resources", "packs"))


def study_root(arg):
    root = arg or os.environ.get("STUDY_HOME") or os.path.expanduser("~/.claude/study-companion")
    return os.path.expanduser(root)


def list_packs():
    if not os.path.isdir(PACKS_DIR):
        print("(no packs bundled)"); return
    for name in sorted(os.listdir(PACKS_DIR)):
        pj = os.path.join(PACKS_DIR, name, "pack.json")
        if os.path.exists(pj):
            meta = json.load(open(pj))
            print(f"- {meta.get('slug', name)}: {meta.get('subject','')}")
            if meta.get("description"):
                print(f"    {meta['description']}")


def resolve_pack(pack):
    if os.path.isdir(pack):
        return pack
    cand = os.path.join(PACKS_DIR, pack)
    if os.path.isdir(cand):
        return cand
    print(f"pack not found: {pack} (looked in {PACKS_DIR})", file=sys.stderr)
    sys.exit(1)


def main():
    p = argparse.ArgumentParser(description="Materialize a study resource pack")
    p.add_argument("--list", action="store_true")
    p.add_argument("--pack")
    p.add_argument("--study-home")
    p.add_argument("--force", action="store_true", help="overwrite an existing materialized subject")
    a = p.parse_args()

    if a.list or not a.pack:
        list_packs()
        if not a.pack:
            return

    pack_dir = resolve_pack(a.pack)
    meta = json.load(open(os.path.join(pack_dir, "pack.json")))
    slug = meta["slug"]
    dest = os.path.join(study_root(a.study_home), slug)

    if os.path.exists(dest) and not a.force:
        print(f"already installed at {dest} (use --force to overwrite). Resuming existing subject.")
        return

    os.makedirs(os.path.join(dest, "state"), exist_ok=True)
    os.makedirs(os.path.join(dest, "artifacts"), exist_ok=True)

    # copy plan/index/notes/keywords if present
    for fn in ("plan.md", "index.md", "notes.md", "keywords.md", "learner-profile.md"):
        src = os.path.join(pack_dir, fn)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(dest, fn))

    # copy corpus if present
    corpus = os.path.join(pack_dir, "corpus")
    if os.path.isdir(corpus):
        shutil.copytree(corpus, os.path.join(dest, "corpus"), dirs_exist_ok=True)

    # seed the scheduler state
    seed = os.path.join(pack_dir, meta.get("seed_items", "items.seed.json"))
    items_dst = os.path.join(dest, "state", "items.json")
    if os.path.exists(seed):
        shutil.copy2(seed, items_dst)
    elif not os.path.exists(items_dst):
        json.dump({"items": {}}, open(items_dst, "w"))

    # ensure history file exists
    hist = os.path.join(dest, "state", "quiz-history.jsonl")
    if not os.path.exists(hist):
        open(hist, "a").close()

    n = len(json.load(open(items_dst)).get("items", {}))
    print(f"installed '{slug}' → {dest}")
    print(f"  subject: {meta.get('subject','')}")
    print(f"  seeded items: {n}")
    print(f"  next: run the quiz skill on this subject (state/items.json).")


if __name__ == "__main__":
    main()
