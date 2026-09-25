"""Check the Lumen WQHD version and optional release tag without importing its generator."""
import argparse
import ast
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION_PATTERN = r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def version_triplet(value, label):
    require(isinstance(value, list) and len(value) == 3
            and all(type(part) is int and part >= 0 for part in value),
            f"{label}: expected three non-negative version integers")
    return value


def source_version(path):
    """Read one literal top-level VERSION assignment; never execute source code."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    assignments = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == "VERSION"
                   for target in node.targets):
                assignments.append(node.value)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id == "VERSION":
                assignments.append(node.value)
    require(len(assignments) == 1, f"{path}: expected one literal VERSION assignment")
    try:
        value = ast.literal_eval(assignments[0])
    except (ValueError, TypeError) as error:
        raise ValueError(f"{path}: VERSION must be a literal list") from error
    return version_triplet(value, str(path))


def read_manifest(path, expected):
    manifest = json.loads(path.read_text(encoding="utf-8"))
    require(version_triplet(manifest["header"]["version"], str(path)) == expected,
            f"{path}: header version differs from generator VERSION")
    modules = manifest["modules"]
    require(isinstance(modules, list) and modules, f"{path}: missing modules")
    for module in modules:
        require(version_triplet(module["version"], str(path)) == expected,
                f"{path}: module version differs from generator VERSION")
    return manifest


def check_versions(root=ROOT):
    root = Path(root)
    lumen_version = source_version(root / "scripts/create_pack.py")
    read_manifest(root / "pack/manifest.json", lumen_version)
    return {"lumen": ".".join(map(str, lumen_version))}


def check_release(root=ROOT, tag=None):
    root = Path(root)
    versions = check_versions(root)
    if tag is not None:
        match = re.fullmatch(rf"v({VERSION_PATTERN})", tag)
        require(match is not None, "Release tag must be vX.Y.Z (no suffixes or leading zeros)")
        version = match.group(1)
        require(version == versions["lumen"],
                f"Release tag version must equal {versions['lumen']} for Lumen WQHD")
        changelog = root / "CHANGELOG.md"
        heading = f"## [{version}]"
        require(any(re.fullmatch(re.escape(heading) + r"(?: - .+)?", line)
                    for line in changelog.read_text(encoding="utf-8").splitlines()),
                f"{changelog}: missing release heading {heading} (optional ' - date/status' suffix)")
    return versions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", help="Check vX.Y.Z and its changelog entry")
    args = parser.parse_args()
    try:
        versions = check_release(tag=args.tag)
    except (ValueError, KeyError, TypeError, OSError, SyntaxError) as error:
        parser.exit(1, f"Release check failed: {error}\n")
    print(f"PASS: Lumen WQHD {versions['lumen']}"
          + (f"; tag {args.tag}" if args.tag is not None else ""))


if __name__ == "__main__":
    main()
