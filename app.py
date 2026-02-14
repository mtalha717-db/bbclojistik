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

# --- 2. CSS TASARIM (DÜZELTİLMİŞ) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    [data-testid="stSidebar"] { background-color: #001529; border-right: 3px solid #e30613; }
    
    /* Giriş Kutuları ve Seçim Kutusu İçi */
    .stTextInput input { background-color: white !important; color: black !important; font-weight: bold; }
    div[data-baseweb="select"] > div { background-color: white !important; color: black !important; }
    
    /* Butonlar */
    div.stButton > button { background-color: #e30613; color: white; border: none; width: 100%; border-radius: 5px; }
    div.stButton > button:hover { background-color: white; color: #e30613; }
    
    /* Yazılar */
    h1, h2, h3, p, label, .stMarkdown { color: white !important; }
    
    /* Metrik Kartları */
    div[data-testid="stMetric"] { background-color: #1a1c24; border-left: 5px solid #e30613; border-radius: 5px; padding: 10px; }
    div[data-testid="stMetricLabel"] { color: #e30613 !important; }
    div[data-testid="stMetricValue"] { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GOOGLE SHEETS BAĞLANTISI ---
conn = st.connection("gsheets", type=GSheetsConnection)

def veri_yukle():
    try:
        df = conn.read(worksheet="Sayfa1", ttl="0")
        expected_cols = ['takip_kodu', 'alici', 'plaka', 'durum', 'konum', 'lat', 'lon', 'kayit_tarihi']
        # Eksik sütun varsa tamamla
        for col in expected_cols:
            if col not in df.columns:
                df[col] = "" 
        return df.dropna(how="all")
    except Exception as e:
        # Hata olursa boş tablo döndür (Site çökmesin)
        return pd.DataFrame(columns=['takip_kodu', 'alici', 'plaka', 'durum', 'konum', 'lat', 'lon', 'kayit_tarihi'])

def veri_kaydet(yeni_satir_df):
    try:
        mevcut_df = veri_yukle()
        guncel_df = pd.concat([mevcut_df, yeni_satir_df], ignore_index=True)
        conn.update(worksheet="Sayfa1", data=guncel_df)
        st.toast("Kayıt Başarıyla Buluta İşlendi! ☁️", icon="✅")
        time.sleep(1)
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
            # Boşlukları temizle ki hata olmasın
            t_no = t_no.strip()
            res = df[df['takip_kodu'] == t_no]
            
            if not res.empty:
                k = res.iloc[0]
                st.success(f"Durum: {k['durum']}")
                
                # Kart Görünümü
                c1, c2, c3 = st.columns(3)
                c1.metric("Alıcı", k['alici'])
                c2.metric("Plaka", k['plaka'])
                c3.metric("Konum", k['konum'])
                
                # Harita
                try:
                    lat = float(str(k['lat']).replace(',', '.'))
                    lon = float(str(k['lon']).replace(',', '.'))
                    st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))
                except:
                    st.warning("Konum verisi yüklenemedi.")
            else:
                st.error("Bu takip numarasına ait kayıt bulunamadı!")
        else:
            st.error("Sistemde henüz kayıt yok.")

else:
    st.title("🔐 Yönetici Paneli")
    if st.text_input("Şifre", type="password") == "1234":
        st.success("Giriş Başarılı")
        st.info("Yeni sevkiyat oluşturmak için formu doldurun.")
        
        with st.form("yeni_kayit"):
            ad = st.text_input("Müşteri Adı")
            pl = st.text_input("Plaka (Örn: 27 BBC 27)")
            cs = st.selectbox("Çıkış Noktası", list(ROTA.keys()))
            
            if st.form_submit_button("Sisteme Kaydet"):
                if ad and pl: # Boş kaydetmeyi engelle
                    kod = str(random.randint(100000, 999999))
                    yeni_veri = pd.DataFrame([{
                        'takip_kodu': kod,
                        'alici': ad, 
                        'plaka': pl, 
                        'durum': 'Yükleniyor', 
                        'konum': cs, 
                        'lat': ROTA[cs]['lat'], 
                        'lon': ROTA[cs]['lon'], 
                        'kayit_tarihi': time.strftime("%d.%m.%Y")
                    }])
                    veri_kaydet(yeni_veri)
                    st.success(f"✅ Kayıt Başarılı! Takip Kodu: {kod}")
                else:
                    st.warning("Lütfen Müşteri Adı ve Plaka giriniz.")
        
        st.write("---")
        st.subheader("📋 Tüm Kayıtlar (Canlı)")
        try:
            st.dataframe(veri_yukle(), use_container_width=True)
        except:
            st.warning("Veri yok.")