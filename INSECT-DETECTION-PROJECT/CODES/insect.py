import time
import cv2
import numpy as np
from ultralytics import YOLO
from picamera2 import Picamera2
import math
from collections import deque
import oledandled
import os
import json
from datetime import datetime

# ==========================
# CONFIG
# ==========================
LOW_RES = (640, 480)
INFER_RES = 640
HIGH_RES = (2304,1296)
CONF_THRESH = 0.25
MIN_BOX_SIZE = 10

CLASS_LABELS = {2: "fly", 3: "Cockroach"}
REAL_WIDTHS_M = {"fly": 0.08, "Cockroach": 0.08}
FOCAL_LENGTH_PIXELS = 1200.0

# Radar
RADAR_SIZE = 300
RADAR_RANGE_M = 1.0
RADAR_CIRCLE_STEP_M = 0.2
RADAR_CIRCLES = [round(i, 1) for i in np.arange(RADAR_RANGE_M, 0, -RADAR_CIRCLE_STEP_M)]
MAX_TRAIL = 30

# Models
MODEL_PATH_1 = "cockroach-n.pt"
MODEL_PATH_2 = "100best.pt"
models = [YOLO(MODEL_PATH_1), YOLO(MODEL_PATH_2)]

# Camera setup
picam2 = Picamera2()
cfg = picam2.create_video_configuration(main={"size": HIGH_RES, "format": "RGB888"})
picam2.configure(cfg)
picam2.start()
time.sleep(0.1)

# Memory
prev_centers = {}
trajectories = {}
prev_time = 0
speed_tracker = {}
species_summary = {}  # Track overall summary per species
nearest_encounter = {"distance_m": float('inf'), "frame": None, "label": None, "angle_deg": None}

# Video output
VIDEO_FPS = 30
frame_interval = 1.0 / VIDEO_FPS
output_filename = "insect_detection_output.avi"
fourcc = cv2.VideoWriter_fourcc(*'XVID')
frame_width = LOW_RES[0]
frame_height = LOW_RES[1] + RADAR_SIZE
out = cv2.VideoWriter(output_filename, fourcc, VIDEO_FPS, (frame_width, frame_height))

# JSON logging
json_filename = "insect_log2.json"
if os.path.exists(json_filename):
    try:
        with open(json_filename, "r") as f:
            json_data = json.load(f)
        if not isinstance(json_data, dict):
            json_data = {}
    except Exception:
        json_data = {}
else:
    json_data = {}

frame_id = 0

# ==========================
# FUNCTIONS
# ==========================
def save_json():
    """Save JSON file safely"""
    try:
        with open(json_filename, "w") as f:
            json.dump(json_data, f, indent=4)
    except Exception as e:
        print("JSON save error:", e)

def get_distance_meters(width_px: float, real_width_m: float, focal_px: float) -> float:
    if width_px <= 0 or focal_px <= 0 or real_width_m <= 0:
        return 0.0
    return (real_width_m * focal_px) / width_px

def draw_radar_points(radar_data, radar_size):
    radar = np.zeros((radar_size, radar_size, 3), dtype=np.uint8)
    cx, cy = radar_size // 2, radar_size // 2
    max_r = radar_size // 2 - 20
    for r_m in RADAR_CIRCLES:
        r_px = int((r_m / RADAR_RANGE_M) * max_r)
        cv2.circle(radar, (cx, cy), r_px, (30, 80, 30), 1)
        cv2.putText(radar, f"{r_m:.1f}m", (cx+5, cy-r_px+10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100,200,100), 1)
    for deg in range(0, 360, 45):
        rad = math.radians(deg)
        x, y = int(cx + max_r * math.cos(rad)), int(cy - max_r * math.sin(rad))
        cv2.line(radar, (cx, cy), (x, y), (40,40,40), 1)
    for norm_x, distance_m, label in radar_data:
        if label not in CLASS_LABELS.values(): continue
        r_px = int(min(max_r, (distance_m / RADAR_RANGE_M) * max_r))
        x = int(cx + norm_x * max_r)
        y = int(cy - r_px)
        cv2.circle(radar, (x, y), 5, (0,200,0), -1)
        cv2.putText(radar, label[0], (x+6, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,255,0), 1)
    return radar

def draw_radar_trajectories(trajectories, radar_size):
    radar = np.zeros((radar_size, radar_size, 3), dtype=np.uint8)
    cx, cy = radar_size // 2, radar_size // 2
    max_r = radar_size // 2 - 20
    for r_m in RADAR_CIRCLES:
        r_px = int((r_m / RADAR_RANGE_M) * max_r)
        cv2.circle(radar, (cx, cy), r_px, (30, 80, 30), 1)
        cv2.putText(radar, f"{r_m:.1f}m", (cx+5, cy-r_px+10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100,200,100), 1)
    for deg in range(0, 360, 45):
        rad = math.radians(deg)
        x, y = int(cx + max_r * math.cos(rad)), int(cy - max_r * math.sin(rad))
        cv2.line(radar, (cx, cy), (x, y), (40,40,40), 1)
    for label, traj in trajectories.items():
        if label not in CLASS_LABELS.values(): continue
        if len(traj) >= 2:
            cv2.arrowedLine(radar, tuple(traj[-2]), tuple(traj[-1]),
                            (0,0,255), 2, tipLength=0.3)
    return radar

def save_species_summary_to_json(species_summary):
    """Save snapshot of current species summary"""
    timestamp = datetime.now().isoformat()
    json_data[timestamp] = {}
    for label, info in species_summary.items():
        json_data[timestamp][label] = {
            "start_distance_m": round(info.get("entry_distance_m",0), 2),
            "end_distance_m": round(info.get("exit_distance_m",0), 2),
            "start_angle_deg": round(info.get("entry_angle_deg",0), 1),
            "end_angle_deg": round(info.get("exit_angle_deg",0), 1),
            "count": info.get("count",0)
        }
    save_json()


# ==========================
# MAIN LOOP
# ==========================
try:
    while True:
        frame = picam2.capture_array()
        if frame is None: continue
        small_frame = cv2.resize(frame, (INFER_RES, INFER_RES))
        detections = []

        # YOLO predictions
        for model in models:
            results = model.predict(small_frame, imgsz=INFER_RES, conf=CONF_THRESH, verbose=False)
            for r in results:
                for box in r.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                    scale_x = frame.shape[1] / INFER_RES
                    scale_y = frame.shape[0] / INFER_RES
                    x1, x2 = int(x1*scale_x), int(x2*scale_x)
                    y1, y2 = int(y1*scale_y), int(y2*scale_y)
                    w, h = x2-x1, y2-y1
                    if w<MIN_BOX_SIZE or h<MIN_BOX_SIZE: continue

                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0].cpu())
                    label = CLASS_LABELS.get(cls_id, r.names.get(cls_id, f"Class {cls_id}"))
                    if label not in CLASS_LABELS.values(): continue

                    real_w_m = REAL_WIDTHS_M.get(label, 0.01)
                    width_px = float(w)
                    distance_m = get_distance_meters(width_px, real_w_m, FOCAL_LENGTH_PIXELS)

                    detections.append((x1, y1, x2, y2, label, distance_m, conf))

        radar_points = []
        current_labels = set()
        now = time.time()

        for (x1, y1, x2, y2, label, distance_m, conf) in detections:
            current_labels.add(label)
            cx, cy = (x1+x2)//2, (y1+y2)//2

            # Angle 0-180 degrees (left to right)
            angle_deg = ((cx / frame.shape[1]) * 180.0)

            # Speed calculation
            if label in speed_tracker:
                px, py, pt, prev_speed = speed_tracker[label]
                dt = now - pt
                if dt>0:
                    dist_px = np.sqrt((cx-px)**2 + (cy-py)**2)
                    speed_mps = (dist_px*0.02)/dt
                    speed_tracker[label]=(cx,cy,now,speed_mps)
            else:
                speed_tracker[label]=(cx,cy,now,0.0)
            speed_mps = speed_tracker[label][3]

            # Species summary update
            if label not in species_summary:
                species_summary[label] = {
                    "count": 0,
                    "entry_angle_deg": round(angle_deg, 1),
                    "exit_angle_deg": round(angle_deg, 1),
                    "entry_distance_m": round(distance_m, 2),
                    "exit_distance_m": round(distance_m, 2)
                }
            species_summary[label]["count"] += 1
            species_summary[label]["exit_angle_deg"] = round(angle_deg, 1)
            species_summary[label]["exit_distance_m"] = round(distance_m, 2)

            # Nearest encounter
            if distance_m < nearest_encounter["distance_m"]:
                nearest_encounter.update({
                    "distance_m": round(distance_m,3),
                    "frame": frame_id,
                    "label": label,
                    "angle_deg": round(angle_deg,1)
                })

            # Draw boxes and arrows
            cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.putText(frame,f"{label} {distance_m:.2f}m {speed_mps:.2f}m/s",(x1,max(y1-5,15)),
                        cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)
            if label in prev_centers:
                prev_cx, prev_cy = prev_centers[label]
                dx, dy = cx-prev_cx, cy-prev_cy
                length = int(np.sqrt(dx**2+dy**2))
                if length>0:
                    scale=40
                    dir_x=int((dx/length)*scale)
                    dir_y=int((dy/length)*scale)
                    cv2.arrowedLine(frame,(cx,cy),(cx+dir_x,cy+dir_y),(0,0,255),2,tipLength=0.4)
            prev_centers[label]=(cx,cy)

            norm_x = (cx/frame.shape[1])-0.5
            radar_points.append((norm_x,distance_m,label))
            if label not in trajectories: trajectories[label]=deque(maxlen=MAX_TRAIL)
            r_px=int(min((distance_m/RADAR_RANGE_M)*(RADAR_SIZE//2-20), RADAR_SIZE//2-20))
            x=int(RADAR_SIZE//2 + norm_x*(RADAR_SIZE//2-20))
            y=int(RADAR_SIZE//2 - r_px)
            trajectories[label].append((x,y))

        # Remove missing insects
        for lbl in list(trajectories.keys()):
            if lbl not in current_labels:
                trajectories.pop(lbl,None)
                prev_centers.pop(lbl,None)
                speed_tracker.pop(lbl,None)

        # OLED/LED display
        try:
            oledandled.reset_leds()
            if detections:
                _,_,_,_,first_label,_,_=detections[0]
                cls_name=first_label.lower()
                if 'fly' in cls_name: oledandled.lgpio.gpio_write(oledandled.chip, oledandled.GREEN_LED,1)
                elif 'cockroach' in cls_name: oledandled.lgpio.gpio_write(oledandled.chip, oledandled.YELLOW_LED,1)

            total_insects=len(detections)
            nearest_track=min(detections,key=lambda d:d[5]) if detections else None
            if nearest_track:
                x1,y1,x2,y2,nearest_label,nearest_distance, _=nearest_track
                nearest_speed_mps=0.0
                if nearest_label in speed_tracker: nearest_speed_mps=speed_tracker[nearest_label][3]
                oled_lines=[
                    f"Insects: {total_insects}",
                    f"Nearest: {nearest_label}",
                    f"Distance: {nearest_distance:.2f}m",
                    f"Speed: {nearest_speed_mps:.2f} m/s"
                ]
                oledandled.display_on_oled(oled_lines)
        except Exception as e:
            print("OLED/LED error:", e)

        # Radar drawing
        radar1=draw_radar_points(radar_points,RADAR_SIZE)
        radar2=draw_radar_trajectories(trajectories,RADAR_SIZE)
        radar_combined=np.hstack([radar1,radar2])
        disp=cv2.resize(frame,LOW_RES)
        radar_rs=cv2.resize(radar_combined,(LOW_RES[0],RADAR_SIZE))
        final_display=np.vstack([disp,radar_rs])

        out.write(final_display)
        cv2.imshow("Insect Detection + Dual Radar",final_display)

        frame_id+=1
        # Save JSON every 30 frames (~1 sec)
        if frame_id % 30 == 0:
            save_species_summary_to_json(species_summary)

        curr_time = time.time()
        fps = 1/(curr_time-prev_time) if prev_time else 0
        prev_time = curr_time
        print(f"FPS: {fps:.1f}", end="\r")

        if cv2.waitKey(1) & 0xFF == ord("q"): break

finally:
    # Save final summary
    save_species_summary_to_json(species_summary)
    json_data["nearest_encounter"] = nearest_encounter
    save_json()
    cv2.destroyAllWindows()
    picam2.stop()
    out.release()
