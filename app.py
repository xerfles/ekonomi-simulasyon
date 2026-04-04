import streamlit as st
import pandas as pd
import requests
import re
import os
from datetime import datetime

# --- 📁 VERİ SAKLAMA (CSV TABANLI) ---
DB_FILE = 'beklenti_havuzu.csv'

def save_to_csv(profil, enflasyon, korku):
    new_data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), profil, enflasyon, korku]], 
                            columns=['tarih', 'profil', 'beklenen_enflasyon', 'en_cok_korkulan'])
    if not os.path.isfile(DB_FILE):
        new_data.to_csv(DB_FILE, index=False)
    else:
        new_data.to_csv(DB_FILE, mode='a', index=False, header=False)

# --- 📡 CANLI VERİ & SABİTLER ---
TCMB_2026_HEDEF = 22.0
BAZ_ENFLASYON = 14.40 

# --- ⚙️ AYARLAR ---
st.set_page_config(page_title="2026 Ekonomi Analizi", layout="wide")

st.title("🏠 2026 Yılı Yaşam Maliyeti Tahmin Paneli")
st.markdown("Nisan-Aralık dönemi için kendi ekonomik senaryonuzu oluşturun.")

# --- 🕹️ KENAR ÇUBUĞU ---
st.sidebar.header("🎯 Tahminlerinizi Girin")

user_profile = st.sidebar.selectbox(
    "Durumunuz:", 
    ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"]
)

st.sidebar.divider()

gida_artisi = st.sidebar.slider("🛒 Market/Gıda (%)", 0, 100, 0)
kira_artisi = st.sidebar.slider("🏠 Kira/Konut (%)", 0, 100, 0)
ulasim_artisi = st.sidebar.slider("🚗 Ulaşım/Benzin (%)", 0, 100, 0)
diger_artisi = st.sidebar.slider("🎭 Diğer Giderler (%)", 0, 100, 0)

korku_faktoru = st.sidebar.selectbox(
    "Sizi en çok korkutan zam:", 
    ["Gıda", "Kira", "Akaryakıt", "Eğitim/Sağlık"]
)

# --- 🧮 HESAPLAMA (SADELEŞTİRİLMİŞ) ---
# Profillere göre ağırlıklar
weights = {
    "Öğrenci": [0.30, 0.40, 0.20, 0.10],
    "Emekli": [0.50, 0.20, 0.10, 0.20],
    "Çalışan": [0.30, 0.30, 0.20, 0.20],
    "Kamu Personeli": [0.30, 0.30, 0.20, 0.20],
    "Esnaf": [0.20, 0.30, 0.30, 0.20]
}

w = weights[user_profile]
ek_enflasyon = (gida_artisi * w[0]) + (kira_artisi * w[1]) + (ulasim_artisi * w[2]) + (diger_artisi * w[3])
tahmin = BAZ_ENFLASYON + ek_enflasyon

# --- 📊 SONUÇLAR ---
st.divider()
col1, col2, col3 = st.columns(3)

col1.metric("📊 Profil", user_profile)
col2.metric("🎯 TCMB Hedefi", f"%{TCMB_2026_HEDEF}")
col3.metric("📈 Sizin Tahmininiz", f"%{tahmin:.2f}", f"{tahmin-TCMB_2026_HEDEF:.2f} Sapma", delta_color="inverse")

# --- 💾 VERİ GÖNDERME ---
st.divider()
st.subheader("🔍 Pilot Çalışma")
st.write("Tahmininizi havuza göndererek genel ortalamaya katkıda bulunun.")

if st.button("🚀 Tahminimi Kaydet"):
    save_to_csv(user_profile, tahmin, korku_faktoru)
    st.success("Kaydedildi! Teşekkürler.")

# --- 🛡️ ADMİN PANELİ ---
st.sidebar.divider()
with st.sidebar.expander("🔐 Yönetici"):
    sifre = st.text_input("Şifre", type="password")
    if sifre == "alper2026":
        if os.path.exists(DB_FILE):
            df = pd.read_csv(DB_FILE)
            st.write(f"**Toplam Kayıt:** {len(df)}")
            st.write(f"**Genel Ort.** %{df['beklenen_enflasyon'].mean():.2f}")
            st.dataframe(df)
        else:
            st.info("Veri yok.")
