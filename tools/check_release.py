"""Check this product's eight-skill release, not arbitrary installed skills.

Usage: python tools/check_release.py [release-root]. Python 3.10+, stdlib only.
"""
from pathlib import Path
import argparse
import sys
from release_core import check_release


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        report = check_release(args.root)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    for excluded in report.excluded:
        print(f"EXCLUDED: {excluded}")
    for error in report.errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if report.errors:
        print(f"FAIL: {len(report.errors)} release error(s)", file=sys.stderr)
        return 1
    print(f"PASS: {len(report.files)} releasable files; 8 skills; version {report.version}")
    print("Scope: local package integrity only; no harness, network-link, or teaching-effect verification.")
    print("Content scan: finite path/token/scaffold patterns; not a complete secrets or personal-data audit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
