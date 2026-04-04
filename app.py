import streamlit as st
import pandas as pd
import requests
import re
import sqlite3
from datetime import datetime

# --- 🗄️ 1. VERİ TABANI ---
def init_db():
    conn = sqlite3.connect('beklenti_havuzu.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS anket 
                 (tarih TEXT, profil TEXT, beklenen_enflasyon REAL, en_cok_korkulan TEXT)''')
    conn.commit()
    conn.close()

def save_survey(profil, enflasyon, korku):
    conn = sqlite3.connect('beklenti_havuzu.db')
    c = conn.cursor()
    c.execute("INSERT INTO anket VALUES (?, ?, ?, ?)", (datetime.now().strftime("%Y-%m-%d %H:%M"), profil, enflasyon, korku))
    conn.commit()
    conn.close()

# --- 📡 2. CANLI VERİ & SABİTLER ---
TCMB_2026_HEDEF = 22.0
GECMIS_VERI = {"2023": 64.77, "2024": 44.81, "2025": 32.10} # Örnek tarihsel veriler

# --- ⚙️ 3. AYARLAR ---
st.set_page_config(page_title="2026 Finansal Simülatör", layout="wide")
init_db()

st.title("🏠 2026 Yılı Yaşam Maliyeti ve Maaş Koruma Simülatörü")
st.markdown("---")

# --- 🕹️ 4. KENAR ÇUBUĞU (GELİŞMİŞ GİRDİLER) ---
st.sidebar.header("🎯 Senaryonuzu Oluşturun")

user_profile = st.sidebar.selectbox("Profiliniz:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"])
maas = st.sidebar.number_input("Mevcut Aylık Geliriniz (TL):", min_value=0, value=25000, step=500)

st.sidebar.divider()
st.sidebar.write("**Nisan-Aralık Tahminleriniz (%)**")

# Özellik 2: Harcama Sepeti Özelleştirme (Checkbox ile)
custom_weights = st.sidebar.checkbox("Ağırlıkları Ben Belirlemek İstiyorum")

if custom_weights:
    w_gida = st.sidebar.slider("Gıda Ağırlığı (%)", 0, 100, 30) / 100
    w_kira = st.sidebar.slider("Kira Ağırlığı (%)", 0, 100, 30) / 100
    w_ulasim = st.sidebar.slider("Ulaşım Ağırlığı (%)", 0, 100, 20) / 100
    w_diger = 1.0 - (w_gida + w_kira + w_ulasim)
    st.sidebar.caption(f"Diğer Kalemi: %{w_diger*100:.0f}")
else:
    weights = {
        "Öğrenci": {"gida": 0.30, "kira": 0.40, "ulasim": 0.20, "diger": 0.10},
        "Emekli": {"gida": 0.50, "kira": 0.20, "ulasim": 0.10, "diger": 0.20},
        "Çalışan": {"gida": 0.25, "kira": 0.35, "ulasim": 0.20, "diger": 0.20},
        "Kamu Personeli": {"gida": 0.30, "kira": 0.30, "ulasim": 0.20, "diger": 0.20},
        "Esnaf": {"gida": 0.20, "kira": 0.30, "ulasim": 0.30, "diger": 0.20}
    }
    w_gida, w_kira, w_ulasim, w_diger = weights[user_profile].values()

gida_artisi = st.sidebar.slider("Market/Pazar (%)", 0, 100, 0)
kira_artisi = st.sidebar.slider("Kira/Aidat (%)", 0, 100, 0)
ulasim_artisi = st.sidebar.slider("Ulaşım (%)", 0, 100, 0)
diger_artisi = st.sidebar.slider("Giyim/Eğlence (%)", 0, 100, 0)

korku_faktoru = st.sidebar.selectbox("En Büyük Risk:", ["Gıda", "Kira", "Akaryakıt", "Maaş Erimesi"])

# --- 🧮 5. HESAPLAMALAR ---
BAZ_ENFLASYON = 14.40
hissedilen_ek = (gida_artisi * w_gida) + (kira_artisi * w_kira) + (ulasim_artisi * w_ulasim) + (diger_artisi * w_diger)
tahmin = BAZ_ENFLASYON + hissedilen_ek

# Özellik 1: Maaş Erimesi Analizi
reel_deger = maas / (1 + (tahmin/100))
erime_miktari = maas - reel_deger

# --- 📊 6. SONUÇLAR ---
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("🏁 Senaryo Özeti")
    res_col1, res_col2, res_col3 = st.columns(3)
    
    # Özellik 3: Enflasyon Canavarı (Görsel Uyarılar)
    if tahmin < TCMB_2026_HEDEF: status, color = "🔵 İyimser", "blue"
    elif tahmin <= 40: status, color = "🟢 Dengeli", "green"
    elif tahmin <= 60: status, color = "🟠 Riskli", "orange"
    else: status, color = "🔴 Hiper-Baskı", "red"
    
    res_col1.metric("Senaryo Tipi", status)
    res_col2.metric("TCMB Hedefi", f"%{TCMB_2026_HEDEF}")
    res_col3.metric("Sizin Tahmininiz", f"%{tahmin:.2f}", f"{tahmin-TCMB_2026_HEDEF:.2f} Sapma", delta_color="inverse")

    # Özellik 1 Devamı: Maaş Analizi Görselleştirme
    st.info(f"💰 **Satın Alma Gücü Analizi:** Yıl sonu tahmininiz gerçekleşirse, bugünkü **{maas:,.0g} TL** maaşınızın alım gücü yıl sonunda **{reel_deger:,.0g} TL** seviyesine gerileyecektir. (Kayıp: {erime_miktari:,.0g} TL)")

with c2:
    # Özellik 4: Tarihsel Kıyaslama
    st.subheader("📜 Tarihsel Kıyas")
    df_history = pd.DataFrame({
        "Yıl": ["2023", "2024", "2025", "2026 (Siz)"],
        "Enflasyon (%)": [64.77, 44.81, 32.10, tahmin]
    })
    st.bar_chart(df_history.set_index("Yıl"))

# --- 💾 7. VERİ GÖNDERME ---
st.divider()
if st.button("🚀 Tahminimi Havuza Kaydet"):
    save_survey(user_profile, tahmin, korku_faktoru)
    st.success("Veriler kaydedildi! Pilot çalışmaya katkınız için teşekkürler.")

# --- 🛡️ 8. GİZLİ YÖNETİCİ GİRİŞİ ---
st.sidebar.divider()
with st.sidebar.expander("🔐 Yönetici Girişi"):
    sifre = st.text_input("Şifre", type="password")
    if sifre == "alper2026":
        st.divider()
        st.header("📂 Yönetici Analiz Paneli")
        conn = sqlite3.connect('beklenti_havuzu.db')
        df = pd.read_sql_query("SELECT * FROM anket", conn)
        conn.close()
        if not df.empty:
            st.write(f"**Ortalama Toplum Tahmini:** %{df['beklenen_enflasyon'].mean():.2f}")
            st.dataframe(df)
        else: st.info("Henüz veri yok.")
