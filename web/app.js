/**
 * Wi-Fi Network Radar - Kali Linux Edition
 * 60FPS Tactical HUD Canvas Animation, Device Discovery & Customization System
 */

// --- Global State ---
let devices = [];
let selectedDeviceId = 3; // Default selection matching screenshot (Android Phone)
let currentNetworkInfo = {
  ssid: "CyberNet_5G",
  interface: "wlan0",
  subnet: "192.168.1.0/24",
  gateway: "192.168.1.1"
};

let sweepAngle = 0; // Current radar sweep angle in degrees
let sweepSpeed = 1.0; // Normal rotation speed
let isScanning = false;
let autoScanEnabled = true;
let autoScanTimer = null;
let soundEnabled = true;
let isDemoMode = false;

// Audio Context for Tactical Radar Ping
let audioCtx = null;

// DOM Elements
const canvas = document.getElementById("radar-canvas");
const ctx = canvas.getContext("2d");
const radarDevicesLayer = document.getElementById("radar-devices-layer");
const devicesTbody = document.getElementById("devices-tbody");
const devicesCountSpan = document.getElementById("devices-count");
const telemetryCount = document.getElementById("telemetry-count");
const radarStatusText = document.getElementById("radar-status-text");

// Selected Device Details Elements
const detailName = document.getElementById("detail-name");
const detailIp = document.getElementById("detail-ip");
const detailMac = document.getElementById("detail-mac");
const detailVendor = document.getElementById("detail-vendor");
const selectedBigIconWrapper = document.getElementById("selected-big-icon-wrapper");
const brandLogoWrapper = document.getElementById("brand-logo-svg");

// Header Elements
const wifiSsid = document.getElementById("wifi-ssid");
const wifiIface = document.getElementById("wifi-iface");
const wifiSubnet = document.getElementById("wifi-subnet");
const btnScan = document.getElementById("btn-scan");
const scanText = document.getElementById("scan-text");
const btnAutoscan = document.getElementById("btn-autoscan");
const btnAudio = document.getElementById("btn-audio");
const audioIconOn = document.getElementById("audio-icon-on");
const audioIconOff = document.getElementById("audio-icon-off");
const btnDemoToggle = document.getElementById("btn-demo-toggle");

// Modal Elements
const editModal = document.getElementById("edit-modal");
const modalClose = document.getElementById("modal-close");
const modalCancel = document.getElementById("btn-modal-cancel");
const modalSave = document.getElementById("btn-modal-save");
const modalReset = document.getElementById("btn-modal-reset");
const modalTargetMac = document.getElementById("modal-target-mac");
const modalTargetIp = document.getElementById("modal-target-ip");
const inputDeviceName = document.getElementById("input-device-name");
const inputDeviceNotes = document.getElementById("input-device-notes");
const iconSelectorGrid = document.getElementById("icon-selector-grid");
let modalSelectedIcon = "android";

// --- Vector Icon Library (Clean, Sharp SVGs) ---
const ICONS = {
  android: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="3" ry="3"></rect><line x1="12" y1="18" x2="12.01" y2="18" stroke-width="3"></line></svg>`,
  iphone: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="4" ry="4"></rect><line x1="12" y1="18" x2="12.01" y2="18" stroke-width="2.5"></line><path d="M10 4h4" stroke-width="1.5"></path></svg>`,
  laptop: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="12" rx="2"></rect><path d="M2 20h20"></path><line x1="12" y1="16" x2="12" y2="17"></line></svg>`,
  desktop: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>`,
  router: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="14" width="20" height="7" rx="2"></rect><path d="M6 14V6"></path><path d="M18 14V6"></path><line x1="6" y1="18" x2="6.01" y2="18"></line><line x1="10" y1="18" x2="10.01" y2="18"></line><line x1="14" y1="18" x2="14.01" y2="18"></line><line x1="18" y1="18" x2="18.01" y2="18"></line><circle cx="6" cy="5" r="1" fill="currentColor"></circle><circle cx="18" cy="5" r="1" fill="currentColor"></circle></svg>`,
  printer: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 6 2 18 2 18 9"></polyline><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path><rect x="6" y="14" width="12" height="8"></rect></svg>`,
  tablet: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect><circle cx="12" cy="18" r="1"></circle></svg>`,
  tv: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="13" rx="2"></rect><polyline points="17 2 12 7 7 2"></polyline></svg>`,
  gamepad: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="6" y1="12" x2="10" y2="12"></line><line x1="8" y1="10" x2="8" y2="14"></line><line x1="15" y1="13" x2="15.01" y2="13" stroke-width="3"></line><line x1="18" y1="11" x2="18.01" y2="11" stroke-width="3"></line><rect x="2" y="6" width="20" height="12" rx="6"></rect></svg>`,
  camera: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>`,
  iot: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="14" x2="23" y2="14"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="14" x2="4" y2="14"></line></svg>`,
  watch: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="7"></circle><polyline points="12 9 12 12 13.5 13.5"></polyline><path d="M16.51 17.35l-.35 3.83a2 2 0 0 1-2 1.82H9.83a2 2 0 0 1-2-1.82l-.35-3.83m.01-10.7l.35-3.83A2 2 0 0 1 9.83 1h4.35a2 2 0 0 1 2 1.82l.35 3.83"></path></svg>`,
  speaker: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="3"></rect><circle cx="12" cy="7" r="1" fill="currentColor"></circle><circle cx="12" cy="14" r="4"></circle></svg>`,
  server: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="8" rx="2"></rect><rect x="2" y="14" width="20" height="8" rx="2"></rect><line x1="6" y1="6" x2="6.01" y2="6"></line><line x1="6" y1="18" x2="6.01" y2="18"></line></svg>`
};

// Brand Badges (Logos for right side card)
const BRAND_BADGES = {
  android: `<svg viewBox="0 0 24 24" fill="#a4c639"><path d="M6 18c0 .55.45 1 1 1h1v3.5c0 .83.67 1.5 1.5 1.5s1.5-.67 1.5-1.5V19h2v3.5c0 .83.67 1.5 1.5 1.5s1.5-.67 1.5-1.5V19h1c.55 0 1-.45 1-1V8H6v10zM3.5 8C2.67 8 2 8.67 2 9.5v6c0 .83.67 1.5 1.5 1.5S5 16.33 5 15.5v-6C5 8.67 4.33 8 3.5 8zm17 0c-.83 0-1.5.67-1.5 1.5v6c0 .83.67 1.5 1.5 1.5s1.5-.67 1.5-1.5v-6c0-.83-.67-1.5-1.5-1.5zm-4.97-4.84l1.29-1.29c.2-.2.2-.51 0-.71a.495.495 0 0 0-.7 0l-1.44 1.44C13.63 2.22 12.35 2 11 2s-2.63.22-3.68.6l-1.44-1.44a.495.495 0 0 0-.7 0c-.2.2-.2.51 0 .71l1.29 1.29C4.87 4.19 3.86 5.86 3.65 7.78h14.7c-.21-1.92-1.22-3.59-2.82-4.62zM9 5.5c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm6 0c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1z"/></svg>`,
  apple: `<svg viewBox="0 0 24 24" fill="#ffffff"><path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M15.97 4.67c.66-.8 1.1-1.91.98-3.02-.95.04-2.1.63-2.77 1.42-.59.68-1.11 1.8-1 2.89 1.06.08 2.14-.52 2.79-1.29z"/></svg>`,
  dell: `<svg viewBox="0 0 24 24" fill="#0076ce"><circle cx="12" cy="12" r="10" stroke="#0076ce" stroke-width="2" fill="none"></circle><text x="12" y="16" font-family="Arial, sans-serif" font-weight="bold" font-size="9" text-anchor="middle" fill="#0076ce">DELL</text></svg>`,
  hp: `<svg viewBox="0 0 24 24" fill="#0096d6"><circle cx="12" cy="12" r="10" stroke="#0096d6" stroke-width="2" fill="none"></circle><text x="12" y="16" font-family="Arial, sans-serif" font-weight="bold" font-style="italic" font-size="11" text-anchor="middle" fill="#0096d6">hp</text></svg>`,
  "tp-link": `<svg viewBox="0 0 24 24" fill="#48c5a2"><circle cx="12" cy="12" r="9" stroke="#48c5a2" stroke-width="2" fill="none"></circle><path d="M8 12h8M12 8v8" stroke="#48c5a2" stroke-width="2"></path></svg>`,
  linux: `<svg viewBox="0 0 24 24" fill="#e5a93c"><path d="M12 2C9.5 2 8 4 8 7v4c-1.5 1-2 3-2 5 0 2.5 2 4 6 4s6-1.5 6-4c0-2-.5-4-2-5V7c0-3-1.5-5-4-5z"/></svg>`,
  windows: `<svg viewBox="0 0 24 24" fill="#00a4ef"><path d="M3 5.4l7.6-1V11H3V5.4zm7.6 6.4v6.8L3 17.5V11.8h7.6zM11.6 4.3L21 3v8h-9.4V4.3zm9.4 8.7L11.6 19.8V13H21v0z"/></svg>`,
  network: `<svg viewBox="0 0 24 24" fill="none" stroke="#00ff66" stroke-width="2"><circle cx="12" cy="12" r="9"></circle><path d="M12 3a15 15 0 0 0 0 18M12 3a15 15 0 0 1 0 18M3 12h18"></path></svg>`
};

// Available categories for customize modal
const CATEGORIES = [
  { id: "android", name: "Android Phone" },
  { id: "iphone", name: "iPhone / iOS" },
  { id: "laptop", name: "Laptop" },
  { id: "desktop", name: "Desktop PC" },
  { id: "router", name: "Router / AP" },
  { id: "printer", name: "Printer" },
  { id: "tablet", name: "Tablet / iPad" },
  { id: "tv", name: "Smart TV" },
  { id: "gamepad", name: "Gaming Console" },
  { id: "camera", name: "Security Camera" },
  { id: "iot", name: "Smart Home / IoT" },
  { id: "watch", name: "Smartwatch" },
  { id: "speaker", name: "Smart Speaker" },
  { id: "server", name: "Server / NAS" }
];

// --- Audio Synthesizer (Sci-Fi Radar Sonar Ping) ---
function playSonarPing() {
  if (!soundEnabled) return;
  try {
    if (!audioCtx) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx.state === "suspended") {
      audioCtx.resume();
    }
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    const now = audioCtx.currentTime;

    osc.type = "sine";
    osc.frequency.setValueAtTime(880, now);
    osc.frequency.exponentialRampToValueAtTime(440, now + 0.35);

    gain.gain.setValueAtTime(0.08, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);

    osc.connect(gain);
    gain.connect(audioCtx.destination);

    osc.start(now);
    osc.stop(now + 0.35);
  } catch (e) {
    console.warn("Audio ping error:", e);
  }
}

// --- Fetch Network Status & Info ---
async function fetchNetworkStatus() {
  try {
    const res = await fetch("/api/status");
    if (!res.ok) throw new Error("Status fetch failed");
    const data = await res.json();
    currentNetworkInfo = data;
    wifiSsid.textContent = data.ssid || "CyberNet_5G";
    wifiIface.textContent = data.interface || "wlan0";
    wifiSubnet.textContent = data.subnet || "192.168.1.0/24";
  } catch (err) {
    console.log("Using default network status:", err.message);
  }
}

// --- Fetch Devices ---
async function fetchDevices(showFeedback = false) {
  try {
    const res = await fetch("/api/devices");
    if (!res.ok) throw new Error("Devices fetch failed");
    const data = await res.json();
    devices = data.devices || [];
    renderDevicesTable();
    updateSelectedDeviceCard();
    updateDeauthTestingTarget();
    renderRadarBlips();
    updateTelemetry();
    if (showFeedback) showToast(`Detected ${devices.length} connected devices`);
  } catch (err) {
    console.error("Fetch devices error:", err);
  }
}

// --- Trigger Network Scan ---
async function triggerScan() {
  if (isScanning) return;
  isScanning = true;
  sweepSpeed = 2.4; // Speed up sweep during scan
  btnScan.classList.add("scanning");
  document.querySelector(".radar-spin").classList.add("spinning");
  scanText.textContent = "SCANNING...";
  radarStatusText.textContent = "DEEP ARP & NMAP SCAN IN PROGRESS";
  radarStatusText.style.color = "var(--neon-cyan)";

  try {
    const res = await fetch("/api/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        interface: currentNetworkInfo.interface,
        subnet: currentNetworkInfo.subnet,
        mode: isDemoMode ? "demo" : "live"
      })
    });
    const data = await res.json();
    if (data.devices) {
      devices = data.devices;
      renderDevicesTable();
      updateSelectedDeviceCard();
      renderRadarBlips();
      updateTelemetry();
      playSonarPing();
    }
  } catch (err) {
    console.error("Scan error:", err);
  } finally {
    isScanning = false;
    sweepSpeed = 1.0;
    btnScan.classList.remove("scanning");
    document.querySelector(".radar-spin").classList.remove("spinning");
    scanText.textContent = "SCAN NETWORK";
    radarStatusText.textContent = "RADAR SWEEP ACTIVE";
    radarStatusText.style.color = "var(--neon-green)";
  }
}

// --- Render Table ---
function renderDevicesTable() {
  devicesCountSpan.textContent = devices.length;
  devicesTbody.innerHTML = "";

  devices.forEach((dev) => {
    const tr = document.createElement("tr");
    if (dev.id === selectedDeviceId) {
      tr.classList.add("selected");
    }

    const iconSvg = ICONS[dev.icon] || ICONS.desktop;

    tr.innerHTML = `
      <td style="font-weight: 700; color: #a4c639;">${dev.id}</td>
      <td>
        <div class="device-name-cell">
          <div class="row-device-icon">${iconSvg}</div>
          <span>${escapeHtml(dev.name)}</span>
        </div>
      </td>
      <td class="code-font" style="color: #00e5ff;">${dev.ip}</td>
      <td class="code-font" style="color: #cbd5e1;">${dev.mac}</td>
      <td style="color: #98ff98;">${escapeHtml(dev.vendor)}</td>
    `;

    tr.addEventListener("click", () => {
      selectDevice(dev.id);
    });

    devicesTbody.appendChild(tr);
  });
}

// --- Select Device Handler ---
function selectDevice(id) {
  selectedDeviceId = id;
  // Update table highlight
  const rows = devicesTbody.querySelectorAll("tr");
  devices.forEach((dev, index) => {
    if (rows[index]) {
      if (dev.id === id) {
        rows[index].classList.add("selected");
      } else {
        rows[index].classList.remove("selected");
      }
    }
  });

  // Update Radar targeting reticle
  updateRadarTargetingReticle();
  // Update detail card
  updateSelectedDeviceCard();
  // Update Deauthentication Testing Target Summary
  updateDeauthTestingTarget();
}

// --- Update Selected Device Details Card ---
function updateSelectedDeviceCard() {
  const dev = devices.find((d) => d.id === selectedDeviceId) || devices[0];
  if (!dev) return;

  detailName.textContent = dev.name;
  detailIp.textContent = dev.ip;
  detailMac.textContent = dev.mac;
  detailVendor.textContent = dev.vendor;

  // Update big device icon
  const iconSvg = ICONS[dev.icon] || ICONS.desktop;
  selectedBigIconWrapper.innerHTML = iconSvg;

  // Update OS / Brand Logo badge
  const badgeSvg = BRAND_BADGES[dev.os_badge] || BRAND_BADGES.network;
  brandLogoWrapper.innerHTML = badgeSvg;
}

// --- Telemetry Update ---
function updateTelemetry() {
  telemetryCount.textContent = devices.length;
  const pings = ["1ms", "2ms", "1.4ms", "0.8ms"];
  const pingEl = document.getElementById("telemetry-ping");
  if (pingEl) pingEl.textContent = pings[Math.floor(Math.random() * pings.length)];
}

// --- Render Radar Blips and Icons ---
function renderRadarBlips() {
  radarDevicesLayer.innerHTML = "";
  const size = 520;
  const center = size / 2;
  const maxRadius = size * 0.45;

  devices.forEach((dev) => {
    // Polar coordinates: dev.angle in degrees (0° = 12 o'clock, clockwise), dev.distance 0.0 to 1.0
    // Math angles: 0° is 3 o'clock, so angle - 90 converts to math angle
    const rad = ((dev.angle - 90) * Math.PI) / 180;
    const r = dev.distance * maxRadius;
    const x = center + r * Math.cos(rad);
    const y = center + r * Math.sin(rad);

    const blipContainer = document.createElement("div");
    blipContainer.className = "radar-blip-container";
    blipContainer.id = `blip-device-${dev.id}`;
    blipContainer.style.left = `${x}px`;
    blipContainer.style.top = `${y}px`;

    if (dev.id === selectedDeviceId) {
      blipContainer.classList.add("targeted");
    }

    const iconSvg = ICONS[dev.icon] || ICONS.desktop;

    blipContainer.innerHTML = `
      <div class="blip-point"></div>
      <div class="blip-icon-badge" title="${escapeHtml(dev.name)} (${dev.ip})">
        ${iconSvg}
      </div>
      <div class="blip-targeting-box"></div>
      <div class="blip-targeting-box-extra"></div>
    `;

    blipContainer.addEventListener("click", (e) => {
      e.stopPropagation();
      selectDevice(dev.id);
    });

    radarDevicesLayer.appendChild(blipContainer);
  });
}

function updateRadarTargetingReticle() {
  devices.forEach((dev) => {
    const el = document.getElementById(`blip-device-${dev.id}`);
    if (el) {
      if (dev.id === selectedDeviceId) {
        el.classList.add("targeted");
      } else {
        el.classList.remove("targeted");
      }
    }
  });
}

// --- 60FPS Tactical Canvas Radar Animation ---
let lastFrameTime = performance.now();

function drawRadar(timestamp) {
  const delta = (timestamp - lastFrameTime) / 1000;
  lastFrameTime = timestamp;

  // Advance radar sweep angle (0 to 360)
  sweepAngle = (sweepAngle + sweepSpeed * 60 * delta) % 360;

  const w = canvas.width;
  const h = canvas.height;
  const cx = w / 2;
  const cy = h / 2;
  const radius = w * 0.44;

  ctx.clearRect(0, 0, w, h);

  // 1. Draw outer circle border
  ctx.save();
  ctx.beginPath();
  ctx.arc(cx, cy, radius, 0, Math.PI * 2);
  ctx.strokeStyle = "rgba(0, 255, 102, 0.75)";
  ctx.lineWidth = 2.5;
  ctx.shadowColor = "rgba(0, 255, 102, 0.6)";
  ctx.shadowBlur = 12;
  ctx.stroke();
  ctx.restore();

  // 2. Draw 4 Concentric Green Grid Rings
  const rings = [0.25, 0.5, 0.75, 1.0];
  rings.forEach((scale) => {
    ctx.beginPath();
    ctx.arc(cx, cy, radius * scale, 0, Math.PI * 2);
    ctx.strokeStyle = "rgba(0, 255, 102, 0.35)";
    ctx.lineWidth = 1.2;
    ctx.stroke();
  });

  // 3. Draw Radial Grid Spoke Lines (every 45 degrees)
  for (let a = 0; a < 360; a += 45) {
    const rad = (a * Math.PI) / 180;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(cx + radius * Math.cos(rad), cy + radius * Math.sin(rad));
    ctx.strokeStyle = "rgba(0, 255, 102, 0.25)";
    ctx.lineWidth = 1;
    ctx.stroke();
  }

  // Intermediate fainter tick spokes (every 15 degrees)
  for (let a = 0; a < 360; a += 15) {
    if (a % 45 !== 0) {
      const rad = (a * Math.PI) / 180;
      ctx.beginPath();
      ctx.moveTo(cx + radius * 0.94 * Math.cos(rad), cy + radius * 0.94 * Math.sin(rad));
      ctx.lineTo(cx + radius * Math.cos(rad), cy + radius * Math.sin(rad));
      ctx.strokeStyle = "rgba(0, 255, 102, 0.4)";
      ctx.lineWidth = 1;
      ctx.stroke();
    }
  }

  // 4. Draw Rotating Radar Sweep Cone (Phosphor trail)
  ctx.save();
  ctx.beginPath();
  ctx.moveTo(cx, cy);
  // Convert sweepAngle (where 0 is 12 o'clock) to radians
  const leadRad = ((sweepAngle - 90) * Math.PI) / 180;
  const trailSpan = (48 * Math.PI) / 180; // 48-degree sweep cone
  const trailRad = leadRad - trailSpan;

  ctx.arc(cx, cy, radius, trailRad, leadRad, false);
  ctx.closePath();

  // Radial / Angular gradient effect
  const sweepGrad = ctx.createRadialGradient(cx, cy, 10, cx, cy, radius);
  sweepGrad.addColorStop(0, "rgba(0, 255, 102, 0.25)");
  sweepGrad.addColorStop(0.7, "rgba(0, 255, 102, 0.15)");
  sweepGrad.addColorStop(1, "rgba(0, 255, 102, 0.05)");

  ctx.fillStyle = sweepGrad;
  ctx.fill();

  // Leading bright sweep line
  ctx.beginPath();
  ctx.moveTo(cx, cy);
  ctx.lineTo(cx + radius * Math.cos(leadRad), cy + radius * Math.sin(leadRad));
  ctx.strokeStyle = "#39ff14";
  ctx.lineWidth = 2.5;
  ctx.shadowColor = "#39ff14";
  ctx.shadowBlur = 10;
  ctx.stroke();
  ctx.restore();

  // 5. Detect when sweep passes over devices for blip ping
  devices.forEach((dev) => {
    const diff = (sweepAngle - dev.angle + 360) % 360;
    if (diff >= 0 && diff < 3 && !dev._pinged) {
      dev._pinged = true;
      triggerBlipFlash(dev.id);
      playSonarPing();
    } else if (diff > 15) {
      dev._pinged = false;
    }
  });

  requestAnimationFrame(drawRadar);
}

// Flash blip visually when beam sweeps over it
function triggerBlipFlash(deviceId) {
  const el = document.getElementById(`blip-device-${deviceId}`);
  if (!el) return;
  const pt = el.querySelector(".blip-point");
  if (pt) {
    pt.style.transform = "scale(1.8)";
    pt.style.boxShadow = "0 0 25px #00ff66, 0 0 40px #ffffff";
    setTimeout(() => {
      pt.style.transform = "";
      pt.style.boxShadow = "";
    }, 450);
  }
}

// --- Customization Modal Logic ---
function openEditModal(deviceId) {
  const dev = devices.find((d) => d.id === deviceId) || devices[0];
  if (!dev) return;

  modalTargetMac.textContent = dev.mac;
  modalTargetIp.textContent = dev.ip;
  inputDeviceName.value = dev.name;
  inputDeviceNotes.value = dev.notes || "";
  modalSelectedIcon = dev.icon || "android";

  buildIconSelectorGrid();
  editModal.classList.remove("hidden");
  inputDeviceName.focus();
}

function closeEditModal() {
  editModal.classList.add("hidden");
}

function buildIconSelectorGrid() {
  iconSelectorGrid.innerHTML = "";
  CATEGORIES.forEach((cat) => {
    const card = document.createElement("div");
    card.className = "icon-choice-card";
    if (cat.id === modalSelectedIcon) {
      card.classList.add("selected");
    }

    card.innerHTML = `
      ${ICONS[cat.id]}
      <span class="icon-choice-name">${cat.name}</span>
    `;

    card.addEventListener("click", () => {
      modalSelectedIcon = cat.id;
      iconSelectorGrid.querySelectorAll(".icon-choice-card").forEach((c) => c.classList.remove("selected"));
      card.classList.add("selected");
    });

    iconSelectorGrid.appendChild(card);
  });
}

async function saveDeviceCustomization() {
  const mac = modalTargetMac.textContent.trim();
  const newName = inputDeviceName.value.trim() || "Device";
  const newNotes = inputDeviceNotes.value.trim();

  // Optimistic update
  const dev = devices.find((d) => d.mac === mac);
  if (dev) {
    dev.name = newName;
    dev.icon = modalSelectedIcon;
    dev.notes = newNotes;
    dev.is_customized = true;
  }

  renderDevicesTable();
  updateSelectedDeviceCard();
  renderRadarBlips();
  closeEditModal();
  showToast(`Updated identity for ${newName}`);

  // Send to backend
  try {
    await fetch("/api/device/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        mac: mac,
        name: newName,
        icon: modalSelectedIcon,
        notes: newNotes
      })
    });
  } catch (err) {
    console.error("Save error:", err);
  }
}

async function resetDeviceCustomization() {
  const mac = modalTargetMac.textContent.trim();
  closeEditModal();
  showToast(`Reset device to auto-detection`);

  try {
    await fetch("/api/device/delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mac: mac })
    });
    fetchDevices();
  } catch (err) {
    console.error("Reset error:", err);
  }
}

// --- Toast Notification ---
function showToast(msg) {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.classList.remove("hidden");
  setTimeout(() => {
    toast.classList.add("hidden");
  }, 3200);
}

// --- HTML Escaping Helper ---
function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

// --- Export Functions ---
document.getElementById("btn-export-csv").addEventListener("click", () => {
  window.open("/api/export?format=csv", "_blank");
});

document.getElementById("btn-export-json").addEventListener("click", () => {
  window.open("/api/export?format=json", "_blank");
});

// --- Event Listeners ---
btnScan.addEventListener("click", () => {
  triggerScan();
});

btnAutoscan.addEventListener("click", () => {
  autoScanEnabled = !autoScanEnabled;
  if (autoScanEnabled) {
    btnAutoscan.classList.add("active");
    startAutoScan();
    showToast("Auto-scan enabled (15s interval)");
  } else {
    btnAutoscan.classList.remove("active");
    stopAutoScan();
    showToast("Auto-scan paused");
  }
});

function startAutoScan() {
  if (autoScanTimer) clearInterval(autoScanTimer);
  autoScanTimer = setInterval(() => {
    if (!isScanning) triggerScan();
  }, 15000);
}

function stopAutoScan() {
  if (autoScanTimer) {
    clearInterval(autoScanTimer);
    autoScanTimer = null;
  }
}

btnAudio.addEventListener("click", () => {
  soundEnabled = !soundEnabled;
  if (soundEnabled) {
    audioIconOn.classList.remove("hidden");
    audioIconOff.classList.add("hidden");
    playSonarPing();
    showToast("Radar audio enabled");
  } else {
    audioIconOn.classList.add("hidden");
    audioIconOff.classList.remove("hidden");
    showToast("Radar audio muted");
  }
});

btnDemoToggle.addEventListener("click", () => {
  isDemoMode = !isDemoMode;
  showToast(isDemoMode ? "Previewing Demo Radar Devices" : "Switched to Live Kali Network");
  triggerScan();
});

document.getElementById("btn-edit-selected").addEventListener("click", () => {
  openEditModal(selectedDeviceId);
});

modalClose.addEventListener("click", closeEditModal);
modalCancel.addEventListener("click", closeEditModal);
modalSave.addEventListener("click", saveDeviceCustomization);
modalReset.addEventListener("click", resetDeviceCustomization);

// ==============================================================================
// Deauthentication Testing & Defensive Monitoring Module
// ==============================================================================

// Deauth Testing DOM Elements
const targetDeviceBanner = document.getElementById("target-device-banner");
const targetName = document.getElementById("target-name");
const targetIp = document.getElementById("target-ip");
const targetMac = document.getElementById("target-mac");
const targetVendor = document.getElementById("target-vendor");

const btnStartDeauth = document.getElementById("btn-start-deauth");
const btnStopDeauth = document.getElementById("btn-stop-deauth");
const deauthStatusBadge = document.getElementById("deauth-status-badge");
const deauthStatusText = document.getElementById("deauth-status-text");

const durationChipsContainer = document.getElementById("duration-chips");
const durationSelectDropdown = document.getElementById("duration-select-dropdown");

const deauthProgressBar = document.getElementById("deauth-progress-bar");
const telemetryProgressPct = document.getElementById("telemetry-progress-pct");
const telemetryFrames = document.getElementById("telemetry-frames");
const countdownTimerDisplay = document.getElementById("countdown-timer-display");

// Defensive Monitoring DOM Elements
const defensiveEventsTbody = document.getElementById("defensive-events-tbody");
const defensiveTotalCount = document.getElementById("defensive-total-count");
const defensiveDeauthCount = document.getElementById("defensive-deauth-count");
const defensiveDisassocCount = document.getElementById("defensive-disassoc-count");
const defensivePmfCount = document.getElementById("defensive-pmf-count");
const btnClearDefensiveLog = document.getElementById("btn-clear-defensive-log");
const btnExportDefensiveLog = document.getElementById("btn-export-defensive-log");

// Real Monitoring DOM Elements
const adapterCapabilityPill = document.getElementById("adapter-capability-pill");
const capIndicator = document.getElementById("cap-indicator");
const capText = document.getElementById("cap-text");
const monitorReasonLine = document.getElementById("monitor-reason-line");
const btnToggleMonitoring = document.getElementById("btn-toggle-monitoring");
const monitorToggleLabel = document.getElementById("monitor-toggle-label");

// Testing & Defensive State
let currentTestDuration = 10; // seconds
let deauthTestState = {
  status: "idle", // 'idle' | 'running' | 'completed' | 'stopped'
  duration: 10,
  remaining: 10,
  elapsed: 0,
  framesCount: 0,
  interval: null
};

let defensiveEventsList = [];

// Real Monitoring State (passive capture only - never transmits frames)
let monitorSupported = false;
let monitorActiveState = false;
let monitorLastEventId = 0;
let monitorPollTimer = null;

// Format seconds into MM:SS display
function formatTime(sec) {
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

// Update Target Summary in the Testing Panel
function updateDeauthTestingTarget() {
  const dev = devices.find((d) => d.id === selectedDeviceId);

  if (!dev) {
    targetName.textContent = "No Device Selected";
    targetIp.textContent = "--";
    targetMac.textContent = "--";
    targetVendor.textContent = "Select from table or radar";
    targetDeviceBanner.classList.remove("has-target");

    if (deauthTestState.status === "idle") {
      btnStartDeauth.disabled = true;
      toggleDurationControls(false);
    }
    return;
  }

  targetName.textContent = dev.name;
  targetIp.textContent = dev.ip;
  targetMac.textContent = dev.mac;
  targetVendor.textContent = dev.vendor;
  targetDeviceBanner.classList.add("has-target");

  if (deauthTestState.status !== "running") {
    btnStartDeauth.disabled = false;
    toggleDurationControls(true);
  }
}

// Toggle enabled/disabled state for duration controls
function toggleDurationControls(enabled) {
  durationSelectDropdown.disabled = !enabled;
  const chips = durationChipsContainer.querySelectorAll(".duration-chip");
  chips.forEach((c) => (c.disabled = !enabled));
}

// Set selected duration (synchronizes chips & dropdown)
function setTestDuration(seconds) {
  if (deauthTestState.status === "running") return;
  currentTestDuration = Number(seconds);

  // Update chips active state
  const chips = durationChipsContainer.querySelectorAll(".duration-chip");
  chips.forEach((chip) => {
    if (Number(chip.getAttribute("data-seconds")) === currentTestDuration) {
      chip.classList.add("active");
    } else {
      chip.classList.remove("active");
    }
  });

  // Update dropdown value
  durationSelectDropdown.value = String(currentTestDuration);

  // Update countdown clock when idle or completed
  if (deauthTestState.status !== "running") {
    countdownTimerDisplay.textContent = formatTime(currentTestDuration);
    deauthTestState.remaining = currentTestDuration;
  }
}

// Update Testing Status UI (Idle, Running, Completed, Stopped)
function updateDeauthUI() {
  deauthStatusBadge.className = `testing-status-badge status-${deauthTestState.status}`;

  switch (deauthTestState.status) {
    case "idle":
      deauthStatusText.textContent = "Status: Idle";
      btnStartDeauth.disabled = !devices.some((d) => d.id === selectedDeviceId);
      btnStopDeauth.disabled = true;
      toggleDurationControls(true);
      deauthProgressBar.classList.remove("active-anim");
      break;

    case "running":
      deauthStatusText.textContent = "Status: Running";
      btnStartDeauth.disabled = true;
      btnStopDeauth.disabled = false;
      toggleDurationControls(false);
      deauthProgressBar.classList.add("active-anim");
      break;

    case "completed":
      deauthStatusText.textContent = "Status: Completed";
      btnStartDeauth.disabled = false;
      btnStopDeauth.disabled = true;
      toggleDurationControls(true);
      deauthProgressBar.classList.remove("active-anim");
      break;

    case "stopped":
      deauthStatusText.textContent = "Status: Stopped";
      btnStartDeauth.disabled = false;
      btnStopDeauth.disabled = true;
      toggleDurationControls(true);
      deauthProgressBar.classList.remove("active-anim");
      break;
  }
}

// Start Safe Deauthentication Simulation
function startDeauthSimulation() {
  const dev = devices.find((d) => d.id === selectedDeviceId);
  if (!dev) {
    showToast("Please select a target device first");
    return;
  }

  // Clear any existing timer
  if (deauthTestState.interval) {
    clearInterval(deauthTestState.interval);
    deauthTestState.interval = null;
  }

  deauthTestState.status = "running";
  deauthTestState.duration = currentTestDuration;
  deauthTestState.remaining = currentTestDuration;
  deauthTestState.elapsed = 0;
  deauthTestState.framesCount = 0;

  deauthProgressBar.style.width = "0%";
  telemetryProgressPct.textContent = "0%";
  telemetryFrames.textContent = "0";
  countdownTimerDisplay.textContent = formatTime(currentTestDuration);

  updateDeauthUI();
  showToast(`Starting safe simulation for ${dev.name} (${currentTestDuration}s)`);

  // Notify backend for defensive audit log
  fetch("/api/deauth/test", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      action: "start",
      target_mac: dev.mac,
      target_name: dev.name,
      duration: currentTestDuration
    })
  }).catch((e) => console.warn("Audit test log notice:", e));

  // Log to the Defensive Monitor, clearly tagged as a simulation so it is
  // never confused with a real frame detected by the monitoring panel below.
  addDefensiveEvent({
    time: new Date().toLocaleTimeString(),
    event_type: "DEAUTH (SIM)",
    source: "Simulated Test (no frames transmitted)",
    target: `${dev.mac} [${dev.name}]`,
    reason_code: "N/A - simulation only",
    signal_dbm: "--",
    pmf: "Simulation",
    status: "Test Active"
  });

  const startTime = Date.now();
  const totalMs = currentTestDuration * 1000;

  deauthTestState.interval = setInterval(() => {
    const now = Date.now();
    const elapsedMs = now - startTime;
    const elapsedSec = Math.floor(elapsedMs / 1000);
    deauthTestState.elapsed = Math.min(elapsedSec, currentTestDuration);
    deauthTestState.remaining = Math.max(0, currentTestDuration - deauthTestState.elapsed);

    // Frame simulation counter (~10 simulated frames/sec)
    deauthTestState.framesCount = Math.floor(elapsedMs / 100);

    const progressPct = Math.min(100, (elapsedMs / totalMs) * 100);
    deauthProgressBar.style.width = `${progressPct.toFixed(1)}%`;
    telemetryProgressPct.textContent = `${Math.floor(progressPct)}%`;
    telemetryFrames.textContent = deauthTestState.framesCount;
    countdownTimerDisplay.textContent = formatTime(deauthTestState.remaining);

    // Play subtle tactical ping every 5 seconds
    if (elapsedSec > 0 && elapsedSec % 5 === 0 && deauthTestState.lastPingSec !== elapsedSec) {
      deauthTestState.lastPingSec = elapsedSec;
      playSonarPing();
    }

    if (elapsedMs >= totalMs) {
      completeDeauthSimulation();
    }
  }, 100);
}

// Stop Active Simulation
function stopDeauthSimulation() {
  if (deauthTestState.interval) {
    clearInterval(deauthTestState.interval);
    deauthTestState.interval = null;
  }

  deauthTestState.status = "stopped";
  updateDeauthUI();
  showToast("Deauthentication testing stopped by user");

  const dev = devices.find((d) => d.id === selectedDeviceId);
  addDefensiveEvent({
    time: new Date().toLocaleTimeString(),
    event_type: "DISASSOC (SIM)",
    source: "Manual Operator (simulation stopped early)",
    target: dev ? `${dev.mac} [${dev.name}]` : "--",
    reason_code: "N/A - simulation only",
    signal_dbm: "--",
    pmf: "Simulation",
    status: "Stopped Early"
  });
}

// Complete Simulation
function completeDeauthSimulation() {
  if (deauthTestState.interval) {
    clearInterval(deauthTestState.interval);
    deauthTestState.interval = null;
  }

  deauthTestState.status = "completed";
  deauthTestState.remaining = 0;
  deauthProgressBar.style.width = "100%";
  telemetryProgressPct.textContent = "100%";
  countdownTimerDisplay.textContent = "00:00";
  updateDeauthUI();

  const dev = devices.find((d) => d.id === selectedDeviceId);
  const targetLabel = dev ? `${dev.name} (${dev.mac})` : "Selected device";
  showToast(`Deauthentication test completed for ${targetLabel}`);
  playSonarPing();

  addDefensiveEvent({
    time: new Date().toLocaleTimeString(),
    event_type: "DEAUTH (SIM)",
    source: "Simulated Test (no frames transmitted)",
    target: dev ? `${dev.mac} [${dev.name}]` : "--",
    reason_code: "N/A - simulation only",
    signal_dbm: "--",
    pmf: "Simulation",
    status: "Completed (100%)"
  });
}

// --- Defensive Monitoring Functions ---

async function fetchDefensiveEvents() {
  try {
    const res = await fetch("/api/deauth/events");
    if (!res.ok) throw new Error("Defensive events fetch failed");
    const data = await res.json();
    defensiveEventsList = data.events || [];
    if (defensiveEventsList.length) {
      monitorLastEventId = Math.max(...defensiveEventsList.map((e) => e.id || 0));
    }
    renderDefensiveEventsTable();
  } catch (err) {
    // No fabricated fallback data - an unreachable backend just means an
    // empty, honest log rather than invented sample events.
    console.log("Could not fetch defensive events:", err.message);
    renderDefensiveEventsTable();
  }
}

function renderDefensiveEventsTable() {
  defensiveEventsTbody.innerHTML = "";

  if (defensiveEventsList.length === 0) {
    defensiveEventsTbody.innerHTML = `<tr class="defensive-events-empty-row"><td colspan="8">No deauthentication or disassociation frames detected yet.</td></tr>`;
    defensiveTotalCount.textContent = "0";
    defensiveDeauthCount.textContent = "0";
    defensiveDisassocCount.textContent = "0";
    defensivePmfCount.textContent = "0";
    return;
  }

  let deauthCount = 0;
  let disassocCount = 0;
  let pmfCount = 0;

  defensiveEventsList.forEach((ev, idx) => {
    const tr = document.createElement("tr");

    const isSim = ev.event_type.includes("SIM");
    const isDeauth = ev.event_type.includes("DEAUTH");
    const isDisassoc = ev.event_type.includes("DISASSOC");

    if (isDeauth && !isSim) deauthCount++;
    if (isDisassoc && !isSim) disassocCount++;
    if (ev.pmf && ev.pmf.includes("Protected")) pmfCount++;

    let badgeClass;
    if (isSim) {
      badgeClass = isDeauth ? "event-badge-deauth-sim" : "event-badge-disassoc-sim";
    } else {
      badgeClass = isDeauth ? "event-badge-deauth" : "event-badge-disassoc";
    }

    tr.innerHTML = `
      <td style="font-weight: 700; color: #a4c639;">${idx + 1}</td>
      <td class="code-font" style="color: #7df9ff;">${escapeHtml(ev.time)}</td>
      <td><span class="${badgeClass}">${escapeHtml(ev.event_type)}</span></td>
      <td class="code-font" style="color: #cbd5e1;">${escapeHtml(ev.source)}</td>
      <td class="code-font" style="color: #00e5ff;">${escapeHtml(ev.target)}</td>
      <td style="color: #cbd5e1;">${escapeHtml(ev.reason_code)}</td>
      <td class="code-font" style="color: #98ff98;">${escapeHtml(ev.signal_dbm)}</td>
      <td><span class="defense-status-tag">● ${escapeHtml(ev.status || ev.pmf)}</span></td>
    `;

    defensiveEventsTbody.appendChild(tr);
  });

  // Update telemetry counters
  defensiveTotalCount.textContent = defensiveEventsList.length;
  defensiveDeauthCount.textContent = deauthCount;
  defensiveDisassocCount.textContent = disassocCount;
  defensivePmfCount.textContent = pmfCount;
}

function addDefensiveEvent(eventObj) {
  eventObj.id = (monitorLastEventId += 1);
  defensiveEventsList.unshift(eventObj);
  if (defensiveEventsList.length > 200) {
    defensiveEventsList.pop();
  }
  renderDefensiveEventsTable();
}

function clearDefensiveLog() {
  defensiveEventsList = [];
  renderDefensiveEventsTable();
  showToast("Defensive 802.11 event log cleared");
  fetch("/api/deauth/clear", { method: "POST" }).catch(() => {});
}

// ------------------------------------------------------------------------------
// Real Defensive Monitoring (passive capture, never transmits anything)
//
// This checks whether the Kali box can actually put its adapter into monitor
// mode and parse live 802.11 management frames with tshark, and if so lets the
// user start/stop that real capture. If it can't (no root, no monitor-mode
// adapter, tshark missing, etc.) the panel says exactly why instead of ever
// faking detections.
// ------------------------------------------------------------------------------

async function checkMonitorCapability() {
  try {
    const res = await fetch("/api/monitor/status");
    const data = await res.json();
    monitorSupported = !!data.supported;
    monitorActiveState = !!data.active;

    if (monitorActiveState) {
      setCapabilityPillState("running", `Monitoring active on ${data.monitor_interface || data.interface}`);
      btnToggleMonitoring.disabled = false;
      monitorToggleLabel.textContent = "STOP MONITORING";
      btnToggleMonitoring.classList.add("monitoring-active");
      monitorReasonLine.classList.add("hidden");
      if (!monitorPollTimer) monitorPollTimer = setInterval(pollMonitorEvents, 2000);
    } else if (monitorSupported) {
      setCapabilityPillState("supported", `Adapter ready: ${data.interface}`);
      btnToggleMonitoring.disabled = false;
      monitorToggleLabel.textContent = "START MONITORING";
      btnToggleMonitoring.classList.remove("monitoring-active");
      monitorReasonLine.classList.add("hidden");
    } else {
      setCapabilityPillState("unsupported", "Monitoring unavailable");
      btnToggleMonitoring.disabled = true;
      monitorReasonLine.textContent = data.reason || "Real monitoring is unavailable on this system.";
      monitorReasonLine.classList.remove("hidden");
    }
  } catch (err) {
    setCapabilityPillState("unsupported", "Backend unreachable");
    monitorReasonLine.textContent = "Could not reach the monitoring backend.";
    monitorReasonLine.classList.remove("hidden");
    btnToggleMonitoring.disabled = true;
  }
}

function setCapabilityPillState(state, text) {
  adapterCapabilityPill.className = `adapter-capability-pill ${state}`;
  capIndicator.className = `cap-indicator cap-${state}`;
  capText.textContent = text;
}

async function toggleMonitoring() {
  if (!monitorActiveState) {
    btnToggleMonitoring.disabled = true;
    try {
      const res = await fetch("/api/monitor/start", { method: "POST" });
      const data = await res.json();
      if (!data.ok) {
        showToast(data.error || "Could not start monitoring");
        btnToggleMonitoring.disabled = false;
        return;
      }
      monitorActiveState = true;
      monitorToggleLabel.textContent = "STOP MONITORING";
      btnToggleMonitoring.classList.add("monitoring-active");
      btnToggleMonitoring.disabled = false;
      setCapabilityPillState("running", `Monitoring active on ${data.interface}`);
      showToast(`Passive monitoring started on ${data.interface} (no frames transmitted)`);
      if (monitorPollTimer) clearInterval(monitorPollTimer);
      monitorPollTimer = setInterval(pollMonitorEvents, 2000);
    } catch (err) {
      showToast("Monitoring backend unreachable");
      btnToggleMonitoring.disabled = false;
    }
  } else {
    btnToggleMonitoring.disabled = true;
    try {
      await fetch("/api/monitor/stop", { method: "POST" });
    } catch (err) {
      // ignore - we still reflect stopped state locally
    }
    monitorActiveState = false;
    if (monitorPollTimer) {
      clearInterval(monitorPollTimer);
      monitorPollTimer = null;
    }
    monitorToggleLabel.textContent = "START MONITORING";
    btnToggleMonitoring.classList.remove("monitoring-active");
    btnToggleMonitoring.disabled = false;
    setCapabilityPillState("supported", "Monitoring stopped");
    showToast("Passive monitoring stopped; adapter restored");
  }
}

async function pollMonitorEvents() {
  try {
    const res = await fetch(`/api/deauth/events?after=${monitorLastEventId}`);
    if (!res.ok) return;
    const data = await res.json();
    const newEvents = data.events || [];
    if (newEvents.length) {
      // Server returns newest-first; prepend in the same order the table expects.
      newEvents.forEach((ev) => {
        if (ev.id > monitorLastEventId) monitorLastEventId = ev.id;
      });
      defensiveEventsList = [...newEvents, ...defensiveEventsList].slice(0, 200);
      renderDefensiveEventsTable();
      const realDeauth = newEvents.find((e) => e.event_type === "DEAUTH");
      const realDisassoc = newEvents.find((e) => e.event_type === "DISASSOC");
      if (realDeauth || realDisassoc) {
        showToast(`Detected ${newEvents.length} real 802.11 management frame(s)`);
        playSonarPing();
      }
    }
  } catch (err) {
    console.error("Monitor poll error:", err);
  }
}

function exportDefensiveLogCSV() {
  if (defensiveEventsList.length === 0) {
    showToast("No defensive events to export");
    return;
  }
  let csv = "ID,Time,Event Type,Source,Target,Reason Code,Signal,Defense Status\n";
  defensiveEventsList.forEach((ev, idx) => {
    csv += `"${idx + 1}","${ev.time}","${ev.event_type}","${ev.source}","${ev.target}","${ev.reason_code}","${ev.signal_dbm}","${ev.status || ev.pmf}"\n`;
  });
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `defensive_wifi_events_${Date.now()}.csv`;
  a.click();
  URL.revokeObjectURL(url);
  showToast("Exported defensive event log to CSV");
}

// Bind Event Listeners for Deauth Testing & Defensive Monitoring
durationChipsContainer.addEventListener("click", (e) => {
  const chip = e.target.closest(".duration-chip");
  if (chip && !chip.disabled) {
    const sec = chip.getAttribute("data-seconds");
    setTestDuration(sec);
  }
});

durationSelectDropdown.addEventListener("change", (e) => {
  setTestDuration(e.target.value);
});

btnStartDeauth.addEventListener("click", startDeauthSimulation);
btnStopDeauth.addEventListener("click", stopDeauthSimulation);

btnClearDefensiveLog.addEventListener("click", clearDefensiveLog);
btnExportDefensiveLog.addEventListener("click", exportDefensiveLogCSV);
btnToggleMonitoring.addEventListener("click", toggleMonitoring);

// --- Initialization ---
async function init() {
  await fetchNetworkStatus();
  await fetchDevices();
  await fetchDefensiveEvents();
  await checkMonitorCapability();
  updateDeauthTestingTarget();
  setTestDuration(10);
  startAutoScan();
  requestAnimationFrame(drawRadar);
}

window.addEventListener("DOMContentLoaded", init);

