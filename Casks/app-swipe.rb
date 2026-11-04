cask "app-swipe" do
  version "0.1.4"
  sha256 "c327160a4f713e5490b83d970d3f7d9d67c4d3f8bb4af65623a65e09018d834e"

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
