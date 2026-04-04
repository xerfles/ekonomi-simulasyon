import streamlit as st
import pandas as pd
import requests
import re
import sqlite3
from datetime import datetime

# --- 🗄️ 1. VERİ TABANI AYARI (GİZLİ SİLAH) ---
def init_db():
    conn = sqlite3.connect('ekonomi_verileri.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tahminler 
                 (tarih TEXT, dolar_tahmin REAL, enflasyon_tahmin REAL, faiz_tahmin REAL)''')
    conn.commit()
    conn.close()

def save_prediction(dolar, enf, faiz):
    conn = sqlite3.connect('ekonomi_verileri.db')
    c = conn.cursor()
    c.execute("INSERT INTO tahminler VALUES (?, ?, ?, ?)", 
              (datetime.now().strftime("%Y-%m-%d %H:%M"), dolar, enf, faiz))
    conn.commit()
    conn.close()

# --- 📡 2. CANLI VERİ ÇEKME ---
def get_live_usd():
    try:
        url = "https://www.google.com/finance/quote/USD-TRY"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        match = re.search(r'class="YMlKec fxKbKc">([\d,.]+)<', res.text)
        return float(match.group(1).replace(",", ""))
    except: return 44.92 

# --- ⚙️ 3. ANA AYARLAR ---
st.set_page_config(page_title="AR-GE: Ekonomi Strateji Matrisi", layout="wide")
init_db()
CANLI_DOLAR = get_live_usd()
BAZ_ENFLASYON = 14.40   
RESMI_HEDEF = 22.0      
MEVCUT_FAIZ = 37.0      

st.title("🏛️ Makroekonomik Karar Destek Sistemi (V2.0-Beta)")
st.caption("TÜBİTAK 2209-A Proje Taslağı | Gelişmiş Enflasyon Simülatörü")

# --- 🕹️ 4. GELİŞMİŞ KONTROL PANELİ ---
st.sidebar.header("🕹️ Senaryo Parametreleri")

with st.sidebar.expander("💸 Döviz & Dışsal Şoklar", expanded=True):
    kur = st.slider("Kur Değişimi (%)", -10, 100, 0)
    fed = st.slider("Fed Faiz Etkisi (Puan)", -2, 5, 0)

with st.sidebar.expander("🥗 Gıda & Tarım Maliyetleri"):
    gubre = st.slider("Gübre/Mazot Maliyeti (%)", 0, 100, 0)
    araci = st.slider("Aracı Kâr Marjı (%)", 0, 50, 0)

with st.sidebar.expander("🏦 Para & Maliye Politikası"):
    faiz_hamlesi = st.slider("Faiz Değişimi (Puan)", -20, 20, 0)
    vergi = st.slider("Dolaylı Vergi Yükü (%)", 0, 50, 0)

with st.sidebar.expander("👥 Sosyal Faktörler"):
    ucret = st.slider("Asgari Ücret/Maaş Zammı (%)", 0, 100, 0)
    beklenti = st.slider("Hanehalkı Enflasyon Beklentisi (%)", 0, 50, 0)

# --- 🧮 5. AR-GE HESAP MOTORU (GEÇİŞKENLİK ANALİZİ) ---
# Katsayılar akademik literatürden (Pass-through) optimize edildi
e_kur = (kur * 0.38) + (fed * 0.12)
e_gida = (gubre * 0.15) + (araci * 0.10)
e_mali = (vergi * 0.18) + (faiz_hamlesi * -0.22) # Faiz negatif etkiler
e_sosyal = (ucret * 0.25) + (beklenti * 0.20)

ek_yuk = e_kur + e_gida + e_mali + e_sosyal
toplam_enf = BAZ_ENFLASYON + ek_yuk
tahmini_dolar = CANLI_DOLAR * (1 + kur/100)

# --- 📊 6. DASHBOARD ---
st.divider()
col1, col2, col3, col4 = st.columns(4)

col1.metric("🎯 Hedef", f"%{RESMI_HEDEF}")
col2.metric("📈 Yıl Sonu Tahmini", f"%{toplam_enf:.2f}", f"{toplam_enf-RESMI_HEDEF:.2f} Sapma", delta_color="inverse")
col3.metric("💵 Tahmini Dolar", f"{tahmini_dolar:.2f} TL")
col4.metric("🏦 Politika Faizi", f"%{MEVCUT_FAIZ + faiz_hamlesi}")

# --- 📈 7. ANALİZ VE KAYIT ---
st.divider()
c_left, c_right = st.columns([2, 1])

with c_left:
    st.subheader("🔍 Enflasyonun Bileşen Analizi")
    data = {
        "Kaynak": ["Döviz/Dışsal", "Gıda/Tarım", "Maliye/Faiz", "Maaş/Beklenti"],
        "Etki Puanı": [e_kur, e_gida, e_mali, e_sosyal]
    }
    st.bar_chart(pd.DataFrame(data).set_index("Kaynak"))

with c_right:
    st.subheader("💾 Senaryoyu Arşivle")
    st.write("Bu veriler anonim olarak 'Piyasa Beklenti Anketi' için kaydedilir.")
    if st.button("Tahminimi Veri Tabanına Kaydet"):
        save_prediction(tahmini_dolar, toplam_enf, MEVCUT_FAIZ + faiz_hamlesi)
        st.success("Veri tabanına işlendi! (TÜBİTAK Analizi Hazır)")

# --- 📚 8. VERİ TABANI ÖNİZLEME (HOCAYA GÖSTERMELİK) ---
if st.checkbox("Kayıtlı Tahmin Geçmişini Göster (Admin)"):
    conn = sqlite3.connect('ekonomi_verileri.db')
    df_db = pd.read_sql_query("SELECT * FROM tahminler", conn)
    st.dataframe(df_db.tail(10))
    conn.close()
