#!/usr/bin/env bash
# ==============================================================================
#  Wi-Fi Network Radar - Kali Linux Launcher
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=8888
URL="http://127.0.0.1:${PORT}"

# Terminal Colors
CYAN="\033[1;36m"
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
BOLD="\033[1m"
RESET="\033[0m"

echo -e "${CYAN}"
cat << "EOF"
  __        ___       _____ _   _   _     _ _ _ 
  \ \      / (_)_    |  ___(_) | \ | |___| (_) |__ 
   \ \ /\ / /| | |___| |_  | | |  \| / _ \ | | '_ \ 
    \ V  V / | | |___|  _| | | | |\  <  __/ | | |_) |
     \_/\_/  |_|_|   |_|   |_| |_| \_\___|_|_|_.__/ 

          WI-FI NETWORK RADAR - KALI EDITION
EOF
echo -e "${RESET}"

# 1. Root Privilege Escalation for ARP / Raw Socket Access
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}[!] Root privileges required for raw ARP & Wi-Fi scanning.${RESET}"
    echo -e "${CYAN}[*] Requesting sudo authorization...${RESET}"
    exec sudo bash "$0" "$@"
fi

echo -e "${GREEN}[+] Running with root privileges.${RESET}"

# 2. Dependency Checks
echo -e "${CYAN}[*] Verifying Kali system dependencies...${RESET}"

# Check Python 3
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}[!] python3 is not installed. Please run: apt install -y python3${RESET}"
    exit 1
fi

# Check arp-scan or nmap (recommended for full-speed discovery)
MISSING_PKGS=()
if ! command -v arp-scan &>/dev/null; then
    MISSING_PKGS+=("arp-scan")
fi
if ! command -v iw &>/dev/null && ! command -v iwconfig &>/dev/null; then
    MISSING_PKGS+=("wireless-tools")
fi

if [ ${#MISSING_PKGS[@]} -gt 0 ]; then
    echo -e "${YELLOW}[!] Optional scanner packages missing: ${MISSING_PKGS[*]}${RESET}"
    echo -e "${CYAN}[*] Installing missing scanner tools via apt...${RESET}"
    apt-get update -qq && apt-get install -y "${MISSING_PKGS[@]}" || {
        echo -e "${YELLOW}[!] Package installation skipped; fallback scanning will be used.${RESET}"
    }
fi

# 3. Detect Active Wi-Fi or Network Interface
echo -e "${CYAN}[*] Detecting active network interfaces...${RESET}"
WIFI_IFACE=""
# Look for wireless interfaces (wlan*, wlo*, ra*)
for iface in $(ip -o link show | awk -F': ' '{print $2}'); do
    if [[ "$iface" =~ ^wl ]]; then
        WIFI_IFACE="$iface"
        break
    fi
done

if [ -z "$WIFI_IFACE" ]; then
    # Fallback to default route interface
    WIFI_IFACE=$(ip route show default | awk '{print $5}' | head -n1)
fi

if [ -n "$WIFI_IFACE" ]; then
    echo -e "${GREEN}[+] Active Interface : ${BOLD}${WIFI_IFACE}${RESET}"
else
    WIFI_IFACE="wlan0"
    echo -e "${YELLOW}[!] No active network found, defaulting to: ${WIFI_IFACE}${RESET}"
fi

# 4. Check if Port 8888 is already in use
if lsof -Pi :${PORT} -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}[!] Port ${PORT} already active. Terminating previous instance...${RESET}"
    fuser -k ${PORT}/tcp >/dev/null 2>&1 || true
    sleep 1
fi

# 5. Start Python Radar Backend Server
cd "$SCRIPT_DIR"
if [ ! -f "web/index.html" ] && [ ! -f "index.html" ]; then
    echo -e "${YELLOW}[*] Web assets folder not found on disk.${RESET}"
    echo -e "${CYAN}[*] wifi_radar.py will auto-unpack embedded frontend assets...${RESET}"
fi
echo -e "${CYAN}[*] Launching Wi-Fi Network Radar Server on port ${PORT}...${RESET}"
python3 wifi_radar.py &
RADAR_PID=$!

# Trap Ctrl+C and exit cleanly
cleanup() {
    echo -e "\n${YELLOW}[*] Shutting down Wi-Fi Network Radar (PID ${RADAR_PID})...${RESET}"
    kill -TERM "$RADAR_PID" 2>/dev/null || true
    wait "$RADAR_PID" 2>/dev/null || true
    echo -e "${GREEN}[+] Radar stopped successfully. Goodbye!${RESET}"
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# Wait briefly for HTTP server to become responsive
for i in {1..10}; do
    if curl -s "${URL}/api/status" >/dev/null 2>&1; then
        break
    fi
    sleep 0.5
done

echo -e "${GREEN}[✓] Radar Server is live at: ${BOLD}${URL}${RESET}"

# 6. Launch Web Browser
# Determine non-root user if running under sudo so browser runs smoothly
TARGET_USER="${SUDO_USER:-$USER}"

echo -e "${CYAN}[*] Opening Radar Tactical Display in browser...${RESET}"
if command -v chromium &>/dev/null; then
    su - "$TARGET_USER" -c "chromium --app=${URL} --new-window >/dev/null 2>&1 &" 2>/dev/null || \
    chromium --app="${URL}" --no-sandbox >/dev/null 2>&1 &
elif command -v google-chrome &>/dev/null; then
    su - "$TARGET_USER" -c "google-chrome --app=${URL} --new-window >/dev/null 2>&1 &" 2>/dev/null || \
    google-chrome --app="${URL}" --no-sandbox >/dev/null 2>&1 &
elif command -v firefox &>/dev/null; then
    su - "$TARGET_USER" -c "firefox --new-window ${URL} >/dev/null 2>&1 &" 2>/dev/null || \
    firefox --new-window "${URL}" >/dev/null 2>&1 &
elif command -v xdg-open &>/dev/null; then
    su - "$TARGET_USER" -c "xdg-open ${URL} >/dev/null 2>&1 &" 2>/dev/null || \
    xdg-open "${URL}" >/dev/null 2>&1 &
else
    echo -e "${YELLOW}[!] Browser launcher not found. Open manually:${RESET} ${BOLD}${URL}${RESET}"
fi

echo -e "\n${GREEN}================================================================${RESET}"
echo -e "${GREEN}  WI-FI NETWORK RADAR RUNNING! Press ${BOLD}Ctrl+C${RESET}${GREEN} to terminate.${RESET}"
echo -e "${GREEN}  Access HUD at: ${BOLD}${URL}${RESET}"
echo -e "${GREEN}================================================================${RESET}\n"

# Keep script running to maintain server
wait "$RADAR_PID"
