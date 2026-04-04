import streamlit as st
import pandas as pd
import requests
import re

# --- 📡 1. CANLI VERİ ---
def get_live_usd():
    try:
        url = "https://www.google.com/finance/quote/USD-TRY"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        match = re.search(r'class="YMlKec fxKbKc">([\d,.]+)<', res.text)
        return float(match.group(1).replace(",", ""))
    except:
        return 44.92 

# --- ⚙️ 2. AYARLAR & MEVCUT DURUM ---
st.set_page_config(page_title="2026 Ekonomi Strateji Matrisi", layout="wide")
CANLI_DOLAR = get_live_usd()
BAZ_ENFLASYON = 14.40   # Ocak-Mart Gerçekleşen Veri
RESMI_HEDEF = 22.0      # Yıl Sonu Hedefi
MEVCUT_FAIZ = 37.0      # Güncel Politika Faizi

st.title("🏛️ 2026 Türkiye Makroekonomik Strateji Matrisi")
st.markdown(f"""
📡 **Veri Tarihi:** 4 Nisan 2026 | **Anlık Dolar:** {CANLI_DOLAR} TL | 
**Mevcut Politika Faizi:** %{MEVCUT_FAIZ} | **İlk Çeyrek Enflasyonu:** %{BAZ_ENFLASYON}
""")

# --- 🕹️ 3. KONTROL PANELİ (NİSAN-ARALIK İÇİN SIFIRLANDI) ---
st.sidebar.header("🕹️ Nisan-Aralık Dönemi Kararları")
st.sidebar.write("Gelecek 9 ayı yönetmek için sliderları kullanın.")

with st.sidebar.expander("🌐 Makro & Dışsal Faktörler", expanded=True):
    kur = st.slider("Kur Artışı (%)", -5, 50, 0)
    fed = st.slider("Fed Faizi (Puan)", -2, 5, 0)
    dis_sok = st.slider("Dışsal Şoklar (%)", 0, 30, 0)
    guven = st.select_slider("Kurumsal Güven (0-10)", options=range(11), value=5)

with st.sidebar.expander("💰 Maliye & Bütçe Politikası"):
    vergi = st.slider("Vergi Artış/Yükü (%)", 0, 40, 0)
    butce = st.slider("Bütçe Açığı (%)", 0, 20, 0)
    faiz_hamlesi = st.slider("MB Faiz Hamlesi (Puan)", -15, 15, 0)

with st.sidebar.expander("🌾 Tarım & Gıda Krizi"):
    gubre = st.slider("Gübre/Tohum Maliyeti (%)", 0, 60, 0)
    araci = st.slider("Aracı Kârı/Spekülasyon (%)", 0, 50, 0)
    gida = st.slider("Gıda Enflasyonu Baskısı (%)", 0, 60, 0)
    tarim_sorun = st.slider("Tarım Sorunu (Yapısal %)", 0, 30, 0)

with st.sidebar.expander("🏠 Sosyal & Diğer"):
    ucret = st.slider("Ücret Zammı (%)", 0, 60, 0)
    kira = st.slider("Kira Baskısı (%)", 0, 80, 0)
    mazot = st.slider("Mazot Fiyatı (%)", -10, 60, 0)
    algi = st.slider("Fiyat Algısı (%)", 0, 40, 0)
    baz_puan = st.slider("Baz Etkisi (Puan)", -10, 10, 0)

# --- 🧮 4. HESAP MOTORU (KATSAYILAR KORUNDU) ---
e_kur = kur * 0.35 + fed * 0.15
e_ucret = ucret * 0.22
e_mazot = mazot * 0.12
e_kira = kira * 0.18
e_gida = (gida * 0.15) + (gubre * 0.08) + (araci * 0.10) + (tarim_sorun * 0.12)
e_maliye = (vergi * 0.14) + (butce * 0.10)
e_psiko = (algi * 0.20) + (dis_sok * 0.10) + ((5 - guven) * 0.80)
e_faiz = faiz_hamlesi * -0.18
e_baz = baz_puan * 1.0

# Yeni eklenen enflasyon baskısı ve toplam
ek_baski = e_kur + e_ucret + e_mazot + e_kira + e_gida + e_maliye + e_psiko + e_faiz + e_baz
toplam_enflasyon = BAZ_ENFLASYON + ek_baski

# --- 📊 5. ANA GÖSTERGELER ---
st.divider()
c1, c2, c3 = st.columns(3)

with c1:
    st.metric("🎯 Hedeflenen Enflasyon", f"%{RESMI_HEDEF}")
    st.caption("Yıl Sonu Resmi Hedef")

with c2:
    delta_val = toplam_enflasyon - RESMI_HEDEF
    st.metric("📈 Şu An Olan Enflasyon", f"%{toplam_enflasyon:.2f}", f"{delta_val:.2f} Sapma", delta_color="inverse")
    st.caption("İlk Çeyrek (%14.4) + Sizin Kararlarınız")

with c3:
    yeni_faiz = MEVCUT_FAIZ + faiz_hamlesi
    st.metric("🏦 Yeni Politika Faizi", f"%{yeni_faiz}")
    st.caption(f"Baz: %{MEVCUT_FAIZ}")

st.divider()

# --- 📊 6. NİSAN-ARALIK ANALİZİ ---
st.subheader("📊 Nisan-Aralık Dönemi Ek Enflasyon Yükü")
if ek_baski > 0:
    st.warning(f"Seçtiğiniz parametreler yılın geri kalanında +%{ek_baski:.2f} ek enflasyon yaratıyor.")
else:
    st.success(f"Seçtiğiniz parametreler yılın geri kalanında enflasyonu %{abs(ek_baski):.2f} puan aşağı çekiyor.")

analiz_df = pd.DataFrame({
    "Kategori": ["Kur/Fed", "Ücretler", "Kiralar", "Gıda/Tarım", "Maliye/Vergi", "Psikoloji/Güven", "Faiz Hamlesi", "Baz Etkisi"],
    "Ek Puan Katkısı": [e_kur, e_ucret, e_kira, e_gida, e_maliye, e_psiko, e_faiz, e_baz]
})
st.bar_chart(analiz_df.set_index("Kategori"))

st.info("💡 **İpucu:** Tüm sliderlar '0'dayken sadece Ocak-Mart verisini görürsünüz. Hareket ettirdikçe 9 aylık faturayı çıkarırsınız.")
