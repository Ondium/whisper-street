#!/usr/bin/env python3
"""Repository hygiene checks that do not depend on the project's language.

Run locally with:  python3 .github/scripts/check_repo_hygiene.py

Checks:
  1. No committed audio, model weights, or obvious secret files.
  2. The documents the contribution process points at all exist.
  3. Relative Markdown links resolve to real files and anchors.
  4. Issue-template and workflow YAML parses.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Formats that must never be committed. Small, license-clear fixtures under
# tests/fixtures/ are the one exception (see CONTRIBUTING.md).
FORBIDDEN_SUFFIXES = {
    ".wav", ".mp3", ".m4a", ".flac", ".ogg", ".opus", ".aac",
    ".mp4", ".mkv", ".webm", ".mov",
    ".bin", ".pt", ".pth", ".onnx", ".ggml", ".gguf", ".safetensors", ".ckpt",
    ".pem", ".key", ".p12", ".pfx",
}
FORBIDDEN_EXEMPT_PREFIXES = ("tests/fixtures/",)
FORBIDDEN_NAMES = {".env", "credentials.json", "id_rsa", "id_ed25519"}

REQUIRED_DOCS = [
    "README.md", "LICENSE", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md",
    "SECURITY.md", "GOVERNANCE.md", "CHANGELOG.md", "AGENTS.md",
    "CLAUDE.md", "llms.txt",
    ".github/PULL_REQUEST_TEMPLATE.md", ".github/CODEOWNERS",
    "docs/README.md", "docs/architecture.md",
    "docs/api/README.md", "docs/mcp/README.md",
]

LINK_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*?)\s*$", re.MULTILINE)

failures: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


def tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    )
    return [line for line in out.stdout.splitlines() if line]


def check_forbidden(files: list[str]) -> None:
    for f in files:
        if f.startswith(FORBIDDEN_EXEMPT_PREFIXES):
            continue
        p = Path(f)
        if p.suffix.lower() in FORBIDDEN_SUFFIXES or p.name in FORBIDDEN_NAMES:
            fail(
                f"forbidden file committed: {f}\n"
                "    Audio, model weights, and credentials must not be committed. "
                "See CONTRIBUTING.md#audio-models-and-test-fixtures."
            )


def check_required(files: list[str]) -> None:
    tracked = set(files)
    for doc in REQUIRED_DOCS:
        if doc not in tracked:
            fail(f"required document missing: {doc}")


def slugify(heading: str) -> str:
    """GitHub's anchor slug: lowercase, drop punctuation, spaces to hyphens."""
    text = re.sub(r"`|\*|_", "", heading)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # link text only
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return re.sub(r"[\s]+", "-", text)


def anchors_of(path: Path) -> set[str]:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return set()
    return {slugify(h) for h in HEADING_RE.findall(content)}


def check_links(files: list[str]) -> None:
    md_files = [f for f in files if f.endswith(".md")]
    anchor_cache: dict[Path, set[str]] = {}

    for f in md_files:
        src = ROOT / f
        try:
            content = src.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        for target in LINK_RE.findall(content):
            if target.startswith(("http://", "https://", "mailto:", "tel:")):
                continue

            path_part, _, anchor = target.partition("#")

            if not path_part:  # same-document anchor
                dest, dest_anchors = src, anchor_cache.setdefault(src, anchors_of(src))
            else:
                dest = (src.parent / path_part).resolve()
                if not dest.exists():
                    fail(f"broken link in {f}: {target} -> {path_part} does not exist")
                    continue
                if dest.is_dir() or dest.suffix != ".md":
                    continue
                dest_anchors = anchor_cache.setdefault(dest, anchors_of(dest))

            if anchor and anchor not in dest_anchors:
                fail(f"broken anchor in {f}: {target} (no heading '#{anchor}')")


def check_yaml(files: list[str]) -> None:
    try:
        import yaml  # type: ignore
    except ImportError:
        print("note: PyYAML not installed, skipping YAML parse check")
        return

    for f in files:
        if not f.endswith((".yml", ".yaml")):
            continue
        if not (f.startswith(".github/") or f.endswith(("action.yml", "action.yaml"))):
            continue
        try:
            yaml.safe_load((ROOT / f).read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001 - report whatever the parser says
            fail(f"invalid YAML: {f}: {exc}")


def main() -> int:
    files = tracked_files()
    check_forbidden(files)
    check_required(files)
    check_links(files)
    check_yaml(files)

    if failures:
        print(f"\n{len(failures)} repository hygiene problem(s):\n")
        for msg in failures:
            print(f"  ✗ {msg}")
        print()
        return 1

    print(f"✓ repository hygiene checks passed ({len(files)} tracked files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
