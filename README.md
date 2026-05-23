# Google TTS GUI

Modern graphical interface for Text-to-Speech with support for multiple engines.

## Supported TTS Engines

### 🌐 Google TTS
- Free, basic quality
- 30+ languages including Slovak

### 🔷 Edge TTS (Microsoft)
- Free, Neural voices
- All voices available via API
- Playback speed support

### ✨ Gemini 3.1 TTS (Google Cloud)
- **Premium AI-powered TTS**
- 30+ unique voices (Achernar, Kore, Leda, Charon, ...)
- **Prompts** - style instructions for pronunciation control
- **Markup tags** - [sigh], [laughing], [uhm], [whispering], [sarcasm], [short pause], ...
- Multi-speaker conversations
- Requires Google Cloud API key

## Features

- 🎙️ **Text to Speech** - Convert text to voice
- 🌍 **Language selection** - Support for 30+ languages
- 🎭 **Prompts** (Gemini 3.1) - Style instructions for tone control
- 🗣️ **Voice selection** - All available voices for each engine
- ⚡ **Speed** - Playback speed setting (0.5x - 2.0x)
- 🔊 **Playback** - Direct playback of generated audio
- 💾 **Saving** - Option to save output as MP3 file

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

For Gemini 3.1 TTS you also need:
```bash
pip install google-cloud-texttospeech
```

## Usage

Run the application:
```bash
python main.py
```

### Gemini 3.1 TTS - Prompts

In the prompt field you can enter style instructions:
- `"Say it in a friendly and enthusiastic way"`
- `"Narrate in a calm, professional tone for a documentary"`
- `"Speak like a 1940s radio news announcer"`

### Gemini 3.1 TTS - Markup tags

In the text you can use special tags:
- `[sigh]` - Sigh
- `[laughing]` - Laugh
- `[uhm]` - Hesitation
- `[whispering]` - Whispering
- `[sarcasm]` - Sarcastic tone
- `[short pause]` - Short pause
- `[medium pause]` - Medium pause
- `[long pause]` - Long pause

## Requirements

- Python 3.8+
- Internet connection
- Google Cloud API key (for Gemini 3.1 TTS)

## 🔑 Service Account for Gemini 3.1 TTS

Gemini 3.1 TTS requires **Service Account** authentication (not a simple API key).

### How to create a Service Account

1. Open [Google Cloud Console - Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Click **CREATE SERVICE ACCOUNT**
3. Enter a name (e.g. "tts-service-account")
4. Click **CREATE AND CONTINUE**
5. For role select: **Cloud Text-to-Speech User**
6. Click **CONTINUE** → **DONE**

### How to download JSON key

1. Find your Service Account in the list
2. Click on it
3. Go to the **KEYS** tab
4. Click **ADD KEY** → **Create new key**
5. Select **JSON**
6. Click **CREATE**
7. The file will automatically download (e.g. `tts-service-account-123456.json`)

### JSON File Validation

The application automatically checks if the JSON contains all required fields:
- ✅ `type` (must be "service_account")
- ✅ `project_id`
- ✅ `private_key`
- ✅ `client_email`

If any field is missing, the application will show an error with instructions.

## License

GPL-3.0 license
