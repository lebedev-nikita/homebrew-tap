cask "gitler" do
  version "0.5.3"
  sha256 "bb3e33c4495bcc0faa519e4d4b1b9c0a016a71f5813f807f71a763ed756f5b50"

  url "https://github.com/lebedev-nikita/gitler/releases/download/v#{version}/Gitler_#{version}_macos-arm64.app.tar.gz"
  name "Gitler"
  desc "Git graph for branches and worktrees"
  homepage "https://github.com/lebedev-nikita/gitler"

  livecheck do
    url :url
    regex(/^v?(\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?)$/i)
    strategy :github_releases do |json, regex|
      json.filter_map do |release|
        next if release["draft"]

        release["tag_name"]&.[](regex, 1)
      end
    end
  end

  depends_on arch: :arm64
  depends_on formula: "git"
  depends_on :macos

  app "Gitler.app"
  binary "#{appdir}/Gitler.app/Contents/MacOS/gitler"
end
