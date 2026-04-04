import streamlit as st
import pandas as pd
import requests
import re

# --- 📡 1. CANLI DOLAR KURUNU ÇEK ---
def get_live_usd():
    try:
        url = "https://www.google.com/finance/quote/USD-TRY"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        match = re.search(r'class="YMlKec fxKbKc">([\d,.]+)<', res.text)
        return float(match.group(1).replace(",", ""))
    except:
        return 44.92 

# --- ⚙️ 2. RESMİ VERİLER (4 NİSAN 2026) ---
st.set_page_config(page_title="2026 Ekonomi Analizi", layout="wide")
CANLI_DOLAR = get_live_usd()

# OCAK-MART 2026 GERÇEKLEŞEN ENFLASYON (Senin Başlangıç Noktan)
BAZ_ENFLASYON = 14.40 
RESMI_HEDEF = 22.0
MEVCUT_FAIZ = 37.0

st.title("🏛️ 2026 Türkiye Makroekonomik Strateji Matrisi")
st.subheader(f"📊 Mevcut Durum: İlk Çeyrek (Ocak-Mart) Birikmiş Enflasyon: %{BAZ_ENFLASYON}")

# --- 🕹️ 3. KONTROL PANELİ (SIDEBAR) ---
st.sidebar.header("🕹️ Gelecek 9 Ayı Yönet")
st.sidebar.info("Sliderları '0'da bırakırsan, yılın geri kalanında hiç ek enflasyon oluşmadığını varsayar.")

# Slider başlangıç değerlerini 0 yapıyoruz ki temiz başlasın
kur = st.sidebar.slider("Dolar Kuru Artışı (%)", -5, 50, 0)
ucret = st.sidebar.slider("Yeni Maaş Zamları (%)", 0, 60, 0)
mazot = st.sidebar.slider("Ek Mazot/Lojistik Zammı (%)", -10, 60, 0)
faiz = st.sidebar.slider("MB Faiz Hamlesi (Puan)", -15, 15, 0)
algi = st.sidebar.slider("Fiyat Algısı/Atalet (%)", 0, 40, 0)
baz_puan_etkisi = st.sidebar.slider("Baz Etkisi (Matematiksel Puan)", -10, 10, 0)

# --- 🧮 4. HESAP MOTORU ---
# Katsayılar nisan-aralık dönemini temsil eder
e_kur = kur * 0.38
e_ucret = ucret * 0.25
e_mazot = mazot * 0.12
e_faiz = faiz * -0.18
e_algi = algi * 0.22
e_baz = baz_puan_etkisi * 1.0

# Yeni eklenen enflasyon baskısı
ek_baski = e_kur + e_ucret + e_mazot + e_faiz + e_algi + e_baz
yil_sonu_tahmin = BAZ_ENFLASYON + ek_baski

# --- 📊 5. ANA GÖSTERGELER (KIYASLAMALI) ---
st.divider()
c1, c2, c3 = st.columns(3)

with c1:
    st.metric("🎯 Resmi Hedef", f"%{RESMI_HEDEF}")
    st.caption("TCMB 2026 Yıl Sonu Hedefi")

with c2:
    # Renklendirme: Hedefin üzerindeyse kırmızı, altındaysa yeşil
    delta_val = yil_sonu_tahmin - RESMI_HEDEF
    st.metric("🔮 Sizin Tahmininiz", f"%{yil_sonu_tahmin:.2f}", f"{delta_val:.2f} Puan Fark", delta_color="inverse")
    st.caption("Senaryonuza Göre Yıl Sonu")

with c3:
    st.metric("📈 Ek Enflasyon Yükü", f"+%{ek_baski:.2f}")
    st.caption("Nisan-Aralık Tahmini Baskı")

st.divider()

# --- 📝 6. DETAYLI ANALİZ ---
col_left, col_right = st.columns(2)

with col_left:
    st.write("### 🔩 Değişimlerin Faturası")
    analiz_df = pd.DataFrame({
        "Parametre": ["Kur", "Ücret", "Mazot", "Faiz", "Algı", "Baz Etkisi"],
        "Katkı (Puan)": [e_kur, e_ucret, e_mazot, e_faiz, e_algi, e_baz]
    })
    st.bar_chart(analiz_df.set_index("Parametre"))

with col_right:
    st.write("### 📋 Senaryo Özeti")
    if yil_sonu_tahmin <= RESMI_HEDEF:
        st.success(f"Tebrikler! Belirlediğiniz politikalarla enflasyonu %{RESMI_HEDEF} hedefinin altında tutabiliyorsunuz.")
    else:
        st.warning(f"Dikkat: Mevcut şartlarda enflasyon hedeften %{yil_sonu_tahmin - RESMI_HEDEF:.2f} puan sapıyor.")
    
    st.write(f"**Yeni Politika Faizi:** %{MEVCUT_FAIZ + faiz}")
    st.write(f"**Reel Faiz Durumu:** %{(MEVCUT_FAIZ + faiz) - yil_sonu_tahmin:.2f}")
