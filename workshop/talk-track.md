# Talk track — "Teaching Devin a migration"

Speaker notes for `slides.pdf` (23 slides, 60 minutes). Timings are cumulative
"end by" marks. Everything in *italics* is stage direction, not script.

**Room requirements:** attendees have Devin Desktop **3.9.19 or newer** signed
in (Cascade was removed in that release; this material targets the Devin Local
agent), the repo cloned and opened as a workspace, and CMake + a C++17
compiler. Ask them to run the verify command from `workshop/lab.html` *before*
the session; budget 3 minutes at the top for stragglers if you did not.

**Two structural rules for running this on time:**

1. **Hands on keyboards by minute 12.** The first nine minutes are the only
   teaching block. If you are behind at slide 8, cut slide 6 and the room
   question on slide 3 — not the lab.
2. **The Probe starts at minute 44.** It is the payoff. If the migration in
   Prompt 3 is going badly, stop it mid-package and move on; a half-migrated
   package is a perfectly good thing to attack.

Slides 15–17 are talk-over-the-room slides: the attendees are working through
Prompts 2 and 3 while you narrate. Do not stop the room to present them.
Slide 14 is the exception — stop the room for it.

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

## Slide 3 — The problem with "just prompt it" · by 0:03

This is the persuasion slide. One minute — resist the discussion.

*Ask the room:* "How many packages, modules or files are in the migration you
actually care about?" Take **one** answer, multiply, move on.

> "Every one of those repeats the same dozen decisions and the same handful
> of traps. A prompt re-derives them from scratch, in a fresh context, with a
> different engineer at the keyboard. That variance is the whole cost of a
> migration."

Key line:

> "A skill is the difference between knowing how to do the migration and the
> project knowing how to do the migration."

---

## Slide 4 — Skills in 90 seconds · by 0:05

Mechanics, fast. Do not linger — they will absorb the layout when they create
the folder in seven minutes.

Three points that matter:

- It is a folder, not a file. Checklists and reference tables live beside
  `SKILL.md` — that is what makes skills more than a saved prompt.
- Project skills are committed. Your team gets it, and so does every future
  session, including cloud Devin sessions on the same repo.
- Two triggers, both on by default: the agent invokes it when the description
  matches, and you can invoke it yourself with `/ada-to-cpp-migration`.

*If anyone is on an older build and sees Cascade in the agent picker:* have
them switch to Devin Local or update. `@mention` was the Cascade syntax and
Cascade is gone as of 3.9.19.

---

## Slide 5 — Progressive disclosure · by 0:07

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

## Slide 6 — Skill vs rule · by 0:07

Thirty seconds, and the first thing to cut if you are behind.

> "`AGENTS.md` is always-on project guidance, so it has to be short and
> universally true; rules can be configured with other activation behaviours.
> A skill is procedural context that loads when it is relevant and brings its
> supporting files with it. A migration procedure is long and conditional,
> and you want it to fire even when the engineer has forgotten it exists.
> That is a skill."

*If someone asks about Workflows:* they were a Cascade feature and Devin Local
does not have them. The replacement is a skill you invoke with a slash
command.

---

## Slide 7 — The sample · by 0:08

*Have `ada/src/telemetry.ads` open on screen.*

> "Five packages, about 450 lines. Sensor readings in, calibration, summary,
> alert rules."

Then the honest bit:

> "I did not pick this because it is realistic. I picked it because every
> construct in it has a plausible wrong translation. Fixed point, tagged
> types, variant records, generics, constrained subtypes, and exception
> messages that get printed. Your codebase has its own list. The lab is how
> you discover it."

---

## Slide 8 — `golden/` is the specification · by 0:09

Slow down for thirty seconds. This is the technical heart.

> "Before a line of C++ existed, we ran the Ada program and captured stdout,
> stderr and the exit status for three cases. Those files are the spec."

> "Notice what is being compared: all three streams, byte for byte. Not 'the
> output looks right'. Not a test the agent wrote for itself — a test whose
> expected values it cannot have influenced, because they were produced by
> the program it is replacing."

The line to repeat:

> "A migration that compiles is not a migration that works. A migration that
> matches the goldens is evidence."

Then the caveat, in one breath, before an engineer supplies it for you:

> "Evidence for the behaviour these three cases cover. Characterization, not
> proof of equivalence. On a real migration, how many cases you capture is a
> decision you make on purpose."

*If asked "what about programs with no CLI output?":* the harness moves, the
principle does not — capture whatever is observable and deterministic (API
responses, a database dump, emitted files), and if nothing is deterministic,
making it deterministic is the first task of the migration.

---

## Slide 9 — Verify your starting state · by 0:11

*Run it live, on the projector, and let them see three red tests.*

> "Three failures. That is the correct starting state — and it is a real
> check, not ceremony. If the suite were green right now, it would be
> comparing nothing, and you would not find out until the end."

*Sweep the room:* everyone should have three red tests. This is the last
moment where a broken environment is cheap to fix. Anyone still broken pairs
with a neighbour — do not debug one laptop in front of thirty people.

*While the room settles, have them send Prompt 0.* It reads the repo and
changes nothing, so it is safe to run unattended and it warms up the
workspace index.

---

## Slide 10 — The lab · by 0:12

Set expectations for the next 45 minutes.

> "Open `workshop/lab.html` from your clone — the whole lab is on that one
> page and every prompt has a copy button. Paste them verbatim the first time
> through — each one is shaped deliberately, and the notes under them explain
> the shape. I will call time at each step and demo my version, so you can
> stay with the group even if yours diverges."

---

## Slide 11 — Prompt 1, draft · lab work to 0:22

*Send Prompt 1 on the projector, then let them work. Circulate.*

> "Look at what the prompt demands: the description specified separately, the
> commands literal, and 'do not include anything you have not verified by
> reading the repo'. Skills fail most often by being generically true and
> specifically useless."

Point out the precondition wording, because it is a trap people repeat:

> "The precondition is 'trusted reference output with known provenance', not
> 'the Ada build runs'. Almost nobody in this room has GNAT installed. If you
> write a precondition your users cannot satisfy, you have written a skill
> that stops on step one and blames them."

*Common thing to catch while circulating:* a `SKILL.md` full of statements
like "write clean, maintainable C++". Tell them to delete every line that
would be true of any project. What remains is the skill.

---

## Slide 12 — Your turn, name three gates · by 0:24

*Hands off keyboards. Two minutes, and worth every second.*

> "You are about to trust this thing across hundreds of files while you are in
> a meeting. What are three things it must never be allowed to do in order to
> get a green test?"

Take **two** answers and supply the rest yourself — with thirty people this
becomes a five-minute discussion if you let it. You will reliably get "change
the expected output" and "delete the test". Then ask the sharper question
yourself: "how would *you* make three tests pass in one minute without doing
the migration?" That gets you to hard-coding the fixture, and to its cousin:
shelling out to the Ada binary.

> "Keep your list. Mine is on the next slide and it is not more correct than
> yours — it is just the one I have already run. The skill you write for your
> own migration will need gates nobody in this room can guess."

---

## Slide 13 — Prompt 2, the part that does the work · lab work to 0:34

> "Everything so far was scaffolding for these prohibitions."

Read two or three of the gates aloud, deliberately flatly, so the absoluteness
is audible.

---

## Slide 14 — The gate that deadlocks · stop the room, 90 seconds

Hands off keyboards for this one. It is the strongest conceptual lesson in
the hour and it does not survive being narrated at people staring at a
terminal.

Walk it as a sequence and let them answer step 3:

1. the first package is translated
2. the executable is still incomplete
3. so what do the three end-to-end parity tests do? — *stay red*
4. therefore "never advance while anything is red" is unsatisfiable
5. therefore gates must be scoped to lifecycle stage

> "'Never advance while any parity case fails' sounds like the most rigorous
> rule on the list. It is a deadlock. The suite is end-to-end — it cannot go
> green until the last package lands — so an agent that obeys that sentence
> literally refuses to start package two and reports that it is blocked."

> "The fix is not to soften it, it is to say *which* check applies *when*:
> per package, nothing that was passing may start failing; once the whole
> dependency closure exists, the suite must be green; and never call the
> migration done with a red suite."

Land the general point:

> "You cannot find that bug by reading your skill. It reads beautifully. You
> find it by running it — which is why the last third of this hour is testing,
> not writing."

> "And we are catching it together, here, instead of letting thirty machines
> discover it independently in ten minutes. A skill is a program. It has
> failure modes, and this is one of them."

---

## Slide 15 — Why prohibitions beat instructions · talk over the room

> "'Prefer not to modify golden files' is a preference. It competes with
> everything else in the context window, and the thing it competes with is a
> failing test the agent is trying to make pass. 'Never edit anything in
> golden/' is a gate: the agent can check it, and so can you, in review, in
> ten seconds."

> "Here is the test: if you cannot phrase it as *never* or *stop and report*,
> it is not a gate. That does not make it worthless — it makes it reference
> material. Put it in the idiom map."

---

## Slides 16–17 — The idiom map and a real trap · talk over the room

> "The traps are the entries that compile cleanly and give the wrong answer.
> Those are the only entries worth writing down; the agent already knows
> `package` becomes `namespace`."

*Slide 17, walk the concrete case:*

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

## Slide 18 — Prompt 3, the real test of the description · lab work to 0:44

*New conversation on the projector. Send the one-line prompt.*

> "Watch the conversation, not the code. Did the skill load before it started
> writing? That is the whole assertion."

If it fires:

> "It fired on a prompt that never named it. That means it will fire for the
> engineer who joins in March and has never heard of it. That is what you
> built."

If it does not fire — and let it happen if it happens:

> "Perfect, this is the failure I wanted you to see. The bug is in the
> description, not the prompt. Do not fix it by typing the slash command; that
> just hides the defect. A skill you have to remember to invoke is a skill
> your team will not use. Rewrite the description with the words a real
> request uses."

*Call time at 0:44 regardless of where anyone is.* An unfinished package is a
fine thing to attack in the next step.

---

## Slide 19 — Prompt 4, attack your own gates · to 0:53

**Protect this slot.** Demo it live, one probe at a time.

> "Three prompts. All three are things a tired engineer says at 6pm on a
> Friday. One edits the specification. One takes on unbounded numeric risk
> with a promise to fix it later. One fakes the output entirely."

*If the slot is running short, cut to the third probe.* It is the most
concrete and the most memorable, and the first two can be demonstrated
centrally in thirty seconds each.

*Send the golden-file prompt. Read the refusal out loud, including the gate
it cites.*

> "That refusal is the deliverable. Not the C++."

On the third probe, make the point explicitly:

> "This is the one your test suite cannot catch. Detect the fixture, print the
> expected bytes, three green tests, zero migration. Every gate before this
> was about doing the work correctly; this one is about doing the work at
> all."

*If someone points out that a gate against hard-coding does not stop the
program simply opening `golden/report.stdout` and copying it out, they are
right, and they have found the reason the prohibition names build time and
run time as well as literal bytes.*

> "If yours complies — and some of yours will — you have learned the most
> valuable thing available today: your gate was decoration. Rewrite it as an
> absolute and re-run the probe in a fresh conversation. You are testing the
> skill, not the model."

---

## Slide 20 — Prompt 5, stop asking nicely · to 0:57

The conceptual turn at the end of the hour. **Drive this one yourself** —
attendees who are caught up can follow along, but do not make thirty people
edit YAML, open a conversation and diagnose a non-firing skill in the last
five minutes.

Invoke the skill explicitly for the re-probe (`/ada-to-cpp-migration`, then
the golden-file request). Discovery was tested in Prompt 3; this step is
about enforcement, and an explicit invocation makes the demo deterministic
instead of hoping the skill fires on a prompt that is not a migration
request.

> "Everything you just watched depended on the model agreeing with you. It did
> agree — but 'it agreed' is not a control."

*Show the permissions block, then re-run probe 1 in a fresh conversation.*

> "Now the write is denied by the platform. Not declined, denied. It does not
> matter how good my excuse is."

Be accurate about the layer, because someone will test it later:

> "This is a tool-level guardrail, not OS-level filesystem isolation. Shell
> side effects are governed separately. Prose rule, tool guardrail, sandbox —
> three different strengths, and it is worth knowing which one you have."

Point at the `ask` entry too:

> "The harness is `ask`, not `deny`. Adding a parity case is legitimate;
> weakening one is not; no path rule can tell those apart. What it can do is
> make the change impossible to do quietly."

Then the important half:

> "And look at what you cannot enforce this way. 'Do not turn fixed point into
> a double' is a judgement about meaning — there is no permission for it. So
> the rule is: enforce what the platform can enforce, and spend your prose on
> the judgements that are left. If you find yourself writing a gate that a
> permission could have covered, you are asking nicely for something you could
> have made impossible."

---

## Slide 21 — What "done" looks like · by 0:58

Show the folder. Note the shape: short `SKILL.md`, bulk in supporting files,
enforcement in the frontmatter, all committed.

> "Committed means the next engineer starts here, and so does every future
> session on this repo — including cloud sessions. The skill is the artefact
> that outlives the conversation."

---

## Slide 22 — Prompt 6, take it home · by 0:59

This one is homework, and say so plainly rather than starting something you
cannot finish.

> "The last prompt is yours to run tonight. It makes the skill generic, and
> then asks it what got weaker — and something always does. Generic skills are
> weaker skills. Keep the specific one in the repo it serves and let each
> team's traps accumulate in their own idiom map."

Point at the step that transfers:

> "If your legacy program has no deterministic observable behaviour, making it
> deterministic *is* the first migration task. That is true for COBOL,
> Fortran, VB6 and Delphi as much as Ada."

Also tell them where the answer key is:

> "The finished skill and a complete migration are on the `solution` branch —
> deliberately not on the branch you were working on, so your agent could not
> read the answer while orienting itself. The commands are at the bottom of
> the lab page."

---

## Slide 23 — The three things · by 1:00

Land it and stop.

> "The description decides whether the skill exists in practice. The gates
> decide whether you can trust the output — and enforce the ones that can be
> enforced. The evidence, byte-for-byte golden output, decides whether the
> migration is real. Everything else on these slides is detail."

---

## Appendix — questions you will get

**"Why not let it write its own tests instead of goldens?"**
Self-written tests encode the agent's understanding of the code, which is
exactly the thing under test. Goldens come from the program being replaced.
Use both — but only one of them is evidence.

**"Three cases isn't much coverage."**
Correct, and say so. Three is enough to teach the method and to catch the
traps I planted. On a real migration the case count is a deliberate decision;
the harness is what makes adding the fiftieth case cheap.

**"Isn't this just a very long prompt?"**
Structurally, yes. Operationally, no: it is versioned, reviewed, shared,
loaded automatically when relevant instead of when remembered, and — with
`permissions` — able to deny actions rather than discourage them.

**"How big should a skill be?"**
`SKILL.md` short enough to read in a sitting; everything else in supporting
files that load only when the skill fires.

**"Can we enforce these gates instead of asking for them?"**
Partly, and that is slide 20. `permissions` in the frontmatter denies writes
to paths at the tool level; CI running the parity suite catches the rest. The
prose gates cover what neither can express. Do not overclaim: a denied write
tool is not a sandbox.

**"Couldn't it just call the Ada binary from C++ and pass everything?"**
Yes, and it is the best question in the deck — no hard-coded fixture, no
golden file read, three green tests, zero migration. That is why the gate
list forbids wrapping, linking to or shelling out to the reference program.
Every characterization suite has this hole; the gate is the only thing that
closes it.

**"What is the difference between `allowed-tools` and `permissions`?"**
`allowed-tools` narrows which tools the skill may use at all; `permissions`
allows, denies or prompts for specific scopes such as `Write(golden/**)`. Use
`allowed-tools` for read-only skills, `permissions` for surgical prohibitions.

**"Our migration target isn't Ada."**
Everything here is language-agnostic except the idiom map. Replace it, keep
the loop, the gates, the harness and the probes.

**"What about tasking / concurrency?"**
Not exercised by this sample, deliberately. Concurrency changes observable
ordering, so the deterministic harness has to come first. The idiom map has
the mappings and the warning.
