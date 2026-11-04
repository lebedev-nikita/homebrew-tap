cask "app-swipe" do
  version "0.2.4"
  sha256 "41f6aa64b928db6ac9537388978e5784a2ad33eae29ca71c661beea8938d63c3"

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
