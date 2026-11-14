"""Google My Business endpoints — manage clinic profile, reviews, and posts.

Provides:
- Profile sync from Google Business Profile
- Review monitoring and AI-generated reply suggestions
- Post creation (offers, updates, events)
- Performance insights (views, calls, direction requests)
- Automated review request links for patients
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_doctor
from app.db.session import get_db
from app.models.doctor import Doctor
from app.services.google_my_business import GoogleMyBusinessService

router = APIRouter(prefix="/gmb", tags=["google-my-business"])


# ─── Request Models ───

class ReplyRequest(BaseModel):
    review_id: str
    reply_text: str


class GenerateReplyRequest(BaseModel):
    review_text: str
    rating: int


class CreatePostRequest(BaseModel):
    post_type: str = "UPDATE"  # UPDATE, OFFER, EVENT
    title: str = ""
    body: str
    cta_type: str = "BOOK"
    cta_url: str = ""


class GeneratePostRequest(BaseModel):
    post_type: str = "UPDATE"
    treatment: str = ""


# ─── Profile ───

@router.get("/profile")
async def get_profile(
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Get the clinic's Google Business Profile.

    Returns clinic name, address, hours, rating, review count, and verification status.
    Falls back to demo data if GMB is not connected.
    """
    service = GoogleMyBusinessService(db)
    return await service.get_business_profile(doctor)


@router.post("/profile/sync")
async def sync_profile(
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Sync clinic info from Google Business Profile into PatientPlex.

    Pulls name, address, phone, hours, categories, website URL.
    """
    service = GoogleMyBusinessService(db)
    return await service.sync_profile(doctor)


# ─── Reviews ───

@router.get("/reviews")
async def get_reviews(
    page_size: int = 20,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Get recent Google reviews for the clinic.

    Returns reviews with rating, text, reviewer name, timestamp, and reply status.
    """
    service = GoogleMyBusinessService(db)
    return await service.get_reviews(doctor, page_size)


@router.post("/reviews/reply")
async def reply_to_review(
    body: ReplyRequest,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Post a reply to a Google review.

    The reply appears publicly under the review on Google Maps and Search.
    """
    service = GoogleMyBusinessService(db)
    return await service.reply_to_review(doctor, body.review_id, body.reply_text)


@router.post("/reviews/generate-reply")
async def generate_reply(
    body: GenerateReplyRequest,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """AI-generate a professional reply to a Google review.

    Returns a suggested reply based on review sentiment. Doctor reviews before posting.
    """
    service = GoogleMyBusinessService(db)
    return await service.generate_review_reply(doctor, body.review_text, body.rating)


@router.get("/reviews/request-link")
async def get_review_request_link(
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Generate a direct review link and WhatsApp message template.

    Returns a URL that opens Google Maps on the review form, plus
    pre-written WhatsApp and SMS messages to send to patients after appointments.
    """
    service = GoogleMyBusinessService(db)
    return await service.generate_review_link(doctor)


# ─── Posts ───

@router.post("/posts")
async def create_post(
    body: CreatePostRequest,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Create a Google Business Profile post.

    Supports: UPDATE (general news), OFFER (promotion), EVENT (clinic event).
    Each post appears on the clinic's Google Maps and Search listing.
    """
    service = GoogleMyBusinessService(db)
    return await service.create_post(
        doctor, body.post_type, body.title, body.body, body.cta_type, body.cta_url,
    )


@router.post("/posts/generate")
async def generate_post(
    body: GeneratePostRequest,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """AI-generate NMC-compliant content for a Google Business Profile post.

    Returns suggested post text based on the clinic's specialty and treatment.
    """
    service = GoogleMyBusinessService(db)
    return await service.generate_post_content(doctor, body.post_type, body.treatment)


# ─── Insights ───

@router.get("/insights")
async def get_insights(
    days: int = 30,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Get Google Business Profile performance insights.

    Returns: profile views, search appearances, direction requests,
    phone calls, website clicks, photo views — with trends.
    """
    service = GoogleMyBusinessService(db)
    return await service.get_insights(doctor, days)
