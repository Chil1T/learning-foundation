"""Small, dependency-free release checks; not an installer or a Markdown/YAML parser."""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import stat
from urllib.parse import unquote, urlsplit
import zipfile

SKILLS = frozenset({
    "learning-entry", "concept-tutor", "learning-plan-designer",
    "learning-state-reconciler", "research-learning-entry", "paper-deep-reader",
    "research-meeting-prep", "learning-method-workbench",
})
ROOT_FILES = frozenset({"README.md", "LICENSE", "VERSION", "AGENTS.md", ".gitignore", "CHANGELOG.md"})
ROOT_DIRS = frozenset({"skills", "docs", "presets", "templates", "tools", "tests"})
EXCLUDED = frozenset({".git", ".pytest_cache", ".mypy_cache", ".ruff_cache", "__pycache__", "node_modules", ".venv", "venv", "dist", "build", "cache", ".DS_Store", "Thumbs.db"})
SUFFIXES = frozenset({".md", ".py", ".txt", ".json", ".yaml", ".yml", ".toml", ".svg", ".png"})
PERSONAL_DIRS = frozenset({"notes", "sources", "learning", ".obsidian"})
SENSITIVE_FILES = frozenset({".env", "credentials.json", "id_rsa", "id_ed25519"})
LOCAL_PATH = re.compile(r"(?i)(?:\b[A-Z]:[\\/]|/(?:Users|home)/[^\s/]+/|" + "file:" + r"//)")
SECRET = re.compile(r"(?:-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bsk-[A-Za-z0-9_-]{20,}|\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,})")
UNFINISHED = re.compile(r"(?im)^\s*(?:(?:[-*]\s+)?(?:TODO|FIXME|TBD)\s*[:：]|<!--\s*(?:TODO|FIXME|TBD)\b)")


@dataclass
class Report:
    root: Path
    files: list[Path] = field(default_factory=list)
    excluded: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    version: str = ""

    def require_valid(self) -> None:
        if self.errors:
            raise ValueError("\n".join(self.errors))


def is_link(path: Path) -> bool:
    info = path.lstat()
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def collect(root: Path) -> Report:
    report = Report(root)
    if not root.is_dir() or is_link(root):
        report.errors.append("Root must be a real directory, not a symlink/reparse point.")
        return report

    def visit(directory: Path) -> None:
        for path in sorted(directory.iterdir()):
            rel = path.relative_to(root)
            label = rel.as_posix()
            if is_link(path):
                report.errors.append(f"{label}: symlink/reparse point is not allowed")
                continue
            if path.name in EXCLUDED or path.suffix.lower() in {".pyc", ".pyo"}:
                report.excluded.append(label)
                continue
            if ((path.name in PERSONAL_DIRS and "templates" not in rel.parts[:-1])
                    or path.name in SENSITIVE_FILES or path.name.startswith(".env.")):
                report.errors.append(f"{label}: personal data or credential location is not releasable")
                continue
            if len(rel.parts) == 1 and path.name not in ROOT_FILES | ROOT_DIRS:
                report.errors.append(f"{label}: unexpected root entry (not in release allowlist)")
                continue
            if path.is_dir():
                if len(rel.parts) == 1 and path.name not in ROOT_DIRS:
                    report.errors.append(f"{label}: expected a file")
                else:
                    visit(path)
            elif path.is_file():
                if len(rel.parts) == 1 and path.name not in ROOT_FILES:
                    report.errors.append(f"{label}: expected a directory")
                elif len(rel.parts) > 1 and path.suffix.lower() not in SUFFIXES:
                    report.errors.append(f"{label}: unsupported release file type")
                else:
                    report.files.append(path)
            else:
                report.errors.append(f"{label}: special filesystem object is not allowed")

    visit(root)
    return report


def without_code(text: str) -> str:
    # Fenced examples and inline code are not active Markdown links.
    text = re.sub(r"(?ms)^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$", "", text)
    return re.sub(r"(`+).*?\1", "", text)


def destination(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("<"):
        return raw[1:raw.find(">")]
    return re.split(r"\s+", raw, maxsplit=1)[0] if raw else ""


def markdown_links(text: str):
    text = without_code(text)
    for match in re.finditer(r"!?\[[^\]\n]*\]\(", text):
        start = pos = match.end()
        depth = 1
        while pos < len(text) and text[pos] != "\n":
            if text[pos] == "\\":
                pos += 2
                continue
            if text[pos] == "(":
                depth += 1
            elif text[pos] == ")":
                depth -= 1
                if depth == 0:
                    yield destination(text[start:pos])
                    break
            pos += 1
    definitions = {}
    for match in re.finditer(r"(?m)^\s{0,3}\[([^\]\n]+)\]:\s*(.+)$", text):
        definitions[match[1].strip().casefold()] = destination(match[2])
        yield destination(match[2])
    for match in re.finditer(r"!?\[([^\]\n]+)\]\[([^\]\n]*)\]", text):
        key = (match[2] or match[1]).strip().casefold()
        if key not in definitions:
            yield "missing-reference:" + key
    for match in re.finditer(r"<(?:a|img|source)\b[^>]*?\b(?:href|src)\s*=\s*['\"]([^'\"]+)", text, re.I):
        yield match[1]
    for match in re.finditer(r"\[\[([^\]\n]+)\]\]", text):
        yield match[1].split("|", 1)[0]


def check_links(report: Report, path: Path, text: str) -> None:
    included = set(report.files)
    rel = path.relative_to(report.root)
    boundary = report.root / "skills" / rel.parts[1] if rel.parts[0] == "skills" and len(rel.parts) > 2 else report.root
    for link in markdown_links(text):
        parsed = urlsplit(link)
        if parsed.scheme in {"https", "http", "mailto", "tel"} or link.startswith("//"):
            continue
        if parsed.scheme or link.startswith(("/", "\\")):
            report.errors.append(f"{rel}: forbidden absolute or unsupported link: {link}")
            continue
        local = unquote(parsed.path).replace("\\", "/")
        if not local:
            continue
        target = (path.parent / local).resolve()
        if not within(target, boundary):
            report.errors.append(f"{rel}: link escapes {'skill' if boundary != report.root else 'release'} boundary: {link}")
            continue
        if target not in included and not (target.is_dir() and any(within(item, target) for item in included)):
            report.errors.append(f"{rel}: missing or excluded relative link target: {link}")


def frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        return {}
    result = {}
    end = lines.index("---", 1)
    for index in range(1, end):
        match = re.fullmatch(r"(name|description):\s*(.*)", lines[index])
        if not match:
            continue
        key, value = match.groups()
        if key in result:
            raise ValueError(f"duplicate {key} metadata")
        if value in {">", "|", ">-", "|-"}:
            block = []
            for line in lines[index + 1:end]:
                if line and not line.startswith((" ", "\t")):
                    break
                block.append(line.strip())
            value = " ".join(block).strip()
        elif len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        result[key] = value
    return result


def check_release(root: Path) -> Report:
    # Preserve the original final component for link detection before resolving.
    root = Path(os.path.abspath(root))
    report = collect(root)
    if not root.is_dir() or is_link(root):
        return report
    for name in ("README.md", "LICENSE", "VERSION", "AGENTS.md"):
        if root / name not in report.files:
            report.errors.append(f"Missing required release file: {name}")
    version_path = root / "VERSION"
    if version_path in report.files:
        report.version = version_path.read_text(encoding="utf-8-sig").strip()
        if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?", report.version):
            report.errors.append("VERSION must be a single safe semantic version, e.g. 0.1.0")
    skills_dir = root / "skills"
    actual = {p.name for p in skills_dir.iterdir() if p.is_dir() and not is_link(p)} if skills_dir.is_dir() and not is_link(skills_dir) else set()
    if actual != SKILLS:
        report.errors.append(f"Skill folders mismatch; missing={sorted(SKILLS - actual)}, unexpected={sorted(actual - SKILLS)}")
    texts = {}
    for path in report.files:
        if path.suffix.lower() in {".png"}:
            continue
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeError:
            report.errors.append(f"{rel}: expected UTF-8 text")
            continue
        texts[path] = text
        if LOCAL_PATH.search(text):
            report.errors.append(f"{rel}: machine-specific absolute path or file URI")
        if SECRET.search(text):
            report.errors.append(f"{rel}: potential private key/token")
        if path.suffix.lower() == ".md":
            if UNFINISHED.search(without_code(text)):
                report.errors.append(f"{rel}: unfinished scaffold marker")
            check_links(report, path, text)
    for name in sorted(SKILLS):
        path = skills_dir / name / "SKILL.md"
        if path not in texts:
            report.errors.append(f"skills/{name}/SKILL.md: missing readable skill entry")
            continue
        try:
            metadata = frontmatter(texts[path])
        except ValueError as error:
            report.errors.append(f"skills/{name}/SKILL.md: {error}")
            continue
        if metadata.get("name") != name or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", metadata.get("name", "")):
            report.errors.append(f"skills/{name}/SKILL.md: name must match its standard folder name")
        description = metadata.get("description", "")
        if not description or len(description) > 1024 or description[0] in "[{" or "<" in description or ">" in description:
            report.errors.append(f"skills/{name}/SKILL.md: description must be a nonempty plain string of at most 1024 characters")
    return report


def verify_archive(archive: Path, manifest: dict[str, str]) -> None:
    """Check names, type, CRC, exact inventory and bytes before declaring success."""
    with zipfile.ZipFile(archive) as packed:
        names = set()
        for item in packed.infolist():
            name = item.filename
            path = PurePosixPath(name)
            if ("\\" in name or ":" in name or path.is_absolute() or ".." in path.parts
                    or name in names or name not in manifest or item.flag_bits & 1
                    or stat.S_IFMT(item.external_attr >> 16) not in {0, stat.S_IFREG}):
                raise ValueError(f"Unsafe or unexpected zip member: {name}")
            names.add(name)
            if hashlib.sha256(packed.read(item)).hexdigest() != manifest[name]:
                raise ValueError(f"Zip content mismatch: {name}")
        if names != set(manifest) or packed.testzip() is not None:
            raise ValueError("Zip inventory or CRC check failed")
