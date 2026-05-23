import customtkinter as ctk
from gtts import gTTS
import edge_tts
import asyncio
import pygame
import os
import tempfile
import threading
import json
import webbrowser
from tkinter import filedialog, messagebox


class GoogleTTSApp:
    def __init__(self):
        # Nastavenie vzhľadu
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Hlavné okno
        self.root = ctk.CTk()
        self.root.title("Google TTS GUI")
        self.root.geometry("800x650")
        self.root.minsize(700, 550)

        # Inicializácia pygame pre prehrávanie zvuku
        pygame.mixer.init()

        # Premenné
        self.current_audio_file = None
        self.is_playing = False
        self.tts_engine = "Google TTS"
        self.all_edge_voices = []  # Všetky Edge TTS hlasy
        self.current_voices = []   # Filtrované hlasy pre aktuálny jazyk

        # Zoznam TTS engine-ov
        self.tts_engines = ["Google TTS", "Edge TTS (Microsoft)", "Gemini 3.1 TTS"]

        # Zoznam jazykov
        self.languages = {
            "Slovenčina": "sk",
            "Čeština": "cs",
            "English (US)": "en",
            "English (UK)": "en-uk",
            "Deutsch": "de",
            "Français": "fr",
            "Español": "es",
            "Italiano": "it",
            "Polski": "pl",
            "Magyar": "hu",
            "Русский": "ru",
            "中文 (简体)": "zh-CN",
            "日本語": "ja",
            "한국어": "ko",
            "Nederlands": "nl",
            "Português": "pt",
            "Türkçe": "tr",
            "العربية": "ar",
            "Hindi": "hi",
            "Ελληνικά": "el",
            "Română": "ro",
            "Български": "bg",
            "Hrvatski": "hr",
            "Srpski": "sr",
            "Svenska": "sv",
            "Dansk": "da",
            "Norsk": "no",
            "Suomi": "fi",
            "Eesti": "et",
            "Latviešu": "lv",
            "Lietuvių": "lt",
        }

        # Gemini 3.1 TTS hlasy (globálne pre všetky jazyky)
        self.gemini_voices = [
            ("Kore", "Kore (Žena) - Odporúčaný"),
            ("Leda", "Leda (Žena)"),
            ("Charon", "Charon (Muž)"),
            ("Puck", "Puck (Muž)"),
            ("Achernar", "Achernar (Žena)"),
            ("Achird", "Achird (Muž)"),
            ("Algenib", "Algenib (Muž)"),
            ("Algieba", "Algieba (Muž)"),
            ("Alnilam", "Alnilam (Muž)"),
            ("Aoede", "Aoede (Žena)"),
            ("Autonoe", "Autonoe (Žena)"),
            ("Callirrhoe", "Callirrhoe (Žena)"),
            ("Despina", "Despina (Žena)"),
            ("Enceladus", "Enceladus (Muž)"),
            ("Erinome", "Erinome (Žena)"),
            ("Fenrir", "Fenrir (Muž)"),
            ("Gacrux", "Gacrux (Žena)"),
            ("Iapetus", "Iapetus (Muž)"),
            ("Laomedeia", "Laomedeia (Žena)"),
            ("Orus", "Orus (Muž)"),
            ("Pulcherrima", "Pulcherrima (Žena)"),
            ("Rasalgethi", "Rasalgethi (Muž)"),
            ("Sadachbia", "Sadachbia (Muž)"),
            ("Sadaltager", "Sadaltager (Muž)"),
            ("Schedar", "Schedar (Muž)"),
            ("Sulafat", "Sulafat (Žena)"),
            ("Umbriel", "Umbriel (Muž)"),
            ("Vindemiatrix", "Vindemiatrix (Žena)"),
            ("Zephyr", "Zephyr (Žena)"),
            ("Zubenelgenubi", "Zubenelgenubi (Muž)"),
        ]

        # Načítaj Edge TTS hlasy asynchrónne
        self.load_edge_voices()

        self.create_widgets()

    def load_edge_voices(self):
        """Načíta všetky Edge TTS hlasy v pozadí"""
        def fetch_voices():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                voices = loop.run_until_complete(edge_tts.list_voices())
                self.all_edge_voices = voices
                self.root.after(0, self.update_voice_menu)
            except Exception as e:
                print(f"Chyba pri načítaní Edge TTS hlasov: {e}")
                # Fallback - základné hlasy
                self.all_edge_voices = []

        thread = threading.Thread(target=fetch_voices, daemon=True)
        thread.start()

    def get_edge_voices_for_language(self, lang_name):
        """Vráti Edge TTS hlasy pre zvolený jazyk"""
        lang_map = {
            "Slovenčina": "sk-SK",
            "Čeština": "cs-CZ",
            "English (US)": "en-US",
            "English (UK)": "en-GB",
            "Deutsch": "de-DE",
            "Français": "fr-FR",
            "Español": "es-ES",
            "Italiano": "it-IT",
            "Polski": "pl-PL",
            "Magyar": "hu-HU",
            "Русский": "ru-RU",
            "中文 (简体)": "zh-CN",
            "日本語": "ja-JP",
            "한국어": "ko-KR",
            "Nederlands": "nl-NL",
            "Português": "pt-PT",
            "Türkçe": "tr-TR",
            "العربية": "ar-SA",
            "Hindi": "hi-IN",
            "Ελληνικά": "el-GR",
            "Română": "ro-RO",
            "Български": "bg-BG",
            "Hrvatski": "hr-HR",
            "Srpski": "sr-RS",
            "Svenska": "sv-SE",
            "Dansk": "da-DK",
            "Norsk": "nb-NO",
            "Suomi": "fi-FI",
            "Eesti": "et-EE",
            "Latviešu": "lv-LV",
            "Lietuvių": "lt-LT",
        }

        prefix = lang_map.get(lang_name, "en-US")
        voices = []

        for voice in self.all_edge_voices:
            if voice["ShortName"].startswith(prefix):
                gender = voice.get("Gender", "Unknown")
                name = voice["ShortName"]
                friendly = voice.get("FriendlyName", name)
                voices.append((name, f"{friendly} ({gender})"))

        if not voices:
            # Fallback
            fallback = {
                "Slovenčina": [("sk-SK-LukasNeural", "Lukas (Muž)")],
                "Čeština": [("cs-CZ-AntoninNeural", "Antonin (Muž)")],
                "English (US)": [
                    ("en-US-GuyNeural", "Guy (Muž)"),
                    ("en-US-JennyNeural", "Jenny (Žena)"),
                    ("en-US-AriaNeural", "Aria (Žena)"),
                    ("en-US-DavisNeural", "Davis (Muž)"),
                ],
                "English (UK)": [
                    ("en-GB-RyanNeural", "Ryan (Muž)"),
                    ("en-GB-SoniaNeural", "Sonia (Žena)"),
                ],
                "Deutsch": [
                    ("de-DE-ConradNeural", "Conrad (Muž)"),
                    ("de-DE-KatjaNeural", "Katja (Žena)"),
                ],
                "Français": [
                    ("fr-FR-HenriNeural", "Henri (Muž)"),
                    ("fr-FR-DeniseNeural", "Denise (Žena)"),
                ],
                "Español": [
                    ("es-ES-AlvaroNeural", "Alvaro (Muž)"),
                    ("es-ES-ElviraNeural", "Elvira (Žena)"),
                ],
                "Italiano": [
                    ("it-IT-DiegoNeural", "Diego (Muž)"),
                    ("it-IT-ElsaNeural", "Elsa (Žena)"),
                ],
                "Polski": [
                    ("pl-PL-MarekNeural", "Marek (Muž)"),
                    ("pl-PL-ZofiaNeural", "Zofia (Žena)"),
                ],
                "日本語": [
                    ("ja-JP-KeitaNeural", "Keita (Muž)"),
                    ("ja-JP-NanamiNeural", "Nanami (Žena)"),
                ],
                "한국어": [
                    ("ko-KR-InJoonNeural", "InJoon (Muž)"),
                    ("ko-KR-SunHiNeural", "SunHi (Žena)"),
                ],
                "中文 (简体)": [
                    ("zh-CN-YunjianNeural", "Yunjian (Muž)"),
                    ("zh-CN-XiaoxiaoNeural", "Xiaoxiao (Žena)"),
                ],
                "Русский": [
                    ("ru-RU-DmitryNeural", "Dmitry (Muž)"),
                    ("ru-RU-SvetlanaNeural", "Svetlana (Žena)"),
                ],
                "Hindi": [
                    ("hi-IN-MadhurNeural", "Madhur (Muž)"),
                    ("hi-IN-SwaraNeural", "Swara (Žena)"),
                ],
            }
            voices = fallback.get(lang_name, [("en-US-GuyNeural", "Guy (Muž)")])

        return voices

    def create_widgets(self):
        # Hlavný frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Nadpis
        title_label = ctk.CTkLabel(
            main_frame,
            text="🎙️ Text-to-Speech GUI",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # Frame pre vstup
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Label pre text
        text_label = ctk.CTkLabel(
            input_frame,
            text="Zadaj text na prevod:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        text_label.pack(anchor="w", padx=10, pady=(10, 5))

        # Textové pole
        self.text_input = ctk.CTkTextbox(
            input_frame,
            height=120,
            font=ctk.CTkFont(size=12),
            wrap="word"
        )
        self.text_input.pack(fill="both", expand=True, padx=10, pady=5)
        self.text_input.insert("1.0", "Ahoj! Toto je testovací text pre Text-to-Speech.")

        # Prompt frame (pre Gemini 3.1 TTS)
        self.prompt_frame = ctk.CTkFrame(input_frame)
        self.prompt_frame.pack(fill="x", padx=10, pady=(5, 0))
        self.prompt_frame.pack_forget()  # Skryté na začiatku

        prompt_label = ctk.CTkLabel(
            self.prompt_frame,
            text="🎭 Prompt (štýlové inštrukcie pre Gemini):",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        prompt_label.pack(anchor="w", pady=(5, 2))

        self.prompt_input = ctk.CTkTextbox(
            self.prompt_frame,
            height=60,
            font=ctk.CTkFont(size=11),
            wrap="word"
        )
        self.prompt_input.pack(fill="x", pady=(0, 5))
        self.prompt_input.insert("1.0", "Povedz to priateľským a nadšeným spôsobom.")

        # Markup tags hint
        markup_hint = ctk.CTkLabel(
            self.prompt_frame,
            text="💡 Markup tags: [sigh], [laughing], [uhm], [sarcasm], [whispering], [short pause], [medium pause], [long pause]",
            font=ctk.CTkFont(size=9),
            text_color="gray"
        )
        markup_hint.pack(anchor="w", pady=(0, 5))

        # Frame pre nastavenia
        settings_frame = ctk.CTkFrame(main_frame)
        settings_frame.pack(fill="x", padx=10, pady=10)

        # Riadok 1 - Engine a Jazyk
        row1_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        row1_frame.pack(fill="x", padx=5, pady=5)

        # Výber TTS engine
        engine_label = ctk.CTkLabel(
            row1_frame,
            text="Engine:",
            font=ctk.CTkFont(size=12)
        )
        engine_label.pack(side="left", padx=(5, 2))

        self.engine_var = ctk.StringVar(value="Google TTS")
        self.engine_menu = ctk.CTkOptionMenu(
            row1_frame,
            values=self.tts_engines,
            variable=self.engine_var,
            width=200,
            command=self.on_engine_change
        )
        self.engine_menu.pack(side="left", padx=2)

        # Výber jazyka
        lang_label = ctk.CTkLabel(
            row1_frame,
            text="Jazyk:",
            font=ctk.CTkFont(size=12)
        )
        lang_label.pack(side="left", padx=(15, 2))

        self.lang_var = ctk.StringVar(value="Slovenčina")
        self.lang_menu = ctk.CTkOptionMenu(
            row1_frame,
            values=list(self.languages.keys()),
            variable=self.lang_var,
            width=180,
            command=self.on_language_change
        )
        self.lang_menu.pack(side="left", padx=2)

        # Riadok 2 - Výber hlasu
        row2_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        row2_frame.pack(fill="x", padx=5, pady=5)

        voice_label = ctk.CTkLabel(
            row2_frame,
            text="Hlas:",
            font=ctk.CTkFont(size=12)
        )
        voice_label.pack(side="left", padx=(5, 2))

        self.voice_var = ctk.StringVar()
        self.voice_menu = ctk.CTkOptionMenu(
            row2_frame,
            values=["Predvolený"],
            variable=self.voice_var,
            width=400
        )
        self.voice_menu.pack(side="left", padx=2, fill="x", expand=True)

        # Riadok 3 - Rýchlosť a API kľúč
        row3_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        row3_frame.pack(fill="x", padx=5, pady=5)

        speed_label = ctk.CTkLabel(
            row3_frame,
            text="Rýchlosť:",
            font=ctk.CTkFont(size=12)
        )
        speed_label.pack(side="left", padx=(5, 2))

        self.speed_var = ctk.StringVar(value="1.0")
        self.speed_menu = ctk.CTkOptionMenu(
            row3_frame,
            values=["0.5", "0.75", "1.0", "1.25", "1.5", "2.0"],
            variable=self.speed_var,
            width=80
        )
        self.speed_menu.pack(side="left", padx=2)

        # API kľúč pre Gemini 3.1 - Service Account JSON
        self.api_key_label = ctk.CTkLabel(
            row3_frame,
            text="Service Account:",
            font=ctk.CTkFont(size=12)
        )
        self.api_key_label.pack(side="left", padx=(15, 2))

        self.api_key_entry = ctk.CTkEntry(
            row3_frame,
            width=200,
            placeholder_text="Vlož Service Account JSON..."
        )
        self.api_key_entry.pack(side="left", padx=2, fill="x", expand=True)

        # Tlačidlo pre otvorenie Google Cloud Console
        self.api_key_button = ctk.CTkButton(
            row3_frame,
            text="� Vybrať JSON",
            command=self.select_service_account_file,
            width=110,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color="#4285f4",
            hover_color="#3367d6"
        )
        self.api_key_button.pack(side="left", padx=(5, 2))

        # Tlačidlo pre billing
        self.billing_button = ctk.CTkButton(
            row3_frame,
            text="💳 Billing",
            command=self.open_billing_page,
            width=90,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color="#ea4335",
            hover_color="#c5221f"
        )
        self.billing_button.pack(side="left", padx=(2, 2))

        self.api_key_label.pack_forget()
        self.api_key_entry.pack_forget()
        self.api_key_button.pack_forget()

        # Frame pre tlačidlá
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        # Tlačidlo pre prehrávanie
        self.play_button = ctk.CTkButton(
            button_frame,
            text="▶ Prehrať",
            command=self.play_text,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.play_button.pack(side="left", padx=(10, 5), pady=10)

        # Tlačidlo pre zastavenie
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="⏹ Zastaviť",
            command=self.stop_playback,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#c0392b",
            hover_color="#a93226"
        )
        self.stop_button.pack(side="left", padx=5, pady=10)

        # Tlačidlo pre uloženie
        self.save_button = ctk.CTkButton(
            button_frame,
            text="💾 Uložiť MP3",
            command=self.save_audio,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#27ae60",
            hover_color="#219a52"
        )
        self.save_button.pack(side="left", padx=5, pady=10)

        # Tlačidlo pre vymazanie
        self.clear_button = ctk.CTkButton(
            button_frame,
            text="🗑 Vymazať",
            command=self.clear_text,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color="gray",
            hover_color="#555555"
        )
        self.clear_button.pack(side="left", padx=5, pady=10)

        # Account status frame (pre Gemini 3.1)
        self.account_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.account_frame.pack(fill="x", padx=10, pady=(0, 5))
        self.account_frame.pack_forget()

        self.account_status_label = ctk.CTkLabel(
            self.account_frame,
            text="💳 Billing: Neoverené | Free tier: 1M znakov/mesiac | Cena: ~$16/1M znakov",
            font=ctk.CTkFont(size=10),
            text_color="orange"
        )
        self.account_status_label.pack(side="left", padx=(10, 5))

        self.check_account_button = ctk.CTkButton(
            self.account_frame,
            text="🔄 Skontrolovať účet",
            command=self.check_account_status,
            width=140,
            height=25,
            font=ctk.CTkFont(size=10),
            fg_color="#fbbc04",
            hover_color="#f9a825",
            text_color="black"
        )
        self.check_account_button.pack(side="left", padx=5)

        # Info label
        self.info_label = ctk.CTkLabel(
            main_frame,
            text="💡 Google TTS: Bezplatný | Edge TTS: Bezplatný, Neural hlasy | Gemini 3.1: Premium s promptami a markup tags",
            font=ctk.CTkFont(size=10),
            text_color="gray",
            wraplength=700
        )
        self.info_label.pack(pady=(0, 5))

        # Status bar
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Pripravený",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.status_label.pack(pady=(5, 5))

        # Progress bar
        self.progress = ctk.CTkProgressBar(main_frame, mode="indeterminate")
        self.progress.pack(fill="x", padx=10, pady=(0, 10))
        self.progress.set(0)

        # Inicializuj menu hlasov
        self.update_voice_menu()

    def on_engine_change(self, engine_name):
        """Zmení TTS engine"""
        self.tts_engine = engine_name

        # Zobraz/skry API kľúč
        if engine_name == "Gemini 3.1 TTS":
            self.api_key_label.pack(side="left", padx=(15, 2))
            self.api_key_entry.pack(side="left", padx=2, fill="x", expand=True)
            self.api_key_button.pack(side="left", padx=(5, 2))
            self.billing_button.pack(side="left", padx=(2, 2))
            self.prompt_frame.pack(fill="x", padx=10, pady=(5, 0))
            self.account_frame.pack(fill="x", padx=10, pady=(0, 5))
        else:
            self.api_key_label.pack_forget()
            self.api_key_entry.pack_forget()
            self.api_key_button.pack_forget()
            self.billing_button.pack_forget()
            self.prompt_frame.pack_forget()
            self.account_frame.pack_forget()

        self.update_voice_menu()
        self.set_status(f"Vybraný engine: {engine_name}", "gray")

    def on_language_change(self, lang_name):
        """Zmení jazyk - aktualizuje hlasy"""
        self.update_voice_menu()

    def update_voice_menu(self):
        """Aktualizuje menu hlasov podľa engine a jazyka"""
        engine = self.engine_var.get()
        lang = self.lang_var.get()

        voices = []

        if engine == "Google TTS":
            # Google TTS nemá výber hlasu - len jazyk
            voices = [("default", "Predvolený Google TTS hlas")]
        elif engine == "Edge TTS (Microsoft)":
            voices = self.get_edge_voices_for_language(lang)
        elif engine == "Gemini 3.1 TTS":
            voices = self.gemini_voices

        if not voices:
            voices = [("default", "Predvolený")]

        # Ulož mapovanie názov -> hodnota
        self.voice_map = {friendly: value for value, friendly in voices}
        voice_names = [friendly for _, friendly in voices]

        self.voice_menu.configure(values=voice_names)
        if voice_names:
            self.voice_var.set(voice_names[0])

    def set_status(self, message, color="gray"):
        self.status_label.configure(text=message, text_color=color)

    async def generate_edge_tts(self, text, voice, save_path=None, speed=1.0):
        """Generuje TTS audio pomocou Edge TTS"""
        rate = f"{int((speed - 1.0) * 100)}%"
        if speed < 1.0:
            rate = f"-{abs(int((speed - 1.0) * 100))}%"
        else:
            rate = f"+{int((speed - 1.0) * 100)}%"

        communicate = edge_tts.Communicate(text, voice, rate=rate)
        if save_path:
            await communicate.save(save_path)
            return save_path
        else:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_file.close()
            await communicate.save(temp_file.name)
            return temp_file.name

    def generate_gemini_tts(self, text, voice_name, save_path=None, speed=1.0):
        """Generuje TTS audio pomocou Gemini 3.1 TTS"""
        try:
            from google.cloud import texttospeech
            from google.oauth2 import service_account

            # Získaj cestu k Service Account JSON súboru
            sa_file = self.api_key_entry.get().strip()
            if not sa_file:
                raise ValueError("Vyber Service Account JSON súbor!")
            
            if not os.path.exists(sa_file):
                raise ValueError(f"Súbor neexistuje: {sa_file}")

            # Validuj JSON súbor
            try:
                with open(sa_file, 'r') as f:
                    sa_data = json.load(f)
            except json.JSONDecodeError:
                raise ValueError("Súbor nie je platný JSON!")
            
            required_fields = ['type', 'project_id', 'private_key', 'client_email']
            missing = [field for field in required_fields if field not in sa_data]
            if missing:
                raise ValueError(
                    f"JSON súbor chýba povinné polia: {', '.join(missing)}.\n"
                    f"Stiahni správny Service Account JSON z Google Cloud Console."
                )
            
            if sa_data.get('type') != 'service_account':
                raise ValueError(
                    f"Toto nie je Service Account JSON (typ: {sa_data.get('type', 'neznámy')}).\n"
                    f"Potrebuješ Service Account JSON s typom 'service_account'."
                )

            # Načítaj credentials zo Service Account
            credentials = service_account.Credentials.from_service_account_file(
                sa_file,
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            
            client = texttospeech.TextToSpeechClient(credentials=credentials)

            # Získaj prompt z prompt textového poľa
            prompt = self.prompt_input.get("1.0", "end-1c").strip()

            # Získaj language code z voice_name alebo z výberu jazyka
            lang = self.lang_var.get()
            lang_code_map = {
                "Slovenčina": "sk-SK",
                "Čeština": "cs-CZ",
                "English (US)": "en-US",
                "English (UK)": "en-GB",
                "Deutsch": "de-DE",
                "Français": "fr-FR",
                "Español": "es-ES",
                "Italiano": "it-IT",
                "Polski": "pl-PL",
                "Magyar": "hu-HU",
                "Русский": "ru-RU",
                "中文 (简体)": "cmn-CN",
                "日本語": "ja-JP",
                "한국어": "ko-KR",
                "Nederlands": "nl-NL",
                "Português": "pt-PT",
                "Türkçe": "tr-TR",
                "العربية": "ar-001",
                "Hindi": "hi-IN",
                "Ελληνικά": "el-GR",
                "Română": "ro-RO",
                "Български": "bg-BG",
                "Hrvatski": "hr-HR",
                "Srpski": "sr-RS",
                "Svenska": "sv-SE",
                "Dansk": "da-DK",
                "Norsk": "nb-NO",
                "Suomi": "fi-FI",
                "Eesti": "et-EE",
                "Latviešu": "lv-LV",
                "Lietuvių": "lt-LT",
            }
            language_code = lang_code_map.get(lang, "en-US")

            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=voice_name,
                model_name="gemini-3.1-flash-tts-preview"
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=speed
            )

            # Skús generovať s promptom
            if prompt:
                try:
                    synthesis_input = texttospeech.SynthesisInput(text=text, prompt=prompt)
                    response = client.synthesize_speech(
                        input=synthesis_input, voice=voice, audio_config=audio_config
                    )
                except Exception as e:
                    if "prompt" in str(e).lower():
                        # Fallback - generuj bez promptu
                        self.root.after(0, lambda: self.set_status(
                            "⚠️ Prompt nie je podporovaný, generujem bez promptu...", "orange"
                        ))
                        synthesis_input = texttospeech.SynthesisInput(text=text)
                        response = client.synthesize_speech(
                            input=synthesis_input, voice=voice, audio_config=audio_config
                        )
                    else:
                        raise
            else:
                synthesis_input = texttospeech.SynthesisInput(text=text)
                response = client.synthesize_speech(
                    input=synthesis_input, voice=voice, audio_config=audio_config
                )

            if save_path:
                with open(save_path, "wb") as out:
                    out.write(response.audio_content)
                return save_path
            else:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                temp_file.write(response.audio_content)
                temp_file.close()
                return temp_file.name

        except ImportError:
            raise ImportError("Nainštaluj google-cloud-texttospeech: pip install google-cloud-texttospeech")
        except Exception as e:
            error_msg = str(e).lower()
            if "billing" in error_msg:
                self.root.after(0, lambda: self.show_api_error_dialog("billing", str(e)))
                raise ValueError("Billing nie je zapnutý!")
            elif "permission" in error_msg or "api key" in error_msg or "project" in error_msg:
                self.root.after(0, lambda: self.show_api_error_dialog("permission", str(e)))
                raise ValueError("API kľúč nemá oprávnenie!")
            elif "voice" in error_msg:
                self.root.after(0, lambda: self.show_api_error_dialog("voice", str(e)))
                raise ValueError(f"Hlas nie je dostupný!")
            elif "not been used" in error_msg or "enable" in error_msg or "403" in str(e):
                self.root.after(0, lambda: self.show_api_error_dialog("api_not_enabled", str(e)))
                raise ValueError("API nie je povolené v projekte!")
            else:
                self.root.after(0, lambda: self.show_api_error_dialog("other", str(e)))
                raise ValueError(f"Chyba Gemini TTS: {str(e)}")
        except Exception as e:
            raise e

    def generate_tts(self, text, voice_code, save_path=None):
        """Generuje TTS audio pomocou zvoleného engine"""
        try:
            speed = float(self.speed_var.get())

            if self.tts_engine == "Edge TTS (Microsoft)":
                voice = voice_code
                if save_path:
                    asyncio.run(self.generate_edge_tts(text, voice, save_path, speed))
                    return save_path
                else:
                    return asyncio.run(self.generate_edge_tts(text, voice, speed=speed))
            elif self.tts_engine == "Gemini 3.1 TTS":
                return self.generate_gemini_tts(text, voice_code, save_path, speed)
            else:
                # Google TTS
                lang_code = voice_code
                tts = gTTS(text=text, lang=lang_code, slow=False)
                if save_path:
                    tts.save(save_path)
                    return save_path
                else:
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                    tts.save(temp_file.name)
                    temp_file.close()
                    return temp_file.name
        except Exception as e:
            raise e

    def get_voice_code(self):
        """Vráti kód hlasu podľa zvoleného engine"""
        engine = self.engine_var.get()
        lang = self.lang_var.get()
        voice_friendly = self.voice_var.get()

        if engine == "Google TTS":
            return self.languages.get(lang, "en")
        elif engine == "Edge TTS (Microsoft)":
            return self.voice_map.get(voice_friendly, "en-US-GuyNeural")
        elif engine == "Gemini 3.1 TTS":
            return self.voice_map.get(voice_friendly, "Kore")
        return "en"

    def play_text(self):
        """Prehrá text"""
        text = self.text_input.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("Upozornenie", "Zadaj text na prehratie!")
            return

        # Zastav aktuálne prehrávanie
        self.stop_playback()

        # Spusti generovanie a prehrávanie v samostatnom vlákne
        thread = threading.Thread(target=self._play_thread, args=(text,))
        thread.daemon = True
        thread.start()

    def _play_thread(self, text):
        """Vlákno pre generovanie a prehrávanie"""
        try:
            self.root.after(0, lambda: self.set_status("Generujem audio...", "orange"))
            self.root.after(0, lambda: self.progress.start())
            self.root.after(0, lambda: self.play_button.configure(state="disabled"))

            voice_code = self.get_voice_code()

            # Generuj audio
            audio_file = self.generate_tts(text, voice_code)
            self.current_audio_file = audio_file

            # Prehraj
            self.root.after(0, lambda: self.set_status("Prehrávam...", "green"))
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            self.is_playing = True

            # Čakaj na dokončenie prehrávania
            while pygame.mixer.music.get_busy():
                import time
                time.sleep(0.1)

            self.is_playing = False
            self.root.after(0, lambda: self.set_status("Prehrávanie dokončené", "gray"))

            # Vymaž dočasný súbor
            try:
                os.unlink(audio_file)
                self.current_audio_file = None
            except:
                pass

        except Exception as e:
            error_text = str(e)
            self.root.after(0, lambda: self.set_status(f"Chyba: {error_text}", "red"))
            
            # Ak je to Gemini chyba, zobraz custom okno
            if self.tts_engine == "Gemini 3.1 TTS":
                if "oprávnenie" in error_text.lower() or "permission" in error_text.lower():
                    self.root.after(0, lambda: self.show_api_error_dialog("permission", error_text))
                elif "billing" in error_text.lower():
                    self.root.after(0, lambda: self.show_api_error_dialog("billing", error_text))
                elif "povolené" in error_text.lower() or "api nie je" in error_text.lower():
                    self.root.after(0, lambda: self.show_api_error_dialog("api_not_enabled", error_text))
                else:
                    messagebox.showerror("Chyba", f"Nastala chyba pri generovaní audio: {error_text}")
            else:
                messagebox.showerror("Chyba", f"Nastala chyba pri generovaní audio: {error_text}")

        finally:
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.progress.set(0))
            self.root.after(0, lambda: self.play_button.configure(state="normal"))

    def stop_playback(self):
        """Zastaví prehrávanie"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            self.is_playing = False
            self.set_status("Prehrávanie zastavené", "gray")

        # Vymaž dočasný súbor ak existuje
        if self.current_audio_file and os.path.exists(self.current_audio_file):
            try:
                os.unlink(self.current_audio_file)
                self.current_audio_file = None
            except:
                pass

    def save_audio(self):
        """Uloží audio do súboru"""
        text = self.text_input.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("Upozornenie", "Zadaj text na uloženie!")
            return

        # Dialóg pre uloženie
        file_path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 súbory", "*.mp3"), ("Všetky súbory", "*.*")],
            title="Uložiť audio ako"
        )

        if not file_path:
            return

        # Spusti ukladanie v samostatnom vlákne
        thread = threading.Thread(target=self._save_thread, args=(text, file_path))
        thread.daemon = True
        thread.start()

    def _save_thread(self, text, file_path):
        """Vlákno pre ukladanie"""
        try:
            self.root.after(0, lambda: self.set_status("Ukladám audio...", "orange"))
            self.root.after(0, lambda: self.progress.start())
            self.root.after(0, lambda: self.save_button.configure(state="disabled"))

            voice_code = self.get_voice_code()

            # Generuj a ulož
            self.generate_tts(text, voice_code, file_path)

            self.root.after(0, lambda: self.set_status(f"Uložené: {os.path.basename(file_path)}", "green"))
            messagebox.showinfo("Úspech", f"Audio bolo uložené do:\n{file_path}")

        except Exception as e:
            self.root.after(0, lambda: self.set_status(f"Chyba: {str(e)}", "red"))
            messagebox.showerror("Chyba", f"Nastala chyba pri ukladaní: {str(e)}")

        finally:
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.progress.set(0))
            self.root.after(0, lambda: self.save_button.configure(state="normal"))

    def show_api_error_dialog(self, error_type, error_message=""):
        """Zobrazí okno s chybou a klikateľnými odkazmi na riešenie"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Chyba API kľúča")
        dialog.geometry("550x450")
        dialog.transient(self.root)
        dialog.grab_set()

        # Nadpis
        title = ctk.CTkLabel(
            dialog,
            text="❌ Chyba API kľúča",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="red"
        )
        title.pack(pady=(20, 10))

        # Popis chyby
        if error_type == "billing":
            desc_text = """Tvoj billing účet nie je aktivovaný alebo je uzavretý.

Gemini 3.1 TTS vyžaduje platný billing účet."""
            links = [
                ("💳 Otvoriť Billing Console", "https://console.cloud.google.com/billing"),
                ("📖 Návod - Ako zapnúť billing", "https://cloud.google.com/billing/docs/how-to/modify-project"),
            ]
        elif error_type == "permission":
            desc_text = """Service Account nemá oprávnenie pre Cloud Text-to-Speech API.

Skontroluj:
1. Či je Service Account vytvorený v správnom projekte
2. Či má Service Account rolu 'Cloud TTS User'
3. Či je povolené Cloud Text-to-Speech API"""
            links = [
                ("📋 IAM & Admin (Oprávnenia)", "https://console.cloud.google.com/iam-admin/iam"),
                ("🔑 Service Accounts", "https://console.cloud.google.com/iam-admin/serviceaccounts"),
                ("📚 Povoliť API", "https://console.cloud.google.com/apis/library/texttospeech.googleapis.com"),
            ]
        elif error_type == "api_not_enabled":
            desc_text = f"""Cloud Text-to-Speech API nie je povolené v tomto projekte.

Chyba: {error_message}

Musíš povoliť API v Google Cloud Console."""
            links = [
                ("📚 Povoliť API (API Library)", "https://console.cloud.google.com/apis/library/texttospeech.googleapis.com"),
                ("📖 Návod - Ako povoliť API", "https://cloud.google.com/text-to-speech/docs/before-you-begin"),
            ]
        elif error_type == "voice":
            desc_text = f"""Hlas nie je dostupný pre zvolený jazyk.

{error_message}"""
            links = [
                ("📖 Zoznam hlasov", "https://cloud.google.com/text-to-speech/docs/voices"),
            ]
        else:
            desc_text = f"""Nastala neočakávaná chyba:

{error_message}"""
            links = [
                ("📖 Dokumentácia", "https://cloud.google.com/text-to-speech/docs/gemini-tts"),
            ]

        desc = ctk.CTkLabel(
            dialog,
            text=desc_text,
            font=ctk.CTkFont(size=12),
            wraplength=500,
            justify="left"
        )
        desc.pack(padx=20, pady=10)

        # Odkazy
        links_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        links_frame.pack(padx=20, pady=10, fill="x")

        for label, url in links:
            btn = ctk.CTkButton(
                links_frame,
                text=label,
                command=lambda u=url: webbrowser.open(u),
                font=ctk.CTkFont(size=12),
                fg_color="#4285f4",
                hover_color="#3367d6",
                height=35
            )
            btn.pack(pady=5, fill="x")

        # Zatvoriť tlačidlo
        close_btn = ctk.CTkButton(
            dialog,
            text="Zatvoriť",
            command=dialog.destroy,
            font=ctk.CTkFont(size=12),
            fg_color="gray",
            hover_color="#555555",
            height=35
        )
        close_btn.pack(pady=(10, 20))

    def select_service_account_file(self):
        """Otvorí dialóg pre výber Service Account JSON súboru"""
        file_path = filedialog.askopenfilename(
            title="Vyber Service Account JSON súbor",
            filetypes=[("JSON súbory", "*.json"), ("Všetky súbory", "*.*")],
            defaultextension=".json"
        )
        if file_path:
            # Validuj JSON súbor
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                required_fields = ['type', 'project_id', 'private_key', 'client_email']
                missing = [field for field in required_fields if field not in data]
                
                if missing:
                    messagebox.showerror(
                        "Neplatný Service Account",
                        f"JSON súbor chýba povinné polia:\n\n{', '.join(missing)}\n\n"
                        f"Toto nie je platný Service Account JSON súbor.\n"
                        f"Stiahni správny súbor z Google Cloud Console."
                    )
                    return
                
                if data.get('type') != 'service_account':
                    messagebox.showerror(
                        "Neplatný typ",
                        f"Toto nie je Service Account JSON.\n"
                        f"Typ: {data.get('type', 'neznámy')}\n\n"
                        f"Potrebuješ Service Account JSON s typom 'service_account'."
                    )
                    return
                
                self.api_key_entry.delete(0, "end")
                self.api_key_entry.insert(0, file_path)
                self.set_status(f"✅ Service Account: {data.get('client_email', 'neznámy')}", "green")
                
            except json.JSONDecodeError:
                messagebox.showerror(
                    "Neplatný JSON",
                    "Súbor nie je platný JSON.\n\n"
                    "Skontroluj či si vybral správny Service Account súbor."
                )
            except Exception as e:
                messagebox.showerror(
                    "Chyba",
                    f"Chyba pri čítaní súboru:\n{str(e)}"
                )

    def open_billing_page(self):
        """Otvorí stránku pre billing v Google Cloud"""
        webbrowser.open("https://console.cloud.google.com/billing")
        info_text = """Ako zapnúť billing pre Gemini 3.1 TTS:

1. Otvor Google Cloud Console → Billing
2. Vytvor alebo pripoj billing účet
3. Pridaj platobnú kartu (Visa, Mastercard, ...)
4. Povol billing pre tvoj projekt

💡 Gemini 3.1 TTS má free tier:
- 1 milión znakov mesačne ZDARMA
- Potom ~$16 za 1 milión znakov

Poznámka: Bez billing účtu API nebude fungovať!
        """
        messagebox.showinfo("Ako zapnúť billing", info_text)

    def open_api_key_page(self):
        """Otvorí prehliadač na stránku pre vytvorenie API kľúča"""
        urls = [
            "https://console.cloud.google.com/apis/credentials",
            "https://console.cloud.google.com/apis/library/texttospeech.googleapis.com",
            "https://aistudio.google.com/app/apikey"
        ]
        
        # Otvoríme hlavnú stránku credentials
        webbrowser.open(urls[0])
        
        # Zobrazíme informačné okno
        info_text = """Ako získať API kľúč pre Gemini 3.1 TTS:

1. Vytvor alebo vyber projekt v Google Cloud Console
2. Povol Cloud Text-to-Speech API
3. Choď do "Credentials" a klikni "CREATE CREDENTIALS"
4. Vyber "API key"
5. Skopíruj kľúč a vlož ho sem

Alternatívne môžeš použiť:
- Google AI Studio: aistudio.google.com/app/apikey

Poznámka: Gemini 3.1 TTS vyžaduje platný billing účet.
        """
        messagebox.showinfo("Ako získať API kľúč", info_text)

    def check_account_status(self):
        """Skontroluje stav billing účtu pre Gemini 3.1 TTS"""
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            self.account_status_label.configure(
                text="❌ Zadaj API kľúč pre kontrolu účtu",
                text_color="red"
            )
            return

        self.account_status_label.configure(
            text="🔄 Kontrolujem stav účtu...",
            text_color="orange"
        )
        self.root.update()

        # Spusti kontrolu v samostatnom vlákne
        thread = threading.Thread(target=self._check_account_thread, args=(api_key,))
        thread.daemon = True
        thread.start()

    def _check_account_thread(self, api_key):
        """Vlákno pre kontrolu stavu účtu"""
        try:
            import requests

            # Skúsime jednoduchý TTS request cez REST API
            url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}"
            headers = {"Content-Type": "application/json"}
            data = {
                "input": {"text": "Test"},
                "voice": {
                    "languageCode": "en-US",
                    "name": "Kore",
                    "modelName": "gemini-3.1-flash-tts-preview"
                },
                "audioConfig": {"audioEncoding": "MP3"}
            }

            response = requests.post(url, headers=headers, json=data, timeout=10)

            if response.status_code == 200:
                self.root.after(0, lambda: self.account_status_label.configure(
                    text="✅ Billing OK | Free tier: 1M znakov/mesiac | Cena: ~$16/1M znakov",
                    text_color="green"
                ))
            elif response.status_code == 403:
                error_data = response.json()
                error_message = error_data.get("error", {}).get("message", "")
                if "billing" in error_message.lower() or "disabled" in error_message.lower():
                    self.root.after(0, lambda: self.account_status_label.configure(
                        text="❌ Billing nie je zapnutý! Klikni na 💳 Billing pre návod",
                        text_color="red"
                    ))
                else:
                    self.root.after(0, lambda: self.account_status_label.configure(
                        text=f"❌ Chyba API kľúča: {error_message[:50]}",
                        text_color="red"
                    ))
            else:
                error_data = response.json()
                error_message = error_data.get("error", {}).get("message", f"HTTP {response.status_code}")
                self.root.after(0, lambda: self.account_status_label.configure(
                    text=f"⚠️ Chyba: {error_message[:60]}",
                    text_color="orange"
                ))

        except requests.exceptions.ConnectionError:
            self.root.after(0, lambda: self.account_status_label.configure(
                text="❌ Žiadne pripojenie k internetu",
                text_color="red"
            ))
        except Exception as e:
            self.root.after(0, lambda: self.account_status_label.configure(
                text=f"❌ Chyba: {str(e)[:60]}",
                text_color="red"
            ))

    def clear_text(self):
        """Vymaže textové pole"""
        self.text_input.delete("1.0", "end")
        self.set_status("Text vymazaný", "gray")

    def run(self):
        """Spustí aplikáciu"""
        self.root.mainloop()

        # Cleanup pri ukončení
        pygame.mixer.quit()
        if self.current_audio_file and os.path.exists(self.current_audio_file):
            try:
                os.unlink(self.current_audio_file)
            except:
                pass


if __name__ == "__main__":
    app = GoogleTTSApp()
    app.run()
