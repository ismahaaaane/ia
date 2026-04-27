"""
╔══════════════════════════════════════════════════════════════╗
║             PROJECT 10: Data Visualization Tool              ║
║──────────────────────────────────────────────────────────────║
║  INSTALLATION:                                               ║
║    pip install matplotlib pandas numpy                       ║
║                                                              ║
║  RUN:                                                        ║
║    python project10_data_viz.py                             ║
╚══════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pandas as pd
import numpy as np

CHART_TYPES = [
    "Line Chart", "Bar Chart", "Scatter Plot",
    "Histogram", "Pie Chart", "Box Plot", "Area Chart"
]

PALETTE = ["#6366f1","#f59e0b","#10b981","#ef4444","#3b82f6","#8b5cf6","#ec4899"]

DARK_FIG = {
    "figure.facecolor":  "#0f172a",
    "axes.facecolor":    "#1e293b",
    "axes.edgecolor":    "#334155",
    "axes.labelcolor":   "#94a3b8",
    "xtick.color":       "#64748b",
    "ytick.color":       "#64748b",
    "text.color":        "#e2e8f0",
    "grid.color":        "#1e293b",
    "grid.linestyle":    "--",
    "grid.alpha":        0.4,
}


class DataVizApp:
    BG      = "#0f172a"
    SURFACE = "#1e293b"
    ACCENT  = "#6366f1"
    TEXT    = "#e2e8f0"
    MUTED   = "#64748b"

    def __init__(self, root):
        self.root = root
        self.root.title("📊 Data Visualization Tool")
        self.root.configure(bg=self.BG)
        self.root.geometry("1100x680")
        self.df = None
        self._build_ui()

    def _build_ui(self):
        import matplotlib
        matplotlib.rcParams.update(DARK_FIG)

        # ── Left Sidebar ─────────────────────────────────────────
        sidebar = tk.Frame(self.root, bg=self.SURFACE, width=240)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="DATA VIZ",
                 font=("Helvetica", 16, "bold"),
                 fg=self.ACCENT, bg=self.SURFACE, pady=14).pack()

        # Upload
        tk.Button(sidebar, text="📂  Upload CSV",
                  font=("Helvetica", 11, "bold"),
                  bg=self.ACCENT, fg="white",
                  activebackground="#4f46e5",
                  bd=0, padx=0, pady=10, cursor="hand2",
                  width=22, command=self.upload_csv).pack(pady=(0, 12))

        # File info
        self.file_lbl = tk.Label(sidebar, text="No file loaded",
                                  font=("Helvetica", 8), fg=self.MUTED,
                                  bg=self.SURFACE, wraplength=200)
        self.file_lbl.pack(padx=8)

        sep = tk.Frame(sidebar, bg="#334155", height=1)
        sep.pack(fill="x", padx=12, pady=12)

        # Chart type
        tk.Label(sidebar, text="CHART TYPE", font=("Helvetica", 9, "bold"),
                 fg=self.MUTED, bg=self.SURFACE).pack(anchor="w", padx=12)
        self.chart_type = tk.StringVar(value=CHART_TYPES[0])
        self.chart_menu = ttk.Combobox(sidebar, textvariable=self.chart_type,
                                        values=CHART_TYPES, state="disabled",
                                        font=("Helvetica", 10))
        self.chart_menu.pack(fill="x", padx=12, pady=4)

        # X axis
        tk.Label(sidebar, text="X AXIS", font=("Helvetica", 9, "bold"),
                 fg=self.MUTED, bg=self.SURFACE).pack(anchor="w", padx=12, pady=(8, 0))
        self.x_var = tk.StringVar()
        self.x_menu = ttk.Combobox(sidebar, textvariable=self.x_var,
                                    state="disabled", font=("Helvetica", 10))
        self.x_menu.pack(fill="x", padx=12, pady=4)

        # Y axis
        tk.Label(sidebar, text="Y AXIS (numeric)", font=("Helvetica", 9, "bold"),
                 fg=self.MUTED, bg=self.SURFACE).pack(anchor="w", padx=12, pady=(4, 0))
        self.y_var = tk.StringVar()
        self.y_menu = ttk.Combobox(sidebar, textvariable=self.y_var,
                                    state="disabled", font=("Helvetica", 10))
        self.y_menu.pack(fill="x", padx=12, pady=4)

        # Title
        tk.Label(sidebar, text="CHART TITLE", font=("Helvetica", 9, "bold"),
                 fg=self.MUTED, bg=self.SURFACE).pack(anchor="w", padx=12, pady=(4, 0))
        self.title_entry = tk.Entry(sidebar, font=("Helvetica", 10),
                                    bg="#334155", fg=self.TEXT,
                                    insertbackground=self.TEXT, bd=0, relief="flat")
        self.title_entry.pack(fill="x", padx=12, pady=4, ipady=4)
        self.title_entry.insert(0, "My Chart")

        # Plot button
        self.plot_btn = tk.Button(sidebar, text="▶  PLOT",
                                   font=("Helvetica", 12, "bold"),
                                   bg="#22c55e", fg="#000",
                                   activebackground="#16a34a",
                                   bd=0, padx=0, pady=10, cursor="hand2",
                                   width=22, command=self.plot,
                                   state="disabled")
        self.plot_btn.pack(pady=12)

        # Save
        tk.Button(sidebar, text="💾 Save PNG",
                  font=("Helvetica", 10),
                  bg="#334155", fg=self.TEXT,
                  activebackground="#475569",
                  bd=0, padx=0, pady=7, cursor="hand2",
                  width=22, command=self.save_png).pack()

        # Stats
        sep2 = tk.Frame(sidebar, bg="#334155", height=1)
        sep2.pack(fill="x", padx=12, pady=12)
        tk.Label(sidebar, text="QUICK STATS", font=("Helvetica", 9, "bold"),
                 fg=self.MUTED, bg=self.SURFACE).pack(anchor="w", padx=12)
        self.stats_lbl = tk.Label(sidebar, text="", font=("Courier New", 8),
                                   fg=self.MUTED, bg=self.SURFACE,
                                   justify="left", padx=12)
        self.stats_lbl.pack(anchor="w")

        # ── Right — chart area ───────────────────────────────────
        right = tk.Frame(self.root, bg=self.BG)
        right.pack(side="right", fill="both", expand=True)

        self.fig = Figure(figsize=(8, 5.5), dpi=100)
        self.ax  = self.fig.add_subplot(111)
        self._draw_empty()

        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

        toolbar = NavigationToolbar2Tk(self.canvas, right)
        toolbar.update()
        toolbar.configure(bg=self.SURFACE)

        # Style dropdowns
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox",
                        fieldbackground="#334155", background=self.SURFACE,
                        foreground=self.TEXT, selectbackground=self.ACCENT)

    def _draw_empty(self):
        self.ax.clear()
        self.ax.text(0.5, 0.5, "Upload a CSV file\nto get started",
                     ha="center", va="center",
                     fontsize=14, color=self.MUTED,
                     transform=self.ax.transAxes)
        self.ax.set_xticks([]); self.ax.set_yticks([])

    def upload_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        try:
            self.df = pd.read_csv(path)
            cols = list(self.df.columns)
            num_cols = list(self.df.select_dtypes(include=np.number).columns)

            self.x_menu.configure(values=cols, state="readonly")
            self.y_menu.configure(values=num_cols, state="readonly")
            self.chart_menu.configure(state="readonly")
            self.plot_btn.configure(state="normal")

            self.x_var.set(cols[0])
            self.y_var.set(num_cols[0] if num_cols else cols[0])

            import os
            fname = os.path.basename(path)
            self.file_lbl.configure(
                text=f"{fname}\n{len(self.df):,} rows · {len(cols)} cols"
            )
            self._update_stats()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load CSV:\n{e}")

    def _update_stats(self):
        if self.df is None:
            return
        y = self.y_var.get()
        if y and y in self.df.columns and pd.api.types.is_numeric_dtype(self.df[y]):
            s = self.df[y].dropna()
            self.stats_lbl.configure(
                text=f"Col: {y}\n"
                     f"Min:  {s.min():.3g}\n"
                     f"Max:  {s.max():.3g}\n"
                     f"Mean: {s.mean():.3g}\n"
                     f"Std:  {s.std():.3g}\n"
                     f"N:    {len(s):,}"
            )

    def plot(self):
        if self.df is None:
            return
        chart = self.chart_type.get()
        x_col = self.x_var.get()
        y_col = self.y_var.get()
        title = self.title_entry.get() or "Chart"

        self.ax.clear()
        try:
            x = self.df[x_col]
            y = self.df[y_col] if y_col in self.df.columns else None

            if chart == "Line Chart":
                self.ax.plot(x, y, color=PALETTE[0], linewidth=2)
            elif chart == "Bar Chart":
                self.ax.bar(x.astype(str), y, color=PALETTE[:len(x)])
                self.ax.tick_params(axis="x", rotation=45)
            elif chart == "Scatter Plot":
                self.ax.scatter(x, y, color=PALETTE[0], alpha=0.7, edgecolors="none")
            elif chart == "Histogram":
                self.ax.hist(y, bins=20, color=PALETTE[0], edgecolor="none", alpha=0.85)
            elif chart == "Pie Chart":
                counts = y.value_counts() if not pd.api.types.is_numeric_dtype(y) else \
                         x.value_counts()
                self.ax.pie(counts, labels=counts.index, colors=PALETTE,
                            autopct="%1.1f%%", startangle=90)
            elif chart == "Box Plot":
                num_df = self.df.select_dtypes(include=np.number)
                num_df.plot.box(ax=self.ax, color={"boxes": PALETTE[0],
                                                    "whiskers": PALETTE[1],
                                                    "medians": PALETTE[2],
                                                    "caps": PALETTE[3]})
            elif chart == "Area Chart":
                self.ax.fill_between(range(len(y)), y, color=PALETTE[0], alpha=0.5)
                self.ax.plot(range(len(y)), y, color=PALETTE[0])

            self.ax.set_title(title, fontsize=13, pad=12)
            self.ax.set_xlabel(x_col, fontsize=10)
            if chart not in ("Pie Chart", "Box Plot"):
                self.ax.set_ylabel(y_col, fontsize=10)
            self.ax.grid(True, alpha=0.2)
            self.fig.tight_layout()
        except Exception as e:
            self.ax.text(0.5, 0.5, f"Error: {e}", ha="center", va="center",
                         color="#ef4444", transform=self.ax.transAxes)

        self.canvas.draw()
        self._update_stats()

    def save_png(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("PDF", "*.pdf")]
        )
        if path:
            self.fig.savefig(path, dpi=150, bbox_inches="tight")
            messagebox.showinfo("Saved", f"Chart saved to:\n{path}")


if __name__ == "__main__":
    root = tk.Tk()
    DataVizApp(root)
    root.mainloop()
