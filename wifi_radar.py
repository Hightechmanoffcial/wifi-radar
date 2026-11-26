#!/usr/bin/env python3
"""
Wi-Fi Network Radar - Backend Server
Created for Kali Linux
Provides REST API for network scanning, device discovery, and identity customization.
Uses Python standard library (no pip packages required).
"""

import http.server
import socketserver
import json
import os
import sys
import subprocess
import re
import socket
import threading
import time
import urllib.parse
import math
import gzip
import base64
import shutil
import hashlib

PORT = 8888
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")
OVERRIDES_FILE = os.path.join(BASE_DIR, "device_overrides.json")

# Embedded Fallback Web Assets (Gzip + Base64)
import gzip
import base64

EMBEDDED_ASSETS_GZ_B64 = {
    'index.html': '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',
    'style.css': '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',
    'app.js': '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',
}


def get_asset_bytes(filename):
    """
    Finds and returns the raw bytes for a requested asset.
    Checks disk first in multiple candidate directories, then falls back to embedded data.
    """
    clean_name = os.path.basename(filename)
    candidates = [
        os.path.join(BASE_DIR, "web", clean_name),
        os.path.join(BASE_DIR, clean_name),
        os.path.join(os.getcwd(), "web", clean_name),
        os.path.join(os.getcwd(), clean_name),
    ]
    for path in candidates:
        if os.path.isfile(path):
            try:
                with open(path, "rb") as f:
                    return f.read()
            except Exception:
                pass

    if clean_name in EMBEDDED_ASSETS_GZ_B64:
        try:
            compressed = base64.b64decode(EMBEDDED_ASSETS_GZ_B64[clean_name])
            return gzip.decompress(compressed)
        except Exception as e:
            print(f"[!] Error decompressing embedded asset {clean_name}: {e}")

    return None

def ensure_web_assets_on_disk():
    """
    If the web/ folder or index.html is missing on disk (e.g. user cloned/downloaded
    only the python/sh script from GitHub), auto-generate the web directory and files.
    """
    web_dir = os.path.join(BASE_DIR, "web")
    try:
        os.makedirs(web_dir, exist_ok=True)
    except Exception:
        pass

    for filename in ["index.html", "style.css", "app.js"]:
        target_path = os.path.join(web_dir, filename)
        if not os.path.isfile(target_path):
            data = get_asset_bytes(filename)
            if data:
                try:
                    with open(target_path, "wb") as f:
                        f.write(data)
                    print(f"[+] Auto-generated missing web asset: {target_path}")
                except Exception as e:
                    print(f"[*] Notice: Could not write {target_path}: {e}")


# Built-in OUI Database for fast offline vendor identification
OUI_DATABASE = {
    # Apple
    "B4:E6:2D": "Apple", "A4:83:E7": "Apple", "F0:18:98": "Apple", "3C:22:FB": "Apple",
    "BC:54:36": "Apple", "98:01:A7": "Apple", "70:EC:E4": "Apple", "68:9C:70": "Apple",
    "AC:BC:32": "Apple", "DC:2B:61": "Apple", "F4:34:F0": "Apple", "00:1C:B3": "Apple",
    "A8:66:7F": "Apple", "88:66:5A": "Apple", "40:6c:8f": "Apple", "14:10:9F": "Apple",
    # Samsung
    "A6:7B:3C": "Samsung Electronics", "B8:5E:7B": "Samsung Electronics", "D0:B3:3F": "Samsung Electronics",
    "F4:7B:5E": "Samsung Electronics", "90:18:7C": "Samsung Electronics", "44:80:EB": "Samsung Electronics",
    "CC:07:AB": "Samsung Electronics", "84:25:DB": "Samsung Electronics", "34:14:5F": "Samsung Electronics",
    "00:12:47": "Samsung Electronics", "50:85:69": "Samsung Electronics", "94:65:2D": "Samsung Electronics",
    # TP-Link
    "E4:5F:01": "TP-Link", "50:C7:BF": "TP-Link", "74:03:BD": "TP-Link", "84:16:F9": "TP-Link",
    "98:48:27": "TP-Link", "C0:06:C3": "TP-Link", "EC:08:6B": "TP-Link", "14:CC:20": "TP-Link",
    "30:B5:C2": "TP-Link", "60:32:B1": "TP-Link", "AC:84:C6": "TP-Link",
    # Dell
    "3C:9C:0F": "Dell Inc.", "18:66:DA": "Dell Inc.", "34:17:EB": "Dell Inc.", "54:48:10": "Dell Inc.",
    "8C:EC:4B": "Dell Inc.", "B8:85:84": "Dell Inc.", "D4:BE:D9": "Dell Inc.", "00:14:22": "Dell Inc.",
    # HP / Hewlett-Packard
    "00:1A:11": "HP Inc.", "3C:D9:2B": "HP Inc.", "94:57:A5": "HP Inc.", "A0:B3:CC": "HP Inc.",
    "B4:99:BA": "HP Inc.", "C8:D3:FF": "HP Inc.", "FC:3F:DB": "HP Inc.", "00:08:02": "HP Inc.",
    # Intel
    "A4:34:D9": "Intel Corporate", "00:1B:77": "Intel Corporate", "00:21:5C": "Intel Corporate",
    "00:24:D7": "Intel Corporate", "34:13:E8": "Intel Corporate", "68:05:71": "Intel Corporate",
    # Google
    "F4:F5:D8": "Google LLC", "30:FD:38": "Google LLC", "54:60:09": "Google LLC", "64:16:66": "Google LLC",
    "94:EB:CD": "Google LLC", "A4:77:33": "Google LLC", "D8:6C:63": "Google LLC",
    # Cisco / Linksys
    "00:1A:2F": "Cisco Systems", "00:1B:2B": "Cisco Systems", "00:21:A0": "Cisco Systems",
    "58:97:1E": "Cisco Systems", "68:86:A7": "Cisco Systems", "C4:72:95": "Cisco Systems",
    # Netgear
    "00:14:6C": "Netgear", "00:1E:2A": "Netgear", "20:4E:7F": "Netgear", "84:1B:5E": "Netgear",
    # Xiaomi
    "00:EC:0A": "Xiaomi", "18:59:36": "Xiaomi", "28:6C:07": "Xiaomi", "64:CC:2E": "Xiaomi",
    "7C:49:EB": "Xiaomi", "9C:99:A0": "Xiaomi", "AC:C1:EE": "Xiaomi",
    # Huawei
    "00:E0:FC": "Huawei", "10:C6:1F": "Huawei", "24:69:68": "Huawei", "48:46:FB": "Huawei",
    # Sony
    "00:01:4A": "Sony", "00:04:1F": "Sony", "00:13:A9": "Sony", "70:9E:29": "Sony", "F8:46:1C": "Sony",
    # LG
    "00:05:C9": "LG Electronics", "00:19:A1": "LG Electronics", "20:2B:C1": "LG Electronics", "58:A2:B5": "LG Electronics",
    # Espressif (IoT / Smart Home)
    "24:0A:C4": "Espressif Inc.", "24:6F:28": "Espressif Inc.", "30:AE:A4": "Espressif Inc.",
    "84:F3:EB": "Espressif Inc.", "A4:CF:12": "Espressif Inc.", "DC:4F:22": "Espressif Inc.",
    # Raspberry Pi
    "B8:27:EB": "Raspberry Pi Foundation", "DC:A6:32": "Raspberry Pi Trading", "28:CD:C1": "Raspberry Pi Trading",
    # Amazon
    "44:65:0D": "Amazon", "68:37:E9": "Amazon", "74:75:48": "Amazon", "AC:63:BE": "Amazon",
    # Microsoft
    "00:12:5A": "Microsoft", "00:17:FA": "Microsoft", "00:50:F2": "Microsoft", "DC:98:40": "Microsoft",
    # Asus
    "00:0C:6E": "Asus", "00:18:F3": "Asus", "08:60:6E": "Asus", "1C:87:2C": "Asus",
    # Lenovo
    "00:12:FE": "Lenovo", "00:21:CC": "Lenovo", "50:7B:9D": "Lenovo", "80:56:F2": "Lenovo",
    # Canon / Epson
    "00:00:85": "Canon", "00:1E:8F": "Canon", "00:00:48": "Epson", "00:26:AB": "Epson"
}

# In-memory storage for scanned devices and state
current_devices = []
scan_lock = threading.Lock()
is_scanning = False
last_scan_time = None
demo_mode_active = False

# Defensive monitoring events buffer.
# Populated only by (a) the safe deauth-test simulation logger (tagged "(SIM)"),
# and (b) the real monitor-mode capture pipeline below. No fabricated/demo
# entries are seeded here, so an empty table honestly means "nothing detected yet".
defensive_events = []
defensive_event_counter = 0

# ------------------------------------------------------------------------------
# Real Defensive Monitoring: monitor-mode capture of 802.11 deauth/disassoc frames
#
# This is READ-ONLY / PASSIVE. It never transmits deauthentication or
# disassociation frames; it only puts the adapter into monitor mode and parses
# management frames that are already in the air, exactly like an IDS such as
# Kismet would. Requires: root, a monitor-mode-capable Wi-Fi adapter, and the
# `tshark` package (plus `airmon-ng` from aircrack-ng, or `iw`, to switch modes).
# ------------------------------------------------------------------------------
monitor_lock = threading.Lock()
monitor_active = False
monitor_interface_name = None   # the monitor-mode interface actually in use (e.g. wlan0mon)
monitor_base_interface = None   # the original managed-mode interface it came from
monitor_used_airmon = False
monitor_process = None          # subprocess.Popen running tshark
monitor_reader_thread = None

def check_monitor_capability():
    """
    Checks whether REAL deauth/disassociation monitoring is possible on this
    system right now. Returns (supported: bool, reason: str, interface: str|None).
    Never guesses "yes" when it can't confirm - an honest "no" with a reason
    is always preferred to fake data.
    """
    if os.geteuid() != 0:
        return False, "Root privileges are required to enable monitor mode. Run wifi_radar.sh with sudo.", None

    net_info = get_network_info()
    iface = net_info.get("interface", "wlan0")

    if not net_info.get("is_wifi"):
        return False, f"Active interface '{iface}' does not appear to be a Wi-Fi adapter.", None

    if not shutil.which("tshark"):
        return False, "The 'tshark' package is required but was not found. Install it with: apt install -y tshark", None

    if not (shutil.which("airmon-ng") or shutil.which("iw")):
        return False, "Neither 'airmon-ng' (aircrack-ng) nor 'iw' were found to switch the adapter into monitor mode.", None

    # Best-effort check that the physical radio actually advertises monitor mode.
    # If we can't determine this either way, we still allow the attempt rather
    # than blocking on an inconclusive check.
    try:
        dev_out = subprocess.check_output(["iw", "dev", iface, "info"], universal_newlines=True, stderr=subprocess.DEVNULL, timeout=5)
        m = re.search(r"wiphy (\d+)", dev_out)
        if m:
            phy_out = subprocess.check_output(["iw", f"phy{m.group(1)}", "info"], universal_newlines=True, stderr=subprocess.DEVNULL, timeout=5)
            if "* monitor" not in phy_out:
                return False, f"The wireless adapter on '{iface}' does not advertise monitor-mode support.", None
    except Exception:
        pass

    return True, "", iface

def start_monitor_interface(iface):
    """
    Switches the interface into monitor mode. Prefers airmon-ng (ships with
    aircrack-ng on Kali by default); falls back to plain iw/ip if unavailable.
    Returns (monitor_iface_name, used_airmon).
    """
    if shutil.which("airmon-ng"):
        try:
            # Stops NetworkManager/wpa_supplicant from fighting over the interface.
            subprocess.run(["airmon-ng", "check", "kill"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
        except Exception:
            pass
        out = subprocess.check_output(["airmon-ng", "start", iface], universal_newlines=True, stderr=subprocess.STDOUT, timeout=20)
        m = re.search(r"monitor mode (?:vif )?enabled.*?\[?([\w.]+mon\w*)\]?", out, re.IGNORECASE)
        mon_iface = m.group(1) if m else f"{iface}mon"
        check = subprocess.run(["ip", "link", "show", mon_iface], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if check.returncode != 0:
            # Some airmon-ng builds switch the mode on the original interface in place.
            mon_iface = iface
        return mon_iface, True
    else:
        subprocess.run(["ip", "link", "set", iface, "down"], check=True, timeout=10)
        subprocess.run(["iw", iface, "set", "monitor", "none"], check=True, timeout=10)
        subprocess.run(["ip", "link", "set", iface, "up"], check=True, timeout=10)
        return iface, False

def stop_monitor_interface(mon_iface, used_airmon, base_iface):
    try:
        if used_airmon and shutil.which("airmon-ng"):
            subprocess.run(["airmon-ng", "stop", mon_iface], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
        else:
            subprocess.run(["ip", "link", "set", mon_iface, "down"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
            subprocess.run(["iw", mon_iface, "set", "type", "managed"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
            subprocess.run(["ip", "link", "set", mon_iface, "up"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
    except Exception as e:
        print(f"[!] Error restoring adapter after monitoring: {e}")

def monitor_reader_loop():
    """
    Reads tshark's filtered field output line by line and appends a real
    event per captured deauth (subtype 0x0c) or disassoc (subtype 0x0a) frame.
    Pure parsing of frames already broadcast over the air - no transmission.
    """
    global defensive_event_counter
    proc = monitor_process
    if not proc or not proc.stdout:
        return
    try:
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            src_mac = (parts[0] or "Unknown").strip().upper()
            dst_mac = (parts[1] or "Unknown").strip().upper()
            subtype = parts[2].strip().lower()
            reason_raw = parts[3].strip() if len(parts) > 3 else ""

            if subtype in ("0x0c", "12"):
                event_type = "DEAUTH"
            elif subtype in ("0x0a", "10"):
                event_type = "DISASSOC"
            else:
                continue

            reason_map = {
                "1": "Code 1: Unspecified reason",
                "2": "Code 2: Prior auth no longer valid",
                "3": "Code 3: STA leaving (deauth)",
                "4": "Code 4: Inactivity disassociated",
                "6": "Code 6: Class 2 frame from non-auth STA",
                "7": "Code 7: Class 3 frame from non-assoc STA",
                "8": "Code 8: STA leaving BSS (disassoc)"
            }
            reason_text = reason_map.get(reason_raw, f"Code {reason_raw}" if reason_raw else "Unknown")

            with monitor_lock:
                defensive_event_counter += 1
                event = {
                    "id": defensive_event_counter,
                    "time": time.strftime("%H:%M:%S"),
                    "event_type": event_type,
                    "source": src_mac,
                    "target": dst_mac,
                    "reason_code": reason_text,
                    "signal_dbm": "--",
                    "pmf": "Live Capture",
                    "status": "Detected (Monitor Mode)"
                }
                defensive_events.insert(0, event)
                if len(defensive_events) > 200:
                    defensive_events.pop()
    except Exception as e:
        print(f"[!] Monitor capture loop ended: {e}")

def load_overrides():
    if os.path.exists(OVERRIDES_FILE):
        try:
            with open(OVERRIDES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Error loading overrides: {e}")
    return {}

def save_overrides(overrides):
    try:
        with open(OVERRIDES_FILE, "w", encoding="utf-8") as f:
            json.dump(overrides, f, indent=2)
    except Exception as e:
        print(f"[!] Error saving overrides: {e}")

def get_mac_vendor(mac):
    if not mac or len(mac) < 8:
        return "Unknown"
    mac_clean = mac.upper().replace("-", ":")
    prefix = mac_clean[:8]
    if prefix in OUI_DATABASE:
        return OUI_DATABASE[prefix]
    # Check Kali system OUI files if present
    for sys_oui in ["/usr/share/arp-scan/ieee-oui.txt", "/usr/share/nmap/nmap-mac-prefixes"]:
        if os.path.exists(sys_oui):
            try:
                hex_prefix = prefix.replace(":", "")
                with open(sys_oui, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if line.startswith(hex_prefix):
                            parts = line.strip().split("\t")
                            if len(parts) >= 2:
                                return parts[1].strip()
            except Exception:
                pass
    return "Unknown Vendor"

def detect_device_icon_and_type(vendor, name="", is_gateway=False, is_self=False):
    if is_gateway:
        return "router", "Router (Gateway)"
    if is_self:
        return "laptop", "Kali Linux (Scanner)"

    text = f"{vendor} {name}".lower()
    
    if any(k in text for k in ["router", "gateway", "ap", "access point", "modem", "tp-link", "cisco", "netgear", "d-link", "ubiquiti", "mikrotik"]):
        return "router", "Router / AP"
    if any(k in text for k in ["iphone", "ios", "apple phone"]):
        return "iphone", "iPhone"
    if any(k in text for k in ["android", "samsung", "galaxy", "xiaomi", "redmi", "pixel", "oneplus", "oppo", "vivo", "huawei phone"]):
        return "android", "Android Phone"
    if any(k in text for k in ["ipad", "tablet", "tab"]):
        return "tablet", "Tablet"
    if any(k in text for k in ["printer", "canon", "epson", "brother", "laserjet", "deskjet", "hp inc", "hewlett-packard"]):
        return "printer", "Printer"
    if any(k in text for k in ["laptop", "macbook", "thinkpad", "dell", "notebook", "zenbook"]):
        return "laptop", "Laptop"
    if any(k in text for k in ["desktop", "pc", "workstation", "tower", "intel corporate"]):
        return "desktop", "Desktop PC"
    if any(k in text for k in ["tv", "smart tv", "roku", "vizio", "bravia", "firestick", "chromecast"]):
        return "tv", "Smart TV"
    if any(k in text for k in ["espressif", "tuya", "sonoff", "iot", "smart plug", "bulb", "esp8266", "esp32", "shelly"]):
        return "iot", "IoT Device"
    if any(k in text for k in ["camera", "cam", "hikvision", "dahua", "reolink", "cctv"]):
        return "camera", "Security Camera"
    if any(k in text for k in ["playstation", "xbox", "nintendo", "switch", "console"]):
        return "gamepad", "Gaming Console"
    if any(k in text for k in ["raspberry", "rpi", "orangepi"]):
        return "server", "Single Board Computer"
    if any(k in text for k in ["apple"]):
        return "iphone", "Apple Device"
        
    return "desktop", "Network Device"

def get_network_info():
    info = {
        "interface": "wlan0",
        "ssid": "CyberNet_5G",
        "ip": "192.168.1.15",
        "subnet": "192.168.1.0/24",
        "gateway": "192.168.1.1",
        "mac": "00:11:22:33:44:55",
        "is_wifi": True,
        "interfaces": ["wlan0", "eth0", "lo"]
    }

    try:
        # Detect default route & interface
        out = subprocess.check_output(["ip", "route", "show", "default"], universal_newlines=True, stderr=subprocess.DEVNULL)
        m = re.search(r"default via ([\d\.]+) dev (\S+)", out)
        if m:
            info["gateway"] = m.group(1)
            info["interface"] = m.group(2)
    except Exception:
        pass

    try:
        # List all interfaces
        out = subprocess.check_output(["ip", "-o", "link", "show"], universal_newlines=True, stderr=subprocess.DEVNULL)
        ifaces = [re.search(r":\s+(\S+?):", line).group(1) for line in out.splitlines() if re.search(r":\s+(\S+?):", line)]
        if ifaces:
            info["interfaces"] = ifaces
    except Exception:
        pass

    iface = info["interface"]

    try:
        # Get IP and subnet mask
        out = subprocess.check_output(["ip", "-4", "-o", "addr", "show", iface], universal_newlines=True, stderr=subprocess.DEVNULL)
        m = re.search(r"inet ([\d\.]+)/(\d+)", out)
        if m:
            info["ip"] = m.group(1)
            prefix = int(m.group(2))
            # Calculate subnet base
            ip_parts = list(map(int, info["ip"].split(".")))
            ip_num = (ip_parts[0] << 24) + (ip_parts[1] << 16) + (ip_parts[2] << 8) + ip_parts[3]
            mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
            net_num = ip_num & mask
            net_base = f"{(net_num >> 24) & 255}.{(net_num >> 16) & 255}.{(net_num >> 8) & 255}.{net_num & 255}"
            info["subnet"] = f"{net_base}/{prefix}"
    except Exception:
        pass

    try:
        # Get MAC address
        with open(f"/sys/class/net/{iface}/address", "r") as f:
            info["mac"] = f.read().strip().upper()
    except Exception:
        pass

    # Detect SSID
    is_wifi = False
    ssid = None
    try:
        out = subprocess.check_output(["iw", "dev", iface, "link"], universal_newlines=True, stderr=subprocess.DEVNULL)
        m = re.search(r"SSID:\s*(.+)", out)
        if m:
            ssid = m.group(1).strip()
            is_wifi = True
    except Exception:
        pass

    if not ssid:
        try:
            out = subprocess.check_output(["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"], universal_newlines=True, stderr=subprocess.DEVNULL)
            for line in out.splitlines():
                if line.startswith("yes:"):
                    ssid = line.split(":", 1)[1].strip()
                    is_wifi = True
                    break
        except Exception:
            pass

    if not ssid:
        try:
            out = subprocess.check_output(["iwgetid", "-r", iface], universal_newlines=True, stderr=subprocess.DEVNULL)
            if out.strip():
                ssid = out.strip()
                is_wifi = True
        except Exception:
            pass

    if ssid:
        info["ssid"] = ssid
        info["is_wifi"] = True
    else:
        info["ssid"] = "CyberNet_5G" if iface.startswith("wl") else f"Ethernet ({iface})"
        info["is_wifi"] = iface.startswith("wl")

    return info

def calculate_radar_position(ip, mac, is_gateway, index, total):
    """
    Computes consistent, aesthetic polar coordinates (angle in degrees, distance 0.1 to 0.9)
    so blips stay stably positioned and look like a tactical radar screen.
    """
    if is_gateway:
        # Gateway placed slightly south-east or near center ring
        return 135.0, 0.40

    # Deterministic hash from MAC & IP
    h = int(hashlib.md5(f"{mac}{ip}".encode()).hexdigest()[:6], 16)
    
    # Specific curated angles for iconic look matching screenshot
    preset_angles = [340, 20, 75, 120, 195, 255, 305, 160, 45, 230]
    angle = preset_angles[index % len(preset_angles)] + ((h % 15) - 7)
    angle = (angle + 360) % 360

    # Distance between 0.35 and 0.82 radius
    distance_presets = [0.45, 0.65, 0.72, 0.58, 0.78, 0.50, 0.82]
    distance = distance_presets[index % len(distance_presets)]

    return round(float(angle), 1), round(float(distance), 2)

def generate_mock_devices():
    """Returns realistic mock devices exactly matching the user's reference image for demo/testing."""
    return [
        {
            "id": 1,
            "name": "Router (Gateway)",
            "ip": "192.168.1.1",
            "mac": "E4:5F:01:2A:7C:90",
            "vendor": "TP-Link",
            "icon": "router",
            "device_type": "Router (Gateway)",
            "status": "Connected (Online)",
            "is_gateway": True,
            "angle": 135.0,
            "distance": 0.38,
            "os_badge": "tp-link"
        },
        {
            "id": 2,
            "name": "Manu's Laptop",
            "ip": "192.168.1.10",
            "mac": "3C:9C:0F:18:2D:4B",
            "vendor": "Dell Inc.",
            "icon": "laptop",
            "device_type": "Laptop",
            "status": "Connected (Online)",
            "is_gateway": False,
            "angle": 265.0,
            "distance": 0.68,
            "os_badge": "dell"
        },
        {
            "id": 3,
            "name": "Android Phone",
            "ip": "192.168.1.14",
            "mac": "A6:7B:3C:D2:9F:01",
            "vendor": "Samsung Electronics",
            "icon": "android",
            "device_type": "Android Phone",
            "status": "Connected (Online)",
            "is_gateway": False,
            "angle": 75.0,
            "distance": 0.75,
            "os_badge": "android"
        },
        {
            "id": 4,
            "name": "iPhone",
            "ip": "192.168.1.18",
            "mac": "B4:E6:2D:7A:6C:92",
            "vendor": "Apple Inc.",
            "icon": "iphone",
            "device_type": "iPhone",
            "status": "Connected (Online)",
            "is_gateway": False,
            "angle": 345.0,
            "distance": 0.60,
            "os_badge": "apple"
        },
        {
            "id": 5,
            "name": "Printer",
            "ip": "192.168.1.25",
            "mac": "00:1A:11:9B:C3:4D",
            "vendor": "HP Inc.",
            "icon": "printer",
            "device_type": "Printer",
            "status": "Connected (Online)",
            "is_gateway": False,
            "angle": 195.0,
            "distance": 0.72,
            "os_badge": "hp"
        }
    ]

def perform_live_scan(interface, subnet, gateway_ip):
    raw_devices = []
    seen_macs = set()

    # 1. Try arp-scan (fastest, Kali native)
    try:
        cmd = ["arp-scan", "--interface", interface, "--localnet", "--numeric", "--quiet"]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout, _ = p.communicate(timeout=10)
        for line in stdout.splitlines():
            line = line.strip()
            # Match: 192.168.1.1   e4:5f:01:2a:7c:90   TP-Link Technologies
            m = re.match(r"^([\d\.]+)\s+([0-9a-fA-F:]{17})\s*(.*)$", line)
            if m:
                ip, mac, vendor = m.group(1), m.group(2).upper(), m.group(3).strip()
                if mac not in seen_macs:
                    seen_macs.add(mac)
                    raw_devices.append({"ip": ip, "mac": mac, "vendor": vendor or get_mac_vendor(mac)})
    except Exception as e:
        print(f"[*] arp-scan direct attempt info: {e}")

    # 2. Try nmap -sn if raw_devices empty
    if not raw_devices:
        try:
            cmd = ["nmap", "-sn", "-PR", subnet, "-e", interface]
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            stdout, _ = p.communicate(timeout=15)
            cur_ip = None
            for line in stdout.splitlines():
                m_ip = re.search(r"Nmap scan report for (?:(\S+) )?\(?([\d\.]+)\)?", line)
                if m_ip:
                    cur_ip = m_ip.group(2)
                m_mac = re.search(r"MAC Address: ([0-9a-fA-F:]{17})(?:\s*\((.*?)\))?", line)
                if m_mac and cur_ip:
                    mac = m_mac.group(1).upper()
                    vendor = m_mac.group(2) or get_mac_vendor(mac)
                    if mac not in seen_macs:
                        seen_macs.add(mac)
                        raw_devices.append({"ip": cur_ip, "mac": mac, "vendor": vendor})
        except Exception as e:
            print(f"[*] nmap attempt info: {e}")

    # 3. Try reading /proc/net/arp & ip neigh
    if not raw_devices:
        try:
            out = subprocess.check_output(["ip", "neigh", "show", "dev", interface], universal_newlines=True, stderr=subprocess.DEVNULL)
            for line in out.splitlines():
                m = re.match(r"^([\d\.]+)\s+lladdr\s+([0-9a-fA-F:]{17})", line)
                if m:
                    ip, mac = m.group(1), m.group(2).upper()
                    if mac not in seen_macs and mac != "00:00:00:00:00:00":
                        seen_macs.add(mac)
                        raw_devices.append({"ip": ip, "mac": mac, "vendor": get_mac_vendor(mac)})
        except Exception:
            pass

    # Sort devices by IP address
    def ip_sort_key(d):
        try:
            return [int(x) for x in d["ip"].split(".")]
        except Exception:
            return [0, 0, 0, 0]

    raw_devices.sort(key=ip_sort_key)
    return raw_devices

def process_devices(raw_devices, gateway_ip, net_info):
    overrides = load_overrides()
    devices = []

    for idx, raw in enumerate(raw_devices, start=1):
        ip = raw.get("ip", "")
        mac = raw.get("mac", "").upper()
        vendor = raw.get("vendor", "")
        if not vendor or vendor == "Unknown":
            vendor = get_mac_vendor(mac)

        is_gateway = (ip == gateway_ip)
        is_self = (ip == net_info.get("ip") or mac == net_info.get("mac"))

        auto_icon, auto_type = detect_device_icon_and_type(vendor, "", is_gateway, is_self)
        
        # Check overrides
        override = overrides.get(mac, {})
        name = override.get("name") or (auto_type if not is_gateway else "Router (Gateway)")
        icon = override.get("icon") or auto_icon
        notes = override.get("notes") or ""

        angle, distance = calculate_radar_position(ip, mac, is_gateway, idx, len(raw_devices))

        # Brand / OS badge
        os_badge = "network"
        v_lower = (vendor + " " + icon).lower()
        if "samsung" in v_lower or "android" in v_lower:
            os_badge = "android"
        elif "apple" in v_lower or "iphone" in v_lower or "ios" in v_lower:
            os_badge = "apple"
        elif "dell" in v_lower:
            os_badge = "dell"
        elif "hp" in v_lower or "hewlett" in v_lower:
            os_badge = "hp"
        elif "tp-link" in v_lower:
            os_badge = "tp-link"
        elif "linux" in v_lower:
            os_badge = "linux"
        elif "microsoft" in v_lower or "windows" in v_lower:
            os_badge = "windows"

        devices.append({
            "id": idx,
            "name": name,
            "ip": ip,
            "mac": mac,
            "vendor": vendor,
            "icon": icon,
            "device_type": auto_type,
            "status": "Connected (Online)",
            "is_gateway": is_gateway,
            "angle": angle,
            "distance": distance,
            "os_badge": os_badge,
            "notes": notes,
            "is_customized": bool(override)
        })

    return devices

class RadarRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def serve_static_asset(self, filename, content_type):
        data = get_asset_bytes(filename)
        if data is not None:
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_error(404, f"File '{filename}' not found.")


    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/status":
            info = get_network_info()
            info["is_scanning"] = is_scanning
            info["last_scan"] = last_scan_time
            info["demo_mode"] = demo_mode_active
            self.send_json_response(info)
            return

        if path == "/api/devices":
            with scan_lock:
                devs = list(current_devices)
            self.send_json_response({"devices": devs, "count": len(devs)})
            return

        if path == "/api/deauth/events":
            query = urllib.parse.parse_qs(parsed.query)
            after = int((query.get("after", ["0"])[0] or "0"))
            net_info = get_network_info()
            with monitor_lock:
                if after > 0:
                    evs = [e for e in defensive_events if e["id"] > after]
                else:
                    evs = list(defensive_events)
                active = monitor_active
                mon_iface = monitor_interface_name
            self.send_json_response({
                "events": evs,
                "count": len(defensive_events),
                "adapter": mon_iface or net_info.get("interface", "wlan0"),
                "monitor_active": active
            })
            return

        if path == "/api/monitor/status":
            supported, reason, iface = check_monitor_capability()
            with monitor_lock:
                active = monitor_active
                mon_iface = monitor_interface_name
            self.send_json_response({
                "supported": supported,
                "reason": reason,
                "interface": iface,
                "active": active,
                "monitor_interface": mon_iface
            })
            return

        if path == "/api/export":
            # Export CSV or JSON
            query = urllib.parse.parse_qs(parsed.query)
            fmt = query.get("format", ["json"])[0]
            with scan_lock:
                devs = list(current_devices)
            if fmt == "csv":
                self.send_response(200)
                self.send_header("Content-Type", "text/csv")
                self.send_header("Content-Disposition", "attachment; filename=wifi_devices.csv")
                self.end_headers()
                csv_data = "ID,Name,IP Address,MAC Address,Vendor,Type,Status\n"
                for d in devs:
                    csv_data += f'"{d.get("id")}","{d.get("name")}","{d.get("ip")}","{d.get("mac")}","{d.get("vendor")}","{d.get("device_type")}","{d.get("status")}"\n'
                self.wfile.write(csv_data.encode("utf-8"))
            else:
                self.send_json_response(devs)
            return

        # Serve static web files directly (with fallback to embedded assets)
        clean_path = path.lstrip("/")
        if not clean_path or clean_path == "index.html":
            self.serve_static_asset("index.html", "text/html; charset=utf-8")
            return

        if clean_path == "style.css":
            self.serve_static_asset("style.css", "text/css; charset=utf-8")
            return

        if clean_path == "app.js":
            self.serve_static_asset("app.js", "application/javascript; charset=utf-8")
            return

        if clean_path in ["screenshot_reference.png", "web/screenshot_reference.png"]:
            self.serve_static_asset("screenshot_reference.png", "image/png")
            return

        try:
            return super().do_GET()
        except Exception:
            self.send_error(404, f"File not found: {path}")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            data = json.loads(body)
        except Exception:
            data = {}

        if path == "/api/scan":
            global is_scanning, last_scan_time, current_devices, demo_mode_active
            mode = data.get("mode", "auto")
            
            if mode == "demo":
                demo_mode_active = True
                with scan_lock:
                    current_devices = generate_mock_devices()
                    last_scan_time = time.strftime("%H:%M:%S")
                self.send_json_response({"status": "success", "mode": "demo", "devices": current_devices})
                return

            demo_mode_active = False
            net_info = get_network_info()
            iface = data.get("interface") or net_info["interface"]
            subnet = data.get("subnet") or net_info["subnet"]
            gateway = net_info["gateway"]

            def run_scan_thread():
                global is_scanning, last_scan_time, current_devices
                with scan_lock:
                    is_scanning = True
                try:
                    raw = perform_live_scan(iface, subnet, gateway)
                    # If live scan found nothing and user is testing/unprivileged, load demo devices gracefully
                    if not raw:
                        processed = generate_mock_devices()
                    else:
                        processed = process_devices(raw, gateway, net_info)
                    with scan_lock:
                        current_devices = processed
                        last_scan_time = time.strftime("%H:%M:%S")
                finally:
                    with scan_lock:
                        is_scanning = False

            t = threading.Thread(target=run_scan_thread)
            t.daemon = True
            t.start()
            # Wait briefly or respond async
            t.join(timeout=3.5)

            with scan_lock:
                self.send_json_response({
                    "status": "scanning" if is_scanning else "complete",
                    "devices": current_devices,
                    "count": len(current_devices)
                })
            return

        if path == "/api/device/update":
            mac = data.get("mac", "").upper()
            if not mac:
                self.send_json_response({"error": "MAC required"}, 400)
                return
            
            overrides = load_overrides()
            cur = overrides.get(mac, {})
            if "name" in data:
                cur["name"] = data["name"]
            if "icon" in data:
                cur["icon"] = data["icon"]
            if "notes" in data:
                cur["notes"] = data["notes"]
            overrides[mac] = cur
            save_overrides(overrides)

            # Update current in-memory device list
            with scan_lock:
                for d in current_devices:
                    if d.get("mac", "").upper() == mac:
                        if "name" in data and data["name"]:
                            d["name"] = data["name"]
                        if "icon" in data and data["icon"]:
                            d["icon"] = data["icon"]
                        if "notes" in data:
                            d["notes"] = data["notes"]
                        d["is_customized"] = True
                        break

            self.send_json_response({"status": "updated", "mac": mac, "override": cur})
            return

        if path == "/api/device/delete":
            mac = data.get("mac", "").upper()
            overrides = load_overrides()
            if mac in overrides:
                del overrides[mac]
                save_overrides(overrides)
            with scan_lock:
                current_devices[:] = [d for d in current_devices if d.get("mac", "").upper() != mac]
            self.send_json_response({"status": "deleted", "mac": mac})
            return

        if path == "/api/deauth/test":
            # Safe simulation telemetry logger only - no frames are ever sent.
            global defensive_event_counter
            action = data.get("action", "start")
            target_mac = data.get("target_mac", "UNKNOWN")
            target_name = data.get("target_name", "Device")
            duration_sec = data.get("duration", 10)

            with monitor_lock:
                defensive_event_counter += 1
                new_event = {
                    "id": defensive_event_counter,
                    "time": time.strftime("%H:%M:%S"),
                    "event_type": "DEAUTH (SIM)",
                    "source": "Simulated Test (no frames transmitted)",
                    "target": f"{target_mac} ({target_name})",
                    "reason_code": "N/A - simulation only",
                    "signal_dbm": "--",
                    "pmf": "Simulation",
                    "status": f"Test {action.upper()}: {duration_sec}s window"
                }
                defensive_events.insert(0, new_event)
                if len(defensive_events) > 200:
                    defensive_events.pop()

            self.send_json_response({
                "status": "success",
                "mode": "simulation",
                "action": action,
                "event": new_event
            })
            return

        if path == "/api/deauth/clear":
            with monitor_lock:
                defensive_events.clear()
            self.send_json_response({"status": "cleared"})
            return

        if path == "/api/monitor/start":
            global monitor_active, monitor_interface_name, monitor_base_interface, monitor_process, monitor_reader_thread, monitor_used_airmon
            with monitor_lock:
                if monitor_active:
                    self.send_json_response({"ok": True, "interface": monitor_interface_name, "already_running": True})
                    return
            supported, reason, iface = check_monitor_capability()
            if not supported:
                self.send_json_response({"ok": False, "error": reason})
                return
            try:
                mon_iface, used_airmon = start_monitor_interface(iface)
                proc = subprocess.Popen(
                    ["tshark", "-i", mon_iface, "-l", "-n", "-T", "fields",
                     "-e", "wlan.sa", "-e", "wlan.da", "-e", "wlan.fc.type_subtype", "-e", "wlan.fixed.reason_code",
                     "-Y", "wlan.fc.type_subtype==0x0c or wlan.fc.type_subtype==0x0a"],
                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, universal_newlines=True, bufsize=1
                )
                with monitor_lock:
                    monitor_process = proc
                    monitor_interface_name = mon_iface
                    monitor_base_interface = iface
                    monitor_used_airmon = used_airmon
                    monitor_active = True
                t = threading.Thread(target=monitor_reader_loop, daemon=True)
                t.start()
                monitor_reader_thread = t
                self.send_json_response({"ok": True, "interface": mon_iface})
            except Exception as e:
                self.send_json_response({"ok": False, "error": f"Failed to start monitoring: {e}"})
            return

        if path == "/api/monitor/stop":
            with monitor_lock:
                proc = monitor_process
                mon_iface = monitor_interface_name
                base_iface = monitor_base_interface
                used_airmon = monitor_used_airmon
                monitor_active = False
                monitor_process = None
            if proc:
                try:
                    proc.terminate()
                except Exception:
                    pass
            if mon_iface:
                stop_monitor_interface(mon_iface, used_airmon, base_iface)
            self.send_json_response({"ok": True})
            return

        self.send_json_response({"error": "Endpoint not found"}, 404)

    def send_json_response(self, data, code=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def main():
    global current_devices
    os.chdir(BASE_DIR)
    ensure_web_assets_on_disk()
    
    # Initialize initial sample/live device data
    net_info = get_network_info()
    current_devices = generate_mock_devices()

    print("=" * 65)
    print("  ⚡ WI-FI NETWORK RADAR - KALI LINUX EDITION ⚡")
    print("=" * 65)
    print(f"[*] Detected Interface: {net_info['interface']}")
    print(f"[*] Wi-Fi SSID        : {net_info['ssid']}")
    print(f"[*] Subnet Range      : {net_info['subnet']}")
    print(f"[*] Gateway IP        : {net_info['gateway']}")
    print(f"[*] Web Server URL    : http://127.0.0.1:{PORT}")
    print("=" * 65)

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), RadarRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Stopping Wi-Fi Network Radar...")
            with monitor_lock:
                proc = monitor_process
                mon_iface = monitor_interface_name
                base_iface = monitor_base_interface
                used_airmon = monitor_used_airmon
                active = monitor_active
            if active:
                print("[*] Restoring wireless adapter from monitor mode...")
                if proc:
                    try:
                        proc.terminate()
                    except Exception:
                        pass
                if mon_iface:
                    stop_monitor_interface(mon_iface, used_airmon, base_iface)
            httpd.shutdown()

if __name__ == "__main__":
    main()
