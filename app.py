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

# --- 📊 TARİHSEL VERİLER (TÜİK/TCMB RESMİ VERİLERİ) ---
GECMIS_ENFLASYON = {
    "2022": 64.27,
    "2023": 64.77,
    "2024": 44.81,
    "2025": 32.10 # Tahmini/Gerçekleşen
}
TCMB_2026_HEDEF = 22.0
BAZ_ENFLASYON = 14.40 

# --- ⚙️ AYARLAR ---
st.set_page_config(page_title="2026 Ekonomi Analizi", layout="wide")

st.title("🏠 2026 Yılı Yaşam Maliyeti Tahmin Paneli")

# --- 🕹️ KULLANICI GİRDİLERİ ---
st.sidebar.header("🎯 Tahmin Senaryosu")
user_profile = st.sidebar.selectbox("Profiliniz:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"])
st.sidebar.divider()

gida = st.sidebar.slider("🛒 Market/Gıda (%)", 0, 100, 0)
kira = st.sidebar.slider("🏠 Kira/Konut (%)", 0, 100, 0)
ulasim = st.sidebar.slider("🚗 Ulaşım (%)", 0, 100, 0)
diger = st.sidebar.slider("🎭 Diğer (%)", 0, 100, 0)

korku = st.sidebar.selectbox("Temel Endişe:", ["Gıda Fiyatları", "Kira Artışı", "Akaryakıt Zamları", "Eğitim/Sağlık"])

# Hesaplama
weights = {"Öğrenci": [0.3, 0.4, 0.2, 0.1], "Emekli": [0.5, 0.2, 0.1, 0.2], "Çalışan": [0.3, 0.3, 0.2, 0.2], "Kamu Personeli": [0.3, 0.3, 0.2, 0.2], "Esnaf": [0.2, 0.3, 0.3, 0.2]}
w = weights[user_profile]
tahmin = BAZ_ENFLASYON + (gida * w[0] + kira * w[1] + ulasim * w[2] + diger * w[3])

# --- 🏁 ANA EKRAN: SONUÇ VE KIYASLAMA ---
st.subheader("🏁 Senaryo Karşılaştırması")
col_res, col_hist = st.columns([2, 1])

with col_res:
    st.write("#### Tahmin Özeti")
    r1, r2, r3 = st.columns(3)
    r1.metric("📊 Profil", user_profile)
    r2.metric("🎯 2026 Hedefi", f"%{TCMB_2026_HEDEF}")
    r3.metric("📈 Sizin Tahmininiz", f"%{tahmin:.2f}", f"{tahmin-TCMB_2026_HEDEF:.2f} Sapma", delta_color="inverse")
    
    if st.button("🚀 Tahminimi Havuza Kaydet"):
        save_to_csv(user_profile, tahmin, korku)
        st.success("Veriler başarıyla kaydedildi!")

with col_hist:
    st.write("#### 📜 Geçmiş Yıllar")
    # Geçmiş verilerle mevcut tahmini birleştiriyoruz
    hist_df = pd.DataFrame({
        "Yıl": list(GECMIS_ENFLASYON.keys()) + ["2026 (Siz)"],
        "Enflasyon (%)": list(GECMIS_ENFLASYON.values()) + [tahmin]
    })
    st.bar_chart(hist_df.set_index("Yıl"))

# --- 🛡️ YÖNETİCİ PANELİ (FERAH GÖRÜNÜM) ---
st.sidebar.divider()
with st.sidebar.expander("🔐 Yönetici Girişi"):
    sifre = st.text_input("Şifre", type="password")
    admin_active = (sifre == "alper2026")

if admin_active:
    st.divider()
    st.header("📂 Stratejik Analiz Raporu")
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        
        # Üst Metrikler
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Toplam Katılım", f"{len(df)} Kişi")
        m2.metric("Genel Beklenti Ort.", f"%{df['beklenen_enflasyon'].mean():.2f}")
        m3.metric("En Düşük", f"%{df['beklenen_enflasyon'].min():.2f}")
        m4.metric("En Yüksek", f"%{df['beklenen_enflasyon'].max():.2f}")

        # Analiz Bölümleri
        st.divider()
        c_left, c_right = st.columns([1, 1.5])
        with c_left:
            st.write("#### 📊 Grup Bazlı Detaylar")
            g_df = df.groupby("profil")["beklenen_enflasyon"].agg(['mean', 'count']).reset_index()
            g_df.columns = ['Grup', 'Ort. Beklenti (%)', 'Kişi']
            st.dataframe(g_df.style.format("{:.2f}", subset=['Ort. Beklenti (%)']), use_container_width=True)
        with c_right:
            st.write("#### 📈 Grupların Tahmin Dağılımı")
            st.bar_chart(df.groupby("profil")["beklenen_enflasyon"].mean())

        st.write("#### 🚨 Toplumun Risk Algısı")
        st.bar_chart(df['en_cok_korkulan'].value_counts())
        
        with st.expander("🗑️ Veri Yönetimi"):
            st.dataframe(df)
            sil_id = st.selectbox("Silinecek tarih:", df['tarih'].tolist())
            if st.button("Seçileni Sil"):
                df = df[df.tarih != sil_id]
                df.to_csv(DB_FILE, index=False)
                st.rerun()
    else:
        st.info("Henüz veri yok.")
