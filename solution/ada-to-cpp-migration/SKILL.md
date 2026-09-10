---
name: ada-to-cpp-migration
description: Migrate an Ada codebase (or a single Ada package) to C++17 with behavioural parity proven against captured reference output. Use whenever the request involves translating, porting or rewriting .ads/.adb sources into C++, or extending an in-progress Ada to C++ migration.
---

# Ada to C++ migration

Translate Ada to C++ **one package at a time**, proving after every package
that the program still produces byte-identical output. A migration that
compiles is not a migration that works.

## Preconditions — check before writing any C++

1. A reference build of the Ada program exists and runs (`ada/Makefile`, a
   `.gpr` project, or `gnatmake`).
2. Reference outputs are captured in `golden/` — one `.stdout`, `.stderr` and
   `.exit` per case. If they are missing, generate them first
   (`make -C ada golden`) and commit them **before** changing anything.
3. `cmake --build cpp/build && ctest --test-dir cpp/build` runs and the parity
   tests fail for the expected reason (the C++ program is incomplete), not
   because the harness is broken.

If any precondition fails, fix it and stop. Do not translate code with no way
to detect a regression.

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
5. **Build with warnings as errors for the new files.** Fix warnings; do not
   silence them.
6. **Run the parity suite.** `ctest --test-dir cpp/build --output-on-failure`.
7. **Diff-driven debugging.** When a case fails, compare against the Ada
   source, not against your expectation of what the Ada source ought to do.
   Consult `reference/idiom-map.md` — most mismatches come from the rounding,
   ordering and formatting entries there.
8. **Commit the package** only when the whole parity suite is green.

Follow `checklists/per-package.md` before declaring a package done.

## Hard gates

These are not suggestions. Violating one means the migration is unverified.

- **Never edit `golden/` to make a test pass.** The reference output is the
  specification. If you believe a golden file is wrong, stop and ask.
- **Never edit the Ada sources.** They are the reference implementation.
- **Never weaken, skip, or comment out a parity test**, and never add a
  tolerance to a comparison that used to be exact.
- **Never move to the next package while any parity case fails.**
- **Never introduce floating point** where the Ada used a fixed point or
  integer type. See the fixed point entry in `reference/idiom-map.md`.
- **Never drop a run-time check.** An Ada subtype constraint that raises
  `Constraint_Error` must have an explicit C++ counterpart that produces the
  same observable behaviour.
- If a construct cannot be translated faithfully, **stop and report it** with
  the Ada source location. Do not approximate silently.

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
