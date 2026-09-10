# Talk track — 30-minute presentation

Speaker notes for `slides.pdf` in this folder (18 slides, 30 minutes).
Timings are cumulative and assume you start on time. This is the *no-lab*
edition: nobody in the room types, so the pacing risk is the opposite of the
workshop's — there is no natural pause, and it is easy to arrive at the last
slide with six minutes left and no plan for them.

The full hands-on version is `workshop/lab.html` (repo-based) and
`workshop/standalone.html` (attendees' own codebase). Do not try to run this
deck and a lab in the same 30 minutes.

**Budget.** Skills mechanics 0:00–0:09 · evidence 0:09–0:15 · gates
0:15–0:25 · take-home 0:25–0:30. If you are behind, cut the idiom-map slide
and the skill-vs-rule slide, in that order. Do **not** cut the loopholes
slide or the defect story; they are the reason the talk is not a features
tour.

---

## 0:00 — Title

One sentence on why you are the one giving this talk: you built the
migration, and the interesting part is what went wrong.

Set the expectation immediately that this is not a product demo. The
audience is engineers with Ada exposure; they have seen migration projects
fail and are, correctly, sceptical.

## 0:01 — What this session is

Say plainly that there is a hands-on version and this is not it. If your
room *could* do the lab later, tell them now — it changes how they listen.

> "Everything here comes out of building the thing and then finding out it
> was wrong. The last third of the talk is a defect in our own answer key."

## 0:03 — The problem with "just prompt it"

The point is repetition, not capability. Nobody in the room doubts that a
model can translate one package.

Ask for a show of hands: who has a migration in front of them right now?
It is the only audience interaction in the deck and it tells you how
concrete to be for the next 25 minutes.

## 0:04 — Skills in 90 seconds

Keep to 90 seconds. Read the frontmatter aloud, and land the description as
a *trigger* rather than documentation — you return to it twice later.

If someone asks about Cascade or `@name`: it was removed in Desktop 3.9.19,
Devin Local is the agent, and skills are invoked with `/name`.

## 0:06 — Desktop and CLI

This is the slide people came for if they use the terminal. It is short on
purpose: the honest answer is that it is the same folder and the same file,
which is the good news.

The line to land is *author it in the repo*. A skill in a home directory is
a personal shortcut; a skill in `.agents/skills/` is reviewable, versioned,
and shows up for the next engineer who clones.

## 0:07 — Progressive disclosure

The mechanism explains three things at once: why the description matters so
much, why supporting files are free, and why a beautiful `SKILL.md` with a
bad description effectively does not exist.

In the lab, attendees discover this by starting a fresh conversation and
typing one vague sentence. Here you can only assert it — so assert it as the
single most common defect, because it is.

## 0:08 — Skill vs rule

Thirty seconds. It exists to stop the "why isn't this just AGENTS.md?"
question from arriving later, at a worse moment.

## 0:09 — The worked example

Do not tour the code. The only load-bearing sentence is the last one: every
construct on the slide has a plausible wrong translation that compiles.

Name one for texture — `Integer'Image` puts a leading blank on
non-negatives, so a C++ port that "obviously" prints the number produces
different bytes and every test that looks at stdout goes red.

## 0:11 — Compilation is not migration

Slow down. This is the spine of the talk.

> "Before a line of C++ existed, we ran the Ada program and captured stdout,
> stderr and the exit status for five cases. Those files are the spec."

Then immediately qualify it, before an engineer in the room does it for you:
five cases are characterization evidence for the behaviour they cover, not
proof that the two programs are equivalent. Saying it yourself buys you the
credibility you will spend on the defect story later.

## 0:13 — The gates

Read the list, do not paraphrase it. Ten prohibitions takes forty seconds
and the cadence is the point — every one is *never*, none is *prefer*.

If you want the audience beat from the lab and you have the time, ask before
you reveal: *you are about to trust this across hundreds of files — what are
three things it must never be allowed to do to get a green test?* Budget two
minutes and only do it if you are at or ahead of 0:13.

## 0:15 — Why *never* and not *prefer*

The table is the takeaway slide people photograph. Give it a beat.

The last line matters for their own authoring: if you cannot phrase it as an
absolute, it is guidance, and guidance goes in a reference file where it
does not dilute the gates.

## 0:17 — The gate that deadlocks

Tell it as a mistake, because it was one. "Never advance while any parity
case fails" was in our first draft, it sounds like discipline, and an
obedient agent would have refused to start the second package — the suite is
end-to-end and cannot go green until the last one lands.

The fix is scope, not softening: per-package, at dependency closure, at
completion. Land the general lesson — **you find this by running the skill,
not by reading it** — because it is the one that transfers to their gate
lists.

## 0:19 — Three ways to a green suite

The best slide in the deck. Take three minutes, one per route.

1. Special-casing the fixture is the one people expect.
2. Copying the captured output at run time is the one that gets past a
   no-hard-coding rule, because it hard-codes nothing. Read the two lines of
   C++ aloud. Then note that if you forbid only run time, a build-time
   generated header is the next move — which is why the rule has to name
   both.
3. Delegating to the Ada binary is the one that makes people laugh, and it
   is the most dangerous: every case green, nothing migrated, and the
   artifact still depends on the compiler you were trying to retire.

Close with: assume your list is one loophole short. That is the posture,
not a criticism of any particular list.

## 0:22 — Prose vs enforced

Sequence matters: you have just spent three minutes on gates that are only
prose. Now show the ones the platform enforces.

`deny` holds whether or not the model agrees. Explain why tests are `ask` —
adding a parity case is legitimate, weakening one is not, and a path pattern
cannot tell those apart, so a human decides.

Be accurate about the limit: this is a tool-level guardrail, not OS
isolation, and it does not govern arbitrary side effects. And "do not map
fixed point to `double`" cannot be a permission at all — it is a judgement
about meaning, so it stays prose. That is the takeaway: enforce what can be
enforced, reserve prose for what cannot.

## 0:24 — The traps

Ninety seconds, and only if you are on time. Point at the fixed-point row
because the next slide is about it.

The authoring lesson: this table lives in a reference file the skill loads
when it needs it, not in `SKILL.md`. Procedure in the skill, domain detail
alongside it.

## 0:25 — The defect our own suite missed

Tell this one straight, including that it was ours.

The range check was on parsed input only. A reading of 150.0 on a sensor
with a +1.5 offset became 151.5 and printed a clean report, where Ada raises
`Constraint_Error` and exits 2. All three parity cases passed. The finished
answer key was violating the skill's own "never drop a run-time constraint
check" rule, and the suite could not see it.

Do not rush to the moral; let it sit for a second. Then: the fix was two new
cases — a constraint that fails on a *computed* value, and a missing file,
which fails before parsing with an exception that is not the program's own.

## 0:27 — What that story is about

The four bullets are the actual thesis of the talk. Read them.

The one to emphasise is the last: a rule no test case can falsify is a rule
you are trusting on faith. It reframes test design as gate design, which is
what you want them doing on Monday.

## 0:28 — Monday morning

Practical, deliberately small. The commonest failure is scope: someone
tries to characterise the whole system and never gets to step three.

Step 2 is where their real work is. If the legacy program is not
deterministic — timestamps, hash ordering, tasking — making it deterministic
is task one, and it is worth doing even if the migration never happens.

Step 4 is the part they will skip and shouldn't: attack the skill in a fresh
conversation and treat a refusal as the passing result.

## 0:29 — The three things

Close on the deck's own words and stop. Do not add a summary of the summary.

If you have the hands-on lab available, this is the moment to point at it,
and to say what it adds: in the lab they author the skill themselves and
watch their own gates fold under pressure, which no slide can do.

---

## Questions you should expect

**"How is this different from a long prompt?"** It persists, it is
versioned, it is reviewed like code, it loads only when relevant, and it can
carry files. A prompt is a conversation; a skill is an asset.

**"Won't the model just ignore the gates?"** Sometimes — which is why you
probe them, and why anything the platform can enforce goes in
`permissions` rather than prose. Be honest here; overclaiming loses the
room faster than admitting the limit.

**"Five test cases is nothing."** Correct, and that is the defect story.
The number is a decision you make deliberately per subsystem; the discipline
is picking by failure mode rather than by count.

**"Can it do the whole migration unattended?"** Not the question the talk
answers. What the skill buys you is that the parts it does are checkable,
and that it stops rather than guessing. Offer the deadlock story as evidence
that "stops" is a real behaviour, not an aspiration.

**"What about tasking / protected objects / real-time?"** Out of scope for
the example, and genuinely harder: the golden-output technique needs
deterministic observable behaviour, so concurrency usually means building a
deterministic harness first.
