# Homebrew formula for the Sage-is tap: brew install sage-is/apps/mini
#
# Sage.is AI-UI mini is the platform. Downes is the first agent shipped on it,
# and has its own formula. This one carries no curriculum: no skills, no
# METHOD, no downes agent — you bring your own.
#
# That split is also the licence boundary. mini is MIT throughout, so the
# release asset lives on the MIT fork repo. The downes formula pulls from
# AI-Education-Downes because its payload includes AGPL curriculum content.
#
# A FORMULA, deliberately, not a Cask: casks apply Gatekeeper quarantine by
# default and formulas do not, so this installs without a security warning
# while the app is unsigned.
#
# Self-contained: the engine is a Bun single-file executable, so a Mac with
# nothing but Homebrew can run it. No depends_on for a language runtime — if
# one were ever needed, the payload was assembled wrong.
class Mini < Formula
  desc "Sage.is AI-UI mini — a light desktop platform for running AI agents"
  homepage "https://sage.is"
  version "0.1.3"
  license "MIT"

  on_arm do
    url "https://github.com/Sage-is/ai-ui-mini/releases/download/mini-v0.1.3/mini-0.1.3-darwin-arm64.tar.gz"
    sha256 "c1fcbf7d56353473eff72729882dc0bb71e24311114a85d4ea8691ba3bb49ad1"
  end

  # No Intel build yet — the release machine's Rust toolchain has only the
  # aarch64 host target. Failing loudly beats a confusing 404.
  on_intel do
    odie "Sage.is mini does not have an Intel build yet — Apple Silicon only for now."
  end

  def install
    # One unit in libexec. The app resolves the engine by walking up from its
    # own canonicalized path, so this relative layout is load-bearing:
    #   libexec/bin/opencode            engine
    #   libexec/Sage.is mini.app        the studio
    #   libexec/product                 which workspace folder to use
    libexec.install Dir["*"]

    (bin/"mini").write <<~SH
      #!/bin/bash
      exec "#{libexec}/launcher/downes.sh" "$@"
    SH
    chmod 0755, bin/"mini"

    prefix.install_symlink libexec/"Sage.is mini.app"
  end

  # There is deliberately no post_install placing the app in ~/Applications.
  # It cannot work: Homebrew replaces HOME with a temp directory it later
  # deletes, and runs post_install in a sandbox that permits writes only under
  # the formula prefix. The symlink reports success and creates nothing — a
  # step that lies is worse than no step. launcher/downes.sh does it instead,
  # where there is a real HOME and no sandbox, so running `mini` once from a
  # terminal places the app. The caveat below covers everyone else.
  def caveats
    <<~EOS
      Sage.is mini is installed. Run it once from a terminal:

        mini

      That also puts a clickable Sage.is mini in ~/Applications, which Finder,
      Spotlight and Launchpad index alongside /Applications.

      Prefer to place it yourself? No password needed:

        mkdir -p ~/Applications && ln -sfn "#{opt_prefix}/Sage.is mini.app" ~/Applications/

      Your work lives in ~/SageMini.

      This is the platform on its own, with no agent bundled. For the
      curriculum agent, install Downes:

        brew install sage-is/apps/downes
    EOS
  end

  test do
    assert_predicate bin/"mini", :executable?
    assert_predicate libexec/"bin/opencode", :executable?
    assert_match "Mach-O", shell_output("file #{libexec}/bin/opencode")
  end
end
