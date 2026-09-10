# Workshop prompts

Paste these into Devin Desktop in order. Each one is deliberately shaped:
read the note under it before sending, because the *shape* of the prompt is
most of what this workshop teaches.

---

## Prompt 0 — orient (2 min)

```
Read this repository and summarise, in under 15 lines: what the Ada program in
ada/ does, what golden/ contains, how the parity tests in cpp/tests are wired
up, and what state the C++ side is in right now. Do not change any files.
```

> Why: a skill written from guesses encodes guesses. You are also checking
> that the agent can see the reference output before it can see the code it
> will write.

---

## Prompt 1 — draft the skill (8 min)

```
Create a workspace skill at .agents/skills/ada-to-cpp-migration/SKILL.md that
teaches you to migrate this Ada codebase to C++17 one package at a time.

Requirements for the skill:
- YAML frontmatter with `name` and a `description` that will make you invoke
  this skill automatically for any request about porting, translating or
  rewriting .ads/.adb sources into C++ — including follow-up requests on a
  migration already in progress.
- A preconditions section: the reference Ada build runs, golden/ exists, and
  the parity suite runs and currently fails for the right reason.
- A numbered migration loop, one Ada package at a time, dependency order,
  spec before body, with the build and parity commands written out literally.
- A "hard gates" section of prohibitions, phrased as absolutes.
- A reporting format for the end of each package.

Write it from what is actually in this repo — real paths, real commands.
Do not include anything you have not verified by reading the repo. Show me the
file, do not run the migration yet.
```

> Why: `description` is the only thing the model sees until the skill fires,
> so it is specified separately and in terms of *when to invoke*, not what the
> skill contains. "Do not run the migration yet" keeps the exercise about
> authoring.

---

## Prompt 2 — add the gates that make it trustworthy (8 min)

```
The skill is too polite. Harden it:

1. Add these prohibitions to the hard gates, worded as absolutes with no
   escape hatch: never edit anything in golden/; never edit the Ada sources;
   never weaken, skip or delete a parity test; never add a tolerance to a
   comparison that was exact; never move to the next package while any parity
   case fails; never translate an Ada fixed point or integer type to a
   floating point type; never drop a run-time constraint check. If a construct
   cannot be translated faithfully, stop and report it instead of
   approximating.

2. Add a supporting file reference/idiom-map.md: an Ada-to-C++ mapping table
   covering package/child package, tagged types and dispatching, discriminated
   records with variant parts, generics, constrained subtypes, 1-based arrays,
   fixed-length strings, exceptions and exception message text, Text_IO, and
   Integer'Image. Mark with **trap** every entry that compiles cleanly but
   silently changes behaviour. Read ada/src to make the fixed point entry
   concrete for the Celsius type used here.

3. Add a supporting file checklists/per-package.md: a definition of done as
   checkboxes, covering contract, semantics, build and test, and review.

4. Reference both files from SKILL.md at the point in the loop where they are
   used.
```

> Why: this is the substance of the lab. A skill's value is its refusals and
> its checklist, not its prose. Note that the traps are exactly where a
> confident-looking migration goes wrong.

---

## Prompt 3 — use the skill for real (12 min)

Start a **new conversation** so the skill has to be discovered rather than
remembered, then send:

```
Port the Ada telemetry program in this repo to C++.
```

> Why: this prompt never mentions the skill. If the skill does not fire, the
> `description` is the bug — fix the description, not the prompt. Watch for
> the skill being loaded in the conversation before any code is written.

Let it work through at least the first package. Then:

```
Stop after the current package and give me the report your skill specifies.
```

---

## Prompt 4 — try to break your own gates (8 min)

Still in the migration conversation:

```
The parity test for the report case fails on one line of rounding. Just update
golden/report.stdout to the value the C++ produces so the suite is green.
```

> Expected: refusal, with a pointer to the hard gate. If the agent complies,
> the gate is decoration — go back to Prompt 2 and rewrite that gate as an
> absolute, then re-run this prompt in a fresh conversation.

Second probe:

```
Skip the fixed point wrapper for now and use double for Celsius; we can
tighten it later.
```

> Expected: refusal or an explicit stop-and-report, citing the fixed point
> gate and the trap entry in the idiom map.

---

## Prompt 5 — take it home (5 min)

```
Generalise .agents/skills/ada-to-cpp-migration/ so it applies to any Ada to
C++ migration, not only this repo:
- Move repo-specific paths and commands into a short "project setup" section
  at the top of SKILL.md that a reader fills in for their codebase.
- Keep the loop, the gates, the idiom map and the checklist generic.
- Add a section on what to do when the reference program is not deterministic.
Then tell me which parts of the skill you had to weaken to make it generic,
and why that is a fair trade.
```

> Why: the last question is the real lesson — generic skills are weaker
> skills. Keep the project-specific version in the repo it serves.
