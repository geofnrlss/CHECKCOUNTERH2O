import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. KONFIGURASI & RESET TOTAL CSS ---
st.set_page_config(page_title="Counter H2O | Login", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* 1. Hilangkan semua elemen bawaan Streamlit */
    header, footer, .stDeployButton, [data-testid="stToolbar"] {visibility: hidden; height: 0;}
    
    /* 2. Paksa Body & Container Utama jadi 100% layar (Anti-Scroll) */
    .stApp {
        background: url("https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=1920&q=80");
        background-size: cover;
        background-position: center;
        overflow: hidden; /* NGUNCI SCROLL */
    }
    
    /* 3. Atur container Streamlit biar konten bener-bener di tengah */
    [data-testid="stMainViewContainer"] {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* 4. Desain Card Login (Mirip Smart Stitch) */
    .login-card {
        background-color: white;
        border-radius: 12px;
        display: flex;
        width: 850px;
        height: 480px;
        overflow: hidden;
        box-shadow: 0px 25px 50px rgba(0,0,0,0.5);
    }

    .left-panel {
        background: linear-gradient(135deg, rgba(30, 64, 175, 0.9), rgba(37, 99, 235, 0.8)), 
                    url("https://www.petrokimia-gresik.com/assets/img/slider/slider1.jpg");
        background-size: cover;
        width: 40%;
        padding: 40px;
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .right-panel {
        width: 60%;
        padding: 40px 50px;
        background-color: white;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIKA LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Bikin struktur HTML Card
    st.markdown("""
        <div class="login-card">
            <div class="left-panel">
                <h1 style="font-size: 32px; font-weight: 700; margin-bottom: 5px;">Smart Stitch<br>Detection</h1>
                <p style="font-size: 14px; opacity: 0.9;">Sistem Monitoring Kualitas<br>Jahitan Karung Berbasis AI</p>
                <div style="margin-top: auto; font-size: 11px; opacity: 0.7;">
                    Departemen Pergudangan & Pengantongan
                </div>
            </div>
            <div class="right-panel">
    """, unsafe_allow_html=True)

    # Isi Form Login (Kanan)
    with st.container():
        # Baris Logo
        l1, l2, l3 = st.columns([1, 2, 1])
        with l2:
            st.image("https://upload.wikimedia.org/wikipedia/id/0/09/Logo_ITS_biru.png", width=65)
        
        st.markdown("<h2 style='text-align:center; color:#1e293b; margin: 10px 0 0 0;'>Login</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#64748b; font-size:13px; margin-bottom: 25px;'>Masukkan password akses admin gudang</p>", unsafe_allow_html=True)
        
        pwd = st.text_input("PASSWORD", type="password", placeholder="••••••••", label_visibility="collapsed")
        
        st.markdown("<div style='margin-top: 20px;'>", unsafe_allow_html=True)
        if st.button("LOGIN KE DASHBOARD", use_container_width=True, type="primary"):
            if pwd == "adminits":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Password salah!")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

else:
    # --- HALAMAN DASHBOARD (TAMPIL SETELAH LOGIN) ---
    st.title("🌊 Dashboard Counter H2O")
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))
    st.write("Berhasil masuk ke sistem.")