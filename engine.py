import socket
import mysql.connector
import numpy as np
from datetime import datetime

# ──────────────────────────────────────────────────────────────────
# KONFIGURASI INTERVAL PEMBACAAN DATA
INTERVAL_DETIK = 5   
# ──────────────────────────────────────────────────────────────────

class H2OLogic:
    def __init__(self, ip='192.168.x.x', limit=1.50): # Ganti IP sesuai ESP32
        self.limit = limit
        self.interval = INTERVAL_DETIK   
        self.history_h2o = [0.0] * 20
        self.history_timestamps = [""] * 20
        self.validation_buffer = []
        self.buffer_timestamps = [] 
        self.timer_seconds = 0
        self.is_alarm = False
        self.current_val = 0.0

        # Siklus dummy data yang pasti trigger alarm (index maju 1x per 5 detik)
        self.dummy_sequence = [0.90, 1.05, 1.65, 1.80, 1.95, 0.85, 0.92, 1.10]
        self.dummy_index = 0
        
        # Koneksi MySQL
        try:
            self.db = mysql.connector.connect(host="localhost", user="root", password="", database="ssd_project")
            self.cursor = self.db.cursor()
        except: self.db = None

        # Koneksi WiFi ESP32
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(1)
        try: self.client.connect((ip, 80))
        except: self.client = None

    def send_cmd(self, cmd):
        if self.client:
            try: self.client.send(f"{cmd}\n".encode())
            except: pass

    def process_data(self):
        raw_adc, sw_mode = 0, 0
        if self.client:
            try:
                data = self.client.recv(1024).decode('utf-8').strip()
                if "DATA:" in data:
                    parts = data.split('\n')[-1].split(":")[1].split(",")
                    raw_adc, sw_mode = int(parts[0]), int(parts[1])
            except: pass

        # Rumus Kalibrasi
        val = round((raw_adc / 4095.0) * 3.0, 2)
        if not self.client:
            val = round(self.dummy_sequence[self.dummy_index % len(self.dummy_sequence)], 2)
        
        self.current_val = val
        self.timer_seconds += 1

        if self.timer_seconds >= self.interval:
            self.timer_seconds = 0
            now_str = datetime.now().strftime("%H:%M:%S")
            self.validation_buffer.append(val)
            self.buffer_timestamps.append(now_str)
            if not self.client:
                self.dummy_index += 1  # Maju 1 slot per 5 detik (sinkron dengan capture)
            if len(self.validation_buffer) > 3:
                self.validation_buffer.pop(0)
                self.buffer_timestamps.pop(0)
            self.is_alarm = all(v > self.limit for v in self.validation_buffer) if len(self.validation_buffer)==3 else False

            # Tambah ke history hanya setiap 5 detik (1 titik per siklus)
            self.history_h2o.append(val); self.history_h2o.pop(0)
            self.history_timestamps.append(datetime.now().strftime("%H:%M")); self.history_timestamps.pop(0)

            if sw_mode == 2: # Mode AUTO
                self.send_cmd("LAMP_ON")
                self.send_cmd("PUMP_ON" if self.is_alarm else "PUMP_OFF")
            
            # Simpan ke MySQL
            if self.db:
                try:
                    self.cursor.execute("INSERT INTO log_moisture (moisture_val, status, raw_adc) VALUES (%s, %s, %s)", 
                                        (val, "ALARM" if self.is_alarm else "NORMAL", raw_adc))
                    self.db.commit()
                except: pass

        return {"val": val, "is_alarm": self.is_alarm, "buffer": list(self.validation_buffer),
                "buffer_timestamps": list(self.buffer_timestamps), "timestamp": datetime.now().strftime("%H:%M:%S")}

    def get_raw_spectrum(self):
        x = np.linspace(340, 850, 288)
        noise = np.random.normal(1200, 150, 288) + 7000 * np.exp(-((x - 760)**2) / 1200)
        return x, noise