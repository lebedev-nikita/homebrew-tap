cask "open-dictate" do
  version "0.5.2"
  sha256 "7a051356019e8ad3835bcefd24da31084a301112d3b62231976655de5b34de7f"

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
