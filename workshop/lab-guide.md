# Lab guide — build an Ada→C++ migration skill in Devin Desktop

**Duration:** 60 minutes. **You will leave with:** a working skill in your own
clone, and a method you can point at your own legacy codebase.

---

## 0. Before you start (do this ahead of the session)

Required:

- Devin Desktop installed and signed in.
- A C++17 compiler and CMake 3.16+ (`cmake --version`).
- This repo cloned and opened as your workspace:
  `git clone https://github.com/EvangelosG/ADA-Workshop`

Optional (not needed — the reference outputs are committed):

- GNAT, if you want to build and run the Ada program yourself.
  Ubuntu: `sudo apt-get install gnat`. macOS/Windows: install Alire
  (<https://alire.ada.dev>). Then `make -C ada run`.

Verify your setup — this **must fail**, with three failing parity tests:

```
cmake -S cpp -B cpp/build
cmake --build cpp/build
ctest --test-dir cpp/build --output-on-failure
```

Three red tests means the harness works and the migration has not been done.
That is the correct starting state.

---

## 1. What is in the repo

| Path | What it is |
| --- | --- |
| `ada/src/` | The reference implementation: 5 packages, ~450 lines. Read-only during the lab. |
| `ada/data/` | Input files for the reference cases. |
| `golden/` | Captured stdout, stderr and exit status of the Ada program. **The specification.** |
| `cpp/` | Where your migration goes. Contains a stub `main.cpp` and the parity harness. |
| `cpp/tests/parity.cmake` | Runs the C++ binary and compares all three streams against `golden/`. |
| `solution/cpp/` | A completed migration that passes all parity cases. Look after, not during. |
| `solution/ada-to-cpp-migration/` | The finished skill. Also look after — it is deliberately *not* in a skill directory, so Devin will not load it during the lab. |
| `workshop/prompts.md` | The prompts you will paste. |

The Ada program reads a CSV of sensor readings, calibrates them per sensor
type, prints a summary, and evaluates alert rules. It was chosen because it
covers the constructs that make Ada migrations go wrong: decimal fixed point,
tagged types with dispatching, discriminated records with variant parts,
generics, constrained subtypes, and exception messages that are printed.

---

## 2. Skills in Devin Desktop — the 90 seconds you need

- A skill is a folder with a `SKILL.md`. Workspace skills live in
  `.windsurf/skills/<name>/` or `.agents/skills/<name>/` and are committed
  with the repo; global skills live in `~/.codeium/windsurf/skills/<name>/`.
  We use `.agents/skills/` because it is shared across agents.
- Frontmatter needs `name` and `description`.
- **Progressive disclosure:** only `name` and `description` are in context
  until the skill fires. That is why the description is written as *when to
  invoke me*.
- It fires automatically on a matching request, or explicitly with
  `@ada-to-cpp-migration`.
- Supporting files in the folder (checklists, reference tables, templates)
  are available once the skill is invoked. Put the bulk there, keep
  `SKILL.md` short.
- Skill vs rule vs workflow: a rule is always-on context, a workflow is
  manual-only, a skill is loaded on demand when relevant. Migration procedure
  belongs in a skill.

---

## 3. The lab

Run the prompts in `workshop/prompts.md` in order.

| Step | Prompt | Time | You should see |
| --- | --- | --- | --- |
| Orient | 0 | 2 min | An accurate summary of `ada/`, `golden/`, and the failing parity suite. |
| Draft | 1 | 8 min | `.agents/skills/ada-to-cpp-migration/SKILL.md` with real paths and real commands. |
| Harden | 2 | 8 min | Absolute prohibitions, plus `reference/idiom-map.md` and `checklists/per-package.md`. |
| Run | 3 | 12 min | **New conversation.** The skill fires from a prompt that never names it; first package translated; parity suite re-run. |
| Probe | 4 | 8 min | Two refusals. If either gate folds, rewrite it and retry. |
| Generalise | 5 | 5 min | A portable version, plus an honest account of what got weaker. |

### Checkpoints

**After Prompt 1** — your `SKILL.md` is good if a colleague could follow it
without you, and if every command in it can be copy-pasted and run. Delete
anything that is true of software in general rather than of this migration.

**After Prompt 2** — read your gates out loud. "Prefer not to modify golden
files" is not a gate. "Never edit anything in `golden/`" is.

**After Prompt 3** — the question is not "did it write C++", it is "did the
skill load before it wrote C++". Check the conversation for the skill being
invoked. If it did not, your `description` is wrong: it should name the
artefacts (`.ads`, `.adb`, "port", "translate", "migrate") that appear in a
real request.

**After Prompt 4** — a gate that is only obeyed when you are watching is not
a gate. This probe is the whole point of the lab: you are testing the skill,
not the model.

---

## 4. Traps hidden in the sample (spoilers)

Do not read this until after Prompt 3.

<details>
<summary>Expand</summary>

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
