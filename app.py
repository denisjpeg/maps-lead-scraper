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
    """İşletmenin web sitesine gizlice gidip e-posta adresi arar."""
    if not url or url == "Yok" or "google.com" in url:
        return "Yok"
    try:
        # Web sitesinin HTML kodunu indir
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
        # Düzenli ifade (Regex) ile e-posta adreslerini ayıkla
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}', html)
        
        # Gereksiz imaj uzantılarını veya çöpleri temizle
        valid_emails = [e for e in emails if not e.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg'))]
        
        if valid_emails:
            return list(set(valid_emails))[0] # İlk benzersiz e-postayı dön
    except:
        pass
    return "Yok"

# Web Sayfası Tasarımı
st.set_page_config(page_title="Altunay Soft - Harita & Mail Kazıcı", page_icon="🚀", layout="wide")

st.title("🚀 Gelişmiş Harita & E-Posta Kazıcı")
st.subheader("Altunay Soft Lead Generation SaaS v2.0")

# Dinamik Konum ve Kelime Girişleri
col1, col2, col3 = st.columns(3)
with col1:
    country = st.text_input("🌍 Ülke (Zorunlu):", "Türkiye")
with col2:
    city = st.text_input("🏙️ İl (Zorunlu):", "İstanbul")
with col3:
    district = st.text_input("📍 İlçe (İsteğe Bağlı - Boş Bırakılabilir):", "")

base_keyword = st.text_input("🔍 Aratılacak Sektör / Kelime (Örn: Lojistik, Tekstil, Dentist):", "")
max_pages = st.slider("Tarama Derinliği (Sayfa Sayısı - Her sayfa ~20 sonuç getirir):", min_value=1, max_value=5, value=2)

if st.button("Müşterileri ve E-Postaları Bul 🔍", type="primary"):
    if not country or not city or not base_keyword:
        st.warning("⚠️ Lütfen Ülke, İl ve Anahtar Kelime alanlarını boş bırakmayın!")
    else:
        # Arama terimini dinamik oluşturuyoruz
        target_location = f"{district} {city} {country}".strip()
        full_query = f"{base_keyword} {target_location}"
        
        st.info(f"🚀 **Arama Hedefi:** `{full_query}` için süreç başlatıldı. Web sitelerinden mailler kazınıyor...")
        
        all_leads = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        start_index = 0
        for page in range(max_pages):
            status_text.write(f"⏳ Google Haritalar'dan Sayfa {page + 1} sonuçları alınıyor...")
            encoded_keyword = urllib.parse.quote(full_query)
            url = f"https://serpapi.com/search.json?engine=google_maps&q={encoded_keyword}&start={start_index}&api_key={SERPAPI_KEY}&hl=tr&gl=tr"
            
            try:
                with urllib.request.urlopen(url) as response:
                    data = json.loads(response.read().decode())
                    
                results = data.get("local_results", [])
                if not results:
                    status_text.write("ℹ️ Bu sayfada başka sonuç bulunamadı.")
                    break
                    
                for item in results:
                    title = item.get("title", "Bilinmiyor")
                    phone = item.get("phone", "Yok")
                    website = item.get("website", "Yok")
                    
                    # Aynı firmayı tekrar eklememe kontrolü
                    if any(lead["İşletme Adı"] == title for lead in all_leads):
                        continue
                    
                    # Eğer web sitesi varsa arka planda e-posta adresi tara
                    status_text.write(f"🔎 `{title}` firmasının web sitesinden mail adresi aranıyor...")
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
                time.sleep(0.5)
                
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")
                break
                
        status_text.success(f"✨ İşlem Tamamlandı! Toplam {len(all_leads)} benzersiz işletme listelendi.")
        
        if all_leads:
            # Canlı tabloyu göster
            st.dataframe(all_leads, use_container_width=True)
            
            # Excel (CSV) çıktısı hazırlama
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=["İşletme Adı", "Telefon", "E-Posta", "Web Sitesi", "Konum/Adres", "Kategori"])
            writer.writeheader()
            for lead in all_leads:
                writer.writerow(lead)
            
            csv_data = "\ufeff" + output.getvalue()
            
            st.download_button(
                label="📥 Mail Destekli Excel Listesini İndir (CSV)",
                data=csv_data.encode('utf-8-sig'),
                file_name=f"{base_keyword.replace(' ', '_')}_{city}_leads.csv",
                mime="text/csv",
            )
