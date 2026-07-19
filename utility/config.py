import os
from dotenv import load_dotenv
from typing import Optional, Literal, List
from openai import OpenAI

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class ConfigurationError(Exception):
    pass


class Config:
    _instance: Optional['Config'] = None

    def __new__(cls) -> 'Config':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        load_dotenv()
        self._validate_env_file()
        self._validate_configuration()
        self._llm_client = None
        self._initialized = True

    def _validate_env_file(self) -> None:
        env_path = os.path.join(os.getcwd(), '.env')
        if not os.path.exists(env_path):
            raise ConfigurationError(
                ".env file not found. Please create a .env file based on .env.example\n"
                f"Expected location: {env_path}"
            )

    def _validate_configuration(self) -> None:
        errors = []
        llm_provider = os.getenv('LLM_PROVIDER', 'auto').lower()

        if llm_provider not in ['auto', 'openrouter', 'openai', 'groq', 'gemini']:
            errors.append(
                f"Invalid LLM_PROVIDER: '{llm_provider}'. Must be one of: auto, openrouter, openai, groq, gemini"
            )

        has_any_key = bool(
            os.getenv('OPENROUTER_API_KEY') or
            os.getenv('OPENAI_API_KEY') or
            os.getenv('GROQ_API_KEY') or
            os.getenv('GEMINI_API_KEY')
        )
        if not has_any_key:
            errors.append(
                "At least one LLM API key (OPENROUTER, OPENAI, GROQ, or GEMINI) must be provided."
            )

        if not os.getenv('PEXELS_API_KEY') and not os.getenv('MUAPI_API_KEY'):
            errors.append(
                "Missing required API key: PEXELS_API_KEY or MUAPI_API_KEY must be provided"
            )

        stt_provider = os.getenv('STT_PROVIDER', 'whisper').lower()
        if stt_provider not in ['whisper', 'deepgram']:
            errors.append(
                f"Invalid STT_PROVIDER: '{stt_provider}'. Must be one of: whisper, deepgram"
            )
        elif stt_provider == 'deepgram':
            if not os.getenv('DEEPGRAM_API_KEY'):
                errors.append(
                    "Missing required API key: DEEPGRAM_API_KEY (required for STT_PROVIDER=deepgram)"
                )

        tts_provider = os.getenv('TTS_PROVIDER', 'edgetts').lower()
        if tts_provider not in ['edgetts', 'elevenlabs']:
            errors.append(
                f"Invalid TTS_PROVIDER: '{tts_provider}'. Must be one of: edgetts, elevenlabs"
            )
        elif tts_provider == 'edgetts':
            if not os.getenv('EDGETTS_VOICE'):
                errors.append(
                    "Missing required configuration: EDGETTS_VOICE (required for TTS_PROVIDER=edgetts)"
                )
        elif tts_provider == 'elevenlabs':
            if not os.getenv('ELEVENLABS_API_KEY'):
                errors.append(
                    "Missing required API key: ELEVENLABS_API_KEY (required for TTS_PROVIDER=elevenlabs)"
                )
            if not os.getenv('ELEVENLABS_VOICE_ID'):
                errors.append(
                    "Missing required configuration: ELEVENLABS_VOICE_ID (required for TTS_PROVIDER=elevenlabs)"
                )

        if errors:
            error_message = "Configuration validation failed:\n\n"
            for error in errors:
                error_message += f"  - {error}\n"
            error_message += "\nPlease check your .env file and ensure all required keys are set."
            raise ConfigurationError(error_message)

    def get_llm_provider(self) -> str:
        return os.getenv('LLM_PROVIDER', 'auto').lower()

    def get_llm_models(self, provider: str = None) -> List[str]:
        """Return list of models for each provider in priority order for fallback"""
        if provider is None:
            provider = self.get_llm_provider()
            if provider == 'auto':
                provider = 'openrouter'

        if provider == 'openrouter':
            return [
                os.getenv('OPENROUTER_MODEL', 'openai/gpt-4o'),
                'meta-llama/llama-3.3-70b-instruct',
                'mistralai/mistral-large',
                'qwen/qwen-2.5-72b-instruct',
                'deepseek/deepseek-chat',
                'openai/gpt-4o-mini'
            ]
        elif provider == 'openai':
            return [
                os.getenv('OPENAI_MODEL', 'gpt-4o'),
                'gpt-4o-mini',
                'gpt-4-turbo',
                'o1-mini',
                'gpt-3.5-turbo'
            ]
        elif provider == 'groq':
            return [
                os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile'),
                'llama-3.1-70b-versatile',
                'mixtral-8x7b-32768',
                'gemma2-9b-it',
                'llama-3.1-8b-instant'
            ]
        elif provider == 'gemini':
            return [
                os.getenv('GEMINI_MODEL', 'gemini-1.5-flash'),
                'gemini-1.5-pro',
                'gemini-1.5-flash-8b',
                'gemini-2.0-flash-exp'
            ]
        raise ConfigurationError(f"Unknown LLM provider: {provider}")

    def get_llm_model(self, provider: str = None) -> str:
        """Return the primary model for a provider"""
        if provider is None:
            provider = self.get_llm_provider()
            if provider == 'auto':
                provider = 'openrouter'
        models = self.get_llm_models(provider)
        return models[0] if models else 'gpt-4o'

    def get_llm_client(self, provider: str = None):
        """Return the LLM client for the given provider"""
        if provider is None:
            provider = self.get_llm_provider()
            if provider == 'auto':
                provider = 'openrouter'

        if provider == 'openrouter':
            api_key = os.getenv('OPENROUTER_API_KEY')
            if not api_key:
                raise ConfigurationError("Missing required API key: OPENROUTER_API_KEY")
            return OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "https://github.com/SamurAIGPT/Text-To-Video-AI",
                    "X-Title": "Text-To-Video-AI"
                }
            )
        elif provider == 'openai':
            return OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        elif provider == 'groq':
            if not GROQ_AVAILABLE:
                raise ConfigurationError("Groq library not installed. Run: pip install groq")
            return Groq(api_key=os.getenv('GROQ_API_KEY'))
        elif provider == 'gemini':
            if not GEMINI_AVAILABLE:
                raise ConfigurationError("Gemini library not installed. Run: pip install google-generativeai")
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            return genai

        raise ConfigurationError(f"Unknown LLM provider: {provider}")

    def get_stt_provider(self) -> Literal['whisper', 'deepgram']:
        return os.getenv('STT_PROVIDER', 'whisper').lower()

    def get_tts_provider(self) -> Literal['edgetts', 'elevenlabs']:
        return os.getenv('TTS_PROVIDER', 'edgetts').lower()

    def get_tts_voice(self) -> str:
        provider = self.get_tts_provider()
        if provider == 'edgetts':
            return os.getenv('EDGETTS_VOICE', 'en-AU-WilliamNeural')
        elif provider == 'elevenlabs':
            return os.getenv('ELEVENLABS_VOICE_ID', '21m00Tcm4TlvDq8ikWAM')
        raise ConfigurationError(f"Unknown TTS provider: {provider}")

    def get_pexels_api_key(self) -> str:
        key = os.getenv('PEXELS_API_KEY')
        if not key:
            raise ConfigurationError("PEXELS_API_KEY not found in .env file")
        return key

    def get_video_orientation(self) -> bool:
        orientation = os.getenv('VIDEO_ORIENTATION', 'portrait').lower()
        if orientation not in ['portrait', 'landscape']:
            raise ConfigurationError(
                f"Invalid VIDEO_ORIENTATION: '{orientation}'. Must be 'portrait' or 'landscape'"
            )
        return orientation == 'landscape'

    def get_deepgram_api_key(self) -> str:
        key = os.getenv('DEEPGRAM_API_KEY')
        if not key:
            raise ConfigurationError("DEEPGRAM_API_KEY not found in .env file")
        return key

    def get_elevenlabs_api_key(self) -> str:
        key = os.getenv('ELEVENLABS_API_KEY')
        if not key:
            raise ConfigurationError("ELEVENLABS_API_KEY not found in .env file")
        return key

    def get_captions_enabled(self) -> bool:
        return os.getenv('CAPTIONS_ENABLED', 'true').lower() == 'true'

    def get_caption_font_size(self) -> int:
        return int(os.getenv('CAPTION_FONT_SIZE', '100'))

    def get_caption_font_color(self) -> str:
        return os.getenv('CAPTION_FONT_COLOR', 'white').lower()

    def get_caption_stroke_width(self) -> int:
        return int(os.getenv('CAPTION_STROKE_WIDTH', '3'))

    def get_caption_stroke_color(self) -> str:
        return os.getenv('CAPTION_STROKE_COLOR', 'black').lower()

    def get_caption_position(self) -> str:
        position = os.getenv('CAPTION_POSITION', 'bottom_center').lower()
        valid_positions = ['center', 'top', 'bottom', 'bottom_center', 'bottom_left', 'bottom_right']
        if position not in valid_positions:
            raise ConfigurationError(
                f"Invalid CAPTION_POSITION: '{position}'. Must be one of: {', '.join(valid_positions)}"
            )
        return position

    def get_caption_font_face(self) -> str:
        return os.getenv('CAPTION_FONT_FACE', 'Arial-Bold')


def get_config() -> Config:
    try:
        return Config()
    except ConfigurationError as e:
        print(f"\n{'='*70}")
        print("ERROR: Configuration Failed")
        print('='*70)
        print(f"\n{str(e)}\n")
        print("Please fix these issues and try again.")
        print('='*70 + '\n')
        raise
