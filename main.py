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
        # Appearance settings
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Main window
        self.root = ctk.CTk()
        self.root.title("Google TTS GUI")
        self.root.geometry("800x650")
        self.root.minsize(700, 550)

        # Initialize pygame for audio playback
        pygame.mixer.init()

        # Variables
        self.current_audio_file = None
        self.is_playing = False
        self.tts_engine = "Google TTS"
        self.all_edge_voices = []  # All Edge TTS voices
        self.current_voices = []   # Filtered voices for current language

        # List of TTS engines
        self.tts_engines = ["Google TTS", "Edge TTS (Microsoft)", "Gemini 3.1 TTS"]

        # List of languages
        self.languages = {
            "Slovak": "sk",
            "Czech": "cs",
            "English (US)": "en",
            "English (UK)": "en-uk",
            "German": "de",
            "French": "fr",
            "Spanish": "es",
            "Italian": "it",
            "Polish": "pl",
            "Hungarian": "hu",
            "Russian": "ru",
            "Chinese (Simplified)": "zh-CN",
            "Japanese": "ja",
            "Korean": "ko",
            "Dutch": "nl",
            "Portuguese": "pt",
            "Turkish": "tr",
            "Arabic": "ar",
            "Hindi": "hi",
            "Greek": "el",
            "Romanian": "ro",
            "Bulgarian": "bg",
            "Croatian": "hr",
            "Serbian": "sr",
            "Swedish": "sv",
            "Danish": "da",
            "Norwegian": "no",
            "Finnish": "fi",
            "Estonian": "et",
            "Latvian": "lv",
            "Lithuanian": "lt",
        }

        # Gemini 3.1 TTS voices (global for all languages)
        self.gemini_voices = [
            ("Kore", "Kore (Female) - Recommended"),
            ("Leda", "Leda (Female)"),
            ("Charon", "Charon (Male)"),
            ("Puck", "Puck (Male)"),
            ("Achernar", "Achernar (Female)"),
            ("Achird", "Achird (Male)"),
            ("Algenib", "Algenib (Male)"),
            ("Algieba", "Algieba (Male)"),
            ("Alnilam", "Alnilam (Male)"),
            ("Aoede", "Aoede (Female)"),
            ("Autonoe", "Autonoe (Female)"),
            ("Callirrhoe", "Callirrhoe (Female)"),
            ("Despina", "Despina (Female)"),
            ("Enceladus", "Enceladus (Male)"),
            ("Erinome", "Erinome (Female)"),
            ("Fenrir", "Fenrir (Male)"),
            ("Gacrux", "Gacrux (Female)"),
            ("Iapetus", "Iapetus (Male)"),
            ("Laomedeia", "Laomedeia (Female)"),
            ("Orus", "Orus (Male)"),
            ("Pulcherrima", "Pulcherrima (Female)"),
            ("Rasalgethi", "Rasalgethi (Male)"),
            ("Sadachbia", "Sadachbia (Male)"),
            ("Sadaltager", "Sadaltager (Male)"),
            ("Schedar", "Schedar (Male)"),
            ("Sulafat", "Sulafat (Female)"),
            ("Umbriel", "Umbriel (Male)"),
            ("Vindemiatrix", "Vindemiatrix (Female)"),
            ("Zephyr", "Zephyr (Female)"),
            ("Zubenelgenubi", "Zubenelgenubi (Male)"),
        ]

        # Load Edge TTS voices asynchronously
        self.load_edge_voices()

        self.create_widgets()

    def load_edge_voices(self):
        """Loads all Edge TTS voices in background"""
        def fetch_voices():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                voices = loop.run_until_complete(edge_tts.list_voices())
                self.all_edge_voices = voices
                self.root.after(0, self.update_voice_menu)
            except Exception as e:
                print(f"Error loading Edge TTS voices: {e}")
                # Fallback - basic voices
                self.all_edge_voices = []

        thread = threading.Thread(target=fetch_voices, daemon=True)
        thread.start()

    def get_edge_voices_for_language(self, lang_name):
        """Returns Edge TTS voices for selected language"""
        lang_map = {
            "Slovak": "sk-SK",
            "Czech": "cs-CZ",
            "English (US)": "en-US",
            "English (UK)": "en-GB",
            "German": "de-DE",
            "French": "fr-FR",
            "Spanish": "es-ES",
            "Italian": "it-IT",
            "Polish": "pl-PL",
            "Hungarian": "hu-HU",
            "Russian": "ru-RU",
            "Chinese (Simplified)": "zh-CN",
            "Japanese": "ja-JP",
            "Korean": "ko-KR",
            "Dutch": "nl-NL",
            "Portuguese": "pt-PT",
            "Turkish": "tr-TR",
            "Arabic": "ar-SA",
            "Hindi": "hi-IN",
            "Greek": "el-GR",
            "Romanian": "ro-RO",
            "Bulgarian": "bg-BG",
            "Croatian": "hr-HR",
            "Serbian": "sr-RS",
            "Swedish": "sv-SE",
            "Danish": "da-DK",
            "Norwegian": "nb-NO",
            "Finnish": "fi-FI",
            "Estonian": "et-EE",
            "Latvian": "lv-LV",
            "Lithuanian": "lt-LT",
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
                "Slovak": [("sk-SK-LukasNeural", "Lukas (Male)")],
                "Czech": [("cs-CZ-AntoninNeural", "Antonin (Male)")],
                "English (US)": [
                    ("en-US-GuyNeural", "Guy (Male)"),
                    ("en-US-JennyNeural", "Jenny (Female)"),
                    ("en-US-AriaNeural", "Aria (Female)"),
                    ("en-US-DavisNeural", "Davis (Male)"),
                ],
                "English (UK)": [
                    ("en-GB-RyanNeural", "Ryan (Male)"),
                    ("en-GB-SoniaNeural", "Sonia (Female)"),
                ],
                "German": [
                    ("de-DE-ConradNeural", "Conrad (Male)"),
                    ("de-DE-KatjaNeural", "Katja (Female)"),
                ],
                "French": [
                    ("fr-FR-HenriNeural", "Henri (Male)"),
                    ("fr-FR-DeniseNeural", "Denise (Female)"),
                ],
                "Spanish": [
                    ("es-ES-AlvaroNeural", "Alvaro (Male)"),
                    ("es-ES-ElviraNeural", "Elvira (Female)"),
                ],
                "Italian": [
                    ("it-IT-DiegoNeural", "Diego (Male)"),
                    ("it-IT-ElsaNeural", "Elsa (Female)"),
                ],
                "Polish": [
                    ("pl-PL-MarekNeural", "Marek (Male)"),
                    ("pl-PL-ZofiaNeural", "Zofia (Female)"),
                ],
                "Japanese": [
                    ("ja-JP-KeitaNeural", "Keita (Male)"),
                    ("ja-JP-NanamiNeural", "Nanami (Female)"),
                ],
                "Korean": [
                    ("ko-KR-InJoonNeural", "InJoon (Male)"),
                    ("ko-KR-SunHiNeural", "SunHi (Female)"),
                ],
                "Chinese (Simplified)": [
                    ("zh-CN-YunjianNeural", "Yunjian (Male)"),
                    ("zh-CN-XiaoxiaoNeural", "Xiaoxiao (Female)"),
                ],
                "Russian": [
                    ("ru-RU-DmitryNeural", "Dmitry (Male)"),
                    ("ru-RU-SvetlanaNeural", "Svetlana (Female)"),
                ],
                "Hindi": [
                    ("hi-IN-MadhurNeural", "Madhur (Male)"),
                    ("hi-IN-SwaraNeural", "Swara (Female)"),
                ],
            }
            voices = fallback.get(lang_name, [("en-US-GuyNeural", "Guy (Male)")])

        return voices

    def create_widgets(self):
        # Main frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="🎙️ Text-to-Speech GUI",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # Input frame
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Text label
        text_label = ctk.CTkLabel(
            input_frame,
            text="Enter text to convert:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        text_label.pack(anchor="w", padx=10, pady=(10, 5))

        # Text field
        self.text_input = ctk.CTkTextbox(
            input_frame,
            height=120,
            font=ctk.CTkFont(size=12),
            wrap="word"
        )
        self.text_input.pack(fill="both", expand=True, padx=10, pady=5)
        self.text_input.insert("1.0", "Hello! This is a test text for Text-to-Speech.")

        # Prompt frame (for Gemini 3.1 TTS)
        self.prompt_frame = ctk.CTkFrame(input_frame)
        self.prompt_frame.pack(fill="x", padx=10, pady=(5, 0))
        self.prompt_frame.pack_forget()  # Hidden by default

        prompt_label = ctk.CTkLabel(
            self.prompt_frame,
            text="🎭 Prompt (style instructions for Gemini):",
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
        self.prompt_input.insert("1.0", "Say it in a friendly and enthusiastic way.")

        # Markup tags hint
        markup_hint = ctk.CTkLabel(
            self.prompt_frame,
            text="💡 Markup tags: [sigh], [laughing], [uhm], [sarcasm], [whispering], [short pause], [medium pause], [long pause]",
            font=ctk.CTkFont(size=9),
            text_color="gray"
        )
        markup_hint.pack(anchor="w", pady=(0, 5))

        # Settings frame
        settings_frame = ctk.CTkFrame(main_frame)
        settings_frame.pack(fill="x", padx=10, pady=10)

        # Row 1 - Engine and Language
        row1_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        row1_frame.pack(fill="x", padx=5, pady=5)

        # TTS engine selection
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

        # Language selection
        lang_label = ctk.CTkLabel(
            row1_frame,
            text="Language:",
            font=ctk.CTkFont(size=12)
        )
        lang_label.pack(side="left", padx=(15, 2))

        self.lang_var = ctk.StringVar(value="Slovak")
        self.lang_menu = ctk.CTkOptionMenu(
            row1_frame,
            values=list(self.languages.keys()),
            variable=self.lang_var,
            width=180,
            command=self.on_language_change
        )
        self.lang_menu.pack(side="left", padx=2)

        # Row 2 - Voice selection
        row2_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        row2_frame.pack(fill="x", padx=5, pady=5)

        voice_label = ctk.CTkLabel(
            row2_frame,
            text="Voice:",
            font=ctk.CTkFont(size=12)
        )
        voice_label.pack(side="left", padx=(5, 2))

        self.voice_var = ctk.StringVar()
        self.voice_menu = ctk.CTkOptionMenu(
            row2_frame,
            values=["Default"],
            variable=self.voice_var,
            width=400
        )
        self.voice_menu.pack(side="left", padx=2, fill="x", expand=True)

        # Row 3 - Speed and API key
        row3_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        row3_frame.pack(fill="x", padx=5, pady=5)

        speed_label = ctk.CTkLabel(
            row3_frame,
            text="Speed:",
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

        # API key for Gemini 3.1 - Service Account JSON
        self.api_key_label = ctk.CTkLabel(
            row3_frame,
            text="Service Account:",
            font=ctk.CTkFont(size=12)
        )
        self.api_key_label.pack(side="left", padx=(15, 2))

        self.api_key_entry = ctk.CTkEntry(
            row3_frame,
            width=200,
            placeholder_text="Enter Service Account JSON..."
        )
        self.api_key_entry.pack(side="left", padx=2, fill="x", expand=True)

        # Button to open Google Cloud Console
        self.api_key_button = ctk.CTkButton(
            row3_frame,
            text="� Select JSON",
            command=self.select_service_account_file,
            width=110,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color="#4285f4",
            hover_color="#3367d6"
        )
        self.api_key_button.pack(side="left", padx=(5, 2))

        # Billing button
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

        # Button frame
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        # Play button
        self.play_button = ctk.CTkButton(
            button_frame,
            text="▶ Play",
            command=self.play_text,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.play_button.pack(side="left", padx=(10, 5), pady=10)

        # Stop button
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="⏹ Stop",
            command=self.stop_playback,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#c0392b",
            hover_color="#a93226"
        )
        self.stop_button.pack(side="left", padx=5, pady=10)

        # Save button
        self.save_button = ctk.CTkButton(
            button_frame,
            text="💾 Save MP3",
            command=self.save_audio,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#27ae60",
            hover_color="#219a52"
        )
        self.save_button.pack(side="left", padx=5, pady=10)

        # Clear button
        self.clear_button = ctk.CTkButton(
            button_frame,
            text="🗑 Clear",
            command=self.clear_text,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color="gray",
            hover_color="#555555"
        )
        self.clear_button.pack(side="left", padx=5, pady=10)

        # Account status frame (for Gemini 3.1)
        self.account_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.account_frame.pack(fill="x", padx=10, pady=(0, 5))
        self.account_frame.pack_forget()

        self.account_status_label = ctk.CTkLabel(
            self.account_frame,
            text="💳 Billing: Unverified | Free tier: 1M chars/month | Price: ~$16/1M chars",
            font=ctk.CTkFont(size=10),
            text_color="orange"
        )
        self.account_status_label.pack(side="left", padx=(10, 5))

        self.check_account_button = ctk.CTkButton(
            self.account_frame,
            text="🔄 Check Account",
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
            text="💡 Google TTS: Free | Edge TTS: Free, Neural voices | Gemini 3.1: Premium with prompts and markup tags",
            font=ctk.CTkFont(size=10),
            text_color="gray",
            wraplength=700
        )
        self.info_label.pack(pady=(0, 5))

        # Status bar
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Ready",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.status_label.pack(pady=(5, 5))

        # Progress bar
        self.progress = ctk.CTkProgressBar(main_frame, mode="indeterminate")
        self.progress.pack(fill="x", padx=10, pady=(0, 10))
        self.progress.set(0)

        # Initialize voice menu
        self.update_voice_menu()

    def on_engine_change(self, engine_name):
        """Changes TTS engine"""
        self.tts_engine = engine_name

        # Show/hide API key
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
        self.set_status(f"Selected engine: {engine_name}", "gray")

    def on_language_change(self, lang_name):
        """Changes language - updates voices"""
        self.update_voice_menu()

    def update_voice_menu(self):
        """Updates voice menu based on engine and language"""
        engine = self.engine_var.get()
        lang = self.lang_var.get()

        voices = []

        if engine == "Google TTS":
            # Google TTS has no voice selection - only language
            voices = [("default", "Default Google TTS voice")]
        elif engine == "Edge TTS (Microsoft)":
            voices = self.get_edge_voices_for_language(lang)
        elif engine == "Gemini 3.1 TTS":
            voices = self.gemini_voices

        if not voices:
            voices = [("default", "Default")]

        # Save mapping name -> value
        self.voice_map = {friendly: value for value, friendly in voices}
        voice_names = [friendly for _, friendly in voices]

        self.voice_menu.configure(values=voice_names)
        if voice_names:
            self.voice_var.set(voice_names[0])

    def set_status(self, message, color="gray"):
        self.status_label.configure(text=message, text_color=color)

    async def generate_edge_tts(self, text, voice, save_path=None, speed=1.0):
        """Generates TTS audio using Edge TTS"""
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
        """Generates TTS audio using Gemini 3.1 TTS"""
        try:
            from google.cloud import texttospeech
            from google.oauth2 import service_account

            # Get Service Account JSON file path
            sa_file = self.api_key_entry.get().strip()
            if not sa_file:
                raise ValueError("Select Service Account JSON file!")
            
            if not os.path.exists(sa_file):
                raise ValueError(f"File does not exist: {sa_file}")

            # Validate JSON file
            try:
                with open(sa_file, 'r') as f:
                    sa_data = json.load(f)
            except json.JSONDecodeError:
                raise ValueError("File is not valid JSON!")
            
            required_fields = ['type', 'project_id', 'private_key', 'client_email']
            missing = [field for field in required_fields if field not in sa_data]
            if missing:
                raise ValueError(
                    f"JSON file is missing required fields: {', '.join(missing)}.\n"
                    f"Download the correct Service Account JSON from Google Cloud Console."
                )
            
            if sa_data.get('type') != 'service_account':
                raise ValueError(
                    f"This is not a Service Account JSON (type: {sa_data.get('type', 'unknown')}).\n"
                    f"You need a Service Account JSON with type 'service_account'."
                )

            # Load credentials from Service Account
            credentials = service_account.Credentials.from_service_account_file(
                sa_file,
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            
            client = texttospeech.TextToSpeechClient(credentials=credentials)

            # Get prompt from prompt text field
            prompt = self.prompt_input.get("1.0", "end-1c").strip()

            # Get language code from voice_name or language selection
            lang = self.lang_var.get()
            lang_code_map = {
                "Slovak": "sk-SK",
                "Czech": "cs-CZ",
                "English (US)": "en-US",
                "English (UK)": "en-GB",
                "German": "de-DE",
                "French": "fr-FR",
                "Spanish": "es-ES",
                "Italian": "it-IT",
                "Polish": "pl-PL",
                "Hungarian": "hu-HU",
                "Russian": "ru-RU",
                "Chinese (Simplified)": "cmn-CN",
                "Japanese": "ja-JP",
                "Korean": "ko-KR",
                "Dutch": "nl-NL",
                "Portuguese": "pt-PT",
                "Turkish": "tr-TR",
                "Arabic": "ar-001",
                "Hindi": "hi-IN",
                "Greek": "el-GR",
                "Romanian": "ro-RO",
                "Bulgarian": "bg-BG",
                "Croatian": "hr-HR",
                "Serbian": "sr-RS",
                "Swedish": "sv-SE",
                "Danish": "da-DK",
                "Norwegian": "nb-NO",
                "Finnish": "fi-FI",
                "Estonian": "et-EE",
                "Latvian": "lv-LV",
                "Lithuanian": "lt-LT",
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

            # Try generating with prompt
            if prompt:
                try:
                    synthesis_input = texttospeech.SynthesisInput(text=text, prompt=prompt)
                    response = client.synthesize_speech(
                        input=synthesis_input, voice=voice, audio_config=audio_config
                    )
                except Exception as e:
                    if "prompt" in str(e).lower():
                        # Fallback - generate without prompt
                        self.root.after(0, lambda: self.set_status(
                            "⚠️ Prompt is not supported, generating without prompt...", "orange"
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
            raise ImportError("Install google-cloud-texttospeech: pip install google-cloud-texttospeech")
        except Exception as e:
            error_msg = str(e).lower()
            if "billing" in error_msg:
                self.root.after(0, lambda: self.show_api_error_dialog("billing", str(e)))
                raise ValueError("Billing is not enabled!")
            elif "permission" in error_msg or "api key" in error_msg or "project" in error_msg:
                self.root.after(0, lambda: self.show_api_error_dialog("permission", str(e)))
                raise ValueError("API key does not have permission!")
            elif "voice" in error_msg:
                self.root.after(0, lambda: self.show_api_error_dialog("voice", str(e)))
                raise ValueError(f"Voice is not available!")
            elif "not been used" in error_msg or "enable" in error_msg or "403" in str(e):
                self.root.after(0, lambda: self.show_api_error_dialog("api_not_enabled", str(e)))
                raise ValueError("API is not enabled in the project!")
            else:
                self.root.after(0, lambda: self.show_api_error_dialog("other", str(e)))
                raise ValueError(f"Gemini TTS Error: {str(e)}")
        except Exception as e:
            raise e

    def generate_tts(self, text, voice_code, save_path=None):
        """Generates TTS audio using the selected engine"""
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
        """Returns voice code based on selected engine"""
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
        """Plays text"""
        text = self.text_input.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("Warning", "Enter text to play!")
            return

        # Stop current playback
        self.stop_playback()

        # Start generation and playback in a separate thread
        thread = threading.Thread(target=self._play_thread, args=(text,))
        thread.daemon = True
        thread.start()

    def _play_thread(self, text):
        """Thread for generation and playback"""
        try:
            self.root.after(0, lambda: self.set_status("Generating audio...", "orange"))
            self.root.after(0, lambda: self.progress.start())
            self.root.after(0, lambda: self.play_button.configure(state="disabled"))

            voice_code = self.get_voice_code()

            # Generate audio
            audio_file = self.generate_tts(text, voice_code)
            self.current_audio_file = audio_file

            # Play
            self.root.after(0, lambda: self.set_status("Playing...", "green"))
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            self.is_playing = True

            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                import time
                time.sleep(0.1)

            self.is_playing = False
            self.root.after(0, lambda: self.set_status("Playback completed", "gray"))

            # Delete temporary file
            try:
                os.unlink(audio_file)
                self.current_audio_file = None
            except:
                pass

        except Exception as e:
            error_text = str(e)
            self.root.after(0, lambda: self.set_status(f"Error: {error_text}", "red"))
            
            # If it's a Gemini error, show custom window
            if self.tts_engine == "Gemini 3.1 TTS":
                if "permission" in error_text.lower() or "permission" in error_text.lower():
                    self.root.after(0, lambda: self.show_api_error_dialog("permission", error_text))
                elif "billing" in error_text.lower():
                    self.root.after(0, lambda: self.show_api_error_dialog("billing", error_text))
                elif "enabled" in error_text.lower() or "api is not" in error_text.lower():
                    self.root.after(0, lambda: self.show_api_error_dialog("api_not_enabled", error_text))
                else:
                    messagebox.showerror("Error", f"An error occurred while generating audio: {error_text}")
            else:
                messagebox.showerror("Error", f"An error occurred while generating audio: {error_text}")

        finally:
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.progress.set(0))
            self.root.after(0, lambda: self.play_button.configure(state="normal"))

    def stop_playback(self):
        """Stops playback"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            self.is_playing = False
            self.set_status("Playback stopped", "gray")

        # Delete temporary file if it exists
        if self.current_audio_file and os.path.exists(self.current_audio_file):
            try:
                os.unlink(self.current_audio_file)
                self.current_audio_file = None
            except:
                pass

    def save_audio(self):
        """Saves audio to file"""
        text = self.text_input.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("Warning", "Enter text to save!")
            return

        # Save dialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")],
            title="Save audio as"
        )

        if not file_path:
            return

        # Start saving in a separate thread
        thread = threading.Thread(target=self._save_thread, args=(text, file_path))
        thread.daemon = True
        thread.start()

    def _save_thread(self, text, file_path):
        """Thread for saving"""
        try:
            self.root.after(0, lambda: self.set_status("Saving audio...", "orange"))
            self.root.after(0, lambda: self.progress.start())
            self.root.after(0, lambda: self.save_button.configure(state="disabled"))

            voice_code = self.get_voice_code()

            # Generate and save
            self.generate_tts(text, voice_code, file_path)

            self.root.after(0, lambda: self.set_status(f"Saved: {os.path.basename(file_path)}", "green"))
            messagebox.showinfo("Success", f"Audio was saved to:\n{file_path}")

        except Exception as e:
            self.root.after(0, lambda: self.set_status(f"Error: {str(e)}", "red"))
            messagebox.showerror("Error", f"An error occurred while saving: {str(e)}")

        finally:
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.progress.set(0))
            self.root.after(0, lambda: self.save_button.configure(state="normal"))

    def show_api_error_dialog(self, error_type, error_message=""):
        """Shows error window with clickable links to solution"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("API Key Error")
        dialog.geometry("550x450")
        dialog.transient(self.root)
        dialog.grab_set()

        # Title
        title = ctk.CTkLabel(
            dialog,
            text="❌ API Key Error",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="red"
        )
        title.pack(pady=(20, 10))

        # Error description
        if error_type == "billing":
            desc_text = """Your billing account is not activated or is closed.

Gemini 3.1 TTS requires a valid billing account."""
            links = [
                ("💳 Open Billing Console", "https://console.cloud.google.com/billing"),
                ("📖 Guide - How to enable billing", "https://cloud.google.com/billing/docs/how-to/modify-project"),
            ]
        elif error_type == "permission":
            desc_text = """Service Account does not have permission for Cloud Text-to-Speech API.

Check:
1. If the Service Account is created in the correct project
2. If the Service Account has the 'Cloud TTS User' role
3. If Cloud Text-to-Speech API is enabled"""
            links = [
                ("📋 IAM & Admin (Permissions)", "https://console.cloud.google.com/iam-admin/iam"),
                ("🔑 Service Accounts", "https://console.cloud.google.com/iam-admin/serviceaccounts"),
                ("📚 Enable API", "https://console.cloud.google.com/apis/library/texttospeech.googleapis.com"),
            ]
        elif error_type == "api_not_enabled":
            desc_text = f"""Cloud Text-to-Speech API is not enabled in this project.

Error: {error_message}

You must enable the API in Google Cloud Console."""
            links = [
                ("📚 Enable API (API Library)", "https://console.cloud.google.com/apis/library/texttospeech.googleapis.com"),
                ("📖 Guide - How to enable API", "https://cloud.google.com/text-to-speech/docs/before-you-begin"),
            ]
        elif error_type == "voice":
            desc_text = f"""Voice is not available for the selected language.

{error_message}"""
            links = [
                ("📖 Voice list", "https://cloud.google.com/text-to-speech/docs/voices"),
            ]
        else:
            desc_text = f"""An unexpected error occurred:

{error_message}"""
            links = [
                ("📖 Documentation", "https://cloud.google.com/text-to-speech/docs/gemini-tts"),
            ]

        desc = ctk.CTkLabel(
            dialog,
            text=desc_text,
            font=ctk.CTkFont(size=12),
            wraplength=500,
            justify="left"
        )
        desc.pack(padx=20, pady=10)

        # Links
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

        # Close button
        close_btn = ctk.CTkButton(
            dialog,
            text="Close",
            command=dialog.destroy,
            font=ctk.CTkFont(size=12),
            fg_color="gray",
            hover_color="#555555",
            height=35
        )
        close_btn.pack(pady=(10, 20))

    def select_service_account_file(self):
        """Opens dialog for selecting Service Account JSON file"""
        file_path = filedialog.askopenfilename(
            title="Select Service Account JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            defaultextension=".json"
        )
        if file_path:
            # Validate JSON file
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                required_fields = ['type', 'project_id', 'private_key', 'client_email']
                missing = [field for field in required_fields if field not in data]
                
                if missing:
                    messagebox.showerror(
                        "Invalid Service Account",
                        f"JSON file is missing required fields:\n\n{', '.join(missing)}\n\n"
                        f"This is not a valid Service Account JSON file.\n"
                        f"Download the correct file from Google Cloud Console."
                    )
                    return
                
                if data.get('type') != 'service_account':
                    messagebox.showerror(
                        "Invalid type",
                        f"This is not a Service Account JSON.\n"
                        f"Type: {data.get('type', 'unknown')}\n\n"
                        f"You need a Service Account JSON with type 'service_account'."
                    )
                    return
                
                self.api_key_entry.delete(0, "end")
                self.api_key_entry.insert(0, file_path)
                self.set_status(f"✅ Service Account: {data.get('client_email', 'unknown')}", "green")
                
            except json.JSONDecodeError:
                messagebox.showerror(
                    "Invalid JSON",
                    "File is not valid JSON.\n\n"
                    "Check if you selected the correct Service Account file."
                )
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Error reading file:\n{str(e)}"
                )

    def open_billing_page(self):
        """Opens billing page in Google Cloud"""
        webbrowser.open("https://console.cloud.google.com/billing")
        info_text = """How to enable billing for Gemini 3.1 TTS:

1. Open Google Cloud Console → Billing
2. Create or connect a billing account
3. Add a payment card (Visa, Mastercard, ...)
4. Enable billing for your project

💡 Gemini 3.1 TTS has a free tier:
- 1 million characters per month FREE
- Then ~$16 per 1 million characters

Note: Without a billing account, the API will not work!
        """
        messagebox.showinfo("How to enable billing", info_text)

    def open_api_key_page(self):
        """Opens browser to the page for creating an API key"""
        urls = [
            "https://console.cloud.google.com/apis/credentials",
            "https://console.cloud.google.com/apis/library/texttospeech.googleapis.com",
            "https://aistudio.google.com/app/apikey"
        ]
        
        # Open the main credentials page
        webbrowser.open(urls[0])
        
        # Show information window
        info_text = """How to get an API key for Gemini 3.1 TTS:

1. Create or select a project in Google Cloud Console
2. Enable Cloud Text-to-Speech API
3. Go to "Credentials" and click "CREATE CREDENTIALS"
4. Select "API key"
5. Copy the key and paste it here

Alternatively, you can use:
- Google AI Studio: aistudio.google.com/app/apikey

Note: Gemini 3.1 TTS requires a valid billing account.
        """
        messagebox.showinfo("How to get an API key", info_text)

    def check_account_status(self):
        """Checks billing account status for Gemini 3.1 TTS"""
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            self.account_status_label.configure(
                text="❌ Enter an API key to check account status",
                text_color="red"
            )
            return

        self.account_status_label.configure(
            text="🔄 Checking account status...",
            text_color="orange"
        )
        self.root.update()

        # Start check in a separate thread
        thread = threading.Thread(target=self._check_account_thread, args=(api_key,))
        thread.daemon = True
        thread.start()

    def _check_account_thread(self, api_key):
        """Thread for checking account status"""
        try:
            import requests

            # Try a simple TTS request via REST API
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
                    text="✅ Billing OK | Free tier: 1M chars/month | Price: ~$16/1M chars",
                    text_color="green"
                ))
            elif response.status_code == 403:
                error_data = response.json()
                error_message = error_data.get("error", {}).get("message", "")
                if "billing" in error_message.lower() or "disabled" in error_message.lower():
                    self.root.after(0, lambda: self.account_status_label.configure(
                        text="❌ Billing is not enabled! Click on 💳 Billing for instructions",
                        text_color="red"
                    ))
                else:
                    self.root.after(0, lambda: self.account_status_label.configure(
                        text=f"❌ API key error: {error_message[:50]}",
                        text_color="red"
                    ))
            else:
                error_data = response.json()
                error_message = error_data.get("error", {}).get("message", f"HTTP {response.status_code}")
                self.root.after(0, lambda: self.account_status_label.configure(
                    text=f"⚠️ Error: {error_message[:60]}",
                    text_color="orange"
                ))

        except requests.exceptions.ConnectionError:
            self.root.after(0, lambda: self.account_status_label.configure(
                text="❌ No internet connection",
                text_color="red"
            ))
        except Exception as e:
            self.root.after(0, lambda: self.account_status_label.configure(
                text=f"❌ Error: {str(e)[:60]}",
                text_color="red"
            ))

    def clear_text(self):
        """Clears text field"""
        self.text_input.delete("1.0", "end")
        self.set_status("Text cleared", "gray")

    def run(self):
        """Starts application"""
        self.root.mainloop()

        # Cleanup on exit
        pygame.mixer.quit()
        if self.current_audio_file and os.path.exists(self.current_audio_file):
            try:
                os.unlink(self.current_audio_file)
            except:
                pass


if __name__ == "__main__":
    app = GoogleTTSApp()
    app.run()
