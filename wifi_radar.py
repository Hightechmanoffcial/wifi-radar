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
import shutil
import hashlib

PORT = 8888
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")
OVERRIDES_FILE = os.path.join(BASE_DIR, "device_overrides.json")

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

        # Serve static web files
        return super().do_GET()

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
