# Talk track — 30-minute presentation

Speaker notes for `slides.pdf` in this folder (23 slides, 30 minutes).
Timings are cumulative and assume you start on time.

**Who this is written for.** Engineers who know Ada and have a migration in
front of them, and who may never have used an AI coding tool. Assume nothing:
the first third of the talk is "a skill is a folder with a markdown file in
it, and here is where it goes". Resist the urge to skip that because it feels
obvious — it is the part that makes the rest usable.

**Nothing on screen requires a repository of ours.** Every path, filename and
prompt in the deck is invented and generic on purpose, so the room never has
to wonder what they are missing. If someone asks whether there is a worked
example they can read, the honest answer is that the method is the
deliverable and the skeleton on slide 22 is the starting point.

**Budget.** What a skill is 0:00–0:14 · evidence 0:14–0:18 · gates 0:18–0:25 ·
take-home 0:25–0:30. If you are behind, cut the idiom-map slide and the
skill-vs-rule slide, in that order. Do **not** cut the loopholes slide, the
defect slide or "your first hour".

---

## 0:00 — Title

Say what the next 30 minutes buys them: a way to write down a migration
method once, so that it is applied the same way on package 200 as on package
one.

Set the expectation that this is not a product demo, and not a live coding
session. The audience has seen migration projects fail and is, correctly,
sceptical.

## 0:01 — What you should leave with

Two things, and say them plainly: what a skill is as files on disk, and how
to write one for their own Ada codebase.

Promise the ending explicitly — a skeleton and a first-hour plan — so nobody
spends the talk wondering whether it becomes practical.

## 0:02 — The problem with "just prompt it"

The point is repetition, not capability. Nobody doubts a model can translate
one package.

Ask for a show of hands: who has a migration in front of them right now? It
is the only audience interaction in the deck and it tells you how concrete to
be for the next 25 minutes.

The sentence to land: a fresh conversation has no memory of the last one, so
without a written method you re-derive it every time and get a slightly
different answer every time.

## 0:04 — A skill is a folder of markdown

Slow down here. For a room new to these tools this is the slide that
demystifies everything.

Read the tree aloud, literally: a hidden `.agents` folder in the repo, a
`skills` folder inside it, one folder per skill, and inside that a file
called `SKILL.md` plus whatever else you want beside it.

Then the two reassurances: you make these with any text editor, and you
commit them like source. There is nothing to install and nothing to register.

## 0:06 — What is inside `SKILL.md`

Name the frontmatter out loud — "the bit between the three dashes" — because
it is the only piece of syntax in the talk. Everything else is prose with
headings.

The four headings are the shape of every migration skill you will write:
preconditions, procedure, gates, reporting. You come back to them on slide 10
and again on slide 22.

## 0:07 — Where the folder goes

Two locations, one recommendation. In the repo is the answer; a global skill
in your home directory helps only you.

The line that matters for a mixed room: this is the same folder and the same
file whether you use Devin Desktop or the Devin CLI in a terminal. Neither
needs to be told the skill exists.

## 0:09 — How it actually gets used

The mechanics question everyone is quietly holding. Answer it concretely: you
type a normal sentence, Devin matches it against the descriptions it can see,
loads the one that fits, and you see the skill named in the response.

Then the fallback — slash the name to invoke it deliberately. If anyone asks
about Cascade or `@name`: removed in Desktop 3.9.19, Devin Local is the agent,
so slash.

Be honest about the limit: matching is a judgement about relevance, not a
keyword search, so it is not guaranteed. That is exactly why the next slide
matters.

## 0:10 — Only the description is always in view

The mechanism explains three things at once: why the description carries all
the weight, why long reference files are free, and why a beautiful `SKILL.md`
with a vague description effectively does not exist.

Give them the check to run later: open a fresh conversation, describe the task
the way they normally would, and see whether the skill loads unprompted.

## 0:12 — Skill or rule?

Thirty seconds. It exists so the "why isn't this just `AGENTS.md`?" question
does not arrive later, at a worse moment.

Rule: short, always read, universally true. Skill: long, conditional, carries
files, read when relevant.

## 0:13 — So where does each thing go?

This is the slide that answers the question a beginner is actually asking:
*I understand the ideas, but where does any of this get written down?*

Do not read the whole table. Point at three rows — the gate list goes in the
Gates section of `SKILL.md`, the Ada→C++ table goes in a file beside it, the
paths nothing may write to go in the frontmatter — and move on.

## 0:14 — Compilation is not migration

Slow down. This is the spine of the talk.

> "Before you write a line of C++, run the Ada program and save what it did:
> stdout, stderr, exit status. Those files are the specification."

Read the shell line literally; it is the most concrete instruction in the
deck and for many rooms it is the takeaway. Then qualify it before an
engineer does it for you: a handful of cases is evidence for the behaviour
those cases cover, not proof the two programs are equivalent. Saying it
yourself buys the credibility you spend on the defect slide.

## 0:16 — Choosing the cases

The list is the deliverable; the last two bullets are the ones people miss —
a failure *after* validation, and an exception whose message text is now
pinned down as observable output.

If the room's programs are not deterministic, this is where they will say so.
Agree loudly: making it deterministic is task one, and it is worth doing even
if the migration is cancelled.

## 0:18 — The gates: what it must never do

Read the list, do not paraphrase it. Ten prohibitions takes forty seconds and
the cadence is the point — every one is *never*, none is *prefer*.

Remind them where it goes: verbatim, into the Gates section.

If you are at or ahead of 0:18, ask first: *you are about to trust this
across hundreds of files — name three things it must never do to get a green
test.* Two minutes, and it makes the next three slides land harder.

## 0:19 — Why *never* and not *prefer*

The table is the slide people photograph. Give it a beat.

The authoring lesson: if you cannot phrase it as an absolute, it is guidance,
and guidance goes in a reference file where it does not dilute the gates.

## 0:20 — A gate that sounds right and stops all work

Tell it as a mistake, because it is a common one. "Never move on while any
test fails" sounds like discipline; the tests exercise the whole program, so
they stay red until the last package lands, and a literal-minded agent
refuses to start the second one.

The fix is scope, not softening: one gate per moment. Land the general lesson
— you find these by running the skill, not by reading it — because that is
what transfers to their own gate lists.

## 0:22 — Three ways to pass every test and migrate nothing

The best slide in the deck. Take two minutes, one per route.

1. Special-casing the input is the one people expect.
2. Reading the expected-output file at run time is the one that slips past a
   no-hard-coding rule, because it hard-codes nothing. Say that if you forbid
   only run time, a generated header at build time is the next move — which
   is why the rule names both.
3. Delegating to the Ada binary is the one that gets a laugh, and it is the
   worst: every test green, nothing translated, and the artifact still needs
   the compiler you were trying to retire.

Close with: assume your list is one loophole short. That is a posture, not a
criticism of any particular list.

## 0:24 — Some gates you can enforce, not just write

Sequence matters: you have just spent two minutes on rules that hold only
because the model cooperates. Now show the ones the tool enforces.

`deny` refuses the write regardless of the argument being made. Explain why
tests are `ask` — adding a test is honest, weakening one is not, and a path
pattern cannot tell them apart, so a human decides.

Be accurate about the limit: this governs file writes, not every possible
side effect, and "do not map fixed point to `double`" cannot be a permission
at all because it is about meaning.

## 0:25 — The traps are the whole job

Ninety seconds, and only if you are on time. Point at the fixed-point row,
because the next slide is about it.

The authoring lesson: this table lives in a file beside `SKILL.md`, loaded
when needed. Procedure in the skill, domain detail alongside.

## 0:26 — The defect that is easiest to ship

Tell it slowly; it is the most memorable minute in the talk.

Ada checks a subtype constraint on every assignment, including computed
results. The natural C++ checks it where the value is read. So a legal
reading plus a legal offset produces an illegal value, a clean report and a
zero exit status, where Ada raises `Constraint_Error` and exits 2.

Then the twist: every test passed, because no test computed a value out of
range. The gate was right and the evidence was too thin to catch the
violation. If you are asked whether this is hypothetical, say that it is the
mistake this kind of migration makes most often, and that it is worth
stealing as a test case on day one.

## 0:27 — Try to break your own skill

The most actionable slide for a room that has never used these tools. Read
the three shortcut requests aloud in a tired voice; they should recognise
themselves.

**A refusal is the passing result.** Say it twice. If it complies, the gate
was decoration.

## 0:28 — Your first hour

Six numbered steps. Read them; do not elaborate. This is the slide people
photograph on the way out.

If the room is going to do one thing, it is steps 1 and 2 — a runnable slice
and saved output — because everything else depends on them.

## 0:29 — A skeleton to start from

Say clearly that it is a skeleton on purpose: the gate list transfers between
projects, the paths and commands do not, and a skill copied whole carries
somebody else's assumptions into their codebase without announcing it.

Hand the page out here, not at the start — it is the deck's argument in
reading form, plus the idiom map, the checklist and the full skeleton.

## 0:30 — The three things

Close on the deck's own words and stop. Do not summarise the summary.

---

## If you are asked

**"Does this work with any other agent?"** The format described here is what
Devin Desktop and the Devin CLI read. The method — evidence first,
prohibitions, staged gates — is not tool-specific.

**"How long is a real skill?"** A page or two of `SKILL.md`, plus reference
files as long as they need to be. Length in `SKILL.md` costs attention;
length in a reference file does not, because it is read only when needed.

**"What if our program is not deterministic?"** Then that is the project,
before the migration. Pin timestamps, order iteration, remove concurrency
from the harness. It is worth doing on its own merits.

**"Can it just translate the whole thing and we review it?"** Review does not
scale past a few thousand lines and does not catch behaviour, only shape. The
comparison against saved output is what catches behaviour.

**"What does it cost to be wrong here?"** A migration that compiles, passes
review and quietly computes different numbers is more expensive than one that
never shipped. That is the argument for gates.
