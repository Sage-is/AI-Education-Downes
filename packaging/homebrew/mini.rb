cask "mini" do
  version "0.1.7"
  sha256 "4be2580d28a30456e2545f312cb6952e5cf4d6b63a7a9471ac4fbeb76ec80848"

  url "https://github.com/Sage-is/ai-ui-mini/releases/download/mini-v#{version}/mini-#{version}-darwin-arm64.tar.gz"
  name "SAGE.IS mini"
  desc "Sage.is AI-UI mini — the platform, with no agent bundled"
  homepage "https://sage.is/mini"

  depends_on arch: :arm64

  # The bundle is self-contained: engine, sandbox profile and curriculum
  # template all live in Contents/Resources, so the app works wherever it lands.
  app "SAGE.IS mini.app"
  binary "#{appdir}/SAGE.IS mini.app/Contents/Resources/launcher/downes.sh", target: "mini"

  # The bundle was "Sage.is mini.app" through 0.1.5. macOS volumes are
  # case-insensitive by default, so the new name resolves to the old path and a
  # plain upgrade keeps the old casing on disk: the rename looks done in git and
  # never reaches the Dock. Remove any bundle that is ours case-insensitively
  # but is not spelled the new way. Comparing downcased names cannot tell the
  # two apart -- both lowercase to the same string -- so test the exact name.
  preflight do
    Dir.glob("#{appdir}/*.app").each do |bundle|
      base = File.basename(bundle)
      next if base == "SAGE.IS mini.app"
      FileUtils.rm_rf(bundle) if base.downcase == "sage.is mini.app"
    end
  end

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
                   args: ["-d", "-r", "com.apple.quarantine", "#{appdir}/SAGE.IS mini.app"],
                   must_succeed: false
  end

  # Courses are the teacher's work and are never removed. Only our own state
  # goes, and only on an explicit `brew uninstall --zap`.
  zap trash: [
    "~/SageMini/.downes",
    # launcher/downes.sh writes this on every start so our state can never be
    # committed. It is ours, not the teacher's, so a --zap must take it too;
    # through 0.1.5 it survived and left ~/SageMini non-empty after uninstall.
    "~/SageMini/.gitignore",
  ]

  caveats do
    "Your work lives in ~/SageMini. For the curriculum agent: brew install sage-is/apps/downes"
  end
end
