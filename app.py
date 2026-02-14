import streamlit as st
import pandas as pd
import random
import time
from streamlit_gsheets import GSheetsConnection

# --- 1. AYARLAR ---
st.set_page_config(page_title="Babacanlar Lojistik", page_icon="🚛", layout="wide")
LOGO_URL = "https://babacanlarkargo.com.tr/wp-content/uploads/2021/01/babacanlar-logo.png"

# --- KULLANICILAR ---
KULLANICILAR = {
    "veysel": "5456",
    "mehmet": "6567",
    "kenan":  "7678"
}

# --- OTURUM ---
if 'admin_logged_in' not in st.session_state:
    st.session_state['admin_logged_in'] = False
if 'admin_name' not in st.session_state:
    st.session_state['admin_name'] = ""

# --- SABİT VERİLER ---
ROTA = {
    "Gaziantep": {"lat": 37.0662, "lon": 37.3833},
    "İstanbul":  {"lat": 41.0082, "lon": 28.9784},
    "Aktarma":   {"lat": 39.9334, "lon": 32.8597}
}

BASLANGIC_SECENEKLERI = ["Gaziantep Çıkış", "İstanbul Çıkış"]

DURUMLAR = [
    "Yükleniyor", "Yolda", "Dağıtım Merkezinde", 
    "Dağıtımda", "Teslim Edildi", "İptal Edildi"
]

# --- 2. CSS TASARIM ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    [data-testid="stSidebar"] { background-color: #001529; border-right: 3px solid #e30613; }
    
    /* GİRİŞ KUTULARI (Siyah Arkaplan) */
    input[type="text"], input[type="password"] {
        background-color: #1a1c24 !important;
        color: white !important;
        border: 1px solid #444 !important;
    }
    
    /* SEÇİM KUTULARI */
    div[data-baseweb="select"] > div {
        background-color: #1a1c24 !important;
        color: white !important;
        border: 1px solid #444 !important;
    }
    div[data-baseweb="select"] span { color: white !important; }
    
    /* MENÜLER */
    ul[data-baseweb="menu"] { background-color: #1a1c24 !important; }
    li[role="option"] { color: white !important; }
    
    /* BUTONLAR */
    div.stButton > button { 
        background-color: #e30613 !important; 
        color: white !important; 
        border: 2px solid #e30613 !important; 
        width: 100%; font-weight: bold;
    }
    div.stButton > button:hover { 
        background-color: white !important; 
        color: #e30613 !important; 
        border: 2px solid white !important;
    }
    
    /* METİNLER */
    h1, h2, h3, p, label, span { color: white !important; }
    div[data-testid="stMetric"] { background-color: #1a1c24; border-left: 5px solid #e30613; border-radius: 5px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BAĞLANTI ---
conn = st.connection("gsheets", type=GSheetsConnection)

def veri_yukle():
    try:
        df = conn.read(worksheet="Sayfa1", ttl="0")
        cols = ['takip_kodu', 'alici', 'telefon', 'email', 'plaka', 'durum', 'konum', 'lat', 'lon', 'kayit_tarihi']
        for c in cols:
            if c not in df.columns: df[c] = ""
        df['takip_kodu'] = df['takip_kodu'].astype(str).str.replace(r'\.0$', '', regex=True)
        return df
    except:
        return pd.DataFrame(columns=['takip_kodu', 'alici', 'telefon', 'email', 'plaka', 'durum', 'konum', 'lat', 'lon', 'kayit_tarihi'])

def tum_veriyi_guncelle(df):
    try:
        conn.update(worksheet="Sayfa1", data=df)
        st.toast("İşlem Başarılı! ☁️", icon="✅")
        time.sleep(1)
        st.rerun()
    except Exception as e:
        st.error(f"Hata: {e}")

# --- 4. KENAR ÇUBUĞU ---
with st.sidebar:
    st.markdown('<div style="background-color:white; padding:10px; border-radius:10px; text-align:center;">', unsafe_allow_html=True)
    try: st.image(LOGO_URL, use_container_width=True)
    except: st.header("🚛 BABACANLAR")
    st.markdown('</div>', unsafe_allow_html=True)