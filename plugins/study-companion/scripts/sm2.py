#!/usr/bin/env python3
"""
sm2.py — deterministic SM-2 spaced-repetition scheduler for study-companion.

The LLM (tutor agent) OWNS content: it writes questions, explanations, keywords,
notes. This script OWNS state: which item is due, how the interval/ease evolve,
per-item mastery. Keeping scheduling in a tested script (not an LLM instruction)
is why progress can't silently drift — same lesson as the AMA/DealMaker trackers.

State file: a JSON object  { "items": { "<id>": {item}, ... } }
Each item: id, topic, bloom, question, answer, keywords[], EF, interval, reps,
           due (YYYY-MM-DD), last_grade, mastery (0..1), reviews.

Commands:
  init   --state F
  add    --state F --id ID --topic T [--bloom B] [--question Q] [--answer A] [--keywords "k1,k2"]
  due    --state F [--today YYYY-MM-DD] [--limit N] [--json]
  grade  --state F --id ID --grade 0..5 [--today YYYY-MM-DD]
  show   --state F [--json]
  selftest
"""
import argparse, json, sys, os
from datetime import date, timedelta

EF_START = 2.5
EF_FLOOR = 1.3


def _today(s):
    return date.fromisoformat(s) if s else date.today()


def load(path):
    if not os.path.exists(path):
        return {"items": {}}
    with open(path) as f:
        return json.load(f)


def save(path, state):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def sm2_update(item, q, today):
    """Apply the SM-2 algorithm for grade q (0..5) reviewed on `today`.
    Returns the mutated item."""
    q = int(q)
    ef = item.get("EF", EF_START)
    reps = item.get("reps", 0)
    if q >= 3:
        if reps == 0:
            interval = 1
        elif reps == 1:
            interval = 6
        else:
            interval = round(item.get("interval", 1) * ef)
        reps += 1
    else:
        reps = 0
        interval = 1
    ef = ef + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    if ef < EF_FLOOR:
        ef = EF_FLOOR
    item["EF"] = round(ef, 4)
    item["reps"] = reps
    item["interval"] = interval
    item["due"] = (today + timedelta(days=interval)).isoformat()
    item["last_grade"] = q
    # rolling mastery: EMA of normalized grade, responsive but not jumpy
    prev = item.get("mastery", 0.0)
    item["mastery"] = round(0.6 * prev + 0.4 * (q / 5.0), 4)
    item["reviews"] = item.get("reviews", 0) + 1
    return item


def due_items(state, today, limit=None):
    """Items due on/before `today`, interleaved across topics (round-robin),
    weakest-mastery topics first. New items (no due) count as due."""
    due = []
    for it in state["items"].values():
        d = it.get("due")
        if d is None or date.fromisoformat(d) <= today:
            due.append(it)
    # bucket by topic
    buckets = {}
    for it in due:
        buckets.setdefault(it.get("topic", "_"), []).append(it)
    # sort each bucket weakest-first, and order topics by mean mastery
    for b in buckets.values():
        b.sort(key=lambda x: (x.get("mastery", 0.0), x.get("due") or ""))
    topic_order = sorted(
        buckets.keys(),
        key=lambda t: sum(x.get("mastery", 0.0) for x in buckets[t]) / len(buckets[t]),
    )
    # round-robin interleave
    out, i = [], 0
    while any(buckets[t] for t in topic_order):
        t = topic_order[i % len(topic_order)]
        if buckets[t]:
            out.append(buckets[t].pop(0))
        i += 1
    return out[:limit] if limit else out


def cmd_init(a):
    save(a.state, {"items": {}})
    print(f"initialized empty state at {a.state}")


def cmd_add(a):
    state = load(a.state)
    if a.id in state["items"]:
        print(f"item '{a.id}' already exists", file=sys.stderr)
        sys.exit(1)
    state["items"][a.id] = {
        "id": a.id, "topic": a.topic, "bloom": a.bloom or "recall",
        "question": a.question or "", "answer": a.answer or "",
        "keywords": [k.strip() for k in a.keywords.split(",")] if a.keywords else [],
        "EF": EF_START, "interval": 0, "reps": 0, "due": None,
        "last_grade": None, "mastery": 0.0, "reviews": 0,
    }
    save(a.state, state)
    print(f"added '{a.id}' (topic={a.topic}, bloom={a.bloom or 'recall'})")


def cmd_due(a):
    state = load(a.state)
    items = due_items(state, _today(a.today), a.limit)
    if a.json:
        print(json.dumps(items, ensure_ascii=False, indent=2))
        return
    if not items:
        print("nothing due — you're caught up.")
        return
    for it in items:
        print(f"[{it['id']}] ({it['topic']}/{it['bloom']}) mastery={it['mastery']:.2f}  {it['question']}")


def cmd_grade(a):
    state = load(a.state)
    if a.id not in state["items"]:
        print(f"no item '{a.id}'", file=sys.stderr)
        sys.exit(1)
    it = sm2_update(state["items"][a.id], a.grade, _today(a.today))
    save(a.state, state)
    print(f"{a.id}: grade={a.grade} → interval={it['interval']}d due={it['due']} "
          f"EF={it['EF']} mastery={it['mastery']:.2f}")


def cmd_show(a):
    state = load(a.state)
    if a.json:
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return
    for it in state["items"].values():
        print(f"[{it['id']}] {it['topic']}/{it['bloom']} mastery={it['mastery']:.2f} "
              f"due={it['due']} reps={it['reps']} EF={it['EF']}")


def cmd_selftest(a):
    """Verify the SM-2 math and scheduling against known expectations."""
    fails = []
    t = date(2026, 1, 1)

    # 1. first correct (q=4) from fresh → reps 0→1, interval 1
    it = {"EF": 2.5, "reps": 0, "interval": 0, "mastery": 0.0}
    sm2_update(it, 4, t)
    if it["interval"] != 1 or it["reps"] != 1:
        fails.append(f"first correct: interval={it['interval']} reps={it['reps']} (want 1,1)")

    # 2. second correct → interval 6
    sm2_update(it, 4, t)
    if it["interval"] != 6 or it["reps"] != 2:
        fails.append(f"second correct: interval={it['interval']} reps={it['reps']} (want 6,2)")

    # 3. third correct → round(6 * EF)
    ef_before = it["EF"]
    sm2_update(it, 4, t)
    if it["interval"] != round(6 * ef_before):
        fails.append(f"third correct: interval={it['interval']} (want {round(6*ef_before)})")

    # 4. lapse (q=1) resets reps→0 interval→1
    sm2_update(it, 1, t)
    if it["interval"] != 1 or it["reps"] != 0:
        fails.append(f"lapse: interval={it['interval']} reps={it['reps']} (want 1,0)")

    # 5. EF floor at 1.3 after repeated lapses
    it2 = {"EF": 1.3, "reps": 0, "interval": 0, "mastery": 0.0}
    sm2_update(it2, 0, t)
    if it2["EF"] < EF_FLOOR - 1e-9:
        fails.append(f"EF floor: {it2['EF']} (want >= {EF_FLOOR})")

    # 6. EF increases on perfect grade
    it3 = {"EF": 2.5, "reps": 0, "interval": 0, "mastery": 0.0}
    sm2_update(it3, 5, t)
    if it3["EF"] <= 2.5:
        fails.append(f"EF on q=5: {it3['EF']} (want > 2.5)")

    # 7. due-list: overdue + new are due, future is not
    state = {"items": {
        "a": {"id": "a", "topic": "x", "bloom": "recall", "mastery": 0.1, "due": "2025-12-01"},
        "b": {"id": "b", "topic": "y", "bloom": "recall", "mastery": 0.9, "due": None},
        "c": {"id": "c", "topic": "x", "bloom": "recall", "mastery": 0.5, "due": "2026-06-01"},
    }}
    got = [x["id"] for x in due_items(state, t)]
    if set(got) != {"a", "b"}:
        fails.append(f"due set: {got} (want a,b)")

    # 8. interleave: weakest topic first, alternating topics
    state2 = {"items": {
        "a1": {"id": "a1", "topic": "A", "bloom": "r", "mastery": 0.1, "due": None},
        "a2": {"id": "a2", "topic": "A", "bloom": "r", "mastery": 0.2, "due": None},
        "b1": {"id": "b1", "topic": "B", "bloom": "r", "mastery": 0.8, "due": None},
    }}
    order = [x["id"] for x in due_items(state2, t)]
    if order[0] != "a1" or order[1] != "b1":
        fails.append(f"interleave order: {order} (want a1,b1,a2)")

    if fails:
        print("SELFTEST FAILED:")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("selftest: all 8 checks passed")


def main():
    p = argparse.ArgumentParser(description="SM-2 scheduler for study-companion")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init"); s.add_argument("--state", required=True); s.set_defaults(fn=cmd_init)

    s = sub.add_parser("add")
    s.add_argument("--state", required=True); s.add_argument("--id", required=True)
    s.add_argument("--topic", required=True); s.add_argument("--bloom")
    s.add_argument("--question"); s.add_argument("--answer"); s.add_argument("--keywords")
    s.set_defaults(fn=cmd_add)

    s = sub.add_parser("due")
    s.add_argument("--state", required=True); s.add_argument("--today")
    s.add_argument("--limit", type=int); s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_due)

    s = sub.add_parser("grade")
    s.add_argument("--state", required=True); s.add_argument("--id", required=True)
    s.add_argument("--grade", required=True, type=int, choices=range(0, 6))
    s.add_argument("--today"); s.set_defaults(fn=cmd_grade)

    s = sub.add_parser("show")
    s.add_argument("--state", required=True); s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_show)

    s = sub.add_parser("selftest"); s.set_defaults(fn=cmd_selftest)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
