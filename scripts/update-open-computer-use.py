#!/usr/bin/env python3
"""Pin the newest stable Open Computer Use release after verifying its macOS app archive."""

import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile


REPOSITORY = "iFurySt/open-computer-use"
CASK = Path(__file__).resolve().parents[1] / "Casks/open-computer-use.rb"
STABLE_TAG = re.compile(r"v((?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*))")


def archive_name(version):
    return f"Open-Computer-Use-{version}-macOS-universal.app.zip"


def latest_release(releases):
    candidates = []
    for release in releases:
        match = STABLE_TAG.fullmatch(release["tag_name"])
        if match and not release["draft"] and not release["prerelease"]:
            version = match[1]
            candidates.append((tuple(map(int, version.split("."))), version, release))
    if not candidates:
        raise ValueError("No stable release found")
    _, version, release = max(candidates, key=lambda candidate: candidate[0])
    return version, release


def verified_digest(archive, checksums):
    expected = [
        line.split("  ", 1)[0].lower()
        for line in checksums.read_text().splitlines()
        if re.fullmatch(r"[0-9a-fA-F]{64}  " + re.escape(archive.name), line)
    ]
    if len(expected) != 1:
        raise ValueError("SHA256SUMS must list the app archive exactly once")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != expected[0]:
        raise ValueError("App archive does not match SHA256SUMS")
    return digest


def updated_cask(text, version, digest):
    current = re.search(r'^  version "(\d+\.\d+\.\d+)"$', text, re.MULTILINE)
    if not current:
        raise ValueError("Missing stable cask version")
    if tuple(map(int, version.split("."))) < tuple(map(int, current[1].split("."))):
        raise ValueError("Refusing to downgrade the cask")
    text = re.sub(r'^  version "[^"]+"$', f'  version "{version}"', text, count=1, flags=re.MULTILINE)
    text, count = re.subn(r'^  sha256 "[0-9a-f]{64}"$', f'  sha256 "{digest}"', text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise ValueError("Missing cask checksum")
    return text


def main():
    result = subprocess.check_output([
        "gh", "api", "--paginate", "--slurp", f"repos/{REPOSITORY}/releases?per_page=100",
    ], text=True)
    version, release = latest_release([release for page in json.loads(result) for release in page])
    filename = archive_name(version)
    assets = {asset["name"]: asset for asset in release["assets"] if asset["state"] == "uploaded"}
    if filename not in assets or "SHA256SUMS" not in assets:
        raise ValueError("Stable release is missing its macOS app archive or SHA256SUMS")
    with tempfile.TemporaryDirectory(prefix="open-computer-use-cask-") as directory:
        subprocess.run([
            "gh", "release", "download", release["tag_name"], "--repo", REPOSITORY,
            "--pattern", filename, "--pattern", "SHA256SUMS", "--dir", directory,
        ], check=True)
        digest = verified_digest(Path(directory) / filename, Path(directory) / "SHA256SUMS")
    published_digest = assets[filename].get("digest")
    if published_digest and published_digest != f"sha256:{digest}":
        raise ValueError("App archive does not match GitHub's asset digest")
    original = CASK.read_text()
    updated = updated_cask(original, version, digest)
    if updated != original:
        CASK.write_text(updated)
        print(f"Updated Open Computer Use to {version}")
    else:
        print(f"Open Computer Use {version} is up to date")


if __name__ == "__main__":
    main()
