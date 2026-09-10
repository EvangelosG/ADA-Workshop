---
name: ada-to-cpp-migration
description: Migrate an Ada codebase (or a single Ada package) to C++17 with behavioural parity proven against captured reference output. Use whenever the request involves translating, porting or rewriting .ads/.adb sources into C++, or extending an in-progress Ada to C++ migration.
permissions:
  deny:
    - Write(golden/**)
    - Write(ada/**)
  ask:
    - Write(cpp/tests/**)
---

# Ada to C++ migration

Translate Ada to C++ **one package at a time**, applying the gate for the
stage you are at after each one (see "Gates by stage"). Once the executable's
dependency closure exists, byte-identical output is required before
anything else. A migration that compiles is not a migration that works.

## Preconditions — check before writing any C++

1. Trusted reference outputs exist in `golden/` — one `.stdout`, `.stderr` and
   `.exit` per case — and their provenance is known: they were captured from
   the reference program, not written by hand or by a previous migration
   attempt.
2. If an Ada toolchain is available, verify them with `make -C ada
   check-golden`, which re-runs the reference program into a scratch
   directory and diffs. Never verify by regenerating in place: rewriting the
   goldens destroys the only record of what the program did before you
   started. If no toolchain is available, the committed goldens are
   authoritative — that is not a blocker, it is the normal case.
   If the goldens are missing entirely and cannot be generated, stop: there is
   no way to detect a regression.
3. `cmake --build cpp/build && ctest --test-dir cpp/build` runs and the parity
   tests fail for the expected reason (the C++ program is incomplete), not
   because the harness is broken.

## Migration loop

For each Ada package, in dependency order (leaves first):

1. **Read the spec before the body.** The `.ads` is the contract: exported
   types, subtype constraints, exceptions, generics, tagged types. Note every
   constraint — they become explicit checks in C++.
2. **Write the plan as a comment-free list** of the C++ files to add
   (`include/<unit>.hpp`, `src/<unit>.cpp`) and the mapping decisions taken
   from `reference/idiom-map.md`. Call out any construct with no direct C++
   equivalent and how you resolved it.
3. **Translate the spec first** (header), then the body (source).
4. **Add the new sources to `cpp/CMakeLists.txt`.**
5. **Build clean at the project's warning level**, and enable
   warnings-as-errors where the build supports it (`-DPARITY_WERROR=ON`
   here). Fix warnings; do not silence them.
6. **Run the parity suite.** `ctest --test-dir cpp/build --output-on-failure`.
   Record which cases pass, so the next package can be checked for
   regressions.
7. **Diff-driven debugging.** When a case fails, compare against the Ada
   source, not against your expectation of what the Ada source ought to do.
   Consult `reference/idiom-map.md` — most mismatches come from the rounding,
   ordering and formatting entries there.
8. **Apply the gate for this stage** (below), then commit the package.

## Gates by stage

The parity suite is end-to-end: it cannot pass until every package the
executable needs exists. Applying the final gate to an early package would
deadlock the migration, so the gate depends on where you are.

| Stage | What must hold before continuing |
| --- | --- |
| After each package | The tree builds clean at the project's warning level, the per-package checklist passes, and **no parity case that was passing has started failing**. |
| Once the executable's dependency closure is translated | The **whole** parity suite passes. While any case is red, fixing it is the only permitted work: no new package, no cleanup, no idiomatic refactoring, no next subsystem. Debugging the failure is not "further work", it *is* the work. |
| Completion | Never describe the migration as done, complete or ready for review while any parity case fails or any case has been skipped. |

When the program does not yet run end to end, say so explicitly in the report
rather than presenting a red suite as progress.

Follow `checklists/per-package.md` before declaring a package done.

## Hard gates

These are not suggestions. Violating one means the migration is unverified.

- **Never edit `golden/` to make a test pass.** The reference output is the
  specification. If you believe a golden file is wrong, stop and ask.
- **Never edit the Ada sources.** They are the reference implementation.
- **Never weaken, skip, or comment out a parity test**, and never add a
  tolerance to a comparison that used to be exact.
- **Never regress a parity case that was passing**, and never continue past a
  complete dependency closure with a red suite (see "Gates by stage").
- **Never make the program aware that it is under test.** No hard-coded
  expected output, no fixture filenames, no branch that behaves differently
  for `readings.csv`, and no reading of, embedding of or code generation
  from `golden/` at build time or run time. A green suite obtained this way
  is worse than a red one, because it hides the gap.
- **Never delegate the behaviour to the reference implementation.** The C++
  must implement the logic itself: no invoking, embedding, linking to or
  shelling out to the Ada program or any other compatibility layer. A shim
  passes every parity case and migrates nothing.
- **Never translate a fixed point or integer type to floating point.** See
  the fixed point entry in `reference/idiom-map.md`.
- **Never drop a run-time constraint check.** An Ada subtype constraint that
  raises `Constraint_Error` must have an explicit C++ counterpart with the
  same observable behaviour, enforced everywhere a value of that type is
  produced — results of arithmetic and conversions, not only parsed input.
- If a construct cannot be translated faithfully, **stop and report it** with
  the Ada source location. Do not approximate silently.

The first two gates are also enforced by the `permissions` block in this
file's frontmatter: writes to `golden/` and `ada/` are denied, and writes to
the harness under `cpp/tests/` require confirmation — adding a parity case is
legitimate, weakening one is not, and no path rule tells them apart. That is
a tool-level guardrail, not filesystem isolation; it constrains the write
tools, and shell side effects are governed separately. The remaining gates
are judgements about meaning — no permission can express "this fixed point
type must not become a `double`" — and depend on you honouring them.

## Conventions for the generated C++

- C++17, no external dependencies beyond the standard library.
- One namespace per Ada package; a child package `Parent.Child` becomes
  `parent::child`.
- Header per spec, source per body; header guards via `#pragma once`.
- Preserve the Ada identifier names in lower_snake_case so that a reviewer can
  diff the two trees side by side.
- Keep the C++ structurally parallel to the Ada, even where a more idiomatic
  C++ design exists. Idiomatic refactoring is a **separate, later** change;
  mixing it with the translation destroys reviewability.

## Reporting

At the end of each package, report exactly: the Ada units translated, the C++
files added, the parity cases run and their status, and every construct where
a faithful translation was not possible.
