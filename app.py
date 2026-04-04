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

# --- ⚙️ AYARLAR ---
st.set_page_config(page_title="2026 Ekonomi Paneli", layout="wide") # 'wide' modu ekranı tam kullanır
TCMB_2026_HEDEF = 22.0
BAZ_ENFLASYON = 14.40 

st.title("🏠 2026 Yılı Yaşam Maliyeti Tahmin Paneli")

# --- 🕹️ KULLANICI ARAYÜZÜ (SOL TARAF) ---
st.sidebar.header("🎯 Senaryo Girişi")
user_profile = st.sidebar.selectbox("Profiliniz:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"])
st.sidebar.divider()

gida = st.sidebar.slider("🛒 Market/Gıda (%)", 0, 100, 0)
kira = st.sidebar.slider("🏠 Kira/Konut (%)", 0, 100, 0)
ulasim = st.sidebar.slider("🚗 Ulaşım (%)", 0, 100, 0)
diger = st.sidebar.slider("🎭 Diğer (%)", 0, 100, 0)

korku = st.sidebar.selectbox("Temel Endişe:", ["Gıda Fiyatları", "Kira Artışı", "Akaryakıt Zamları", "Eğitim/Sağlık"])

# Hesaplama Mantığı
weights = {"Öğrenci": [0.3, 0.4, 0.2, 0.1], "Emekli": [0.5, 0.2, 0.1, 0.2], "Çalışan": [0.3, 0.3, 0.2, 0.2], "Kamu Personeli": [0.3, 0.3, 0.2, 0.2], "Esnaf": [0.2, 0.3, 0.3, 0.2]}
w = weights[user_profile]
tahmin = BAZ_ENFLASYON + (gida * w[0] + kira * w[1] + ulasim * w[2] + diger * w[3])

# Kullanıcı Ana Ekranı
st.subheader("🏁 Kişisel Senaryo Sonucunuz")
res1, res2, res3 = st.columns(3)
res1.metric("📊 Seçilen Profil", user_profile)
res2.metric("🎯 TCMB 2026 Hedefi", f"%{TCMB_2026_HEDEF}")
res3.metric("📈 Yıl Sonu Tahmininiz", f"%{tahmin:.2f}", f"{tahmin-TCMB_2026_HEDEF:.2f} Sapma", delta_color="inverse")

if st.button("🚀 Tahminimi Sisteme Kaydet"):
    save_to_csv(user_profile, tahmin, korku)
    st.success("Veriler başarıyla havuzda toplandı!")

# --- 🛡️ GENİŞLETİLMİŞ YÖNETİCİ PANELİ ---
st.sidebar.divider()
with st.sidebar.expander("🔐 Yönetici Paneli (Geniş Görünüm)"):
    sifre = st.text_input("Şifre", type="password")
    if sifre == "alper2026":
        admin_active = True
    else:
        admin_active = False

if admin_active:
    st.divider()
    st.header("📂 Stratejik Analiz Raporu")
    
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        
        # 1. BÜYÜK ÖZET KARTLARI (Ferah Yerleşim)
        st.markdown("### 🌍 Genel Görünüm")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Toplam Katılım", f"{len(df)} Kişi")
        m2.metric("Genel Beklenti Ort.", f"%{df['beklenen_enflasyon'].mean():.2f}")
        m3.metric("En Düşük Tahmin", f"%{df['beklenen_enflasyon'].min():.2f}")
        m4.metric("En Yüksek Tahmin", f"%{df['beklenen_enflasyon'].max():.2f}")

        st.divider()

        # 2. GRUP ANALİZLERİ (Sol: Tablo, Sağ: Grafik)
        col_left, col_right = st.columns([1, 1.5])
        
        with col_left:
            st.write("#### 📊 Grup Bazlı Detaylar")
            grup_df = df.groupby("profil")["beklenen_enflasyon"].agg(['mean', 'count']).reset_index()
            grup_df.columns = ['Meslek/Grup', 'Ort. Beklenti (%)', 'Katılımcı']
            st.dataframe(grup_df.style.format("{:.2f}", subset=['Ort. Beklenti (%)']), use_container_width=True)

        with col_right:
            st.write("#### 📈 Grupların Tahmin Dağılımı")
            st.bar_chart(df.groupby("profil")["beklenen_enflasyon"].mean(), use_container_width=True)

        st.divider()

        # 3. KORKU VE ENDİŞE ANALİZİ
        st.write("#### 🚨 Toplumun Temel Risk Algısı (Korkular)")
        korku_data = df['en_cok_korkulan'].value_counts()
        st.bar_chart(korku_data)

        # 4. HAM VERİ LİSTESİ (Sayfanın En Altında, Geniş)
        st.divider()
        with st.expander("📝 Tüm Kayıtları Listele ve Düzenle"):
            st.dataframe(df, use_container_width=True)
            
            # Silme İşlemi
            st.write("---")
            c_del1, c_del2 = st.columns([2, 1])
            with c_del1:
                silme_id = st.selectbox("Silmek istediğiniz kaydın zaman damgasını seçin:", df['tarih'].tolist())
            with c_del2:
                if st.button("🗑️ Kaydı Sistemden Sil"):
                    df = df[df.tarih != silme_id]
                    df.to_csv(DB_FILE, index=False)
                    st.warning("Kayıt silindi, sayfa güncelleniyor...")
                    st.rerun()
    else:
        st.info("Sistemde henüz toplanmış veri bulunmamaktadır.")
