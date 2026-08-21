# Homebrew formula for the sage-is tap: brew install sage-is/tap/downes
# v1 ships the fork binary + launcher + Downes.app shim via the tap, which
# sidesteps Gatekeeper quarantine (no signing needed). The notarized DMG is
# the backlogged alternative for teachers without Homebrew.
class Downes < Formula
  desc "Course-design studio for teachers, on Sage.is AI-UI mini"
  homepage "https://sage.is/downes"
  version "0.1.0"
  license "MIT"

  # Placeholder until the ai-ui-mini fork publishes a release tarball.
  url "https://github.com/Sage-is/ai-ui-mini/releases/download/v0.1.0/downes-0.1.0.tar.gz"
  sha256 :no_check

  def install
    libexec.install Dir["*"]
    (bin/"downes").write <<~SH
      #!/bin/bash
      exec "#{libexec}/launcher/downes.sh" "$@"
    SH
    chmod 0755, bin/"downes"
    prefix.install "launcher/Downes.app"
  end

  def caveats
    <<~EOS
      Downes installed. Launch the studio with:
        downes
      Or open Downes.app from:
        #{prefix}/Downes.app
      Your courses live in ~/Downes. Nothing outside that folder is touched.
    EOS
  end

  test do
    assert_predicate bin/"downes", :executable?
  end
end
