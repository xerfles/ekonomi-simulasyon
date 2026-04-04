import streamlit as st
import pandas as pd
import requests
import re
import sqlite3
from datetime import datetime

# --- 🗄️ 1. VERİ TABANI ---
def init_db():
    conn = sqlite3.connect('hanehalkı_beklenti.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS anket 
                 (tarih TEXT, profil TEXT, beklenen_enflasyon REAL, en_cok_korkulan TEXT)''')
    conn.commit()
    conn.close()

def save_survey(profil, enflasyon, korku):
    conn = sqlite3.connect('hanehalkı_beklenti.db')
    c = conn.cursor()
    c.execute("INSERT INTO anket VALUES (?, ?, ?, ?)", (datetime.now().strftime("%Y-%m-%d %H:%M"), profil, enflasyon, korku))
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
st.set_page_config(page_title="Hanehalkı Ekonomi Simülatörü", layout="wide")
init_db()
CANLI_DOLAR = get_live_usd()
BAZ_ENFLASYON = 14.40 

st.title("🏠 Hanehalkı Yaşam Maliyeti ve Enflasyon Simülatörü")
st.markdown("Bu çalışma, farklı toplum kesimlerinin nisan-aralık dönemine dair ekonomik beklentilerini ölçmek için tasarlanmıştır.")

# --- 🕹️ 4. KULLANICI PROFİLİ VE GİRDİLER ---
st.sidebar.header("👤 Profilinizi Belirleyin")
user_profile = st.sidebar.selectbox("Hangi gruptasınız?", ["Öğrenci", "Emekli", "Beyaz Yakalı (Özel Sektör)", "Memur", "Esnaf/İşletme Sahibi"])

st.sidebar.divider()
st.sidebar.header("📉 Yaşam Maliyeti Tahmininiz")
gida_artisi = st.sidebar.slider("Market/Pazar Alışverişi Artışı (%)", 0, 100, 0)
kira_artisi = st.sidebar.slider("Kira/Konut Gideri Artışı (%)", 0, 100, 0)
ulasim_artisi = st.sidebar.slider("Ulaşım/Yakıt Artışı (%)", 0, 100, 0)
diger_artisi = st.sidebar.slider("Giyim/Eğlence/Diğer Artışı (%)", 0, 100, 0)

korku_faktoru = st.sidebar.selectbox("Sizi en çok hangi zam korkutuyor?", ["Gıda", "Kira", "Akaryakıt", "Eğitim/Sağlık"])

# --- 🧮 5. PROFİLE ÖZEL HESAPLAMA (AĞIRLIKLANDIRMA) ---
# Gruplara göre harcama sepeti ağırlıkları (TÜİK ve Saha Araştırması Bazlı)
weights = {
    "Öğrenci": {"gida": 0.30, "kira": 0.40, "ulasim": 0.20, "diger": 0.10},
    "Emekli": {"gida": 0.50, "kira": 0.20, "ulasim": 0.10, "diger": 0.20},
    "Beyaz Yakalı (Özel Sektör)": {"gida": 0.25, "kira": 0.35, "ulasim": 0.20, "diger": 0.20},
    "Memur": {"gida": 0.30, "kira": 0.30, "ulasim": 0.20, "diger": 0.20},
    "Esnaf/İşletme Sahibi": {"gida": 0.20, "kira": 0.30, "ulasim": 0.30, "diger": 0.20}
}

w = weights[user_profile]
hissedilen_ek_enflasyon = (gida_artisi * w["gida"]) + (kira_artisi * w["kira"]) + (ulasim_artisi * w["ulasim"]) + (diger_artisi * w["diger"])
yıl_sonu_tahmini = BAZ_ENFLASYON + hissedilen_ek_enflasyon

# --- 📊 6. SONUÇLAR ---
st.divider()
c1, c2, c3 = st.columns(3)

with c1:
    st.metric("📊 Sizin Grubunuz", user_profile)
    st.caption(f"Sepet Ağırlığı: Gıda %{w['gida']*100:.0f}, Kira %{w['kira']*100:.0f}")

with c2:
    st.metric("📈 Hissedilen Yıl Sonu Enflasyonu", f"%{yıl_sonu_tahmini:.2f}")
    st.caption("Nisan-Aralık Beklentiniz Dahil")

with c3:
    st.metric("🛡️ En Büyük Risk", korku_faktoru)
    st.caption("Kişisel Endişe Odağı")

# --- 💾 7. ANKET VE VERİ TOPLAMA ---
st.divider()
st.subheader("📝 2209-A Araştırmasına Katılın")
st.write("Tahminlerinizi kaydederek toplumsal beklenti endeksinin oluşmasına yardımcı olun.")

if st.button("Beklentilerimi Kaydet ve Endekse Katıl"):
    save_survey(user_profile, yıl_sonu_tahmini, korku_faktoru)
    st.success("Teşekkürler! Beklentileriniz veri tabanına işlendi.")

# --- 📈 8. TOPLUMSAL ANALİZ (GERÇEK ZAMANLI VERİ) ---
st.divider()
st.subheader("📊 Toplumsal Beklenti Havuzu (Canlı Sonuçlar)")

conn = sqlite3.connect('hanehalkı_beklenti.db')
df_res = pd.read_sql_query("SELECT * FROM anket", conn)
conn.close()

if not df_res.empty:
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("**Gruba Göre Ortalama Enflasyon Beklentisi**")
        avg_enf = df_res.groupby("profil")["beklenen_enflasyon"].mean()
        st.bar_chart(avg_enf)
    
    with col_b:
        st.write("**En Çok Korkulan Zam Kalemleri**")
        korku_counts = df_res["en_cok_korkulan"].value_counts()
        st.bar_chart(korku_counts)
else:
    st.info("Henüz veri toplanmadı. İlk tahmini siz yapın!")
