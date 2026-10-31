import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location("update_cliprelay", Path(__file__).resolve().parents[1] / "scripts/update-cliprelay.py")
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


def release(tag, **kwargs):
    return {"tag_name": tag, "draft": False, "prerelease": False, **kwargs}


class UpdateClipRelayTests(unittest.TestCase):
    def test_selects_numeric_mac_version_without_android_drafts_or_prereleases(self):
        version, _ = updater.latest_release([
            release("android/v9.0.0"), release("mac/v0.7.9"), release("mac/v0.7.10"),
            release("mac/v1.0.0-rc.1"), release("mac/v2.0.0", prerelease=True),
            release("mac/v3.0.0", draft=True), release("mac/v01.0.0"),
        ])
        self.assertEqual(version, "0.7.10")

    def test_requires_a_stable_mac_release(self):
        with self.assertRaises(ValueError):
            updater.latest_release([release("android/v1.0.0"), release("mac/v1.0.0-rc.1")])

    def test_rejects_downgrade(self):
        with self.assertRaises(ValueError):
            updater.updated_cask('  version "0.7.10"\n', "0.7.9", "a" * 64)

    def test_updates_version_and_checksum_without_changing_artifacts(self):
        original = '  version "0.7.5"\n  sha256 "' + "a" * 64 + '"\n  app "ClipRelay.app"\n'
        expected = original.replace('"0.7.5"', '"0.7.6"').replace("a" * 64, "b" * 64)
        self.assertEqual(updater.updated_cask(original, "0.7.6", "b" * 64), expected)

    def test_verifies_digest_and_rejects_corruption_or_wrong_filename(self):
        with tempfile.TemporaryDirectory() as directory:
            dmg = Path(directory) / "ClipRelay-0.7.6.dmg"
            dmg.write_bytes(b"dmg")
            digest = hashlib.sha256(b"dmg").hexdigest()
            checksum = Path(directory) / "ClipRelay-0.7.6.dmg.sha256"
            checksum.write_text(f"{digest}  ClipRelay-0.7.6.dmg\n")
            self.assertEqual(updater.verified_digest(dmg, checksum), digest)
            checksum.write_text(f"{'0' * 64}  ClipRelay-0.7.6.dmg\n")
            with self.assertRaises(ValueError):
                updater.verified_digest(dmg, checksum)
            checksum.write_text(f"{digest}  Other.dmg\n")
            with self.assertRaises(ValueError):
                updater.verified_digest(dmg, checksum)


if __name__ == "__main__":
    unittest.main()
