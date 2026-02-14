import streamlit as st
import pandas as pd
import random
import time
from streamlit_gsheets import GSheetsConnection

# --- 1. AYARLAR ---
st.set_page_config(page_title="Babacanlar Lojistik", page_icon="🚛", layout="wide")
LOGO_URL = "https://babacanlarkargo.com.tr/wp-content/uploads/2021/01/babacanlar-logo.png"

# Oturum Durumu Kontrolü (Giriş yapıldı mı?)
if 'admin_logged_in' not in st.session_state:
    st.session_state['admin_logged_in'] = False

# Sabit Veriler
ROTA = {
    "Gaziantep (Çıkış)": {"lat": 37.0662, "lon": 37.3833},
    "Adana (Aktarma)": {"lat": 37.0000, "lon": 35.3213},
    "Ankara (Mola)": {"lat": 39.9334, "lon": 32.8597},
    "Bolu (Seyir)": {"lat": 40.7350, "lon": 31.6061},
    "İstanbul (Varış)": {"lat": 41.0082, "lon": 28.9784},
    "İzmir (Aktarma)":   {"lat": 38.4192, "lon": 27.1287},
    "Mersin (Liman)":    {"lat": 36.8000, "lon": 34.6333}
}
DURUMLAR = ["Yükleniyor 📦", "Yola Çıktı 🚛", "Gümrükte 🛃", "Dağıtımda 🚚", "Teslim Edildi ✅", "İptal Edildi ❌"]

# --- 2. CSS TASARIM ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    [data-testid="stSidebar"] { background-color: #001529; border-right: 3px solid #e30613; }
    .stTextInput input, .stSelectbox div { background-color: white !important; color: black !important; font-weight: bold; }
    div.stButton > button { background-color: #e30613; color: white; border: none; width: 100%; border-radius: 5px; }
    div.stButton > button:hover { background-color: white; color: #e30613; }
    h1, h2, h3, p, label, .stMarkdown { color: white !important; }
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
        for col in expected_cols:
            if col not in df.columns:
                df[col] = ""
        df = df.astype(str)
        return df
    except:
        return pd.DataFrame(columns=['takip_kodu', 'alici', 'plaka', 'durum', 'konum', 'lat', 'lon', 'kayit_tarihi'])

def tum_veriyi_guncelle(df):
    try:
        conn.update(worksheet="Sayfa1", data=df)
        st.toast("Veritabanı Güncellendi! ☁️", icon="✅")
        time.sleep(1)
        st.rerun()
    except Exception as e:
        st.error(f"Hata: {e}")

# --- 4. KENAR ÇUBUĞU VE GİRİŞ SİSTEMİ ---
with st.sidebar:
    st.markdown('<div style="background-color:white; padding:10px; border-radius:10px; text-align:center;">', unsafe_allow_html=True)
    try: st.image(LOGO_URL, use_container_width=True)
    except: st.header("🚛 BABACANLAR")
    st.markdown('</div>', unsafe_allow_html=True)
    st.write("---")
    
    # Varsayılan (Müşteri) Menüsü
    secilen_sayfa = "🔍 KARGO TAKİP"

    # Eğer Admin Giriş Yapmışsa Menüyü Genişlet
    if st.session_state['admin_logged_in']:
        st.success("👤 Yönetici: Hasan Bey")
        secilen_sayfa = st.radio("YÖNETİM PANELİ", ["🔍 KARGO TAKİP", "⚙️ OPERASYON MERKEZİ"])
        
        st.write("---")
        if st.button("Çıkış Yap 🔒"):
            st.session_state['admin_logged_in'] = False
            st.rerun()
            
    # Eğer Giriş Yapılmamışsa Gizli Giriş Panelini Göster
    else:
        st.info("Müşteri Paneli Aktif")
        with st.expander("Yönetici Girişi 🔐"):
            kullanici = st.text_input("Kullanıcı Adı")
            sifre = st.text_input("Şifre", type="password")
            if st.button("Giriş"):
                if kullanici == "admin" and sifre == "1234":
                    st.session_state['admin_logged_in'] = True
                    st.rerun()
                else:
                    st.error("Hatalı Bilgi!")

# --- 5. SAYFA İÇERİKLERİ ---

# --- SAYFA: MÜŞTERİ GÖRÜNÜMÜ ---
if secilen_sayfa == "🔍 KARGO TAKİP":
    st.title("📦 Kargo Takip Sistemi")
    st.markdown("Gönderinizin durumunu öğrenmek için 6 haneli takip kodunuzu giriniz.")
    
    t_no = st.text_input("Takip No", placeholder="Örn: 508650")
    
    if st.button("SORGULA"):
        df = veri_yukle()
        if not df.empty:
            t_no = t_no.strip()
            res = df[df['takip_kodu'] == t_no]
            
            if not res.empty:
                k = res.iloc[0]
                st.success(f"DURUM: {k['durum']}")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Alıcı", k['alici'])
                c2.metric("Plaka", k['plaka'])
                c3.metric("Son Konum", k['konum'])
                
                try:
                    lat = float(str(k['lat']).replace(',', '.'))
                    lon = float(str(k['lon']).replace(',', '.'))
                    st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))
                except:
                    st.warning("Harita verisi yok.")
            else:
                st.error("Kayıt bulunamadı. Lütfen kodu kontrol ediniz.")
        else:
            st.error("Sistem şu an bakımda.")

# --- SAYFA: ADMİN GÖRÜNÜMÜ (GİZLİ) ---
elif secilen_sayfa == "⚙️ OPERASYON MERKEZİ":
    st.title("⚙️ Operasyon Merkezi")
    st.markdown("Sevkiyatları buradan yönetebilirsiniz.")
    
    df = veri_yukle()
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Yeni Ekle", "🔄 Güncelle", "❌ Sil", "📋 Liste"])

    # Ekleme Modülü
    with tab1:
        with st.form("ekle_form"):
            ad = st.text_input("Müşteri Adı")
            pl = st.text_input("Plaka")
            cs = st.selectbox("Çıkış Noktası", list(ROTA.keys()))
            if st.form_submit_button("Kaydet"):
                kod = str(random.randint(100000, 999999))
                yeni_satir = pd.DataFrame([{
                    'takip_kodu': kod, 'alici': ad, 'plaka': pl, 
                    'durum': 'Yükleniyor 📦', 'konum': cs, 
                    'lat': ROTA[cs]['lat'], 'lon': ROTA[cs]['lon'], 
                    'kayit_tarihi': time.strftime("%d.%m.%Y")
                }])
                guncel_df = pd.concat([df, yeni_satir], ignore_index=True)
                tum_veriyi_guncelle(guncel_df)
                st.info(f"Takip Kodu: {kod}")

    # Güncelleme Modülü
    with tab2:
        if not df.empty:
            secenekler = df['takip_kodu'] + " - " + df['alici']
            secilen = st.selectbox("Kargo Seç:", secenekler)
            if secilen:
                secilen_kod = secilen.split(" - ")[0]
                idx = df[df['takip_kodu'] == secilen_kod].index[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    yeni_durum = st.selectbox("Yeni Durum", DURUMLAR)
                with col2:
                    yeni_konum = st.selectbox("Yeni Konum", list(ROTA.keys()))
                
                if st.button("Güncelle"):
                    df.at[idx, 'durum'] = yeni_durum
                    df.at[idx, 'konum'] = yeni_konum
                    df.at[idx, 'lat'] = ROTA[yeni_konum]['lat']
                    df.at[idx, 'lon'] = ROTA[yeni_konum]['lon']
                    tum_veriyi_guncelle(df)

    # Silme Modülü
    with tab3:
        if not df.empty:
            sil_secenek = st.selectbox("Silinecek Kayıt:", df['takip_kodu'] + " - " + df['alici'], key="sil")
            if st.button("🗑️ Sil"):
                kod_sil = sil_secenek.split(" - ")[0]
                yeni_df = df[df['takip_kodu'] != kod_sil]
                tum_veriyi_guncelle(yeni_df)

    # Liste Modülü
    with tab4:
        st.dataframe(df, use_container_width=True)