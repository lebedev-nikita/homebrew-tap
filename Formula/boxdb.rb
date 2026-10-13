class Boxdb < Formula
  desc "Embedded SQL database with strict types, Git-friendly files, and S3 backups"
  homepage "https://github.com/lebedev-nikita/boxdb"
  license "MIT"

  on_macos do
    on_arm do
      url "https://github.com/lebedev-nikita/boxdb/releases/download/v0.1.0/boxdb-0.1.0-aarch64-apple-darwin.tar.gz"
      sha256 "05bdcc98a33e7dee4c06c99eaaf91539da9d67090fd537f7ea3caba8027a21fa"
    end

    on_intel do
      url "https://github.com/lebedev-nikita/boxdb/releases/download/v0.1.0/boxdb-0.1.0.crate"
      sha256 "48079d57b1e3d9a061b37f3278bf46d3166d910780162e69831935c4ce1e4ea4"

      depends_on "cmake" => :build
      depends_on "rust" => :build
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/lebedev-nikita/boxdb/releases/download/v0.1.0/boxdb-0.1.0-x86_64-unknown-linux-musl.tar.gz"
      sha256 "a1bfbcfdc848b018c8d599c5c57986905655b1de5c8670ee10fa82fa27767bbc"
    end

    on_arm do
      url "https://github.com/lebedev-nikita/boxdb/releases/download/v0.1.0/boxdb-0.1.0.crate"
      sha256 "48079d57b1e3d9a061b37f3278bf46d3166d910780162e69831935c4ce1e4ea4"

      depends_on "cmake" => :build
      depends_on "rust" => :build
    end
  end

  def fetch
    system "cargo", "fetch", *std_cargo_fetch_args if (buildpath/"Cargo.toml").exist?
  end

  def install
    if (buildpath/"Cargo.toml").exist?
      system "cargo", "install", *std_cargo_args
    else
      bin.install "boxdb"
    end
    doc.install "README.md"
    (doc/"docs").install "docs/replication.md"
    (doc/"assets").install "assets/icon.svg"
  end

  test do
    assert_equal "boxdb #{version}\n", shell_output("#{bin}/boxdb --version")
    readable = testpath/"readable.jsonl"
    binary = testpath/"binary.boxdb"
    system bin/"boxdb", readable, "--format", "readable", "-e",
           "CREATE TABLE items(id INTEGER); INSERT INTO items VALUES(7)"
    assert_equal "id\n7\n", shell_output("#{bin}/boxdb #{readable} -e 'SELECT id FROM items'")
    assert_match "type mismatch",
                 shell_output("#{bin}/boxdb #{readable} -e \"INSERT INTO items VALUES('7')\" 2>&1", 1)
    system bin/"boxdb", "convert", readable, binary, "--format", "binary"
    assert_equal "id\n7\n", shell_output("#{bin}/boxdb #{binary} -e 'SELECT id FROM items'")
  end
end
