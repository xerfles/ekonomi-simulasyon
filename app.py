import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 📁 VERİ SAKLAMA ---
DB_FILE = 'beklenti_havuzu.csv'

def save_to_csv(profil, beklenti_9ay, toplam, dolar_tahmini, korku):
    new_data = pd.DataFrame([[
        datetime.now().strftime("%Y-%m-%d %H:%M"), 
        profil, beklenti_9ay, toplam, dolar_tahmini, korku
    ]], columns=['tarih', 'profil', 'beklenti_9ay', 'toplam_yıl_sonu', 'dolar_tahmini', 'en_cok_korkulan'])
    
    if not os.path.isfile(DB_FILE):
        new_data.to_csv(DB_FILE, index=False)
    else:
        new_data.to_csv(DB_FILE, mode='a', index=False, header=False)

# --- 📊 EKONOMİK VERİLER ---
ILK_CEYREK_GERCEKLESEN = 14.40
TCMB_2026_HEDEF = 22.0
GUNCEL_DOLAR = 44.92 # 5 Nisan 2026 varsayılan kur

GECMIS_DOLAR = {
    "2022 Sonu": 18.70,
    "2023 Sonu": 29.50,
    "2024 Sonu": 34.20,
    "2025 Sonu": 41.10,
    "Şu An (Nisan 2026)": GUNCEL_DOLAR
}

# --- ⚙️ SAYFA AYARLARI ---
st.set_page_config(page_title="2026 Ekonomi Simülatörü", layout="wide")

st.title("🏠 2026 Yılı Enflasyon ve Kur Tahmin Paneli")
st.markdown(f"📊 **İlk Çeyrek Enflasyon:** %{ILK_CEYREK_GERCEKLESEN}  |  🎯 **TCMB Hedefi:** %{TCMB_2026_HEDEF}  |  💵 **Güncel Dolar:** {GUNCEL_DOLAR} TL")

# --- 🕹️ KENAR ÇUBUĞU ---
st.sidebar.header("🎯 Tahmin Parametreleri")

user_profile = st.sidebar.selectbox("Profiliniz:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"])
st.sidebar.divider()

# Dolar Tahmini Bölümü
st.sidebar.write("**💵 2026 Yıl Sonu Dolar Tahmininiz:**")
dolar_tahmin = st.sidebar.slider("Dolar Ne Olur? (TL)", 40.0, 70.0, float(GUNCEL_DOLAR))

st.sidebar.divider()
st.sidebar.write("**📈 Nisan-Aralık Enflasyon Beklentiniz:**")
gida = st.sidebar.slider("🛒 Market/Gıda (%)", 0, 100, 0)
kira = st.sidebar.slider("🏠 Kira/Konut (%)", 0, 100, 0)
ulasim = st.sidebar.slider("🚗 Ulaşım (%)", 0, 100, 0)
diger = st.sidebar.slider("🎭 Diğer (%)", 0, 100, 0)

korku = st.sidebar.selectbox("Temel Endişe:", ["Gıda Fiyatları", "Kira Artışı", "Dolar Kuru", "Maaş Yetmezliği"])

# --- 🧮 HESAPLAMA ---
weights = {"Öğrenci": [0.3, 0.4, 0.2, 0.1], "Emekli": [0.5, 0.2, 0.1, 0.2], "Çalışan": [0.3, 0.3, 0.2, 0.2], "Kamu Personeli": [0.3, 0.3, 0.2, 0.2], "Esnaf": [0.2, 0.3, 0.3, 0.2]}
w = weights[user_profile]
beklenti_9ay = (gida * w[0] + kira * w[1] + ulasim * w[2] + diger * w[3])
toplam_enf = ILK_CEYREK_GERCEKLESEN + beklenti_9ay

# --- 🏁 ANA EKRAN: KARŞILAŞTIRMALI ANALİZ ---
st.divider()
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("🏁 Senaryo Sonuçları")
    res1, res2, res3 = st.columns(3)
    res1.metric("🔮 Sizin 9 Aylık Beklentiniz", f"%{beklenti_9ay:.2f}")
    res2.metric("📈 Yıl Sonu Toplam Tahmin", f"%{toplam_enf:.2f}")
    
    # Dolar Artış Oranı Hesaplama
    kur_artisi = ((dolar_tahmin / GUNCEL_DOLAR) - 1) * 100
    res3.metric("💵 Yıl Sonu Dolar Tahmini", f"{dolar_tahmin:.2f} TL", f"%{kur_artisi:.1f} Artış")

    if st.button("🚀 Tahminimi Havuza Gönder"):
        save_to_csv(user_profile, beklenti_9ay, toplam_enf, dolar_tahmin, korku)
        st.success("Tahminleriniz başarıyla kaydedildi!")

with c2:
    st.subheader("📜 Doların Yolculuğu")
    # Geçmiş Dolar Verileri Tablosu
    dolar_df = pd.DataFrame({
        "Dönem": list(GECMIS_DOLAR.keys()) + ["2026 Sonu (Sizin Tahmin)"],
        "Kur (TL)": list(GECMIS_DOLAR.values()) + [dolar_tahmin]
    })
    st.bar_chart(dolar_df.set_index("Dönem"))

# --- 🛡️ YÖNETİCİ PANELİ ---
st.sidebar.divider()
with st.sidebar.expander("🔐 Yönetici Girişi"):
    sifre = st.text_input("Şifre", type="password")
    if sifre == "alper2026":
        st.header("📂 Analiz Paneli")
        if os.path.exists(DB_FILE):
            df = pd.read_csv(DB_FILE)
            st.metric("Toplam Katılım", f"{len(df)} Kişi")
            st.write("#### Ortalama Dolar Beklentisi")
            st.metric("Toplum Dolar Ortalaması", f"{df['dolar_tahmini'].mean():.2f} TL")
            st.write("#### Grupların Yıl Sonu Enflasyon Beklentisi")
            st.bar_chart(df.groupby("profil")["toplam_yıl_sonu"].mean())
            st.dataframe(df)
        else:
            st.info("Veri yok.")
