cask "open-dictate" do
  version "0.4.4"
  sha256 "6f2608cbdf034b8b48fc9e7a0a3a5904a03811406b755cce5919603d8f725fa1"

  url "https://github.com/lebedev-nikita/open-dictate/releases/download/macos-v#{version}/OpenDictate-macOS-#{version}-universal.dmg"
  name "OpenDictate"
  desc "Menu bar dictation and voice editing using your OpenAI API key"
  homepage "https://github.com/lebedev-nikita/open-dictate"

  livecheck do
    url :homepage
    regex(/^macos-v(\d+\.\d+\.\d+)$/i)
    strategy :github_releases
  end

  depends_on macos: :sonoma

  app "OpenDictate.app"

  caveats <<~EOS
    GitHub release builds are locally signed and not notarized.
    If macOS blocks launching OpenDictate, use System Settings > Privacy & Security > Open Anyway.
    Allow Microphone and Accessibility when setting up the app, and supply your own OpenAI API key.
  EOS
end
