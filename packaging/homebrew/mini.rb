cask "mini" do
  version "0.1.4"
  sha256 "7c011828831944ea8dc79f48bf050ffb40b538a111d2f9ebb823f4f3800fbb89"

  url "https://github.com/Sage-is/ai-ui-mini/releases/download/mini-v#{version}/mini-#{version}-darwin-arm64.tar.gz"
  name "Sage.is mini"
  desc "Sage.is AI-UI mini — the platform, with no agent bundled"
  homepage "https://sage.is/mini"

  depends_on arch: :arm64

  # The bundle is self-contained: engine, sandbox profile and curriculum
  # template all live in Contents/Resources, so the app works wherever it lands.
  app "Sage.is mini.app"
  binary "#{appdir}/Sage.is mini.app/Contents/Resources/launcher/downes.sh", target: "mini"

  # Courses are the teacher's work and are never removed. Only our own state
  # goes, and only on an explicit `brew uninstall --zap`.
  zap trash: [
    "~/SageMini/.downes",
  ]

  caveats do
    "Your work lives in ~/SageMini. For the curriculum agent: brew install sage-is/apps/downes"
  end
end
