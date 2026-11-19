import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location(
    "update_open_computer_use", Path(__file__).resolve().parents[1] / "scripts/update-open-computer-use.py"
)
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


def release(tag, **kwargs):
    return {"tag_name": tag, "draft": False, "prerelease": False, **kwargs}


class UpdateOpenComputerUseTests(unittest.TestCase):
    def test_selects_numeric_stable_version_without_drafts_or_prereleases(self):
        version, _ = updater.latest_release([
            release("v1.1.5"), release("v1.1.10"), release("reference-bundles", prerelease=True),
            release("v1.2.0-rc.1"), release("v2.0.0", prerelease=True),
            release("v3.0.0", draft=True), release("v01.0.0"),
        ])
        self.assertEqual(version, "1.1.10")

    def test_requires_a_stable_release(self):
        with self.assertRaises(ValueError):
            updater.latest_release([release("reference-bundles"), release("v1.0.0-rc.1")])

    def test_rejects_downgrade(self):
        with self.assertRaises(ValueError):
            updater.updated_cask('  version "1.1.5"\n', "1.1.4", "a" * 64)

    def test_updates_version_and_checksum_without_changing_artifacts(self):
        original = '  version "1.1.5"\n  sha256 "' + "a" * 64 + '"\n  app "Open Computer Use.app"\n'
        expected = original.replace('"1.1.5"', '"1.1.6"').replace("a" * 64, "b" * 64)
        self.assertEqual(updater.updated_cask(original, "1.1.6", "b" * 64), expected)

    def test_verifies_digest_against_the_matching_sums_line(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / updater.archive_name("1.1.5")
            checksums = Path(directory) / "SHA256SUMS"
            archive.write_bytes(b"test artifact")
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            checksums.write_text(f"{'c' * 64}  other.tar.gz\n{digest}  {archive.name}\n")
            self.assertEqual(updater.verified_digest(archive, checksums), digest)
            archive.write_bytes(b"corrupt artifact")
            with self.assertRaises(ValueError):
                updater.verified_digest(archive, checksums)
            checksums.write_text(f"{digest}  other.zip\n")
            with self.assertRaises(ValueError):
                updater.verified_digest(archive, checksums)


if __name__ == "__main__":
    unittest.main()
