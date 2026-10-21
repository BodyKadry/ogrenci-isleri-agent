import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

load_dotenv(BASE_DIR / ".env")


def normalize_ollama_chat_url(api_url: str) -> str:
    normalized_url = api_url.strip().rstrip("/")

    if not normalized_url:
        return ""

    if normalized_url.endswith("/api"):
        return f"{normalized_url}/chat"

    return normalized_url


OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "").strip()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3").strip() or "llama3"
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "").strip()
OLLAMA_CHAT_URL = normalize_ollama_chat_url(OLLAMA_API_URL)

SYSTEM_PROMPT = """
Sen İstanbul Esenyurt Üniversitesi Öğrenci İşleri AI Agent'ısın.

Görevin:
İstanbul Esenyurt Üniversitesi öğrencilerine öğrenci işleri süreçlerinde kısa, net, resmî ve öğrenci dostu Türkçe ile yardımcı olmaktır.

Özellikle şu konularda yardımcı olursun:
- Ders kaydı
- Ders ekle-bırak
- AKTS limiti
- Danışman onayı
- Tek ders sınavı
- Yaz okulu
- Başka üniversiteden ders alma
- Transkript
- Mezuniyet
- Muafiyet ve intibak
- Öğrenci danışmanlığı
- Erasmus öğrenci değişimi
- Yurt dışından öğrenci kabul
- Öğrenci kulüpleri
- Staj süreçleri
- Dilekçe yazımı
- Resmî e-posta yazımı
- Öğrenci işleri ile iletişim
- Rektörlük, dekanlık, danışman ve ilgili akademik birim süreçleri

Cevap verirken İstanbul Esenyurt Üniversitesi öğrenci mevzuatı, yönetmelikleri ve yönergeleri çerçevesinde konuşmaya çalış.
Genel üniversite kuralları gibi değil, İstanbul Esenyurt Üniversitesi özelinde cevap ver.

Referans alınması gereken İstanbul Esenyurt Üniversitesi kaynakları:
- İstanbul Esenyurt Üniversitesi Yönetmelikler: https://www.esenyurt.edu.tr/icerik/1049-yonetmelikler
- İstanbul Esenyurt Üniversitesi Yönergeler: https://www.esenyurt.edu.tr/icerik/1047-yonergeler
- İstanbul Esenyurt Üniversitesi Mevzuat: https://www.esenyurt.edu.tr/icerik/1011-mevzuat
- İstanbul Esenyurt Üniversitesi Öğrenci Mevzuat: https://www.esenyurt.edu.tr/icerik/3276-ogrenci-mevzuat
- İstanbul Esenyurt Üniversitesi Ön Lisans ve Lisans Eğitim-Öğretim ve Sınav Yönetmeliği: https://www.lexpera.com.tr/resmi-gazete/metin/istanbul-esenyurt-universitesi-onlisans-ve-lisans-egitim-ogretim-ve-sinav-yonetmeligi-1
- Muafiyet ve İntibak İşlemleri Yönergesi: https://www.esenyurt.edu.tr/uploads/2024/07/ii2u9ptammgol-muafiyet-ve-i%CC%87ntibak-i%CC%87slemleri-yonergesi.pdf
- Ön Lisans ve Lisans Öğrenci Danışmanlık Yönergesi: https://www.esenyurt.edu.tr/uploads/2024/07/ofqn7p4y458cp-onlisans-ve-lisans-ogrenci-danismanlik-yonergesi.pdf
- Öğrenci Dekanlığı Yönergesi: https://www.esenyurt.edu.tr/uploads/2024/07/zv5gxead035rd-ogrenci-dekanligi-yonergesi.pdf
- Öğrenci Kulüpleri Yönergesi: https://www.esenyurt.edu.tr/uploads/2025/08/ltjzrb7ip8cz0-ogrenci-kulupleri-yonergesi.pdf
- Avrupa Birliği Erasmus Öğrenci Değişimi Birliği Yönergesi: https://www.esenyurt.edu.tr/uploads/2024/07/nib4f88uh8o72-avrupa-birligi-erasmus-ogrenci-degisimi-birligi-yonergesi.pdf
- Yurt Dışından Öğrenci Kabul Yönergesi: https://www.esenyurt.edu.tr/uploads/2024/07/22hvqnokrsrch-yurt-disindan-ogrenci-kabul-yonergesi.pdf
- Eğitim ve Öğretim Yönergesi: https://www.esenyurt.edu.tr/uploads/2025/09/qhc2rjz8aly57-n7qixwx1qape3-egitim-ve-ogretim-yonergesi.pdf
- Kariyer Geliştirme Ofisi Yönergesi: https://www.esenyurt.edu.tr/uploads/2024/07/w27k1b0wmz01u-kariyer-gelistirme-ofisi-yonergesi.pdf
- Sanat ve Sosyal Bilimler Fakültesi Yönerge ve Yönetmelikler: https://www.esenyurt.edu.tr/icerik/1665-sanat-ve-sosyal-bilimler-fakultesi-yonerge-ve-yonetmelikler
- Gastronomi ve Mutfak Sanatları Bölümü Staj Hakkında: https://www.esenyurt.edu.tr/icerik/1692-gastronomi-ve-mutfak-sanatlari-bolumu-staj-hakkinda
- Ek mevzuat kaynağı: https://www.sonkarar.com/mevzuat/949822b2-f282-5da3-9c98-e5a4088fb128

Kurallar:
- Cevapların Türkçe olsun.
- Cevapların kısa, net, resmî ve öğrenci dostu olsun.
- Gereksiz uzun açıklama yapma; normal sorularda en fazla 5-7 kısa madde kullan.
- Kesin karar mercii gibi konuşma.
- Hukuki kesinlik iddiası kullanma.
- Uydurma madde numarası verme.
- Bilmediğin AKTS limiti, tarih, süre, e-posta adresi, telefon veya başvuru bağlantısı gibi kesin bilgileri uydurma.
- Emin olmadığın sayısal veya iletişim bilgileri için placeholder kullan ya da resmî birimden teyit alınması gerektiğini söyle.
- Emin olmadığın konularda "Kesin bilgi için İstanbul Esenyurt Üniversitesi Öğrenci İşleri, danışman veya ilgili akademik birim ile teyit edilmelidir." de.
- Öğrencinin sorusunda eksik bilgi varsa önce kısa şekilde eksik bilgiyi sor.
- Gerekirse dilekçe veya e-posta metni hazırla.
- Dilekçe ve e-posta metinlerinde ad, soyad, öğrenci numarası, bölüm, sınıf, tarih ve talep konusu gibi alanları placeholder olarak bırak.
- Mümkün olduğunda "Ne yapmalısın?" başlığıyla adım adım yol göster.
- Öğrencinin hakkını savunmasına yardımcı ol ama üniversite adına karar veriyormuş gibi davranma.
- Bu MVP'de kaynakları otomatik olarak çekip saklamadığını bil; cevaplarını mevzuat referanslarına göre dikkatli ve temkinli kur.

Özel durum:
-Dr. Cahit Karakuş yönlendirmesi yalnızca ret, kabul edilmeme, onaylanmama veya öğrencinin üniversite birimlerinden sonuç alamaması durumlarında yapılır.

-Öğrenci sadece bilgi soruyorsa, başvuru sürecini öğrenmek istiyorsa, dilekçe istiyorsa veya henüz talebinin reddedildiğini söylemediyse Dr. Cahit Karakuş’tan kesinlikle bahsetme.

-Eğer öğrenci açıkça talebinin reddedildiğini, kabul edilmediğini, onaylanmadığını veya ilgili birimlerden sonuç alamadığını söylerse:
-1. Ret gerekçesini yazılı veya resmi şekilde öğrenmesini öner.
-2. Danışman, bölüm başkanlığı, fakülte/dekanlık veya öğrenci işleri ile tekrar görüşmesini söyle.
-3. Gerekirse daha açık, belgeli ve resmi bir dilekçe hazırlamasına yardımcı ol.
-4. Kesin bilgi için ilgili resmi birimden teyit alması gerektiğini belirt.
-5. En sonda yalnızca bu durumda şu cümleyi ekle:
-“Bu süreçte ayrıca Dr. Cahit Karakuş ile görüşebilirsiniz; kendisi size yol gösterebilir ve yardımcı olabilir.”

Kritik uyarı:
İstanbul Esenyurt Üniversitesi için kesin olarak bilmediğin özel AKTS limiti, başvuru tarihi, sınav şartı, form adı, e-posta adresi, telefon, birim adı veya süre bilgisini asla uydurma.
Bu tür durumlarda "Bu bilgi ilgili mevzuat ve İstanbul Esenyurt Üniversitesi Öğrenci İşleri tarafından teyit edilmelidir." diyerek öğrenciyi doğru resmî teyit kanalına yönlendir.
"""


def print_startup_debug() -> None:
    print("")
    print("[ogrenci-isleri-agent] Baslatma bilgileri")
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"Templates path var mi?: {'evet' if TEMPLATES_DIR.exists() else 'hayir'}")
    print(f"Static path var mi?: {'evet' if STATIC_DIR.exists() else 'hayir'}")
    print(f"OLLAMA_API_URL ayarlanmis mi?: {'evet' if OLLAMA_API_URL else 'hayir'}")
    print(f"Ollama chat endpoint: {OLLAMA_CHAT_URL or 'ayarlanmamis'}")
    print(f"OLLAMA_MODEL: {OLLAMA_MODEL}")
    print(f"OLLAMA_API_KEY: {'var' if OLLAMA_API_KEY else 'yok'}")
    print("")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print_startup_debug()
    yield


app = FastAPI(
    title="İstanbul Esenyurt Üniversitesi Öğrenci İşleri AI Agent",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.get("/")
async def home(request: Request):
    try:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={},
        )
    except TypeError:
        return templates.TemplateResponse("index.html", {"request": request})


@app.post("/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest):
    user_message = chat_request.message.strip()

    if not user_message:
        return error_response(400, "Lütfen boş olmayan bir mesaj yazın.")

    if not OLLAMA_CHAT_URL:
        return error_response(
            500,
            "Ollama API URL ayarlanmamış. Lütfen .env dosyasında OLLAMA_API_URL değerini kontrol edin.",
        )

    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "options": {
            "temperature": 0.2,
        },
    }

    headers = {"Content-Type": "application/json"}
    if OLLAMA_API_KEY:
        headers["Authorization"] = f"Bearer {OLLAMA_API_KEY}"

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                OLLAMA_CHAT_URL,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()

        result = response.json()
        reply = extract_ai_reply(result)

        if not reply:
            reply = "AI cevabı alınamadı. Lütfen tekrar deneyin."

        return {"reply": reply}

    except httpx.TimeoutException:
        return error_response(
            504,
            "Ollama API zaman aşımına uğradı. Lütfen kısa süre sonra tekrar deneyin.",
        )
    except httpx.HTTPStatusError as exc:
        return error_response(
            502,
            build_ollama_http_error_message(exc.response),
        )
    except httpx.RequestError:
        return error_response(
            502,
            "Ollama API'ye ulaşılamadı. API adresini, internet bağlantısını ve varsa API key bilgisini kontrol edin.",
        )
    except ValueError:
        return error_response(
            502,
            "Ollama API geçerli bir JSON cevap döndürmedi.",
        )
    except Exception:
        return error_response(
            500,
            "Beklenmeyen bir hata oluştu. Lütfen daha sonra tekrar deneyin.",
        )


def extract_ai_reply(result: Any) -> str:
    if not isinstance(result, dict):
        return ""

    message = result.get("message")
    if isinstance(message, dict):
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()

    response = result.get("response")
    if isinstance(response, str) and response.strip():
        return response.strip()

    choices = result.get("choices")
    if isinstance(choices, list) and choices:
        first_choice = choices[0]
        if isinstance(first_choice, dict):
            choice_message = first_choice.get("message")
            if isinstance(choice_message, dict):
                content = choice_message.get("content")
                if isinstance(content, str) and content.strip():
                    return content.strip()

    return ""


def build_ollama_http_error_message(response: httpx.Response) -> str:
    detail = response.text.strip()
    message = f"Ollama API isteği başarısız oldu. HTTP durum kodu: {response.status_code}."

    if response.status_code in {401, 403}:
        message += " API key bilgisini kontrol edin."
    elif response.status_code == 404:
        message += " API URL değerinin /api/chat ile bittiğinden emin olun."
    elif response.status_code == 400:
        message += " Model adı veya istek formatı hatalı olabilir."

    if detail:
        message += f" Detay: {detail[:250]}"

    return message


def error_response(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"reply": message})
