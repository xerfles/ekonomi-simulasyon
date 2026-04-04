import streamlit as st
import pandas as pd
import requests
import re

# --- 📡 CANLI VERİ ÇEKİCİ (4 NİSAN 2026) ---
def get_live_usd():
    try:
        url = "https://www.google.com/finance/quote/USD-TRY"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        match = re.search(r'class="YMlKec fxKbKc">([\d,.]+)<', res.text)
        return float(match.group(1).replace(",", ""))
    except:
        return 44.88 

# --- ⚙️ AYARLAR ---
st.set_page_config(page_title="2026 Ekonomi Simülatörü v10", layout="wide")
CANLI_DOLAR = get_live_usd()
BIRIKMIS_ENF = 14.40 # Ocak-Mart 2026
RESMI_HEDEF = 22.0
MEVCUT_FAIZ = 37.0

st.title("🏛️ 2026 Türkiye Makroekonomik Strateji Matrisi")
st.markdown(f"📡 **Anlık Veri:** 4 Nisan 2026 | **Dolar/TL:** {CANLI_DOLAR} | **Politika Faizi:** %{MEVCUT_FAIZ}")

# --- 🕹️ YAN PANEL (TÜM DEĞİŞKENLER) ---
st.sidebar.header("🕹️ Ekonomi Kumanda Masası")

with st.sidebar.expander("💵 Döviz ve Dışsal Şoklar", expanded=True):
    kur = st.slider("Kur Artışı (%)", -5, 50, 10)
    petrol = st.slider("Brent Petrol Şoku (%)", -20, 60, 5)
    fed = st.slider("Fed Faiz Baskısı (%)", -5, 15, 3)
    soklar = st.slider("Jeopolitik Riskler (%)", -10, 50, 5)

with st.sidebar.expander("👷 Ücret ve Maliyetler"):
    ucret = st.slider("Ücret Zamları (%)", 0, 60, 20)
    mazot = st.slider("Mazot/Nakliye Artışı (%)", -10, 60, 15)
    gubre = st.slider("Gübre/Tohum (Tarım) (%)", 0, 80, 20)
    araci = st.slider("Aracı/Komisyoncu Kârı (%)", 0, 50, 10)

with st.sidebar.expander("🏛️ Kamu ve Psikoloji"):
    fiyat_algisi = st.slider("Fiyat Algısı Bozulması (%)", 0, 40, 15)
    vergi = st.slider("Vergi Artışları (Puan)", 0, 30, 5)
    butce = st.slider("Bütçe Açığı Etkisi (%)", 0, 30, 5)
    kira = st.slider("Kira/Konut Baskısı (%)", 0, 60, 15)
    guven = st.select_slider("Kurumsal Güven", options=range(11), value=5)
    baz = st.slider("Baz Etkisi (Puan)", -10, 10, 0)

# --- 🧮 HESAP MOTORU ---
e_kur = kur * 0.38
e_mazot = mazot * 0.12
e_gubre = gubre * 0.10
e_araci = araci * 0.08
e_algı = fiyat_algisi * 0.22
e_ucret = ucret * 0.25
e_vergi = vergi * 0.15
e_butce = butce * 0.12
e_kira = kira * 0.18
e_fed = fed * 0.07
e_guven = (5 - guven) * 0.85
e_baz = baz * 1.0
e_soklar = petrol * 0.15 + soklar * 0.10

toplam_etki = e_kur + e_mazot + e_gubre + e_araci + e_algı + e_ucret + e_vergi + e_butce + e_kira + e_fed + e_guven + e_baz + e_soklar
yil_sonu_final = BIRIKMIS_ENF + toplam_etki

# --- 📊 DASHBOARD ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Yıl Sonu Tahmini", f"%{yil_sonu_final:.2f}", f"{yil_sonu_final - RESMI_HEDEF:.2f} Sapma", delta_color="inverse")
c2.metric("Nisan-Aralık Etkisi", f"+%{toplam_etki:.2f}")
c3.metric("Tahmini Reel Faiz", f"%{MEVCUT_FAIZ - yil_sonu_final:.1f}")
c4.metric("Senaryo Doları", f"{CANLI_DOLAR * (1 + kur/100):.2f} TL")

st.divider()

# --- 📉 ETKİ ANALİZİ GRAFİĞİ ---
st.subheader("🔍 Enflasyonu Tetikleyen Unsurların Dağılımı")
chart_data = pd.DataFrame({
    'Faktör': ['Kur', 'Ücret', 'Gıda/Tarım', 'Psikoloji', 'Kamu/Vergi', 'Kira', 'Güven/Baz', 'Dış Şoklar'],
    'Katkı (Puan)': [e_kur, e_ucret, e_gida_toplam := (e_gubre + e_araci), e_algı, e_vergi + e_butce, e_kira, e_guven + e_baz, e_soklar + e_fed]
}).set_index('Faktör')

st.bar_chart(chart_data)

# --- 📝 ANALİZ NOTLARI ---
col_a, col_b = st.columns(2)
with col_a:
    st.info(f"📌 **Gerçekleşen Veri:** 2026'nın ilk 3 ayında (Ocak-Mart) enflasyon %{BIRIKMIS_ENF} olarak realize oldu. Yılın geri kalanında hedefe ulaşmak için alanın daralıyor.")
with col_b:
    if guven < 4:
        st.error("🚨 **Güven Krizi:** Kurumsal güven düşük olduğu için para politikası etkisiz kalıyor. Psikolojik zamlar enflasyonu besliyor.")
    elif yil_sonu_final <= RESMI_HEDEF:
        st.success("🎯 **Hedef Uyumu:** Tebrikler! Tüm makro dengeleri gözeterek resmi hedefi yakaladın.")
