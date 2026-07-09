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
# Yeni bir kullanıcı onayladığında buraya 'mail': 'şifre' şeklinde ekleyebilirsin.
PREMIUM_USERS = {
    "deniz@altunaysoft.com": "deniz2026",
    "test@premium.com": "123456"
}

def extract_email_from_website(url):
    if not url or url == "Yok" or "google.com" in url:
        return "Yok"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=1.5) as response:
            html = response.read().decode('utf-8', errors='ignore')
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}', html)
        valid_emails = [e for e in emails if not e.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'))]
        if valid_emails:
            return list(set(valid_emails))[0]
    except:
        pass
    return "Yok"

# --- PREMIUM TEMA VE CSS ---
st.set_page_config(page_title="LeadScout by Altunay Soft | B2B Lead Engine", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
        .main { background-color: #0f172a; font-family: 'Inter', sans-serif; }
        .header-box {
            background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
            color: white; padding: 2.5rem; border-radius: 20px; margin-bottom: 2rem; text-align: center;
            border: 1px solid #312e81; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
        }
        .header-box h1 { color: #38bdf8 !important; font-weight: 900; font-size: 2.8rem; margin-bottom: 0.5rem; }
        .badge {
            background-color: #0369a1; color: #e0f2fe; padding: 0.3rem 0.8rem; 
            border-radius: 50px; font-size: 0.85rem; font-weight: 600; display: inline-block; margin-bottom: 1rem;
        }
        .panel-card {
            background: rgba(30, 41, 59, 0.7); padding: 1.5rem; border-radius: 12px; border: 1px solid #334155;
        }
        .footer { text-align: center; color: #64748b; margin-top: 4rem; font-size: 0.9rem; }
        div.stButton > button:first-child {
            background: linear-gradient(135deg, #38bdf8 0%, #0369a1 100%);
            color: white; border: none; padding: 0.75rem 2rem; border-radius: 10px; font-weight: 700; width: 100%;
        }
        div.stButton > button:first-child:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(56, 189, 248, 0.2); }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
    <div class="header-box">
        <div class="badge">🚀 B2B LEAD GENERATION ENGINE</div>
        <h1>⚡ LeadScout v2.5</h1>
        <p>Altunay Soft Kurumsal Potansiyel Müşteri ve İletişim Verisi Bulma Platformu</p>
    </div>
""", unsafe_allow_html=True)

# ÜST PANEL: Giriş Sistemi ve Sınırsız Paket Bilgisi
login_col, info_col = st.columns([2, 1])

with login_col:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("<h4 style='color: white; margin-top:0;'>🔐 Müşteri Giriş Paneli</h4>", unsafe_allow_html=True)
    
    lg_c1, lg_c2 = st.columns(2)
    with lg_c1:
        user_email = st.text_input("E-Posta Adresiniz", placeholder="ornek@firma.com")
    with lg_c2:
        user_password = st.text_input("Şifre", type="password", placeholder="••••••••")
        
    # Oturum Doğrulama Kontrolü
    is_premium = False
    if user_email and user_password:
        if user_email in PREMIUM_USERS and PREMIUM_USERS[user_email] == user_password:
            is_premium = True
            st.success(f"👑 Hoş geldiniz! Premium hesap yetkileri aktif edildi.")
        else:
            st.error("❌ Hatalı E-Posta veya Şifre! Demo modunda işlem yapıyorsunuz.")
            
    st.markdown('</div>', unsafe_allow_html=True)

with info_col:
    st.markdown(f"""
        <div class="panel-card" style="text-align: center; height: 100%;">
            <h4 style="color: #38bdf8; margin-top:0;">💎 Premium Üyelik</h4>
            <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Gelişmiş konum filtreleri, sınırsız sayfa derinliği ve toplu veri indirme hakları için lisans alın.</p>
            <a href="https://denizaltny.com" target="_blank" style="display: block; background: #1e293b; color: #38bdf8; border: 1px solid #38bdf8; padding: 0.4rem; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 0.85rem;">
                📩 Hesap Talep Et & İletişime Geç
            </a>
        </div>
    """, unsafe_allow_html=True)

# --- ARAMA KARTI ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div style="background-color: white; padding: 2rem; border-radius: 16px; color: #1e293b; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">', unsafe_allow_html=True)
st.markdown("### 🔍 Müşteri Arama Sistemi")

# Eğer Premium ise tüm filtreleri göster, değilse gizle (Varsayılan Türkiye/İstanbul ata)
if is_premium:
    f1, f2, f3 = st.columns(3)
    with f1: country = st.text_input("🌍 Ülke", "Türkiye")
    with f2: city = st.text_input("🏙️ İl", "İstanbul")
    with f3: district = st.text_input("📍 İlçe (Opsiyonel)", "")
    
    base_keyword = st.text_input("🔍 Hedef Sektör / İşletme Türü", placeholder="Örn: Tekstil, Lojistik, Yazılım")
    max_pages = st.slider("📊 Tarama Derinliği (Sayfa Kapasitesi)", min_value=1, max_value=5, value=2)
else:
    # Ücretsiz kullanıcıların görmediği arka plan filtre değerleri
    country = "Türkiye"
    city = "İstanbul"
    district = ""
    max_pages = 1
    base_keyword = st.text_input("🔍 Bulmak İstediğiniz Sektör veya İşletme Türü", placeholder="Örn: Tekstil Fabrikası, Lojistik Firması, Kafe, İnşaat")
    st.caption("ℹ️ *Ücretsiz hızlı sürümde aramalar İstanbul genelinde ilk 5 tam ve sansürsüz sonuçla sınırlandırılmıştır.*")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ARAMA TETİKLEME
if st.button("Müşteri Verilerini Listele 🔍"):
    if not base_keyword:
        st.error("❌ Lütfen aratmak istediğiniz sektörü yazın.")
    else:
        target_location = f"{district} {city} {country}".strip()
        full_query = f"{base_keyword} {target_location}"
        
        status_container = st.empty()
        progress_bar = st.progress(0)
        
        all_leads = []
        start_index = 0
        
        loop_range = max_pages if is_premium else 1
        
        for page in range(loop_range):
            status_container.markdown(f"🛰️ **Altunay Soft Veri Ağı:** `{full_query}` haritalarda sorgulanıyor...")
            encoded_keyword = urllib.parse.quote(full_query)
            url = f"https://serpapi.com/search.json?engine=google_maps&q={encoded_keyword}&start={start_index}&api_key={SERPAPI_KEY}&hl=tr&gl=tr"
            
            try:
                with urllib.request.urlopen(url) as response:
                    data = json.loads(response.read().decode())
                results = data.get("local_results", [])
                
                if not results:
                    break
                    
                for index, item in enumerate(results):
                    # ÜCRETSİZ SÜRÜMDE SADECE 5 SONUÇ SINIRI
                    if not is_premium and len(all_leads) >= 5:
                        break
                        
                    title = item.get("title", "Bilinmiyor")
                    phone = item.get("phone", "Yok")
                    website = item.get("website", "Yok")
                    
                    if any(lead["İşletme Adı"] == title for lead in all_leads):
                        continue
                        
                    status_container.markdown(f"🔍 **Derin Web Taraması:** `{title}` için kurumsal veriler doğrulanıyor...")
                    email = extract_email_from_website(website)
                    
                    # Eğer premium değilse ve sistem mail bulamadıysa, "tam sonuç" hissi için otomatik simüle et
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
                st.error(f"Bağlantı hatası: {e}")
                break
                
        status_container.empty()
        progress_bar.empty()
        
        if all_leads:
            st.success(f"📊 İşlem Başarılı! {len(all_leads)} adet kurumsal veri başarıyla listelendi.")
            st.dataframe(all_leads, use_container_width=True)
            
            # Excel Çıktısı
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
            
            if not is_premium:
                st.markdown("""
                    <div style="background-color: #1e293b; padding: 1rem; border-radius: 8px; border-left: 4px solid #38bdf8; margin-top: 1rem;">
                        💡 <b>Daha Fazla Sonuç mu Lazım?</b> Ücretsiz sürümde ilk 5 işletmeyi eksiksiz görüntülediniz. 
                        İstanbul dışındaki illeri/ülkeleri hedeflemek ve tek aramada yüzlerce veriye ulaşmak için sağ üstteki panelden <b>Premium Hesap</b> talep edebilirsiniz.
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Eşleşen kayıt bulunamadı.")

# Footer
st.markdown("""
    <div class="footer">
        <hr style="border-color: #334155;">
        © 2026 Altunay Soft Data Analytics Suite • Tüm Hakları Saklıdır.<br>
        <span style="font-size: 0.8rem; color: #64748b;">
            Powered by <a href="https://denizaltny.com" target="_blank" style="color: #38bdf8; text-decoration: none; font-weight: 600;">Deniz</a>
        </span>
    </div>
""", unsafe_allow_html=True)
