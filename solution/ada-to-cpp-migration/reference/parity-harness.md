# The parity harness

The harness is the part of this skill that makes the migration trustworthy.
It exists before any C++ is written.

## What it does

For each reference case it runs the C++ executable and compares three things
against files captured from the Ada program:

- `golden/<case>.stdout`
- `golden/<case>.stderr`
- `golden/<case>.exit`

All three must match exactly. Exit status and stderr matter: a program that
prints the right report but returns the wrong status has not been migrated.

## Capturing the reference output

```
make -C ada golden
```

Regenerate only when the Ada reference implementation itself changes, and
review the diff — an unexplained change in `golden/` during a migration means
something is wrong.

## Running it

```
cmake -S cpp -B cpp/build
cmake --build cpp/build
ctest --test-dir cpp/build --output-on-failure
```

The runner is `cpp/tests/parity.cmake`, invoked through `cmake -P` so the
suite has no shell dependency and behaves the same on Windows.

## Adding a case

In `cpp/tests/CMakeLists.txt`:

```cmake
add_parity_test(<case_name> "<argument>")
```

then capture the matching golden files from the Ada build.

## How much the suite proves

A passing suite is characterization evidence for the behaviour its cases
cover, not proof that the two programs are equivalent. Treat coverage as a
deliberate decision: every case is a behaviour someone chose to pin down, and
every behaviour not pinned down is free to change silently.

The suite is also end-to-end, so it says nothing until the executable's
whole dependency closure exists. While the migration is partway through, the
useful signal is "no case that was passing has started failing", not "the
suite is green".

## What makes a good case set

- The happy path, exercising every output section.
- At least one rejected input per distinct error message.
- The usage/no-argument path.
- A boundary value for every constrained subtype in the Ada specs.
- A value that makes rounding visible: negative, and not exactly
  representable at the target scale.

## Non-deterministic programs

If the reference program prints timestamps, addresses, hash ordering or
anything scheduling-dependent, the harness must be made deterministic before
the migration starts — inject a clock, sort the output, or filter the volatile
lines in both runs. Never "fix" this by loosening the comparison.
