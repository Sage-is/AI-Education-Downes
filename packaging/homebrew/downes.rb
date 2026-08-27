cask "downes" do
  version "0.1.4"
  sha256 "e973e0e8ec71204a7bb4d4ce224b60712a884cd576dd1f46f1a26a3ce32d8bd2"

  url "https://github.com/Sage-is/AI-Education-Downes/releases/download/v#{version}/downes-#{version}-darwin-arm64.tar.gz"
  name "Downes"
  desc "Course-design studio for teachers, on Sage.is AI-UI mini"
  homepage "https://sage.is/downes"

  depends_on arch: :arm64

  # The bundle is self-contained: engine, sandbox profile and curriculum
  # template all live in Contents/Resources, so the app works wherever it lands.
  app "Downes.app"
  binary "#{appdir}/Downes.app/Contents/Resources/launcher/downes.sh", target: "downes"

  # Courses are the teacher's work and are never removed. Only our own state
  # goes, and only on an explicit `brew uninstall --zap`.
  zap trash: [
    "~/Downes/.downes",
  ]

  caveats do
    "Your courses live in ~/Downes. Downes works in that one folder."
  end
end
