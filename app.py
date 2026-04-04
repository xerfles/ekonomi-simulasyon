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
st.set_page_config(page_title="2026 Yaşam Maliyeti Analizi", layout="wide")
init_db()
CANLI_DOLAR = get_live_usd()
BAZ_ENFLASYON = 14.40 
TCMB_2026_HEDEF = 22.0 

st.title("🏠 2026 Yılı Yaşam Maliyeti Tahmin Paneli")
st.markdown("""
**Hoş geldiniz!** Bu panelde, 2026 yılının geri kalanında (Nisan-Aralık) fiyatların nasıl değişeceğini tahmin ederek kendi 'kişisel enflasyonunuzu' hesaplayabilirsiniz.
""")

st.info(f"💡 **Güncel Durum:** Yılın ilk 3 ayında fiyatlar zaten **%{BAZ_ENFLASYON}** arttı. Şimdi sıra sizin gelecek 9 ay tahmininizde!")

# --- 🕹️ 4. KULLANICI GİRDİLERİ (AÇIKLAYICI DİL) ---
st.sidebar.header("🎯 Senaryonuzu Oluşturun")
st.sidebar.write("Nisan'dan Aralık ayına kadar fiyatlar sizce ne kadar artar?")

user_profile = st.sidebar.selectbox(
    "Öncelikle durumunuzu seçin:", 
    ["Öğrenci", "Emekli", "Çalışan", "Kamu Personeli", "Esnaf"],
    help="Harcama alışkanlıklarınız bu seçime göre ağırlıklandırılır."
)

st.sidebar.divider()

gida_artisi = st.sidebar.slider(
    "🛒 Market ve Pazar Fiyatları (%)", 0, 100, 0,
    help="Temel gıda ürünlerine (et, süt, sebze vb.) beklediğiniz toplam zam oranı."
)
kira_artisi = st.sidebar.slider(
    "🏠 Kira ve Konut Masrafları (%)", 0, 100, 0,
    help="Kiranıza veya aidat/bakım gibi ev giderlerinize beklediğiniz artış."
)
ulasim_artisi = st.sidebar.slider(
    "🚗 Ulaşım ve Akaryakıt (%)", 0, 100, 0,
    help="Benzin, otobüs bileti veya servis ücretlerindeki beklediğiniz değişim."
)
diger_artisi = st.sidebar.slider(
    "🎭 Giyim, Eğlence ve Diğer (%)", 0, 100, 0,
    help="Kıyafet, dışarıda yemek, sinema veya eğitim gibi diğer tüm harcamalar."
)

korku_faktoru = st.sidebar.selectbox(
    "Sizi en çok hangi zam kaleminden korkuyorsunuz?", 
    ["Gıda Fiyatları", "Kira Artışı", "Akaryakıt/Ulaşım", "Maaşın Alım Gücü"],
    help="En büyük risk odağınızı belirtin."
)

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
st.subheader("🏁 Tahmin Sonuçlarınız")

c1, c2, c3 = st.columns([1, 1, 1.5])

with c1:
    st.metric("📊 Profiliniz", user_profile)
    st.write(f"Sizin için **Gıda** %{w['gida']*100:.0f}, **Kira** %{w['kira']*100:.0f} ağırlığa sahip.")

with c2:
    st.metric("🎯 Resmi Hedef (TCMB)", f"%{TCMB_2026_HEDEF}")
    st.caption("Merkez Bankası'nın 2026 sonu beklentisi.")

with c3:
    delta_val = tahmin - TCMB_2026_HEDEF
    st.metric("📈 Sizin Tahmininiz", f"%{tahmin:.2f}", f"{delta_val:.2f} Puan Sapma", delta_color="inverse")
    st.write(f"Senaryonuza göre 2026 yılını bu enflasyonla kapatacaksınız.")

# --- 💾 7. VERİ GÖNDERME ---
st.divider()
st.subheader("🔍 Pilot Çalışma: Beklenti Havuzu")
st.write("Tahmininizi sisteme kaydederek, toplumun genel beklenti ortalamasını oluşturmamıza yardımcı olun.")

if st.button("Tahminimi Kaydet ve Havuza Gönder"):
    save_survey(user_profile, tahmin, korku_faktoru)
    st.success("✅ Kaydedildi! Katkınız için teşekkürler.")

# --- 🛡️ 8. GİZLİ YÖNETİCİ GİRİŞİ ---
st.sidebar.divider()
with st.sidebar.expander("🔐 Yönetici Girişi"):
    sifre = st.text_input("Şifre Girin", type="password")
    admin_modu = (sifre == "alper2026")

# --- 📉 9. YÖNETİCİ ANALİZİ ---
if admin_modu:
    st.divider()
    st.header("📂 Yönetici Özel Analiz Raporu")
    conn = sqlite3.connect('beklenti_havuzu.db')
    df = pd.read_sql_query("SELECT * FROM anket", conn)
    conn.close()
    
    if not df.empty:
        m1, m2, m3 = st.columns(3)
        m1.metric("🌍 Toplum Ortalaması", f"%{df['beklenen_enflasyon'].mean():.2f}")
        m2.metric("🏆 En Çok Katılım", df['profil'].value_counts().idxmax())
        m3.metric("🚨 Genel Korku", df['en_cok_korkulan'].value_counts().idxmax())

        st.divider()
        g1, g2 = st.columns(2)
        with g1:
            st.write("### 📈 Grupların Tahmin Ortalamaları")
            st.bar_chart(df.groupby("profil")["beklenen_enflasyon"].mean())
        with g2:
            st.write("### 👥 Katılımcı Sayıları")
            st.bar_chart(df["profil"].value_counts())
            
        with st.expander("🗑️ Veri Yönetimi"):
            st.dataframe(df)
            sil = st.selectbox("Silinecek Kayıt:", df["tarih"].tolist())
            if st.button("Seçili Kaydı Sil"):
                delete_record(sil)
                st.rerun()
    else:
        st.info("Henüz veri yok.")
