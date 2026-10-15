# Homebrew tap

## BoxDB

Install [BoxDB](https://github.com/lebedev-nikita/boxdb), an experimental SQL
database for single-server apps and Git-tracked data:

```sh
brew install lebedev-nikita/tap/boxdb
```

Apple Silicon macOS and x86-64 Linux use release binaries. Intel macOS and ARM
Linux build from the source package with Rust and CMake. Update with:

```sh
brew update
brew upgrade boxdb
```

The update workflow checks stable BoxDB releases hourly and can be run manually
from Actions. It verifies the binary and source archives against `SHA256SUMS`
before updating the formula. Drafts, prereleases, incomplete releases, and
downgrades are excluded. Published assets must remain unchanged.

For maintainers, releases need both CLI archives, the `.crate` source package,
and `SHA256SUMS`. The updater and workflow define the required filenames. The
workflow uses this tap's `GITHUB_TOKEN`; no extra credentials are required.
A sparse maintenance commit keeps scheduled checks active during quiet periods.

```sh
python3 -m unittest discover -s tests
python3 scripts/update-boxdb.py
brew style --formula lebedev-nikita/tap/boxdb
brew audit --strict --formula lebedev-nikita/tap/boxdb
brew test lebedev-nikita/tap/boxdb
```

## Concentration Slop

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

## Gitler

Install [Gitler](https://github.com/lebedev-nikita/gitler), a desktop Git graph for
branches and worktrees, on a Mac with Apple Silicon:

```sh
brew install --cask lebedev-nikita/tap/gitler
gitler /path/to/repository
```

This installs `Gitler.app`, the `gitler` command, and Git. Update with:

```sh
brew update
brew upgrade --cask lebedev-nikita/tap/gitler
```

If installed from `jeff-business/tap`, switch with:

```sh
brew reinstall --cask lebedev-nikita/tap/gitler
```

The app uses ad-hoc signing and is not notarized.

The update workflow checks published Gitler releases hourly, including release
candidates. It uses the matching released `scripts/release.py` helper to update
the version and archive checksum, with this tap's `GITHUB_TOKEN`; no extra
credentials are required. Run an immediate check with:

```sh
gh workflow run update-gitler.yml --repo lebedev-nikita/homebrew-tap
```

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
