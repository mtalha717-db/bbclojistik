import streamlit as st
import pandas as pd
import random
import time
from streamlit_gsheets import GSheetsConnection

# --- 1. AYARLAR ---
st.set_page_config(page_title="Babacanlar Lojistik", page_icon="🚛", layout="wide")
LOGO_URL = "https://babacanlarkargo.com.tr/wp-content/uploads/2021/01/babacanlar-logo.png"

# --- KULLANICI HESAPLARI ---
KULLANICILAR = {
    "veysel": "5456",
    "mehmet": "6567",
    "kenan":  "7678"
}

# Oturum Durumu
if 'admin_logged_in' not in st.session_state:
    st.session_state['admin_logged_in'] = False
if 'admin_name' not in st.session_state:
    st.session_state['admin_name'] = ""

# --- SABİT VERİLER ---
ROTA = {
    "Gaziantep (Çıkış)": {"lat": 37.0662, "lon": 37.3833},
    "Aktarma":           {"lat": 39.9334, "lon": 32.8597},
    "İstanbul (Varış)":  {"lat": 41.0082, "lon": 28.9784}
}

DURUMLAR = [
    "Yükleniyor", 
    "Yola Çıktı", 
    "Yolda", 
    "Dağıtım Merkezinde", 
    "Dağıtımda", 
    "Teslim Edildi", 
    "İptal Edildi"
]

# --- 2. CSS TASARIM ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    [data-testid="stSidebar"] { background-color: #001529; border-right: 3px solid #e30613; }
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
        background-color: white !important; color: black !important; font-weight: bold; border-radius: 5px;
    }
    ul[data-baseweb="menu"] { background-color: white !important; }
    ul[data-baseweb="menu"] li { color: black !important; }
    div.stButton > button { 
        background-color: #e30613; color: white; border: 2px solid #e30613; width: 100%; border-radius: 5px; font-weight: bold; transition: all 0.3s ease;
    }
    div.stButton > button:hover { 
        background-color: white !important; color: #e30613 !important; border: 2px solid #e30613 !important;
    }
    h1, h2, h3, p, label, .stMarkdown, .stRadio label { color: white !important; }
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
        
        # --- .0 TEMİZLİĞİ VE STR FORMATI ---
        # Sayıları string yap ve .0 ile bitiyorsa sil
        df['takip_kodu'] = df['takip_kodu'].astype(str).str.replace(r'\.0$', '', regex=True)
        return df
    except:
        return pd.DataFrame(columns=['takip_kodu', 'alici', 'plaka', 'durum', 'konum', 'lat', 'lon', 'kayit_tarihi'])

def tum_veriyi_guncelle(df):
    try:
        conn.update(worksheet="Sayfa1", data=df)
        st.toast("İşlem Başarılı! ☁️", icon="✅")
        time.sleep(1)
        st.rerun()
    except Exception as e:
        st.error(f"Hata: {e}")

# --- 4. ARAYÜZ ---
with st.sidebar:
    st.markdown('<div style="background-color:white; padding:10px; border-radius:10px; text-align:center;">', unsafe_allow_html=True)
    try: st.image(LOGO_URL, use_container_width=True)
    except: st.header("🚛 BABACANLAR")
    st.markdown('</div>', unsafe_allow_html=True)
    st.write("---")
    
    secilen_sayfa = "🔍 KARGO TAKİP"

    if st.session_state['admin_logged_in']:
        kullanici_adi = st.session_state['admin_name'].capitalize()
        st.success(f"👤 Yönetici: {kullanici_adi}")
        secilen_sayfa = st.radio("PANEL", ["🔍 KARGO TAKİP", "⚙️ OPERASYON MERKEZİ"])
        st.write("---")
        if st.button("Çıkış Yap 🔒"):
            st.session_state['admin_logged_in'] = False
            st.session_state['admin_name'] = ""
            st.rerun()     
    else:
        st.info("Müşteri Paneli Aktif")
        with st.expander("Personel Girişi 🔐"):
            kullanici = st.text_input("Kullanıcı Adı").lower()
            sifre = st.text_input("Şifre", type="password")
            if st.button("Giriş Yap"):
                if kullanici in KULLANICILAR and KULLANICILAR[kullanici] == sifre:
                    st.session_state['admin_logged_in'] = True
                    st.session_state['admin_name'] = kullanici
                    st.rerun()
                else:
                    st.error("Hatalı Bilgi!")

# --- 5. İÇERİK ---

if secilen_sayfa == "🔍 KARGO TAKİP":
    st.title("📦 Kargo Takip Sistemi")
    st.markdown("Gönderi durumunu sorgulamak için **12 haneli** takip kodunu giriniz.")
    
    t_no = st.text_input("Takip No", placeholder="Örn: 102938475610")
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
                c3.metric("Konum", k['konum'])
                try:
                    lat = float(str(k['lat']).replace(',', '.'))
                    lon = float(str(k['lon']).replace(',', '.'))
                    st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))
                except:
                    st.warning("Harita verisi yok.")
            else:
                st.error("Kayıt bulunamadı.")
        else:
            st.error("Veri yok.")

elif secilen_sayfa == "⚙️ OPERASYON MERKEZİ":
    st.title(f"⚙️ Operasyon Merkezi - {st.session_state['admin_name'].capitalize()}")
    df = veri_yukle()
    
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Yeni Ekle", "🔄 Güncelle", "❌ Sil", "📋 Liste"])

    # --- YENİ EKLE ---
    with tab1:
        with st.form("ekle_form", clear_on_submit=True):
            ad = st.text_input("Müşteri Adı")
            pl = st.text_input("Plaka")
            cs = st.selectbox("Çıkış Noktası", list(ROTA.keys()))
            if st.form_submit_button("Kaydet"):
                # 12 Haneli Takip Kodu Üretimi
                # Başına '10' koyduk ki Excel bunu sayı sanıp 0 ile başlatmasın
                kod = str(random.randint(100000000000, 999999999999)) 
                
                yeni_satir = pd.DataFrame([{
                    'takip_kodu': kod, 'alici': ad, 'plaka': pl, 
                    'durum': 'Yükleniyor', 'konum': cs, 
                    'lat': ROTA[cs]['lat'], 'lon': ROTA[cs]['lon'], 
                    'kayit_tarihi': time.strftime("%d.%m.%Y")
                }])
                guncel_df = pd.concat([df, yeni_satir], ignore_index=True)
                tum_veriyi_guncelle(guncel_df)
                st.info(f"YENİ TAKİP KODU: {kod}")

    # --- GÜNCELLE ---
    with tab2:
        if not df.empty:
            secenekler = df['takip_kodu'] + " - " + df['alici']
            secilen = st.selectbox("Kargo Seç:", secenekler, key="gnc_slct")
            
            with st.form("gnc_form"):
                col1, col2 = st.columns(2)
                with col1:
                    yeni_durum = st.selectbox("Yeni Durum", DURUMLAR)
                with col2:
                    yeni_konum = st.selectbox("Yeni Konum", list(ROTA.keys()))
                
                if st.form_submit_button("Güncellemeyi Kaydet"):
                    secilen_kod = secilen.split(" - ")[0]
                    idx = df[df['takip_kodu'] == secilen_kod].index[0]
                    
                    df.at[idx, 'durum'] = yeni_durum
                    df.at[idx, 'konum'] = yeni_konum
                    df.at[idx, 'lat'] = ROTA[yeni_konum]['lat']
                    df.at[idx, 'lon'] = ROTA[yeni_konum]['lon']
                    tum_veriyi_guncelle(df)

    # --- SİL ---
    with tab3:
        if not df.empty:
            with st.form("sil_form"):
                sil_secenek = st.selectbox("Silinecek Kayıt:", df['takip_kodu'] + " - " + df['alici'])
                if st.form_submit_button("🗑️ Kaydı Sil"):
                    kod_sil = sil_secenek.split(" - ")[0]
                    yeni_df = df[df['takip_kodu'] != kod_sil]
                    tum_veriyi_guncelle(yeni_df)

    # --- LİSTE ---
    with tab4:
        st.dataframe(df, use_container_width=True)