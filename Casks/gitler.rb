cask "gitler" do
  version "0.5.4"
  sha256 "4783631d9a921094a5ab677f4106f4f9a1039ca7747e59df572c48492eb44530"

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
