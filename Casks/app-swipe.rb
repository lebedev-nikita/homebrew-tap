cask "app-swipe" do
  version "0.3.0"
  sha256 "211a364b858288f460ccd2a4bb7d85895530e1658db37e2b17424b6ac7edfef9"

  url "https://github.com/lebedev-nikita/AppSwipe/releases/download/v#{version}/AppSwipe-#{version}.zip"
  name "AppSwipe"
  desc "Switch apps and windows with trackpad swipes"
  homepage "https://github.com/lebedev-nikita/AppSwipe"

  livecheck do
    url :url
    strategy :github_latest
  end

  depends_on macos: :tahoe

  app "AppSwipe.app"

  zap trash: [
    "~/Library/Logs/AppSwipe",
    "~/Library/Preferences/io.github.lebedev-nikita.AppSwipe.plist",
  ]

  caveats <<~EOS
    AppSwipe release builds are signed with a self-signed certificate and not notarized.
    If macOS blocks launching AppSwipe, use System Settings > Privacy & Security > Open Anyway.
    Allow Accessibility, and Screen Recording for window previews, when AppSwipe asks.
  EOS
end
