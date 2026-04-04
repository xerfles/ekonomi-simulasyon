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

# --- 📊 RESMİ EKONOMİK VERİLER (2026 BAŞI) ---
ILK_CEYREK_GERCEKLESEN = 14.40  # Ocak-Mart Toplam Enflasyon
TCMB_2026_HEDEF = 22.0          # TCMB Yıl Sonu Hedefi
GUNCEL_DOLAR = 44.92            # Nisan 2026 piyasa kuru

# Geçmiş Yıllar Veri Seti (2022 Verisi Güncellendi)
GECMIS_VERILER = {
    "Yıl": ["2022", "2023", "2024", "2025"],
    "Enflasyon (%)": [64.27, 64.77, 44.81, 32.10],
    "Dolar Sonu (TL)": [18.70, 29.50, 34.20, 41.10]
}

# --- ⚙️ SAYFA AYARLARI ---
st.set_page_config(page_title="Hanehalkı Beklenti Anketi", layout="wide")

st.title("🏠 2026 Yılı Hanehalkı Enflasyon Beklenti Anketi")
st.markdown(f"""
**Resmi Durum:** Yılın ilk çeyreğinde (Ocak-Mart) enflasyon **%{ILK_CEYREK_GERCEKLESEN}** olarak gerçekleşti. 
TCMB'nin yıl sonu hedefi ise **%{TCMB_2026_HEDEF}**. Sizin tahmininiz nedir?
""")

# --- 🕹️ KENAR ÇUBUĞU ---
st.sidebar.header("🎯 Tahmin Parametreleriniz")
user_profile = st.sidebar.selectbox("Sosyal Profiliniz:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"])

st.sidebar.divider()
st.sidebar.write("**💵 Döviz Beklentisi**")
dolar_tahmin = st.sidebar.slider("2026 Yıl Sonu Dolar Tahmininiz (TL)", 40.0, 70.0, float(GUNCEL_DOLAR))

st.sidebar.divider()
st.sidebar.write("**📈 Nisan-Aralık Enflasyon Tahmini**")
gida = st.sidebar.slider("🛒 Market/Gıda (%)", 0, 100, 0)
kira = st.sidebar.slider("🏠 Kira/Konut (%)", 0, 100, 0)
ulasim = st.sidebar.slider("🚗 Ulaşım (%)", 0, 100, 0)
diger = st.sidebar.slider("🎭 Diğer (%)", 0, 100, 0)

korku = st.sidebar.selectbox("En Büyük Risk Odağı:", ["Gıda Fiyatları", "Kira Artışı", "Döviz Kuru", "Alım Gücü Kaybı"])

# --- 🧮 HESAPLAMA ---
weights = {"Öğrenci": [0.3, 0.4, 0.2, 0.1], "Emekli": [0.5, 0.2, 0.1, 0.2], "Çalışan": [0.3, 0.3, 0.2, 0.2], "Kamu Personeli": [0.3, 0.3, 0.2, 0.2], "Esnaf": [0.2, 0.3, 0.3, 0.2]}
w = weights[user_profile]
beklenti_9ay = (gida * w[0] + kira * w[1] + ulasim * w[2] + diger * w[3])
toplam_yıl_sonu = ILK_CEYREK_GERCEKLESEN + beklenti_9ay

# --- 📊 ANA EKRAN: ANALİZ VE KARŞILAŞTIRMA ---
st.divider()
c_main, c_side = st.columns([2, 1])

with c_main:
    st.subheader("🏁 Beklenti ve Hedef Kıyaslaması")
    m1, m2, m3 = st.columns(3)
    m1.metric("📊 İlk Çeyrek (Olan)", f"%{ILK_CEYREK_GERCEKLESEN}")
    m2.metric("🔮 Sizin 9 Aylık Tahmininiz", f"%{beklenti_9ay:.2f}")
    
    sapma = toplam_yıl_sonu - TCMB_2026_HEDEF
    m3.metric("📈 Yıl Sonu Toplam Beklentiniz", f"%{toplam_yıl_sonu:.2f}", f"{sapma:+.2f} Hedef Sapması", delta_color="inverse")

    st.write("#### 📜 Yıllık Enflasyon Trendi (2022-2026)")
    enf_hist_df = pd.DataFrame({
        "Yıl": GECMIS_VERILER["Yıl"] + ["2026 (Siz)"],
        "Enflasyon (%)": GECMIS_VERILER["Enflasyon (%)"] + [toplam_yıl_sonu]
    })
    st.bar_chart(enf_hist_df.set_index("Yıl"))

    if st.button("🚀 Verilerimi Havuza Gönder"):
        save_to_csv(user_profile, beklenti_9ay, toplam_yıl_sonu, dolar_tahmin, korku)
        st.success("Katılımınız için teşekkürler! Tahmininiz kaydedildi.")

with c_side:
    st.write("#### 📜 Dolar Kuru Serüveni")
    dolar_hist_df = pd.DataFrame({
        "Yıl": GECMIS_VERILER["Yıl"] + ["2026 (Siz)"],
        "Dolar (TL)": GECMIS_VERILER["Dolar Sonu (TL)"] + [dolar_tahmin]
    })
    st.line_chart(dolar_hist_df.set_index("Yıl"))
    st.caption("Geçmiş yıl sonu kurları ve sizin beklentiniz.")

# --- 🛡️ YÖNETİCİ PANELİ ---
st.sidebar.divider()
with st.sidebar.expander("🔐 Yönetici Girişi"):
    sifre = st.text_input("Şifre", type="password")
    if sifre == "alper2026":
        st.divider()
        st.header("📂 Hanehalkı Beklenti Verileri")
        if os.path.exists(DB_FILE):
            df = pd.read_csv(DB_FILE)
            st.metric("Toplam Katılımcı", f"{len(df)} Kişi")
            st.write("#### Gruplara Göre Yıl Sonu Beklenti Ortalaması")
            st.bar_chart(df.groupby("profil")["toplam_yıl_sonu"].mean())
            st.dataframe(df)
        else: st.info("Henüz veri girişi yapılmadı.")
