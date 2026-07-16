#include <Arduino.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>

#include "config.h"

// ── State machine ─────────────────────────────────────────────────────────────
enum class SensorState { PRESENT, ABSENT_CONFIRMING, ABSENT_TRIGGERED };
static SensorState state = SensorState::PRESENT;
static unsigned long absentSince = 0;

// ── WiFi ──────────────────────────────────────────────────────────────────────
static void wifiBegin() {
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    Serial.printf("[WiFi] Connecting to %s ...\n", WIFI_SSID);
}

// ── Webhook ───────────────────────────────────────────────────────────────────
static void sendAlert() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("[WARN] WiFi not connected — skipping alert");
        return;
    }
    WiFiClient wifiClient;
    HTTPClient http;
    if (!http.begin(wifiClient, SERVER_URL)) {
        Serial.println("[ERROR] http.begin() failed");
        return;
    }
    http.addHeader("Content-Type", "application/json");
    const String payload =
        "{\"status\":\"empty\",\"device\":\"" DEVICE_ID "\"}";
    int code = http.POST(payload);
    Serial.printf("[HTTP] POST %s -> %d\n", SERVER_URL, code);
    http.end();
}

// ── Setup ─────────────────────────────────────────────────────────────────────
void setup() {
    Serial.begin(115200);
    // INPUT: float-safe for this sensor; switch to INPUT_PULLUP if signal
    // fluctuates during testing (see config.h SENSOR_PIN comment).
    pinMode(SENSOR_PIN, INPUT);

    wifiBegin();

    // Print IP once at boot (blocking for up to 10 s — only at startup).
    unsigned long t0 = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - t0 < 10000) {
        delay(500);
    }
    if (WiFi.status() == WL_CONNECTED) {
        Serial.printf("[WiFi] Connected: %s\n",
                      WiFi.localIP().toString().c_str());
    } else {
        Serial.println("[WiFi] Not connected at boot — will retry in loop");
    }
}

// ── Loop ──────────────────────────────────────────────────────────────────────
void loop() {
    // Non-blocking reconnect: just re-issues the connect request if dropped.
    if (WiFi.status() != WL_CONNECTED) {
        WiFi.reconnect();
    }

    // HIGH = filament present (sensor closes circuit to 3V3).
    // Invert this condition if your sensor logic is reversed.
    const bool filamentPresent = (digitalRead(SENSOR_PIN) == HIGH);

    switch (state) {
        case SensorState::PRESENT:
            if (!filamentPresent) {
                absentSince = millis();
                state = SensorState::ABSENT_CONFIRMING;
                Serial.println("[SENSOR] Absent — debounce started");
            }
            break;

        case SensorState::ABSENT_CONFIRMING:
            if (filamentPresent) {
                state = SensorState::PRESENT;
                Serial.println("[SENSOR] False alarm — filament present again");
            } else if (millis() - absentSince >= DEBOUNCE_MS) {
                state = SensorState::ABSENT_TRIGGERED;
                Serial.println("[SENSOR] Confirmed absent — sending alert");
                sendAlert();
            }
            break;

        case SensorState::ABSENT_TRIGGERED:
            if (filamentPresent) {
                state = SensorState::PRESENT;
                Serial.println("[SENSOR] Filament reinserted — ready");
            }
            break;
    }

    // 100 ms tick — fine resolution without starving WiFi stack.
    delay(100);
}
