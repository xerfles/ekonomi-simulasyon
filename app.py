import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 📁 VERİ SAKLAMA ---
DB_FILE = 'beklenti_havuzu.csv'

def save_to_csv(profil, beklenti_9ay, toplam, dolar_artis, korku):
    new_data = pd.DataFrame([[
        datetime.now().strftime("%Y-%m-%d %H:%M"), 
        profil, beklenti_9ay, toplam, dolar_artis, korku
    ]], columns=['tarih', 'profil', 'beklenti_9ay', 'toplam_yıl_sonu', 'dolar_artis_beklentisi', 'en_cok_korkulan'])
    
    if not os.path.isfile(DB_FILE):
        new_data.to_csv(DB_FILE, index=False)
    else:
        new_data.to_csv(DB_FILE, mode='a', index=False, header=False)

# --- 📊 EKONOMİK VERİLER (2026 BAŞI) ---
ILK_CEYREK_GERCEKLESEN = 14.40
TCMB_2026_HEDEF = 22.0

# Detaylı Geçmiş Veri Seti
GECMIS_VERILER = {
    "Yıl": ["2022", "2023", "2024", "2025"],
    "Enflasyon (%)": [64.27, 64.77, 44.81, 32.10],
    "Dolar Sonu (TL)": [18.70, 29.50, 34.20, 41.10],
    "Dolar Artışı (%)": [93.9, 57.7, 15.9, 20.2],
    "Dolar Değişim (TL)": ["+5.78", "+10.80", "+4.70", "+6.90"]
}

# --- ⚙️ SAYFA AYARLARI ---
st.set_page_config(page_title="Hanehalkı Beklenti Anketi", layout="wide")

st.title("🏠 2026 Yılı Hanehalkı Enflasyon Beklenti Anketi")
st.markdown(f"**Ocak-Şubat-Mart Gerçekleşen Enflasyon:** %{ILK_CEYREK_GERCEKLESEN} | **TCMB Yıl Sonu Hedefi:** %{TCMB_2026_HEDEF}")

# --- 🕹️ KENAR ÇUBUĞU ---
st.sidebar.header("🎯 Tahmin Paneli")
user_profile = st.sidebar.selectbox("Profiliniz:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"])

st.sidebar.divider()
st.sidebar.write("**📈 Nisan-Aralık Artış Beklentiniz (%)**")
dolar_artis = st.sidebar.slider("💵 Dolar Kuru Artışı (%)", 0, 100, 0)
gida = st.sidebar.slider("🛒 Market/Gıda (%)", 0, 100, 0)
kira = st.sidebar.slider("🏠 Kira/Konut (%)", 0, 100, 0)
ulasim = st.sidebar.slider("🚗 Ulaşım (%)", 0, 100, 0)
diger = st.sidebar.slider("🎭 Diğer (%)", 0, 100, 0)

korku = st.sidebar.selectbox("Temel Risk:", ["Gıda", "Kira", "Dolar", "Alım Gücü"])

# --- 🧮 HESAPLAMA ---
weights = {"Öğrenci": [0.2, 0.25, 0.35, 0.15, 0.05], "Emekli": [0.15, 0.45, 0.15, 0.10, 0.15], "Çalışan": [0.2, 0.25, 0.25, 0.15, 0.15], "Kamu Personeli": [0.2, 0.25, 0.25, 0.15, 0.15], "Esnaf": [0.3, 0.2, 0.2, 0.2, 0.1]}
w = weights[user_profile]
beklenti_9ay = (dolar_artis * w[0] + gida * w[1] + kira * w[2] + ulasim * w[3] + diger * w[4])
toplam_yıl_sonu = ILK_CEYREK_GERCEKLESEN + beklenti_9ay

# --- 🏁 ANA EKRAN ---
st.divider()

# Üst Metrikler
m1, m2, m3, m4 = st.columns(4)
m1.metric("📊 İlk Çeyrek (Gerçekleşen)", f"%{ILK_CEYREK_GERCEKLESEN}")
m2.metric("🔮 Sizin 9 Aylık Beklentiniz", f"%{beklenti_9ay:.2f}")
m3.metric("📈 Yıl Sonu Toplam Tahmin", f"%{toplam_yıl_sonu:.2f}")
sapma = toplam_yıl_sonu - TCMB_2026_HEDEF
m4.metric("🎯 Hedef Sapması", f"{sapma:+.2f} Puan", delta_color="inverse")

st.divider()

# Tarihsel Veri Tablosu (Geniş ve Net)
st.subheader("📜 Tarihsel Ekonomi Karnesi (2022-2025)")
st.write("Geçmiş yıllardaki değişimleri birim ve yüzde bazında inceleyebilirsiniz:")

hist_df = pd.DataFrame(GECMIS_VERILER).set_index("Yıl")
st.table(hist_df) # 'table' daha okunaklı ve sabit durur

st.divider()

# Kayıt Butonu
col_btn1, col_btn2 = st.columns([1, 1])
with col_btn1:
    if st.button("🚀 Tahminimi Sisteme Kaydet"):
        save_to_csv(user_profile, beklenti_9ay, toplam_yıl_sonu, dolar_artis, korku)
        st.success("Verileriniz anonim olarak havuza eklendi!")

# --- 🛡️ YÖNETİCİ PANELİ ---
st.sidebar.divider()
with st.sidebar.expander("🔐 Yönetici"):
    if st.text_input("Şifre", type="password") == "alper2026":
        if os.path.exists(DB_FILE):
            df = pd.read_csv(DB_FILE)
            st.write(f"**Toplam Katılım:** {len(df)}")
            st.dataframe(df)
