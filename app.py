import streamlit as st
import pandas as pd
import requests
import re
import os
from datetime import datetime

# --- 📁 ALTERNATİF VERİ SAKLAMA (CSV TABANLI) ---
# SQLite hatası almamak için verileri CSV'de tutuyoruz, daha güvenli.
DB_FILE = 'beklenti_verileri.csv'

def save_to_csv(profil, enflasyon, korku):
    new_data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), profil, enflasyon, korku]], 
                            columns=['tarih', 'profil', 'beklenen_enflasyon', 'en_cok_korkulan'])
    if not os.path.isfile(DB_FILE):
        new_data.to_csv(DB_FILE, index=False)
    else:
        new_data.to_csv(DB_FILE, mode='a', index=False, header=False)

# --- 📡 CANLI VERİ ---
TCMB_2026_HEDEF = 22.0

# --- ⚙️ AYARLAR ---
st.set_page_config(page_title="2026 Finansal Simülatör", layout="wide")

st.title("🏠 2026 Yılı Yaşam Maliyeti Analiz Paneli")
st.caption("Veri Tabanı: Modüler CSV Sistemi (Hata Giderildi)")

# --- 🕹️ KENAR ÇUBUĞU ---
st.sidebar.header("🎯 Senaryonuzu Oluşturun")
user_profile = st.sidebar.selectbox("Profiliniz:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"])
maas = st.sidebar.number_input("Mevcut Aylık Geliriniz (TL):", min_value=0, value=25000)

st.sidebar.divider()
gida_artisi = st.sidebar.slider("Market/Gıda (%)", 0, 100, 0)
kira_artisi = st.sidebar.slider("Kira/Konut (%)", 0, 100, 0)
ulasim_artisi = st.sidebar.slider("Ulaşım/Benzin (%)", 0, 100, 0)
diger_artisi = st.sidebar.slider("Diğer Giderler (%)", 0, 100, 0)

korku_faktoru = st.sidebar.selectbox("En Büyük Risk:", ["Gıda", "Kira", "Akaryakıt", "Maaş Erimesi"])

# --- 🧮 HESAPLAMA ---
BAZ_ENFLASYON = 14.40
weights = {"Öğrenci": 0.40, "Emekli": 0.50, "Çalışan": 0.35, "Kamu Personeli": 0.30, "Esnaf": 0.25} # Örnek ağırlık
tahmin = BAZ_ENFLASYON + (gida_artisi * 0.4 + kira_artisi * 0.3 + ulasim_artisi * 0.2 + diger_artisi * 0.1)
reel_deger = maas / (1 + (tahmin/100))

# --- 📊 SONUÇLAR ---
c1, c2, c3 = st.columns(3)
c1.metric("Profil", user_profile)
c2.metric("TCMB Hedefi", f"%{TCMB_2026_HEDEF}")
c3.metric("Tahmininiz", f"%{tahmin:.2f}", f"{tahmin-TCMB_2026_HEDEF:.2f} Sapma", delta_color="inverse")

st.info(f"💰 **Alım Gücü:** Maaşınız yıl sonunda **{reel_deger:,.0g} TL** değerine düşebilir.")

# --- 💾 VERİ GÖNDERME ---
if st.button("🚀 Tahminimi Havuza Kaydet"):
    save_to_csv(user_profile, tahmin, korku_faktoru)
    st.success("Veriler CSV dosyasına başarıyla kaydedildi!")

# --- 🛡️ GİZLİ ADMİN PANELİ ---
st.sidebar.divider()
with st.sidebar.expander("🔐 Yönetici Girişi"):
    sifre = st.text_input("Şifre", type="password")
    if sifre == "alper2026":
        st.header("📂 Veri İzleme Paneli")
        if os.path.exists(DB_FILE):
            df = pd.read_csv(DB_FILE)
            st.write(f"**Toplam Katılımcı:** {len(df)}")
            st.dataframe(df)
            
            # Basit Grafikler
            st.bar_chart(df.groupby("profil")["beklenen_enflasyon"].mean())
        else:
            st.info("Henüz kaydedilmiş veri bulunmuyor.")
