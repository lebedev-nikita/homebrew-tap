#!/usr/bin/env python3
"""Pin the newest stable macOS release after verifying its downloaded DMG."""

import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile


REPOSITORY = "lebedev-nikita/open-dictate"
CASK = Path(__file__).resolve().parents[1] / "Casks/open-dictate.rb"
STABLE_TAG = re.compile(r"macos-v((?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*))")


def latest_release(releases):
    candidates = []
    for release in releases:
        match = STABLE_TAG.fullmatch(release["tag_name"])
        if match and not release["draft"] and not release["prerelease"]:
            version = match[1]
            candidates.append((tuple(map(int, version.split("."))), version, release))
    if not candidates:
        raise ValueError("No stable macOS release found")
    _, version, release = max(candidates, key=lambda candidate: candidate[0])
    return version, release


def verified_digest(dmg, checksum):
    match = re.fullmatch(r"([0-9a-fA-F]{64})  " + re.escape(dmg.name) + r"\n?", checksum.read_text())
    if not match:
        raise ValueError("Invalid checksum attachment or unexpected DMG filename")
    digest = hashlib.sha256(dmg.read_bytes()).hexdigest()
    if digest != match[1].lower():
        raise ValueError("DMG does not match its published checksum")
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
    filename = f"OpenDictate-macOS-{version}-universal.dmg"
    assets = {asset["name"]: asset for asset in release["assets"] if asset["state"] == "uploaded"}
    if filename not in assets or filename + ".sha256" not in assets:
        raise ValueError("Stable release is missing its DMG or checksum attachment")
    with tempfile.TemporaryDirectory(prefix="opendictate-cask-") as directory:
        subprocess.run([
            "gh", "release", "download", release["tag_name"], "--repo", REPOSITORY,
            "--pattern", filename, "--pattern", filename + ".sha256", "--dir", directory,
        ], check=True)
        digest = verified_digest(Path(directory) / filename, Path(directory) / (filename + ".sha256"))
    published_digest = assets[filename].get("digest")
    if published_digest and published_digest != f"sha256:{digest}":
        raise ValueError("DMG does not match GitHub's asset digest")
    original = CASK.read_text()
    updated = updated_cask(original, version, digest)
    if updated != original:
        CASK.write_text(updated)
        print(f"Updated OpenDictate to {version}")
    else:
        print(f"OpenDictate {version} is up to date")


if __name__ == "__main__":
    main()
