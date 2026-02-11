#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONSOLE_DIR="${ROOT_DIR}/genesis-console"
DESKTOP_DIR="${HOME}/Desktop"
APP_NAME="Genesis Kiosk.app"
APP_DIR="${DESKTOP_DIR}/${APP_NAME}"
ICON_SOURCE_DEFAULT="/Volumes/jeremyserna/Desktop/Jeremy_Logos_Revision/truth_engine/truth_engine (1).png"
ICON_SOURCE="${1:-${ICON_SOURCE_DEFAULT}}"

if [[ ! -d "${CONSOLE_DIR}" ]]; then
  echo "Missing genesis-console directory: ${CONSOLE_DIR}" >&2
  exit 1
fi

if [[ ! -f "${ICON_SOURCE}" ]]; then
  echo "Logo file not found: ${ICON_SOURCE}" >&2
  echo "Pass a logo path as the first argument if you want a different source image." >&2
  exit 1
fi

for cmd in sips iconutil npm; do
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "Missing required command: ${cmd}" >&2
    exit 1
  fi
done

RASTER_SOURCE="${ICON_SOURCE}"
ICON_RASTER_TMP_DIR=""
ICON_SOURCE_LOWER="$(printf '%s' "${ICON_SOURCE}" | tr '[:upper:]' '[:lower:]')"
if [[ "${ICON_SOURCE_LOWER}" == *.ai ]]; then
  if ! command -v qlmanage >/dev/null 2>&1; then
    echo "Cannot use .ai logo without qlmanage available." >&2
    exit 1
  fi
  ICON_RASTER_TMP_DIR="$(mktemp -d)"
  if ! qlmanage -t -s 2048 -o "${ICON_RASTER_TMP_DIR}" "${ICON_SOURCE}" >/dev/null 2>&1; then
    echo "Failed to rasterize .ai logo via Quick Look: ${ICON_SOURCE}" >&2
    rm -rf "${ICON_RASTER_TMP_DIR}"
    exit 1
  fi
  GENERATED_PNG="${ICON_RASTER_TMP_DIR}/$(basename "${ICON_SOURCE}").png"
  if [[ ! -f "${GENERATED_PNG}" ]]; then
    echo "Expected rasterized PNG not found: ${GENERATED_PNG}" >&2
    rm -rf "${ICON_RASTER_TMP_DIR}"
    exit 1
  fi
  RASTER_SOURCE="${GENERATED_PNG}"
fi

rm -rf "${APP_DIR}"
mkdir -p "${APP_DIR}/Contents/MacOS" "${APP_DIR}/Contents/Resources"

LAUNCHER_PATH="${APP_DIR}/Contents/MacOS/genesis-kiosk-launcher"
cat >"${LAUNCHER_PATH}" <<EOF
#!/usr/bin/env bash

set -euo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:\${PATH:-}"

CONSOLE_DIR="${CONSOLE_DIR}"
API_PORT=3141
RUNTIME_DIR="\${HOME}/.genesis-kiosk"
LOG_DIR="\${RUNTIME_DIR}/logs"
API_LOG="\${LOG_DIR}/api.log"
BOOT_LOG="\${LOG_DIR}/bootstrap.log"
HEALTH_URL="http://127.0.0.1:\${API_PORT}/api/health"
APP_URL="http://127.0.0.1:\${API_PORT}/"
KIOSK_STATUS_URL="http://127.0.0.1:\${API_PORT}/api/kiosk/status"

mkdir -p "\${LOG_DIR}"

resolve_npm() {
  local candidates=(
    "\${NPM_BIN:-}"
    "\$(command -v npm 2>/dev/null || true)"
    "/opt/homebrew/bin/npm"
    "/usr/local/bin/npm"
    "/usr/bin/npm"
  )
  local candidate
  for candidate in "\${candidates[@]}"; do
    if [[ -n "\${candidate}" && -x "\${candidate}" ]]; then
      printf '%s' "\${candidate}"
      return 0
    fi
  done
  return 1
}

is_listening() {
  local port="\$1"
  lsof -iTCP:"\${port}" -sTCP:LISTEN -n -P >/dev/null 2>&1
}

wait_for_port() {
  local port="\$1"
  local attempts="\$2"
  local delay="\$3"
  for _ in \$(seq 1 "\${attempts}"); do
    if is_listening "\${port}"; then
      return 0
    fi
    sleep "\${delay}"
  done
  return 1
}

wait_for_http() {
  local url="\$1"
  local attempts="\$2"
  local delay="\$3"
  for _ in \$(seq 1 "\${attempts}"); do
    if curl -sf --max-time 2 "\${url}" >/dev/null 2>&1; then
      return 0
    fi
    sleep "\${delay}"
  done
  return 1
}

pid_for_port() {
  local port="\$1"
  lsof -tiTCP:"\${port}" -sTCP:LISTEN -n -P | head -n 1
}

stop_api() {
  if ! is_listening "\${API_PORT}"; then
    return 0
  fi
  local pid
  pid="\$(pid_for_port "\${API_PORT}")"
  if [[ -n "\${pid}" ]]; then
    kill "\${pid}" >/dev/null 2>&1 || true
    sleep 0.3
  fi
}

ensure_dependencies() {
  if [[ -d "\${CONSOLE_DIR}/node_modules" ]]; then
    return 0
  fi

  (
    cd "\${CONSOLE_DIR}"
    "\${NPM_BIN}" install >>"\${BOOT_LOG}" 2>&1
  )
}

ensure_ui_build() {
  if [[ -f "\${CONSOLE_DIR}/dist/index.html" ]]; then
    return 0
  fi

  (
    cd "\${CONSOLE_DIR}"
    "\${NPM_BIN}" run build >>"\${BOOT_LOG}" 2>&1
  )
}

rebuild_ui() {
  (
    cd "\${CONSOLE_DIR}"
    "\${NPM_BIN}" run build >>"\${BOOT_LOG}" 2>&1
  )
}

start_api() {
  if is_listening "\${API_PORT}"; then
    return 0
  fi

  (
    cd "\${CONSOLE_DIR}"
    nohup "\${NPM_BIN}" run server >>"\${API_LOG}" 2>&1 &
  )
}

detect_browser() {
  local candidates=(
    "Google Chrome"
    "Brave Browser"
    "Chromium"
    "Microsoft Edge"
  )
  local app
  for app in "\${candidates[@]}"; do
    if [[ -d "/Applications/\${app}.app" ]] || [[ -d "\${HOME}/Applications/\${app}.app" ]]; then
      printf '%s' "\${app}"
      return 0
    fi
  done
  return 1
}

maintenance_active() {
  local status_json
  if ! status_json="\$(curl -sf --max-time 2 "\${KIOSK_STATUS_URL}" 2>/dev/null)"; then
    return 1
  fi
  if printf '%s' "\${status_json}" | tr -d '[:space:]' | grep -q '"maintenance_mode":true'; then
    return 0
  fi
  return 1
}

{
  date '+%Y-%m-%d %H:%M:%S'
  echo "Genesis kiosk launch requested."
} >>"\${BOOT_LOG}"

for cmd in lsof curl npm; do
  if [[ "\${cmd}" == "npm" ]]; then
    continue
  fi
  if ! command -v "\${cmd}" >/dev/null 2>&1; then
    osascript -e "display dialog \"Missing command: \${cmd}\" buttons {\"OK\"} default button \"OK\" with icon caution"
    exit 1
  fi
done

NPM_BIN="\$(resolve_npm || true)"
if [[ -z "\${NPM_BIN}" ]]; then
  osascript -e 'display dialog "Could not find npm in launcher environment. Install Node.js and ensure npm is available in /opt/homebrew/bin or /usr/local/bin." buttons {"OK"} default button "OK" with icon caution'
  exit 1
fi

ensure_dependencies
ensure_ui_build
start_api

if ! wait_for_port "\${API_PORT}" 100 0.2; then
  osascript -e 'display dialog "Genesis API failed to start. Check ~/.genesis-kiosk/logs/api.log" buttons {"OK"} default button "OK" with icon caution'
  exit 1
fi

if ! wait_for_http "\${HEALTH_URL}" 50 0.2; then
  stop_api
  start_api
  if ! wait_for_http "\${HEALTH_URL}" 50 0.2; then
    osascript -e 'display dialog "Genesis API health check failed. Check ~/.genesis-kiosk/logs/api.log" buttons {"OK"} default button "OK" with icon caution'
    exit 1
  fi
fi

if ! wait_for_http "\${APP_URL}" 50 0.2; then
  rebuild_ui
  stop_api
  start_api
  if ! wait_for_http "\${APP_URL}" 80 0.2; then
    osascript -e 'display dialog "Genesis UI failed to load after auto-repair. Check ~/.genesis-kiosk/logs/bootstrap.log and api.log" buttons {"OK"} default button "OK" with icon caution'
    exit 1
  fi
fi

BROWSER_APP="\$(detect_browser || true)"
if [[ -z "\${BROWSER_APP}" ]]; then
  osascript -e 'display dialog "No supported kiosk browser found. Install Google Chrome, Brave, Chromium, or Edge." buttons {"OK"} default button "OK" with icon caution'
  exit 1
fi

if maintenance_active; then
  {
    date '+%Y-%m-%d %H:%M:%S'
    echo "Maintenance mode detected. Launching non-kiosk browser session."
  } >>"\${BOOT_LOG}"
  open -a "\${BROWSER_APP}" "\${APP_URL}"
else
  open -a "\${BROWSER_APP}" --args --kiosk --app="\${APP_URL}"
fi
EOF
chmod +x "${LAUNCHER_PATH}"

cat >"${APP_DIR}/Contents/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDevelopmentRegion</key>
  <string>en</string>
  <key>CFBundleExecutable</key>
  <string>genesis-kiosk-launcher</string>
  <key>CFBundleIconFile</key>
  <string>AppIcon</string>
  <key>CFBundleIdentifier</key>
  <string>ai.truthforge.genesis.kiosk</string>
  <key>CFBundleInfoDictionaryVersion</key>
  <string>6.0</string>
  <key>CFBundleName</key>
  <string>Genesis Kiosk</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleShortVersionString</key>
  <string>1.0</string>
  <key>CFBundleVersion</key>
  <string>1</string>
  <key>LSApplicationCategoryType</key>
  <string>public.app-category.productivity</string>
</dict>
</plist>
EOF

ICON_WORK_DIR="$(mktemp -d)"
ICONSET_DIR="${ICON_WORK_DIR}/AppIcon.iconset"
mkdir -p "${ICONSET_DIR}"

sips -s format png -z 16 16 "${RASTER_SOURCE}" --out "${ICONSET_DIR}/icon_16x16.png" >/dev/null
sips -s format png -z 32 32 "${RASTER_SOURCE}" --out "${ICONSET_DIR}/icon_16x16@2x.png" >/dev/null
sips -s format png -z 32 32 "${RASTER_SOURCE}" --out "${ICONSET_DIR}/icon_32x32.png" >/dev/null
sips -s format png -z 64 64 "${RASTER_SOURCE}" --out "${ICONSET_DIR}/icon_32x32@2x.png" >/dev/null
sips -s format png -z 128 128 "${RASTER_SOURCE}" --out "${ICONSET_DIR}/icon_128x128.png" >/dev/null
sips -s format png -z 256 256 "${RASTER_SOURCE}" --out "${ICONSET_DIR}/icon_128x128@2x.png" >/dev/null
sips -s format png -z 256 256 "${RASTER_SOURCE}" --out "${ICONSET_DIR}/icon_256x256.png" >/dev/null
sips -s format png -z 512 512 "${RASTER_SOURCE}" --out "${ICONSET_DIR}/icon_256x256@2x.png" >/dev/null
sips -s format png -z 512 512 "${RASTER_SOURCE}" --out "${ICONSET_DIR}/icon_512x512.png" >/dev/null
sips -s format png -z 1024 1024 "${RASTER_SOURCE}" --out "${ICONSET_DIR}/icon_512x512@2x.png" >/dev/null

iconutil -c icns "${ICONSET_DIR}" -o "${APP_DIR}/Contents/Resources/AppIcon.icns"
rm -rf "${ICON_WORK_DIR}"
if [[ -n "${ICON_RASTER_TMP_DIR}" ]]; then
  rm -rf "${ICON_RASTER_TMP_DIR}"
fi

touch "${APP_DIR}"
echo "Installed: ${APP_DIR}"
echo "Logo source: ${ICON_SOURCE}"
echo "Double-click the app icon on your Desktop to launch Genesis in kiosk mode."
