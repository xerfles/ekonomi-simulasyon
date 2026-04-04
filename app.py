import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 📁 VERİ SAKLAMA ---
DB_FILE = 'beklenti_havuzu.csv'

def save_to_csv(profil, beklenti_9ay, toplam, dolar_artis, korku):
    new_data = pd.DataFrame([[
        datetime.now().strftime("%Y-%m-%d %H:%M"), 
        profil, beklenti_9ay, toplam, dolar_artis, korku
    ]], columns=['tarih', 'profil', 'beklenti_9ay', 'toplam_yıl_sonu', 'dolar_artis_beklentisi', 'en_cok_korkulan'])
    
    if not os.path.isfile(DB_FILE):
        new_data.to_csv(DB_FILE, index=False)
    else:
        new_data.to_csv(DB_FILE, mode='a', index=False, header=False)

# --- 📊 GÜNCEL EKONOMİK VERİLER (5 Nisan 2026) ---
GUNCEL_DOLAR_KURU = 44.92
ILK_CEYREK_ENF = 14.40
TCMB_2026_HEDEF = 22.0

# Gelişmiş Tarihsel Veri Seti
GECMIS_VERILER = {
    "Yıl": ["2022", "2023", "2024", "2025"],
    "Enflasyon (%)": ["%64.27", "%64.77", "%44.81", "%32.10"],
    "Yıl Sonu Dolar (TL)": ["18.70 TL", "29.50 TL", "34.20 TL", "41.10 TL"],
    "Yıllık Dolar Artışı": ["+%93.9", "+%57.7", "+%15.9", "+%20.2"],
    "Fiyat Değişimi": ["+5.78 TL", "+10.80 TL", "+4.70 TL", "+6.90 TL"]
}

# --- ⚙️ SAYFA AYARLARI ---
st.set_page_config(page_title="Hanehalkı Beklenti Paneli", layout="wide")

# Üst Bilgi Alanı
st.title("🏠 2026 Yılı Hanehalkı Enflasyon Beklenti Anketi")
inf_col1, inf_col2, inf_col3 = st.columns(3)
inf_col1.warning(f"💵 **Güncel Dolar Kuru:** {GUNCEL_DOLAR_KURU} TL")
inf_col2.info(f"📊 **İlk Çeyrek Enflasyon:** %{ILK_CEYREK_ENF}")
inf_col3.success(f"🎯 **TCMB Yıl Sonu Hedefi:** %{TCMB_2026_HEDEF}")

st.divider()

# --- 🕹️ KENAR ÇUBUĞU ---
st.sidebar.header("🎯 Senaryo Oluştur")
user_profile = st.sidebar.selectbox("Sosyal Profiliniz:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"])

st.sidebar.divider()
st.sidebar.write("**📈 Nisan-Aralık Artış Beklentiniz (%)**")
dolar_artis = st.sidebar.slider("💵 Dolar Kuru (%)", 0, 100, 0)
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

# --- 🏁 ANA EKRAN ---
# Özet Metrikler
st.subheader("🏁 Tahmin Sonuçlarınız")
m1, m2, m3, m4 = st.columns(4)
m1.metric("9 Aylık Beklenti", f"%{beklenti_9ay:.2f}")
m2.metric("Yıl Sonu Toplam", f"%{toplam_yıl_sonu:.2f}")
m3.metric("Tahmini Dolar", f"{GUNCEL_DOLAR_KURU * (1 + dolar_artis/100):.2f} TL")
sapma = toplam_yıl_sonu - TCMB_2026_HEDEF
m4.metric("Hedef Sapması", f"{sapma:+.2f} Puan", delta_color="inverse")

st.divider()

# Tarihsel Veri Tablosu
st.subheader("📜 Tarihsel Verilerle Kıyaslama (2022-2025)")
st.write("Aşağıdaki tablo, geçmiş yıllardaki dolar ve enflasyon hareketlerini özetlemektedir:")
hist_df = pd.DataFrame(GECMIS_VERILER).set_index("Yıl")
st.table(hist_df)

st.divider()

# Kayıt
if st.button("🚀 Tahminimi Veri Havuzuna Gönder"):
    save_to_csv(user_profile, beklenti_9ay, toplam_yıl_sonu, dolar_artis, korku)
    st.success("Verileriniz başarıyla kaydedildi. Analize katkınız için teşekkürler!")

# --- 🛡️ YÖNETİCİ PANELİ ---
st.sidebar.divider()
with st.sidebar.expander("🔐 Yönetici"):
    if st.text_input("Şifre", type="password") == "alper2026":
        if os.path.exists(DB_FILE):
            df = pd.read_csv(DB_FILE)
            st.write(f"**Toplam Katılım:** {len(df)}")
            st.dataframe(df)
