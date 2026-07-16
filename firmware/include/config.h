#pragma once

// ── WiFi ─────────────────────────────────────────────────────────────────────
#define WIFI_SSID "your-ssid"
#define WIFI_PASS "your-password"

// ── Homelab service endpoint ──────────────────────────────────────────────────
// Full URL including port and path
#define SERVER_URL "http://192.168.1.x:8080/v1/filament/alert"

// ── Hardware ──────────────────────────────────────────────────────────────────
// D5 = GPIO14: safe during boot (no boot-mode effect)
#define SENSOR_PIN D5

// ── Debounce ──────────────────────────────────────────────────────────────────
// Filament must be absent this many milliseconds before triggering alert.
// 3000 ms = 3 seconds (adjust between 2000–5000 if needed)
#define DEBOUNCE_MS 3000UL

// ── Device identifier sent in webhook payload ─────────────────────────────────
#define DEVICE_ID "ender3_v3_se"
