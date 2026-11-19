class Boxdb < Formula
  desc "SQLite with validated types, exact decimals, and readable YAML storage"
  homepage "https://github.com/lebedev-nikita/boxdb"
  license "MIT"

  on_macos do
    on_arm do
      url "https://github.com/lebedev-nikita/boxdb/releases/download/v0.8.1/boxdb-0.8.1-aarch64-apple-darwin.tar.gz"
      sha256 "3dc1d2ddd369d6cff23a13434ea67307e1c3f8623067cae2110ecc4207448558"
    end

    on_intel do
      url "https://github.com/lebedev-nikita/boxdb/releases/download/v0.8.1/boxdb-0.8.1.crate"
      sha256 "e7f9fbacea187535f1a57edb0a0738226d331924f39bf8005a50895be9a23c73"

      depends_on "cmake" => :build
      depends_on "rust" => :build
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/lebedev-nikita/boxdb/releases/download/v0.8.1/boxdb-0.8.1-x86_64-unknown-linux-musl.tar.gz"
      sha256 "a027991fc9a13d7176e7ae14d8db16fafcfbf854a3e7ec36d047ffa551ac06f5"
    end

    on_arm do
      url "https://github.com/lebedev-nikita/boxdb/releases/download/v0.8.1/boxdb-0.8.1.crate"
      sha256 "e7f9fbacea187535f1a57edb0a0738226d331924f39bf8005a50895be9a23c73"

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
