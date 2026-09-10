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
    assert expected >= 6
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


def test_lab_covers_all_six_prompts(page: str) -> None:
    for step in range(6):
        assert f"Prompt {step} —" in page


def test_starting_state_is_documented_as_failing(page: str) -> None:
    assert "3 tests failed out of 3" in page


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
