"""
╔══════════════════════════════════════════════════════════════╗
║         PROJECT 4: Object Detection on Images (YOLOv8)       ║
║──────────────────────────────────────────────────────────────║
║  INSTALLATION:                                               ║
║    pip install ultralytics pillow                            ║
║                                                              ║
║  RUN:                                                        ║
║    python project4_yolo_detection.py                        ║
╚══════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import threading
import random

COLORS = [
    "#FF6B6B","#4ECDC4","#45B7D1","#96CEB4","#FFEAA7",
    "#DDA0DD","#98D8C8","#F7DC6F","#BB8FCE","#85C1E9",
]

class YOLODetectionApp:
    BG      = "#0a0a0a"
    SURFACE = "#141414"
    ACCENT  = "#f97316"
    TEXT    = "#f5f5f5"
    MUTED   = "#737373"

    def __init__(self, root):
        self.root = root
        self.root.title("🎯 YOLOv8 Object Detection")
        self.root.configure(bg=self.BG)
        self.root.geometry("800x700")
        self.model = None
        self._build_ui()
        self._load_model_async()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.root, bg=self.SURFACE)
        hdr.pack(fill="x")
        tk.Label(hdr, text="YOLO", font=("Impact", 20), fg=self.ACCENT,
                 bg=self.SURFACE, pady=10).pack(side="left", padx=20)
        tk.Label(hdr, text="v8 · Object Detection", font=("Helvetica", 11),
                 fg=self.MUTED, bg=self.SURFACE).pack(side="left")

        # Main area
        main = tk.Frame(self.root, bg=self.BG)
        main.pack(fill="both", expand=True, padx=16, pady=12)

        # Left — image
        left = tk.Frame(main, bg=self.SURFACE,
                        highlightthickness=1, highlightbackground="#2a2a2a")
        left.pack(side="left", fill="both", expand=True)

        self.img_lbl = tk.Label(left, bg="#050505", text="Upload an image to detect objects",
                                font=("Helvetica", 11), fg=self.MUTED,
                                width=50, height=22)
        self.img_lbl.pack(padx=2, pady=2, fill="both", expand=True)

        # Right — results
        right = tk.Frame(main, bg=self.SURFACE, width=220,
                         highlightthickness=1, highlightbackground="#2a2a2a")
        right.pack(side="right", fill="y", padx=(8, 0))
        right.pack_propagate(False)

        tk.Label(right, text="DETECTIONS", font=("Courier New", 10, "bold"),
                 fg=self.ACCENT, bg=self.SURFACE, pady=10).pack(anchor="w", padx=12)

        self.results_box = tk.Text(right, bg="#0f0f0f", fg=self.TEXT,
                                   font=("Courier New", 10), bd=0,
                                   relief="flat", state="disabled", wrap="word")
        self.results_box.pack(fill="both", expand=True, padx=4, pady=(0, 4))

        # Bottom bar
        bot = tk.Frame(self.root, bg=self.SURFACE)
        bot.pack(fill="x", side="bottom")

        self.upload_btn = tk.Button(
            bot, text="📂  UPLOAD IMAGE", font=("Helvetica", 11, "bold"),
            bg=self.ACCENT, fg="white", activebackground="#ea6b0e",
            activeforeground="white", bd=0, padx=24, pady=10,
            cursor="hand2", command=self.upload, state="disabled"
        )
        self.upload_btn.pack(side="left", padx=16, pady=10)

        self.status_var = tk.StringVar(value="Loading YOLOv8n model…")
        tk.Label(bot, textvariable=self.status_var, font=("Helvetica", 9),
                 fg=self.MUTED, bg=self.SURFACE).pack(side="left")

    def _load_model_async(self):
        def _load():
            from ultralytics import YOLO
            self.model = YOLO("yolov8n.pt")
            self.root.after(0, lambda: self.status_var.set("✓ Ready — upload an image"))
            self.root.after(0, lambda: self.upload_btn.configure(state="normal"))
        threading.Thread(target=_load, daemon=True).start()

    def upload(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.webp")]
        )
        if not path:
            return
        self.upload_btn.configure(state="disabled")
        self.status_var.set("Detecting…")
        threading.Thread(target=self._detect, args=(path,), daemon=True).start()

    def _detect(self, path):
        results = self.model(path, verbose=False)[0]
        img = Image.open(path).convert("RGB")

        # Draw boxes
        draw = ImageDraw.Draw(img)
        detections = []
        for box in results.boxes:
            x1,y1,x2,y2 = map(int, box.xyxy[0].tolist())
            cls_id = int(box.cls[0])
            label  = results.names[cls_id]
            conf   = float(box.conf[0])
            color  = COLORS[cls_id % len(COLORS)]
            draw.rectangle([x1,y1,x2,y2], outline=color, width=3)
            draw.rectangle([x1, y1-18, x1+len(label)*8+8, y1], fill=color)
            draw.text((x1+4, y1-16), f"{label} {conf:.0%}", fill="black")
            detections.append((label, conf, color))

        # Resize for display
        img.thumbnail((520, 440))
        imgtk = ImageTk.PhotoImage(img)
        self.root.after(0, self._show, imgtk, detections)

    def _show(self, imgtk, detections):
        self._imgtk = imgtk
        self.img_lbl.configure(image=imgtk, text="")

        self.results_box.configure(state="normal")
        self.results_box.delete("1.0", "end")
        if not detections:
            self.results_box.insert("end", "No objects detected.\n")
        else:
            counts = {}
            for label, conf, _ in detections:
                counts[label] = counts.get(label, 0) + 1
            for label, cnt in sorted(counts.items(), key=lambda x: -x[1]):
                self.results_box.insert("end", f"  {cnt}×  {label}\n")
            self.results_box.insert("end", f"\n──────────────────\n")
            self.results_box.insert("end", f"Total: {len(detections)} object(s)\n")
        self.results_box.configure(state="disabled")

        self.status_var.set(f"✓ Found {len(detections)} object(s)")
        self.upload_btn.configure(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    YOLODetectionApp(root)
    root.mainloop()
