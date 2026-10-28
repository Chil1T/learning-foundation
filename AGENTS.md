# Maintaining Learning Foundation

This guide defines the engineering conventions and contribution rules for AI coding assistants and developers collaborating on the **Learning Foundation** repository.

---

## 🏛️ Repository Architecture

This repository distributes self-contained, composable **Agent Skills** conforming to the [Agent Skills specification](https://agentskills.io/specification).

```
learning-foundation/
├── skills/               # Independently installable Agent Skills
│   ├── concept-tutor/
│   ├── learning-entry/
│   ├── learning-plan-designer/
│   ├── learning-state-reconciler/
│   ├── research-learning-entry/
│   ├── paper-deep-reader/
│   ├── research-meeting-prep/
│   └── learning-method-workbench/
├── presets/              # Recommended skill suites (Markdown guides)
├── docs/                 # In-depth architectural, pedagogical, and compatibility guides
├── tools/                # Zero-dependency packaging and release verification tools (Python 3.10+)
├── tests/                # Automated regression test suite
├── AGENTS.md             # This maintainer guide
├── README.md             # Project showcase and user entry point
├── LICENSE               # MIT License
└── VERSION               # Semantic version string
```

---

## 🧭 Core Maintainer Principles

When modifying or expanding skills and documentation in this repository:

1. **Strict Skill Independence**:
   - Every directory under `skills/<name>/` must be a completely standalone, portable unit.
   - Any required assets or references must reside inside that skill's own directory (e.g. `skills/<name>/references/`).
   - Cross-skill relative links (e.g., pointing from one skill to another skill's internal files) are forbidden to ensure that users can cherry-pick a single skill folder without broken dependencies.
2. **Standard Agent Skills Metadata**:
   - Every skill must have a valid `SKILL.md` file with standard YAML frontmatter containing `name` and `description`.
   - The `name` field must match the directory name exactly (lowercase alphanumeric with hyphens).
   - The `description` must be a crisp, single-line explanation (at most 1024 characters).
3. **No Private/Machine Leakage**:
   - Never commit machine-specific absolute file paths, private keys, or tokens.
   - Never commit unfinished scaffold markers (such as `TODO:`, `FIXME:`, or `TBD:`) into release markdown.
   - All internal markdown links must strictly resolve to valid repository-local files.
4. **Pedagogical Integrity**:
   - Preserve the five core principles: explicit user authorization, content identity, evidence-proportionate mastery, resumable context, and reviewable evolution.
   - Do not weaken prompt constraints that protect the user from passive illusion of learning or unauthorized file modifications.

---

## 🧪 Verification & Release Workflow

Release verification uses only the Python 3.10+ standard library without external dependencies.

### Running Local Checks
Before committing or publishing changes:

```sh
# 1. Run static release checks (syntax, metadata, links, sensitive patterns)
python tools/check_release.py

# 2. Run automated test suite
python -m unittest discover -s tests -v
```

### Packaging an Archive
To build a clean, deterministic `.zip` distribution archive alongside its SHA-256 checksum:

```sh
python tools/build_release.py --output ../learning-foundation-releases
```

The output directory must reside outside the project root to prevent self-inclusion. Existing release archives are never overwritten.
