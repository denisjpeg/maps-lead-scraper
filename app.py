from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import urllib.request
import urllib.parse
import json
import time
import re

app = FastAPI(title="Altunay Soft LeadScout API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    is_premium = False
    # Küçük harf duyarlılığı ve boşluk temizleme ile kesin giriş doğrulaması
    user_email = req.email.strip().lower() if req.email else ""
    if user_email and req.password:
        if PREMIUM_USERS.get(user_email) == req.password.strip():
            is_premium = True

    # Filtrelerin birleştirilmesi
    target_location = f"{req.district} {req.city} {req.country}".strip()
    full_query = f"{req.keyword} {target_location}"
    
    encoded_keyword = urllib.parse.quote(full_query)
    url = f"https://serpapi.com/search.json?engine=google_maps&q={encoded_keyword}&api_key={SERPAPI_KEY}&hl=tr&gl=tr"
    
    try:
        req_obj = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_obj) as response:
            data = json.loads(response.read().decode())
        results = data.get("local_results", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    all_leads = []
    limit = 20 if is_premium else 5  # Premium ise ilk 20, demo ise 5 sonuç

    for item in results[:limit]:
        title = item.get("title", "Bilinmiyor")
        phone = item.get("phone", "Yok")
        website = item.get("website", "Yok")
        
        # Premium kullanıcı için derin web e-posta taramasını çalıştır
        email = "Yok"
        if is_premium:
            if website and website != "Yok":
                email = extract_email(website)
        else:
            # Demo kullanıcı için simüle edilmiş örnek e-posta gösterimi
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
        "is_premium": is_premium,
        "data": all_leads
    }
