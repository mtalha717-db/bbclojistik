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

# --- SABİT VERİLER (YENİ SİSTEM) ---
# 1. ROTA (Sadece Şehir İsimleri - Veritabanında Böyle Görünecek)
ROTA = {
    "Gaziantep": {"lat": 37.0662, "lon": 37.3833},
    "İstanbul":  {"lat": 41.0082, "lon": 28.9784},
    "Aktarma":   {"lat": 39.9334, "lon": 32.8597}
}

# 2. BAŞLANGIÇ SEÇENEKLERİ (Sadece Yeni Ekle Kısmında Görünecek)
BASLANGIC_SECENEKLERI = ["Gaziantep Çıkış", "İstanbul Çıkış"]

# 3. DURUMLAR (Sadeleştirildi - 'Yola Çıktı' silindi)
DURUMLAR = [
    "Yükleniyor", "Yolda", "Dağıtım Merkezinde", 
    "Dağıtımda", "Teslim Edildi", "İptal Edildi"
]

# --- 2. CSS TASARIM (GÖRÜNÜRLÜK GARANTİLİ) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    [data-testid="stSidebar"] { background-color: #001529; border-right: 3px solid #e30613; }
    
    /* GİRİŞ KUTULARI - KOYU MOD (Okunabilirlik İçin En İyisi) */
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
    
    /* AÇILIR MENÜLER */
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
    st.write("---")
    
    secilen_sayfa = "🔍 KARGO TAKİP"

    if st.session_state['admin_logged_in']:
        kullanici_adi = st.session_state['admin_name'].capitalize()
        st.success(f"👤 Yönetici: {kullanici_adi}")
        secilen_sayfa = st.radio("PANEL", ["🔍 KARGO TAKİP", "⚙️ OPERASYON MERKEZİ"])
        st.write("---")
        if st.button("Çıkış Yap 🔒"):
            st.session_state['admin_logged_in'] = False
            st.rerun()     
    else:
        st.info("Müşteri Paneli Aktif")
        with st.expander("Personel Girişi 🔐"):
            # --- FORM EKLENDİ (HATAYI ÇÖZEN KISIM) ---
            with st.form("giris_form"):
                kullanici = st.text_input("Kullanıcı Adı").lower()
                sifre = st.text_input("Şifre", type="password")
                # Form Submit Butonu sayfanın yenilenmesini bekler
                giris_yap = st.form_submit_button("Giriş Yap")
                
                if giris_yap:
                    if kullanici in KULLANICILAR and KULLANICILAR[kullanici] == sifre:
                        st.session_state['admin_logged_in'] = True
                        st.session_state['admin_name'] = kullanici
                        st.rerun()
                    else:
                        st.error("Hatalı Bilgi!")

# --- 5. İÇERİK ---

if secilen_sayfa == "🔍 KARGO TAKİP":
    st.title("📦 Kargo Takip Sistemi")
    st.markdown("Takip kodunu giriniz.")
    t_no = st.text_input("Takip No", placeholder="Örn: 102938475610")
    
    if st.button("SORGULA"):
        df = veri_yukle()
        if not df.empty:
            res = df[df['takip_kodu'] == t_no.strip()]
            if not res.empty:
                k = res.iloc[0]
                st.success(f"DURUM: {k['durum']}")
                c1, c2, c3 = st.columns(3)
                c1.metric("Alıcı", k['alici'])
                c2.metric("Plaka", k['plaka'])
                c3.metric("Konum", k['konum'])
                try:
                    st.map(pd.DataFrame({'lat': [float(str(k['lat']).replace(',','.'))], 'lon': [float(str(k['lon']).replace(',','.'))]}))
                except: st.warning("Harita yüklenemedi.")
            else: st.error("Kayıt bulunamadı.")
        else: st.error("Veri yok.")

elif secilen_sayfa == "⚙️ OPERASYON MERKEZİ":
    st.title(f"⚙️ Operasyon Merkezi - {st.session_state['admin_name'].capitalize()}")
    df = veri_yukle()
    
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Yeni Ekle", "🔄 Güncelle", "❌ Sil", "📋 Liste"])

    # --- YENİ EKLE ---
    with tab1:
        st.subheader("Yeni Sevkiyat")
        with st.form("ekle_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                ad = st.text_input("Müşteri Adı / Firma")
                tel = st.text_input("Telefon No")
            with col_b:
                email = st.text_input("E-Posta")
                pl = st.text_input("Plaka")
            
            # Burada 'Gaziantep Çıkış' seçtiriyoruz
            baslangic = st.selectbox("Çıkış Noktası", BASLANGIC_SECENEKLERI)
            
            if st.form_submit_button("Kaydet"):
                # Seçime göre saf konumu (Gaziantep/İstanbul) belirle
                saf_konum = "Gaziantep" if "Gaziantep" in baslangic else "İstanbul"
                
                kod = str(random.randint(100000000000, 999999999999))
                
                yeni = pd.DataFrame([{
                    'takip_kodu': kod, 'alici': ad, 'telefon': tel, 'email': email,
                    'plaka': pl, 'durum': 'Yükleniyor', 'konum': saf_konum,
                    'lat': ROTA[saf_konum]['lat'], 'lon': ROTA[saf_konum]['lon'],
                    'kayit_tarihi': time.strftime("%d.%m.%Y")
                }])
                tum_veriyi_guncelle(pd.concat([df, yeni], ignore_index=True))
                st.info(f"YENİ KOD: {kod}")

    # --- GÜNCELLE ---
    with tab2:
        if not df.empty:
            secilen = st.selectbox("Kargo Seç:", df['takip_kodu'] + " - " + df['alici'], key="gnc")
            with st.form("gnc_form"):
                c1, c2 = st.columns(2)
                with c1: durum = st.selectbox("Yeni Durum", DURUMLAR)
                with c2: konum = st.selectbox("Yeni Konum", list(ROTA.keys()))
                
                if st.form_submit_button("Güncellemeyi Kaydet"):
                    idx = df[df['takip_kodu'] == secilen.split(" - ")[0]].index[0]
                    df.at[idx, 'durum'] = durum
                    df.at[idx, 'konum'] = konum
                    df.at[idx, 'lat'] = ROTA[konum]['lat']
                    df.at[idx, 'lon'] = ROTA[konum]['lon']
                    tum_veriyi_guncelle(df)

    # --- SİL ---
    with tab3:
        if not df.empty:
            with st.form("sil_form"):
                silinecek = st.selectbox("Silinecek:", df['takip_kodu'] + " - " + df['alici'])
                if st.form_submit_button("Sil"):
                    tum_veriyi_guncelle(df[df['takip_kodu'] != silinecek.split(" - ")[0]])

    # --- LİSTE ---
    with tab4:
        st.dataframe(df, use_container_width=True)