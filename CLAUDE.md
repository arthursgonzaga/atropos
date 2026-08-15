# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Atropos** is an intelligent filament-end sensor system for the Creality Ender 3 V3 SE. When the sensor detects absent filament, an ESP8266 microcontroller fires a webhook to a Homelab Docker microservice, which pauses the print via OctoPrint's REST API and sends a Telegram alert via Synapse.

## Architecture

```
[Makerbase Sensor] → [NodeMCU ESP8266] --HTTP POST--> [Python/Docker on Homelab] --REST--> [OctoPrint]
                                                                                    --Webhook--> [Synapse/Telegram]
```

Two independent codebases live in this repo:

| Directory | Language | Purpose |
|-----------|----------|---------|
| `firmware/` | C++ (Arduino) | NodeMCU ESP8266 firmware |
| `service/` | Python | Docker microservice (FastAPI or Flask) |

## Firmware (NodeMCU / ESP8266)

**Toolchain:** Arduino IDE or PlatformIO

Flash to device:
```bash
# PlatformIO
pio run --target upload

# Arduino IDE: Sketch → Upload (select "NodeMCU 1.0 (ESP-12E Module)")
```

Monitor serial output:
```bash
pio device monitor --baud 115200
```

**Key design constraints:**
- Sensor signal pin: **D5 (GPIO14)** — chosen because it doesn't affect ESP8266 boot state
- Pin mode: `INPUT` (evaluate `INPUT_PULLUP` if signal floats)
- Debounce: filament-absent state must persist for a configurable window (target 2–5 s) before triggering
- Anti-flood: only one webhook POST per absence event; reset only when sensor reports filament present again
- WiFi reconnect must be non-blocking — sensor read loop must never stall waiting for network

**Webhook payload** sent to the Homelab service:
```json
{ "status": "empty", "device": "ender3_v3_se" }
```
Endpoint: `POST http://<HOMELAB_IP>:<PORT>/v1/filament/alert`

## Python Microservice (Docker)

**Dev setup:**
```bash
cd service
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Run locally:
```bash
uvicorn main:app --reload       # FastAPI
# or
flask run                       # Flask
```

Run tests:
```bash
pytest
pytest tests/test_routes.py::test_alert_empty   # single test
```

Build and run container:
```bash
docker build -t atropos-service .
docker run -p 8080:8080 --env-file .env atropos-service
```

**Service responsibilities (in order on alert receipt):**
1. Validate incoming JSON payload; return `422 Unprocessable Entity` on invalid input (FastAPI default)
2. `POST /api/job` to OctoPrint with `{"command": "pause", "action": "pause"}` and `X-Api-Key` header
3. Send Telegram notification via Synapse webhook: `⚠️ Alerta Ender 3 V3 SE: O filamento acabou! Impressão pausada automaticamente.`
4. On OctoPrint `HTTPError` / `ConnectionError`: log full error to container stdout and fire a critical Telegram alert: `🚨 CRÍTICO: Falha ao tentar pausar a Ender 3 V3 SE! O OctoPrint está inacessível.`

**Environment variables required (`.env`):**
- `OCTOPRINT_URL` — base URL of OctoPrint server
- `OCTOPRINT_API_KEY` — application token from OctoPrint
- `SYNAPSE_URL` — base URL of Synapse server (e.g. `http://192.168.1.x:8001`)
- `TELEGRAM_CHAT_ID` — Telegram chat ID for notifications

## Hardware Wiring Reference

| Sensor Pin | NodeMCU Pin | Notes |
|------------|-------------|-------|
| V (or +) | 3V3 | Regulated 3.3 V supply |
| G (or −) | GND | Common ground |
| S (or Out) | D5 (GPIO14) | Data signal, safe for boot |

NodeMCU power: Micro-USB to a standard 5 V source (phone charger or Homelab USB port).
