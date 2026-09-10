"""Tests for the attendee page generator.

    pip install markdown pytest
    pytest workshop/test_build_lab.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_lab  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def page() -> str:
    return build_lab.render(build_lab.SOURCE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def standalone_source() -> str:
    return (build_lab.ROOT / "src" / "standalone.md").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def standalone(standalone_source: str) -> str:
    return build_lab.render(standalone_source, "standalone.md", interactive=False)


@pytest.fixture(scope="module")
def handout_source() -> str:
    return (build_lab.TALK / "src" / "handout.md").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def handout(handout_source: str) -> str:
    return build_lab.render(handout_source, "handout.md", interactive=False)


@pytest.fixture(scope="module")
def talk_slides() -> str:
    return (build_lab.TALK / "slides.md").read_text(encoding="utf-8")


def test_committed_page_is_up_to_date() -> None:
    result = subprocess.run(
        [sys.executable, "workshop/build_lab.py", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_page_is_offline_self_contained(page: str) -> None:
    """No external fetches: the room's wifi is not a dependency.

    Anchors may point anywhere; what must not appear is a subresource the
    browser has to download before the page renders.
    """
    assert not re.search(r"<script[^>]+\bsrc=", page)
    assert "<link" not in page
    assert not re.search(r"<img[^>]+\bsrc=\"https?:", page)
    assert not re.search(r"url\(\s*['\"]?https?:", page)
    assert "<style>" in page and "<script>" in page


def test_every_prompt_block_has_a_copy_button(page: str) -> None:
    source = build_lab.SOURCE.read_text(encoding="utf-8")
    expected = source.count("```prompt")
    assert expected >= 7
    assert page.count('class="copy"') == expected
    assert 'class="language-prompt"' not in page


def test_prompts_are_reproduced_verbatim(page: str) -> None:
    """A mangled prompt is a broken lab, so compare text exactly."""
    source = build_lab.SOURCE.read_text(encoding="utf-8")
    blocks = re.findall(r"```prompt\n(.*?)```", source, re.DOTALL)
    rendered = re.findall(
        r'<div class="prompt">.*?<code>(.*?)</code>', page, re.DOTALL
    )
    assert len(blocks) == len(rendered)
    for original, shown in zip(blocks, rendered):
        unescaped = (
            shown.replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&quot;", '"')
            .replace("&amp;", "&")
        )
        assert unescaped.strip() == original.strip()


def test_internal_links_resolve(page: str) -> None:
    ids = set(re.findall(r'id="([^"]+)"', page))
    targets = set(re.findall(r'href="#([^"]+)"', page))
    assert targets
    assert targets <= ids


def test_lab_covers_every_prompt(page: str) -> None:
    for step in range(7):
        assert f"Prompt {step} —" in page


def test_starting_state_is_documented_as_failing(page: str) -> None:
    assert "5 tests failed out of 5" in page


def test_lab_targets_devin_local_not_cascade(page: str) -> None:
    """Cascade was removed in Desktop 3.9.19; its syntax misleads the room."""
    assert "@ada-to-cpp-migration" not in page
    assert "/ada-to-cpp-migration" in page
    assert "~/.codeium/" not in page


def test_gate_prompt_separates_per_package_from_completion(page: str) -> None:
    """An unqualified "never advance while a test fails" deadlocks the lab.

    The parity suite is end to end, so it cannot pass until the last package
    lands. The hardening prompt has to scope the gate by stage.
    """
    assert "never report the migration as complete" in page.lower()
    assert "has started failing" in page


def test_lab_closes_the_delegate_to_ada_loophole(page: str) -> None:
    """A C++ shim around the Ada binary passes every case and migrates nothing.

    Nothing in the fixture or golden gates rules it out, so it needs its own.
    """
    assert "shelling out to the Ada program" in page


def test_golden_verification_never_rewrites_the_goldens() -> None:
    """The skill denies writes to golden/, so its verification step must not
    depend on regenerating them in place.
    """
    makefile = (ROOT / "ada" / "Makefile").read_text(encoding="utf-8")
    assert "check-golden:" in makefile

    lab = build_lab.SOURCE.read_text(encoding="utf-8")
    assert "make -C ada check-golden" in lab
    assert "make -C ada golden" not in lab


def test_warnings_as_errors_is_real_where_it_is_claimed() -> None:
    """Either the build enforces it or the material must not promise it."""
    cmake = (ROOT / "cpp" / "CMakeLists.txt").read_text(encoding="utf-8")
    assert "PARITY_WERROR" in cmake
    assert "-Werror" in cmake and "/WX" in cmake


def test_lab_teaches_enforced_as_well_as_prose_gates(page: str) -> None:
    assert "permissions:" in page
    assert "Write(golden/**)" in page


def test_standalone_page_runs_none_of_our_code(standalone: str) -> None:
    """Its whole premise is that nothing of ours executes on their machine.

    A copy button is JavaScript we wrote running in their browser, which the
    security review it exists to satisfy would read as exactly that.
    """
    assert "<script" not in standalone
    assert "onclick" not in standalone
    assert "<button" not in standalone
    assert "github.com" not in standalone
    assert "<link" not in standalone
    assert not re.search(r"<img[^>]+\bsrc=\"https?:", standalone)
    assert "<style>" in standalone


def test_standalone_page_needs_nothing_of_ours(standalone_source: str) -> None:
    """It exists for rooms that may not clone our repo or run our code.

    Anything that tells the attendee to fetch, unpack or execute material we
    supplied defeats its only purpose.
    """
    forbidden = ["git clone", "curl ", "wget ", "base64 -d", "tar -x", "readings.csv"]
    for phrase in forbidden:
        assert phrase not in standalone_source, phrase
    assert "your own Ada codebase" in standalone_source


def test_standalone_page_carries_the_reference_material(standalone: str) -> None:
    """No repo means no idiom map or checklist unless the page contains them."""
    assert "idiom map" in standalone.lower()
    assert "delta 0.1 digits 6" in standalone
    assert "per-package definition of done" in standalone.lower()


def test_standalone_page_teaches_the_same_gates(standalone: str) -> None:
    assert "/ada-to-cpp-migration" in standalone
    assert "@ada-to-cpp-migration" not in standalone
    assert "permissions:" in standalone
    assert "tool-level guardrail" in standalone
    assert standalone.count('class="prompt"') >= 7


def test_standalone_no_build_track_does_not_contradict_the_skill() -> None:
    """Without a build there is no trusted reference output, so a correct
    skill stops. A fallback that has attendees migrate anyway teaches them to
    ignore the precondition they just wrote.
    """
    source = (build_lab.ROOT / "src" / "standalone.md").read_text(encoding="utf-8")
    track = source.split("## 4.")[1].split("## 5.")[0]
    assert "refuse to start" in track
    assert "unverified draft" in track


# One semantic prohibition per entry, phrased differently in each document —
# match the meaning, not the sentence. The runtime-golden-read gate reached
# only one of the three documents before this test existed.
GATE_SENTINELS = {
    "no reading the goldens": r"at build (?:time or run time|or run time)",
    "no delegating to Ada": r"shelling out to the Ada program",
    "no weakening tests": r"weaken, skip",
    "no floating point": r"to floating point|to a floating point type",
    "no dropped checks": r"run-time constraint check",
    "closure debugging only": r"only work allowed|only permitted work",
    "no completion while red": r"fails or\s+(?:was|any case has been)\s+skipped",
}


@pytest.mark.parametrize("name,pattern", sorted(GATE_SENTINELS.items()))
@pytest.mark.parametrize(
    "document",
    [
        build_lab.ROOT / "src" / "lab.md",
        build_lab.ROOT / "src" / "standalone.md",
        build_lab.TALK / "src" / "handout.md",
    ],
    ids=lambda path: path.name,
)
def test_every_edition_teaches_the_same_gates(
    document: Path, name: str, pattern: str
) -> None:
    text = document.read_text(encoding="utf-8")
    assert re.search(pattern, text), f"{document.name} is missing: {name}"


@pytest.mark.parametrize("name,pattern", sorted(GATE_SENTINELS.items()))
def test_answer_key_teaches_the_same_gates(name: str, pattern: str) -> None:
    """Solution branch only; elsewhere the file is deliberately absent."""
    skill = ROOT / "solution" / "ada-to-cpp-migration" / "SKILL.md"
    if not skill.exists():
        pytest.skip("answer key lives on the solution branch")
    assert re.search(pattern, skill.read_text(encoding="utf-8")), name


def test_answer_key_is_not_on_this_branch() -> None:
    """The lab starts by asking the agent to read the repo — so the finished
    skill must not be readable from the branch attendees work on.
    """
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.split()
    branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if branch == "solution":
        return
    assert not [name for name in tracked if name.startswith("solution/")]


def test_answer_key_agrees_with_the_lab() -> None:
    """Runs on the solution branch only; elsewhere there is nothing to check.

    The lab and the finished skill are edited on different branches, which is
    exactly the situation where they drift apart.
    """
    skill = ROOT / "solution" / "ada-to-cpp-migration" / "SKILL.md"
    if not skill.exists():
        return
    text = skill.read_text(encoding="utf-8")
    assert "Never delegate the behaviour to the reference implementation" in text
    assert "check-golden" in text
    assert "Write(cpp/tests/**)" in text
    assert "tool-level guardrail" in text
    # the gate must permit the debugging that turns the suite green
    assert "Debugging the failure is not" in text


def test_handout_runs_none_of_our_code(handout: str) -> None:
    """Same audience as the standalone page: a static takeaway, no scripts."""
    assert "<script" not in handout
    assert "<button" not in handout
    assert "<link" not in handout
    assert "github.com" not in handout
    assert "<style>" in handout


def test_handout_carries_the_reference_material(handout: str) -> None:
    """There is no repo to read it from, and no lab in which to derive it."""
    assert "idiom map" in handout.lower()
    assert "delta 0.1 digits 6" in handout
    assert "per-package definition of done" in handout.lower()
    assert "/ada-to-cpp-migration" in handout
    assert "@ada-to-cpp-migration" not in handout
    assert "permissions:" in handout
    assert "tool-level guardrail" in handout


def test_talk_deck_covers_the_gates_it_cannot_demonstrate(talk_slides: str) -> None:
    """Without a lab the room never runs a probe, so the deck has to carry
    every lesson the lab would otherwise produce by failing in public.
    """
    for claim in (
        "weaken, skip or delete a parity test",
        "at build or run time",
        "shell out to the legacy program",
        "run-time constraint check",
        "only allowed work",
        "fails or was skipped",
        "permissions:",
        "Constraint_Error",
    ):
        assert claim in talk_slides, claim


def test_talk_edition_hands_over_a_skeleton_not_a_finished_skill(
    talk_slides: str, handout_source: str
) -> None:
    """The room leaves with a template. A copyable finished skill would carry
    our fixture names and our domain into codebases that have neither.
    """
    for text in (talk_slides, handout_source):
        assert "skeleton" in text.lower()
        assert "## Gates" in text
        assert "## Reporting" in text
        assert "Telemetry.Sensors" not in text


def test_talk_edition_stands_alone(talk_slides: str, handout_source: str) -> None:
    """The deck and the handout are the whole of this audience's exposure.
    Neither may position itself as the lesser half of a lab they will never
    attend, and neither may lean on a repository they cannot open: every
    example has to be readable as an invented one.
    """
    for text in (talk_slides, handout_source):
        assert "hands-on version" not in text
        assert "this is not it" not in text.lower()
        assert "case study" not in text.lower()
        assert "ctest" not in text
        assert "golden/" not in text
        assert "no prior experience" in text.lower()


def test_talk_deck_is_legible_in_a_dark_room(talk_slides: str) -> None:
    front_matter = talk_slides.split("---", 2)[1]
    assert "background: #10131a" in front_matter
    assert "color: #dfe4ec" in front_matter


def test_talk_deck_and_handout_agree_on_the_platform(
    talk_slides: str, handout_source: str
) -> None:
    for text in (talk_slides, handout_source):
        assert "@ada-to-cpp-migration" not in text
        assert ".agents/skills/" in text
        assert "%APPDATA%\\devin\\skills" in text


def test_no_stale_references_to_retired_files() -> None:
    """lab-guide.md and prompts.md were folded into the page."""
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.split()
    for name in ("workshop/lab-guide.md", "workshop/prompts.md"):
        assert name not in tracked

    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts or "build" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        assert "lab-guide.md" not in text, path
        assert "workshop/prompts.md" not in text, path
