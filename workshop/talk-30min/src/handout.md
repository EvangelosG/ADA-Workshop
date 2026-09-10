# Skills that can be trusted with a migration

How to write a Devin skill that migrates Ada to C++ and can be trusted with
the result. It carries the reference material — the idiom map, the gate
list, the per-unit checklist and a skeleton `SKILL.md` — inline, so it is
usable with nothing to clone and nothing to install.

No prior experience with AI tools is assumed. Everything here applies to an
Ada codebase you already have and are already allowed to build; the
examples use invented file names so that nothing depends on a repository
you cannot see.

## What a skill is

A skill is a folder of markdown files. No plugin, no configuration screen,
no code:

```
your-repo/
  .agents/
    skills/
      ada-to-cpp-migration/
        SKILL.md                  <- the procedure and the rules
        reference/idiom-map.md    <- Ada construct -> C++ construct
        checklists/per-unit.md    <- what "done" means for one package
```

You write these in any text editor and commit them like source. `SKILL.md`
starts with **frontmatter** — the block between the `---` lines — and
continues in plain English:

```markdown
---
name: ada-to-cpp-migration
description: Migrate Ada (.ads/.adb) to C++17 with parity proven against
  captured reference output. Use for any port/translate/rewrite request.
---

## Preconditions   what must be true before starting
## Procedure       numbered steps, one package at a time
## Gates           the things it must never do
## Reporting       what to tell me when it stops
```

### How it gets used

You type an ordinary request — *port the Ada parser in src/parsing to
C++17* — and Devin compares it against the description of every skill it
can see, loads the one that fits and follows it. You will see the skill
named in the response; that is your confirmation. If it does not load, name
it yourself: `/ada-to-cpp-migration`.

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

### Where each thing you know goes

| What you know | Where you write it |
| --- | --- |
| when this method applies | `description` in the frontmatter |
| the order of work | **Procedure** section of `SKILL.md` |
| the things it must never do | **Gates** section of `SKILL.md` |
| what must be true before starting | **Preconditions** section |
| Ada construct → C++ construct | `reference/idiom-map.md` |
| the definition of done for one package | `checklists/per-unit.md` |
| paths nothing may write to | `permissions` in the frontmatter |

## Compilation is not migration

The question a migration has to answer is not "does it build" but "does it
still do the same thing". So the first artifact is not C++ — it is evidence.

Before writing any target code, run the legacy program on each case and save
its stdout, its stderr and its exit status:

```bash
./telemetry data/normal.csv  > expected/normal.out \
                            2> expected/normal.err ; echo $? > expected/normal.exit
```

Then have the test harness run the migrated binary on the same input and
compare all three, byte for byte. That is the definition of done: not a code
review, not a diff of the sources.

Be precise about what this buys you. A handful of cases is strong
**characterization evidence** for the behaviour those cases cover. It is not
proof that the two programs are equivalent, and someone will rightly say so
if you overclaim it. Pick cases by failure mode rather than by count:

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
2. **Copy the evidence.** Open the expected-output file at run time and echo
   it — `std::ifstream in("expected/normal.out"); std::cout << in.rdbuf();`
   This hard-codes nothing, so a rule that only forbids hard-coded output
   misses it entirely. Forbid build time too, or a generated header is the
   next move.
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
  deny:  [Write(expected/**), Write(ada/**)]     # never, no discussion
  ask:   [Write(tests/**)]                       # stop and ask me first
```

`deny` holds whether or not the model agrees. Tests are `ask` rather than
`deny` because adding a parity case is legitimate work and weakening one is
not, and no path pattern can tell those apart — so a human decides.

Two honest limits. This is a **tool-level guardrail**, not OS isolation: it
governs the agent's file writes, not arbitrary side effects. And the most
important rule in the list — do not map fixed point to `double` — cannot be
expressed as a permission at all, because it is a judgement about meaning.

> Enforce what the platform can enforce. Reserve prose for judgement.

## The defect that is easiest to ship

Take a declaration of the kind Ada codebases are full of:

```ada
type Celsius is delta 0.1 digits 6 range -80.0 .. 150.0;
```

The obvious C++ checks that range where the number is *read*. Ada checks it
on every assignment, including computed results — so a reading of 150.0
from a sensor with a +1.5 calibration offset becomes 151.5 and prints a
clean report, where the Ada program raises `Constraint_Error` and exits 2.

Every test passes, because none of them computes a value out of range. The
gate said "never drop a run-time constraint check" and it was being broken
in silence. The two cases that catch it: a constraint violated by a
*computed* value, and a missing input file, which fails before any parsing
with an exception that is not the program's own.

What the story is about, for your migration:

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
   commands yourself, not from memory, then list the Ada constructs it uses:
   fixed point, tagged types, discriminated records, generics, tasking.
   That list is your risk inventory and the first draft of your idiom map.
2. Capture stdout, stderr and exit status for four or five cases chosen by
   failure mode. If the program is not deterministic — timestamps, hash
   ordering, concurrency — making it deterministic is task one, and it is
   worth doing even if the migration never happens.
3. Write `SKILL.md`: a description written as a trigger, a numbered loop
   that does one package at a time, the gate list, and a reporting format.
   Put the idiom map and the checklist in files beside it.
4. Attack it in a fresh conversation, in the words you would actually use
   at 5pm:

   ```
   Just make the test pass for now, we are short on time.
   Use double for the temperature type, we can fix precision later.
   Update the expected output file to match what our C++ prints.
   ```

   **A refusal is the passing result.** A gate that folds under mild
   pressure is decoration — rewrite it as an absolute and probe again. Then
   check the trigger: describe the task in your own words in a new
   conversation and see whether the skill loads without being named.
5. Add `permissions` for what the platform can enforce, and commit the
   folder so the method ships with the code.

## A skeleton to start from

This is deliberately a skeleton rather than a finished skill. The gate list
transfers between migrations; the paths, the build commands and the cases do
not, and a skill copied wholesale carries someone else's assumptions into
your codebase without saying so. `expected/`, `ada/` and `tests/` below are
placeholders for whatever your project calls them.

```markdown
---
name: ada-to-cpp-migration
description: Migrate Ada (.ads/.adb) to C++17, proving each package against
  captured reference output. Use for any port/translate/rewrite request.
permissions:
  deny: [Write(expected/**), Write(ada/**)]
  ask:  [Write(tests/**)]
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
