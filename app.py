import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 📁 VERİ SAKLAMA (EN GÜVENLİ YOL: CSV) ---
DB_FILE = 'beklenti_havuzu.csv'

def save_to_csv(profil, beklenti_9ay, toplam, korku):
    new_data = pd.DataFrame([[
        datetime.now().strftime("%Y-%m-%d %H:%M"), 
        profil, beklenti_9ay, toplam, korku
    ]], columns=['tarih', 'profil', 'beklenti_9ay', 'toplam_yıl_sonu', 'en_cok_korkulan'])
    
    if not os.path.isfile(DB_FILE):
        new_data.to_csv(DB_FILE, index=False)
    else:
        new_data.to_csv(DB_FILE, mode='a', index=False, header=False)

# --- 📊 EKONOMİK VERİLER ---
ILK_CEYREK_GERCEKLESEN = 14.40  # Ocak-Şubat-Mart Toplamı
TCMB_2026_HEDEF = 22.0

# --- ⚙️ SAYFA AYARLARI ---
st.set_page_config(page_title="2026 Ekonomi Paneli", layout="wide")

st.title("🏠 2026 Yılı Enflasyon Beklenti Paneli")
st.markdown(f"📊 **İlk Çeyrek (Gerçekleşen):** %{ILK_CEYREK_GERCEKLESEN}  |  🎯 **TCMB Yıl Sonu Hedefi:** %{TCMB_2026_HEDEF}")

# --- 🕹️ KENAR ÇUBUĞU ---
st.sidebar.header("🎯 Tahmin Ekranı")
st.sidebar.info("Nisan - Aralık dönemi için beklentilerinizi girin.")

user_profile = st.sidebar.selectbox("Profiliniz:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"])
st.sidebar.divider()

gida = st.sidebar.slider("🛒 Market/Gıda (%)", 0, 100, 0)
kira = st.sidebar.slider("🏠 Kira/Konut (%)", 0, 100, 0)
ulasim = st.sidebar.slider("🚗 Ulaşım/Benzin (%)", 0, 100, 0)
diger = st.sidebar.slider("🎭 Diğer Giderler (%)", 0, 100, 0)

korku = st.sidebar.selectbox("Temel Endişe:", ["Gıda Fiyatları", "Kira Artışı", "Akaryakıt Zamları", "Maaş Yetmezliği"])

# --- 🧮 HESAPLAMA ---
weights = {
    "Öğrenci": [0.3, 0.4, 0.2, 0.1], 
    "Emekli": [0.5, 0.2, 0.1, 0.2], 
    "Çalışan": [0.3, 0.3, 0.2, 0.2], 
    "Kamu Personeli": [0.3, 0.3, 0.2, 0.2], 
    "Esnaf": [0.2, 0.3, 0.3, 0.2]
}
w = weights[user_profile]
nisan_aralik_tahmin = (gida * w[0] + kira * w[1] + ulasim * w[2] + diger * w[3])
toplam_tahmin = ILK_CEYREK_GERCEKLESEN + nisan_aralik_tahmin

# --- 🏁 SONUÇ EKRANI ---
st.divider()
st.subheader("🏁 Beklenti Özeti")
c1, c2, c3 = st.columns(3)

c1.metric("📊 İlk Çeyrek (Olan)", f"%{ILK_CEYREK_GERCEKLESEN}")
c2.metric("🔮 Sizin 9 Aylık Beklentiniz", f"%{nisan_aralik_tahmin:.2f}")
c3.metric("📈 Yıl Sonu Toplam Tahmin", f"%{toplam_tahmin:.2f}")

# --- ⚖️ KIYASLAMA VE KAYIT ---
st.divider()
sapma = toplam_tahmin - TCMB_2026_HEDEF
if sapma > 0:
    st.error(f"Tahmininiz TCMB hedefinden **{sapma:.2f} puan** daha yüksek.")
else:
    st.success(f"Tahmininiz TCMB hedefinden **{abs(sapma):.2f} puan** daha düşük (İyimser).")

if st.button("🚀 Tahminimi Havuza Gönder"):
    save_to_csv(user_profile, nisan_aralik_tahmin, toplam_tahmin, korku)
    st.success("Veriler kaydedildi!")

# --- 🛡️ YÖNETİCİ PANELİ ---
st.sidebar.divider()
with st.sidebar.expander("🔐 Yönetici Girişi"):
    sifre = st.text_input("Şifre", type="password")
    if sifre == "alper2026":
        st.header("📂 Analiz Raporu")
        if os.path.exists(DB_FILE):
            df = pd.read_csv(DB_FILE)
            st.metric("Toplam Katılım", f"{len(df)} Kişi")
            st.write("#### 📊 Grupların Yıl Sonu Tahmin Ortalamaları")
            st.bar_chart(df.groupby("profil")["toplam_yıl_sonu"].mean())
            st.dataframe(df)
        else:
            st.info("Veri yok.")
