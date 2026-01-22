import os
import json
import cv2
import math
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
from PIL import Image, ImageTk
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ollama

# ----------------------------
# CONFIG
# ----------------------------
LLM_MODEL = "phi3:latest"
LOG_PATH = "insect_log2.json"
DEFAULT_VIDEO = "/home/aaswat/insects/insect_detection_output.avi"

insect_colors = {"Mosquito": "#e74c3c", "Fly": "#2ecc71", "Cockroach": "#f1c40f"}

# ----------------------------
# Utilities
# ----------------------------
def ask_phi3_short(prompt: str) -> str:
    try:
        messages = [
            {"role": "system",
             "content": "You are an insect analysis assistant. Keep answers simple, accurate, and provide advice in [brackets]."},
            {"role": "user", "content": prompt}
        ]
        res = ollama.chat(model=LLM_MODEL, messages=messages)
        return res["message"]["content"].strip()
    except Exception as e:
        return f"[Ollama error: {e}]"

def load_sessions():
    if not os.path.exists(LOG_PATH):
        return []
    try:
        with open(LOG_PATH, "r") as f:
            raw = json.load(f)
        # Convert each timestamp key into a session dict
        sessions = []
        for ts, data in raw.items():
            sess = data.copy()
            sess["session_info"] = {"session_id": ts, "timestamp": ts}
            sess["video_reference"] = DEFAULT_VIDEO  # or set real video path if stored
            sessions.append(sess)
        return sessions
    except Exception as e:
        print("JSON load error:", e)
        return []


# ----------------------------
# Compute angles and distances
# ----------------------------
def compute_angles_and_distances(raw_detections, video_path):
    out = {}
    for label, info in raw_detections.items():
        if not isinstance(info, dict) or label in ("session_info","video_reference"):
            continue
        out[label] = {
            "entry_angle_deg": info.get("start_angle_deg",0),
            "exit_angle_deg": info.get("end_angle_deg",0),
            "entry_dist_m": info.get("start_distance_m",0),
            "exit_dist_m": info.get("end_distance_m",0)
        }
    return out

# ----------------------------
# Main UI
# ----------------------------
class InsectPopup(tk.Toplevel):
    def __init__(self,parent,sessions):
        super().__init__(parent)
        self.title("Insect Detection Analysis")
        self.geometry("1600x1000")
        self.configure(bg="#f0f2f5")
        self.sessions = sessions
        self.current_session = sessions[-1] if sessions else {}
        self.video_cap = None
        self.video_running = False

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook.Tab", font=("Segoe UI", 12, "bold"), padding=[20,10], background="#34495e", foreground="white")
        style.map("TNotebook.Tab", background=[("selected","#1abc9c")], foreground=[("selected","white")])

        tab_control = ttk.Notebook(self)
        self.tab1,self.tab2,self.tab3 = ttk.Frame(tab_control),ttk.Frame(tab_control),ttk.Frame(tab_control)
        tab_control.add(self.tab1, text="🪰 Insects Data")
        tab_control.add(self.tab2, text="📊 Radar & Pie")
        tab_control.add(self.tab3, text="💡 LLM Advice")
        tab_control.pack(expand=1,fill="both",padx=10,pady=10)

        self.positions_info = compute_angles_and_distances(
            self.current_session,
            self.current_session.get("video_reference", DEFAULT_VIDEO)
        )

        self.build_tab1()
        self.build_tab2()
        self.build_tab3()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------------- TAB 1 ----------------
    def build_tab1(self):
        canvas = tk.Canvas(self.tab1,bg="#f0f2f5")
        scrollbar = tk.Scrollbar(self.tab1, orient="vertical",command=canvas.yview)
        scroll_frame = tk.Frame(canvas,bg="#f0f2f5")
        scroll_frame.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left",fill="both",expand=True)
        scrollbar.pack(side="right",fill="y")

        sess_frame = tk.Frame(scroll_frame,bg="#f0f2f5"); sess_frame.pack(fill=tk.X,pady=5)
        sess_ids = []
        for i,s in enumerate(self.sessions):
            sid = s.get("session_info",{}).get("session_id", f"Session {i}")
            sess_ids.append(sid)
        self.session_map = {sess_ids[i]:self.sessions[i] for i in range(len(sess_ids))}
        self.session_var = tk.StringVar(value=sess_ids[-1] if sess_ids else "")
        ttk.Label(sess_frame,text="Select Session:", font=("Segoe UI",12,"bold")).pack(side=tk.LEFT,padx=5)
        sess_menu = ttk.Combobox(sess_frame,values=sess_ids,textvariable=self.session_var,state="readonly", font=("Segoe UI",12))
        sess_menu.pack(side=tk.LEFT,padx=5)
        sess_menu.bind("<<ComboboxSelected>>", self.change_session)

        self.text_area = scrolledtext.ScrolledText(scroll_frame, wrap=tk.WORD,width=120,height=22,
                                                   font=("Segoe UI",11), bg="#1e1e2f", fg="white")
        self.text_area.pack(fill=tk.BOTH, expand=True,padx=15,pady=10)
        self.update_text_area()

        video_frame = tk.Frame(scroll_frame,bg="black",width=900,height=450); video_frame.pack(padx=15,pady=10)
        self.video_label = tk.Label(video_frame,bg="black",width=900,height=450)
        self.video_label.pack()

        ctrl = tk.Frame(scroll_frame,bg="#f0f2f5"); ctrl.pack(pady=5)
        self.play_btn = tk.Button(ctrl, text="▶️ Play", bg="#1abc9c", fg="white", font=("Segoe UI",12), command=self.play_video)
        self.play_btn.pack(side=tk.LEFT,padx=5)
        self.pause_btn = tk.Button(ctrl, text="⏸️ Pause", bg="#e67e22", fg="white", font=("Segoe UI",12), command=self.pause_video)
        self.pause_btn.pack(side=tk.LEFT,padx=5)
        self.open_btn = tk.Button(ctrl, text="📂 Open Video", bg="#3498db", fg="white", font=("Segoe UI",12), command=self.open_video)
        self.open_btn.pack(side=tk.LEFT,padx=5)

        self.slider = tk.Scale(scroll_frame,from_=0,to=100,orient=tk.HORIZONTAL,length=900,command=self.seek_video, bg="#f0f2f5", fg="#34495e")
        self.slider.pack(pady=5)

        self.start_video(self.current_session.get("video_reference", DEFAULT_VIDEO))

    # ---------------- Video ----------------
    def start_video(self,video_path):
        self.release_video()
        if not os.path.exists(video_path):
            self.video_label.config(text="⚠️ Video file not found", fg="red"); return
        self.video_cap = cv2.VideoCapture(video_path)
        if not self.video_cap.isOpened():
            self.video_label.config(text="⚠️ Could not open video", fg="red"); return
        self.video_running = True
        self.total_frames = int(self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.slider.config(to=self.total_frames-1)
        self.update_video_frame()

    def update_video_frame(self):
        if self.video_cap and self.video_running:
            ret, frame = self.video_cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                w,h = self.video_label.winfo_width(), self.video_label.winfo_height()
                frame = cv2.resize(frame,(w,h))
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.config(image=imgtk)
                self.slider.set(int(self.video_cap.get(cv2.CAP_PROP_POS_FRAMES)))
                self.after(30,self.update_video_frame)
            else:
                self.video_cap.set(cv2.CAP_PROP_POS_FRAMES,0)
                self.video_running = False

    def play_video(self): self.video_running=True; self.update_video_frame()
    def pause_video(self): self.video_running=False
    def seek_video(self,val):
        if self.video_cap:
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES,int(val))
    def open_video(self):
        path = filedialog.askopenfilename(filetypes=[("Video files","*.mp4 *.avi *.mov *.mkv")])
        if path: self.start_video(path)
    def release_video(self):
        self.video_running=False
        if self.video_cap: self.video_cap.release(); self.video_cap=None

    # ----------------------------
    # TAB 2 - Radar & Pie
    # ----------------------------
    def build_tab2(self):
        frame = tk.Frame(self.tab2,bg="#f0f2f5"); frame.pack(fill=tk.BOTH,expand=True,padx=15,pady=15)
        ttk.Button(frame,text="Update Radar/Pie",command=self.plot_graph).pack(pady=5)
        self.canvas_frame = tk.Frame(frame,bg="#ffffff",relief="solid",bd=1); self.canvas_frame.pack(fill=tk.BOTH,expand=True,pady=10)
        self.plot_graph()

    def plot_graph(self):
        for w in self.canvas_frame.winfo_children(): 
            w.destroy()

        # --- Pie Data ---
        per_label = {k:v.get("count",0) for k,v in self.current_session.items() if isinstance(v,dict) and k!="nearest"}
        labels, counts = list(per_label.keys()), list(per_label.values())
        if not labels: labels=["None"]; counts=[0]

        fig = plt.Figure(figsize=(16,6))

        # --- Radar Chart (180° FOV, 0° center, max 1.5 m) ---
        ax1 = fig.add_subplot(121, polar=True)
        ax1.set_theta_zero_location("N")
        ax1.set_theta_direction(-1)  # clockwise
        ax1.set_thetalim(math.radians(-90), math.radians(90))  # left=-90°, right=90°

        # Distance rings every 0.2 m
        distance_rings = [0.2,0.4,0.6,0.8,1.0,1.2,1.4,1.5]
        ax1.set_rlim(0, 1.5)
        ax1.set_rticks(distance_rings)
        ax1.grid(True, linestyle='--', linewidth=0.7)

        for label,pos in self.positions_info.items():
            color = insect_colors.get(label,"blue")
            entry_deg = pos["entry_angle_deg"]
            exit_deg = pos["exit_angle_deg"]
            entry_dist = pos["entry_dist_m"]
            exit_dist = pos["exit_dist_m"]

            # Normalize angles: convert 0-180° → -90° to 90°
            def normalize_angle(a):
                a = a % 360
                if a > 180: a -= 360
                return a - 180 if a > 90 else a  # shift to -90 → 90 range

            entry_rad = math.radians(normalize_angle(entry_deg))
            exit_rad = math.radians(normalize_angle(exit_deg))

            # Draw line between entry → exit
            ax1.plot([entry_rad, exit_rad], [entry_dist, exit_dist], color=color, lw=2)

            # Draw entry point (circle) and exit point (triangle) 
            ax1.scatter([entry_rad], [entry_dist], color=color, s=60, zorder=5)
            ax1.scatter([exit_rad], [exit_dist], color=color, s=60, zorder=5, marker='^')

            # Optional: label
            ax1.text(exit_rad, exit_dist+0.05, f"{label}", color=color, fontsize=10, ha='center', va='bottom')

        ax1.set_title("180° Radar (0° center, max 1.5 m)")

        # --- Pie Chart ---
        ax2 = fig.add_subplot(122)
        ax2.pie(counts, labels=labels, autopct=lambda p:f'{p:.1f}%' if p>0 else '',
                colors=[insect_colors.get(l,"gray") for l in labels])
        ax2.set_title("Insect Proportion")

        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH,expand=True)

    # ---------------- TAB 3 ----------------
    def build_tab3(self):
        self.advice_box = scrolledtext.ScrolledText(self.tab3, wrap=tk.WORD, width=100, height=24,
                                                    font=("Segoe UI",12), bg="#1e1e2f", fg="white")
        self.advice_box.pack(padx=15,pady=10,fill=tk.BOTH,expand=True)
        self.advice_box.insert(tk.END,"💡 LLM Analysis & Advice\n\n")
        input_frame = tk.Frame(self.tab3,bg="#f0f2f5"); input_frame.pack(fill=tk.X,padx=15,pady=5)
        self.prompt_entry = tk.Entry(input_frame,font=("Segoe UI",12), bg="#ecf0f1")
        self.prompt_entry.pack(side=tk.LEFT,fill=tk.X,expand=True,padx=5)
        ask_btn = tk.Button(input_frame,text="Ask LLM", bg="#1abc9c", fg="white", font=("Segoe UI",12), command=self.ask_llm)
        ask_btn.pack(side=tk.LEFT,padx=5)

    def ask_llm(self):
        prompt = self.prompt_entry.get().strip()
        if not prompt: return
        self.prompt_entry.delete(0,tk.END)
        self.advice_box.insert(tk.END,f"\n\n🧑 You: {prompt}\n")

        def run_llm():
            # --- Build compact overall summary ---
            overall_summary = {}
            for sess in self.sessions:
                for label,info in sess.items():
                    if not isinstance(info,dict) or label in ("session_info","video_reference","nearest"):
                        continue
                    if label not in overall_summary:
                        overall_summary[label] = {"count":0,"angles":[],"distances":[]}
                    overall_summary[label]["count"] += info.get("count",0)
                    if "start_angle_deg" in info: overall_summary[label]["angles"].append(info["start_angle_deg"])
                    if "end_angle_deg" in info: overall_summary[label]["angles"].append(info["end_angle_deg"])
                    if "start_distance_m" in info: overall_summary[label]["distances"].append(info["start_distance_m"])
                    if "end_distance_m" in info: overall_summary[label]["distances"].append(info["end_distance_m"])

            ctx = (
                "You are analyzing insect detection logs.\n\n"
                f"Current session data:\n{json.dumps(self.current_session,indent=2)}\n\n"
                f"Overall summary of all sessions:\n{json.dumps(overall_summary,indent=2)}\n\n"
                "When the user asks:\n"
                "- If question is about 'this session' → use Current session.\n"
                "- If question is about 'overall', 'most', 'total', 'all data', or comparisons → use Overall summary.\n\n"
                f"User Question: {prompt}\nAnswer clearly:"
            )

            answer = ask_phi3_short(ctx)
            self.advice_box.insert(tk.END,f"🤖 AI: {answer}\n")
            self.advice_box.see(tk.END)

        threading.Thread(target=run_llm,daemon=True).start()

    # ---------------- General ----------------
    def change_session(self,event=None):
        key = self.session_var.get()
        self.current_session = self.session_map[key]
        self.positions_info = compute_angles_and_distances(
            self.current_session,
            self.current_session.get("video_reference", DEFAULT_VIDEO)
        )
        self.update_text_area()
        self.plot_graph()
        self.start_video(self.current_session.get("video_reference", DEFAULT_VIDEO))

    def update_text_area(self):
        self.text_area.config(state=tk.NORMAL); self.text_area.delete("1.0",tk.END)
        for label,info in self.current_session.items():
            if not isinstance(info, dict) or label in ("session_info","nearest"): 
                continue
            self.text_area.insert(tk.END, f"🪰 {label}\n   Count: {info.get('count',0)}\n")
            angles = self.positions_info.get(label, {})
            if angles:
                self.text_area.insert(tk.END,f"   Entry Angle: {angles.get('entry_angle_deg',0):.1f}°\n")
                self.text_area.insert(tk.END,f"   Exit Angle: {angles.get('exit_angle_deg',0):.1f}°\n")
                self.text_area.insert(tk.END,f"   Entry Distance: {angles.get('entry_dist_m',0):.2f} m\n")
                self.text_area.insert(tk.END,f"   Exit Distance: {angles.get('exit_dist_m',0):.2f} m\n")
        self.text_area.config(state=tk.DISABLED)

    def on_close(self): self.release_video(); self.destroy()

# ----------------------------
# Runner
# ----------------------------
def show_popup():
    root = tk.Tk(); root.withdraw()
    sessions = load_sessions()
    InsectPopup(root,sessions)
    root.mainloop()

if __name__=="__main__":
    show_popup()
