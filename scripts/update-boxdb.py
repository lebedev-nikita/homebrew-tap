#!/usr/bin/env python3
"""Pin the newest stable BoxDB release after verifying every required artifact."""

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile


REPOSITORY = "lebedev-nikita/boxdb"
FORMULA = Path(__file__).resolve().parents[1] / "Formula/boxdb.rb"
VERSION = r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
STABLE_TAG = re.compile(r"v(" + VERSION + r")")
SUFFIXES = ("-aarch64-apple-darwin.tar.gz", "-x86_64-unknown-linux-musl.tar.gz", ".crate")
URL_PREFIX = f"https://github.com/{REPOSITORY}/releases/download/v"
FORMULA_ASSET = re.compile(
    r'^(?P<prefix>[ \t]+url "' + re.escape(URL_PREFIX) +
    r')(?P<version>' + VERSION + r')(?P<filename>/boxdb-)(?P=version)' +
    r'(?P<suffix>' + "|".join(map(re.escape, SUFFIXES)) +
    r')(?P<checksum>"\n[ \t]+sha256 ")(?P<digest>[0-9a-f]{64})(?P<end>"[ \t]*$)', re.MULTILINE,
)


def latest_release(releases):
    candidates = []
    for release in releases:
        match = STABLE_TAG.fullmatch(release["tag_name"])
        if match and not release["draft"] and not release["prerelease"]:
            version = match[1]
            candidates.append((tuple(map(int, version.split("."))), version, release))
    if not candidates:
        raise ValueError("No stable BoxDB release found")
    _, version, release = max(candidates, key=lambda candidate: candidate[0])
    return version, release


def formula_assets(text):
    matches = list(FORMULA_ASSET.finditer(text))
    if Counter(match["suffix"] for match in matches) != Counter({SUFFIXES[0]: 1, SUFFIXES[1]: 1, SUFFIXES[2]: 2}):
        raise ValueError("Expected the four supported formula URL/checksum pairs")
    if len({match["version"] for match in matches}) != 1:
        raise ValueError("Formula artifact versions must agree")
    return matches


def current_version(text):
    return formula_assets(text)[0]["version"]


def asset_names(version):
    return [f"boxdb-{version}{suffix}" for suffix in SUFFIXES]


def uploaded_assets(release, version):
    required = set(asset_names(version) + ["SHA256SUMS"])
    assets = {}
    for asset in release["assets"]:
        if asset["name"] in required and asset["state"] == "uploaded":
            if asset["name"] in assets:
                raise ValueError("Duplicate release asset: " + asset["name"])
            assets[asset["name"]] = asset
    if required != assets.keys():
        raise ValueError("Stable release is missing uploaded assets: " + ", ".join(sorted(required - assets.keys())))
    return assets


def hash_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as artifact:
        for chunk in iter(lambda: artifact.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verified_digests(directory, assets, version):
    actual = {}
    for name, asset in assets.items():
        actual[name] = hash_file(directory / name)
        published = asset.get("digest")
        if published and published != "sha256:" + actual[name]:
            raise ValueError(name + " does not match GitHub's asset digest")
    checksums = {}
    for line in (directory / "SHA256SUMS").read_text().splitlines():
        match = re.fullmatch(r"([0-9a-fA-F]{64})  ([^/\\]+)", line)
        if not match or match[2] in checksums:
            raise ValueError("Invalid or duplicate SHA256SUMS entry")
        checksums[match[2]] = match[1].lower()
    for name in asset_names(version):
        if checksums.get(name) != actual[name]:
            raise ValueError(name + " is missing from or does not match SHA256SUMS")
    return {name: actual[name] for name in asset_names(version)}


def updated_formula(text, version, digests):
    current = current_version(text)
    if tuple(map(int, version.split("."))) < tuple(map(int, current.split("."))):
        raise ValueError("Refusing to downgrade BoxDB")
    def replace_digest(match):
        digest = digests[f"boxdb-{version}{match['suffix']}"]
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("Invalid artifact SHA-256")
        if version == current and digest != match["digest"]:
            raise ValueError("Refusing to change an existing version's artifact digest")
        return (match["prefix"] + version + match["filename"] + version + match["suffix"] +
                match["checksum"] + digest + match["end"])

    return FORMULA_ASSET.sub(replace_digest, text)


def publish_formula(path, original, updated):
    if updated == original:
        return False
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".boxdb-", delete=False) as output:
            temporary = Path(output.name)
            output.write(updated)
            output.flush()
            os.fsync(output.fileno())
        os.chmod(temporary, stat.S_IMODE(path.stat().st_mode))
        if path.read_text() != original:
            raise ValueError("Formula changed while verifying the release")
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--formula", type=Path, default=FORMULA)
    args = parser.parse_args()
    original = args.formula.read_text()
    current = current_version(original)
    result = subprocess.check_output([
        "gh", "api", "--paginate", "--slurp", f"repos/{REPOSITORY}/releases?per_page=100",
    ], text=True)
    version, release = latest_release([release for page in json.loads(result) for release in page])
    if tuple(map(int, version.split("."))) < tuple(map(int, current.split("."))):
        raise ValueError("Refusing to downgrade BoxDB")
    assets = uploaded_assets(release, version)
    with tempfile.TemporaryDirectory(prefix="boxdb-release-") as directory:
        command = ["gh", "release", "download", release["tag_name"], "--repo", REPOSITORY]
        for name in assets:
            command.extend(["--pattern", name])
        subprocess.run(command + ["--dir", directory], check=True)
        digests = verified_digests(Path(directory), assets, version)
    updated = updated_formula(original, version, digests)
    if publish_formula(args.formula, original, updated):
        print(f"Updated BoxDB to {version}")
    else:
        print(f"BoxDB {version} is up to date")


if __name__ == "__main__":
    main()
