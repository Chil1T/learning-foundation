"""Validate and build an external zip plus SHA256; never overwrite an artifact."""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import sys
import zipfile
from release_core import check_release, is_link, verify_archive, within


def build_release(root: Path, output: Path | None = None) -> tuple[Path, Path]:
    report = check_release(root)
    report.require_valid()
    root = report.root
    output = Path(os.path.abspath(output)) if output is not None else root.parent / "learning-foundation-releases"
    for ancestor in (output, *output.parents):
        if (ancestor.exists() or ancestor.is_symlink()) and is_link(ancestor):
            raise ValueError(f"Output path contains a symlink/reparse point: {ancestor}")
    output = output.resolve()
    if within(output, root.resolve()):
        raise ValueError("Output directory must be outside the release root")
    archive = output / f"learning-foundation-{report.version}.zip"
    checksum = archive.with_suffix(".zip.sha256")
    if archive.exists() or checksum.exists():
        raise FileExistsError("Release zip or checksum already exists; choose a new output directory")
    output.mkdir(parents=True, exist_ok=True)
    created = []
    try:
        with archive.open("xb") as zip_stream:
            created.append(archive)
            with checksum.open("xb") as checksum_stream:
                created.append(checksum)
                manifest = {}
                with zipfile.ZipFile(zip_stream, "w", compression=zipfile.ZIP_DEFLATED) as packed:
                    for path in report.files:
                        if is_link(path) or not within(path.resolve(), root.resolve()):
                            raise ValueError(f"Input changed to a link or escaped root: {path}")
                        data = path.read_bytes()
                        name = "learning-foundation/" + path.relative_to(root).as_posix()
                        manifest[name] = hashlib.sha256(data).hexdigest()
                        info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
                        info.create_system = 3
                        info.external_attr = 0o100644 << 16
                        info.compress_type = zipfile.ZIP_DEFLATED
                        packed.writestr(info, data)
                zip_stream.flush()
                verify_archive(archive, manifest)
                digest = hashlib.sha256(archive.read_bytes()).hexdigest()
                checksum_stream.write(f"{digest}  {archive.name}\n".encode("ascii"))
    except BaseException:
        for path in reversed(created):
            path.unlink(missing_ok=True)
        raise
    for excluded in report.excluded:
        print(f"EXCLUDED: {excluded}")
    return archive, checksum


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, help="Directory outside the project; default: sibling learning-foundation-releases")
    args = parser.parse_args()
    try:
        archive, checksum = build_release(args.root, args.output)
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"ZIP: {archive}\nSHA256: {checksum}")
    print("Verified zip inventory, safe member paths, CRC and file hashes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
