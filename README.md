# ADA-Workshop

Hands-on workshop: **build a skill in Devin Desktop that migrates Ada to
C++17 with proven behavioural parity.** 60 minutes.

The migration is the example. The skill is the deliverable.

## Attendees start here

1. Open `workshop/lab.html` in a browser — the whole lab on one page:
   setup, concepts, and every prompt with a copy button. Works offline
   straight from your clone.
2. Verify your environment (this **must** show 3 failing tests):

```bash
cmake -S cpp -B cpp/build
cmake --build cpp/build
ctest --test-dir cpp/build --output-on-failure
```

Warnings are errors on request: configure with `-DPARITY_WERROR=ON` to build
the migration under `-Werror` / `/WX`.

You need Devin Desktop 3.9.19 or newer (the material targets the **Devin
Local** agent; Cascade was removed in that release), CMake 3.16+ and a C++17
compiler. An Ada toolchain is **not** required — the reference outputs are
committed in `golden/`.

## Presenters start here

- `workshop/slides.pdf` — the deck (source: `workshop/slides.md`, Marp)
- `workshop/talk-track.md` — speaker notes, timings, and the questions you
  will get

Rebuild the deck after editing the source:

```bash
npx @marp-team/marp-cli@latest --pdf workshop/slides.md -o workshop/slides.pdf
```

The attendee page is generated — edit `workshop/src/lab.md`, never
`workshop/lab.html`:

```bash
pip install markdown
python3 workshop/build_lab.py            # regenerate
python3 workshop/build_lab.py --check    # fail if the page is stale
pytest workshop/test_build_lab.py
```

## Layout

| Path | What it is |
| --- | --- |
| `ada/` | Reference implementation: 5 packages, ~450 lines. Read-only during the lab. |
| `golden/` | Captured stdout, stderr and exit status of the Ada program — the specification. |
| `cpp/` | Where the migration goes: a stub `main.cpp` plus the parity harness. |
| `workshop/lab.html` | The attendee page (generated from `workshop/src/lab.md`). |
| `workshop/` | Slides, talk track, and the attendee page generator. |

## The answer key

The finished skill and a completed migration live on the **`solution`
branch**, not here. Keeping them off this branch is deliberate: the lab opens
by asking the agent to read the repository, and an agent that finds a
finished `SKILL.md` while orienting itself has nothing left to teach.

```bash
git fetch origin solution
git show origin/solution:solution/ada-to-cpp-migration/SKILL.md

# or check it out beside your clone, leaving your work untouched
git worktree add ../ada-workshop-solution origin/solution
```

The `solution-v1` tag pins the version a given cohort was shown. The branch is
this branch plus `solution/`; rebase it when the lab materials change, so the
answer key never drifts from the sample it answers.

## Running the reference implementation (optional)

Requires GNAT (`sudo apt-get install gnat`, or Alire on macOS/Windows):

```bash
make -C ada run           # build and run against ada/data/readings.csv
make -C ada check-golden  # verify golden/ still matches, changing nothing
make -C ada golden        # rewrite golden/ — maintainer-only, and only when
                          # the Ada sources changed on purpose
```

A migration verifies with `check-golden`; it never runs `golden`. Build
artefacts go to `.ref-build/` at the repo root, so verifying the reference
never writes inside `ada/`.

## Checking the solution

From a checkout of the `solution` branch:

```bash
cmake -S solution/cpp -B solution/cpp/build
cmake --build solution/cpp/build
ctest --test-dir solution/cpp/build --output-on-failure   # 3/3 pass
```
