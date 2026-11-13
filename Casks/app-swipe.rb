cask "app-swipe" do
  version "0.4.0"
  sha256 "315c8556133efe52b69e08eb2451b75c2a8564c0c24743d6c119a9a5ef86d2d7"

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
