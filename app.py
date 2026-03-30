import streamlit as st
import pandas as pd
import requests
import re

# --- 📡 CANLI VERİ ÇEKİCİ (Google Finance) ---
def get_live_usd():
    try:
        url = "https://www.google.com/finance/quote/USD-TRY"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        # Regex ile HTML içinden canlı fiyat hücresini buluyoruz
        match = re.search(r'class="YMlKec fxKbKc">([\d,.]+)<', res.text)
        if match:
            return float(match.group(1).replace(",", ""))
        return 33.15 # Regex bulamazsa yedek
    except:
        return 33.15 # İnternet koparsa yedek

# Uygulama Başladığında Canlı Kuru Al
CANLI_DOLAR = get_live_usd()
BAZ_ENF = 31.53
BAZ_FAIZ = 37.0
YIL_SONU_HEDEF = 36.0

st.set_page_config(page_title="Alper Ekonomi Sim v6", layout="wide")

st.title("📈 Alper'in Canlı Ekonomi Simülatörü")
st.write(f"📡 **Sistemdeki Canlı Dolar Kuru:** {CANLI_DOLAR} TL")
st.divider()

# --- 🕹️ YAN PANEL ---
st.sidebar.header("Senaryo Ayarları")
dolar_artis_yuzde = st.sidebar.slider("Dolar Artış Beklentisi (%)", -5, 100, 10)
ucret_zammi = st.sidebar.slider("Yıllık Ücret Zammı (%)", 0, 100, 25)
faiz_hamlesi = st.sidebar.slider("Faiz Hamlesi (Puan)", -15, 25, 0)
butce_etkisi = st.sidebar.slider("Ek Bütçe Açığı / GSYH (%)", 0.0, 10.0, 3.0, 0.5)

# --- 🧮 HESAPLAMA ---
kur_puan = dolar_artis_yuzde * 0.40
ucret_puan = ucret_zammi * 0.20
faiz_puan = faiz_hamlesi * -0.15
butce_puan = butce_etkisi * 0.50

yil_sonu_tahmin = BAZ_ENF + kur_puan + ucret_puan + faiz_puan + butce_puan
hedef_kur = CANLI_DOLAR * (1 + dolar_artis_yuzde/100)

# --- 📊 DASHBOARD ---
c1, c2, c3 = st.columns(3)
c1.metric("Yıl Sonu Enflasyon", f"%{yil_sonu_tahmin:.2f}", f"{yil_sonu_tahmin - YIL_SONU_HEDEF:.2f} Sapma")
c2.metric("Senaryo Dolar Kuru", f"{hedef_kur:.2f} TL")
c3.metric("Yeni Politika Faizi", f"%{BAZ_FAIZ + faiz_hamlesi:.1f}")

st.bar_chart(pd.DataFrame({
    'Etken': ['Kur', 'Ücret', 'Bütçe', 'Faiz (Fren)'],
    'Puan': [kur_puan, ucret_puan, butce_puan, faiz_puan]
}).set_index('Etken'))
