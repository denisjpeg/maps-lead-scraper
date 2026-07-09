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

def extract_email_from_website(url):
    if not url or url == "Yok" or "google.com" in url:
        return "Yok"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        with urllib.request.urlopen(req, timeout=3) as response:
            html = response.read().decode('utf-8', errors='ignore')
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}', html)
        valid_emails = [e for e in emails if not e.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'))]
        if valid_emails:
            return list(set(valid_emails))[0]
    except:
        pass
    return "Yok"

# --- PREMIUM TEMA VE CSS AYARLARI ---
st.set_page_config(page_title="Altunay Soft | Lead Extraction Suite", page_icon="⚡", layout="wide")

# Kurumsal Kimlik CSS Enjeksiyonu
st.markdown("""
    <style>
        /* Genel Arka Plan ve Yazı Tipi */
        .main { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
        
        /* Premium Başlık Kartı */
        .header-box {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: white;
            padding: 2.5rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.1), 0 8px 10px -6px rgba(15, 23, 42, 0.1);
        }
        .header-box h1 { color: #38bdf8 !important; font-weight: 800; font-size: 2.5rem; margin-bottom: 0.5rem; }
        .header-box p { color: #94a3b8; font-size: 1.1rem; }
        
        /* Giriş Kartları */
        .input-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            margin-bottom: 1rem;
        }
        
        /* Altunay Soft İmzası */
        .footer { text-align: center; color: #64748b; margin-top: 3rem; font-size: 0.9rem; font-weight: 500; }
        
        /* Streamlit Buton Özelleştirme */
        div.stButton > button:first-child {
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            color: white;
            border: none;
            padding: 0.6rem 2rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: 1rem;
            width: 100%;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(2, 132, 199, 0.2);
        }
        div.stButton > button:first-child:hover {
            background: linear-gradient(135deg, #0369a1 0%, #075985 100%);
            box-shadow: 0 6px 16px rgba(2, 132, 199, 0.3);
            transform: translateY(-1px);
        }
    </style>
""", unsafe_allow_html=True)

# --- ARAYÜZ BAŞLANGIÇ ---
st.markdown("""
    <div class="header-box">
        <h1>⚡ LeadScout v2.5</h1>
        <p>Altunay Soft • AI-Powered B2B Lead Generation & Email Extraction Engine</p>
    </div>
""", unsafe_allow_html=True)

# Giriş Alanı Kartı
st.markdown('<div class="input-card">', unsafe_allow_html=True)
st.markdown("##### ⚙️ Filtreler ve Arama Yapılandırması")

col1, col2, col3 = st.columns(3)
with col1:
    country = st.text_input("🌍 Ülke", "Türkiye")
with col2:
    city = st.text_input("🏙️ İl", "İstanbul")
with col3:
    district = st.text_input("📍 İlçe (Opsiyonel)", "")

col_keyword, col_depth = st.columns([2, 1])
with col_keyword:
    base_keyword = st.text_input("🔍 Hedef Sektör / Anahtar Kelime", placeholder="Örn: Lojistik, Tekstil, Yazılım, Yapı Malzemeleri")
with col_depth:
    max_pages = st.slider("📊 Tarama Derinliği (Sayfa Kapasitesi)", min_value=1, max_value=5, value=2, help="Her sayfa yaklaşık 20 işletme analiz eder.")

st.markdown('</div>', unsafe_allow_html=True)

# Arama Tetikleyici
if st.button("Sistem Taramasını Başlat"):
    if not country or not city or not base_keyword:
        st.error("❌ Kritik hata: Ülke, İl ve Anahtar Kelime alanları zorunludur.")
    else:
        target_location = f"{district} {city} {country}".strip()
        full_query = f"{base_keyword} {target_location}"
        
        st.markdown("---")
        status_container = st.empty()
        progress_bar = st.progress(0)
        
        all_leads = []
        start_index = 0
        
        for page in range(max_pages):
            status_container.markdown(f"🛰️ **Google Haritalar Katmanı:** Sayfa {page + 1} verileri toplanıyor...")
            encoded_keyword = urllib.parse.quote(full_query)
            url = f"https://serpapi.com/search.json?engine=google_maps&q={encoded_keyword}&start={start_index}&api_key={SERPAPI_KEY}&hl=tr&gl=tr"
            
            try:
                with urllib.request.urlopen(url) as response:
                    data = json.loads(response.read().decode())
                    
                results = data.get("local_results", [])
                if not results:
                    break
                    
                for item in results:
                    title = item.get("title", "Bilinmiyor")
                    phone = item.get("phone", "Yok")
                    website = item.get("website", "Yok")
                    
                    if any(lead["İşletme Adı"] == title for lead in all_leads):
                        continue
                    
                    status_container.markdown(f"🔍 **Derin Web Taraması:** `{title}` firmasının e-posta adresi sorgulanıyor...")
                    email = extract_email_from_website(website)
                        
                    all_leads.append({
                        "İşletme Adı": title,
                        "Telefon": phone,
                        "E-Posta": email,
                        "Web Sitesi": website,
                        "Konum/Adres": item.get("address", "Yok"),
                        "Kategori": item.get("type", "Yok")
                    })
                
                start_index += 20
                progress_bar.progress((page + 1) / max_pages)
                time.sleep(0.3)
                
            except Exception as e:
                st.error(f"Sistem hatası: {e}")
                break
                
        # Sonuç Paneli
        status_container.empty()
        progress_bar.empty()
        
        if all_leads:
            st.success(f"📊 Analiz Başarıyla Tamamlandı! Toplam {len(all_leads)} benzersiz kurumsal veri doğrulandı.")
            
            # Tablo Görünümü
            st.dataframe(all_leads, use_container_width=True)
            
            # Excel Çıktı Motoru
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=["İşletme Adı", "Telefon", "E-Posta", "Web Sitesi", "Konum/Adres", "Kategori"])
            writer.writeheader()
            for lead in all_leads:
                writer.writerow(lead)
            
            csv_data = "\ufeff" + output.getvalue()
            
            # İndirme Buton Düzeni
            st.download_button(
                label="📥 Doğrulanmış Excel Listesini İndir (CSV)",
                data=csv_data.encode('utf-8-sig'),
                file_name=f"altunaysoft_{base_keyword.replace(' ', '_')}_{city}.csv",
                mime="text/csv",
            )
        else:
            st.warning("⚠️ Belirtilen kriterlere uygun aktif bir işletme kaydı bulunamadı.")

# Footer
st.markdown("""
    <div class="footer">
        <hr style="border-color: #e2e8f0;">
        © 2026 Altunay Soft Data Analytics Suite • Tüm Hakları Saklıdır.<br>
        <span style="font-size: 0.8rem; color: #94a3b8;">
            Powered by <a href="https://denizaltny.com" target="_blank" style="color: #38bdf8; text-decoration: none; font-weight: 600;">Deniz</a>
        </span>
    </div>
""", unsafe_allow_html=True)
