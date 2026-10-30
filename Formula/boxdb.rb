class Boxdb < Formula
  desc "SQLite with validated types, exact decimals, and readable YAML storage"
  homepage "https://github.com/lebedev-nikita/boxdb"
  license "MIT"

  on_macos do
    on_arm do
      url "https://github.com/lebedev-nikita/boxdb/releases/download/v0.7.0/boxdb-0.7.0-aarch64-apple-darwin.tar.gz"
      sha256 "3b5daadced40df8ab272ddcbfd8b87966289f090f6c824ac32cb0b4fc0f46211"
    end

    on_intel do
      url "https://github.com/lebedev-nikita/boxdb/releases/download/v0.7.0/boxdb-0.7.0.crate"
      sha256 "8746e0ddff185910ee61e9c4f98c6ba215d86c6668ced24591249d0ad442f48a"

      depends_on "cmake" => :build
      depends_on "rust" => :build
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/lebedev-nikita/boxdb/releases/download/v0.7.0/boxdb-0.7.0-x86_64-unknown-linux-musl.tar.gz"
      sha256 "5a380b687a9576867bc5236367646c2661e4aeb405504cc67266170c72912efb"
    end

    on_arm do
      url "https://github.com/lebedev-nikita/boxdb/releases/download/v0.7.0/boxdb-0.7.0.crate"
      sha256 "8746e0ddff185910ee61e9c4f98c6ba215d86c6668ced24591249d0ad442f48a"

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
