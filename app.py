import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 📁 VERİ SAKLAMA ---
DB_FILE = 'beklenti_havuzu.csv'

def save_to_csv(isim, profil, beklenti_9ay, toplam, dolar_artis, korku):
    new_data = pd.DataFrame([[
        datetime.now().strftime("%Y-%m-%d %H:%M"), 
        isim, profil, beklenti_9ay, toplam, dolar_artis, korku
    ]], columns=['tarih', 'isim', 'profil', 'beklenti_9ay', 'toplam_yıl_sonu', 'dolar_artis_beklentisi', 'en_cok_korkulan'])
    
    if not os.path.isfile(DB_FILE):
        new_data.to_csv(DB_FILE, index=False)
    else:
        new_data.to_csv(DB_FILE, mode='a', index=False, header=False)

# --- 📊 GÜNCEL EKONOMİK VERİLER ---
GUNCEL_DOLAR_KURU = 44.92
ILK_CEYREK_ENF = 14.40
TCMB_2026_HEDEF = 22.0

GECMIS_VERILER = {
    "Yıl": ["2022", "2023", "2024", "2025"],
    "Enflasyon (%)": ["%64.27", "%64.77", "%44.81", "%32.10"],
    "Yıl Sonu Dolar (TL)": ["18.70 TL", "29.50 TL", "34.20 TL", "41.10 TL"],
    "Yıllık Dolar Artışı": ["+%93.9", "+%57.7", "+%15.9", "+%20.2"],
    "Fiyat Değişimi": ["+5.78 TL", "+10.80 TL", "+4.70 TL", "+6.90 TL"]
}

# --- ⚙️ SAYFA AYARLARI ---
st.set_page_config(page_title="Hanehalkı Beklenti Paneli", layout="wide")

st.title("🏠 2026 Yılı Hanehalkı Enflasyon Beklenti Anketi")
inf_col1, inf_col2, inf_col3 = st.columns(3)
inf_col1.warning(f"💵 **Güncel Dolar Kuru:** {GUNCEL_DOLAR_KURU} TL")
inf_col2.info(f"📊 **Ocak-Mart Dönemi (Gerçekleşen):** %{ILK_CEYREK_ENF}")
inf_col3.success(f"🎯 **TCMB Yıl Sonu Hedefi:** %{TCMB_2026_HEDEF}")

st.divider()

# --- 🕹️ KENAR ÇUBUĞU ---
st.sidebar.header("👤 Katılımcı Bilgisi")
user_name = st.sidebar.text_input("İsminiz (Veya Takma Adınız):", placeholder="Örn: Alper")

st.sidebar.divider()
st.sidebar.header("🎯 Senaryo Oluştur")
user_profile = st.sidebar.selectbox("Sosyal Profiliniz:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"])

st.sidebar.divider()
st.sidebar.write("**📈 Nisan-Aralık Artış Beklentiniz (%)**")
dolar_artis = st.sidebar.slider("💵 Dolar Kuru Artışı (%)", 0, 100, 0)
gida = st.sidebar.slider("🛒 Gıda ve Market (%)", 0, 100, 0)
kira = st.sidebar.slider("🏠 Kira ve Konut (%)", 0, 100, 0)
ulasim = st.sidebar.slider("🚗 Ulaşım ve Akaryakıt (%)", 0, 100, 0)
diger = st.sidebar.slider("🎭 Diğer Harcamalar (%)", 0, 100, 0)

korku = st.sidebar.selectbox("En Büyük Endişe:", ["Gıda Fiyatları", "Kira Artışı", "Döviz Kuru", "Alım Gücü"])

# --- 🧮 HESAPLAMA ---
weights = {"Öğrenci": [0.2, 0.25, 0.35, 0.15, 0.05], "Emekli": [0.15, 0.45, 0.15, 0.10, 0.15], "Çalışan": [0.2, 0.25, 0.25, 0.15, 0.15], "Kamu Personeli": [0.2, 0.25, 0.25, 0.15, 0.15], "Esnaf": [0.3, 0.2, 0.2, 0.2, 0.1]}
w = weights[user_profile]
beklenti_9ay = (dolar_artis * w[0] + gida * w[1] + kira * w[2] + ulasim * w[3] + diger * w[4])
toplam_yıl_sonu = ILK_CEYREK_ENF + beklenti_9ay
tahmini_dolar_sonu = GUNCEL_DOLAR_KURU * (1 + dolar_artis/100)

# --- 🏁 ANA EKRAN ---
st.subheader("🏁 Tahmin Sonuçlarınız")
m1, m2, m3, m4 = st.columns(4)
m1.metric("📊 Ocak-Mart (Gerçekleşen)", f"%{ILK_CEYREK_ENF}")
m2.metric("🔮 Sizin 9 Aylık Beklentiniz", f"%{beklenti_9ay:.2f}")
m3.metric("📈 Toplam Yıl Sonu Tahmininiz", f"%{toplam_yıl_sonu:.2f}")
m4.metric("💵 Yıl Sonu Tahmini Dolar", f"{tahmini_dolar_sonu:.2f} TL", f"%{dolar_artis} Artış")

st.divider()

# Tarihsel Veri Tablosu
st.subheader("📜 Tarihsel Verilerle Kıyaslama (2022-2025)")
hist_df = pd.DataFrame(GECMIS_VERILER).set_index("Yıl")
st.table(hist_df)

st.divider()

if st.button("🚀 Tahminimi Veri Havuzuna Gönder"):
    if user_name.strip() == "":
        st.error("Lütfen devam etmek için bir isim giriniz!")
    else:
        save_to_csv(user_name, user_profile, beklenti_9ay, toplam_yıl_sonu, dolar_artis, korku)
        st.success(f"Teşekkürler {user_name}, tahminin başarıyla kaydedildi!")

# --- 🛡️ YÖNETİCİ PANELİ (GELİŞMİŞ GRAFİKLİ) ---
st.sidebar.divider()
st.sidebar.subheader("🔐 Yönetici Erişimi")
sifre = st.sidebar.text_input("Yönetici Şifresi", type="password")

if sifre == "alper2026":
    st.divider()
    st.header("📂 Detaylı Analiz Paneli")
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        
        # Üst Metrikler
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Toplam Katılım", f"{len(df)} Kişi")
        c2.metric("Ort. Enflasyon (9 Ay)", f"%{df['beklenti_9ay'].mean():.2f}")
        c3.metric("Ort. Yıl Sonu Tahmini", f"%{df['toplam_yıl_sonu'].mean():.2f}")
        c4.metric("Ort. Dolar Artışı", f"%{df['dolar_artis_beklentisi'].mean():.2f}")
        
        st.divider()
        st.subheader("📋 Kayıt Yönetimi")
        st.dataframe(df, use_container_width=True)
        
        st.write("#### 🗑️ Veri Temizleme")
        row_to_delete = st.number_input("Silmek istediğiniz satır no:", min_value=0, max_value=len(df)-1, step=1)
        if st.button(f"❌ {row_to_delete} Numaralı Kaydı Sil"):
            df = df.drop(df.index[row_to_delete])
            df.to_csv(DB_FILE, index=False)
            st.rerun()

        st.divider()
        
        # İSTEDİĞİN YENİ GRAFİKLER BURADA
        st.subheader("📊 İstatistiksel Dağılımlar")
        g1, g2, g3 = st.columns(3)
        
        with g1:
            st.write("**👨‍👩‍👧‍👦 Katılımcı Profili Dağılımı**")
            st.bar_chart(df['profil'].value_counts())
            
        with g2:
            st.write("**📈 Grupların Tahmin Ortalaması**")
            st.bar_chart(df.groupby("profil")["toplam_yıl_sonu"].mean())
            
        with g3:
            st.write("**😨 En Çok Korkulan Harcamalar**")
            st.bar_chart(df['en_cok_korkulan'].value_counts())

    else:
        st.info("Henüz veri girişi yapılmadı.")
