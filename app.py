import streamlit as st
import csv
import urllib.request
import urllib.parse
import json
import time
import io

# SerpAPI Anahtarın
SERPAPI_KEY = "ba0d96b737f0098fea37e0bbcc0a9b7b188583addc38e00897864db0c145b035"

# Otomatik taranacak konum listesi
LOCATIONS = [
    "İstanbul Kadıköy", "İstanbul Şişli", "İstanbul İkitelli", "İstanbul Ümraniye", 
    "İstanbul Maslak", "İstanbul Maltepe", "Kocaeli Gebze", "Kocaeli İzmit", 
    "Bursa Nilüfer", "Bursa Osmangazi", "Tekirdağ Çorlu"
]

# Web Sayfası Ayarları
st.set_page_config(page_title="Altunay Soft - Harita Kazıcı", page_icon="🚀", layout="wide")

st.title("🚀 Google Maps Lead Scraper (B2B Müşteri Bulucu)")
st.subheader("Altunay Soft Data Analytics Panel")
st.write("Bulmak istediğiniz sektör kelimesini girin, sistem otomatik olarak bölgeleri tarayıp size Excel versin.")

base_keyword = st.text_input("Aratılacak Anahtar Kelime (Örn: Lojistik, Tekstil, Otomotiv):", "")
max_pages = st.slider("Konum Başına Tarama Derinliği (Sayfa Sayısı):", min_value=1, max_value=5, value=2)

if st.button("Taramayı Başlat 🔍", type="primary"):
    if not base_keyword:
        st.warning("⚠️ Lütfen önce bir anahtar kelime girin!")
    else:
        all_leads = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        total_locations = len(LOCATIONS)
        
        for index, location in enumerate(LOCATIONS):
            full_query = f"{base_keyword} {location}"
            status_text.markdown(f"**Şu an taranıyor:** `{full_query}` (Lokasyon {index+1}/{total_locations})")
            
            start_index = 0
            for page in range(max_pages):
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
                        
                        if any(lead["İşletme Adı"] == title for lead in all_leads):
                            continue
                            
                        all_leads.append({
                            "İşletme Adı": title,
                            "Telefon": phone,
                            "Web Sitesi": item.get("website", "Yok"),
                            "Konum/Adres": item.get("address", "Yok"),
                            "Kategori": item.get("type", "Yok"),
                            "Aranan Bölge": location
                        })
                    
                    start_index += 20
                    time.sleep(0.5)
                    
                except Exception as e:
                    st.error(f"Hata oluştu ({location}): {e}")
                    break
            
            progress_bar.progress((index + 1) / total_locations)
            
        status_text.success(f"✨ Tarama tamamlandı! Toplam {len(all_leads)} benzersiz işletme bulundu.")
        
        if all_leads:
            st.dataframe(all_leads, use_container_width=True)
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=["İşletme Adı", "Telefon", "Web Sitesi", "Konum/Adres", "Kategori", "Aranan Bölge"])
            writer.writeheader()
            for lead in all_leads:
                writer.writerow(lead)
            
            csv_data = "\ufeff" + output.getvalue()
            
            st.download_button(
                label="📥 Excel Sürümünü İndir (CSV)",
                data=csv_data.encode('utf-8-sig'),
                file_name=f"{base_keyword.replace(' ', '_')}_leads.csv",
                mime="text/csv",
            )
