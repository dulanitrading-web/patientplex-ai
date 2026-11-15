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


def get_google_ads_auth_url(state: str, redirect_uri: str) -> str:
    """Generate Google OAuth consent URL for Google Ads access.

    Args:
        state: Opaque state token for CSRF protection (created by caller)
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
        "state": state,
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

    Uses the Google Ads REST API directly with the OAuth access token.
    This avoids issues with the SDK needing a refresh_token at init time.
    """
    if not settings.GOOGLE_ADS_DEVELOPER_TOKEN:
        logger.warning("GOOGLE_ADS_DEVELOPER_TOKEN not set — can't list customer IDs")
        return []

    try:
        # Use the REST API directly — much more reliable than SDK for this
        api_url = "https://googleads.googleapis.com/v26/customers:listAccessibleCustomers"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "developer-token": settings.GOOGLE_ADS_DEVELOPER_TOKEN,
        }
        # NOTE: Do NOT include login-customer-id for listAccessibleCustomers.
        # This endpoint uses the OAuth user's own access and doesn't need MCC context.
        # Including an MCC login-customer-id when the user isn't an MCC client causes 403.

        logger.info("Listing accessible customers with dev-token=%s...",
                     settings.GOOGLE_ADS_DEVELOPER_TOKEN[:6] if settings.GOOGLE_ADS_DEVELOPER_TOKEN else "NONE")

        async with httpx.AsyncClient() as client:
            resp = await client.get(api_url, headers=headers, timeout=15)
            if resp.status_code != 200:
                logger.error("listAccessibleCustomers returned %s: %s", resp.status_code, resp.text[:500])
            resp.raise_for_status()
            data = resp.json()

        customers = []
        for resource_name in data.get("resourceNames", []):
            customer_id = resource_name.split("/")[-1]
            customers.append({
                "customer_id": customer_id,
                "resource_name": resource_name,
            })

        logger.info("Found %d accessible Google Ads customers", len(customers))
        return customers

    except Exception as e:
        logger.error("Failed to list Google Ads customers via REST: %s", e)
        return []
