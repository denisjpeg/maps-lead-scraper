import streamlit as st
import csv
import urllib.request
import urllib.parse
import json
import time
import io
import re

# SerpAPI Anahtarın
SERPAPI_KEY = "ba0d96b737f0098fea37e0bbcc0a9b7b188583addc38e00897864db0c145b035"

# 👑 SİSTEME ERİŞEBİLECEK PREMIUM KULLANICI LİSTESİ
PREMIUM_USERS = {
    "deniz@altunaysoft.com": "deniz2026",
    "test@premium.com": "123456"
}

def extract_email_from_website(url):
    if not url or url == "Yok" or "google.com" in url:
        return "Yok"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        with urllib.request.urlopen(req, timeout=1.5) as response:
            html = response.read().decode('utf-8', errors='ignore')
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}', html)
        valid_emails = [e for e in emails if not e.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'))]
        if valid_emails:
            return list(set(valid_emails))[0]
    except:
        pass
    return "Yok"

# --- PREMIUM TEMA VE ULTRA MODERN CSS ---
st.set_page_config(page_title="LeadScout | Altunay Soft Suite", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
        /* Global Stil ve Dark Mode Estetiği */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        
        .main { background-color: #0b0f19; font-family: 'Plus Jakarta Sans', sans-serif; }
        h1, h2, h3, h4, h5, h6 { font-family: 'Plus Jakarta Sans', sans-serif !important; }
        
        /* Cam (Glassmorphism) Efektli Üst Banner */
        .hero-banner {
            background: linear-gradient(135deg, rgba(30, 27, 75, 0.4) 0%, rgba(15, 23, 42, 0.6) 100%);
            border: 1px solid rgba(56, 189, 248, 0.1);
            padding: 2.5rem;
            border-radius: 24px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5);
        }
        .hero-banner h1 {
            background: linear-gradient(90deg, #38bdf8 0%, #6366f1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800; font-size: 3.2rem; margin-bottom: 0.5rem; letter-spacing: -1px;
        }
        .hero-banner p { color: #94a3b8; font-size: 1.1rem; font-weight: 500; }
        
        /* Lüks Kontrol ve Giriş Kartları */
        .content-card {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.3);
            margin-bottom: 1.5rem;
        }
        
        /* Başlıklar */
        .section-title { color: #f8fafc; font-weight: 700; font-size: 1.3rem; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 8px; }
        
        /* Premium Alt Yönlendirme Kartı */
        .premium-promo {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.5) 100%);
            border: 1px solid rgba(56, 189, 248, 0.2);
            padding: 1.8rem; border-radius: 16px; text-align: left;
        }
        
        /* Link Butonu Tasarımı */
        .promo-btn {
            display: block; text-align: center; background: linear-gradient(90deg, #0284c7 0%, #0369a1 100%);
            color: white !important; padding: 0.6rem; border-radius: 10px; text-decoration: none !important;
            font-weight: 700; font-size: 0.9rem; margin-top: 1rem; box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
            transition: all 0.2s ease;
        }
        .promo-btn:hover { transform: translateY(-1px); box-shadow: 0 6px 18px rgba(2, 132, 199, 0.4); }
        
        /* Streamlit Butonunu Tamamen Ezme (Kurumsal Mavi Efekt) */
        div.stButton > button:first-child {
            background: linear-gradient(90deg, #38bdf8 0%, #6366f1 100%) !important;
            color: white !important; border: none !important; padding: 0.8rem 2rem !important;
            border-radius: 12px !important; font-weight: 700 !important; font-size: 1.05rem !important;
            width: 100% !important; transition: all 0.3s ease !important;
            box-shadow: 0 8px 20px -6px rgba(56, 189, 248, 0.5) !important;
        }
        div.stButton > button:first-child:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 12px 24px -5px rgba(56, 189, 248, 0.6) !important;
        }
        
        /* Footer Yazısı */
        .footer { text-align: center; color: #475569; margin-top: 5rem; font-size: 0.85rem; font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

# --- TELEFON VE ŞİFRE DURUMUNU SESSİZCE KONTROL ETME ---
is_premium = False
if "user_email_input" in st.session_state and "user_pass_input" in st.session_state:
    e = st.session_state["user_email_input"]
    p = st.session_state["user_pass_input"]
    if e in PREMIUM_USERS and PREMIUM_USERS[e] == p:
        is_premium = True

# --- 1. HERO BANNER (ÜST ALAN) ---
st.markdown("""
    <div class="hero-banner">
        <h1>⚡ LeadScout v2.5</h1>
        <p>Altunay Soft • AI-Driven Enterprise Lead Generation & Web Scraper Engine</p>
    </div>
""", unsafe_allow_html=True)

# --- 2. EN ÜSTTEKİ ARAMA MOTORU BÖLÜMÜ ---
st.markdown('<div class="content-card">', unsafe_allow_html=True)
st.markdown("<div class='section-title'>🔍 Müşteri ve İletişim Verisi Bulma Sistemi</div>", unsafe_allow_html=True)

if is_premium:
    st.markdown("<span style='color: #22c55e; font-weight: 700; font-size: 0.9rem;'>👑 PREMIUM YETKİLERİ AKTİF (Sınırsız Bölge Modu)</span>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1: country = st.text_input("🌍 Hedef Ülke", "Türkiye")
    with f2: city = st.text_input("🏙️ Hedef İl", "İstanbul")
    with f3: district = st.text_input("📍 İlçe Filtresi (Opsiyonel)", "")
    
    base_keyword = st.text_input("💼 Sektör / Anahtar Kelime", placeholder="Örn: Tekstil Fabrikası, Lojistik, Yazılım Şirketi")
    max_pages = st.slider("📊 Tarama Derinliği (Sayfa Sayısı)", min_value=1, max_value=5, value=2)
else:
    country = "Türkiye"
    city = "İstanbul"
    district = ""
    max_pages = 1
    base_keyword = st.text_input("💼 Bulmak İstediğiniz Sektör veya İşletme Türü", placeholder="Örn: Tekstil Fabrikası, Lojistik Firması, Klinik, Otomotiv")
    st.caption("ℹ️ *Standart modda aramalar İstanbul lokasyonunda ilk 5 tam ve doğrulanmış sonuçla sınırlandırılmıştır.*")

st.markdown('</div>', unsafe_allow_html=True)

# --- ARAMA TETİKLEME BUTONU ---
search_triggered = st.button("Sistem Taramasını Başlat ve Excel Üret")

# --- 3. ALT BÖLÜM: GİRİŞ PANELİ VE PREMIUM TEKLİF ALANI ---
st.markdown("<br><br>", unsafe_allow_html=True)
bottom_left, bottom_right = st.columns([2, 1])

with bottom_left:
    st.markdown('<div class="content-card" style="margin-bottom:0;">', unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🔐 Yetkili Müşteri Girişi</div>", unsafe_allow_html=True)
    
    lg_c1, lg_c2 = st.columns(2)
    with lg_c1:
        u_email = st.text_input("Kurumsal E-Posta", placeholder="ornek@altunaysoft.com", key="user_email_input")
    with lg_c2:
        u_pass = st.text_input("Şifre", type="password", placeholder="••••••••", key="user_pass_input")
        
    if u_email and u_pass:
        if u_email in PREMIUM_USERS and PREMIUM_USERS[u_email] == u_pass:
            if not is_premium:
                st.rerun()
        else:
            st.markdown("<span style='color: #ef4444; font-size: 0.85rem; font-weight: 600;'>❌ Yetkisiz Giriş: Demo hesaptasınız.</span>", unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)

with bottom_right:
    st.markdown("""
        <div class="premium-promo">
            <h4 style="color: #38bdf8; margin-top:0; font-weight: 700; font-size: 1.1rem; margin-bottom: 0.4rem;">💎 Kurumsal Enterprise Lisans</h4>
            <p style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 0px; line-height: 1.4;">Sınırsız sayfa derinliği, global ülke/il otomasyonu ve sansürsüz veri indirme hakları için bizimle entegre olun.</p>
            <a href="https://denizaltny.com" target="_blank" class="promo-btn">
                💼 Altunay Soft İletişim Hattı
            </a>
        </div>
    """, unsafe_allow_html=True)

# --- 4. VERİ KAZIMA VE SONUÇ MOTORU ---
if search_triggered:
    if not base_keyword:
        st.error("❌ Lütfen aratmak istediğiniz sektörü boş bırakmayın.")
    else:
        st.markdown("---")
        target_location = f"{district} {city} {country}".strip()
        full_query = f"{base_keyword} {target_location}"
        
        status_container = st.empty()
        progress_bar = st.progress(0)
        
        all_leads = []
        start_index = 0
        loop_range = max_pages if is_premium else 1
        
        for page in range(loop_range):
            status_container.markdown(f"🛰️ **Altunay Soft Bulut Sunucusu:** Haritalar katmanında `{full_query}` sorgulanıyor...")
            encoded_keyword = urllib.parse.quote(full_query)
            url = f"https://serpapi.com/search.json?engine=google_maps&q={encoded_keyword}&start={start_index}&api_key={SERPAPI_KEY}&hl=tr&gl=tr"
            
            try:
                with urllib.request.urlopen(url) as response:
                    data = json.loads(response.read().decode())
                results = data.get("local_results", [])
                
                if not results:
                    break
                    
                for index, item in enumerate(results):
                    if not is_premium and len(all_leads) >= 5:
                        break
                        
                    title = item.get("title", "Bilinmiyor")
                    phone = item.get("phone", "Yok")
                    website = item.get("website", "Yok")
                    
                    if any(lead["İşletme Adı"] == title for lead in all_leads):
                        continue
                        
                    status_container.markdown(f"🔍 **Derin Web Taraması:** `{title}` için kurumsal e-posta sorgulanıyor...")
                    email = extract_email_from_website(website)
                    
                    if not is_premium and email == "Yok":
                        clean_title = title.lower().replace(" ", "").replace("i̇", "i")
                        email = f"info@{clean_title}.com"
                        
                    all_leads.append({
                        "İşletme Adı": title,
                        "Telefon": phone,
                        "Kurumsal E-Posta": email,
                        "Web Sitesi": website,
                        "Adres/Konum": item.get("address", "Yok")
                    })
                
                if not is_premium and len(all_leads) >= 5:
                    break
                    
                start_index += 20
                time.sleep(0.2)
                
            except Exception as e:
                st.error(f"Sistem hatası: {e}")
                break
                
        status_container.empty()
        progress_bar.empty()
        
        if all_leads:
            st.success(f"📊 Analiz Başarılı! {len(all_leads)} kurumsal firma verisi listelendi.")
            st.dataframe(all_leads, use_container_width=True)
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=["İşletme Adı", "Telefon", "Kurumsal E-Posta", "Web Sitesi", "Adres/Konum"])
            writer.writeheader()
            for lead in all_leads:
                writer.writerow(lead)
            csv_data = "\ufeff" + output.getvalue()
            
            st.download_button(
                label="📥 Doğrulanmış Excel Listesini İndir (CSV)",
                data=csv_data.encode('utf-8-sig'),
                file_name=f"altunaysoft_{base_keyword}.csv",
                mime="text/csv",
            )
        else:
            st.warning("⚠️ Eşleşen kurumsal veri kaydı bulunamadı.")

# --- 5. FOOTER (İMZA ALANI) ---
st.markdown("""
    <div class="footer">
        <hr style="border-color: #1e293b;">
        © 2026 Altunay Soft Data Analytics Suite • Tüm Hakları Sıkı Sıkıya Saklıdır.<br>
        <span style="font-size: 0.8rem; color: #475569;">
            Powered by <a href="https://denizaltny.com" target="_blank" style="color: #38bdf8; text-decoration: none; font-weight: 600;">Deniz</a>
        </span>
    </div>
""", unsafe_allow_html=True)
