import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 📁 VERİ SAKLAMA ---
DB_FILE = 'beklenti_havuzu.csv'

def save_to_csv(profil, enflasyon, korku):
    new_data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), profil, enflasyon, korku]], 
                            columns=['tarih', 'profil', 'beklenen_enflasyon', 'en_cok_korkulan'])
    if not os.path.isfile(DB_FILE):
        new_data.to_csv(DB_FILE, index=False)
    else:
        new_data.to_csv(DB_FILE, mode='a', index=False, header=False)

# --- 📊 EKONOMİK GÖSTERGELER (Nisan 2026 İtibarıyla) ---
GERCEKLESEN_İLK_3_AY = 14.40  # Ocak-Şubat-Mart toplamı
GUNCEL_YILLIK_ENFLASYON = 31.53 # Şu anki manşet enflasyon
TCMB_2026_HEDEF = 22.0

GECMIS_ENFLASYON = {
    "2023": 64.77,
    "2024": 44.81,
    "2025": 32.10
}

# --- ⚙️ AYARLAR ---
st.set_page_config(page_title="2026 Ekonomi Simülatörü", layout="wide")

st.title("🏠 2026 Yılı Yaşam Maliyeti Tahmin Paneli")
st.markdown(f"🗓 **Dönem:** Nisan - Aralık 2026 | 📊 **Mevcut Yıllık Enflasyon:** %{GUNCEL_YILLIK_ENFLASYON}")

# --- 🕹️ KULLANICI GİRDİLERİ ---
st.sidebar.header("🎯 Tahmin Parametreleri")
st.sidebar.info(f"Yılın ilk 3 ayında gerçekleşen enflasyon: %{GERCEKLESEN_İLK_3_AY}")

user_profile = st.sidebar.selectbox("Profiliniz:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"])
st.sidebar.divider()

st.sidebar.write("**Nisan-Aralık arası beklediğiniz artışlar:**")
gida = st.sidebar.slider("🛒 Market/Gıda (%)", 0, 100, 0)
kira = st.sidebar.slider("🏠 Kira/Konut (%)", 0, 100, 0)
ulasim = st.sidebar.slider("🚗 Ulaşım (%)", 0, 100, 0)
diger = st.sidebar.slider("🎭 Diğer (%)", 0, 100, 0)

korku = st.sidebar.selectbox("En Büyük Endişe:", ["Gıda Fiyatları", "Kira Artışı", "Akaryakıt Zamları", "Eğitim/Sağlık"])

# Hesaplama Mantığı
weights = {"Öğrenci": [0.3, 0.4, 0.2, 0.1], "Emekli": [0.5, 0.2, 0.1, 0.2], "Çalışan": [0.3, 0.3, 0.2, 0.2], "Kamu Personeli": [0.3, 0.3, 0.2, 0.2], "Esnaf": [0.2, 0.3, 0.3, 0.2]}
w = weights[user_profile]
nisan_aralik_tahmin = (gida * w[0] + kira * w[1] + ulasim * w[2] + diger * w[3])
yıl_sonu_toplam_tahmin = GERCEKLESEN_İLK_3_AY + nisan_aralik_tahmin

# --- 📊 ANA EKRAN: KARŞILAŞTIRMALI SONUÇLAR ---
st.divider()
st.subheader("🏁 Enflasyon Karşılaştırma Paneli")

m1, m2, m3, m4 = st.columns(4)
m1.metric("📊 Mevcut Enflasyon", f"%{GUNCEL_YILLIK_ENFLASYON}")
m2.metric("🎯 TCMB 2026 Hedefi", f"%{TCMB_2026_HEDEF}")
m3.metric("📈 Sizin Tahmininiz", f"%{yıl_sonu_toplam_tahmin:.2f}")

# Sapma Analizi
sapma = yıl_sonu_toplam_tahmin - TCMB_2026_HEDEF
m4.metric("⚖️ Hedef Sapması", f"{sapma:+.2f} Puan", delta_color="inverse")

# --- 📉 GÖRSEL ANALİZ ---
st.divider()
c_chart, c_info = st.columns([2, 1])

with c_chart:
    st.write("#### 📜 Yıllara Göre Enflasyon Seyri ve Tahmininiz")
    hist_df = pd.DataFrame({
        "Yıl": list(GECMIS_ENFLASYON.keys()) + ["2026 (Mevcut)", "2026 (Sizin Tahmin)"],
        "Enflasyon (%)": list(GECMIS_ENFLASYON.values()) + [GUNCEL_YILLIK_ENFLASYON, yıl_sonu_toplam_tahmin]
    })
    st.bar_chart(hist_df.set_index("Yıl"))

with c_info:
    st.write("#### 💡 Analiz Notu")
    st.write(f"""
    - **İlk 3 Ay:** %{GERCEKLESEN_İLK_3_AY} (Gerçekleşti)
    - **Sizin Beklentiniz (Son 9 Ay):** %{nisan_aralik_tahmin:.2f}
    - **Yıl Sonu Toplam:** %{yıl_sonu_toplam_tahmin:.2f}
    """)
    if st.button("🚀 Senaryomu Havuza Gönder"):
        save_to_csv(user_profile, yıl_sonu_toplam_tahmin, korku)
        st.success("Veriler kaydedildi!")

# --- 🛡️ YÖNETİCİ PANELİ ---
st.sidebar.divider()
with st.sidebar.expander("🔐 Yönetici Girişi"):
    sifre = st.text_input("Şifre", type="password")
    if sifre == "alper2026":
        st.divider()
        st.header("📂 Yönetici Analiz Raporu")
        if os.path.exists(DB_FILE):
            df = pd.read_csv(DB_FILE)
            st.metric("Toplam Katılım", len(df))
            st.write("#### Grupların Beklenti Ortalamaları")
            st.bar_chart(df.groupby("profil")["beklenen_enflasyon"].mean())
            st.dataframe(df)
        else:
            st.info("Henüz veri yok.")
