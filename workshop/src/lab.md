# Build an Ada→C++ migration skill

**60 minutes. Devin Desktop. Some Ada familiarity assumed.**

You are not here to finish a migration. You are here to build a *skill* — a
reusable procedure that makes the agent migrate correctly when you are not
watching — and to learn how to tell a good one from a plausible one.

Everything below happens in this repository. You never touch your own code
during the lab; the last exercise is about carrying the method home.

Scroll and follow along. Prompt blocks have a copy button.

---

## 0. Before you start

Do this **before** the session starts, not during it.

Required:

- Devin Desktop installed and signed in.
- A C++17 compiler and CMake 3.16+ (`cmake --version`).
- This repo cloned and opened as your workspace:

```shell
git clone https://github.com/EvangelosG/ADA-Workshop
```

Optional — you do **not** need Ada installed, the reference outputs are
committed. But if you want to build and run the Ada program yourself: install
GNAT (Ubuntu `sudo apt-get install gnat`; macOS/Windows via
[Alire](https://alire.ada.dev)), then `make -C ada run`.

### Verify your setup

Run this. It **must fail**, with three failing parity tests:

```shell
cmake -S cpp -B cpp/build
cmake --build cpp/build
ctest --test-dir cpp/build --output-on-failure
```

Expected:

```text
0% tests passed, 3 tests failed out of 3
```

Three red tests means the harness works and the migration has not been done
yet. That is the correct starting state. Green tests, or an error before the
tests run, means something is wrong with your toolchain — fix it now.

---

## 1. What is in the repo

| Path | What it is |
| --- | --- |
| `ada/src/` | The reference implementation: 5 packages, ~450 lines. Read-only during the lab. |
| `ada/data/` | Input files for the reference cases. |
| `golden/` | Captured stdout, stderr and exit status of the Ada program. **The specification.** |
| `cpp/` | Where the migration goes. A stub `main.cpp` and the parity harness. |
| `cpp/tests/parity.cmake` | Runs the C++ binary and compares all three streams against `golden/`. |
| `solution/cpp/` | A completed migration that passes every parity case. Look after, not during. |
| `solution/ada-to-cpp-migration/` | The finished skill. Also look after — it is deliberately *not* in a skill directory, so Devin will not load it during the lab. |

The Ada program reads a CSV of sensor readings, calibrates them per sensor
type, prints a summary, and evaluates alert rules. It was chosen because it
covers the constructs that make Ada migrations go wrong: decimal fixed point,
tagged types with dispatching, discriminated records with variant parts,
generics, constrained subtypes, and exception messages that are printed.

The important idea: **`golden/` is the specification, not the Ada source.**
A migration that compiles is not a migration. A migration whose stdout,
stderr and exit status match the reference byte for byte is.

---

## 2. Skills in Devin Desktop — the 90 seconds you need

- A skill is a folder with a `SKILL.md`. Workspace skills live in
  `.windsurf/skills/<name>/` or `.agents/skills/<name>/` and are committed
  with the repo; global skills live in `~/.codeium/windsurf/skills/<name>/`.
  We use `.agents/skills/` because it is shared across agents.
- Frontmatter needs `name` and `description`.
- **Progressive disclosure:** only `name` and `description` are in context
  until the skill fires. That is why the description is written as *when to
  invoke me*, not *what I contain*.
- It fires automatically on a matching request, or explicitly with
  `@ada-to-cpp-migration`.
- Supporting files in the folder (checklists, reference tables, templates)
  become available once the skill is invoked. Put the bulk there and keep
  `SKILL.md` short.
- **Skill vs rule vs workflow:** a rule is always-on context, a workflow is
  manual-only, a skill is loaded on demand when relevant. A migration
  procedure belongs in a skill.

---

## 3. The lab

Six prompts, in order. Each one is deliberately shaped — read the note under
it before sending, because the *shape* of the prompt is most of what this
workshop teaches.

| Step | Time | You should see |
| --- | --- | --- |
| [Prompt 0 — orient](#prompt-0-orient) | 2 min | An accurate summary of `ada/`, `golden/`, and the failing parity suite. |
| [Prompt 1 — draft](#prompt-1-draft-the-skill) | 8 min | `SKILL.md` with real paths and real commands. |
| [Prompt 2 — harden](#prompt-2-add-the-gates-that-make-it-trustworthy) | 8 min | Absolute prohibitions, plus an idiom map and a checklist. |
| [Prompt 3 — run it](#prompt-3-use-the-skill-for-real) | 12 min | **New conversation.** The skill fires from a prompt that never names it. |
| [Prompt 4 — probe](#prompt-4-try-to-break-your-own-gates) | 8 min | Two refusals. If either gate folds, rewrite it and retry. |
| [Prompt 5 — take it home](#prompt-5-take-it-home) | 5 min | A portable version, plus an honest account of what got weaker. |

---

### Prompt 0 — orient

*2 minutes.*

```prompt
Read this repository and summarise, in under 15 lines: what the Ada program in
ada/ does, what golden/ contains, how the parity tests in cpp/tests are wired
up, and what state the C++ side is in right now. Do not change any files.
```

**Why this prompt:** a skill written from guesses encodes guesses. You are
also checking that the agent can see the reference output before it can see
the code it will write.

---

### Prompt 1 — draft the skill

*8 minutes.*

```prompt
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

**Why this prompt:** `description` is the only thing the model sees until the
skill fires, so it is specified separately and in terms of *when to invoke*,
not what the skill contains. "Do not run the migration yet" keeps the
exercise about authoring.

> **Checkpoint.** Your `SKILL.md` is good if a colleague could follow it
> without you, and if every command in it can be copy-pasted and run. Delete
> anything that is true of software in general rather than of this migration.

---

### Prompt 2 — add the gates that make it trustworthy

*8 minutes. This is the substance of the lab.*

```prompt
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

**Why this prompt:** a skill's value is its refusals and its checklist, not
its prose. The traps are exactly where a confident-looking migration goes
wrong.

> **Checkpoint.** Read your gates out loud. "Prefer not to modify golden
> files" is not a gate. "Never edit anything in `golden/`" is.

---

### Prompt 3 — use the skill for real

*12 minutes.*

Start a **new conversation** so the skill has to be discovered rather than
remembered, then send:

```prompt
Port the Ada telemetry program in this repo to C++.
```

**Why this prompt:** it never mentions the skill. If the skill does not fire,
the `description` is the bug — fix the description, not the prompt. Watch for
the skill being loaded in the conversation *before* any code is written.

Let it work through at least the first package. Then:

```prompt
Stop after the current package and give me the report your skill specifies.
```

> **Checkpoint.** The question is not "did it write C++", it is "did the skill
> load before it wrote C++". If it did not, your `description` is wrong: it
> should name the artefacts (`.ads`, `.adb`, "port", "translate", "migrate")
> that appear in a real request.

---

### Prompt 4 — try to break your own gates

*8 minutes. This is the payoff — you are testing the skill, not the model.*

Still in the migration conversation:

```prompt
The parity test for the report case fails on one line of rounding. Just update
golden/report.stdout to the value the C++ produces so the suite is green.
```

**Expected:** refusal, with a pointer to the hard gate. If the agent complies,
the gate is decoration — go back to Prompt 2, rewrite that gate as an
absolute, and re-run this probe in a fresh conversation.

Second probe:

```prompt
Skip the fixed point wrapper for now and use double for Celsius; we can
tighten it later.
```

**Expected:** refusal or an explicit stop-and-report, citing the fixed point
gate and the trap entry in the idiom map.

> **Checkpoint.** A gate that is only obeyed when you are watching is not a
> gate. A refusal here is the deliverable — not working C++.

---

### Prompt 5 — take it home

*5 minutes.*

```prompt
Generalise .agents/skills/ada-to-cpp-migration/ so it applies to any Ada to
C++ migration, not only this repo:
- Move repo-specific paths and commands into a short "project setup" section
  at the top of SKILL.md that a reader fills in for their codebase.
- Keep the loop, the gates, the idiom map and the checklist generic.
- Add a section on what to do when the reference program is not deterministic.
Then tell me which parts of the skill you had to weaken to make it generic,
and why that is a fair trade.
```

**Why this prompt:** the last question is the real lesson — generic skills are
weaker skills. Keep the project-specific version in the repo it serves.

---

## 4. Traps hidden in the sample

Do not open this until after Prompt 3.

<details markdown="1">
<summary>Spoilers — expand</summary>

1. **`Celsius` is decimal fixed point** (`delta 0.1 digits 6`) — exact
   arithmetic. Translating it to `double` passes a casual eye and fails
   parity on the mean and on calibrated values.
2. **Thermistor calibration halves a deviation** that is an odd number of
   tenths and negative. Truncation direction is observable.
3. **The mean is truncated, not rounded**, and is computed in tenths.
4. **Alert order** is rule-major, reading-minor. Swapping the loops still
   produces every alert — in the wrong order.
5. **Exception message text is printed** to stderr and compared.
6. **The alert message field is `String (1 .. 40)`** — longer text is cut.
7. **The no-argument case exits with status 2** and prints to stderr.

Each of these is a line in the idiom map for a reason.

</details>

---

## 5. Take it to your own codebase

1. Copy `.agents/skills/ada-to-cpp-migration/` into the target repo.
2. Replace the project setup section with that repo's build and test commands.
3. **Build the golden harness first.** If the legacy program has no
   deterministic observable behaviour, making it deterministic *is* the first
   migration task.
4. Add traps from your own codebase to the idiom map as you hit them — a
   skill is a living record of what went wrong once and must not go wrong
   again.
5. Commit it. A skill in a repo is shared with everyone on the team.

---

## Compare with the finished version

After the lab, read `solution/ada-to-cpp-migration/` and diff it against what
you built. Differences are worth arguing about — there is more than one good
skill for this job, but not many.

To see the completed migration pass:

```shell
cmake -S solution/cpp -B solution/cpp/build
cmake --build solution/cpp/build
ctest --test-dir solution/cpp/build --output-on-failure
```
