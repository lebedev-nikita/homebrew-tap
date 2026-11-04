cask "app-swipe" do
  version "0.2.3"
  sha256 "3251d55a1a3c36ba8ff9f2a4bba064dc5d2695a939d0d98eafa8d2121624846a"

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
