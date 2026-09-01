cask "downes" do
  version "0.1.9"
  sha256 "d4c191a98136cd97c6ab33437dbb9edfa47fe9b0f602fb6f2e72af7807682f8b"

  url "https://github.com/Sage-is/AI-Education-Downes/releases/download/v#{version}/downes-#{version}-darwin-arm64.tar.gz"
  name "Downes"
  desc "Course-design studio for teachers, on Sage.is AI-UI mini"
  homepage "https://sage.is/downes"

  depends_on arch: :arm64

  # The bundle is self-contained: engine, sandbox profile and curriculum
  # template all live in Contents/Resources, so the app works wherever it lands.
  app "Downes.app"
  binary "#{appdir}/Downes.app/Contents/Resources/launcher/downes.sh", target: "downes"

  # The app is ad-hoc signed, not notarized, so Gatekeeper would refuse it and
  # the teacher would have to right-click -> Open. Clearing the quarantine flag
  # here removes that step.
  #
  # This is a deliberate trade, not an oversight: it disables Gatekeeper's check
  # for this app on every install, which is what Homebrew deprecated
  # --no-quarantine to discourage. Notarization is the real fix and removes the
  # need for this block entirely.
  postflight do
    system_command "/usr/bin/xattr",
                   args: ["-d", "-r", "com.apple.quarantine", "#{appdir}/Downes.app"],
                   must_succeed: false
  end

  # Courses are the teacher's work and are never removed. Only our own state
  # goes, and only on an explicit `brew uninstall --zap`.
  zap trash: [
    "~/Downes/.downes",
  ]

  caveats do
    "Your courses live in ~/Downes. Downes works in that one folder."
  end
end
