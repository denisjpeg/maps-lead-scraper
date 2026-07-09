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

# SENİN ÖZEL PREMIUM ŞİFREN (İstersen tırnak içini değiştirebilirsin)
PREMIUM_CODE = "denizpremium2026"

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
        .magnet-card {
            background: rgba(30, 41, 59, 0.7); padding: 1.5rem; border-radius: 12px; border: 1px solid #334155; text-align: center;
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
        <div class="badge">🔥 FREE DEMO SUITE</div>
        <h1>⚡ LeadScout v2.5</h1>
        <p>B2B Müşteri, Telefon ve E-Posta Bulma Otomasyonu</p>
    </div>
""", unsafe_allow_html=True)

left_col, right_col = st.columns([2, 1])

with left_col:
    st.markdown('<div style="background-color: white; padding: 2rem; border-radius: 16px; color: #1e293b; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Filtreler")
    
    c1, c2, c3 = st.columns(3)
    with c1: country = st.text_input("🌍 Ülke", "Türkiye")
    with c2: city = st.text_input("🏙️ İl", "İstanbul")
    with c3: district = st.text_input("📍 İlçe (Opsiyonel)", "")
    
    base_keyword = st.text_input("🔍 Hedef Sektör / İşletme Türü", placeholder="Örn: Tekstil, Lojistik, Yazılım")
    
    # GİZLİ PREMIUM GİRİŞ KUTUSU
    license_key = st.text_input("🔑 Altunay Soft Lisans Anahtarı (Opsiyonel)", type="password", help="Premium haklarınızı aktif etmek için anahtarınızı girin.")
    
    is_premium = (license_key == PREMIUM_CODE)
    
    if is_premium:
        st.success("👑 Premium Paket Aktif! Sınırsız arama ve sansürsüz veri modu devrede.")
        max_pages = st.slider("📊 Tarama Derinliği (Sayfa Kapasitesi)", min_value=1, max_value=5, value=2)
    else:
        st.caption("ℹ️ *Demo modunda aramalar ilk 10 sonuç ile sınırlıdır ve veri maskeleme uygulanır.*")
        max_pages = 1
        
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.markdown("""
        <div class="magnet-card">
            <h4 style="color: #38bdf8; margin-bottom: 0.5rem;">💎 Sınırsız Premium Sürüm</h4>
            <p style="color: #94a3b8; font-size: 0.9rem; text-align: left;">
                • Sınırsız Tarama ve Tam Liste Çıktısı<br>
                • Tüm Telefon ve Maillerde Sıfır Sansür<br>
                • Toplu Lokasyon ve Excel Desteği
            </p>
            <a href="https://denizaltny.com" target="_blank" style="display: block; background: #1e293b; color: #38bdf8; border: 1px solid #38bdf8; padding: 0.5rem; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 0.9rem; margin-top: 1.5rem;">
                🚀 İletişime Geç & Lisans Satın Al
            </a>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if st.button("Müşteri Datalarını Derle ve İndir 🔍"):
    if not country or not city or not base_keyword:
        st.error("❌ Lütfen zorunlu alanları doldurun.")
    else:
        target_location = f"{district} {city} {country}".strip()
        full_query = f"{base_keyword} {target_location}"
        
        status_container = st.empty()
        progress_bar = st.progress(0)
        
        all_leads = []
        start_index = 0
        
        # Premium ise slider kadar, değilse sadece 1 sayfa dönecek
        loop_range = max_pages if is_premium else 1
        
        for page in range(loop_range):
            status_container.markdown(f"🛰️ **Veri Katmanı:** `{full_query}` sorgusu taranıyor...")
            encoded_keyword = urllib.parse.quote(full_query)
            url = f"https://serpapi.com/search.json?engine=google_maps&q={encoded_keyword}&start={start_index}&api_key={SERPAPI_KEY}&hl=tr&gl=tr"
            
            try:
                with urllib.request.urlopen(url) as response:
                    data = json.loads(response.read().decode())
                results = data.get("local_results", [])
                
                if not results:
                    break
                    
                for index, item in enumerate(results):
                    # DEMO MODUNDA 10 SONUÇ SINIRI
                    if not is_premium and len(all_leads) >= 10:
                        break
                        
                    title = item.get("title", "Bilinmiyor")
                    phone = item.get("phone", "Yok")
                    website = item.get("website", "Yok")
                    
                    if any(lead["İşletme Adı"] == title for lead in all_leads):
                        continue
                        
                    status_container.markdown(f"🔍 **Derin Tarama:** `{title}` için iletişim verileri doğrulanıyor...")
                    email = extract_email_from_website(website)
                    
                    # --- MIKNATIS VE SANSÜR ALGORİTMASI ---
                    if not is_premium:
                        clean_title = title.lower().replace(" ", "").replace("i̇", "i")
                        
                        # Eğer gerçek mail/tel yoksa psikolojik merak uyandırmak için simüle et
                        if email == "Yok":
                            email = f"info@{clean_title}.com"
                        if phone == "Yok":
                            phone = "+90 212 444 00 00"
                            
                        # İlk 5 sonuç: Telefon açık, Mail gizli
                        if len(all_leads) < 5:
                            email = f"inf***@{email[email.find('@')+1:]}"
                        # Sonraki 5 sonuç: Mail açık, Telefon gizli
                        else:
                            phone = f"{phone[:7]}***"
                            if len(email) > 5:
                                email = f"{email[:2]}***{email[-6:]}"
                                
                    all_leads.append({
                        "İşletme Adı": title,
                        "Telefon": phone,
                        "Kurumsal E-Posta": email,
                        "Web Sitesi": website,
                        "Adres/Konum": item.get("address", "Yok")
                    })
                
                if not is_premium and len(all_leads) >= 10:
                    break
                    
                start_index += 20
                time.sleep(0.2)
                
            except Exception as e:
                st.error(f"Bağlantı hatası: {e}")
                break
                
        status_container.empty()
        progress_bar.empty()
        
        if all_leads:
            st.success(f"📊 Analiz Tamamlandı! {len(all_leads)} adet kurumsal veri hazırlandı.")
            st.dataframe(all_leads, use_container_width=True)
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=["İşletme Adı", "Telefon", "Kurumsal E-Posta", "Web Sitesi", "Adres/Konum"])
            writer.writeheader()
            for lead in all_leads:
                writer.writerow(lead)
            csv_data = "\ufeff" + output.getvalue()
            
            st.download_button(
                label="📥 Excel Listesini İndir (CSV)",
                data=csv_data.encode('utf-8-sig'),
                file_name=f"altunaysoft_leads_{base_keyword}.csv",
                mime="text/csv",
            )
            
            if not is_premium:
                st.markdown("""
                    <div style="background-color: #1e293b; padding: 1rem; border-radius: 8px; border-left: 4px solid #38bdf8; margin-top: 1rem;">
                        💡 <b>Demo Sürüm Sınırlandırması:</b> Sistem 10 adet örnek işletme listeledi. Algoritma gereği ilk 5 sonucun e-postaları, 
                        sonraki 5 sonuçun ise telefon numaraları maskelenmiştir. Kısıtlamaları kaldırmak ve tam erişim sağlamak için sağ panelden lisans anahtarı talep edebilirsiniz.
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
