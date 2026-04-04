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

# Üst Bilgi Metrikleri
inf_col1, inf_col2, inf_col3 = st.columns(3)
inf_col1.warning(f"💵 **Güncel Dolar Kuru:** {GUNCEL_DOLAR_KURU} TL")
inf_col2.info(f"📊 **Ocak-Mart (Gerçekleşen):** %{ILK_CEYREK_ENF}")
inf_col3.success(f"🎯 **TCMB Yıl Sonu Hedefi:** %{TCMB_2026_HEDEF}")

st.divider()

# --- 📜 TARİHSEL VERİLER (YUKARI TAŞINDI) ---
st.subheader("📜 Tarihsel Verilerle Ekonomi Karnesi (2022-2025)")
st.write("Tahmininizi yapmadan önce geçmiş yıllardaki dolar ve enflasyon hareketlerini inceleyebilirsiniz:")
hist_df = pd.DataFrame(GECMIS_VERILER).set_index("Yıl")
st.table(hist_df)

st.divider()

# --- 🎯 SENARYO OLUŞTURMA ---
st.subheader("⚙️ Kendi Senaryonuzu Oluşturun")
c_user1, c_user2 = st.columns(2)

with c_user1:
    user_name = st.text_input("👤 İsminiz (Veya Takma Adınız):", placeholder="Örn: Alper")
    user_profile = st.selectbox("💼 Sosyal Profiliniz:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"])
    korku = st.selectbox("😨 En Büyük Endişe Noktanız:", ["Gıda Fiyatları", "Kira Artışı", "Döviz Kuru", "Alım Gücü"])

with c_user2:
    st.write("**📈 Nisan-Aralık Artış Beklentiniz (%)**")
    dolar_artis = st.slider("💵 Dolar Kuru (%)", 0, 100, 0)
    gida = st.slider("🛒 Gıda ve Market (%)", 0, 100, 0)
    kira = st.slider("🏠 Kira ve Konut (%)", 0, 100, 0)
    ulasim = st.slider("🚗 Ulaşım (%)", 0, 100, 0)
    diger = st.slider("🎭 Diğer (%)", 0, 100, 0)

# --- 🧮 HESAPLAMA ---
weights = {"Öğrenci": [0.2, 0.25, 0.35, 0.15, 0.05], "Emekli": [0.15, 0.45, 0.15, 0.10, 0.15], "Çalışan": [0.2, 0.25, 0.25, 0.15, 0.15], "Kamu Personeli": [0.2, 0.25, 0.25, 0.15, 0.15], "Esnaf": [0.3, 0.2, 0.2, 0.2, 0.1]}
w = weights[user_profile]
beklenti_9ay = (dolar_artis * w[0] + gida * w[1] + kira * w[2] + ulasim * w[3] + diger * w[4])
toplam_yıl_sonu = ILK_CEYREK_ENF + beklenti_9ay
tahmini_dolar_sonu = GUNCEL_DOLAR_KURU * (1 + dolar_artis/100)

st.divider()

# --- 🏁 SONUÇLAR VE KAYDET BUTONU ---
st.subheader("🏁 Tahmin Sonuçlarınız")
m1, m2, m3, m4 = st.columns(4)
m1.metric("📊 Ocak-Mart (Net)", f"%{ILK_CEYREK_ENF}")
m2.metric("🔮 9 Aylık Beklentiniz", f"%{beklenti_9ay:.2f}")
m3.metric("📈 Yıl Sonu Toplam", f"%{toplam_yıl_sonu:.2f}")
m4.metric("💵 Yıl Sonu Dolar", f"{tahmini_dolar_sonu:.2f} TL")

st.write("")
# Buton daha belirgin ve yukarıda
if st.button("💾 VERİLERİMİ KAYDET VE ANALİZE KATIL", use_container_width=True, type="primary"):
    if user_name.strip() == "":
        st.error("Lütfen isminizi giriniz!")
    else:
        save_to_csv(user_name, user_profile, beklenti_9ay, toplam_yıl_sonu, dolar_artis, korku)
        st.success(f"Teşekkürler {user_name}, tahminin başarıyla kaydedildi!")

# --- 🛡️ YÖNETİCİ PANELİ ---
with st.sidebar:
    st.write("---" * 5)
    with st.expander("🔐 Admin Panel"):
        sifre = st.text_input("Şifre", type="password")

if sifre == "alper2026":
    st.divider()
    st.header("📂 Detaylı Analiz Paneli")
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        if not df.empty:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Toplam Katılım", f"{len(df)} Kişi")
            c2.metric("Ort. Enflasyon (9 Ay)", f"%{df['beklenti_9ay'].mean():.2f}")
            c3.metric("Ort. Yıl Sonu Tahmini", f"%{df['toplam_yıl_sonu'].mean():.2f}")
            c4.metric("Ort. Dolar Artışı", f"%{df['dolar_artis_beklentisi'].mean():.2f}")
            
            st.divider()
            st.subheader("📋 Kayıt Yönetimi")
            st.dataframe(df, use_container_width=True)
            
            st.write("#### 🗑️ Veri Temizleme")
            row_to_delete = st.number_input("Silmek istediğin satır:", min_value=0, max_value=len(df)-1, step=1)
            if st.button("❌ Kaydı Sil"):
                df = df.drop(df.index[row_to_delete])
                df.to_csv(DB_FILE, index=False)
                st.rerun()

            st.divider()
            st.subheader("📊 İstatistiksel Dağılımlar")
            g1, g2, g3 = st.columns(3)
            with g1: st.bar_chart(df['profil'].value_counts())
            with g2: st.bar_chart(df.groupby("profil")["toplam_yıl_sonu"].mean())
            with g3: st.bar_chart(df['en_cok_korkulan'].value_counts())
        else:
            st.warning("Veritabanı boş.")
