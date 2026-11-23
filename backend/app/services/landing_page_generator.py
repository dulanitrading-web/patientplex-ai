"""Dynamic micro-landing page generator.

Creates dr-name.patientplex.ai subdomain pages with:
- Doctor credentials and photo
- Treatment-specific content
- Google Maps embed
- WhatsApp CTA button
- SEO-optimized meta tags
"""

import logging
import re

from app.core.config import settings
from app.models.doctor import Doctor
from app.schemas.specialty import SPECIALTY_CONFIGS

logger = logging.getLogger(__name__)


def generate_slug(doctor: Doctor) -> str:
    """Generate a URL-friendly slug from doctor name.

    Examples:
        "Dr. Prudhvi Reddy" -> "dr-prudhvi-reddy"
        "Dr. S.K. Sharma" -> "dr-sk-sharma"
    """
    name = doctor.full_name.lower().strip()
    name = re.sub(r"[^\w\s-]", "", name)  # Remove special chars except hyphens
    name = re.sub(r"[\s.]+", "-", name)  # Replace spaces/dots with hyphens
    name = re.sub(r"-+", "-", name).strip("-")  # Collapse multiple hyphens
    if not name.startswith("dr-"):
        name = f"dr-{name}"
    return name


def generate_landing_page_html(doctor: Doctor) -> str:
    """Generate a complete, self-contained HTML landing page for a doctor.

    The page is optimized for:
    - Mobile-first design
    - Fast loading (no external JS frameworks)
    - WhatsApp click-to-chat conversion
    - Local SEO with schema markup
    - Google Ads quality score (relevant, fast landing page)
    """
    specialty = doctor.specialty.value.replace("_", " ").title() if doctor.specialty else "Healthcare"
    services = doctor.services or ["General Consultation"]
    clinic_name = doctor.clinic_name or "Clinic"
    city = doctor.city or ""
    address = doctor.clinic_address or ""
    phone = doctor.whatsapp_number or doctor.phone or ""
    wa_number = phone.replace("+", "").replace(" ", "").replace("-", "")

    # Build service cards HTML
    service_cards = "\n".join(
        f'<div class="service-card"><span class="service-icon">✓</span>{svc}</div>'
        for svc in services
    )

    # Schema.org structured data for local SEO
    schema_json = f"""{{
  "@context": "https://schema.org",
  "@type": "MedicalBusiness",
  "name": "{clinic_name}",
  "description": "{specialty} services by {doctor.full_name} in {city}",
  "address": {{
    "@type": "PostalAddress",
    "streetAddress": "{address}",
    "addressLocality": "{city}",
    "addressRegion": "{doctor.state or ''}",
    "postalCode": "{doctor.pincode or ''}"
  }},
  "telephone": "{phone}",
  "medicalSpecialty": "{specialty}"
}}"""

    maps_embed_src = ""
    if doctor.latitude and doctor.longitude:
        maps_embed_src = f"https://maps.google.com/maps?q={doctor.latitude},{doctor.longitude}&z=15&output=embed"
    elif address and city:
        from urllib.parse import quote_plus
        maps_embed_src = f"https://maps.google.com/maps?q={quote_plus(f'{address}, {city}')}&z=15&output=embed"

    page_title = f"{doctor.full_name} — {specialty} in {city} | {clinic_name}"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <meta name="description" content="{specialty} services at {clinic_name} in {city}. {', '.join(services[:3])}. Book via WhatsApp.">
    <meta name="robots" content="index, follow">
    <meta property="og:title" content="{page_title}">
    <meta property="og:type" content="website">
    <meta property="og:description" content="Expert {specialty.lower()} care by {doctor.full_name}. Book your appointment today.">
    <script type="application/ld+json">{schema_json}</script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #1a1a2e; background: #f8f9fa; }}
        .hero {{ background: linear-gradient(135deg, #0B2545 0%, #13838C 100%); color: white; padding: 3rem 1.5rem 2rem; text-align: center; }}
        .hero h1 {{ font-size: 1.75rem; font-weight: 700; margin-bottom: 0.5rem; }}
        .hero .specialty {{ font-size: 1.1rem; opacity: 0.9; margin-bottom: 0.25rem; }}
        .hero .clinic {{ font-size: 0.95rem; opacity: 0.8; }}
        .trust-bar {{ display: flex; justify-content: center; gap: 1.5rem; padding: 1rem; background: white; border-bottom: 1px solid #e9ecef; font-size: 0.85rem; color: #555; }}
        .trust-bar span {{ display: flex; align-items: center; gap: 0.3rem; }}
        .section {{ max-width: 600px; margin: 0 auto; padding: 1.5rem; }}
        .section-title {{ font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem; color: #0B2545; }}
        .service-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }}
        .service-card {{ background: white; border: 1px solid #e9ecef; border-radius: 10px; padding: 0.85rem; font-size: 0.9rem; display: flex; align-items: center; gap: 0.5rem; }}
        .service-icon {{ color: #13838C; font-weight: bold; }}
        .map-container {{ border-radius: 12px; overflow: hidden; margin: 1rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .map-container iframe {{ width: 100%; height: 250px; border: 0; }}
        .address-text {{ font-size: 0.9rem; color: #555; line-height: 1.5; margin-top: 0.75rem; }}
        .cta-bar {{ position: fixed; bottom: 0; left: 0; right: 0; background: white; padding: 0.75rem 1.5rem; box-shadow: 0 -2px 10px rgba(0,0,0,0.1); display: flex; gap: 0.75rem; z-index: 100; }}
        .cta-btn {{ flex: 1; padding: 0.85rem; border: none; border-radius: 10px; font-size: 1rem; font-weight: 600; cursor: pointer; text-decoration: none; text-align: center; display: flex; align-items: center; justify-content: center; gap: 0.5rem; }}
        .cta-whatsapp {{ background: #25D366; color: white; }}
        .cta-call {{ background: #0B2545; color: white; }}
        .spacer {{ height: 80px; }}
        @media (max-width: 400px) {{
            .service-grid {{ grid-template-columns: 1fr; }}
            .hero h1 {{ font-size: 1.4rem; }}
        }}
    </style>
</head>
<body>
    <div class="hero">
        <h1>{doctor.full_name}</h1>
        <div class="specialty">{specialty}</div>
        <div class="clinic">{clinic_name} · {city}</div>
    </div>

    <div class="trust-bar">
        <span>✓ Verified Doctor</span>
        <span>📍 {city}</span>
        <span>💬 WhatsApp Booking</span>
    </div>

    <div class="section">
        <div class="section-title">Services Offered</div>
        <div class="service-grid">
            {service_cards}
        </div>
    </div>

    <div class="section">
        <div class="section-title">Clinic Location</div>
        {'<div class="map-container"><iframe src="' + maps_embed_src + '" loading="lazy" allowfullscreen referrerpolicy="no-referrer-when-downgrade"></iframe></div>' if maps_embed_src else ''}
        <div class="address-text">📍 {address}, {city} {doctor.pincode or ''}</div>
    </div>

    <div class="spacer"></div>

    <div class="cta-bar">
        <a href="https://wa.me/{wa_number}?text=Hi%2C%20I%20want%20to%20book%20an%20appointment" class="cta-btn cta-whatsapp" target="_blank">
            💬 Book on WhatsApp
        </a>
        <a href="tel:{phone}" class="cta-btn cta-call">
            📞 Call Now
        </a>
    </div>

    <script>
        // Track CTA clicks for analytics
        document.querySelectorAll('.cta-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                const action = btn.classList.contains('cta-whatsapp') ? 'whatsapp_click' : 'call_click';
                if (typeof gtag !== 'undefined') {{
                    gtag('event', action, {{ event_category: 'conversion' }});
                }}
            }});
        }});
    </script>
</body>
</html>"""


def generate_treatment_page_html(doctor: Doctor, treatment: str) -> str:
    """Generate a treatment-specific landing page.

    Example: dr-prudhvi.patientplex.ai/braces
    These pages have higher Google Ads quality scores because they match
    the specific keyword the patient searched for.
    """
    specialty = doctor.specialty.value.replace("_", " ").title() if doctor.specialty else "Healthcare"
    clinic_name = doctor.clinic_name or "Clinic"
    city = doctor.city or ""
    phone = doctor.whatsapp_number or doctor.phone or ""
    wa_number = phone.replace("+", "").replace(" ", "").replace("-", "")
    treatment_slug = treatment.lower().replace(" ", "-")

    # Treatment-specific content hints (would be AI-generated in production)
    page_title = f"{treatment} in {city} — {doctor.full_name} | {clinic_name}"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <meta name="description" content="{treatment} by {doctor.full_name} at {clinic_name}, {city}. Book your appointment on WhatsApp.">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #1a1a2e; background: #f8f9fa; }}
        .hero {{ background: linear-gradient(135deg, #0B2545 0%, #13838C 100%); color: white; padding: 3rem 1.5rem; text-align: center; }}
        .hero h1 {{ font-size: 1.6rem; font-weight: 700; margin-bottom: 0.5rem; }}
        .hero p {{ opacity: 0.9; }}
        .section {{ max-width: 600px; margin: 0 auto; padding: 1.5rem; }}
        .card {{ background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }}
        .card h2 {{ font-size: 1.1rem; color: #0B2545; margin-bottom: 0.75rem; }}
        .card p {{ font-size: 0.9rem; line-height: 1.6; color: #444; }}
        .doctor-info {{ display: flex; align-items: center; gap: 1rem; }}
        .doctor-details h3 {{ font-size: 1rem; }}
        .doctor-details p {{ font-size: 0.85rem; color: #666; }}
        .cta-bar {{ position: fixed; bottom: 0; left: 0; right: 0; background: white; padding: 0.75rem 1.5rem; box-shadow: 0 -2px 10px rgba(0,0,0,0.1); z-index: 100; }}
        .cta-btn {{ display: block; width: 100%; padding: 1rem; background: #25D366; color: white; border: none; border-radius: 10px; font-size: 1.05rem; font-weight: 600; text-align: center; text-decoration: none; cursor: pointer; }}
        .spacer {{ height: 240px; }}
        .form-card {{ background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 2px 12px rgba(0,0,0,0.12); border: 2px solid #10b981; }}
        .form-card h2 {{ font-size: 1.15rem; color: #0B2545; margin-bottom: 0.5rem; text-align: center; }}
        .form-card p {{ font-size: 0.85rem; color: #666; text-align: center; margin-bottom: 1rem; }}
        .form-input {{ width: 100%; padding: 0.85rem 1rem; border: 1px solid #d1d5db; border-radius: 8px; font-size: 0.95rem; margin-bottom: 0.75rem; outline: none; }}
        .form-input:focus {{ border-color: #10b981; box-shadow: 0 0 0 3px rgba(16,185,129,0.15); }}
        .form-submit {{ width: 100%; padding: 0.9rem; background: #10b981; color: white; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; }}
        .form-submit:hover {{ background: #059669; }}
        .form-submit:disabled {{ background: #94a3b8; cursor: not-allowed; }}
        .form-success {{ text-align: center; padding: 2rem 1rem; }}
        .form-success h3 {{ color: #10b981; font-size: 1.3rem; margin-bottom: 0.5rem; }}
        .form-success p {{ color: #64748b; }}
        .hidden {{ display: none; }}
    </style>
</head>
<body>
    <div class="hero">
        <h1>{treatment} in {city}</h1>
        <p>{clinic_name} — {doctor.full_name}</p>
    </div>

    <div class="section">
        <!-- Lead Capture Form -->
        <div class="form-card" id="leadForm">
            <h2>📋 Book Your Consultation</h2>
            <p>Fill in your details — we'll call you within 15 minutes</p>
            <form id="inquiryForm" onsubmit="submitLead(event)">
                <input type="text" name="patient_name" class="form-input" placeholder="Your Name *" required />
                <input type="tel" name="patient_phone" class="form-input" placeholder="Phone Number *" required pattern="[0-9]{{10}}" title="Enter 10-digit phone number" />
                <input type="email" name="patient_email" class="form-input" placeholder="Email (optional)" />
                <button type="submit" class="form-submit" id="submitBtn">
                    Get Free Consultation →
                </button>
            </form>
        </div>
        <div class="form-card hidden" id="successMsg">
            <div class="form-success">
                <h3>✅ Thank You!</h3>
                <p>{clinic_name} will call you within 10-15 minutes.</p>
                <p style="margin-top: 1rem;">
                    <a href="https://wa.me/{wa_number}?text=Hi%2C%20I%20just%20submitted%20an%20inquiry%20for%20{treatment.replace(' ', '%20')}" style="color: #25D366; font-weight: 600;">
                        💬 Or WhatsApp us now
                    </a>
                </p>
            </div>
        </div>

        <div class="card">
            <h2>About This Treatment</h2>
            <p>Get expert {treatment.lower()} care at {clinic_name}. {doctor.full_name} ({specialty}) provides personalized treatment plans tailored to your needs.</p>
        </div>

        <div class="card">
            <h2>Why Choose Us</h2>
            <p>✓ Experienced {specialty.lower()} specialist<br>
               ✓ Modern equipment and facilities<br>
               ✓ Convenient location in {city}<br>
               ✓ Easy WhatsApp booking — instant confirmation</p>
        </div>

        <div class="card">
            <div class="doctor-info">
                <div class="doctor-details">
                    <h3>{doctor.full_name}</h3>
                    <p>{specialty} · {clinic_name}</p>
                    <p>📍 {city}</p>
                </div>
            </div>
        </div>
    </div>

    <div class="spacer"></div>

    <div class="cta-bar">
        <a href="https://wa.me/{wa_number}?text=Hi%2C%20I'm%20interested%20in%20{treatment.replace(' ', '%20')}" class="cta-btn" target="_blank">
            💬 Book {treatment} — WhatsApp
        </a>
    </div>

    <script>
        const API_URL = '{settings.BACKEND_BASE_URL}/api/v1';

        async function submitLead(e) {{
            e.preventDefault();
            const btn = document.getElementById('submitBtn');
            btn.disabled = true;
            btn.textContent = 'Submitting...';

            const form = document.getElementById('inquiryForm');
            const params = new URLSearchParams(window.location.search);

            const data = {{
                patient_name: form.patient_name.value,
                patient_phone: form.patient_phone.value,
                patient_email: form.patient_email.value || null,
                treatment: '{treatment}',
                keyword: params.get('utm_term') || params.get('keyword') || null,
                lead_source: params.get('utm_source') ? 'Google Ads' : 'Website',
                landing_page: '{treatment_slug}',
                doctor_slug: '{generate_slug(doctor)}',
                utm_source: params.get('utm_source') || null,
                utm_medium: params.get('utm_medium') || null,
                utm_campaign: params.get('utm_campaign') || null,
                utm_term: params.get('utm_term') || null,
                utm_content: params.get('utm_content') || null,
            }};

            try {{
                const resp = await fetch(API_URL + '/leads', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(data),
                }});
                const result = await resp.json();

                if (result.success) {{
                    document.getElementById('leadForm').classList.add('hidden');
                    document.getElementById('successMsg').classList.remove('hidden');
                    // Track conversion
                    if (typeof gtag !== 'undefined') {{
                        gtag('event', 'lead_submitted', {{
                            event_category: 'conversion',
                            event_label: '{treatment}',
                        }});
                    }}
                }} else {{
                    btn.disabled = false;
                    btn.textContent = 'Get Free Consultation →';
                    alert('Something went wrong. Please try again or call us directly.');
                }}
            }} catch (err) {{
                btn.disabled = false;
                btn.textContent = 'Get Free Consultation →';
                alert('Network error. Please try again or WhatsApp us.');
            }}
        }}

        // Track CTA clicks
        document.querySelectorAll('.cta-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                if (typeof gtag !== 'undefined') {{
                    gtag('event', 'whatsapp_click', {{ event_category: 'conversion' }});
                }}
            }});
        }});
    </script>
</body>
</html>"""
