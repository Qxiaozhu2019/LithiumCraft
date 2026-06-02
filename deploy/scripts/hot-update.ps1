param(
  [string]$HostName = "139.224.223.234",
  [string]$UserName = "root",
  [string]$AppDir = "/opt/lithiumcraft",
  [string]$BaseUrl = "http://127.0.0.1",
  [switch]$SkipBackup
)

$ErrorActionPreference = "Stop"

function Quote-BashValue {
  param([string]$Value)
  return "'" + $Value.Replace("'", "'\''") + "'"
}

foreach ($tool in @("tar", "scp", "ssh")) {
  if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
    throw "Required command '$tool' was not found. Install OpenSSH/tar or run this script from a shell that provides them."
  }
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$packagePath = Join-Path $env:TEMP "lithiumcraft-deploy.tar.gz"
$remotePackage = "/tmp/lithiumcraft-deploy.tar.gz"
$remoteScript = "/tmp/lithiumcraft-hot-update.sh"
$localRemoteScript = Join-Path $env:TEMP "lithiumcraft-hot-update.sh"

if (Test-Path -LiteralPath $packagePath) {
  Remove-Item -LiteralPath $packagePath -Force
}

Write-Host "Packaging LithiumCraft from $repoRoot"
& tar `
  --exclude=".git" `
  --exclude="node_modules" `
  --exclude="frontend-app/node_modules" `
  --exclude="__pycache__" `
  --exclude=".pytest_cache" `
  --exclude=".ruff_cache" `
  --exclude=".env" `
  --exclude="backend-api/lithiumcraft-dev.db" `
  --exclude="deploy/backups" `
  -czf $packagePath `
  -C $repoRoot `
  .

if ($LASTEXITCODE -ne 0) {
  throw "tar failed with exit code $LASTEXITCODE"
}

$quotedAppDir = Quote-BashValue $AppDir
$quotedBaseUrl = Quote-BashValue $BaseUrl
$quotedRemotePackage = Quote-BashValue $remotePackage
$quotedSkipBackup = Quote-BashValue ($SkipBackup.IsPresent.ToString())

$remoteLines = @(
  "#!/usr/bin/env bash",
  "set -euo pipefail",
  "APP_DIR=$quotedAppDir",
  "BASE_URL=$quotedBaseUrl",
  "PACKAGE=$quotedRemotePackage",
  "SKIP_BACKUP=$quotedSkipBackup",
  "if [ -z `"`$APP_DIR`" ] || [ `"`$APP_DIR`" = '/' ] || [ `"`$APP_DIR`" = '/opt' ]; then",
  "  echo `"Unsafe APP_DIR: `$APP_DIR`" >&2",
  "  exit 1",
  "fi",
  "case `"`$APP_DIR`" in /*) ;; *) echo `"APP_DIR must be absolute: `$APP_DIR`" >&2; exit 1 ;; esac",
  "if [ ! -d `"`$APP_DIR`" ]; then",
  "  echo `"Missing `$APP_DIR. Run first deployment and create .env before hot update.`" >&2",
  "  exit 1",
  "fi",
  "cd `"`$APP_DIR`"",
  "if [ ! -f .env ]; then",
  "  echo `"Missing `$APP_DIR/.env. Create it from deploy/env.production.example before hot update.`" >&2",
  "  exit 1",
  "fi",
  "if [ ! -f `"`$PACKAGE`" ]; then",
  "  echo `"Missing uploaded package: `$PACKAGE`" >&2",
  "  exit 1",
  "fi",
  "before_env_sum=`$(sha256sum .env | awk '{print `$1}')",
  "env_copy=`$(mktemp /tmp/lithiumcraft-env.XXXXXX)",
  "staging_dir=`$(mktemp -d /tmp/lithiumcraft-release.XXXXXX)",
  "cleanup() { rm -rf `"`$staging_dir`"; rm -f `"`$env_copy`"; }",
  "trap cleanup EXIT",
  "cp .env `"`$env_copy`"",
  "if [ `"`$SKIP_BACKUP`" != 'True' ] && [ -f deploy/scripts/backup-postgres.sh ]; then",
  "  find deploy/scripts -maxdepth 1 -type f -name '*.sh' -exec sed -i 's/\r$//' {} +",
  "  find deploy/scripts -maxdepth 1 -type f -name '*.sh' -exec chmod +x {} +",
  "  if docker compose -f deploy/docker-compose.yml --env-file .env ps --services --status running 2>/dev/null | grep -qx postgres; then",
  "    echo 'Creating PostgreSQL backup before hot update...'",
  "    bash deploy/scripts/backup-postgres.sh",
  "  else",
  "    echo 'PostgreSQL container is not running; skipping pre-update backup.'",
  "  fi",
  "else",
  "  echo 'Skipping pre-update PostgreSQL backup.'",
  "fi",
  "echo `"Extracting package to `$staging_dir...`"",
  "tar -xzf `"`$PACKAGE`" -C `"`$staging_dir`"",
  "if [ -f `"`$staging_dir/.env`" ]; then",
  "  echo 'Package unexpectedly contains .env; aborting.' >&2",
  "  exit 1",
  "fi",
  "if [ ! -f `"`$staging_dir/deploy/scripts/deploy.sh`" ]; then",
  "  echo 'Package does not look like a LithiumCraft project root; aborting.' >&2",
  "  exit 1",
  "fi",
  "find `"`$staging_dir/deploy/scripts`" -maxdepth 1 -type f -name '*.sh' -exec sed -i 's/\r$//' {} +",
  "find `"`$staging_dir/deploy/scripts`" -maxdepth 1 -type f -name '*.sh' -exec chmod +x {} +",
  "if [ -d deploy/backups ]; then",
  "  mkdir -p `"`$staging_dir/deploy`"",
  "  cp -a deploy/backups `"`$staging_dir/deploy/backups`"",
  "fi",
  "echo `"Replacing application files in `$APP_DIR while preserving .env and Docker volumes...`"",
  "find `"`$APP_DIR`" -mindepth 1 -maxdepth 1 ! -name '.env' -exec rm -rf -- {} +",
  "cp -a `"`$staging_dir/.`" `"`$APP_DIR/`"",
  "cp `"`$env_copy`" `"`$APP_DIR/.env`"",
  "cd `"`$APP_DIR`"",
  "after_env_sum=`$(sha256sum .env | awk '{print `$1}')",
  "if [ `"`$before_env_sum`" != `"`$after_env_sum`" ]; then",
  "  echo '.env changed unexpectedly; aborting.' >&2",
  "  exit 1",
  "fi",
  "COMPOSE_PROGRESS=plain bash deploy/scripts/deploy.sh",
  "BASE_URL=`"`$BASE_URL`" bash deploy/scripts/verify.sh"
)
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($localRemoteScript, ($remoteLines -join "`n") + "`n", $utf8NoBom)

$target = "${UserName}@${HostName}"

Write-Host "Uploading package to ${target}:${remotePackage}"
& scp $packagePath "${target}:$remotePackage"
if ($LASTEXITCODE -ne 0) {
  throw "scp package failed with exit code $LASTEXITCODE"
}

Write-Host "Uploading remote hot-update script to ${target}:${remoteScript}"
& scp $localRemoteScript "${target}:$remoteScript"
if ($LASTEXITCODE -ne 0) {
  throw "scp remote script failed with exit code $LASTEXITCODE"
}

Write-Host "Running remote hot update"
& ssh $target "bash $remoteScript"
if ($LASTEXITCODE -ne 0) {
  throw "remote hot update failed with exit code $LASTEXITCODE"
}

Write-Host "Hot update completed."

