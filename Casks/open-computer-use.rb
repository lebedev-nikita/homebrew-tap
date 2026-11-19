cask "open-computer-use" do
  version "1.1.5"
  sha256 "f08e54092759b4918487239e3a6a78ed95e91ba6b3027dd78de3dce0628633bf"

  url "https://github.com/iFurySt/open-computer-use/releases/download/v#{version}/Open-Computer-Use-#{version}-macOS-universal.app.zip"
  name "Open Computer Use"
  desc "Computer Use MCP server and CLI for AI agents"
  homepage "https://github.com/iFurySt/open-computer-use"

  livecheck do
    url :url
    strategy :github_latest
  end

  depends_on macos: :sonoma

  app "Open Computer Use.app"
  binary "#{appdir}/Open Computer Use.app/Contents/MacOS/OpenComputerUse", target: "open-computer-use"
  binary "#{appdir}/Open Computer Use.app/Contents/MacOS/OpenComputerUse", target: "ocu"
end
