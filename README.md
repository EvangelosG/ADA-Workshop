# ADA-Workshop

Hands-on workshop: **build a skill in Devin Desktop that migrates Ada to
C++17 with proven behavioural parity.** 60 minutes.

The migration is the example. The skill is the deliverable.

## Attendees start here

1. `workshop/lab-guide.md` — setup, what is in the repo, the lab steps
2. `workshop/prompts.md` — the prompts to paste, in order
3. Verify your environment (this **must** show 3 failing tests):

```bash
cmake -S cpp -B cpp/build
cmake --build cpp/build
ctest --test-dir cpp/build --output-on-failure
```

You need CMake 3.16+ and a C++17 compiler. An Ada toolchain is **not**
required — the reference outputs are committed in `golden/`.

## Presenters start here

- `workshop/slides.pdf` — the deck (source: `workshop/slides.md`, Marp)
- `workshop/talk-track.md` — speaker notes, timings, and the questions you
  will get

Rebuild the deck after editing the source:

```bash
npx @marp-team/marp-cli@latest --pdf workshop/slides.md -o workshop/slides.pdf
```

## Layout

| Path | What it is |
| --- | --- |
| `ada/` | Reference implementation: 5 packages, ~450 lines. Read-only during the lab. |
| `golden/` | Captured stdout, stderr and exit status of the Ada program — the specification. |
| `cpp/` | Where the migration goes: a stub `main.cpp` plus the parity harness. |
| `solution/cpp/` | A completed migration that passes every parity case. |
| `solution/ada-to-cpp-migration/` | The finished skill. |
| `workshop/` | Slides, talk track, lab guide, prompts. |

The finished skill lives under `solution/` rather than `.agents/skills/` on
purpose: if it were in a skill directory, Devin Desktop would load it during
the lab and there would be nothing to build.

## Running the reference implementation (optional)

Requires GNAT (`sudo apt-get install gnat`, or Alire on macOS/Windows):

```bash
make -C ada run       # build and run against ada/data/readings.csv
make -C ada golden    # regenerate golden/ (only if the Ada sources change)
```

## Checking the solution

```bash
cmake -S solution/cpp -B solution/cpp/build
cmake --build solution/cpp/build
ctest --test-dir solution/cpp/build --output-on-failure   # 3/3 pass
```
