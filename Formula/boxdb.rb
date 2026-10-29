class Boxdb < Formula
  desc "SQLite with validated types, exact decimals, and readable YAML storage"
  homepage "https://github.com/lebedev-nikita/boxdb"
  license "MIT"

  on_macos do
    on_arm do
      url "https://github.com/lebedev-nikita/boxdb/releases/download/v0.5.1/boxdb-0.5.1-aarch64-apple-darwin.tar.gz"
      sha256 "6a0bee9e43483dc9d8c78ba609bc4ac1658f2cd7188565c28fefc677407f73ac"
    end

    on_intel do
      url "https://github.com/lebedev-nikita/boxdb/releases/download/v0.5.1/boxdb-0.5.1.crate"
      sha256 "0112f98cd033993776bf28d2c767c720db1634fb54756e518035a6605db40d66"

      depends_on "cmake" => :build
      depends_on "rust" => :build
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/lebedev-nikita/boxdb/releases/download/v0.5.1/boxdb-0.5.1-x86_64-unknown-linux-musl.tar.gz"
      sha256 "d5f7077ca1d4cdc2f49738e99639d2a794a2e83c4b071b563e1ff8617bad8b15"
    end

    on_arm do
      url "https://github.com/lebedev-nikita/boxdb/releases/download/v0.5.1/boxdb-0.5.1.crate"
      sha256 "0112f98cd033993776bf28d2c767c720db1634fb54756e518035a6605db40d66"

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
