class Boxdb < Formula
  desc "SQLite with validated types, exact decimals, and readable YAML storage"
  homepage "https://github.com/lebedev-nikita/boxdb"
  license "MIT"

  on_macos do
    on_arm do
      url "https://github.com/lebedev-nikita/boxdb/releases/download/v0.6.0/boxdb-0.6.0-aarch64-apple-darwin.tar.gz"
      sha256 "90c0af9ac798f6143d97372b97b2ef8d1d6c9b8b09c8baef886918a0f7682ecb"
    end

    on_intel do
      url "https://github.com/lebedev-nikita/boxdb/releases/download/v0.6.0/boxdb-0.6.0.crate"
      sha256 "2691f522e339007084428c3e2d83684e51c0002e85c78d420ce5c4a970794e64"

      depends_on "cmake" => :build
      depends_on "rust" => :build
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/lebedev-nikita/boxdb/releases/download/v0.6.0/boxdb-0.6.0-x86_64-unknown-linux-musl.tar.gz"
      sha256 "9e2bcd94be8353764fa908df5e63e677079336f73a833c14c7e92cb1db25e485"
    end

    on_arm do
      url "https://github.com/lebedev-nikita/boxdb/releases/download/v0.6.0/boxdb-0.6.0.crate"
      sha256 "2691f522e339007084428c3e2d83684e51c0002e85c78d420ce5c4a970794e64"

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
    readable = testpath/"readable.yaml"
    binary = testpath/"binary.boxdb"
    system bin/"boxdb", readable, "--format", "readable", "-e",
           "CREATE TABLE items(id INTEGER); INSERT INTO items VALUES(7)"
    assert_equal "id\n7\n", shell_output("#{bin}/boxdb #{readable} -e 'SELECT id FROM items'")
    assert_match "cannot store TEXT value in INTEGER column",
                 shell_output("#{bin}/boxdb #{readable} -e \"INSERT INTO items VALUES('invalid')\" 2>&1", 1)
    system bin/"boxdb", "convert", readable, binary, "--format", "binary"
    assert_equal "id\n7\n", shell_output("#{bin}/boxdb #{binary} -e 'SELECT id FROM items'")
  end
end
