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
