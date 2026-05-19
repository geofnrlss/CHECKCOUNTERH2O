import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import winsound
import threading
from engine import H2OLogic

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except: pass

# ── Style Konfigurasi (mengikuti gui_referensi) ──────────────────────────────
BG_SIDEBAR, BG_MAIN, BG_CARD, BG_BORDER = "#F3F4F6", "#F9FAFB", "#FFFFFF", "#D1D5DB"
ACCENT, CLR_GOOD, CLR_BAD, CLR_WARN     = "#2563EB", "#10B981", "#EF4444", "#F59E0B"
TXT_PRIMARY, TXT_SEC                     = "#1F2937", "#6B7280"

FONT_BOLD     = ("Segoe UI", 10, "bold")
FONT_H1       = ("Segoe UI", 12, "bold")
FONT_DATA_BIG = ("Consolas", 22, "bold")
FONT_DATA_MED = ("Consolas", 14, "bold")
FONT_SMALL    = ("Segoe UI", 8, "bold")
FONT_BTN      = ("Segoe UI", 10, "bold")

plt.rcParams.update({
    "figure.facecolor": BG_CARD,
    "axes.facecolor":   "#F9FAFB",
    "axes.edgecolor":   BG_BORDER,
    "axes.labelcolor":  TXT_SEC,
    "xtick.color":      TXT_SEC,
    "ytick.color":      TXT_SEC,
    "grid.color":       "#E5E7EB",
    "grid.linestyle":   "--",
    "grid.linewidth":   0.6,
    "text.color":       TXT_PRIMARY,
})

class CounterH2OGUI:
    def __init__(self, root):
        self.root = root
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg=BG_MAIN)
        self.engine = H2OLogic(ip='192.168.1.15')
        self.is_maximized       = None
        self.popup_shown        = False
        self.popup_window       = None
        self._alarm_stop_event  = None
        self.setup_ui()
        self.update_loop()

    # ────────────────────────────────────────────────────────────────────────
    def setup_ui(self):
        # ── TITLE BAR (full width, biru) ─────────────────────────────────────
        title_bar = tk.Frame(self.root, bg=ACCENT, height=46)
        title_bar.pack(side="top", fill="x")
        title_bar.pack_propagate(False)
        # Tombol minimize pojok kanan, pack dulu agar center bisa benar
        tk.Button(title_bar, text="—", font=("Segoe UI", 12, "bold"),
                  bg=ACCENT, fg="white", relief="flat", cursor="hand2",
                  activebackground="#1D4ED8",
                  command=self.root.iconify).pack(side="right", padx=14)
        # Judul di tengah penuh
        tk.Label(title_bar, text="CHECK COUNTER H\u2082O",
                 font=("Segoe UI", 14, "bold"), bg=ACCENT, fg="white",
                 anchor="center").pack(fill="both", expand=True)

        # ── BARIS BAWAH (sidebar + main) ────────────────────────────────────
        body_row = tk.Frame(self.root, bg=BG_MAIN)
        body_row.pack(fill="both", expand=True)

        # ── SIDEBAR ──────────────────────────────────────────────────────────
        sidebar = tk.Frame(body_row, bg=BG_SIDEBAR, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Frame(sidebar, bg=BG_BORDER, height=1).pack(fill="x", padx=20, pady=16)

        # Interval baca
        tk.Label(sidebar, text="INTERVAL BACA", font=FONT_SMALL,
                 bg=BG_SIDEBAR, fg=TXT_SEC).pack()
        self.lbl_next = tk.Label(sidebar, text="5s", font=("Consolas", 30, "bold"),
                                  bg=BG_SIDEBAR, fg=ACCENT)
        self.lbl_next.pack(pady=2)
        tk.Label(sidebar, text="detik berikutnya", font=("Segoe UI", 8),
                 bg=BG_SIDEBAR, fg=TXT_SEC).pack()

        tk.Frame(sidebar, bg=BG_BORDER, height=1).pack(fill="x", padx=20, pady=16)

        # Batas aman
        tk.Label(sidebar, text="BATAS AMAN", font=FONT_SMALL,
                 bg=BG_SIDEBAR, fg=TXT_SEC).pack()
        tk.Label(sidebar, text=f"{self.engine.limit:.2f} %",
                 font=("Consolas", 20, "bold"), bg=BG_SIDEBAR, fg=CLR_GOOD).pack(pady=2)

        tk.Frame(sidebar, bg=BG_BORDER, height=1).pack(fill="x", padx=20, pady=16)

        # Info box (mengikuti referensi: shift + jam)
        info_box = tk.Frame(sidebar, bg="#E5E7EB",
                            highlightthickness=1, highlightbackground=BG_BORDER,
                            padx=10, pady=10)
        info_box.pack(side="bottom", fill="x", padx=15, pady=15)
        tk.Label(info_box, text="WAKTU SISTEM", font=FONT_SMALL,
                 bg="#E5E7EB", fg=ACCENT).pack()
        self.lbl_date = tk.Label(info_box, text="", font=("Segoe UI", 9),
                                  bg="#E5E7EB", fg=TXT_PRIMARY)
        self.lbl_date.pack()
        self.lbl_clock = tk.Label(info_box, text="00:00:00",
                                   font=("Consolas", 13, "bold"),
                                   bg="#E5E7EB", fg=TXT_PRIMARY)
        self.lbl_clock.pack()

        # Tombol exit di bawah sidebar
        tk.Button(sidebar, text="EXIT SYSTEM", bg=CLR_BAD, fg="white",
                  font=FONT_BTN, relief="flat", pady=10, cursor="hand2",
                  activebackground="#B91C1C", command=self.root.destroy
                  ).pack(side="bottom", fill="x", padx=15, pady=(0, 5))

        # ── MAIN CONTAINER ────────────────────────────────────────────────────
        self.main_container = tk.Frame(body_row, bg=BG_MAIN)
        self.main_container.pack(side="right", fill="both", expand=True)

        # Grid: 2 kolom, 3 baris (0=cards, 1=grafik, 2=log)
        self.main_container.grid_columnconfigure(0, weight=1, uniform="eq")
        self.main_container.grid_columnconfigure(1, weight=1, uniform="eq")
        self.main_container.grid_rowconfigure(0, weight=0, minsize=115)  # cards tetap
        self.main_container.grid_rowconfigure(1, weight=2)               # kedua grafik
        self.main_container.grid_rowconfigure(2, weight=1)               # log

        # Kartu info atas
        self.box_moist, self.lbl_moist = self.create_card("PERSEN MOISTURE", 0, 0, ACCENT)
        self.box_status, self.lbl_status = self.create_card("ALARM STATUS",  0, 1, CLR_GOOD)

        # Box grafik dan log
        self.f_g1  = self.create_box("Trend H\u2082O (%)",    1, 0, self.max_g1)
        self.f_g2  = self.create_box("NIR Spectrum",          1, 1, self.max_g2)
        self.f_log = self.create_box("DATA LOG HISTORY",      2, 0, self.max_log, is_log=True)

        # ── Treeview (gaya referensi: Treeview.Heading biru) ─────────────────
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Ref.Treeview.Heading",
                        background=ACCENT, foreground="white",
                        font=FONT_BOLD, relief="flat")
        style.configure("Ref.Treeview",
                        font=("Segoe UI", 9), rowheight=24,
                        background=BG_CARD, fieldbackground=BG_CARD,
                        foreground=TXT_PRIMARY)
        style.map("Ref.Treeview", background=[("selected", "#DBEAFE")])

        self.tree = ttk.Treeview(self.f_log, style="Ref.Treeview",
                                  columns=("TS","TYP","SRC","MSG","BUF"), show='headings')
        for col, w in zip(("TS","TYP","SRC","MSG","BUF"), (90, 75, 95, 130, 200)):
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(col, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=4, pady=4)
        self.tree.tag_configure('ALARM',  foreground=CLR_BAD)
        self.tree.tag_configure('NORMAL', foreground=CLR_GOOD)

        self.init_charts()

    # ── Card ──────────────────────────────────────────────────────────────────
    def create_card(self, title, r, c, accent_clr):
        b = tk.Frame(self.main_container, bg=BG_CARD,
                     highlightthickness=1, highlightbackground=BG_BORDER)
        b.grid(row=r, column=c, sticky="nsew", padx=(10,5) if c==0 else (5,10), pady=(10, 6))
        b.grid_propagate(False)   # ukuran card dikunci

        # Header row
        hdr = tk.Frame(b, bg=BG_CARD)
        hdr.pack(fill="x", padx=14, pady=(12, 4))
        tk.Frame(hdr, bg=accent_clr, width=4).pack(side="left", fill="y", padx=(0,8))
        tk.Label(hdr, text=title, font=FONT_BOLD,
                 bg=BG_CARD, fg=TXT_SEC).pack(side="left")

        # Nilai data
        lbl = tk.Label(b, text="READY", font=FONT_DATA_BIG,
                       bg=BG_CARD, fg=TXT_PRIMARY, anchor="w")
        lbl.pack(fill="x", padx=14)
        return b, lbl

    # ── Box (grafik/log) ──────────────────────────────────────────────────────
    def create_box(self, title, r, c, cmd, is_log=False):
        f = tk.Frame(self.main_container, bg=BG_CARD,
                     highlightthickness=1, highlightbackground=BG_BORDER)
        if is_log:
            f.grid(row=r, column=0, columnspan=2, rowspan=1,
                   sticky="nsew", padx=10, pady=(0, 10))
        else:
            f.grid(row=r, column=c, columnspan=1, rowspan=1,
                   sticky="nsew",
                   padx=(10,5) if c==0 else (5,10), pady=(0, 6))

        # Header mirip referensi: tombol ⛶ di kanan
        hdr = tk.Frame(f, bg=BG_CARD, pady=6)
        hdr.pack(fill="x", padx=0)
        tk.Label(hdr, text=title, font=FONT_BOLD,
                 bg=BG_CARD, fg=TXT_PRIMARY).pack(side="left", padx=12)
        tk.Button(hdr, text="⛶", font=("Segoe UI", 9, "bold"),
                  bg="#E5E7EB", fg=TXT_PRIMARY, relief="flat", cursor="hand2",
                  activebackground=BG_BORDER, command=cmd
                  ).pack(side="right", padx=8)
        tk.Frame(f, bg=BG_BORDER, height=1).pack(fill="x")
        return f

    # ── Charts ────────────────────────────────────────────────────────────────
    def init_charts(self):
        FIG, DPI = (5, 3), 90
        # Margin identik untuk kedua grafik agar area sumbu (axes) sama persis
        ADJ = dict(left=0.10, right=0.98, top=0.92, bottom=0.15)

        self.fig_t, self.ax_t = plt.subplots(figsize=FIG, dpi=DPI)
        self.fig_t.subplots_adjust(**ADJ)
        self.ax_t.grid(True)
        self.line_t, = self.ax_t.plot(range(20), self.engine.history_h2o,
                                       color=ACCENT, lw=2, marker='o', ms=3)
        self.ax_t.axhline(y=self.engine.limit, color=CLR_BAD, ls='--', lw=1,
                           label=f"Batas {self.engine.limit}%")
        self.ax_t.set_ylim(0, 3.0)
        self.ax_t.set_xticks(range(20))
        self.ax_t.set_xticklabels(self.engine.history_timestamps,
                                   rotation=45, ha='right', fontsize=6)
        self.can_t = FigureCanvasTkAgg(self.fig_t, master=self.f_g1)
        self.can_t.get_tk_widget().pack(fill="both", expand=True)

        self.fig_n, self.ax_n = plt.subplots(figsize=FIG, dpi=DPI)
        self.fig_n.subplots_adjust(**ADJ)
        self.ax_n.grid(True)
        self.x_n = np.linspace(340, 850, 288)
        self.line_n, = self.ax_n.plot(self.x_n, np.zeros(288), color=CLR_GOOD, lw=1.5)
        self.ax_n.set_ylim(0, 10000)
        self.ax_n.set_xlabel("Wavelength (nm)", fontsize=8)
        self.can_n = FigureCanvasTkAgg(self.fig_n, master=self.f_g2)
        self.can_n.get_tk_widget().pack(fill="both", expand=True)

    # ── Maximize ──────────────────────────────────────────────────────────────
    def max_g1(self):  self.do_max('g1')
    def max_g2(self):  self.do_max('g2')
    def max_log(self): self.do_max('log')

    def _restore_grid(self):
        """Kembalikan semua frame ke posisi semula dengan columnspan & rowspan eksplisit."""
        self.f_g1.grid(row=1, column=0, columnspan=1, rowspan=1,
                       sticky="nsew", padx=(10,5), pady=(0,6))
        self.f_g2.grid(row=1, column=1, columnspan=1, rowspan=1,
                       sticky="nsew", padx=(5,10), pady=(0,6))
        self.f_log.grid(row=2, column=0, columnspan=2, rowspan=1,
                        sticky="nsew", padx=10, pady=(0,10))
        self.main_container.grid_rowconfigure(1, weight=2)
        self.main_container.grid_rowconfigure(2, weight=1)

    def do_max(self, mode):
        if self.is_maximized == mode:
            self._restore_grid()
            self.is_maximized = None
        else:
            self.f_g1.grid_remove()
            self.f_g2.grid_remove()
            self.f_log.grid_remove()
            self.main_container.grid_rowconfigure(1, weight=1)
            self.main_container.grid_rowconfigure(2, weight=0)
            if mode == 'g1':
                self.f_g1.grid(row=1, column=0, columnspan=2, rowspan=2,
                               sticky="nsew", padx=10, pady=(0,10))
            elif mode == 'g2':
                self.f_g2.grid(row=1, column=0, columnspan=2, rowspan=2,
                               sticky="nsew", padx=10, pady=(0,10))
            elif mode == 'log':
                self.f_log.grid(row=1, column=0, columnspan=2, rowspan=2,
                                sticky="nsew", padx=10, pady=(0,10))
            self.is_maximized = mode
        self.root.update_idletasks()

    # ── Alarm Sound ───────────────────────────────────────────────────────────
    def play_alarm_sound(self, stop_event):
        def _loop():
            import time
            end = time.time() + 10
            while time.time() < end and not stop_event.is_set():
                winsound.Beep(1000, 400)
                stop_event.wait(timeout=0.1)
        threading.Thread(target=_loop, daemon=True).start()

    # ── Alert Popup ───────────────────────────────────────────────────────────
    def show_alert_popup(self, val):
        if self.popup_window and self.popup_window.winfo_exists():
            return

        self._alarm_stop_event = threading.Event()
        self.play_alarm_sound(self._alarm_stop_event)

        popup = tk.Toplevel(self.root)
        popup.title("⚠  PERINGATAN SISTEM")
        popup.configure(bg="#FEF2F2")
        popup.resizable(False, False)
        popup.attributes("-topmost", True)

        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        pw, ph = 480, 250
        popup.geometry(f"{pw}x{ph}+{(sw-pw)//2}+{(sh-ph)//2}")

        def close_popup():
            if self._alarm_stop_event:
                self._alarm_stop_event.set()
            self.popup_window = None
            self.popup_shown  = True
            popup.destroy()

        # Header (gaya referensi: warna solid + tombol ✕)
        hdr = tk.Frame(popup, bg=CLR_BAD, height=50)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="⚠  PERINGATAN SISTEM", font=("Segoe UI", 12, "bold"),
                 bg=CLR_BAD, fg="white").pack(side="left", padx=16, pady=14)
        tk.Button(hdr, text="  ✕  ", font=("Segoe UI", 11, "bold"),
                  bg="#B91C1C", fg="white", relief="flat", cursor="hand2",
                  activebackground="#991B1B",
                  command=close_popup).pack(side="right", padx=6, pady=10)

        # Body — langsung data, tanpa judul ulang
        body = tk.Frame(popup, bg="#FEF2F2")
        body.pack(fill="both", expand=True, padx=30, pady=18)

        tk.Label(body, text=f"Moisture:  {val:.2f} %",
                 font=("Consolas", 28, "bold"), bg="#FEF2F2", fg=CLR_BAD,
                 anchor="w").pack(fill="x")
        tk.Label(body,
                 text=f"Melebihi batas aman  {self.engine.limit:.2f} %",
                 font=("Segoe UI", 10), bg="#FEF2F2", fg="#9F1239",
                 anchor="w").pack(fill="x", pady=(2, 14))
        tk.Button(body, text="  TUTUP PERINGATAN  ",
                  font=FONT_BTN, bg=CLR_BAD, fg="white",
                  relief="flat", cursor="hand2",
                  activebackground="#B91C1C", pady=8,
                  command=close_popup).pack(anchor="w")

        self.popup_window = popup
        popup.protocol("WM_DELETE_WINDOW", close_popup)

    # ── Update Loop ───────────────────────────────────────────────────────────
    def update_loop(self):
        now = datetime.now()
        self.lbl_clock.config(text=now.strftime("%H:%M:%S"))
        self.lbl_date.config(text=now.strftime("%d %B %Y"))
        self.lbl_next.config(text=f"{self.engine.interval - self.engine.timer_seconds}s")
        d = self.engine.process_data()

        if self.engine.timer_seconds == 0:
            if d['is_alarm']:
                self.box_status.config(highlightbackground=CLR_BAD)
                self.lbl_status.config(fg=CLR_BAD, font=FONT_DATA_MED,
                                       text="DI LUAR BATAS AMAN",
                                       bg=BG_CARD)
                self.lbl_moist.config(text=f"{d['val']:.2f} %",
                                      fg=CLR_BAD, font=FONT_DATA_BIG)
                if not self.popup_shown:
                    self.show_alert_popup(d['val'])
            else:
                self.box_status.config(highlightbackground=BG_BORDER)
                self.lbl_status.config(fg=CLR_GOOD, font=FONT_DATA_BIG,
                                       text="AMAN", bg=BG_CARD)
                self.lbl_moist.config(text=f"{d['val']:.2f} %",
                                      fg=ACCENT, font=FONT_DATA_BIG)
                self.popup_shown = False
                # Hentikan suara alarm lalu tutup popup
                if self._alarm_stop_event:
                    self._alarm_stop_event.set()
                if self.popup_window and self.popup_window.winfo_exists():
                    self.popup_window.destroy()
                    self.popup_window = None

            tag = 'ALARM' if d['is_alarm'] else 'NORMAL'
            self.tree.insert("", 0,
                values=(d['timestamp'], tag, "SENSOR_09",
                        f"Read {d['val']}%", str(d['buffer'])),
                tags=(tag,))

            self.line_t.set_ydata(self.engine.history_h2o)
            self.ax_t.set_xticklabels(self.engine.history_timestamps,
                                       rotation=45, ha='right', fontsize=6)
            self.can_t.draw_idle()

        _, noise = self.engine.get_raw_spectrum()
        self.line_n.set_ydata(noise)
        self.can_n.draw_idle()
        self.root.update_idletasks()
        self.root.after(1000, self.update_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = CounterH2OGUI(root)
    root.mainloop()