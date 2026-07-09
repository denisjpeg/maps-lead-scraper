import os
import time
import json
import re
import urllib.request
import urllib.parse
from collections import defaultdict, deque
from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Altunay Soft LeadScout API")

# ---------------------------------------------------------------------------
# 🔐 GİZLİ BİLGİLER — artık kaynak kodunda değil, ortam değişkenlerinde.
# Render / sunucu panelinden şu değişkenleri tanımlaman gerekiyor:
#   SERPAPI_KEY        -> SerpAPI anahtarın
#   PREMIUM_USERS       -> "eposta1:sifre1,eposta2:sifre2" formatında
#   ALLOWED_ORIGINS     -> "https://siten.com,https://www.siten.com" formatında
# ---------------------------------------------------------------------------

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
if not SERPAPI_KEY:
    raise RuntimeError(
        "SERPAPI_KEY ortam değişkeni tanımlı değil. "
        "Sunucu panelinden (ör. Render > Environment) SERPAPI_KEY değişkenini eklemeden uygulama başlatılamaz."
    )

def _parse_kv_pairs(raw: str) -> dict:
    pairs = {}
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk or ":" not in chunk:
            continue
        email, password = chunk.split(":", 1)
        pairs[email.strip().lower()] = password.strip()
    return pairs

PREMIUM_USERS = _parse_kv_pairs(os.environ.get("PREMIUM_USERS", ""))

_raw_origins = os.environ.get("ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]
if not ALLOWED_ORIGINS:
    # Değişken tanımlanmamışsa yalnızca yerel geliştirmeye izin ver; canlıda
    # mutlaka ALLOWED_ORIGINS ortam değişkenini gerçek alan adınla tanımla.
    ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:5500"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

# ---------------------------------------------------------------------------
# 🛡️ Basit IP başına hız sınırlama (bellek içi).
# Tek sunuculu küçük dağıtımlar için yeterlidir; birden çok worker/instance
# kullanırsan Redis tabanlı bir çözüme (ör. slowapi + redis) geçmen önerilir.
# ---------------------------------------------------------------------------
RATE_LIMIT_MAX_REQUESTS = 12
RATE_LIMIT_WINDOW_SECONDS = 60
_request_log: dict[str, deque] = defaultdict(deque)

def _check_rate_limit(client_ip: str):
    now = time.time()
    log = _request_log[client_ip]
    while log and now - log[0] > RATE_LIMIT_WINDOW_SECONDS:
        log.popleft()
    if len(log) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Çok fazla istek gönderildi. Lütfen bir dakika sonra tekrar deneyin.",
        )
    log.append(now)


class SearchRequest(BaseModel):
    keyword: str = Field(..., min_length=2, max_length=80)
    country: str = Field("Türkiye", max_length=60)
    city: str = Field("İstanbul", max_length=60)
    district: str = Field("", max_length=60)
    email: str = Field("", max_length=120)
    password: str = Field("", max_length=120)
    seen_titles: List[str] = Field(default_factory=list, max_length=200)


def extract_email(url: str) -> str:
    if not url or url == "Yok" or "google.com" in url:
        return "Yok"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=1.5) as response:
            html = response.read().decode("utf-8", errors="ignore")
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}", html)
        valid = [e for e in emails if not e.endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"))]
        if valid:
            return list(set(valid))[0]
    except Exception:
        pass
    return "Yok"


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/scrape")
async def scrape_leads(req: SearchRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    _check_rate_limit(client_ip)

    is_premium = False
    if req.email and req.password:
        stored = PREMIUM_USERS.get(req.email.strip().lower())
        if stored is not None and stored == req.password:
            is_premium = True

    target_location = f"{req.district} {req.city} {req.country}".strip()
    full_query = f"{req.keyword} {target_location}"
    encoded_keyword = urllib.parse.quote(full_query)

    url = (
        f"https://serpapi.com/search.json?engine=google_maps"
        f"&q={encoded_keyword}&api_key={SERPAPI_KEY}&hl=tr&gl=tr"
    )
    if is_premium:
        url += "&start=0"

    try:
        req_obj = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req_obj, timeout=10) as response:
            data = json.loads(response.read().decode())
        results = data.get("local_results", [])
    except Exception:
        # SerpAPI hata detayını (anahtar, kota vb. sızdırabilecek bilgi) dışarı vermiyoruz.
        raise HTTPException(status_code=502, detail="Veri sağlayıcısına ulaşılamadı. Lütfen daha sonra tekrar deneyin.")

    all_leads = []

    for item in results:
        title = item.get("title", "Bilinmiyor")

        # 👑 Premium kullanıcı için: daha önce görülen firmaları atla.
        if is_premium and title in req.seen_titles:
            continue

        phone = item.get("phone", "Yok")
        website = item.get("website", "Yok")

        # Yalnızca gerçekten bulunan e-postalar gösterilir; hiçbir zaman
        # tahmini/uydurma bir e-posta üretilmez. Bulunamazsa "Yok" döner.
        email = extract_email(website) if is_premium else "Yok"

        all_leads.append({
            "title": title,
            "phone": phone,
            "email": email,
            "website": website,
            "address": item.get("address", "Yok"),
        })

        if not is_premium and len(all_leads) >= 5:
            break
        if is_premium and len(all_leads) >= 20:
            break

    return {
        "status": "success",
        "is_premium": is_premium,
        "data": all_leads,
    }
