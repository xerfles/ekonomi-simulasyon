import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 📁 VERİ SAKLAMA ---
DB_FILE = 'beklenti_havuzu.csv'

def save_to_csv(profil, enflasyon_9ay, toplam_tahmin, korku):
    # Hem 9 aylık beklentiyi hem de toplamı saklıyoruz ki analizde işine yarasın
    new_data = pd.DataFrame([[
        datetime.now().strftime("%Y-%m-%d %H:%M"), 
        profil, 
        enflasyon_9ay, 
        toplam_tahmin, 
        korku
    ]], columns=['tarih', 'profil', 'beklenti_9ay', 'toplam_yıl_sonu', 'en_cok_korkulan'])
    
    if not os.path.isfile(DB_FILE):
        new_data.to_csv(DB_FILE, index=False)
    else:
        new_data.to_csv(DB_FILE, mode='a', index=False, header=False)

# --- 📊 EKONOMİK VERİLER ---
ILK_CEYREK_GERCEKLESEN = 14.40  # Ocak-Şubat-Mart Toplamı
TCMB_2026_HEDEF = 22.0

# --- ⚙️ AYARLAR ---
st.set_page_config(page_title="2026 Ekonomi Analizi", layout="wide")

st.title("🏠 2026 Yılı Enflasyon Beklenti Paneli")
st.markdown(f"📊 **Resmi Veri (İlk Çeyrek):** %{ILK_CEYREK_GERCEKLESEN} | 🎯 **TCMB Yıl Sonu Hedefi:** %{TCMB_2026_HEDEF}")

# --- 🕹️ KENAR ÇUBUĞU: 9 AYLIK TAHMİN ---
st.sidebar.header("🎯 Gelecek 9 Ay Senaryosu")
st.sidebar.write("Nisan'dan Aralık sonuna kadar fiyatlar sizce ne kadar artar?")

user_profile = st.sidebar.selectbox("Profiliniz:", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"])
st.sidebar.divider()

gida = st.sidebar.slider("🛒 Market/Gıda (%)", 0, 100, 0)
kira = st.sidebar.slider("🏠 Kira/Konut (%)", 0, 100, 0)
ulasim = st.sidebar.slider("🚗 Ulaşım (%)", 0, 100, 0)
diger = st.sidebar.slider("🎭 Diğer (%)", 0, 100, 0)

korku = st.sidebar.selectbox("Temel Endişe:", ["Gıda Fiyatları", "Kira Artışı", "Akaryakıt Zamları", "Maaş Yetmezliği"])

# --- 🧮 HESAPLAMA MANTIĞI ---
weights = {
    "Öğrenci": [0.3, 0.4, 0.2, 0.1], 
    "Emekli": [0.5, 0.2, 0.1, 0.2], 
    "Çalışan": [0.3, 0.3, 0.2, 0.2], 
    "Kamu Personeli": [0.3, 0.3, 0.2, 0.2], 
    "Esnaf": [0.2, 0.3, 0.3, 0.2]
}
w = weights[user_profile]

# Sadece Nisan-Aralık Beklentisi
nisan_aralik_beklentisi = (gida * w[0] + kira * w[1] + ulasim * w[2] + diger * w[3])

# Yıl Sonu Toplam (İlk Çeyrek + Kullanıcı Tahmini)
toplam_yıl_sonu = ILK_CEYREK_GERCEKLESEN + nisan_aralik_beklentisi

# --- 🏁 ANA EKRAN: NET SONUÇLAR ---
st.divider()
st.subheader("🏁 Beklenti Özeti")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("📊 İlk Çeyrek (Gerçekleşen)", f"%{ILK_CEYREK_GERCEKLESEN}")
    st.caption("Ocak-Şubat-Mart toplamı")

with c2:
    st.metric("🔮 Sizin 9 Aylık Beklentiniz", f"%{nisan_aralik_beklentisi:.2f}")
    st.caption("Nisan - Aralık arası beklediğiniz artış")

with c3:
    st.metric("📈 Yıl Sonu Toplam Tahmin", f"%{toplam_yıl_sonu:.2f}")
    st.caption("İlk Çeyrek + Sizin Beklentiniz")

# --- 🎯 HEDEF KIYASLAMA VE KAYIT ---
st.divider()
k1, k2 = st.columns([2, 1])

with k1:
    sapma = toplam_yıl_sonu - TCMB_2026_HEDEF
    st.write(f"#### ⚖️ TCMB Hedefine Göre Durum")
    if sapma > 0:
        st.error(f"Tahmininiz Merkez Bankası hedefinden **{sapma:.2f} puan** daha yüksek.")
    else:
        st.success(f"Tahmininiz Merkez Bankası hedefinden **{abs(sapma):.2f} puan** daha düşük (İyimser).")

with k2:
    if st.button("🚀 Tahminimi Havuza Kaydet"):
        save_to_csv(user_profile, nisan_aralik_beklentisi, toplam_yıl_sonu, korku)
        st.success("Veriler başarıyla kaydedildi!")

# --- 🛡️ YÖNETİCİ PANELİ ---
st.sidebar.divider()
with st.sidebar.expander("🔐 Yönetici Girişi"):
    sifre = st.text_input("Şifre", type="password")
    if sifre == "alper2026":
        st.header("📂 Yönetici Analiz Raporu")
        if os.path.exists(DB_FILE):
            df = pd.read_csv(DB_FILE)
            
            # Özet Veriler
            m1, m2, m3 = st.columns(3)
            m1.metric("Toplam Katılım", len(df))
            m2.metric("Ort. 9 Aylık Beklenti", f"%{df['beklenti_9ay'].mean():.2f}")
            m3.metric("Ort. Yıl Sonu Tahmini", f"%{df['toplam_yıl_sonu'].mean():.2f}")
            
            st.divider()
            st.write("#### Gruplara Göre Yıl Sonu Tahminleri")
            st.bar_chart(df.groupby("profil")["toplam_yıl_sonu"].mean())
            
            st.write("#### Ham Veri")
            st.dataframe(df)
        else:
            st.info("Henüz veri yok.")
