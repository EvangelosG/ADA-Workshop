# Skills that can be trusted with a migration

The takeaway page for the 30-minute talk. It repeats the deck's argument in
enough detail to be useful a week later, and carries the reference material
— the idiom map and the per-package checklist — inline, so it works on its
own with nothing to clone and nothing to install.

Nothing here asks you to run our code, and nothing here is specific to our
sample: everything below applies to an Ada codebase you already have and
are already allowed to build.

## What a skill is

A skill is a folder with a `SKILL.md` in it, plus whatever supporting files
the procedure needs — checklists, mapping tables, templates. The frontmatter
gives it a name and a description:

```markdown
---
name: ada-to-cpp-migration
description: Migrate Ada (.ads/.adb) to C++17 with parity proven against
  captured reference output. Use for any port/translate/rewrite request.
---
```

It is discovered automatically and fires when a request looks relevant to
its description; you can also invoke it by hand as `/ada-to-cpp-migration`.
Devin Local is the agent in Devin Desktop as of 3.9.19, when Cascade was
removed — so slash, not at-sign.

### Desktop and the CLI use the same skill

| | Location |
| --- | --- |
| Project skill | `.agents/skills/<name>/` — committed with the repo |
| Global skill | `~/.config/devin/skills/<name>/` (macOS, Linux), `%APPDATA%\devin\skills\<name>\` (Windows) |

Same folder layout, same frontmatter, same invocation, whether you are in
the desktop app or the terminal.

Author it **in the repo**. A global skill helps you; a project skill is
reviewed like code, versioned with the code it describes, and shows up for
the next engineer who clones. The alternative locations `.devin/skills/` and
`.windsurf/skills/` are also recognised for a project.

### Progressive disclosure, and why the description decides everything

Until a skill fires, the model sees only its `name` and `description`. The
supporting files are read when the procedure needs them.

Three consequences:

1. The description is not a summary, it is a **trigger**. Write it as *when
   to invoke me*, using the words a real request will use — port, translate,
   rewrite, migrate, `.ads`, `.adb`.
2. `SKILL.md` can be long and its resources longer, at no cost until they
   are needed. Keep procedure in the skill and domain detail beside it.
3. A skill nobody triggers is a file nobody reads. The most common defect in
   a hand-written skill is not a bad procedure — it is a description that
   never matches how anyone asks.

If a skill fails to fire on a realistic request, the description is the
first thing to inspect: invocation is a relevance judgement, not a string
match, so a miss is evidence rather than proof.

### Skill or rule?

| | Loaded | Use for |
| --- | --- | --- |
| Rule (`AGENTS.md`) | always | short, universal constraints |
| Skill | on demand, when relevant | procedures with judgement and resources |

A migration method is a skill: long, conditional, resource-carrying, and it
needs to fire even when the engineer has forgotten it exists.

## Compilation is not migration

The question a migration has to answer is not "does it build" but "does it
still do the same thing". So the first artifact is not C++ — it is evidence.

Before writing any target code, run the legacy program and capture, for each
case:

```
stdout        stderr        exit status
```

Then have the test harness run the migrated binary on the same input and
compare all three, byte for byte. That is the definition of done: not a code
review, not a diff of the sources.

Be precise about what this buys you. A handful of cases is strong
**characterization evidence** for the behaviour those cases cover. It is not
proof that the two programs are equivalent, and an engineer in the room will
say so if you overclaim it. Pick cases by failure mode rather than by count:

- a normal case;
- a malformed input;
- a boundary or no-arguments case;
- and at least one that fails **after** validation — a constraint check on a
  computed value, or a missing file. Those are the cases a plausible-looking
  migration passes the others without handling.

## The gates

Write prohibitions, not preferences. An instruction competes with everything
else in the context window; a prohibition is checkable, by the model and by
you in review.

- never edit the captured reference output
- never edit the legacy sources
- never weaken, skip or delete a parity test
- never add a tolerance to a comparison that was exact
- never translate a fixed point or integer type to floating point
- never drop a run-time constraint check — an Ada subtype constraint that
  raises `Constraint_Error` needs an explicit counterpart with the same
  observable behaviour, everywhere a value of that type is produced:
  arithmetic results and conversions, not only parsed input
- never hard-code fixtures, fixture filenames or expected output into the
  program, and never read from or generate code from the captured output at
  build or run time
- never wrap, link to or shell out to the legacy program to pass a case
- never report the migration complete while any parity case fails or was
  skipped
- if something cannot be translated faithfully — stop and report

If you cannot phrase a rule as *never* or *stop and report*, it is guidance.
Guidance belongs in a reference file, where it does not dilute the gates.

### The gate that deadlocks

"Never advance while any parity case fails" reads like rigour and is a bug.
An end-to-end suite stays red until the last package lands, so a
literal-minded agent refuses to start the second package.

Scope the gate by stage instead of softening it:

| Stage | What must hold before continuing |
| --- | --- |
| after each package | the tree builds clean at the project's warning level, the per-package checklist passes, and no case that was passing has started failing |
| once the executable's dependency closure is translated | the whole suite passes; while any case is red, fixing it is the only permitted work — no new package, no cleanup, no refactoring. Debugging the failure is not "further work", it is the work |
| completion | never describe the migration as done while any parity case fails or was skipped |

You find defects like this by **running** the skill, not by reading it.
Assume every gate list you write has one in it.

### Three ways to a green suite with nothing migrated

The agent can read the inputs and the expected output, so the cheapest route
to green is not to migrate at all:

1. **Special-case the fixture.** Branch on the filename, print the expected
   answer. Passing tests, zero migration.
2. **Copy the evidence.** `std::ifstream in("golden/report.stdout");`
   `std::cout << in.rdbuf();` — this hard-codes nothing, so a rule that only
   forbids hard-coded output misses it entirely. Forbid build time too, or a
   generated header is the next move.
3. **Delegate.** An implementation that is really just
   shelling out to the Ada program, or linking against it: every case
   green, nothing translated, and the artifact still depends on the
   toolchain you were trying to retire.

Each of these needed its own prohibition. The general form of the rule is
*never make the program aware that it is under test, and never let the
legacy implementation produce the answer.*

### Prose gates and enforced gates

Everything above holds because the model agrees with it. Some of it can be
enforced instead:

```yaml
permissions:
  deny:  [Write(golden/**), Write(ada/**)]
  ask:   [Write(cpp/tests/**)]
```

`deny` holds whether or not the model agrees. Tests are `ask` rather than
`deny` because adding a parity case is legitimate work and weakening one is
not, and no path pattern can tell those apart — so a human decides.

Two honest limits. This is a **tool-level guardrail**, not OS isolation: it
governs the agent's file writes, not arbitrary side effects. And the most
important rule in the list — do not map fixed point to `double` — cannot be
expressed as a permission at all, because it is a judgement about meaning.

> Enforce what the platform can enforce. Reserve prose for judgement.

## The defect our own suite missed

The worked example declares:

```ada
type Celsius is delta 0.1 digits 6 range -80.0 .. 150.0;
```

Our finished C++ checked that range on parsed input only. A reading of 150.0
from a sensor with a +1.5 calibration offset therefore became 151.5 and
printed a clean report, where the Ada program raises `Constraint_Error` and
exits 2. All three parity cases passed. The answer key was breaking the
skill's own "never drop a run-time constraint check" rule, and the evidence
was too thin to notice.

The fix was two more cases: one where the constraint fails on a *computed*
value, and one where a missing input file fails before any parsing, raising
an exception that is not the program's own.

What the story is about:

- The gate was right. The evidence was too weak to catch its violation.
- Coverage gaps do not look like gaps from the inside. They look green.
- A rule that no test case can falsify is a rule you are trusting on faith.

## Ada → C++ idiom map

The traps are the entries that compile cleanly and give wrong answers.

| Ada | C++ | Notes |
| --- | --- | --- |
| `package P`, child `P.C` | `namespace p`, `p::c` | one header per spec, one source per body |
| `private` part of a spec | private members / pimpl | nothing body-private in the header |
| abstract tagged type | abstract class, `virtual` + `override` | dispatching is not automatic |
| `access T'Class` | `T*` or `std::unique_ptr<T>` | decide ownership explicitly |
| discriminated record, variant part | `std::variant` of payload structs | or a tagged struct if the discriminant is read |
| generic package / subprogram | template | instantiate explicitly if you want the errors early |
| `type T is range 1 .. 99` | `int` plus an explicit check | **trap**: check wherever a value is produced, not only on input |
| `subtype S is T range A .. B` | same | the check does not come for free |
| `delta 0.1 digits 6` | scaled integer (`int` tenths) | **trap**: exact decimal, *not* `double` |
| `array (Positive range <>)` | `std::vector` | **trap**: Ada arrays are commonly 1-based |
| `String (1 .. N)` | `std::string` | **trap**: fixed-length, blank-padded, and the padding is visible |
| `raise E with "msg"` | `throw` | **trap**: the message text is observable output |
| `Integer'Image` | manual formatting | **trap**: leading blank for non-negatives |
| `Ada.Text_IO.Put_Line` | `std::cout << … << '\n'` | keep stdout and stderr on the same streams |
| `mod` vs `rem` | `%` matches `rem` | **trap**: `mod` differs for negative operands |
| unhandled exception at top level | catch, print, exit | match both the text and the exit status |
| task / protected object | `std::thread` / `std::mutex` | needs a deterministic harness before any of this is testable |

## Per-package definition of done

- [ ] every entity exported by the spec exists in the header; nothing
      private to the body leaked into it
- [ ] every exception the package can raise is declared and reachable, with
      the same message text
- [ ] every subtype constraint enforced in this package has an explicit
      check with the same observable effect, applied to computed values as
      well as inputs
- [ ] constraints that only a not-yet-translated package enforces are
      written down as deferred obligations and closed before the
      dependency-closure gate
- [ ] new sources are in the build; it compiles at the project's warning
      level with no new warnings
- [ ] no parity case that was passing before this package now fails
- [ ] no reference output, legacy source or test was modified
- [ ] no fixture name, expected output or test-specific branch appears in
      the migrated sources; nothing reads or generates from the captured
      output at build or run time; nothing invokes, links to or wraps the
      legacy program

## Starting on your own codebase

1. Pick **one runnable slice** — not the system. Verify its build and run
   commands yourself, not from memory.
2. Capture stdout, stderr and exit status for four or five cases chosen by
   failure mode. If the program is not deterministic — timestamps, hash
   ordering, concurrency — making it deterministic is task one, and it is
   worth doing even if the migration never happens.
3. Write `SKILL.md`: a description written as a trigger, a numbered loop
   that does one package at a time, the gate list, and a reporting format.
   Put the idiom map and the checklist in files beside it.
4. Attack it in a fresh conversation. Ask it to relax a type "for now", to
   edit the captured output to match, to special-case a fixture because you
   are short on time. **A refusal is the passing result.** A gate that folds
   under mild pressure is decoration — rewrite it as an absolute and probe
   again.
5. Add `permissions` for what the platform can enforce, and commit the
   folder so the method ships with the code.

## A skeleton to start from

This is deliberately a skeleton rather than a finished skill. The gates
transfer between migrations; the idioms, the build commands and the cases do
not, and a skill copied wholesale carries someone else's assumptions into
your codebase without saying so.

```markdown
---
name: <legacy>-to-<target>-migration
description: Migrate <legacy> to <target> with parity proven against
  captured reference output. Use for any port/translate/rewrite request.
permissions:
  deny: [Write(<reference output>/**), Write(<legacy sources>/**)]
  ask:  [Write(<tests>/**)]
---

# <Legacy> to <target> migration

## Preconditions
Trusted reference output exists and its provenance is known; the parity
suite runs and is red for the expected reason. If either is untrue, stop
and report — do not begin translating.

## Procedure
1. Inventory the units and order them by dependency.
2. Take the next unit. Translate its interface, then its implementation.
3. Build the whole tree at the project's warning level.
4. Run the parity suite. Apply the per-unit checklist.
5. Report the unit, its deferred obligations, and the suite state. Then
   the next unit.

## Gates
<the never-list, verbatim, with no escape hatches — the eight above,
plus the ones specific to your languages>

## Stage gates
<per unit / dependency closure / completion, as above>

## Reporting format
What was translated, what is deferred and why, which cases are red.
---
```

Beside it, in the same folder: `reference/idiom-map.md` with the mapping
table for your language pair, and `checklists/per-unit.md` with the
definition of done. `SKILL.md` holds the procedure; the detail lives next to
it and is read when it is needed.

## The three things

1. The **description** decides whether the skill exists in practice.
2. The **gates** decide whether its output can be trusted — enforce the ones
   the platform can enforce, and assume the list is one loophole short.
3. The **evidence** decides whether the migration is real, and how good the
   evidence is decides what the gates are worth.
