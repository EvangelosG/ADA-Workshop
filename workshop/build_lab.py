#!/usr/bin/env python3
"""Render workshop/src/lab.md into the self-contained attendee page.

The output is a single HTML file with no external requests, so it works from
a file:// URL on a laptop with no network. Prompt blocks (```prompt) get a
copy button.

    pip install markdown
    python3 workshop/build_lab.py
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "src" / "lab.md"
OUTPUT = ROOT / "lab.html"

STYLE = """
:root {
  --bg: #10131a;
  --panel: #171b24;
  --border: #262c38;
  --text: #dfe4ec;
  --muted: #99a2b3;
  --accent: #7aa2f7;
  --warn: #f0b866;
  --code-bg: #0c0f15;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font: 16px/1.65 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
main { max-width: 52rem; margin: 0 auto; padding: 3rem 1.5rem 6rem; }
h1 { font-size: 2.1rem; line-height: 1.2; margin: 0 0 1rem; }
h2 {
  font-size: 1.5rem;
  margin: 3.5rem 0 1rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border);
}
h3 { font-size: 1.2rem; margin: 2.5rem 0 .75rem; color: var(--accent); }
a { color: var(--accent); }
hr { display: none; }
table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.25rem 0;
  font-size: .93rem;
}
th, td {
  border: 1px solid var(--border);
  padding: .5rem .7rem;
  text-align: left;
  vertical-align: top;
}
th { background: var(--panel); }
code {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: .88em;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: .08em .35em;
}
pre {
  background: var(--code-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1rem 1.1rem;
  overflow-x: auto;
}
pre code { background: none; border: 0; padding: 0; font-size: .86rem; }
blockquote {
  margin: 1.5rem 0;
  padding: .9rem 1.1rem;
  background: rgba(240, 184, 102, .08);
  border-left: 3px solid var(--warn);
  border-radius: 0 6px 6px 0;
}
blockquote p { margin: .3rem 0; }
details {
  margin: 1.5rem 0;
  padding: .9rem 1.1rem;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
}
summary { cursor: pointer; font-weight: 600; color: var(--warn); }
.prompt {
  position: relative;
  margin: 1.25rem 0;
  border: 1px solid var(--accent);
  border-radius: 8px;
  background: var(--code-bg);
}
.prompt-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: .45rem .8rem;
  border-bottom: 1px solid var(--border);
  font-size: .74rem;
  letter-spacing: .09em;
  text-transform: uppercase;
  color: var(--muted);
}
.prompt pre { border: 0; background: none; margin: 0; }
.prompt pre code { white-space: pre-wrap; }
button.copy {
  font: inherit;
  font-size: .78rem;
  text-transform: none;
  letter-spacing: 0;
  color: var(--text);
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 5px;
  padding: .2rem .7rem;
  cursor: pointer;
}
button.copy:hover { border-color: var(--accent); }
button.copy.done { color: #7fd88f; border-color: #7fd88f; }
footer {
  margin-top: 4rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border);
  color: var(--muted);
  font-size: .85rem;
}
@media print {
  body { background: #fff; color: #000; }
  .prompt, pre, details, table, th { border-color: #bbb; background: #f6f6f6; }
  button.copy { display: none; }
  details[open], details { background: #f6f6f6; }
}
"""

SCRIPT = """
document.querySelectorAll('button.copy').forEach(function (button) {
  button.addEventListener('click', function () {
    var text = button.closest('.prompt').querySelector('code').innerText;
    var done = function () {
      button.textContent = 'Copied';
      button.classList.add('done');
      setTimeout(function () {
        button.textContent = 'Copy';
        button.classList.remove('done');
      }, 1500);
    };
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done);
      return;
    }
    var area = document.createElement('textarea');
    area.value = text;
    area.style.position = 'fixed';
    area.style.opacity = '0';
    document.body.appendChild(area);
    area.select();
    document.execCommand('copy');
    document.body.removeChild(area);
    done();
  });
});
"""

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{style}</style>
</head>
<body>
<main>
{body}
<footer>
Generated from <code>workshop/src/lab.md</code> by
<code>workshop/build_lab.py</code> — edit the markdown, not this file.
Repo: <a href="https://github.com/EvangelosG/ADA-Workshop">github.com/EvangelosG/ADA-Workshop</a>
</footer>
</main>
<script>{script}</script>
</body>
</html>
"""

PROMPT_BLOCK = re.compile(
    r'<pre><code class="language-prompt">(.*?)</code></pre>', re.DOTALL
)


def wrap_prompts(body: str) -> str:
    """Give every ```prompt block a labelled frame and a copy button."""

    def replace(match: re.Match[str]) -> str:
        return (
            '<div class="prompt">'
            '<div class="prompt-bar"><span>Paste into Devin Desktop</span>'
            '<button class="copy" type="button">Copy</button></div>'
            f"<pre><code>{match.group(1)}</code></pre>"
            "</div>"
        )

    return PROMPT_BLOCK.sub(replace, body)


def render(source_text: str) -> str:
    converter = markdown.Markdown(
        extensions=["extra", "sane_lists", "toc"],
        extension_configs={"toc": {"permalink": False}},
    )
    body = wrap_prompts(converter.convert(source_text))
    title = "Build an Ada→C++ migration skill"
    match = re.search(r"^#\s+(.+)$", source_text, re.MULTILINE)
    if match:
        title = match.group(1).strip()
    return PAGE.format(
        title=html.escape(title), style=STYLE, script=SCRIPT, body=body
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if the committed page is out of date",
    )
    args = parser.parse_args()

    rendered = render(SOURCE.read_text(encoding="utf-8"))

    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != rendered:
            print(
                f"{OUTPUT.name} is out of date; run python3 workshop/build_lab.py",
                file=sys.stderr,
            )
            return 1
        print(f"{OUTPUT.name} is up to date")
        return 0

    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
