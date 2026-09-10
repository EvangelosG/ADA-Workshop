# Talk track — "Teaching Devin a migration"

Speaker notes for `slides.pdf` (20 slides, 60 minutes). Timings are cumulative
"end by" marks. Everything in *italics* is stage direction, not script.

**Room requirements:** attendees have Devin Desktop signed in, the repo cloned
and opened as a workspace, and CMake + a C++17 compiler. Ask them to run the
verify command from the lab guide *before* the session; budget 3 minutes at
the top for stragglers if you did not.

**The one thing to protect:** the Probe step at minute 45. If you are running
late, cut the migration short — never cut the probe. Everything else is
setup for it.

---

## Slide 1 — Title · by 0:01

Open with the framing, not the agenda.

> "By the end of the hour you will have written a skill that migrates Ada to
> C++ and, more importantly, you will have tried to break it and watched it
> hold. We are not going to finish a migration today. We are going to build
> the thing that makes finishing one boring."

---

## Slide 2 — What you leave with · by 0:02

Say the negative goal out loud. Engineers in a migration workshop will
otherwise spend the hour racing the compiler.

> "If you finish the migration today you probably did it by hand and learned
> nothing that scales."

---

## Slide 3 — The problem with "just prompt it" · by 0:05

This is the persuasion slide. Land it with their own numbers.

*Ask the room:* "How many packages, modules or files are in the migration you
actually care about?" Take two answers. Whatever the number, multiply.

> "Every one of those repeats the same dozen decisions and the same handful
> of traps. A prompt re-derives them from scratch, in a fresh context, with a
> different engineer at the keyboard. Sometimes it derives them differently.
> That variance is the whole cost of a migration."

Key line:

> "A skill is the difference between knowing how to do the migration and the
> project knowing how to do the migration."

---

## Slide 4 — Skills in 90 seconds · by 0:08

Mechanics, fast. Do not linger — they will absorb the layout when they create
the folder in ten minutes.

Three points that matter:

- It is a folder, not a file. Checklists and reference tables live beside
  `SKILL.md` — that is what makes skills more than a saved prompt.
- Workspace skills are committed. Your team gets it, and so does every
  future session, including cloud Devin sessions on the same repo.
- `.agents/skills/` is the cross-agent location; `.windsurf/skills/` also
  works. We use `.agents/` in this lab.

---

## Slide 5 — Progressive disclosure · by 0:11

The most important concept on the deck.

> "Until the skill fires, the model sees two strings: the name and the
> description. Nothing else. That has one consequence you must internalise —
> **the description is a trigger, not a summary.**"

> "Write it in the words of the request you expect. Not 'this skill contains
> our migration standards'. Rather: 'use when porting, translating or
> rewriting .ads/.adb sources to C++, including follow-ups on a migration in
> progress'."

Second consequence, briefly: length is cheap. Put the bulk in supporting
files; they cost nothing until the skill is invoked.

---

## Slide 6 — Skill vs rule vs workflow · by 0:13

Short. Someone always asks, so answer it before they do.

> "Rules are always in context, so they must be short and universally true.
> Workflows only run when you type the slash command. Skills load themselves
> when they are relevant. A migration procedure is long, conditional, and you
> want it to fire even when the engineer has forgotten it exists — that is a
> skill."

---

## Slide 7 — The sample · by 0:16

*Have `ada/src/telemetry.ads` open on screen.*

> "Five packages, about 450 lines. It reads sensor readings, calibrates them
> per sensor type, prints a summary and evaluates alert rules."

Then the honest bit:

> "I did not pick this because it is realistic. I picked it because every
> construct in it has a plausible wrong translation. Fixed point, tagged
> types, variant records, generics, constrained subtypes, and exception
> messages that get printed. Your codebase has its own list. The lab is how
> you discover it."

---

## Slide 8 — `golden/` is the specification · by 0:19

Slow down. This is the technical heart.

> "Before a line of C++ exists, we ran the Ada program and captured stdout,
> stderr and the exit status for three cases. Those files are the spec."

> "Notice what is being compared: all three streams, byte for byte. Not 'the
> output looks right'. Not a test the agent wrote for itself — a test whose
> expected values it cannot have influenced, because they were produced by
> the program it is replacing."

The line to repeat:

> "A migration that compiles is not a migration that works. A migration that
> matches the goldens is evidence."

*If asked "what about programs with no CLI output?":* the harness moves, the
principle does not — capture whatever is observable and deterministic (API
responses, a database dump, emitted files), and if nothing is deterministic,
making it deterministic is the first task of the migration.

---

## Slide 9 — Verify your starting state · by 0:21

*Run it live, on the projector, and let them see three red tests.*

> "Three failures. That is the correct starting state — and it is a real
> check, not ceremony. If the suite were green right now, it would be
> comparing nothing, and you would not find out until the end."

*Sweep the room:* everyone should have three red tests before you move on.
This is the last moment where a broken environment is cheap to fix.

---

## Slide 10 — The lab · by 0:23

Set expectations for the next 40 minutes.

> "Prompts are in `workshop/prompts.md`. Paste them verbatim the first time
> through — each one is shaped deliberately, and the notes under them explain
> the shape. I will call time at each step and demo my version, so you can
> stay with the group even if yours diverges."

---

## Slides 11–12 — Prompt 1 and Prompt 2 · lab work to 0:40

*Run Prompt 0 and Prompt 1 on the projector, then let them work. Circulate.*

While drafting (slide 11), the point to make:

> "Look at what the prompt demands: the description specified separately, the
> commands literal, and 'do not include anything you have not verified by
> reading the repo'. Skills fail most often by being generically true and
> specifically useless."

*Common thing to catch while circulating:* a `SKILL.md` full of statements
like "write clean, maintainable C++". Tell them to delete every line that
would be true of any project. What remains is the skill.

At Prompt 2 (slide 12):

> "This is the step that does the work. Everything so far was scaffolding for
> these eight prohibitions."

Read two or three of the gates aloud, deliberately flatly, so the absoluteness
is audible.

---

## Slide 13 — Why prohibitions beat instructions · by 0:42

The conceptual payoff of Prompt 2. Use the table.

> "'Prefer not to modify golden files' is a preference. It competes with
> everything else in the context window, and the thing it competes with is a
> failing test the agent is trying to make pass. 'Never edit anything in
> golden/' is a gate: the agent can check it, and so can you, in review, in
> ten seconds."

> "Here is the test: if you cannot phrase it as *never* or *stop and report*,
> it is not a gate. That does not make it worthless — it makes it reference
> material. Put it in the idiom map."

---

## Slides 14–15 — The idiom map and a real trap · by 0:46

> "The traps are the entries that compile cleanly and give the wrong answer.
> Those are the only entries worth writing down; the agent already knows
> `package` becomes `namespace`."

*Slide 15, walk the concrete case:*

> "`delta 0.1 digits 6` is decimal fixed point — exact. The obvious
> translation is `double`, and `double` will agree with the reference for
> most of your test data. Then the thermistor halves a negative, odd-tenths
> deviation, and the report prints 17.0 where the Ada printed 17.1. One line
> of one case."

> "Without the goldens, that ships. With them, it is a red test in the first
> minute. This is why the harness comes before the translation."

The C++ that passes: a scaled-integer wrapper — `int tenths`, truncating
division, formatting assembled from `magnitude/10` and `magnitude%10`.

---

## Slide 16 — Prompt 3, the real test of the description · by 0:52

*New conversation on the projector. Send the one-line prompt.*

> "Watch the conversation, not the code. Did the skill load before it started
> writing? That is the whole assertion."

If it fires:

> "It fired on a prompt that never named it. That means it will fire for the
> engineer who joins in March and has never heard of it. That is what you
> built."

If it does not fire — and let it happen if it happens:

> "Perfect, this is the failure I wanted you to see. The bug is in the
> description, not the prompt. Do not fix it by typing `@skill-name`; that
> just hides the defect. Rewrite the description with the words a real
> request uses."

*Let them run their own for the rest of the slot. It is fine if nobody
finishes a package.*

---

## Slide 17 — Prompt 4, attack your own gates · by 0:56

**Protect this slot.** Demo it live.

> "Two prompts. Both are things a tired engineer says at 6pm on a Friday, and
> both are reasonable-sounding. One asks it to edit the specification. One
> asks it to take on unbounded numeric risk with a promise to fix it later."

*Send the golden-file prompt. Read the refusal out loud, including the gate
it cites.*

> "That refusal is the deliverable. Not the C++."

> "If yours complies — and some of yours will — you have learned the most
> valuable thing available today: your gate was decoration. Rewrite it as an
> absolute and re-run the probe in a fresh conversation. You are testing the
> skill, not the model."

Close the loop:

> "This is what evaluating a skill looks like. You write it, you trigger it
> without naming it, and you try to talk it out of the rules. Three checks,
> five minutes, and you know whether it is real."

---

## Slide 18 — What "done" looks like · by 0:57

Show the folder. Note the shape: short `SKILL.md`, bulk in supporting files,
all committed.

> "Committed means the next engineer starts here, and so does every future
> session on this repo — including cloud sessions. The skill is the artefact
> that outlives the conversation."

---

## Slide 19 — Prompt 5, take it home · by 0:59

Give them the honest caveat:

> "Prompt 5 makes it generic, and then asks it what got weaker. Something
> always does. Generic skills are weaker skills — keep the specific one in
> the repo it serves and let each team's traps accumulate in their own idiom
> map."

Point at step 3 as the one that transfers:

> "If your legacy program has no deterministic observable behaviour, making it
> deterministic *is* the first migration task. That is true for COBOL,
> Fortran, VB6 and Delphi as much as Ada."

---

## Slide 20 — The three things · by 1:00

Land it and stop.

> "The description decides whether the skill exists in practice. The gates
> decide whether you can trust the output. The evidence — byte-for-byte
> golden output — decides whether the migration is real. Everything else on
> these slides is detail."

---

## Appendix — questions you will get

**"Why not let it write its own tests instead of goldens?"**
Self-written tests encode the agent's understanding of the code, which is
exactly the thing under test. Goldens come from the program being replaced.
Use both — but only one of them is evidence.

**"Isn't this just a very long prompt?"**
Structurally, yes. Operationally, no: it is versioned, reviewed, shared, and
loaded automatically when relevant instead of when remembered.

**"How big should a skill be?"**
`SKILL.md` short enough to read in a sitting; everything else in supporting
files that load only when the skill fires.

**"Can we enforce these gates instead of asking for them?"**
Enforce what you can — CI running the parity suite, and code review on
`golden/`. The gates make the agent's default behaviour right; CI makes the
outcome verifiable. Do both.

**"Our migration target isn't Ada."**
Everything here is language-agnostic except the idiom map. Replace it, keep
the loop, the gates, the harness and the probes.

**"What about tasking / concurrency?"**
Not exercised by this sample, deliberately. Concurrency changes observable
ordering, so the deterministic harness has to come first. The idiom map has
the mappings and the warning.
