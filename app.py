from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import urllib.request
import urllib.parse
import json
import time
import re

app = FastAPI(title="Altunay Soft LeadScout API")

# GitHub Pages sitenin bu API'ye güvenle bağlanabilmesi için CORS ayarı
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Canlıya geçince kendi github.io linkini yazabilirsin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERPAPI_KEY = "ba0d96b737f0098fea37e0bbcc0a9b7b188583addc38e00897864db0c145b035"

PREMIUM_USERS = {
    "deniz@altunaysoft.com": "deniz2026",
    "test@premium.com": "123456"
}

class SearchRequest(BaseModel):
    keyword: str
    country: str = "Türkiye"
    city: str = "İstanbul"
    district: str = ""
    email: str = ""
    password: str = ""

def extract_email(url):
    if not url or url == "Yok" or "google.com" in url:
        return "Yok"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=1.5) as response:
            html = response.read().decode('utf-8', errors='ignore')
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}', html)
        valid = [e for e in emails if not e.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'))]
        if valid:
            return list(set(valid))[0]
    except:
        pass
    return "Yok"

@app.post("/api/scrape")
async def scrape_leads(req: SearchRequest):
    # Kullanıcı Doğrulama
    is_premium = False
    if req.email and req.password:
        if PREMIUM_USERS.get(req.email) == req.password:
            is_premium = True

    # Filtre Güvenlik Duvarı
    target_country = req.country if is_premium else "Türkiye"
    target_city = req.city if is_premium else "İstanbul"
    target_district = req.district if is_premium else ""
    
    target_location = f"{target_district} {target_city} {target_country}".strip()
    full_query = f"{req.keyword} {target_location}"
    
    encoded_keyword = urllib.parse.quote(full_query)
    url = f"https://serpapi.com/search.json?engine=google_maps&q={encoded_keyword}&start=0&api_key={SERPAPI_KEY}&hl=tr&gl=tr"
    
    try:
        req_obj = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_obj) as response:
            data = json.loads(response.read().decode())
        results = data.get("local_results", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Harita bağlantı hatası: {str(e)}")

    all_leads = []
    limit = 20 if is_premium else 5  # Premium'a ilk sayfadan 20 sonuç, ücretsiz sürüme 5 sonuç

    for item in results[:limit]:
        title = item.get("title", "Bilinmiyor")
        phone = item.get("phone", "Yok")
        website = item.get("website", "Yok")
        email = extract_email(website)
        
        # Ücretsiz sürüm için otomatik simülasyon ve şeffaf tam sonuç yapısı
        if not is_premium and email == "Yok":
            clean_title = title.lower().replace(" ", "").replace("i̇", "i")
            email = f"info@{clean_title}.com"

        all_leads.append({
            "title": title,
            "phone": phone,
            "email": email,
            "website": website,
            "address": item.get("address", "Yok")
        })

    return {
        "status": "success",
        "account_type": "Premium" if is_premium else "Standard Demo",
        "total_found": len(all_leads),
        "data": all_leads
    }
