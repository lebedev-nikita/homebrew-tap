import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location("update_cask", Path(__file__).resolve().parents[1] / "scripts/update-cask.py")
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


def release(tag, **kwargs):
    return {"tag_name": tag, "draft": False, "prerelease": False, **kwargs}


class UpdateCaskTests(unittest.TestCase):
    def test_selects_numeric_macos_version_without_android_drafts_or_prereleases(self):
        version, _ = updater.latest_release([
            release("v99.0.0"), release("macos-v0.9.0"), release("macos-v0.10.0"),
            release("macos-v1.0.0-rc.1"), release("macos-v2.0.0", prerelease=True),
            release("macos-v3.0.0", draft=True), release("macos-v01.0.0"),
        ])
        self.assertEqual(version, "0.10.0")

    def test_requires_a_stable_macos_release(self):
        with self.assertRaises(ValueError):
            updater.latest_release([release("v1.0.0"), release("macos-v1.0.0-rc.1")])

    def test_rejects_downgrade(self):
        with self.assertRaises(ValueError):
            updater.updated_cask('  version "0.10.0"\n', "0.9.0", "a" * 64)

    def test_updates_version_and_checksum_without_changing_artifacts(self):
        original = '  version "0.4.1"\n  sha256 "' + "a" * 64 + '"\n  app "OpenDictate.app"\n'
        expected = original.replace('"0.4.1"', '"0.4.2"').replace("a" * 64, "b" * 64)
        self.assertEqual(updater.updated_cask(original, "0.4.2", "b" * 64), expected)

    def test_verifies_digest_and_rejects_corruption_or_wrong_filename(self):
        with tempfile.TemporaryDirectory() as directory:
            dmg = Path(directory) / "OpenDictate.dmg"
            checksum = Path(directory) / "OpenDictate.dmg.sha256"
            dmg.write_bytes(b"test artifact")
            digest = hashlib.sha256(dmg.read_bytes()).hexdigest()
            checksum.write_text(f"{digest}  {dmg.name}\n")
            self.assertEqual(updater.verified_digest(dmg, checksum), digest)
            dmg.write_bytes(b"corrupt artifact")
            with self.assertRaises(ValueError):
                updater.verified_digest(dmg, checksum)
            checksum.write_text(f"{digest}  Other.dmg\n")
            with self.assertRaises(ValueError):
                updater.verified_digest(dmg, checksum)


if __name__ == "__main__":
    unittest.main()
