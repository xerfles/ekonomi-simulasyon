import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 📁 VERİ SAKLAMA ---
DB_FILE = 'beklenti_havuzu.csv'

def save_to_csv(profil, beklenti_9ay, toplam, dolar_yuzde, korku):
    new_data = pd.DataFrame([[
        datetime.now().strftime("%Y-%m-%d %H:%M"), 
        profil, beklenti_9ay, toplam, dolar_yuzde, korku
    ]], columns=['tarih', 'profil', 'beklenti_9ay', 'toplam_yıl_sonu', 'dolar_artis_beklentisi', 'en_cok_korkulan'])
    
    if not os.path.isfile(DB_FILE):
        new_data.to_csv(DB_FILE, index=False)
    else:
        new_data.to_csv(DB_FILE, mode='a', index=False, header=False)

# --- 📊 RESMİ EKONOMİK VERİLER ---
ILK_CEYREK_GERCEKLESEN = 14.40
TCMB_2026_HEDEF = 22.0

GECMIS_VERILER = {
    "Yıl": ["2022", "2023", "2024", "2025"],
    "Enflasyon (%)": [64.27, 64.77, 44.81, 32.10],
    "Dolar Sonu (TL)": [18.70, 29.50, 34.20, 41.10]
}

# --- ⚙️ SAYFA AYARLARI ---
st.set_page_config(page_title="Hanehalkı Beklenti Anketi", layout="wide")

st.title("🏠 2026 Yılı Hanehalkı Enflasyon Beklenti Anketi")
st.markdown(f"**İlk Çeyrek (Gerçekleşen):** %{ILK_CEYREK_GERCEKLESEN} | **TCMB Yıl Sonu Hedefi:** %{TCMB_2026_HEDEF}")

# --- 🕹️ KENAR ÇUBUĞU ---
st.sidebar.header("🎯 Tahmin Parametreleri")
user_profile = st.sidebar.selectbox("Sosyal Profiliniz:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"])

st.sidebar.divider()
st.sidebar.write("**📈 Nisan-Aralık Beklenen Artışlar (%)**")

# Doları buraya çektik ve % slider yaptık
dolar_artis = st.sidebar.slider("💵 Dolar Kuru Artışı (%)", 0, 100, 0)
gida = st.sidebar.slider("🛒 Market/Gıda (%)", 0, 100, 0)
kira = st.sidebar.slider("🏠 Kira/Konut (%)", 0, 100, 0)
ulasim = st.sidebar.slider("🚗 Ulaşım (%)", 0, 100, 0)
diger = st.sidebar.slider("🎭 Diğer (%)", 0, 100, 0)

korku = st.sidebar.selectbox("En Büyük Risk Odağı:", ["Gıda Fiyatları", "Kira Artışı", "Döviz Kuru", "Alım Gücü Kaybı"])

# --- 🧮 HESAPLAMA (DOLAR DAHİL 5 KALEM) ---
# Dolar geçişkenliği ve kalem ağırlıkları
weights = {
    "Öğrenci": {"dolar": 0.20, "gida": 0.25, "kira": 0.35, "ulasim": 0.15, "diger": 0.05},
    "Emekli": {"dolar": 0.15, "gida": 0.45, "kira": 0.15, "ulasim": 0.10, "diger": 0.15},
    "Çalışan": {"dolar": 0.20, "gida": 0.25, "kira": 0.25, "ulasim": 0.15, "diger": 0.15},
    "Kamu Personeli": {"dolar": 0.20, "gida": 0.25, "kira": 0.25, "ulasim": 0.15, "diger": 0.15},
    "Esnaf": {"dolar": 0.30, "gida": 0.20, "kira": 0.20, "ulasim": 0.20, "diger": 0.10}
}

w = weights[user_profile]
beklenti_9ay = (dolar_artis * w["dolar"] + gida * w["gida"] + kira * w["kira"] + ulasim * w["ulasim"] + diger * w["diger"])
toplam_yıl_sonu = ILK_CEYREK_GERCEKLESEN + beklenti_9ay

# --- 📊 ANA EKRAN ---
st.divider()
c_main, c_side = st.columns([2, 1])

with c_main:
    st.subheader("🏁 Beklenti Özeti")
    m1, m2, m3 = st.columns(3)
    m1.metric("🔮 9 Aylık Tahmin", f"%{beklenti_9ay:.2f}")
    m2.metric("📈 Yıl Sonu Toplam", f"%{toplam_yıl_sonu:.2f}")
    
    sapma = toplam_yıl_sonu - TCMB_2026_HEDEF
    m3.metric("🎯 Hedef Sapması", f"{sapma:+.2f} Puan", delta_color="inverse")

    st.write("#### 📜 Yıllık Enflasyon Trendi (2022-2026)")
    enf_hist_df = pd.DataFrame({
        "Yıl": GECMIS_VERILER["Yıl"] + ["2026 (Siz)"],
        "Enflasyon (%)": GECMIS_VERILER["Enflasyon (%)"] + [toplam_yıl_sonu]
    })
    st.bar_chart(enf_hist_df.set_index("Yıl"))

    if st.button("🚀 Tahminimi Havuza Gönder"):
        save_to_csv(user_profile, beklenti_9ay, toplam_yıl_sonu, dolar_artis, korku)
        st.success("Veriler başarıyla kaydedildi!")

with c_side:
    st.write("#### 💡 Tahmin Analizi")
    st.write(f"Seçtiğiniz profile göre harcamalarınızda doların etkisi **%{w['dolar']*100:.0f}** olarak hesaplanmaktadır.")
    
    st.write("#### 📜 Geçmiş Yıl Enflasyonları")
    st.table(pd.DataFrame(GECMIS_VERILER).set_index("Yıl")[["Enflasyon (%)"]])

# --- 🛡️ YÖNETİCİ PANELİ ---
st.sidebar.divider()
with st.sidebar.expander("🔐 Yönetici Girişi"):
    if st.text_input("Şifre", type="password") == "alper2026":
        if os.path.exists(DB_FILE):
            df = pd.read_csv(DB_FILE)
            st.metric("Toplam Katılımcı", len(df))
            st.write("#### Grupların Yıl Sonu Tahminleri")
            st.bar_chart(df.groupby("profil")["toplam_yıl_sonu"].mean())
            st.dataframe(df)
