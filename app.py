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

def delete_record(tarih_id):
    conn = sqlite3.connect('beklenti_havuzu.db')
    c = conn.cursor()
    c.execute("DELETE FROM anket WHERE tarih = ?", (tarih_id,))
    conn.commit()
    conn.close()

# --- 📡 2. CANLI VERİ ---
def get_live_usd():
    try:
        url = "https://www.google.com/finance/quote/USD-TRY"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        match = re.search(r'class="YMlKec fxKbKc">([\d,.]+)<', res.text)
        return float(match.group(1).replace(",", ""))
    except: return 44.92 

# --- ⚙️ 3. AYARLAR ---
st.set_page_config(page_title="Ekonomi Analiz Paneli", layout="wide")
init_db()
CANLI_DOLAR = get_live_usd()
BAZ_ENFLASYON = 14.40 
TCMB_2026_HEDEF = 22.0 # Merkez Bankası 2026 Yıl Sonu Tahmini

st.title("🏠 Hanehalkı Yaşam Maliyeti Analiz Paneli")
st.caption(f"📡 Canlı Dolar: {CANLI_DOLAR} TL | 📊 İlk Çeyrek Gerçekleşen Enflasyon: %{BAZ_ENFLASYON}")

# --- 🕹️ 4. KULLANICI GİRDİLERİ ---
st.sidebar.header("👤 Durumunuz")
user_profile = st.sidebar.selectbox("Hangi gruptasınız?", ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"])

st.sidebar.divider()
st.sidebar.header("📉 Beklenen Artışlar")
gida_artisi = st.sidebar.slider("Market/Gıda (%)", 0, 100, 0)
kira_artisi = st.sidebar.slider("Kira/Konut (%)", 0, 100, 0)
ulasim_artisi = st.sidebar.slider("Ulaşım/Benzin (%)", 0, 100, 0)
diger_artisi = st.sidebar.slider("Diğer Giderler (%)", 0, 100, 0)

korku_faktoru = st.sidebar.selectbox("Sizi en çok zorlayan kalem:", ["Gıda", "Kira", "Akaryakıt", "Maaş Yetmezliği"])

# --- 🧮 5. HESAPLAMA ---
weights = {
    "Öğrenci": {"gida": 0.30, "kira": 0.40, "ulasim": 0.20, "diger": 0.10},
    "Emekli": {"gida": 0.50, "kira": 0.20, "ulasim": 0.10, "diger": 0.20},
    "Çalışan": {"gida": 0.25, "kira": 0.35, "ulasim": 0.20, "diger": 0.20},
    "Kamu Personeli": {"gida": 0.30, "kira": 0.30, "ulasim": 0.20, "diger": 0.20},
    "Esnaf": {"gida": 0.20, "kira": 0.30, "ulasim": 0.30, "diger": 0.20}
}

w = weights[user_profile]
hissedilen_ek = (gida_artisi * w["gida"]) + (kira_artisi * w["kira"]) + (ulasim_artisi * w["ulasim"]) + (diger_artisi * w["diger"])
tahmin = BAZ_ENFLASYON + hissedilen_ek

# --- 📊 6. SONUÇLAR (TCMB EKLEMELİ) ---
st.divider()
c1, c2, c3, c4 = st.columns(4) # Kolon sayısını 4'e çıkardık

with c1: 
    st.metric("📊 Seçilen Profil", user_profile)
with c2: 
    st.metric("🎯 TCMB 2026 Hedefi", f"%{TCMB_2026_HEDEF}")
    st.caption("Resmi Enflasyon Tahmini")
with c3: 
    # Sapma miktarını TCMB hedefine göre hesaplıyoruz
    delta_val = tahmin - TCMB_2026_HEDEF
    st.metric("📈 Hissedilen Enflasyon", f"%{tahmin:.2f}", f"{delta_val:.2f} Sapma", delta_color="inverse")
    st.caption("Sizin Tahmininiz")
with c4: 
    st.metric("🛡️ Temel Endişe", korku_faktoru)

# --- 💾 7. VERİ GÖNDERME ---
st.divider()
st.subheader("🔍 Pilot Çalışma: Veri Toplama")
if st.button("Tahminimi Havuza Gönder"):
    save_survey(user_profile, tahmin, korku_faktoru)
    st.success("Kaydedildi! Verileriniz güvenle sisteme eklendi.")

# --- 🛡️ 8. GİZLİ YÖNETİCİ GİRİŞİ ---
st.sidebar.divider()
with st.sidebar.expander("🔐 Yönetici Girişi"):
    sifre = st.text_input("Şifre Girin", type="password")
    admin_modu = (sifre == "alper2026")

# --- 📉 9. SADECE YÖNETİCİYE ÖZEL ANALİZ ---
if admin_modu:
    st.divider()
    st.header("📂 Yönetici Özel Analiz Raporu")
    
    conn = sqlite3.connect('beklenti_havuzu.db')
    df = pd.read_sql_query("SELECT * FROM anket", conn)
    conn.close()
    
    if not df.empty:
        # ÜST ÖZET KARTLARI
        m1, m2, m3 = st.columns(3)
        with m1:
            genel_ort = df["beklenen_enflasyon"].mean()
            # Genel beklentinin TCMB hedefinden farkını da yönetici görsün
            st.metric("🌍 Toplum Beklentisi (Ort.)", f"%{genel_ort:.2f}", f"{genel_ort - TCMB_2026_HEDEF:.2f} Hedef Sapması")
        with m2:
            populer_grup = df["profil"].value_counts().idxmax()
            st.metric("🏆 En Aktif Katılımcı", populer_grup)
        with m3:
            ana_korku = df["en_cok_korkulan"].value_counts().idxmax()
            st.metric("🚨 Genel Risk Odağı", ana_korku)

        # GRAFİKLER
        st.divider()
        g1, g2 = st.columns(2)
        with g1:
            st.write("### 📈 Grupların Tahmin Ortalamaları")
            st.bar_chart(df.groupby("profil")["beklenen_enflasyon"].mean())
        with g2:
            st.write("### 👥 Katılım Yoğunluğu (Kişi)")
            st.bar_chart(df["profil"].value_counts())
            
        # VERİ LİSTESİ VE TEMİZLEME
        st.divider()
        with st.expander("🗑️ Ham Veri Listesi ve Kayıt Silme"):
            st.dataframe(df, use_container_width=True)
            silinecek_tarih = st.selectbox("Silmek istediğiniz kaydın tarihini seçin:", df["tarih"].tolist())
            if st.button("Kaydı Kalıcı Olarak Sil"):
                delete_record(silinecek_tarih)
                st.warning("Kayıt silindi, sayfa yenileniyor...")
                st.rerun()
    else:
        st.info("Henüz analiz edilecek veri toplanmadı.")
else:
    st.info("💡 **Bilgi:** Pilot çalışma verileri anonim olarak toplanmaktadır. Analiz sonuçları sadece yönetici yetkisiyle görüntülenebilir.")
