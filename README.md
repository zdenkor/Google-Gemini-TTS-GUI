# Google TTS GUI

Moderné grafické rozhranie pre Text-to-Speech s podporou viacerých engine-ov.

## Podporované TTS Engine-y

### 🌐 Google TTS
- Bezplatný, základná kvalita
- 30+ jazykov vrátane slovenčiny

### 🔷 Edge TTS (Microsoft)
- Bezplatný, Neural hlasy
- Všetky hlasy dostupné cez API
- Podpora rýchlosti prehrávania

### ✨ Gemini 3.1 TTS (Google Cloud)
- **Premium AI-powered TTS**
- 30+ unikátnych hlasov (Achernar, Kore, Leda, Charon, ...)
- **Prompty** - štýlové inštrukcie pre kontrolu výslovnosti
- **Markup tags** - [sigh], [laughing], [uhm], [whispering], [sarcasm], [short pause], ...
- Multi-speaker konverzácie
- Vyžaduje Google Cloud API kľúč

## Funkcie

- 🎙️ **Text na reč** - Prevod textu na hlas
- 🌍 **Výber jazyka** - Podpora 30+ jazykov
- 🎭 **Prompty** (Gemini 3.1) - Štýlové inštrukcie pre kontrolu tónu
- 🗣️ **Výber hlasu** - Všetky dostupné hlasy pre každý engine
- ⚡ **Rýchlosť** - Nastavenie rýchlosti prehrávania (0.5x - 2.0x)
- 🔊 **Prehrávanie** - Priame prehrávanie vygenerovaného zvuku
- 💾 **Ukladanie** - Možnosť uložiť výstup ako MP3 súbor

## Inštalácia

1. Nainštaluj závislosti:
```bash
pip install -r requirements.txt
```

Pre Gemini 3.1 TTS potrebuješ aj:
```bash
pip install google-cloud-texttospeech
```

## Použitie

Spusti aplikáciu:
```bash
python main.py
```

### Gemini 3.1 TTS - Prompty

V prompt poli môžeš zadať štýlové inštrukcie:
- `"Povedz to priateľským a nadšeným spôsobom"`
- `"Narrate in a calm, professional tone for a documentary"`
- `"Speak like a 1940s radio news announcer"`

### Gemini 3.1 TTS - Markup tags

V texte môžeš použiť špeciálne značky:
- `[sigh]` - Vzdych
- `[laughing]` - Smiech
- `[uhm]` - Zaváhanie
- `[whispering]` - Šepkanie
- `[sarcasm]` - Sarkastický tón
- `[short pause]` - Krátka pauza
- `[medium pause]` - Stredná pauza
- `[long pause]` - Dlhá pauza

## Požiadavky

- Python 3.8+
- Internetové pripojenie
- Google Cloud API kľúč (pre Gemini 3.1 TTS)

## 🔑 Service Account pre Gemini 3.1 TTS

Gemini 3.1 TTS vyžaduje **Service Account** autentizáciu (nie jednoduchý API kľúč).

### Ako vytvoriť Service Account

1. Otvor [Google Cloud Console - Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Klikni **CREATE SERVICE ACCOUNT**
3. Zadaj názov (napr. "tts-service-account")
4. Klikni **CREATE AND CONTINUE**
5. V roli vyber: **Cloud Text-to-Speech User**
6. Klikni **CONTINUE** → **DONE**

### Ako stiahnuť JSON kľúč

1. Nájdi svoj Service Account v zozname
2. Klikni naň
3. Choď do záložky **KEYS**
4. Klikni **ADD KEY** → **Create new key**
5. Vyber **JSON**
6. Klikni **CREATE**
7. Súbor sa automaticky stiahne (napr. `tts-service-account-123456.json`)

### Validácia JSON súboru

Aplikácia automaticky kontroluje či JSON obsahuje všetky povinné polia:
- ✅ `type` (musí byť "service_account")
- ✅ `project_id`
- ✅ `private_key`
- ✅ `client_email`

Ak chýba niektoré pole, aplikácia zobrazí chybu s návodom.

## Licencia

MIT License
