import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 📁 VERİ SAKLAMA ---
DB_FILE = 'beklenti_havuzu.csv'

def save_to_csv(profil, beklenti_9ay, toplam, dolar_tahmin, korku):
    new_data = pd.DataFrame([[
        datetime.now().strftime("%Y-%m-%d %H:%M"), 
        profil, beklenti_9ay, toplam, dolar_tahmin, korku
    ]], columns=['tarih', 'profil', 'beklenti_9ay', 'toplam_yıl_sonu', 'dolar_tahmini', 'en_cok_korkulan'])
    
    if not os.path.isfile(DB_FILE):
        new_data.to_csv(DB_FILE, index=False)
    else:
        new_data.to_csv(DB_FILE, mode='a', index=False, header=False)

# --- 📊 RESMİ EKONOMİK VERİLER ---
ILK_CEYREK_GERCEKLESEN = 14.40
TCMB_2026_HEDEF = 22.0
GUNCEL_DOLAR = 44.92

GECMIS_VERILER = {
    "Yıl": ["2022", "2023", "2024", "2025"],
    "Enflasyon (%)": [64.27, 64.77, 44.81, 32.10],
    "Dolar Sonu (TL)": [18.70, 29.50, 34.20, 41.10]
}

# --- ⚙️ SAYFA AYARLARI ---
st.set_page_config(page_title="Hanehalkı Beklenti Anketi", layout="wide")

st.title("🏠 2026 Yılı Hanehalkı Enflasyon Beklenti Anketi")
st.markdown(f"**İlk Çeyrek Enflasyonu:** %{ILK_CEYREK_GERCEKLESEN} | **TCMB Hedefi:** %{TCMB_2026_HEDEF} | **Güncel Kur:** {GUNCEL_DOLAR} TL")

# --- 🕹️ KENAR ÇUBUĞU ---
st.sidebar.header("🎯 Tahmin Parametreleri")
user_profile = st.sidebar.selectbox("Sosyal Profiliniz:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"])

st.sidebar.divider()
st.sidebar.write("**💵 Döviz ve Kur Etkisi**")
dolar_tahmin = st.sidebar.slider("2026 Yıl Sonu Dolar Beklentiniz (TL)", 40.0, 70.0, float(GUNCEL_DOLAR))

# Kur artış oranını hesapla
kur_artis_orani = ((dolar_tahmin / GUNCEL_DOLAR) - 1) * 100

st.sidebar.divider()
st.sidebar.write("**📈 Nisan-Aralık Fiyat Artış Beklentisi**")
gida = st.sidebar.slider("🛒 Market/Gıda (%)", 0, 100, 0)
kira = st.sidebar.slider("🏠 Kira/Konut (%)", 0, 100, 0)
ulasim = st.sidebar.slider("🚗 Ulaşım (%)", 0, 100, 0)
diger = st.sidebar.slider("🎭 Diğer (%)", 0, 100, 0)

korku = st.sidebar.selectbox("En Büyük Risk Odağı:", ["Gıda Fiyatları", "Kira Artışı", "Döviz Kuru", "Alım Gücü Kaybı"])

# --- 🧮 HESAPLAMA (KUR GEÇİŞKENLİĞİ DAHİL) ---
# Ağırlıklar: Gıda, Kira, Ulaşım, Diğer + Kur Geçişkenliği (Doların enflasyona %25 etkisi varsayılır)
weights = {
    "Öğrenci": [0.25, 0.35, 0.15, 0.10],
    "Emekli": [0.45, 0.15, 0.10, 0.15],
    "Çalışan": [0.25, 0.30, 0.15, 0.15],
    "Kamu Personeli": [0.25, 0.30, 0.15, 0.15],
    "Esnaf": [0.20, 0.25, 0.25, 0.15]
}

w = weights[user_profile]
# Temel harcama kalemleri etkisi
temel_etki = (gida * w[0] + kira * w[1] + ulasim * w[2] + diger * w[3])
# Kur geçişkenliği etkisi (Dolar artışının %20'si direkt enflasyona yansır)
kur_etkisi = kur_artis_orani * 0.20 

beklenti_9ay = temel_etki + kur_etkisi
toplam_yıl_sonu = ILK_CEYREK_GERCEKLESEN + beklenti_9ay

# --- 📊 ANA EKRAN ---
st.divider()
c_main, c_side = st.columns([2, 1])

with c_main:
    st.subheader("🏁 Beklenti ve Hedef Kıyaslaması")
    m1, m2, m3 = st.columns(3)
    m1.metric("🔮 9 Aylık Tahmin", f"%{beklenti_9ay:.2f}")
    m2.metric("📈 Yıl Sonu Toplam", f"%{toplam_yıl_sonu:.2f}")
    
    sapma = toplam_yıl_sonu - TCMB_2026_HEDEF
    m3.metric("🎯 Hedef Sapması", f"{sapma:+.2f} Puan", delta_color="inverse")

    st.write("#### 📜 Yıllık Enflasyon Trendi (2022-2026)")
    enf_hist_df = pd.DataFrame({
        "Yıl": GECMIS_VERILER["Yıl"] + ["2026 (Siz)"],
        "Enflasyon (%)": GECMIS_VERILER["Enflasyon (%)"] + [toplam_yıl_sonu]
    })
    st.bar_chart(enf_hist_df.set_index("Yıl"))

    if st.button("🚀 Verilerimi Havuza Gönder"):
        save_to_csv(user_profile, beklenti_9ay, toplam_yıl_sonu, dolar_tahmin, korku)
        st.success("Tahmininiz kur etkisi hesaplanarak kaydedildi!")

with c_side:
    st.write("#### 💵 Kur ve Geçişkenlik")
    st.info(f"Dolar beklentinizdeki **%{kur_artis_orani:.1f}** artış, modelimize göre enflasyona **%{kur_etkisi:.2f}** ek yük getirmektedir.")
    
    dolar_hist_df = pd.DataFrame({
        "Yıl": GECMIS_VERILER["Yıl"] + ["2026 (Siz)"],
        "Dolar (TL)": GECMIS_VERILER["Dolar Sonu (TL)"] + [dolar_tahmin]
    })
    st.line_chart(dolar_hist_df.set_index("Yıl"))

# --- 🛡️ YÖNETİCİ PANELİ ---
st.sidebar.divider()
with st.sidebar.expander("🔐 Yönetici Girişi"):
    if st.text_input("Şifre", type="password") == "alper2026":
        if os.path.exists(DB_FILE):
            df = pd.read_csv(DB_FILE)
            st.write(f"**Genel Dolar Beklentisi:** {df['dolar_tahmini'].mean():.2f} TL")
            st.bar_chart(df.groupby("profil")["toplam_yıl_sonu"].mean())
            st.dataframe(df)
