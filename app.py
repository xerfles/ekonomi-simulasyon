import streamlit as st
import pandas as pd

# --- 1. SABİT VERİLER (GÜNCEL DURUM) ---
BAZ_DOLAR = 33.15  # Mevcut Kur
BAZ_ENF = 31.53    # Mevcut Enflasyon
BAZ_FAIZ = 37.0    # Mevcut Politika Faizi
YIL_SONU_HEDEF = 36.0 # Piyasa/MB Yıl Sonu Hedefi

# Sayfa Tasarımı
st.set_page_config(page_title="Ekonomi Projeksiyonu", page_icon="📈", layout="wide")

st.title("🇹🇷 Ekonomi Projeksiyon Simülatörü")
st.markdown(f"""
Bu simülatör, mevcut ekonomik veriler üzerinden yıl sonu tahminleri yapmanızı sağlar.
**Mevcut Durum:** Dolar: {BAZ_DOLAR} TL | Enflasyon: %{BAZ_ENF} | Faiz: %{BAZ_FAIZ}
""")
st.divider()

# --- 2. YAN PANEL (KONTROLLER) ---
st.sidebar.header("🕹️ Senaryo Ayarları")

dolar_degisim = st.sidebar.slider("Dolar Değişimi (%)", -10, 100, 10, help="Kurun mevcut seviyeden ne kadar sapacağını seçin.")
ucret_zammi = st.sidebar.slider("Yıllık Ücret Zammı (%)", 0, 100, 25)
faiz_hamlesi = st.sidebar.slider("Ek Faiz Artışı/İndirimi (Puan)", -15, 25, 0)
butce_etkisi = st.sidebar.slider("Ek Bütçe Açığı / GSYH (%)", 0.0, 10.0, 3.0, 0.5)

# --- 3. HESAPLAMA MOTORU (EKONOMETRİK MODEL) ---
# Türkiye ekonomisi katsayıları:
# Kur Geçişkenliği: 0.40 | Ücret: 0.20 | Faiz: -0.15 | Bütçe: 0.50
kur_puan = dolar_degisim * 0.40
ucret_puan = ucret_zammi * 0.20
faiz_puan = faiz_hamlesi * -0.15
butce_puan = butce_etkisi * 0.50

yil_sonu_tahmin = BAZ_ENF + kur_puan + ucret_puan + faiz_puan + butce_puan
hedef_kur = BAZ_DOLAR * (1 + dolar_degisim/100)
yeni_faiz = BAZ_FAIZ + faiz_hamlesi

# --- 4. SONUÇ GÖSTERİMİ (DASHBOARD) ---
c1, c2, c3 = st.columns(3)

with c1:
    sapma = yil_sonu_tahmin - YIL_SONU_HEDEF
    st.metric("Yıl Sonu Enflasyon Tahmini", f"%{yil_sonu_tahmin:.2f}", f"{sapma:.2f} Hedef Sapması", delta_color="inverse")

with c2:
    st.metric("Senaryo Dolar Kuru", f"{hedef_kur:.2f} TL", f"%{dolar_degisim}")

with c3:
    st.metric("Yeni Politika Faizi", f"%{yeni_faiz:.1f}", f"{faiz_hamlesi} Puan")

st.divider()

# --- 5. ANALİZ VE GRAFİKLER ---
col_grafik, col_analiz = st.columns([2, 1])

with col_grafik:
    st.subheader("📊 Enflasyon Bileşenleri Analizi")
    etki_df = pd.DataFrame({
        'Etken': ['Kur Etkisi', 'Ücret Etkisi', 'Bütçe Etkisi', 'Faiz Freni'],
        'Puan': [kur_puan, ucret_puan, butce_puan, faiz_puan]
    })
    st.bar_chart(etki_df.set_index('Etken'), color="#ff4b4b")

with col_analiz:
    st.subheader("📝 Uzman Notu")
    if yil_sonu_tahmin > 45:
        st.error(f"Enflasyon hedefi (%{YIL_SONU_HEDEF}) ciddi şekilde aşılıyor. Pozitif reel faiz için faiz oranının en az %{yil_sonu_tahmin + 5:.1f} olması önerilir.")
    elif abs(sapma) <= 3:
        st.success("Senaryonuz yıl sonu hedefleriyle uyumlu bir dezenflasyon sürecini destekliyor.")
    else:
        st.warning("Hedeflerden sapma var. Mali disiplin veya ek sıkılaşma gerekebilir.")

st.caption("Bu uygulama Alper Furkan Atsatan tarafından makroekonomik duyarlılık analizleri baz alınarak geliştirilmiştir.")
