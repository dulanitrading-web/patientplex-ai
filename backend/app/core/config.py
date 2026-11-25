"""Application configuration loaded from environment variables."""

import logging
from pydantic import model_validator
from pydantic_settings import BaseSettings

_config_logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """PatientPlex AI application settings.

    All values can be overridden via environment variables or a .env file
    located in the project root.
    """

    PROJECT_NAME: str = "PatientPlex AI"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Sentry error tracking
    SENTRY_DSN: str = ""

    # Deployment URLs (used for OAuth callbacks and redirects)
    BACKEND_BASE_URL: str = "https://patientplex-ai-g7ce.onrender.com"
    FRONTEND_BASE_URL: str = "https://patientplex-ai.vercel.app"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://cliniccare:cliniccare@localhost:5432/cliniccare"

    # JWT / Auth
    SECRET_KEY: str = "change-this-to-a-random-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Google OAuth (Calendar integration)
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "https://patientplex-ai-g7ce.onrender.com/api/v1/onboarding/google-calendar/callback"

    # Meta / Facebook Ads
    META_APP_ID: str = ""
    META_APP_SECRET: str = ""

    # WhatsApp Business API
    WHATSAPP_API_URL: str = "https://graph.facebook.com/v25.0"
    WHATSAPP_API_TOKEN: str = ""
    WHATSAPP_VERIFY_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""  # Meta Cloud API phone number ID

    # Exotel (Primary — Indian voice calls + SMS)
    EXOTEL_API_KEY: str = ""
    EXOTEL_API_TOKEN: str = ""
    EXOTEL_SID: str = ""
    EXOTEL_CALLER_ID: str = ""  # ExoPhone virtual number
    EXOTEL_WEBHOOK_SECRET: str = ""  # For verifying Exotel webhook callbacks

    # Twilio (Backup — international only, not used for India)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    TWILIO_WHATSAPP_NUMBER: str = ""

    # Call handling
    CALL_PROVIDER: str = "exotel"  # "exotel" (India) or "twilio" (international)
    MISSED_CALL_WHATSAPP_DELAY_SECONDS: int = 30  # Wait before sending WhatsApp after missed call
    CLINIC_DEFAULT_OPEN_TIME: str = "09:00"
    CLINIC_DEFAULT_CLOSE_TIME: str = "20:00"
    SLOT_DURATION_MINUTES: int = 30

    # Cal.com (Open-source scheduling — replaces Google Calendar for booking)
    CALCOM_API_KEY: str = ""
    CALCOM_BASE_URL: str = "https://api.cal.com/v1"  # Self-hosted: your-domain/api/v1
    CALCOM_EVENT_TYPE_ID: int = 0  # Default event type for appointments

    # Razorpay (Billing / Payments)
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""  # For verifying Razorpay webhook signatures

    # Field-level encryption for sensitive data (e.g. OAuth tokens)
    # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    ENCRYPTION_KEY: str = ""

    # Redis (caching + rate limiting)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Claude API (AI ad copy generation + receptionist)
    CLAUDE_API_KEY: str = ""

    # Free/alternative LLM (OpenAI-compatible endpoint — Groq, Together, Ollama, etc.)
    # Set these to use a free model instead of Claude API for the receptionist
    FREE_LLM_API_KEY: str = ""          # e.g. Groq API key
    FREE_LLM_BASE_URL: str = ""         # e.g. https://api.groq.com/openai/v1
    FREE_LLM_MODEL: str = "llama-3.3-70b-versatile"  # Model to use

    # Cron endpoint protection — set to a random string; pass as X-Cron-Key header
    CRON_SECRET: str = ""

    # Feature flags
    ADS_ENABLED: bool = False  # Set True to enable ad platform integrations (Google/Meta/LinkedIn/GMB/GA4)

    # Google Ads API (requires ADS_ENABLED=true + developer token approval)
    GOOGLE_ADS_DEVELOPER_TOKEN: str = ""
    GOOGLE_ADS_LOGIN_CUSTOMER_ID: str = ""

    # Meta Marketing API
    META_ACCESS_TOKEN: str = ""
    META_AD_ACCOUNT_ID: str = ""

    # Google My Business API
    GOOGLE_GMB_API_KEY: str = ""

    # LinkedIn Marketing API
    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""
    LINKEDIN_ACCESS_TOKEN: str = ""

    # ChatGPT Ads (OpenAI Sponsored Answers)
    CHATGPT_ADS_API_KEY: str = ""

    # Google Analytics 4
    GA4_MEASUREMENT_ID: str = ""      # G-XXXXXXXXXX
    GA4_API_SECRET: str = ""          # Measurement Protocol API secret
    GA4_PROPERTY_ID: str = ""         # GA4 property ID for Data API reporting

    # Email (appointment confirmations, reminders, digests)
    # Supports SMTP (Gmail, Zoho, any SMTP) or Resend API
    EMAIL_PROVIDER: str = "smtp"      # "smtp" or "resend"
    SMTP_HOST: str = ""               # e.g. smtp.gmail.com
    SMTP_PORT: int = 587
    SMTP_USER: str = ""               # e.g. noreply@patientplex.ai
    SMTP_PASSWORD: str = ""           # app password
    EMAIL_FROM_NAME: str = "PatientPlex AI"
    EMAIL_FROM_ADDRESS: str = ""      # e.g. noreply@patientplex.ai
    RESEND_API_KEY: str = ""          # If using Resend

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }

    @model_validator(mode="after")
    def _block_default_secret_key(self) -> "Settings":
        if (
            self.ENVIRONMENT != "development"
            and self.SECRET_KEY == "change-this-to-a-random-secret-key-in-production"
        ):
            raise ValueError(
                "SECRET_KEY must be changed from the default value in non-development environments. "
                "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        if not self.ENCRYPTION_KEY:
            _config_logger.warning(
                "ENCRYPTION_KEY is not set — OAuth tokens will be stored unencrypted. "
                "Generate one with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )
        return self


settings = Settings()
