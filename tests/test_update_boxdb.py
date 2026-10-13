import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("update_boxdb", ROOT / "scripts/update-boxdb.py")
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


def release(tag, **kwargs):
    return {"tag_name": tag, "draft": False, "prerelease": False, **kwargs}


FORMULA = '''class Boxdb < Formula
  desc "Strict typed database with Git-friendly storage"
  homepage "https://github.com/lebedev-nikita/boxdb"
  license "MIT"

  on_macos do
    on_arm do
      url "https://github.com/lebedev-nikita/boxdb/releases/download/v#{version}/boxdb-#{version}-aarch64-apple-darwin.tar.gz"
      sha256 "MAC_HASH"
    end
    on_intel do
      url "https://github.com/lebedev-nikita/boxdb/releases/download/v#{version}/boxdb-#{version}.crate"
      sha256 "SOURCE_HASH"
      depends_on "rust" => :build
    end
  end
  on_linux do
    on_intel do
      url "https://github.com/lebedev-nikita/boxdb/releases/download/v#{version}/boxdb-#{version}-x86_64-unknown-linux-musl.tar.gz"
      sha256 "LINUX_HASH"
    end
    on_arm do
      url "https://github.com/lebedev-nikita/boxdb/releases/download/v#{version}/boxdb-#{version}.crate"
      sha256 "SOURCE_HASH"
      depends_on "rust" => :build
    end
  end

  def install
    bin.install "boxdb"
  end
end
'''.replace("MAC_HASH", "a" * 64).replace("LINUX_HASH", "b" * 64).replace("SOURCE_HASH", "c" * 64).replace("#{version}", "0.1.0")


class GitHubFixture:
    def __init__(self, directory):
        self.root = Path(directory)
        self.formula = self.root / "boxdb.rb"
        self.formula.write_text(FORMULA)
        self.releases = []
        self.digests = {}
        self.env = dict(os.environ, BOXDB_GH_FIXTURE=str(self.root))
        self.env["PATH"] = str(self.root) + os.pathsep + self.env["PATH"]
        gh = self.root / "gh"
        gh.write_text(f"#!{sys.executable}\n" + '''import json
import os
from pathlib import Path
import shutil
import sys

root = Path(os.environ["BOXDB_GH_FIXTURE"])
args = sys.argv[1:]
with (root / "calls.jsonl").open("a") as calls:
    calls.write(json.dumps(args) + "\\n")
if args[0] == "api":
    print((root / "releases.json").read_text())
elif args[:2] == ["release", "download"]:
    source = root / args[2]
    destination = Path(args[args.index("--dir") + 1])
    for position, value in enumerate(args):
        if value == "--pattern":
            shutil.copyfile(source / args[position + 1], destination / args[position + 1])
    if os.environ.get("BOXDB_MUTATE_FORMULA"):
        with (root / "boxdb.rb").open("a") as formula:
            formula.write("# concurrent edit\\n")
else:
    sys.exit("Unexpected gh command")
''')
        gh.chmod(0o755)

    def add_release(self, version):
        destination = self.root / ("v" + version)
        destination.mkdir()
        names = [
            f"boxdb-{version}-aarch64-apple-darwin.tar.gz",
            f"boxdb-{version}-x86_64-unknown-linux-musl.tar.gz",
            f"boxdb-{version}.crate",
        ]
        digests = {}
        for name in names:
            payload = ("artifact:" + name).encode()
            (destination / name).write_bytes(payload)
            digests[name] = hashlib.sha256(payload).hexdigest()
        checksum = "".join(f"{digests[name]}  {name}\n" for name in names)
        (destination / "SHA256SUMS").write_text(checksum)
        assets = [{"name": name, "state": "uploaded", "digest": "sha256:" + digest}
                  for name, digest in digests.items()]
        assets.append({"name": "SHA256SUMS", "state": "uploaded",
                       "digest": "sha256:" + hashlib.sha256(checksum.encode()).hexdigest()})
        published = release("v" + version, assets=assets)
        self.releases.append(published)
        self.digests[version] = digests
        return published

    def run(self):
        (self.root / "releases.json").write_text(json.dumps([self.releases]))
        return subprocess.run([sys.executable, str(ROOT / "scripts/update-boxdb.py"),
                               "--formula", str(self.formula)], env=self.env,
                              capture_output=True, text=True)

    def replace_checksums(self, version, text):
        (self.root / ("v" + version) / "SHA256SUMS").write_text(text)
        checksum_asset = next(asset for item in self.releases if item["tag_name"] == "v" + version
                              for asset in item["assets"] if asset["name"] == "SHA256SUMS")
        checksum_asset["digest"] = "sha256:" + hashlib.sha256(text.encode()).hexdigest()

    def calls(self):
        return [json.loads(line) for line in (self.root / "calls.jsonl").read_text().splitlines()]

    def assert_unchanged(self, test, result, original):
        test.assertNotEqual(result.returncode, 0)
        test.assertEqual(self.formula.read_text(), original)
        test.assertEqual(list(self.root.glob(".boxdb-*")), [])


class UpdateBoxDBTests(unittest.TestCase):
    def test_selects_highest_semantic_stable_release(self):
        version, _ = updater.latest_release([
            release("v0.9.0"), release("v0.10.0"), release("v0.2.1"),
            release("v2.0.0", draft=True), release("v3.0.0", prerelease=True),
            release("v99.0.0-rc.1"), release("v01.0.0"), release("other-v9.0.0"),
        ])
        self.assertEqual(version, "0.10.0")

    def test_cli_updates_all_platform_hashes_and_preserves_formula(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = GitHubFixture(directory)
            fixture.add_release("0.2.0")
            result = fixture.run()
            self.assertEqual(result.returncode, 0, result.stderr)
            hashes = fixture.digests["0.2.0"]
            expected = FORMULA.replace("0.1.0", "0.2.0")
            expected = expected.replace("a" * 64, hashes["boxdb-0.2.0-aarch64-apple-darwin.tar.gz"])
            expected = expected.replace("b" * 64, hashes["boxdb-0.2.0-x86_64-unknown-linux-musl.tar.gz"])
            expected = expected.replace("c" * 64, hashes["boxdb-0.2.0.crate"])
            self.assertEqual(fixture.formula.read_text(), expected)

    def test_requires_a_stable_release(self):
        with self.assertRaises(ValueError):
            updater.latest_release([release("v1.0.0-rc.1"), release("v2.0.0", draft=True)])

    def test_cli_is_idempotent_and_preserves_file_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = GitHubFixture(directory)
            fixture.add_release("0.2.0")
            fixture.formula.chmod(0o640)
            self.assertEqual(fixture.run().returncode, 0)
            before = fixture.formula.stat()
            original = fixture.formula.read_bytes()
            result = fixture.run()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("up to date", result.stdout)
            after = fixture.formula.stat()
            self.assertEqual(after.st_ino, before.st_ino)
            self.assertEqual(after.st_mtime_ns, before.st_mtime_ns)
            self.assertEqual(after.st_mode & 0o777, 0o640)
            self.assertEqual(fixture.formula.read_bytes(), original)
            self.assertEqual(list(fixture.root.glob(".boxdb-*")), [])

    def test_cli_rejects_downgrade_before_downloading(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = GitHubFixture(directory)
            fixture.add_release("0.0.9")
            result = fixture.run()
            fixture.assert_unchanged(self, result, FORMULA)
            self.assertIn("downgrade", result.stderr)
            self.assertEqual(len(fixture.calls()), 1)

    def test_cli_never_falls_back_from_an_incomplete_newest_release(self):
        for absent in ("macos", "linux", "source", "checksums", "uploading"):
            with self.subTest(absent=absent), tempfile.TemporaryDirectory() as directory:
                fixture = GitHubFixture(directory)
                fixture.add_release("0.1.0")
                latest = fixture.add_release("0.2.0")
                position = {"macos": 0, "linux": 1, "source": 2, "checksums": 3, "uploading": 0}[absent]
                if absent == "uploading":
                    latest["assets"][position]["state"] = "new"
                else:
                    latest["assets"].pop(position)
                result = fixture.run()
                fixture.assert_unchanged(self, result, FORMULA)
                self.assertEqual(len(fixture.calls()), 1)

    def test_cli_rejects_invalid_missing_and_duplicate_checksum_entries(self):
        for defect in ("invalid", "missing", "duplicate", "wrong"):
            with self.subTest(defect=defect), tempfile.TemporaryDirectory() as directory:
                fixture = GitHubFixture(directory)
                fixture.add_release("0.2.0")
                path = fixture.root / "v0.2.0" / "SHA256SUMS"
                lines = path.read_text().splitlines(keepends=True)
                if defect == "invalid":
                    lines[2] = "not a checksum\n"
                elif defect == "missing":
                    lines.pop()
                elif defect == "duplicate":
                    lines.append(lines[2])
                else:
                    lines[2] = "0" * 64 + lines[2][64:]
                fixture.replace_checksums("0.2.0", "".join(lines))
                result = fixture.run()
                fixture.assert_unchanged(self, result, FORMULA)

    def test_cli_rejects_corrupt_last_asset_even_without_github_digests(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = GitHubFixture(directory)
            latest = fixture.add_release("0.2.0")
            for asset in latest["assets"]:
                asset.pop("digest")
            (fixture.root / "v0.2.0" / "boxdb-0.2.0.crate").write_bytes(b"corrupt source")
            result = fixture.run()
            fixture.assert_unchanged(self, result, FORMULA)
            self.assertIn("SHA256SUMS", result.stderr)

    def test_cli_validates_github_digests_for_all_four_downloads(self):
        for position in range(4):
            with self.subTest(position=position), tempfile.TemporaryDirectory() as directory:
                fixture = GitHubFixture(directory)
                latest = fixture.add_release("0.2.0")
                latest["assets"][position]["digest"] = "sha256:" + "0" * 64
                result = fixture.run()
                fixture.assert_unchanged(self, result, FORMULA)
                self.assertIn("GitHub", result.stderr)

    def test_cli_rejects_mutated_assets_for_an_existing_version(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = GitHubFixture(directory)
            latest = fixture.add_release("0.2.0")
            self.assertEqual(fixture.run().returncode, 0)
            original = fixture.formula.read_text()
            source = fixture.root / "v0.2.0" / "boxdb-0.2.0.crate"
            source.write_bytes(b"replacement source")
            replacement_digest = hashlib.sha256(source.read_bytes()).hexdigest()
            latest["assets"][2]["digest"] = "sha256:" + replacement_digest
            checksums = (source.parent / "SHA256SUMS").read_text()
            checksums = checksums.replace(fixture.digests["0.2.0"][source.name], replacement_digest)
            fixture.replace_checksums("0.2.0", checksums)
            result = fixture.run()
            fixture.assert_unchanged(self, result, original)
            self.assertIn("existing version", result.stderr)

    def test_cli_rejects_damaged_formula_without_partial_update(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = GitHubFixture(directory)
            fixture.add_release("0.2.0")
            original = FORMULA.replace('      sha256 "' + "c" * 64 + '"', "      # missing checksum", 1)
            fixture.formula.write_text(original)
            result = fixture.run()
            fixture.assert_unchanged(self, result, original)

    def test_cli_requires_consistent_tag_and_filename_versions(self):
        for defect in ("tag", "mixed"):
            with self.subTest(defect=defect), tempfile.TemporaryDirectory() as directory:
                fixture = GitHubFixture(directory)
                fixture.add_release("0.2.0")
                original = FORMULA.replace("/v0.1.0/", "/v0.0.9/", 1)
                if defect == "mixed":
                    original = original.replace("/boxdb-0.1.0-", "/boxdb-0.0.9-", 1)
                fixture.formula.write_text(original)
                result = fixture.run()
                fixture.assert_unchanged(self, result, original)
                self.assertFalse((fixture.root / "calls.jsonl").exists())

    def test_cli_preserves_concurrent_formula_edits(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = GitHubFixture(directory)
            fixture.add_release("0.2.0")
            fixture.env["BOXDB_MUTATE_FORMULA"] = "1"
            result = fixture.run()
            fixture.assert_unchanged(self, result, FORMULA + "# concurrent edit\n")
            self.assertIn("changed while verifying", result.stderr)

    def test_failed_atomic_publication_preserves_formula_and_cleans_staging(self):
        with tempfile.TemporaryDirectory() as directory:
            formula = Path(directory) / "boxdb.rb"
            formula.write_text(FORMULA)
            updated = FORMULA.replace("0.1.0", "0.2.0")
            with patch.object(updater.os, "replace", side_effect=OSError("injected rename failure")):
                with self.assertRaises(OSError):
                    updater.publish_formula(formula, FORMULA, updated)
            self.assertEqual(formula.read_text(), FORMULA)
            self.assertEqual(list(Path(directory).glob(".boxdb-*")), [])


if __name__ == "__main__":
    unittest.main()
