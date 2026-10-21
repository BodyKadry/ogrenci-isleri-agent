# İstanbul Esenyurt Üniversitesi Öğrenci İşleri AI Agent

Bu proje, İstanbul Esenyurt Üniversitesi öğrencilerine öğrenci işleri süreçleri hakkında yardımcı olmak için hazırlanmış basit bir web tabanlı AI agent MVP uygulamasıdır. FastAPI ile çalışır ve cevap üretmek için Ollama Cloud veya Remote Ollama API kullanır.

Uygulama bilgilendirme amaçlıdır. Kesin ve güncel bilgi için İstanbul Esenyurt Üniversitesi Öğrenci İşleri, danışman veya ilgili akademik birim ile teyit alınmalıdır.

## Özellikler

- Modern, mobil uyumlu tek sayfalık chat arayüzü
- İstanbul Esenyurt Üniversitesi öğrenci işleri süreçlerine odaklı system prompt
- Ders kaydı, ders ekle-bırak, AKTS, tek ders, yaz okulu, transkript, mezuniyet, danışman onayı, muafiyet, intibak, staj, dilekçe ve resmî e-posta konularında destek
- Örnek soru butonları
- Ollama Cloud / Remote Ollama API ile sohbet
- API URL, model adı ve API key değerlerini `.env` dosyasından okuma
- API key boş bırakıldığında Authorization header göndermeden çalışma

## Kurulum

```bash
cd ogrenci-isleri-agent
python -m venv .venv
```

Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Bağımlılıkları yükleyin:

```bash
pip install -r requirements.txt
```

## .env Ayarları

`.env.example` dosyasını `.env` adıyla kopyalayın ve kendi Ollama Cloud veya Remote Ollama API bilgilerinizi girin.

```env
OLLAMA_API_URL=https://your-ollama-api-url.com/api/chat
OLLAMA_MODEL=llama3
OLLAMA_API_KEY=your_api_key_here
```

Ollama Cloud kullanıyorsanız API URL genellikle şu formdadır:

```env
OLLAMA_API_URL=https://ollama.com/api/chat
```

API key gerekmiyorsa `OLLAMA_API_KEY` değerini boş bırakabilirsiniz:

```env
OLLAMA_API_KEY=
```

## Çalıştırma

```bash
uvicorn main:app --reload
```

Tarayıcıda şu adresi açın:

```text
http://127.0.0.1:8000
```

## Örnek Sorular

- AKTS limitimi nasıl artırabilirim?
- Tek ders sınavına girebilir miyim?
- Yaz okulunda başka üniversiteden ders alabilir miyim?
- Ders ekle-bırak için dilekçe yazar mısın?
- Danışmanım talebimi onaylamadı, ne yapmalıyım?

## Test Adımları

1. `pip install -r requirements.txt`
2. `.env` dosyasını oluştur
3. `OLLAMA_API_URL`, `OLLAMA_MODEL`, `OLLAMA_API_KEY` değerlerini gir
4. `uvicorn main:app --reload`
5. `http://127.0.0.1:8000` adresini aç
6. Chat üzerinden test mesajı gönder

## Önemli Uyarı

Bu uygulama bilgilendirme amaçlıdır. Kesin ve güncel bilgi için İstanbul Esenyurt Üniversitesi Öğrenci İşleri, danışman veya ilgili akademik birim ile teyit alınmalıdır.
