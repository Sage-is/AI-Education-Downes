cask "mini" do
  version "0.1.11"
  sha256 "5a88b690e25234f50272020029e885dac146aa3b04ed3e014b5aa85bd3139e0f"

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
    "~/SAGE.ISmini/.downes",
    # launcher/downes.sh writes this on every start so our state can never be
    # committed. It is ours, not the teacher's, so a --zap must take it too;
    # through 0.1.5 it survived and left the workspace non-empty after uninstall.
    "~/SAGE.ISmini/.gitignore",
    # The workspace was ~/SageMini through 0.1.7; take the old name too.
    "~/SageMini/.downes",
    "~/SageMini/.gitignore",
  ]

  caveats do
    "Your work lives in ~/SAGE.ISmini. For the curriculum agent: brew install --cask sage-is/apps/downes"
  end
end
