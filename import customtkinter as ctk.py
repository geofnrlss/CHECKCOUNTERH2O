import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import winsound

# --- 1. ANTI-BERANTAKAN (DPI AWARENESS) ---
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except: pass

# --- STYLE SSD COLORS ---
CLR_SIDEBAR = "#EDF2F7"  
CLR_MAIN_BG = "#FFFFFF"  
CLR_BLUE    = "#2563EB"  
CLR_ORANGE  = "#F59E0B"  
CLR_RED     = "#EF4444"  
CLR_BORDER  = "#D1D5DB"
CLR_GREEN   = "#10B981"  

class CounterH2OGUI:
    def __init__(self, root):
        self.root = root
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg=CLR_MAIN_BG)

        # State Variables
        self.history_h2o = [0.0] * 20
        self.limit = 1.5 
        self.current_max = None 

        # Style untuk Treeview (Excel Look)
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#F3F4F6", foreground="#374151")
        self.style.configure("Treeview", rowheight=30, font=("Segoe UI", 9), borderwidth=0)
        self.style.map("Treeview", background=[('selected', CLR_BLUE)])

        self.setup_ui()
        self.update_loop()

    def setup_ui(self):
        # --- 1. TOP BAR ---
        self.top_bar = tk.Frame(self.root, bg=CLR_MAIN_BG, height=45)
        self.top_bar.pack(side="top", fill="x", padx=15, pady=5)

        tk.Button(self.top_bar, text="✕", font=("Arial", 11, "bold"), bg=CLR_MAIN_BG, fg="gray", relief="flat", command=self.root.destroy).pack(side="right", padx=5)
        tk.Button(self.top_bar, text="—", font=("Arial", 11, "bold"), bg=CLR_MAIN_BG, fg="gray", relief="flat", command=self.root.iconify).pack(side="right", padx=5)
        self.lbl_clock = tk.Label(self.top_bar, text="", font=("Segoe UI", 10, "bold"), bg=CLR_MAIN_BG, fg="#4B5563")
        self.lbl_clock.pack(side="right", padx=15)
        tk.Label(self.top_bar, text="SSD - PRODUCTION MONITORING SYSTEM", font=("Segoe UI", 8, "bold"), bg=CLR_MAIN_BG, fg=CLR_BORDER).pack(side="left")

        # --- 2. SIDEBAR ---
        self.sidebar_frame = tk.Frame(self.root, bg=CLR_SIDEBAR, width=220)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        tk.Label(self.sidebar_frame, text="SSD", font=("Segoe UI", 32, "bold"), bg=CLR_SIDEBAR, fg="#374151").pack(pady=(25, 5))
        tk.Label(self.sidebar_frame, text="CHECK COUNTER H2O", font=("Segoe UI", 9, "bold"), bg=CLR_SIDEBAR, fg=CLR_BLUE).pack(pady=5)
        btn_opt = {"font": ("Segoe UI", 10, "bold"), "relief": "flat", "pady": 15, "fg": "white", "cursor": "hand2"}
        tk.Button(self.sidebar_frame, text="Monitoring Live", bg=CLR_BLUE).pack(fill="x", padx=15, pady=5)
        tk.Button(self.sidebar_frame, text="Dashboard Analytics", bg=CLR_ORANGE).pack(fill="x", padx=15, pady=5)
        tk.Button(self.sidebar_frame, text="Back to Config", bg=CLR_RED, command=self.root.destroy).pack(fill="x", padx=15, pady=5)

        # --- 3. MAIN CONTAINER ---
        self.main_container = tk.Frame(self.root, bg=CLR_MAIN_BG)
        self.main_container.pack(side="right", fill="both", expand=True, padx=25, pady=10)

        # A. KPI FRAME (Atas)
        self.kpi_frame = tk.Frame(self.main_container, bg=CLR_MAIN_BG, height=130)
        self.kpi_frame.pack(side="top", fill="x", pady=(0, 10))
        self.kpi_frame.pack_propagate(False)
        self.box_moist, self.lbl_m_title, self.lbl_moist = self.create_kpi(self.kpi_frame, "PERSEN MOISTURE", "0.00 %")
        self.box_status, self.lbl_s_title, self.lbl_status = self.create_kpi(self.kpi_frame, "STATUS", "AMAN")

        # B. DYNAMIC AREA (Tengah - Grafik & Log)
        self.dynamic_area = tk.Frame(self.main_container, bg=CLR_MAIN_BG)
        self.dynamic_area.pack(side="top", fill="both", expand=True)

        # 1. Log Box (DIUPDATE JADI EXCEL STYLE)
        self.log_box = tk.Frame(self.dynamic_area, bg="white", height=200, highlightthickness=1, highlightbackground=CLR_BORDER)
        self.log_box.pack(side="bottom", fill="x", pady=(10, 0))
        self.log_box.pack_propagate(False)
        
        log_h = tk.Frame(self.log_box, bg="white")
        log_h.pack(fill="x", padx=10, pady=2)
        tk.Label(log_h, text="DATA LOG HISTORY", font=("Segoe UI", 9, "bold"), bg="white").pack(side="left")
        self.btn_max_log = tk.Button(log_h, text="⛶", font=("Arial", 8), bg="#F3F4F6", relief="flat", command=self.toggle_max_log)
        self.btn_max_log.pack(side="right")

        # Excel-Style Table (Treeview)
        cols = ("TIMESTAMP", "TYPE", "SOURCE_NODE", "MESSAGE", "STATUS")
        self.log_tree = ttk.Treeview(self.log_box, columns=cols, show='headings')
        
        # Set Header & Column Width
        col_widths = {"TIMESTAMP": 180, "TYPE": 80, "SOURCE_NODE": 150, "MESSAGE": 350, "STATUS": 100}
        for col in cols:
            self.log_tree.heading(col, text=col, anchor="w")
            self.log_tree.column(col, width=col_widths[col], anchor="w")
        
        # Add Scrollbar
        sb = ttk.Scrollbar(self.log_box, orient="vertical", command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=sb.set)
        
        sb.pack(side="right", fill="y")
        self.log_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Tag colors for Alarm/Warning (Persis Gambar)
        self.log_tree.tag_configure('ALARM', foreground=CLR_RED)
        self.log_tree.tag_configure('NORMAL', foreground="#374151")

        # 2. Graph Row (Ngisi sisa ruang Tengah)
        self.graph_row = tk.Frame(self.dynamic_area, bg=CLR_MAIN_BG)
        self.graph_row.pack(side="top", fill="both", expand=True)
        self.graph_row.grid_columnconfigure(0, weight=1, uniform="equal_width")
        self.graph_row.grid_columnconfigure(1, weight=1, uniform="equal_width")
        self.graph_row.grid_rowconfigure(0, weight=1)

        self.graph_box1 = tk.Frame(self.graph_row, bg="white", highlightthickness=1, highlightbackground=CLR_BORDER)
        self.graph_box1.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        h1 = tk.Frame(self.graph_box1, bg="white")
        h1.pack(fill="x", padx=10, pady=2)
        tk.Label(h1, text="Trend Kelembapan H2O (%)", font=("Segoe UI", 8, "bold"), bg="white").pack(side="left")
        self.btn_max1 = tk.Button(h1, text="⛶", font=("Arial", 8), bg="#F3F4F6", relief="flat", command=self.toggle_max1)
        self.btn_max1.pack(side="right")
        self.init_trend_chart()

        self.graph_box2 = tk.Frame(self.graph_row, bg="white", highlightthickness=1, highlightbackground=CLR_BORDER)
        self.graph_box2.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        h2 = tk.Frame(self.graph_box2, bg="white")
        h2.pack(fill="x", padx=10, pady=2)
        tk.Label(h2, text="NIR Spectral Signature", font=("Segoe UI", 8, "bold"), bg="white").pack(side="left")
        self.btn_max2 = tk.Button(h2, text="⛶", font=("Arial", 8), bg="#F3F4F6", relief="flat", command=self.toggle_max2)
        self.btn_max2.pack(side="right")
        self.init_nir_chart()

    def create_kpi(self, parent, title, val):
        box = tk.Frame(parent, bg="white", highlightthickness=1, highlightbackground=CLR_BORDER, padx=20, pady=12, width=420)
        box.pack(side="left", expand=True, fill="both", padx=5)
        box.pack_propagate(False) 
        t_lbl = tk.Label(box, text=title, font=("Segoe UI", 10, "bold"), bg="white", fg="#6B7280")
        t_lbl.pack(anchor="w")
        v_lbl = tk.Label(box, text=val, font=("Segoe UI", 28, "bold"), bg="white", fg="#1F2937", width=12, anchor="w")
        v_lbl.pack(anchor="w")
        return box, t_lbl, v_lbl

    def init_trend_chart(self):
        self.fig_t, self.ax_t = plt.subplots(figsize=(4, 1.2), dpi=100)
        self.fig_t.patch.set_facecolor('white')
        self.ax_t.set_facecolor('#F9FAFB')
        self.line_t, = self.ax_t.plot(range(20), self.history_h2o, color=CLR_BLUE, lw=2, marker='o', ms=3)
        self.ax_t.axhline(y=self.limit, color=CLR_RED, ls='--', lw=1)
        self.ax_t.set_ylim(0, 2.5); self.ax_t.tick_params(labelsize=7)
        for s in ["top", "right"]: self.ax_t.spines[s].set_visible(False)
        self.canvas_t = FigureCanvasTkAgg(self.fig_t, master=self.graph_box1)
        self.canvas_t.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=2)

    def init_nir_chart(self):
        self.fig_n, self.ax_n = plt.subplots(figsize=(4, 1.2), dpi=100)
        self.fig_n.patch.set_facecolor('white')
        self.ax_n.set_facecolor('#F9FAFB')
        self.x_nir = np.linspace(340, 850, 288)
        self.line_n, = self.ax_n.plot(self.x_nir, np.zeros(288), color=CLR_GREEN, lw=1)
        self.ax_n.set_ylim(0, 8000); self.ax_n.tick_params(labelsize=7)
        for s in ["top", "right"]: self.ax_n.spines[s].set_visible(False)
        self.canvas_n = FigureCanvasTkAgg(self.fig_n, master=self.graph_box2)
        self.canvas_n.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=2)

    def restore_layout(self):
        self.graph_box1.grid_forget(); self.graph_box2.grid_forget()
        self.graph_row.pack_forget(); self.log_box.pack_forget()
        self.log_box.pack(side="bottom", fill="x", pady=(10, 0))
        self.graph_row.pack(side="top", fill="both", expand=True)
        self.graph_row.grid_columnconfigure(0, weight=1, uniform="equal_width")
        self.graph_row.grid_columnconfigure(1, weight=1, uniform="equal_width")
        self.graph_box1.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.graph_box2.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.btn_max1.config(text="⛶"); self.btn_max2.config(text="⛶"); self.btn_max_log.config(text="⛶")
        self.current_max = None

    def toggle_max1(self):
        if self.current_max != 'graph1':
            self.restore_layout()
            self.log_box.pack_forget(); self.graph_box2.grid_forget()
            self.graph_row.grid_columnconfigure(1, weight=0, uniform="")
            self.btn_max1.config(text="❐"); self.current_max = 'graph1'
        else: self.restore_layout()

    def toggle_max2(self):
        if self.current_max != 'graph2':
            self.restore_layout()
            self.log_box.pack_forget(); self.graph_box1.grid_forget()
            self.graph_row.grid_columnconfigure(0, weight=0, uniform="")
            self.btn_max2.config(text="❐"); self.current_max = 'graph2'
        else: self.restore_layout()

    def toggle_max_log(self):
        if self.current_max != 'log':
            self.restore_layout()
            self.graph_row.pack_forget()
            self.log_box.pack(side="top", fill="both", expand=True)
            self.btn_max_log.config(text="❐"); self.current_max = 'log'
        else: self.restore_layout()

    def update_loop(self):
        now = datetime.now()
        ts_full = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        ts_short = now.strftime("%H:%M:%S")
        self.lbl_clock.config(text=now.strftime("%A, %d %B %Y | %H:%M:%S"))
        val = 0.85 + np.random.uniform(-0.3, 0.9)
        
        # Logic Alarm untuk Log
        log_type = "NORMAL"
        log_status = "OK"
        log_tag = 'NORMAL'
        
        if val > self.limit:
            self.box_status.config(bg=CLR_RED); self.lbl_s_title.config(bg=CLR_RED, fg="white")
            self.lbl_status.config(bg=CLR_RED, fg="white", text="BAHAYA   ")
            self.lbl_moist.config(text=f"{val:.2f} %   ", fg=CLR_RED)
            log_type = "ALARM"
            log_status = "ACTIVE"
            log_tag = 'ALARM'
            winsound.Beep(1000, 200)
        else:
            self.box_status.config(bg=CLR_GREEN); self.lbl_s_title.config(bg=CLR_GREEN, fg="white")
            self.lbl_status.config(bg=CLR_GREEN, fg="white", text="AMAN     ")
            self.lbl_moist.config(text=f"{val:.2f} %   ", fg="#1F2937")

        self.root.update_idletasks()

        # Update Log (Excel Style)
        msg = f"Moisture Level: {val:.2f}%"
        if val > self.limit: msg = f"Moisture > {self.limit}% (CRITICAL)"
        
        self.log_tree.insert("", 0, values=(ts_full, log_type, "SENSOR_H20_09", msg, log_status), tags=(log_tag,))
        
        # Limit log 50 baris biar enteng
        if len(self.log_tree.get_children()) > 50:
            self.log_tree.delete(self.log_tree.get_children()[-1])

        self.history_h2o.append(val); self.history_h2o.pop(0)
        self.line_t.set_ydata(self.history_h2o)
        y_nir = np.random.normal(1200, 100, 288) + 5000 * np.exp(-((self.x_nir - 760)**2) / 1000)
        self.line_n.set_ydata(y_nir)
        self.canvas_t.draw_idle(); self.canvas_n.draw_idle()
        self.root.after(1000, self.update_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = CounterH2OGUI(root)
    root.mainloop()