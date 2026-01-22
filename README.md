# 🪰Insect Detection & Analysis System  
### 🚀 Real-Time AI-Powered Insect Monitoring with Raspberry Pi 5, YOLOv8 & LLM 

An end-to-end intelligent platform for **insect detection, tracking, trajectory analysis, and real-time reporting**.  
Built on **Raspberry Pi 5 (16GB)** with **YOLOv8 object detection**, hardware integration (OLED + LEDs), and **LLM-powered insights** for natural-language analysis.  

# 🌍 Overview  

Monitoring insect behavior plays a **critical role** in pest control, agriculture, and ecological research.  
Traditional methods often rely on **manual observations** that are slow, error-prone, and lack the ability to deliver real-time insights.  

The ** Insect Detection & Analysis System** addresses these limitations by combining **computer vision, sensor integration, and AI-driven analysis** into a single intelligent platform.  

Our solution delivers **real-time detection, tracking, trajectory mapping, and analytics** directly on an edge device (Raspberry Pi 5), with seamless visualization and post-processing through an interactive dashboard.  

---

# ✨ Key Features  

✅ **YOLOv8-Powered Real-Time Detection**  
- Detects multiple insect species (fly, cockroach, mosquito, etc.) with high accuracy.  
- Runs directly on Raspberry Pi 5 Bookworm 64-bit OS for fully offline operation.
- Uses **camera calibration and pinhole geometry** to calculate distances in meters.  
- Computes insect **speed (m/s)** by analyzing movement across frames.
  
✅ **Dual-Radar Visualization**  
- Live radar plots showing **instant insect positions**.  
- Historical trajectory tracking with arrows for **movement prediction**.

✅ **Hardware-Integrated Feedback**  
- **OLED Display (SSD1306)** shows nearest insect, distance, and speed.  
- **Traffic-Light LED Indicators** provide instant alerts:  
  - 🟨 Yellow → Cockroach 
  - 🟩 Green → Fly

✅ **Structured JSON Logging**  
- Every session is automatically logged with **timestamped insect data**.  
- Includes entries such as **species, position, trajectory, speed, and nearest encounter**.  
- Ensures **reproducibility and transparency** for future analysis.  

✅ **Interactive Analysis Dashboard (Llm.py)**  
- Built with **Tkinter GUI** for ease of use.  
- Provides:  
  - 📂 **Log Explorer** → Browse detection sessions.  
  - 🎥 **Video Playback** → Replay annotated detection runs with timeline control.  
  - 📊 **Radar & Pie Chart Analysis** → Visualize insect trajectories and proportions.  
  - 🤖 **LLM-Driven Insights** → Ask natural-language questions and get instant answers powered by Ollama’s Phi3:Latest model.
  Goes beyond numbers: provides **interpretations and summaries**.  
- Example questions you can ask:  
  - *“Which insect was most frequent in this session?”*  
  - *“What was the average distance of cockroaches detected?”*  
  - *“Which species moved fastest overall?”*
---

# PROJECT
---
 🛠️ Hardware & Materials
 --
Category	Product Name	Price (INR)	Source	Link
| Category        | Product Name                                      | 
| --------------- | ------------------------------------------------- | 
| Raspberry Pi    | Raspberry Pi 5 - 16GB RAM                         |
| Power / Battery | 18650 Battery Holder Development Board            | 
| Power / Battery | 2x 18650 Lithium Battery Expansion Shield         |
| Wires           | 20CM DuPont Jumper Cable (40PCS)                  | 
| Camera          | Arducam V3 Standard 12MP Camera                   |  
| Display         | 0.96 inch I2C OLED Display Module                 | 
| Prototyping     | MB102 Breadboard (830 Points)                     | 
| LED Module      | LED Traffic Light Signal Module                   |  
| Micro SD Card   | SanDisk 64GB UHS-I Class 10                       |
| Charger         | Official 27W USB-C PD Power Supply                |
| Cables          | Micro HDMI to HDMI, HDMI-VGA Adapter, VGA Cable   |  
| SD Card Reader  | Quantum QHM5570 Micro SD Reader                   |
| Pi Case         | Official Raspberry Pi 5 Case (Red-White)          | 
| Cooler          | Official Raspberry Pi 5 Active Cooler             |  

This project integrates computer vision, hardware displays (OLED + LEDs), radar-style visualization, and natural language analysis to study insect activity in real-time and generate interactive insights.

- Raspberry Pi 5 (16GB) BookWorkm 64-bit → Main processing unit.  
- Camera Module v3 Wide → Connected to Pi’s camera port, captures high-resolution video feed of insects.  
- Distance Calculation → Using pinhole camera geometry formula in background:  
- Speed Detection & Trajectory Prediction → Computed from consecutive positions of bounding boxes.  
- OLED Display (SSD1306, I²C) → Shows:
- Nearest insect species label  
- Distance (in meters)  
- Speed (m/s)  
- Trajectory movement updates  
- LED Indicators (Traffic Light style, GPIO controlled)**:
- Yellow → Cockroach 
- Green → Fly

# System Design:

BreadBoard Design:
--
<img width="1115" height="861" alt="BreadBoard" src="https://github.com/user-attachments/assets/bd1b4223-8290-41d4-87fa-7f2f93a54745" />

Schematic Design:
--
<img width="1046" height="748" alt="image" src="https://github.com/user-attachments/assets/71aa1c98-f870-49c1-93fb-21a8d12c1cc8" />

Connections Overview:
- Raspberry Pi 5 GPIO pins used for LED control.  
- OLED connected via I²C (SDA, SCL).  
- LEDs directly connected to GPIO pins with ground return.  

Pin Mapping Example:
| Component         | Pi GPIO Pin | Notes                    |
|-------------------|-------------|--------------------------|
| OLED SDA          | GPIO2 (SDA) | I²C Data                 |
| OLED SCL          | GPIO3 (SCL) | I²C Clock                |
| Yellow LED (Cockroach) | GPIO27  | Digital output            |
| Green LED (Fly) | GPIO22  | Digital output            |
| GND (OLED + LEDs) | Any GND pin | Shared ground            |

###############################################################################

# 🛠 Hardware Pipeline

### Core

* **Raspberry Pi 5 (BookWorm 64-bit OS)**

  * Runs detection (`insect.py`), logging (JSON), LLM analysis (`llm.py`), and (`oledandled.py`) for Oled and Led.

### Sensors & Outputs

1. **Camera**

   * Raspberry Pi Camera Module v3 Wide-Angle (CSI connector).
   * Connected via PiCamera2 API in code.

2. **OLED Display (SSD1306, I2C)**

   * SCL → GPIO 3 (SCL1)
   * SDA → GPIO 2 (SDA1)
   * VCC → 3.3V
   * GND → GND

3. **LEDs (Fly/Cockroach/Mosquito indicators, GPIO controlled)**

   * Green LED → GPIO 17
   * Yellow LED → GPIO 27
---

# 🔌 Pin Map (BCM Numbering)

| Component    | Pin (BCM) | Physical Pin |
| ------------ | --------- | ------------ |
| OLED SDA     | GPIO 2    | Pin 3        |
| OLED SCL     | GPIO 3    | Pin 5        |
| Green LED    | GPIO 17   | Pin 11       |
| Yellow LED   | GPIO 27   | Pin 13       |
| 3.3V Power   | 3.3V      | Pin 1        |
| 5V Power     | 5V        | Pin 2        |
| Ground       | GND       | Pin 6, 9, 14 |

---

# 🧠 Logic Pipeline

### Step 1: **Video Capture**

* PiCamera2 captures frames at **HIGH\_RES (2304×1296)**.
* Resized to **INFER\_RES (640×640)** for YOLO inference.

### Step 2: **Detection**

* Two YOLO models (`cockroach-n.pt` + `100best.pt`) run sequentially.
* Only valid insects (`fly`, `cockroach`) considered.
* Distance estimated using focal length formula.

### Step 3: **Tracking & Radar**

* Position mapped to **radar (polar coordinates)**.
* Trajectories drawn with `deque(maxlen=30)`.
* Dual-radar: one for **positions**, one for **trajectories**.

### Step 4: **Speed + Nearest Insect**

* Frame-to-frame displacement → speed (m/s).
* System keeps track of **nearest encounter (distance, angle, label)**.

### Step 5: **OLED + LED Output**

* OLED displays:

  * Insect count
  * Nearest insect
  * Distance (m)
  * Speed (m/s)
* LEDs light up based on detected species:

  * Fly → Green
  * Cockroach → Yellow
  * Mosquito (if added) → Red

### Step 6: **Logging**

* JSON (`insect_log2.json`) updated every \~30 frames.
* Stores **entry/exit angles, distances, counts, nearest encounter**.

### Step 7: **LLM Analysis (llm.py)**

* Reads JSON log + video file.
* Provides **UI in Tkinter**:

  * Tab 1: Session text + video playback
  * Tab 2: Radar & Pie chart visualization
  * Tab 3: LLM advice using `ollama (phi3:latest)`

---

# 🖥️ Software Pipeline

1. **`insect.py`**

   * Runs detection + Speed & Distance + radar visualization + OLED/LED output.
   * Saves JSON logs & video.
   * Handles GPIO LED toggling & OLED text display.

2. **`oledandled.py`**
   * takes the data from (`insect.py`) and shows the data on oled display and led of detected insect will light up

4. **`llm.py`**

   * GUI-based analysis after run.
   * Loads session data from JSON.
   * Calls LLM (`phi3:latest`) for human-readable advice.

---

✅ This makes a **closed-loop insect detection system**:

* Detect → Track → Display → Log → Analyze.

---
#  Methodology

<img width="1813" height="889" alt="image" src="https://github.com/user-attachments/assets/0b9e5074-e8de-42db-a756-a7dfc45a64fe" />

# 📊Results
 Detection Example:
--
<img width="745" height="381" alt="image" src="https://github.com/user-attachments/assets/b3b2d8b9-12ef-484d-a1e0-e05c5a70a4b8" />

 Radar Visualization:
---
<img width="804" height="210" alt="image" src="https://github.com/user-attachments/assets/3d744aa1-db5c-4a0b-8a40-db548e48f230" />

 LLM Dashboard:
---
<img width="804" height="895" alt="image" src="https://github.com/user-attachments/assets/1cce96e5-6213-4583-917a-9276697dcb4d" />

 UI : 
--
https://github.com/user-attachments/assets/87de04e1-fa88-4a51-be23-4ed7638838f8

 Current vs Future Accuracy Metrics
---
<img width="1000" height="600" alt="Picture1" src="https://github.com/user-attachments/assets/6123fb14-41c4-4c01-ba3e-af0419c0e850" />

 Model (.pt) Metrics
 ---
 
| Metric    | Best Value | Notes                                 |
| --------- | ---------- | ------------------------------------- |
| Precision | **0.89903**   | Correct positive detections           |
| Recall    | **0.81294**   | Ability to detect all insects         |
| mAP50     | **0.88055**   | Mean Average Precision @ IoU=0.5      |
| mAP50-95  | **0.55907**   | Stricter metric across IoU thresholds |

# 📂 Reproducibility (Setup & Usage)
---
Follow these steps to reproduce the system on your Raspberry Pi or PC:

1️⃣ Installation:
--
Download Raspberry Pi 5 Bookworm 64-bit OS Using Raspberry pi Imager Using USB to Micro SD CARD flash Drive and Download the OS Using the Imager
Then Put the Micro SD card in the Raspberry Pi and Do the required Configuration and setup the Raspberry pi.
Go to Terminal. 
```
sudo apt update && sudo apt upgrade
```
```
sudo raspi-config
```
Then go to Interface option and enable **[I2C]** and **[vnc]** and **[SPI]** and **[SSH]**.
Then enable all the options and press Enter, and Go to terminal and enter:
```
sudo nano /boot/config.txt.
```
On Raspberry Pi OS Bookworm (64-bit) for Raspberry Pi 5, you don’t enable the camera in raspi-config like before.
Instead, you edit the /boot/config.txt file.
Specifically, you need to add this line:
```
camera_auto_detect=1
```
👉 If you want to force the camera, you can also add:
```
dtoverlay=imx708
```
(for the Camera Module 3 / v3 wide camera)
or the correct overlay for your camera module.
Then reboot: s
```
sudo reboot
```
After Rebooting check the camera if its getting recognized or not 
```
rpicam-hello
```
After that, picamera2 should detect your camera.

Clone the repo and install dependencies:
```
cd INSECT-DETECTION-PROJECT
pip install -r requirements.txt
```

Make sure you have:
```
Python 3.11+
Ultralytics (YOLOv8)
OpenCV
Picamera2 (for Raspberry Pi camera)
OLED & GPIO libraries
```

2️⃣ Run Instructions

1.Main detection script (runs detection with radar + OLED/LED control + logging):
```
python insect.py
```

2.Integrated pipeline (UI and LLM):
```
python Llm.py
```

3. Oled and led script ( takes the data and shows the data on oled display and led of detected insect will light up)
```
python oledandled.py
```

4.Ollama Setup

In a separate VSCode terminal:
```
ollama
ollama pull phi3:latest
ollama run phi3:latest # keep it running in the other terminal 
```

✅ Now Llm.py can import ollama directly.

# CODE EXPLANATION:

🚀 **`insect.py` — Real-Time Detection & Logging**
This script (`insect.py`) is the **core pipeline** running on the Raspberry Pi.  
It connects the **camera**, **YOLO models**, **OLED/LED hardware**, and **radar visualization**, while logging all data into **JSON** and saving annotated **video outputs**.

## 1. Imports & Configuration

```python
import time, cv2, numpy as np, math, os, json
from ultralytics import YOLO
from picamera2 import Picamera2
from collections import deque
import oledandled
from datetime import datetime
````

**Libraries & Purpose**

* **OpenCV (cv2)** → video processing (drawing boxes, output video, radar).
* **YOLO (Ultralytics)** → object detection engine.
* **Picamera2** → interface with Pi Camera v3.
* **deque** → store recent trajectory points for arrow drawing.
* **oledandled** → custom module for OLED display + LED GPIO control.
* **json** → structured logging.

---
2.Insect.py — Real-Time Detection & Logging

## 2. Constants Setup

```python
LOW_RES = (640, 480)     # Display resolution
INFER_RES = 640          # YOLOv8 input size
HIGH_RES = (2304,1296)   # Camera resolution
CONF_THRESH = 0.25       # Detection threshold
MIN_BOX_SIZE = 10        # Ignore tiny boxes

CLASS_LABELS = {2: "fly", 3: "Cockroach"}
REAL_WIDTHS_M = {"fly": 0.08, "Cockroach": 0.08}
FOCAL_LENGTH_PIXELS = 1200.0
```

* Defines **species mapping**.
* Sets **real-world insect size**.
* Configures **focal length** for distance formula.

### Radar constants

```python
RADAR_SIZE = 300
RADAR_RANGE_M = 1.0
RADAR_CIRCLE_STEP_M = 0.2
RADAR_CIRCLES = [...]
MAX_TRAIL = 30
```

* Radar display = **300×300 pixels**.
* Detection range = **1 meter**.
* Circles drawn every **0.2m**.

---

## 3. Models & Camera Initialization

```python
MODEL_PATH_1 = "cockroach-n.pt"
MODEL_PATH_2 = "100best.pt"
models = [YOLO(MODEL_PATH_1), YOLO(MODEL_PATH_2)]
```

* Loads **two YOLO models** in parallel to **cross-validate detections**.

```python
picam2 = Picamera2()
cfg = picam2.create_video_configuration(main={"size": HIGH_RES, "format": "RGB888"})
picam2.configure(cfg)
picam2.start()
time.sleep(0.1)
```

* Configures **Pi Camera v3** at high resolution (`2304×1296`).
* Small sleep ensures camera is ready.

---

## 4. Memory and Output Setup

```python
prev_centers, trajectories, speed_tracker = {}, {}, {}
species_summary = {}
nearest_encounter = {"distance_m": inf, "frame": None, "label": None, "angle_deg": None}
```

* **`prev_centers`** → previous positions for speed/trajectory.
* **`species_summary`** → entry/exit distance, angles, counts.
* **`nearest_encounter`** → closest insect ever detected.

```python
out = cv2.VideoWriter("insect_detection_output.avi", fourcc, 30, (640, 780))
json_data = {} or load existing insect_log2.json
```

* Saves **annotated video + radar**.
* Maintains **rolling JSON log**.

---

## 5. Helper Functions

### JSON Handling

```python
def save_json(): ...
def save_species_summary_to_json(): ...
```

* Dumps insect summaries to **`insect_log2.json`**.

### Distance Formula

```python
def get_distance_meters(width_px, real_width_m, focal_px):
    return (real_width_m * focal_px) / width_px
```

* **Pinhole camera model** → object width vs focal length.

### Radar Drawing

* `draw_radar_points()` → draws **current detections** as green dots.
* `draw_radar_trajectories()` → draws **arrows showing last N positions**.

---

## 6. Main Loop

```python
while True:
    frame = picam2.capture_array()
    small_frame = cv2.resize(frame, (INFER_RES, INFER_RES))
```

* Captures **frames continuously**.
* Resizes to `640×640` for YOLO inference.

---

### YOLO Detection

```python
for model in models:
    results = model.predict(...)
    for r in results:
        for box in r.boxes:
            ...
```

* Runs **both YOLO models**.
* Extracts **bounding box, confidence, class ID → species name**.
* Calculates **distance in meters**.

---

### Motion & Speed

```python
if label in speed_tracker:
    speed = displacement / Δt
else:
    speed = 0
```

* Tracks **insect speed (m/s)** between frames.
* Stored in `speed_tracker`.

---

### Summary & Nearest Encounter

* Updates **species\_summary**: entry/exit distance, angles, count.
* Tracks **closest insect** → `nearest_encounter`.

---

### Drawing

* Bounding boxes with **label, distance, speed**.
* Red arrows = **motion direction**.
* Radar = **current vs trajectory**.
* Combined into **final display**.

---

### OLED + LED Control

```python
oledandled.reset_leds()
if "fly": turn on Green
if "cockroach": Yellow
if "mosquito": Red
oledandled.display_on_oled([...])
```

* OLED shows **count, nearest, distance, speed**.
* LEDs light up by insect species.

---

### Logging

* Every **30 frames (\~1 sec)** → snapshot to JSON.
* Saves **video with radar overlay**.

---

## 7. Exit Handling

```python
finally:
    save_species_summary_to_json(species_summary)
    json_data["nearest_encounter"] = nearest_encounter
    save_json()
    out.release()
    picam2.stop()
```

* On exit, final **JSON summary** + **nearest insect** recorded.
* Safely stops **camera** and closes **video writer**.
  
```
Camera (Pi v3) → YOLO Detection → Distance/Speed Estimation 
→ OLED/LED Feedback + Radar Visualization 
→ JSON Logging + Video Output
```

* **Camera** feeds live frames.
* **YOLO** detects insects → bounding boxes + labels.
* **Distance** via pinhole formula.
* **Speed** via displacement/time.
* **OLED & LEDs** → real-time user feedback.
* **Radar** → visual positions + trajectories.
* **Logs + Video** → saved for analysis later.

---

# 📊 **`Llm.py` — Dashboard & LLM Analysis** 
This script (`Llm.py`) is the **post-processing dashboard UI** for the insect detection system.  
It loads logs from the detection pipeline, replays recorded videos, visualizes radar/pie charts, and integrates an LLM for natural language analysis.

---

## 1. Configuration

```python
LLM_MODEL = "phi3:latest"
LOG_PATH = "insect_log2.json"
DEFAULT_VIDEO = "insect_detection_output.avi"
````

* **LLM**: Uses **Ollama’s `phi3:latest`** model.
* **Logs**: Reads structured insect logs from `insect_log2.json`.
* **Default Video**: Uses annotated video generated by `insect.py`.

---

## 2. Utilities

### `ask_phi3_short(prompt)`

* Sends query to the **LLM** with context.
* Returns **short, advisory-style answers**.

### `load_sessions()`

* Reads **JSON logs** from detection pipeline.
* Converts each timestamp into a **session** object with metadata.
* Attaches video reference to each session.

---

## 3. UI Structure

The application is built using **Tkinter** with a **tabbed interface**.

### Root Window

```python
self.tab1, self.tab2, self.tab3 = ...
```

* **Tab 1** → Insects Data (log + video player)
* **Tab 2** → Radar & Pie Chart visualization
* **Tab 3** → LLM Advice & Analysis

---

## 4. Tab 1 — Insects Data

* Displays a **scrollable text log** summarizing insect detections.
* **Dropdown menu** allows switching between sessions.
* Embedded **video player** for replay of recorded detection output:

  * Play, Pause, Seek slider, and Open Video options available.

---

## 5. Tab 2 — Radar & Pie Chart

* **Radar Plot (Polar Graph)**:

  * Normalizes angles (0–180° → -90° to 90°).
  * Distance rings every 0.2 m.
  * Entry points = circles, Exit points = triangles.
  * Lines drawn between entry and exit positions.

* **Pie Chart**:

  * Displays **insect proportions** within the session.
  * Uses color-coded slices for each insect class.

---

## 6. Tab 3 — LLM Advice

* Provides **text box + input field** for natural queries.
* Example: *“Which insect was most frequent overall?”*
* Script builds **context**:

  * Current session data
  * Overall summary across all sessions
* Sends structured JSON → **Ollama LLM**.
* Displays natural-language **AI response** in the advice box.

---

## 7. Flow of Operation

1. **User launches dashboard (`python Llm.py`)**
2. **Loads sessions** from `insect_log2.json`
3. **Chooses session** (via dropdown)
4. **Can perform:**

   * Replay detection video
   * View radar + pie chart visualization
   * Ask LLM natural questions about detections
---

---

# 💡 **`oledandled.py` — OLED Display & LED Control**

This module provides **real-time hardware feedback** for the insect detection system.
It manages **traffic light LEDs** for insect alerts and an **OLED screen** for displaying status information.

---

## 1. Configuration

```python
# LED pins
RED_LED = 17
YELLOW_LED = 27
GREEN_LED = 22
```

* **GPIO Pins**:

  * **Red (17)** → Mosquito alert
  * **Yellow (27)** → Cockroach alert
  * **Green (22)** → Fly alert

---

## 2. Dependencies

```python
import lgpio
import board
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
```

* **lgpio** → Controls GPIO pins for LEDs.
* **board, busio** → Handles I2C bus for OLED.
* **PIL (Pillow)** → Renders text onto OLED screen.
* **adafruit\_ssd1306** → Driver for SSD1306-based OLED displays.

If OLED library is missing, the script **disables OLED gracefully**.

---

## 3. LED Control

### Initialization

```python
chip = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(chip, RED_LED)
lgpio.gpio_claim_output(chip, YELLOW_LED)
lgpio.gpio_claim_output(chip, GREEN_LED)
```

* Opens GPIO chip safely.
* Claims control of the three LED pins.
* If GPIO is already in use, it logs a warning and skips LED setup.

### Reset Function

```python
def reset_leds():
    if chip:
        lgpio.gpio_write(chip, RED_LED, 0)
        lgpio.gpio_write(chip, YELLOW_LED, 0)
        lgpio.gpio_write(chip, GREEN_LED, 0)
```

* Ensures all LEDs are **turned off** before shutdown.

---

## 4. OLED Setup

### Initialization

```python
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
oled.fill(0)
oled.show()
```

* Connects to OLED via **I2C**.
* Initializes display resolution → **128x64 pixels**.
* Clears screen before first use.
* If OLED is missing or I2C fails, the module disables OLED gracefully.

---

## 5. Display Function

```python
def display_on_oled(lines):
    if oled:
        oled.fill(0)
        image = Image.new("1", (oled.width, oled.height))
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        for i, line in enumerate(lines[:5]):
            draw.text((0, i * 12), line, font=font, fill=255)
        oled.image(image)
        oled.show()
    else:
        print("OLED disabled, cannot display:", lines)
```

* Clears previous content.
* Renders up to **5 lines of text** (12 px spacing).
* Updates the OLED with insect info:

  * Species name
  * Distance from camera
  * Speed/Trajectory

If OLED is unavailable, prints to console instead.

---

## 6. Cleanup Function

```python
def cleanup():
    reset_leds()
    if chip:
        lgpio.gpiochip_close(chip)
    if oled:
        oled.fill(0)
        oled.show()
```

* **Turns off LEDs**
* **Releases GPIO resources**
* **Clears OLED screen**
* Ensures safe shutdown without leaving LEDs or OLED active

---

## 7. Flow of Operation

1. **Detection system (`insect.py`) calls functions here**

   * `display_on_oled([f"{label}", f"Dist: {d:.2f}m"])`
   * Sets LED based on insect type
2. OLED shows **live stats** (species + distance + speed).
3. LEDs provide **instant visual alert**.
4. `cleanup()` is triggered on shutdown to reset hardware.

---
