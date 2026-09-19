#Requires -Version 5.1
<#
.SYNOPSIS
  Build a Windows installer for Downes or SAGE.IS mini. The Windows half of
  scripts/package_macos.sh.

.DESCRIPTION
  Products:
    downes  the curriculum agent: engine + curriculum template. AGPL.
    mini    the bare platform, no agent and no template. MIT.

  Output: dist\<product>-<version>-windows-<arch>-setup.exe and its sha256.

  Run from a Windows machine with bun, the MSVC Rust toolchain and WebView2.
  A macOS or Linux host cannot produce this: the bundled engine is the one
  built for the host, so a cross-build would ship the wrong binary.

  What this does NOT do, deliberately:
    - Sign the installer. It is unsigned, so SmartScreen warns on first run:
      "More info" then "Run anyway".
    - Contain the engine. macOS runs it under a Seatbelt profile; Windows has
      no counterpart here, so say the app "works in one folder", never that it
      is sandboxed.
#>
[CmdletBinding()]
param(
  [ValidateSet('downes', 'mini')][string]$Product = 'downes',
  [ValidateSet('x64', 'arm64')][string]$Arch = 'x64'
)

$ErrorActionPreference = 'Stop'

$Repo = Split-Path -Parent $PSScriptRoot
$Fork = Join-Path $Repo 'ai-ui-mini'
$Studio = Join-Path $Fork 'packages\studio'
$SrcTauri = Join-Path $Studio 'src-tauri'

if (-not (Test-Path (Join-Path $SrcTauri 'tauri.conf.json'))) {
  throw "no fork checkout at $Fork - run: git submodule update --init"
}

$Version = (Get-Content (Join-Path $SrcTauri 'tauri.conf.json') -Raw | ConvertFrom-Json).version

# Pin the channel. Left unset, the fork's build script falls back to the current
# GIT BRANCH NAME, so the database filename would depend on which branch the
# release was cut from - and a Windows install would then disagree with a macOS
# one about where its sessions live.
if (-not $env:OPENCODE_CHANNEL) { $env:OPENCODE_CHANNEL = 'downes/v1' }

# Report a real version. Unset, the build stamps 0.0.0-<channel>-<timestamp>,
# which no provider gate accepts. One derivation for both platforms.
if (-not $env:OPENCODE_VERSION) {
  $env:OPENCODE_VERSION = (& bun (Join-Path $Studio 'scripts\engine-version.ts')).Trim()
}

if ($Product -eq 'downes') {
  $AppName = 'Downes'
  $env:DOWNES_PRODUCT = 'Downes'
  $env:DOWNES_TEMPLATE = Join-Path $Repo 'studio'
  $ConfigArg = 'src-tauri\tauri.windows.downes.conf.json'
} else {
  $AppName = 'SAGE.IS mini'
  $env:DOWNES_PRODUCT = 'SAGE.ISmini'
  Remove-Item Env:\DOWNES_TEMPLATE -ErrorAction SilentlyContinue
  $ConfigArg = 'src-tauri\tauri.mini.conf.json'
}

Write-Host "==> $AppName $Version, windows-$Arch, channel $($env:OPENCODE_CHANNEL), version $($env:OPENCODE_VERSION)"

# --- engine ----------------------------------------------------------------
$Engine = Join-Path $Fork "packages\opencode\dist\opencode-windows-$Arch\bin\opencode.exe"

$Reported = ''
if (Test-Path $Engine) { $Reported = (& $Engine --version 2>$null | Out-String).Trim() }

if ($Reported -ne $env:OPENCODE_VERSION) {
  $why = if (Test-Path $Engine) { "engine reports '$Reported', want '$($env:OPENCODE_VERSION)'" } else { 'no engine yet' }
  Write-Host "==> building engine ($why)"
  Push-Location (Join-Path $Fork 'packages\opencode')
  try { & bun script/build.ts --single } finally { Pop-Location }
  $Reported = (& $Engine --version 2>$null | Out-String).Trim()
}

if (-not (Test-Path $Engine)) { throw "engine missing after build: $Engine" }
if ($Reported -ne $env:OPENCODE_VERSION) {
  throw "engine reports '$Reported', expected '$($env:OPENCODE_VERSION)'. Delete $Fork\packages\opencode\dist and re-run."
}

# --- bundle ----------------------------------------------------------------
# tauri.windows.conf.json is merged automatically and runs scripts\stage-payload.ts
# as its beforeBuildCommand: that stages the engine, the product marker and -
# when DOWNES_TEMPLATE is set - the curriculum template, and refuses an engine
# whose version does not match the one above.
Write-Host "==> building $AppName.exe (release)"
Push-Location $Studio
try { & bunx tauri build --config $ConfigArg } finally { Pop-Location }

$Installer = Get-ChildItem (Join-Path $SrcTauri 'target\release\bundle\nsis') -Filter '*-setup.exe' |
  Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $Installer) { throw 'no installer produced' }

# --- checks ----------------------------------------------------------------
# The installer must carry an engine, or an installed copy finds nothing: there
# is no Homebrew cask on Windows to stage one afterwards.
$Payload = Join-Path $SrcTauri 'payload'
foreach ($required in @('bin\opencode.exe', 'product')) {
  if (-not (Test-Path (Join-Path $Payload $required))) { throw "payload is missing $required" }
}
if ($Product -eq 'downes' -and -not (Test-Path (Join-Path $Payload 'studio\opencode.json'))) {
  throw 'payload is missing the curriculum template'
}

$Dist = Join-Path $Repo 'dist'
New-Item -ItemType Directory -Force -Path $Dist | Out-Null
$Out = Join-Path $Dist "$Product-$Version-windows-$Arch-setup.exe"
Copy-Item $Installer.FullName $Out -Force

$Sha = (Get-FileHash $Out -Algorithm SHA256).Hash.ToLower()
$Size = '{0:N0} MB' -f ($Installer.Length / 1MB)

Write-Host ''
Write-Host "  $Out"
Write-Host "  size   $Size"
Write-Host "  sha256 $Sha"
Write-Host ''
Write-Host '  Unsigned: SmartScreen warns on first run - More info, then Run anyway.'
