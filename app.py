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
st.set_page_config(page_title="Hanehalkı Ekonomi Paneli", layout="wide")
init_db()
CANLI_DOLAR = get_live_usd()
BAZ_ENFLASYON = 14.40 

st.title("🏠 Hanehalkı Yaşam Maliyeti Analiz Paneli")
st.caption(f"📡 Canlı Dolar: {CANLI_DOLAR} TL | 📊 Baz Enflasyon: %{BAZ_ENFLASYON}")

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

# --- 📊 6. SONUÇLAR ---
st.divider()
c1, c2, c3 = st.columns(3)
with c1: st.metric("📊 Seçilen Profil", user_profile)
with c2: st.metric("📈 Hissedilen Enflasyon", f"%{tahmin:.2f}")
with c3: st.metric("🛡️ Temel Endişe", korku_faktoru)

# --- 💾 7. VERİ GÖNDERME ---
st.divider()
st.subheader("🔍 Pilot Çalışma: Veri Toplama")
if st.button("Tahminimi Havuza Gönder"):
    save_survey(user_profile, tahmin, korku_faktoru)
    st.success("Kaydedildi! Verileriniz havuza eklendi.")

# --- 🛡️ 8. GİZLİ YÖNETİCİ GİRİŞİ ---
st.sidebar.divider()
with st.sidebar.expander("🔐 Yönetici Girişi"):
    sifre = st.text_input("Şifre Girin", type="password")
    admin_modu = (sifre == "alper2026")

# --- 📈 9. YÖNETİCİ ÖZET RAPORU ---
if admin_modu:
    st.divider()
    st.header("📂 Yönetici Analiz Paneli")
    
    conn = sqlite3.connect('beklenti_havuzu.db')
    df = pd.read_sql_query("SELECT * FROM anket", conn)
    conn.close()
    
    if not df.empty:
        # ÜST ÖZET KARTLARI
        m1, m2, m3 = st.columns(3)
        with m1:
            genel_ort = df["beklenen_enflasyon"].mean()
            st.metric("🌍 Genel Beklenti Ort.", f"%{genel_ort:.2f}")
        with m2:
            populer_grup = df["profil"].value_counts().idxmax()
            st.metric("🏆 En Çok Katılım", populer_grup)
        with m3:
            ana_korku = df["en_cok_korkulan"].value_counts().idxmax()
            st.metric("🚨 En Büyük Korku", ana_korku)

        # GRAFİKSEL ANALİZ
        st.divider()
        g1, g2 = st.columns(2)
        with g1:
            st.write("### 📈 Gruplara Göre Enflasyon Beklentisi")
            st.bar_chart(df.groupby("profil")["beklenen_enflasyon"].mean())
        with g2:
            st.write("### 👥 Katılımcı Dağılımı")
            st.bar_chart(df["profil"].value_counts())

        # VERİ TEMİZLEME VE LİSTE
        st.divider()
        with st.expander("🗑️ Veri Listesi ve Kayıt Silme"):
            st.dataframe(df, use_container_width=True)
            silinecek_tarih = st.selectbox("Silmek istediğiniz kaydın tarihini seçin:", df["tarih"].tolist())
            if st.button("Kaydı Kalıcı Olarak Sil"):
                delete_record(silinecek_tarih)
                st.warning("Kayıt silindi, yenileniyor...")
                st.rerun()
    else:
        st.info("Henüz analiz edilecek veri toplanmadı.")
else:
    st.caption("Pilot çalışma verileri yönetici tarafından analiz edilmektedir.")
