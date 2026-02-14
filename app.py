import streamlit as st
import pandas as pd
import random
import time
from streamlit_gsheets import GSheetsConnection

# --- 1. AYARLAR ---
st.set_page_config(page_title="Babacanlar Lojistik", page_icon="🚛", layout="wide")
LOGO_URL = "https://babacanlarkargo.com.tr/wp-content/uploads/2021/01/babacanlar-logo.png"

ROTA = {
    "Gaziantep (Çıkış)": {"lat": 37.0662, "lon": 37.3833},
    "Adana (Aktarma)": {"lat": 37.0000, "lon": 35.3213},
    "Ankara (Mola)": {"lat": 39.9334, "lon": 32.8597},
    "Bolu (Seyir)": {"lat": 40.7350, "lon": 31.6061},
    "İstanbul (Varış)": {"lat": 41.0082, "lon": 28.9784}
}

# --- 2. CSS TASARIM (DARK MODE) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    [data-testid="stSidebar"] { background-color: #001529; border-right: 3px solid #e30613; }
    .stTextInput input, .stSelectbox div { background-color: white !important; color: black !important; font-weight: bold; }
    div.stButton > button { background-color: #e30613; color: white; border: none; width: 100%; border-radius: 5px; }
    div.stButton > button:hover { background-color: white; color: #e30613; }
    h1, h2, h3, p, label { color: white !important; }
    /* Tablo ve Kartlar */
    div[data-testid="stMetric"] { background-color: #1a1c24; border-left: 5px solid #e30613; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GOOGLE SHEETS BAĞLANTISI ---
# Secrets kısmına girdiğin bilgilerle bağlantı kurar
conn = st.connection("gsheets", type=GSheetsConnection)

def veri_yukle():
    try:
        # ttl=0 demek önbellek tutma, her seferinde canlı veriyi çek demek
        df = conn.read(worksheet="Sayfa1", ttl="0")
        # Eğer tablo boşsa veya sütunlar eksikse hata vermesin diye kontrol
        expected_cols = ['takip_kodu', 'alici', 'plaka', 'durum', 'konum', 'lat', 'lon', 'kayit_tarihi']
        for col in expected_cols:
            if col not in df.columns:
                df[col] = "" 
        return df.dropna(how="all") # Boş satırları temizle
    except Exception as e:
        st.error("Veritabanına bağlanılamadı. Secrets ayarlarını kontrol et.")
        return pd.DataFrame()

def veri_kaydet(yeni_satir_df):
    try:
        mevcut_df = veri_yukle()
        guncel_df = pd.concat([mevcut_df, yeni_satir_df], ignore_index=True)
        conn.update(worksheet="Sayfa1", data=guncel_df)
        st.toast("Kayıt Başarıyla Buluta İşlendi! ☁️", icon="✅")
        time.sleep(1) # Güncelleme için kısa bekleme
    except Exception as e:
        st.error(f"Kayıt Hatası: {e}")

# --- 4. ARAYÜZ ---
with st.sidebar:
    st.markdown('<div style="background-color:white; padding:10px; border-radius:10px; text-align:center;">', unsafe_allow_html=True)
    try: st.image(LOGO_URL, use_container_width=True)
    except: st.header("🚛 BABACANLAR")
    st.markdown('</div>', unsafe_allow_html=True)
    st.write("---")
    menu = st.radio("MENÜ", ["🔍 KARGO TAKİP", "🔐 OPERASYON MERKEZİ"])

if menu == "🔍 KARGO TAKİP":
    st.title("📦 Kargo Takip Sistemi")
    t_no = st.text_input("Takip No", placeholder="Kodu giriniz...")
    if st.button("SORGULA"):
        df = veri_yukle()
        if not df.empty:
            df['takip_kodu'] = df['takip_kodu'].astype(str)
            res = df[df['takip_kodu'] == t_no]
            
            if not res.empty:
                k = res.iloc[0]
                st.success(f"Durum: {k['durum']}")
                c1, c2, c3 = st.columns(3)
                c1.metric("Alıcı", k['alici'])
                c2.metric("Plaka", k['plaka'])
                c3.metric("Konum", k['konum'])
                
                # Harita için koordinatları sayıya çevir
                try:
                    lat = float(k['lat'])
                    lon = float(k['lon'])
                    st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))
                except:
                    st.warning("Konum verisi harita için uygun değil.")
            else:
                st.error("Kayıt bulunamadı!")
        else:
            st.error("Sistemde kayıtlı veri yok.")

else:
    st.title("🔐 Yönetici Paneli")
    if st.text_input("Şifre", type="password") == "1234":
        st.success("Giriş Başarılı")
        with st.form("yeni_kayit"):
            ad = st.text_input("Müşteri Adı")
            pl = st.text_input("Plaka")
            cs = st.selectbox("Çıkış", list(ROTA.keys()))
            if st.form_submit_button("Kaydet"):
                kod = str(random.randint(100000, 999999))
                yeni_veri = pd.DataFrame([{
                    'takip_kodu': kod, 'alici': ad, 'plaka': pl, 
                    'durum': 'Yükleniyor', 'konum': cs, 
                    'lat': ROTA[cs]['lat'], 'lon': ROTA[cs]['lon'], 
                    'kayit_tarihi': time.strftime("%d.%m.%Y")
                }])
                veri_kaydet(yeni_veri)
                st.info(f"Oluşturulan Takip Kodu: {kod}")
        
        st.write("---")
        st.subheader("📋 Tüm Kayıtlar (Google Sheets)")
        try:
            st.dataframe(veri_yukle(), use_container_width=True)
        except:
            st.warning("Henüz veri yok.")