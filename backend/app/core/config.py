"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """PatientPlex AI application settings.

    All values can be overridden via environment variables or a .env file
    located in the project root.
    """

    PROJECT_NAME: str = "PatientPlex AI"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://cliniccare:cliniccare@localhost:5432/cliniccare"

    # JWT / Auth
    SECRET_KEY: str = "change-this-to-a-random-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Google OAuth (Calendar integration)
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/onboarding/google-calendar/callback"

    # Meta / Facebook Ads
    META_APP_ID: str = ""
    META_APP_SECRET: str = ""

    # WhatsApp Business API
    WHATSAPP_API_URL: str = "https://graph.facebook.com/v18.0"
    WHATSAPP_API_TOKEN: str = ""

    # Twilio (Voice calls + SMS + WhatsApp)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""  # Twilio number for outbound calls
    TWILIO_WHATSAPP_NUMBER: str = ""  # Twilio WhatsApp sandbox or business number

    # Exotel (India-specific voice — alternative to Twilio)
    EXOTEL_API_KEY: str = ""
    EXOTEL_API_TOKEN: str = ""
    EXOTEL_SID: str = ""
    EXOTEL_CALLER_ID: str = ""  # Virtual number

    # Call handling
    CALL_PROVIDER: str = "twilio"  # "twilio" or "exotel"
    MISSED_CALL_WHATSAPP_DELAY_SECONDS: int = 30  # Wait before sending WhatsApp after missed call
    CLINIC_DEFAULT_OPEN_TIME: str = "09:00"
    CLINIC_DEFAULT_CLOSE_TIME: str = "20:00"
    SLOT_DURATION_MINUTES: int = 30

    # Cal.com (Open-source scheduling — replaces Google Calendar for booking)
    CALCOM_API_KEY: str = ""
    CALCOM_BASE_URL: str = "https://api.cal.com/v1"  # Self-hosted: your-domain/api/v1
    CALCOM_EVENT_TYPE_ID: int = 0  # Default event type for appointments

    # Claude API (AI ad copy generation + receptionist)
    CLAUDE_API_KEY: str = ""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()
