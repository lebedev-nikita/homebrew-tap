cask "concentration-slop" do
  version "0.2.0"
  sha256 "ca7803acaf322e1e08f2dad5cd6f935994d613a6bdd292da07a0da377b4b6152"

  url "https://github.com/lebedev-nikita/concentration-slop/releases/download/v#{version}/Concentration-Slop-#{version}-macos-universal.zip"
  name "Concentration Slop"
  desc "Silent looping gameplay in a floating window attached to your work app"
  homepage "https://github.com/lebedev-nikita/concentration-slop"

  depends_on formula: "deno"
  depends_on formula: "yt-dlp"
  depends_on macos: :sonoma

  app "Concentration Slop.app"

  caveats <<~EOS
    App binding requires Accessibility access in System Settings > Privacy & Security.
    This app is ad-hoc signed and is not notarized by Apple.
  EOS
end
