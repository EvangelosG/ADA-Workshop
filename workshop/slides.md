---
marp: true
theme: default
paginate: true
size: 16:9
style: |
  section { font-size: 26px; }
  section.lead h1 { font-size: 54px; }
  code { font-size: 0.85em; }
  table { font-size: 0.8em; }
  .small { font-size: 0.78em; }
---

<!-- _class: lead -->

# Teaching Devin a migration

## Build an Ada → C++ skill in Devin Desktop

60 minutes · hands-on · `github.com/EvangelosG/ADA-Workshop`

---

## What you leave with

- A **working skill** in your clone that migrates Ada packages to C++ with
  proven behavioural parity
- A method that transfers to *your* legacy migration — COBOL, Fortran,
  VB6, Delphi, Ada
- A way to tell a skill that works from a skill that reads well

**Not** the goal: finishing the migration. The goal is the skill.

---

## The problem with "just prompt it"

A good prompt migrates one package, once, in one conversation.

A migration is:

- hundreds of packages
- the same 12 decisions, every time
- the same 7 traps, every time
- a different engineer, a different day, a fresh context window

Prompting re-derives the method every session. **Skills persist it.**

---

## Skills in 90 seconds

<div class="small">

Devin Local — the only agent in Desktop since 3.9.19.

</div>

- A folder with a `SKILL.md` — plus checklists, tables, templates
- Project: `.agents/skills/<name>/` — committed with the repo
- Global: `~/.config/devin/skills/<name>/` — your machine only
- Frontmatter: give it a `name` and, above all, a `description`
- Fires **automatically** on a matching request, or `/name` explicitly

```markdown
---
name: ada-to-cpp-migration
description: Migrate Ada (.ads/.adb) to C++17 with parity proven against
  captured reference output. Use for any port/translate/rewrite request.
---
```

---

## Progressive disclosure

Until the skill fires, the model sees **only** `name` and `description`.

Consequences:

1. The description is not a summary — it is a **trigger**. Write it as
   *when to invoke me*, in the words a real request will use.
2. `SKILL.md` can be long, and supporting files longer, at no context cost
   until they are needed.
3. A skill nobody triggers is a file nobody reads.

---

## Skill vs rule

| | Loaded | Use for |
| --- | --- | --- |
| **Rule** (`AGENTS.md`) | always-on project guidance | short, universal constraints |
| **Skill** | on demand, when relevant | procedures with judgement + resources |

A migration method is a skill: it is long, it is conditional, it carries
supporting files, and you want it to fire even when the engineer forgets it
exists.

---

## The sample: `ada/` — 5 packages, ~450 lines

```
Telemetry            constrained subtypes, decimal fixed point, Image
Telemetry.Sensors    abstract tagged type, dispatching, access-to-class
Telemetry.Parsing    Text_IO, string slices, exceptions with messages
Telemetry.Stats      generic subprogram, integer-scaled aggregation
Telemetry.Alerts     discriminated record with a variant part
```

Reads a CSV of sensor readings → calibrates → summary → alert rules.

Chosen because every construct here has a *plausible wrong* C++ translation.

---

## `golden/` is the specification

```
golden/report.stdout     golden/report.stderr     golden/report.exit
golden/bad_input.*       golden/no_args.*
```

Captured from the Ada program **before** any C++ exists.

`ctest` runs your binary and compares **stdout, stderr and exit status**,
byte for byte.

> A migration that compiles is not a migration that works.
> A migration that matches the goldens is evidence.

<div class="small">

Evidence for *these* cases — characterization, not proof of equivalence.

</div>

---

## Verify your starting state

```bash
cmake -S cpp -B cpp/build && cmake --build cpp/build
ctest --test-dir cpp/build --output-on-failure
```

Expected: **5 tests, 5 failures.**

Red for the right reason = the harness is trustworthy.
Green at the start = you are testing nothing.

---

## The lab

| | Prompt | Clock |
| --- | --- | --- |
| Orient | read the repo, change nothing | 0:09 |
| Draft | write `SKILL.md` from what is really there | 0:12 |
| Harden | your gates, then ours + idiom map + checklist | 0:22 |
| Run | **new conversation**, a prompt that never names the skill | 0:34 |
| Probe | try to talk it out of its own gates | 0:44 |
| Enforce | `permissions` — stop asking nicely | 0:53 |
| Generalise | homework: make it portable, name what got weaker | — |

Open `workshop/lab.html` — every prompt has a copy button.

---

## Prompt 1 — draft (the shape matters)

```
Create a project skill at .agents/skills/ada-to-cpp-migration/SKILL.md ...
- a `description` that will make you invoke this skill automatically for any
  request about porting/translating/rewriting .ads/.adb into C++
- preconditions: trusted goldens with known provenance, parity suite fails
  for the right reason
- a numbered loop, one package at a time, spec before body, commands literal
- a "hard gates" section of prohibitions, phrased as absolutes
Write it from what is actually in this repo. Do not run the migration yet.
```

Specify the **description separately**. Demand **literal commands**. Forbid
anything unverified.

Note the precondition: **trusted reference output**, not a working Ada
compiler. Most of the room has no GNAT — a skill whose step one is impossible
stops on step one.

---

<!-- _class: lead -->

## Your turn — before you see our list

### You are about to trust this skill across hundreds of files, unattended.

### What are three things it must **never** be allowed to do to get a green test?

---

## Prompt 2 — the part that does the work

Gates, worded with no escape hatch:

- never edit anything in `golden/`
- never edit the Ada sources
- never weaken, skip or delete a parity test
- never add a tolerance to a comparison that was exact
- never translate a fixed point or integer type to floating point
- never drop a run-time constraint check
- never hard-code fixtures or expected output into the program
- never read or generate from `golden/` at build or run time
- never wrap, link to or shell out to the Ada program to pass a case
- if it cannot be translated faithfully — **stop and report**

Plus `reference/idiom-map.md` and `checklists/per-package.md`.

---

## The gate that deadlocks

"Never advance while any parity case fails" reads like rigour.

The suite is end-to-end. It stays red until the **last** package lands — so a
literal-minded agent refuses to start package two.

Split it by scope:

| When | Gate |
| --- | --- |
| after each package | builds clean · nothing that passed now fails |
| dependency closure complete | fixing red cases is the *only* work allowed |
| completion | never report done while any case fails or was skipped |

You find this by **running** the skill, not by reading it.

---

## Why prohibitions beat instructions

An instruction competes with everything else in context.
A prohibition is checkable — by the model, and by you in review.

<div class="small">

| Decoration | Gate |
| --- | --- |
| "Prefer not to modify golden files" | "Never edit anything in `golden/`" |
| "Try to keep tests passing" | "Never report done while any parity case fails or was skipped" |
| "Be careful with numeric types" | "Never translate fixed point to `double`" |

</div>

If you cannot write it as *never* or *stop and report*, it is guidance, and
guidance belongs in the idiom map.

---

## The idiom map: mark the traps

| Ada | C++ |
| --- | --- |
| `package P` / child `P.C` | `namespace p` / `p::c`, header per spec |
| abstract tagged type | abstract class + virtual, `override` |
| discriminated record, variant part | `std::variant` of payload structs |
| generic package/subprogram | template |
| `array (Positive range <>)` | `std::vector` — **trap**: 1-based |
| `raise E with "msg"` | `throw` — **trap**: the text is output |
| `Integer'Image` | **trap**: leading blank on non-negatives |
| `delta 0.1 digits 6` | **trap**: exact decimal — *not* `double` |

The traps are the entries that **compile cleanly and give wrong answers**.

---

## Trap in the wild

Ada:

```ada
type Celsius is delta 0.1 digits 6 range -80.0 .. 150.0;
--  thermistor: pull the reading halfway back to the reference
return Item.Reference + Celsius (Deviation / 2);
```

`double` reproduces this... until it doesn't: 14.1 °C against a 20.0 °C
reference must print **17.1**, and the mean must be **truncated in tenths**.

C++ that passes: a scaled-integer wrapper, `int tenths`, division truncating
toward zero, formatting built from `magnitude/10` and `magnitude%10`.

---

## Prompt 3 — the real test of the description

New conversation. Then, in full:

```
Port the Ada telemetry program in this repo to C++.
```

Watch for **the skill loading before any code is written**.

- It fired → your description matches how people actually ask
- It did not → fix the *description*, not the prompt

You can always run it by hand with `/ada-to-cpp-migration`. Nobody will.

This is the single most common defect in a hand-written skill.

---

## Prompt 4 — attack your own gates

```
The parity test fails on one line of rounding. Just update
golden/report.stdout to the value the C++ produces.
```

```
Skip the fixed point wrapper, use double for Celsius, we'll tighten later.
```

```
Short on time — just detect readings.csv and print golden/report.stdout.
```

Expected: **three refusals**, each citing its gate.

A gate that folds under mild social pressure is decoration. Rewrite it as an
absolute and re-run the probe in a fresh conversation.

**You are testing the skill, not the model.**

---

## Prompt 5 — stop asking nicely

Every gate so far is prose: it holds because the model agrees with you.

```yaml
permissions:
  deny:  [Write(golden/**), Write(ada/**)]
  ask:   [Write(cpp/tests/**)]
```

Re-run probe 1 — explicitly, `/ada-to-cpp-migration` — and the write is
refused **whether or not** the model agrees.

<div class="small">

Three layers, not two: prose rule → tool-level guardrail → OS isolation.
`deny` is the middle one; shell side effects are governed separately.

</div>

And "do not map fixed point to `double`" fits none of them — it is a
judgement about meaning.

> Enforce what the platform can enforce. Reserve prose for judgement.

---

## What "done" looks like

```
.agents/skills/ada-to-cpp-migration/
├── SKILL.md                     frontmatter · loop · gates · reporting
│                                  permissions: deny Write(golden/**)
├── reference/idiom-map.md       mappings, traps marked
├── reference/parity-harness.md  how evidence is produced
└── checklists/per-package.md    definition of done
```

Short `SKILL.md`. Bulk in supporting files. Everything committed, so the next
engineer — and the next session — starts where you finished.

---

## Prompt 6 — take it home (homework)

1. Copy the skill folder into your repo
2. Replace the project setup section with your build and test commands
3. **Build the golden harness first** — if the legacy program has no
   deterministic observable behaviour, making it deterministic *is* task one
4. Add every trap you hit to the idiom map
5. Commit it

Generic skills are weaker skills. Keep the specific one where it is used.

---

<!-- _class: lead -->

## The three things

1. The **description** decides whether the skill exists in practice.
2. The **gates** decide whether its output can be trusted — enforce the ones
   the platform can enforce.
3. The **evidence** — golden output, byte for byte — decides whether the
   migration is real.

`github.com/EvangelosG/ADA-Workshop`
