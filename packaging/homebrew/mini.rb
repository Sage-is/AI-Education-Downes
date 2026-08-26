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
  version "0.1.2"
  license "MIT"

  on_arm do
    url "https://github.com/Sage-is/ai-ui-mini/releases/download/mini-v0.1.2/mini-0.1.2-darwin-arm64.tar.gz"
    sha256 "1a6e023dad4628c7daeb4936a0459909cf92ec9b49f73b768210860125e86aef"
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

  # ~/Applications is indexed by Finder, Spotlight and Launchpad and needs no
  # sudo; /Applications is root-owned and a formula cannot write there.
  def post_install
    apps = Pathname.new(Dir.home)/"Applications"
    apps.mkpath
    link = apps/"Sage.is mini.app"
    link.unlink if link.symlink? || link.exist?
    link.make_symlink(opt_prefix/"Sage.is mini.app")
  end

  def caveats
    <<~EOS
      Sage.is mini is installed and ready. You'll find it here:

        ~/Applications/Sage.is mini.app

      Or run it from a terminal:

        mini

      To put it in the main /Applications folder instead (you'll need your password):

        sudo ln -sfn "#{opt_prefix}/Sage.is mini.app" "/Applications/Sage.is mini.app"

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
