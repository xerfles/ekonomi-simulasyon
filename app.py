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

# --- ⚙️ AYARLAR & SABİTLER ---
st.set_page_config(page_title="2026 Ekonomi Paneli", layout="wide")
TCMB_2026_HEDEF = 22.0
BAZ_ENFLASYON = 14.40 

st.title("🏠 2026 Yılı Yaşam Maliyeti Tahmin Paneli")

# --- 🕹️ KULLANICI ARAYÜZÜ ---
st.sidebar.header("🎯 Tahmin Ekranı")
user_profile = st.sidebar.selectbox("Durumunuz:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"])

st.sidebar.divider()
gida = st.sidebar.slider("🛒 Market (%)", 0, 100, 0)
kira = st.sidebar.slider("🏠 Konut (%)", 0, 100, 0)
ulasim = st.sidebar.slider("🚗 Ulaşım (%)", 0, 100, 0)
diger = st.sidebar.slider("🎭 Diğer (%)", 0, 100, 0)

korku = st.sidebar.selectbox("En Büyük Endişeniz:", ["Gıda Fiyatları", "Kira Artışı", "Akaryakıt Zamları", "Eğitim/Sağlık Giderleri"])

# Hesaplama
weights = {"Öğrenci": [0.3, 0.4, 0.2, 0.1], "Emekli": [0.5, 0.2, 0.1, 0.2], "Çalışan": [0.3, 0.3, 0.2, 0.2], "Kamu Personeli": [0.3, 0.3, 0.2, 0.2], "Esnaf": [0.2, 0.3, 0.3, 0.2]}
w = weights[user_profile]
tahmin = BAZ_ENFLASYON + (gida * w[0] + kira * w[1] + ulasim * w[2] + diger * w[3])

# Kullanıcı Sonuç Ekranı
st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("Profil", user_profile)
c2.metric("TCMB Hedefi", f"%{TCMB_2026_HEDEF}")
c3.metric("Senaryonuz", f"%{tahmin:.2f}", f"{tahmin-TCMB_2026_HEDEF:.2f} Sapma", delta_color="inverse")

if st.button("🚀 Veriyi Havuza Gönder"):
    save_to_csv(user_profile, tahmin, korku)
    st.success("Tahmininiz başarıyla kaydedildi!")

# --- 🛡️ GELİŞMİŞ YÖNETİCİ PANELİ ---
st.sidebar.divider()
with st.sidebar.expander("🔐 Yönetici Girişi"):
    sifre = st.text_input("Şifre", type="password")
    if sifre == "alper2026":
        st.write("### 📂 Detaylı Analiz Raporu")
        if os.path.exists(DB_FILE):
            df = pd.read_csv(DB_FILE)
            
            # 1. ÖZET METRİKLER
            st.divider()
            m1, m2, m3 = st.columns(3)
            m1.metric("Toplam Katılımcı", f"{len(df)} Kişi")
            m2.metric("Genel Beklenti Ort.", f"%{df['beklenen_enflasyon'].mean():.2f}")
            m3.metric("En Çok Korkulan", df['en_cok_korkulan'].value_counts().idxmax())

            # 2. GRUP BAZLI ORTALAMALAR (Tablo ve Grafik)
            st.write("#### 📊 Gruplara Göre Beklenen Enflasyon Ortalamaları")
            grup_analiz = df.groupby("profil")["beklenen_enflasyon"].agg(['mean', 'count']).rename(columns={'mean': 'Ort. Beklenti (%)', 'count': 'Kişi Sayısı'})
            st.table(grup_analiz.style.format("{:.2f}", subset=['Ort. Beklenti (%)']))
            st.bar_chart(df.groupby("profil")["beklenen_enflasyon"].mean())

            # 3. KORKU ANALİZİ
            st.write("#### 🚨 Toplumun En Çok Korktuğu Kalemler")
            korku_sayilari = df['en_cok_korkulan'].value_counts()
            st.bar_chart(korku_sayilari)

            # 4. HAM VERİ VE SİLME
            with st.expander("🗑️ Kayıtları Yönet"):
                st.dataframe(df, use_container_width=True)
                silme_listesi = df['tarih'].tolist()
                secilen = st.selectbox("Silinecek kaydın tarihini seçin:", silme_listesi)
                if st.button("Kayıtı Sil"):
                    df = df[df.tarih != secilen]
                    df.to_csv(DB_FILE, index=False)
                    st.rerun()
        else:
            st.warning("Henüz veri toplanmadı.")
