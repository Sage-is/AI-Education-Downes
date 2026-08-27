cask "mini" do
  version "0.1.5"
  sha256 "6fa9deeee38373108526e512a87b85d30e4f3556ddb98fdd1aaabde2e46d2667"

  url "https://github.com/Sage-is/ai-ui-mini/releases/download/mini-v#{version}/mini-#{version}-darwin-arm64.tar.gz"
  name "Sage.is mini"
  desc "Sage.is AI-UI mini — the platform, with no agent bundled"
  homepage "https://sage.is/mini"

  depends_on arch: :arm64

  # The bundle is self-contained: engine, sandbox profile and curriculum
  # template all live in Contents/Resources, so the app works wherever it lands.
  app "Sage.is mini.app"
  binary "#{appdir}/Sage.is mini.app/Contents/Resources/launcher/downes.sh", target: "mini"

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
                   args: ["-d", "-r", "com.apple.quarantine", "#{appdir}/Sage.is mini.app"],
                   must_succeed: false
  end

  # Courses are the teacher's work and are never removed. Only our own state
  # goes, and only on an explicit `brew uninstall --zap`.
  zap trash: [
    "~/SageMini/.downes",
  ]

  caveats do
    "Your work lives in ~/SageMini. For the curriculum agent: brew install sage-is/apps/downes"
  end
end
