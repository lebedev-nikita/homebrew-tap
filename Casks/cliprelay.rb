cask "cliprelay" do
  version "0.7.5"
  sha256 "02d14cbc7e3deb0b61964c37b1bbe6f9547b60d470e56f2ae95807e2a0ad3973"

  url "https://github.com/lebedev-nikita/cliprelay/releases/download/mac/v#{version}/ClipRelay-#{version}.dmg"
  name "ClipRelay"
  desc "Clipboard sharing with Android devices over Bluetooth"
  homepage "https://github.com/lebedev-nikita/cliprelay"

  livecheck do
    url :url
    regex(%r{^mac/v(\d+\.\d+\.\d+)$}i)
    strategy :github_releases
  end

  depends_on macos: :ventura

  app "ClipRelay.app"

  zap trash: [
    "~/Library/Application Support/ClipRelay",
    "~/Library/Preferences/org.cliprelay.mac.plist",
  ]

  caveats <<~EOS
    This fork build is ad-hoc signed and not notarized. If macOS blocks launching
    ClipRelay, use System Settings > Privacy & Security > Open Anyway.
    In-app updates come from upstream ClipRelay and would replace this build;
    turn off "Automatically check for updates" in ClipRelay Settings to keep it.
  EOS
end
