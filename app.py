import streamlit as st
import pandas as pd
import random
import os
import time

# --- 1. SAYFA VE TEMA AYARLARI ---
st.set_page_config(page_title="Lojistik Takip Paneli", page_icon="🚛", layout="wide")

# ==========================================
# 👇 LOGO AYARI: LİNKİ AŞAĞIYA YAPIŞTIR 👇
# Tırnakların içini silip kendi linkini koy.
LOGO_URL = "https://www.argembilisim.com/wp-content/uploads/2025/09/babacanlarkargo-300x300.png"
# ==========================================

DB_FILE = 'lojistik_db.csv'
ROTA = {
    "Gaziantep (Çıkış)": {"lat": 37.0662, "lon": 37.3833},
    "Adana (Aktarma)": {"lat": 37.0000, "lon": 35.3213},
    "Ankara (Mola)": {"lat": 39.9334, "lon": 32.8597},
    "Bolu (Seyir)": {"lat": 40.7350, "lon": 31.6061},
    "İstanbul (Varış)": {"lat": 41.0082, "lon": 28.9784},
    "İzmir (Batı)": {"lat": 38.4237, "lon": 27.1428}
}

# ÇOK AGRESİF CSS - TÜM TEMAYI ZORLA DEĞİŞTİRİR
st.markdown("""
    <style>
    /* 1. ANA ARKA PLAN (KOYU GRİ / SİYAH) */
    .stApp {
        background-color: #121212 !important;
    }
    
    /* 2. SOL PANEL (KIRMIZ) */
    [data-testid="stSidebar"] {
        background-color: #121212 !important;
        background-image: none !important;
    }
    
    /* 3. TÜM YAZILAR (BEYAZ) */
    .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp span, .stApp label {
        color: #ffffff !important;
    }

    /* 4. SOL PANELDEKİ YAZILAR */
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {
        color: white !important;
        font-weight: bold !important;
    }

    /* 5. GİRİŞ KUTULARI (GÖRÜNÜRLÜK DÜZELTİLDİ) */
    /* Kutuların içi beyaz, yazılar siyah olsun ki okunabilsin */
    .stTextInput input, .stSelectbox div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* 6. BUTONLAR */
    div.stButton > button {
        background-color: #e30613 !important;
        color: white !important;
        border: 2px solid white !important;
        border-radius: 10px;
    }
    div.stButton > button:hover {
        background-color: white !important;
        color: #e30613 !important;
    }

    /* 7. METRİK KARTLARI */
    div[data-testid="stMetric"] {
        background-color: #1e1e1e !important;
        border: 1px solid #e30613 !important;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
def veri_yukle():
    sutunlar = ['takip_kodu', 'alici', 'plaka', 'durum', 'konum', 'lat', 'lon', 'kayit_tarihi']
    if not os.path.exists(DB_FILE):
        return pd.DataFrame(columns=sutunlar)
    df = pd.read_csv(DB_FILE)
    for s in sutunlar:
        if s not in df.columns: df[s] = "Bilinmiyor"
    return df

def veri_kaydet(df):
    df.to_csv(DB_FILE, index=False)

# --- 3. YAN MENÜ ---
with st.sidebar:
    # Logo Alanı (Beyaz Kutu İçinde)
    st.markdown('<div style="background-color:white; border-radius:10px; padding:10px; text-align:center;">', unsafe_allow_html=True)
    # Hata Korumalı Logo Gösterimi
    try:
        st.image(LOGO_URL, width=200)
    except Exception as e:
        st.error("Logo yüklenemedi! Linki kontrol edin.")
        st.caption(f"Hata: {e}") # Mühendislik detayı: Hatayı göster
        st.header("🚛 LOJİSTİK")

    st.markdown('</div>', unsafe_allow_html=True)
    
    st.write("---")
    menu = st.radio("SİSTEM SEÇİMİ", ["🔍 KARGO TAKİP", "🔐 OPERASYON MERKEZİ"])
    st.write("---")

# --- 4. SAYFALAR ---

if menu == "🔍 KARGO TAKİP":
    st.title("🚛 Gönderi Sorgulama")
    st.write("Takip kodunuzu girerek kargonuzun nerede olduğunu öğrenin.")
    
    t_no = st.text_input("Takip No", placeholder="Örn: 123456")
    if st.button("KARGOMU BUL"):
        df = veri_yukle()
        df['takip_kodu'] = df['takip_kodu'].astype(str)
        res = df[df['takip_kodu'] == t_no]
        
        if not res.empty:
            k = res.iloc[0]
            st.success(f"Kargo Bulundu - {k['durum']}")
            col1, col2, col3 = st.columns(3)
            col1.metric("Müşteri", k['alici'])
            col2.metric("Araç Plaka", k['plaka'])
            col3.metric("Anlık Konum", k['konum'])
            st.map(pd.DataFrame({'lat': [float(k['lat'])], 'lon': [float(k['lon'])]}))
        else:
            st.error("Kayıt bulunamadı!")

else:
    st.title("🔐 Operasyon Merkezi")
    sifre = st.text_input("Yönetici Giriş Şifresi", type="password", placeholder="1234")
    
    if sifre == "1234":
        st.success("Yönetici Yetkisi Doğrulandı.")
        
        # YENİ KAYIT FORMU
        with st.expander("➕ YENİ GÖNDERİ OLUŞTUR"):
            with st.form("kayit_f"):
                ad = st.text_input("Müşteri Adı Soyadı")
                plk = st.text_input("Araç Plakası")
                c_s = st.selectbox("Çıkış Noktası", list(ROTA.keys()))
                if st.form_submit_button("Sisteme Kaydet"):
                    df = veri_yukle()
                    kod = str(random.randint(100000, 999999))
                    yeni = pd.DataFrame([{
                        'takip_kodu': kod, 'alici': ad, 'plaka': plk,
                        'durum': 'Yola Çıkmaya Hazır', 'konum': c_s,
                        'lat': ROTA[c_s]['lat'], 'lon': ROTA[c_s]['lon'],
                        'kayit_tarihi': time.strftime("%d.%m.%Y")
                    }])
                    df = pd.concat([df, yeni], ignore_index=True)
                    veri_kaydet(df)
                    st.success(f"Başarılı! KOD: {kod}")

        # LİSTE VE GÜNCELLEME
        st.subheader("📋 Güncel Gönderi Listesi")
        df_l = veri_yukle()
        if not df_l.empty:
            st.dataframe(df_l[['takip_kodu', 'alici', 'plaka', 'konum', 'durum']], use_container_width=True)
            if st.button("🔄 TÜM ARAÇLARI GPS ÜZERİNDEN GÜNCELLE"):
                for i in df_l.index:
                    yer = random.choice(list(ROTA.keys()))
                    df_l.at[i, 'konum'] = yer
                    df_l.at[i, 'lat'] = ROTA[yer]['lat']
                    df_l.at[i, 'lon'] = ROTA[yer]['lon']
                    df_l.at[i, 'durum'] = "Seyir Halinde"
                veri_kaydet(df_l)
                st.rerun()