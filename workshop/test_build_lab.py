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
    assert "3 tests failed out of 3" in page


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
