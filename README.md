# Homebrew tap

Install [Concentration Slop](https://github.com/lebedev-nikita/concentration-slop) on macOS 14+, on Apple Silicon or Intel:

```sh
brew install --cask lebedev-nikita/tap/concentration-slop
```

This installs **Concentration Slop.app**, yt-dlp, and Deno. Open the app from Applications.
Window binding requires Accessibility access in System Settings.
Releases are ad-hoc signed and not notarized by Apple; macOS may require approval in Privacy & Security.

Update with:

```sh
brew update
brew upgrade --cask lebedev-nikita/tap/concentration-slop
```

If installed from `jeff-business/tap`, switch to this tap with:

```sh
brew update
brew reinstall --cask lebedev-nikita/tap/concentration-slop
```

After publishing a Concentration Slop release, update the cask version and archive SHA-256.
Keep published release assets unchanged.

## OpenDictate

Install [OpenDictate](https://github.com/lebedev-nikita/open-dictate), a macOS
menu bar app for dictation and voice editing with your own OpenAI API key:

```bash
brew install --cask lebedev-nikita/tap/open-dictate
```

Requires macOS 14+ on Apple Silicon or Intel. Quit OpenDictate before upgrading:

```bash
brew update
brew upgrade --cask lebedev-nikita/tap/open-dictate
```

If you previously installed the DMG manually, quit the app and use
`brew install --cask --adopt lebedev-nikita/tap/open-dictate` to adopt an identical
release. If the copies differ, remove only `/Applications/OpenDictate.app` and
run the normal install command. Settings, local history and Keychain credentials
are retained. Ordinary `brew uninstall --cask open-dictate` also keeps this data.

GitHub builds are locally signed and **not notarized**. If macOS blocks launch,
use **System Settings → Privacy & Security → Open Anyway** for OpenDictate.
On first launch, save your API key and grant Microphone and Accessibility access.
See the [app's setup guide](https://github.com/lebedev-nikita/open-dictate#install-on-macos).

### OpenDictate maintenance

The update workflow checks stable `macos-vX.Y.Z` releases every six hours and
can also be run manually from Actions. Android releases, drafts and prereleases
are excluded. Before updating the pinned version and SHA-256, it downloads the
DMG and verifies it against the release's checksum attachment. No additional
GitHub credentials are required; the workflow uses this tap's `GITHUB_TOKEN`.

```bash
python3 -m unittest discover -s tests
python3 scripts/update-cask.py
brew style Casks/open-dictate.rb
```

The updater requires Python 3 and an authenticated `gh` CLI. Cask checks run on
macOS in CI. This tap distributes published binaries; it does not build the app.
