# 📡 2D Radar Scanning & Collision Avoidance System

A compact embedded-systems prototype that combines an Arduino-driven ultrasonic radar with a custom Python SCADA / HMI panel to provide real-time obstacle detection, two-tier alarm annunciation, and remote operator control for a small autonomous or semi-autonomous vehicle (AGV).

---

## 📸 System Previews

<details open>
  <summary><b>🖥️ 1. SCADA Radar HMI (Click to expand)</b></summary>
  <br>

  * **Normal Scan (no obstacles):**
    > _Add a screenshot here, e.g. `assets/normal.png`_

  * **Warning Zone:**
    > _Add a screenshot here, e.g. `assets/warning.png`_

  * **Danger Alarm:**
    > _Add a screenshot here, e.g. `assets/danger.png`_

</details>

<details>
  <summary><b>⚙️ 2. Hardware Prototype (Click to expand)</b></summary>
  <br>

  > _Add a photo of the Arduino + servo + HC-SR04 rig here, e.g. `assets/hardware.jpeg`_

</details>

> Replace the placeholders above with real screenshots or a short screen-recording once you've captured them.

---

## 🤖 Problem Statement & Motivation

**The Problem:** Automated Guided Vehicles (AGVs) and mobile robots operating on a factory floor or warehouse aisle share space with people, shelving, and other equipment. A vehicle that has no continuous, real-time awareness of what is directly ahead of it risks collisions — damaging goods, halting production, or injuring nearby workers.

**The Approach:** This prototype demonstrates the core building block of a collision-avoidance system: a servo-mounted ultrasonic sensor continuously sweeps a 180° arc ahead of the vehicle, classifies whatever it detects into **NORMAL / WARNING / DANGER** zones, drives local alarms accordingly, and automatically halts the scanning mechanism when an obstacle is critically close — while streaming every reading to a SCADA-style dashboard so an operator can supervise the vehicle remotely.

---

## ✨ Core Features & Engineering Logic

* **180° Radar Sweep:** A servo-mounted HC-SR04 ultrasonic sensor sweeps from 15° to 165° in 2° steps, building a continuously updating distance map of the space ahead of the vehicle.
* **Noise-Resistant Distance Sampling:** Each angle is sampled three times and passed through a median-of-three filter, so a single erratic ultrasonic echo can't trigger a false alarm.
* **Operator-Adjustable Sensitivity:** A potentiometer lets a technician tune the DANGER threshold live (10–40 cm); the WARNING threshold is automatically offset +20 cm above it — no firmware reflash needed to recalibrate for a new environment.
* **Two-Tier Alarm Annunciation:** Independent Red/Yellow LEDs plus a PWM-driven buzzer (different intensity for WARNING vs. DANGER) give both a visual and audible status at a glance.
* **Automatic Safety Interlock:** When an obstacle enters the DANGER zone, the sweep motor stops moving — mirroring how a real AGV should freeze rather than keep operating blindly into a hazard.
* **Remote Work / Repair Mode:** From the SCADA panel, an operator can switch the system into **Repair Mode**. Alarms still trigger exactly as normal when thresholds are breached, but the sweep motor keeps moving instead of freezing, letting a technician safely test and calibrate the sensor without the safety interlock blocking every sweep.
* **Remote Mute:** The buzzer can be muted or unmuted directly from the SCADA panel without touching the hardware, with the mute state echoed back over serial for confirmation.
* **Live SCADA Radar HMI:** A dark, industrial-styled `matplotlib` dashboard renders the scan as an animated 180° polar radar — color-coded green / yellow / red per distance zone — with a live sweep line, an on-panel status readout, and a stripped-down interface (no default plot toolbar) for a cleaner control-room feel.

---

## 🧮 Mathematical Modeling & Signal Processing

* **Time-of-Flight Distance Measurement:** Distance is derived from the ultrasonic echo's round-trip time using `distance = duration × 0.034 / 2`, based on the speed of sound (~340 m/s), halved to account for the round trip.
* **Median-of-3 Filtering:** Three consecutive raw readings are taken per angle; the algorithm keeps the one bounded between the other two, rejecting single-sample spikes caused by acoustic interference or edge reflections.
* **Linear Threshold Mapping:** The potentiometer's raw 10-bit ADC value (0–1023) is linearly mapped to a 10–40 cm DANGER threshold; the WARNING threshold is derived as `DANGER + 20 cm`, keeping a constant safety margin between the two alarm tiers at any sensitivity setting.

---

## 🧰 System Architecture

### Hardware (Field Instrument)
* **Controller:** Arduino Uno (C++ firmware)
* **Distance Sensor:** HC-SR04 ultrasonic sensor — Trig: `D9`, Echo: `D10`
* **Scanning Mechanism:** SG90 servo motor (`D6`), 15°–165° sweep
* **Calibration:** Potentiometer on `A0` for live threshold tuning
* **Annunciators:** Red LED (`D2`), Yellow LED (`D3`), piezo buzzer (`D5`, PWM-driven)

### Software (Control Room)
* **SCADA Backend:** Python 3 with `pyserial` for serial communication
* **HMI Frontend:** `matplotlib` + `numpy` — animated polar radar plot, custom `Button` widgets for Mute and Work/Repair mode, dark industrial color theme
* **Communication Protocol:** plain-text CSV over serial @ 9600 baud (see below)

---

## 🔌 Serial Communication Protocol

**Arduino → SCADA** (sent once per sweep step):
| Field | Meaning |
|---|---|
| `angle` | Current servo angle (15°–165°) |
| `distance` | Filtered distance in cm (`999.0` = no echo / out of range) |
| `state` | `0` = NORMAL, `1` = WARNING, `2` = DANGER |
| `mute` | `0` = buzzer active, `1` = buzzer muted |

**SCADA → Arduino** (single-character commands):
| Command | Effect |
|---|---|
| `M` | Mute the buzzer |
| `U` | Unmute the buzzer |
| `R` | Enter Repair Mode — alarms stay active, sweep never freezes |
| `N` | Return to Work Mode — sweep freezes automatically on DANGER |

---

## 🚀 Getting Started

1. Flash the Arduino sketch to your Arduino Uno.
2. Wire the HC-SR04, SG90 servo, LEDs, buzzer, and potentiometer according to the pin map above.
3. Install the Python dependencies:
   ```
   pip install pyserial numpy matplotlib
   ```
4. Set `SERIAL_PORT` in the Python script to match your Arduino's serial port.
5. Run the SCADA panel:
   ```
   python scada_panel.py
   ```

---

## 🛣️ Possible Next Steps

* Log scan history and alarm events to a CSV file for post-incident analysis.
* Read back and display the confirmed mute/repair state from the Arduino for a fully closed control loop.
* Add a second sensor or continuous rotation for 360° perimeter coverage.
* Integrate motor/drive control so the vehicle itself (not just the sensor sweep) reacts to DANGER events.
