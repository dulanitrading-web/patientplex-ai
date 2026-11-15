"""Google Ads OAuth2 flow for per-clinic account linking.

Each clinic connects their OWN Google Ads account through OAuth.
PatientPlex then manages campaigns on their behalf using the MCC + their refresh token.

Flow:
1. Doctor clicks "Connect Google Ads" in Settings
2. Redirected to Google OAuth consent screen (requesting ads.readonly + adwords scope)
3. Doctor authorizes → Google redirects back with auth code
4. We exchange code for refresh_token → store encrypted in doctor record
5. All campaign operations use this doctor's refresh_token + our MCC developer token

This is how real agency tools work — Ryze AI, Madgicx, Optmyzr all do this.
"""

import logging
import os
from typing import Optional
from urllib.parse import urlencode

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# Google Ads OAuth scopes
GOOGLE_ADS_SCOPES = [
    "https://www.googleapis.com/auth/adwords",  # Full Google Ads access
]

# Google OAuth endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def get_google_ads_auth_url(doctor_id: str, redirect_uri: str) -> str:
    """Generate Google OAuth consent URL for Google Ads access.

    Args:
        doctor_id: UUID of the doctor, passed as state parameter
        redirect_uri: Where Google sends the user after consent

    Returns:
        The full Google OAuth consent URL
    """
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(GOOGLE_ADS_SCOPES),
        "access_type": "offline",  # Gets us a refresh_token
        "prompt": "consent",  # Always show consent screen (ensures refresh_token)
        "state": f"google_ads:{doctor_id}",
        "include_granted_scopes": "true",
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


async def exchange_google_ads_code(
    code: str, redirect_uri: str
) -> dict:
    """Exchange authorization code for tokens.

    Returns:
        dict with access_token, refresh_token, expires_in
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        logger.info("Google Ads OAuth token exchange successful")
        return {
            "access_token": data.get("access_token"),
            "refresh_token": data.get("refresh_token"),
            "expires_in": data.get("expires_in"),
            "token_type": data.get("token_type"),
        }


async def get_google_ads_customer_ids(access_token: str) -> list[dict]:
    """Fetch accessible Google Ads customer IDs using the access token.

    Uses the Google Ads API to list all accounts the user has access to.
    Falls back to returning empty list if google-ads SDK isn't available.
    """
    try:
        from google.ads.googleads.client import GoogleAdsClient

        config = {
            "developer_token": settings.GOOGLE_ADS_DEVELOPER_TOKEN,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "use_proto_plus": True,
        }
        if settings.GOOGLE_ADS_LOGIN_CUSTOMER_ID:
            config["login_customer_id"] = settings.GOOGLE_ADS_LOGIN_CUSTOMER_ID

        # Use the OAuth access token
        client = GoogleAdsClient.load_from_dict({
            **config,
            "refresh_token": "dummy",  # Will use access_token directly
        })

        # List accessible customers
        customer_service = client.get_service("CustomerService")
        response = customer_service.list_accessible_customers()

        customers = []
        for resource_name in response.resource_names:
            customer_id = resource_name.split("/")[-1]
            customers.append({
                "customer_id": customer_id,
                "resource_name": resource_name,
            })

        return customers

    except ImportError:
        logger.warning("google-ads SDK not available — can't list customer IDs")
        return []
    except Exception as e:
        logger.error("Failed to list Google Ads customers: %s", e)
        return []
