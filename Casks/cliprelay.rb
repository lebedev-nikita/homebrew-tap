cask "cliprelay" do
  version "0.7.6"
  sha256 "6504a98b42e3b190aa125f0a01567b9cd8abfe90629a1c94b0bd44c501e2c634"

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
    This fork build is ad-hoc signed and not notarized, so Gatekeeper blocks it.
    Before the first launch run:
      xattr -dr com.apple.quarantine /Applications/ClipRelay.app
  EOS
end
