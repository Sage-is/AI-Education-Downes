# Homebrew formula for the Sage-is tap: brew install sage-is/apps/downes
#
# A FORMULA, deliberately, not a Cask. Casks apply Gatekeeper quarantine by
# default; formulas do not. Since the app is unsigned until the Startr LLC
# Apple enrolment completes, the formula is what gives teachers a clean
# install with no security warning at all.
#
# The payload is self-contained: the engine is a Bun single-file executable,
# so a Mac with nothing but Homebrew can run this. There is deliberately no
# depends_on for a language runtime — if one is ever needed, the payload was
# assembled wrong. See scripts/package_macos.sh.
#
# The release asset lives on AI-Education-Downes (AGPL) rather than the MIT
# fork: the payload combines the MIT engine and app with AGPL curriculum
# content (launcher, skills, studio template), so it is distributed from the
# stronger-copyleft side. See docs/legal/STATUS_MATRIX.md.
class Downes < Formula
  desc "Course-design studio for teachers, on Sage.is AI-UI mini"
  homepage "https://sage.is/downes"
  version "0.1.3"
  license "AGPL-3.0-or-later"

  on_arm do
    url "https://github.com/Sage-is/AI-Education-Downes/releases/download/v0.1.3/downes-0.1.3-darwin-arm64.tar.gz"
    sha256 "664885e80f450efef75c8b23b0d28e1fcafb826c6bf5bf81ced1a99e613f9c1a"
  end

  # Intel is not built yet. The Rust toolchain on the release machine has only
  # the aarch64 host target (no rustup), so an x86_64 app bundle needs an
  # Intel CI runner — see the release workflow. Failing loudly here is
  # deliberate: a formula pointing at a tarball that does not exist would
  # download-fail with a confusing 404 instead of saying why.
  on_intel do
    odie "Downes does not have an Intel build yet — Apple Silicon only for now."
  end

  def install
    # Everything lands in libexec as one unit. downes.sh and the app both
    # resolve the engine by walking up from their own location, so the
    # relative layout here is load-bearing:
    #   libexec/bin/opencode          engine
    #   libexec/Downes.app            the studio
    #   libexec/launcher/downes.sh    terminal launcher
    #   libexec/studio/               template copied to ~/Downes on first run
    libexec.install Dir["*"]

    (bin/"downes").write <<~SH
      #!/bin/bash
      exec "#{libexec}/launcher/downes.sh" "$@"
    SH
    chmod 0755, bin/"downes"

    # In prefix so `open` and Finder can reach it.
    prefix.install_symlink libexec/"Downes.app"
  end

  # There is deliberately no post_install placing the app in ~/Applications.
  # It cannot work: Homebrew replaces HOME with a temp directory it later
  # deletes, and runs post_install in a sandbox that permits writes only under
  # the formula prefix. The symlink reports success and creates nothing — a
  # step that lies is worse than no step. launcher/downes.sh does it instead,
  # where there is a real HOME and no sandbox, so running `downes` once from a
  # terminal places the app. The caveat below covers everyone else.
  def caveats
    <<~EOS
      Downes is installed. Run it once from a terminal:

        downes

      That also puts a clickable Downes in ~/Applications, which Finder,
      Spotlight and Launchpad index alongside /Applications.

      Prefer to place it yourself? No password needed:

        mkdir -p ~/Applications && ln -sfn "#{opt_prefix}/Downes.app" ~/Applications/Downes.app

      Your courses live in ~/Downes. Downes works in that one folder.
    EOS
  end

  test do
    assert_predicate bin/"downes", :executable?
    assert_predicate libexec/"bin/opencode", :executable?
    # The engine must be a real binary, not a shim needing a runtime.
    assert_match "Mach-O", shell_output("file #{libexec}/bin/opencode")
  end
end
