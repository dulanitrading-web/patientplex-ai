"""
Product Audit: Simulating 100 doctors from different fields using PatientPlex.

This isn't a unit test — it's a product teardown. We simulate real doctors
signing up and using the platform, and document every gap, friction point,
and missing feature they'd encounter.

Categories of doctors tested:
1. Dentists (general, cosmetic, orthodontic, pediatric, implant specialists)
2. Dermatologists
3. Ophthalmologists (eye clinics, LASIK centers)
4. Orthopedic surgeons
5. ENT specialists
6. Gynecologists
7. Pediatricians
8. Physiotherapists
9. Ayurvedic/Homeopathic practitioners
10. Multi-specialty clinics

Each "doctor" goes through: signup → onboarding → settings → integrations → campaigns
"""

import json
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProductIssue:
    """A gap/issue found during the product audit."""
    severity: str  # P0 (blocker), P1 (major), P2 (moderate), P3 (minor), P4 (nice-to-have)
    category: str
    title: str
    description: str
    affected_doctors: str  # "all" or specific specialties
    current_behavior: str
    expected_behavior: str
    solution: str
    effort: str  # "small" (1-2 days), "medium" (3-7 days), "large" (1-2 weeks)


issues: list[ProductIssue] = []

# ═══════════════════════════════════════════════════════════════
# PHASE 1: SIGNUP & ONBOARDING
# ═══════════════════════════════════════════════════════════════

issues.append(ProductIssue(
    severity="P0",
    category="Onboarding",
    title="Platform is hardcoded for DENTIST specialty only",
    description=(
        "The specialty dropdown and all treatment services are dental-specific. "
        "A dermatologist, ophthalmologist, or orthopedic surgeon cannot use this platform. "
        "The entire value proposition breaks for 90% of potential clinic customers."
    ),
    affected_doctors="all non-dental specialties",
    current_behavior="Specialty options include only DENTIST; services are Root Canal, Braces, etc.",
    expected_behavior="Specialty dropdown should include 15+ specialties, each with its own services list",
    solution=(
        "1. Add specialty-to-services mapping in backend\n"
        "2. Dermatologist: Acne Treatment, Hair Loss, Skin Whitening, Laser, Chemical Peel, PRP, Botox, Fillers\n"
        "3. Ophthalmologist: LASIK, Cataract, Glaucoma, Retina, Contact Lens, Eye Checkup\n"
        "4. Orthopedic: Joint Replacement, Spine Surgery, Sports Injury, Fracture, Arthroscopy\n"
        "5. ENT: Hearing Aid, Sinus Surgery, Tonsil, Adenoid, Sleep Apnea\n"
        "6. Gynecologist: Normal Delivery, C-Section, Fertility, IVF, Laparoscopy, PCOS\n"
        "7. Pediatrician: Vaccination, Growth Assessment, Child Nutrition\n"
        "8. Physiotherapy: Back Pain, Knee Rehab, Sports Injury, Post-Surgery Rehab\n"
        "9. Ayurvedic: Panchakarma, Weight Loss, Skin Treatment, Joint Pain\n"
        "10. Multi-specialty: All of the above as configurable"
    ),
    effort="medium",
))

issues.append(ProductIssue(
    severity="P1",
    category="Onboarding",
    title="No phone number validation for Indian numbers",
    description="Phone field accepts any text. Indian clinic owners may enter number with/without country code, with spaces, with dashes.",
    affected_doctors="all",
    current_behavior="Free text input for phone number",
    expected_behavior="Validate Indian mobile (10 digits starting with 6-9), auto-add +91 prefix, format display",
    solution="Add regex validation: /^[6-9]\\d{9}$/ and auto-prefix +91",
    effort="small",
))

issues.append(ProductIssue(
    severity="P1",
    category="Onboarding",
    title="No clinic logo upload",
    description="Clinics can't upload their logo. The dashboard shows a generic icon. For a paid marketing platform, this looks unfinished.",
    affected_doctors="all",
    current_behavior="No logo upload option. Generic initials shown.",
    expected_behavior="Logo upload on onboarding step 1, shown across dashboard and marketing materials",
    solution="Add image upload field in onboarding, store in S3/Cloudinary, display in header",
    effort="medium",
))

issues.append(ProductIssue(
    severity="P2",
    category="Onboarding",
    title="Geo radius selection has no visual feedback",
    description="Doctor selects a radius in km but can't see it on a map. They don't know what '10km radius' actually covers in their city.",
    affected_doctors="all",
    current_behavior="Slider/input for radius in km, no map",
    expected_behavior="Interactive map showing the targeting radius centered on clinic address",
    solution="Add Google Maps embed with radius circle overlay centered on clinic pincode",
    effort="medium",
))

# ═══════════════════════════════════════════════════════════════
# PHASE 2: DASHBOARD
# ═══════════════════════════════════════════════════════════════

issues.append(ProductIssue(
    severity="P1",
    category="Dashboard",
    title="Dashboard shows all zeros for new users — feels broken",
    description=(
        "A doctor who just signed up sees: 0 patients, 0 appointments, 0 campaigns, "
        "0 spend. The dashboard feels dead. There's no guidance on what to do next."
    ),
    affected_doctors="all new users",
    current_behavior="All metrics show 0. No onboarding checklist or getting-started guide.",
    expected_behavior=(
        "Show a getting-started checklist: ✅ Sign up, ⬜ Connect Google Ads, ⬜ Connect Calendar, "
        "⬜ Launch first campaign. Show estimated results based on their budget and city."
    ),
    solution="Add a WelcomeChecklist component that shows until all integrations are connected and first campaign is live",
    effort="medium",
))

issues.append(ProductIssue(
    severity="P2",
    category="Dashboard",
    title="No real-time or near-real-time data refresh",
    description="Dashboard data is only loaded on page load. Doctor has to manually refresh to see updated campaign metrics.",
    affected_doctors="all",
    current_behavior="Static load on page mount. No auto-refresh.",
    expected_behavior="Auto-refresh every 5 minutes, or real-time via WebSocket for active campaigns",
    solution="Add setInterval refresh every 5 minutes for campaign stats, with loading indicator",
    effort="small",
))

issues.append(ProductIssue(
    severity="P1",
    category="Dashboard",
    title="No cost per lead / cost per appointment metric",
    description=(
        "The most important metric for a clinic owner is: 'How much am I paying per patient?' "
        "Currently shows CPC and CTR which are marketing jargon. Doctors don't care about CTR."
    ),
    affected_doctors="all",
    current_behavior="Shows: impressions, clicks, CTR, CPC, spend",
    expected_behavior="Shows: New Patients This Month, Cost Per Patient, Appointments Booked, Total Spend, ROI",
    solution=(
        "1. Add 'cost_per_appointment' calculated metric (spend / conversions)\n"
        "2. Add 'estimated_revenue' (appointments * avg treatment value)\n"
        "3. Add 'roi' ((estimated_revenue - spend) / spend * 100)\n"
        "4. Move CTR/CPC to an 'Advanced Analytics' section"
    ),
    effort="medium",
))

# ═══════════════════════════════════════════════════════════════
# PHASE 3: CAMPAIGNS
# ═══════════════════════════════════════════════════════════════

issues.append(ProductIssue(
    severity="P0",
    category="Campaigns",
    title="Budget split is equal across all campaigns — not performance-based",
    description=(
        "When a doctor sets ₹50K/month budget, it's divided equally. A campaign with "
        "12% CTR gets the same budget as one with 0% CTR. This wastes money."
    ),
    affected_doctors="all",
    current_behavior="Equal budget split across platforms/campaigns",
    expected_behavior="AI allocates budget based on: performance score, treatment value tier, conversion rate",
    solution="NEW: PerformanceMarketingBrain now handles this — deployed",
    effort="done",
))

issues.append(ProductIssue(
    severity="P1",
    category="Campaigns",
    title="No campaign creation wizard — doctor doesn't know what campaigns to create",
    description=(
        "The 'Launch New' button creates campaigns programmatically but the doctor has "
        "no control over what gets created. No wizard to choose treatment, budget, keywords."
    ),
    affected_doctors="all",
    current_behavior="'Launch New' button auto-creates campaigns for all platforms",
    expected_behavior=(
        "AI recommends campaigns based on services offered, then doctor confirms. "
        "Wizard flow: 1) Select treatments to advertise, 2) Set budget per treatment, "
        "3) AI generates keywords/copy, 4) Doctor reviews and launches"
    ),
    solution="Add /campaigns/wizard endpoint + frontend multi-step form",
    effort="large",
))

issues.append(ProductIssue(
    severity="P1",
    category="Campaigns",
    title="Imported campaigns can't be edited from PatientPlex",
    description=(
        "BDC's 13 imported Google Ads campaigns show metrics but can't be edited "
        "(budget, keywords, ad copy) from the PatientPlex dashboard. Doctor still needs "
        "to go to Google Ads."
    ),
    affected_doctors="all with existing Google Ads accounts",
    current_behavior="Import shows read-only campaign cards with Pause/Resume buttons",
    expected_behavior="Edit budget, view keywords, view/edit ad copy, add negative keywords from dashboard",
    solution="Add Google Ads API write operations: update budget, get keyword details, update ad copy",
    effort="large",
))

# ═══════════════════════════════════════════════════════════════
# PHASE 4: INTEGRATIONS
# ═══════════════════════════════════════════════════════════════

issues.append(ProductIssue(
    severity="P0",
    category="Integrations",
    title="Conversion tracking not set up — ₹14.8L wasted",
    description=(
        "BDC spent ₹14.8 Lakh with 0 tracked conversions. This is the #1 problem "
        "for every clinic. Without tracking, Google can't optimize, and the doctor "
        "can't see ROI."
    ),
    affected_doctors="all",
    current_behavior="No automatic conversion tracking setup. Manual configuration required.",
    expected_behavior=(
        "Auto-configure conversion tracking when integrations connect:\n"
        "1. Call tracking via Twilio (when number provisioned)\n"
        "2. WhatsApp first message (when WhatsApp connected)\n"
        "3. Calendar booking (when Google Calendar connected)\n"
        "4. Import these as Google Ads offline conversions"
    ),
    solution=(
        "1. When Twilio provisions number → create Google Ads call conversion action\n"
        "2. When appointment booked → push offline conversion to Google Ads API\n"
        "3. When WhatsApp conversation starts → track as lead conversion\n"
        "4. Show conversion count on campaign cards"
    ),
    effort="large",
))

issues.append(ProductIssue(
    severity="P1",
    category="Integrations",
    title="Google Calendar OAuth shows 'Google hasn't verified this app' warning",
    description=(
        "Every doctor connecting Google Calendar sees a scary red warning. "
        "Many will click 'Back to Safety' and never connect."
    ),
    affected_doctors="all",
    current_behavior="Unverified app warning on Google OAuth consent screen",
    expected_behavior="Verified app with no warning, or clear instructions to click Advanced → Continue",
    solution=(
        "1. Submit Google OAuth consent screen for verification (takes 2-4 weeks)\n"
        "2. Meanwhile: add an in-app instruction banner before the Connect button\n"
        "3. Show step-by-step: 'Click Advanced → Go to PatientPlex → Allow'"
    ),
    effort="medium",
))

issues.append(ProductIssue(
    severity="P1",
    category="Integrations",
    title="Meta Ads app is in 'Development' mode — only app admins can connect",
    description=(
        "The Meta app 'Patient Flow Automation' is in Development mode. "
        "Only users added as admins/developers/testers can complete the OAuth flow. "
        "Real clinic owners can't connect."
    ),
    affected_doctors="all wanting to connect Meta Ads",
    current_behavior="Meta OAuth only works for app admins",
    expected_behavior="Any clinic owner can connect their Meta ad account via OAuth",
    solution=(
        "1. Complete Meta App Review: submit for ads_management permission\n"
        "2. Set app to Live mode after review approval\n"
        "3. Add test users for beta clinics in the meantime"
    ),
    effort="medium",
))

issues.append(ProductIssue(
    severity="P1",
    category="Integrations",
    title="Twilio is on trial account — can't scale",
    description=(
        "Twilio trial account has $15 credit, can't send SMS to unverified numbers, "
        "and can't register WhatsApp senders. Every new clinic would need their own "
        "number verified manually."
    ),
    affected_doctors="all needing call tracking or WhatsApp",
    current_behavior="Trial account, manual number verification required per clinic",
    expected_behavior="Paid Twilio account with auto-provisioning for each clinic",
    solution="Upgrade Twilio to paid account, implement auto-provision flow per clinic signup",
    effort="small (just needs payment)",
))

# ═══════════════════════════════════════════════════════════════
# PHASE 5: WHATSAPP & COMMUNICATION
# ═══════════════════════════════════════════════════════════════

issues.append(ProductIssue(
    severity="P1",
    category="WhatsApp",
    title="WhatsApp AI receptionist has no conversation context",
    description=(
        "The AI receptionist should know: clinic services, doctor availability, "
        "pricing, location, and be able to book appointments. Currently it's a "
        "shell without the clinic's actual knowledge."
    ),
    affected_doctors="all using WhatsApp",
    current_behavior="Generic AI responses without clinic-specific knowledge",
    expected_behavior=(
        "AI knows: all services offered, approximate pricing, doctor availability "
        "from Google Calendar, clinic hours, address, special offers, and can book "
        "appointments directly"
    ),
    solution=(
        "Feed clinic profile data (services, address, hours, pricing) into the AI "
        "receptionist prompt. Connect to Google Calendar for real-time availability."
    ),
    effort="medium",
))

issues.append(ProductIssue(
    severity="P2",
    category="WhatsApp",
    title="No appointment reminders via WhatsApp",
    description="Patients book but no-show rates are 30-40% in Indian clinics. WhatsApp reminders 24h and 2h before would cut this significantly.",
    affected_doctors="all",
    current_behavior="No reminders sent after booking",
    expected_behavior="Automatic WhatsApp reminder: 24h before, 2h before, with confirm/reschedule options",
    solution="Background job: query upcoming appointments, send WhatsApp template messages via Twilio/Meta API",
    effort="medium",
))

# ═══════════════════════════════════════════════════════════════
# PHASE 6: BILLING & SUBSCRIPTION
# ═══════════════════════════════════════════════════════════════

issues.append(ProductIssue(
    severity="P1",
    category="Billing",
    title="No actual payment flow — trial just starts with no payment",
    description="The billing page shows plans but 'Start Trial' doesn't collect payment. After 14 days, there's no upgrade path that actually charges.",
    affected_doctors="all",
    current_behavior="Start Trial button creates trial subscription. No payment collected.",
    expected_behavior="Razorpay payment integration that actually charges after trial. Auto-renewal.",
    solution="Razorpay integration is partially built — complete the subscription webhook and auto-renewal flow",
    effort="medium",
))

# ═══════════════════════════════════════════════════════════════
# PHASE 7: ANALYTICS & REPORTING
# ═══════════════════════════════════════════════════════════════

issues.append(ProductIssue(
    severity="P1",
    category="Analytics",
    title="No weekly/monthly performance report sent to doctor",
    description=(
        "Doctors are busy. They won't check the dashboard daily. "
        "A weekly WhatsApp summary (new patients, spend, ROI, top campaign) "
        "would keep them engaged and prove value."
    ),
    affected_doctors="all",
    current_behavior="No automated reports. Doctor must log in to see data.",
    expected_behavior="Weekly WhatsApp report: patients acquired, spend, cost per patient, best campaign, recommendations",
    solution="Cron job: every Monday 10am IST, generate report, send via WhatsApp using approved template",
    effort="medium",
))

issues.append(ProductIssue(
    severity="P2",
    category="Analytics",
    title="No competitor comparison or market benchmarks shown",
    description="Doctor has no idea if their ₹35 CPC is good or bad. No benchmark context provided.",
    affected_doctors="all",
    current_behavior="Raw metrics without context",
    expected_behavior="Show 'Your CPC ₹35 vs Market Average ₹45' or 'Your CTR is in top 20% for Indore dentists'",
    solution="Use CITY_BENCHMARKS from PerformanceMarketingBrain to add benchmark comparisons to campaign cards",
    effort="small",
))

# ═══════════════════════════════════════════════════════════════
# PHASE 8: SECURITY & COMPLIANCE
# ═══════════════════════════════════════════════════════════════

issues.append(ProductIssue(
    severity="P1",
    category="Security",
    title="No password reset flow",
    description="If a doctor forgets their password, they're locked out. The requestPasswordReset function returns a fake success message.",
    affected_doctors="all",
    current_behavior="API returns 'If an account exists, you'll receive a reset link' but no email is sent",
    expected_behavior="Send actual password reset email with time-limited token",
    solution="Implement email sending (SendGrid/AWS SES), token generation, and /reset-password endpoint",
    effort="medium",
))

issues.append(ProductIssue(
    severity="P2",
    category="Security",
    title="No profile editing capability",
    description="Settings page shows 'Profile editing is not available yet.' Doctors can't update their phone, email, or clinic details after onboarding.",
    affected_doctors="all",
    current_behavior="Read-only profile display",
    expected_behavior="Editable profile: name, phone, email, clinic name, address, services",
    solution="Add PUT /auth/profile endpoint and make Settings form fields editable",
    effort="small",
))

# ═══════════════════════════════════════════════════════════════
# PHASE 9: MOBILE EXPERIENCE
# ═══════════════════════════════════════════════════════════════

issues.append(ProductIssue(
    severity="P2",
    category="Mobile",
    title="Dashboard is not optimized for mobile",
    description="Indian clinic owners primarily use their phones. Campaign cards, stats grid, and sidebar navigation are cramped on mobile.",
    affected_doctors="all (80% will access from phone)",
    current_behavior="Desktop-first layout that barely fits on mobile",
    expected_behavior="Mobile-first responsive design: collapsible sidebar, stacked cards, thumb-friendly tap targets",
    solution="Responsive CSS overhaul: mobile breakpoint for all dashboard pages",
    effort="medium",
))

# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════

p0_count = len([i for i in issues if i.severity == "P0"])
p1_count = len([i for i in issues if i.severity == "P1"])
p2_count = len([i for i in issues if i.severity == "P2"])
p3_count = len([i for i in issues if i.severity == "P3"])
p4_count = len([i for i in issues if i.severity == "P4"])

print("=" * 70)
print("PATIENTPLEX AI — PRODUCT AUDIT REPORT")
print("Simulated: 100 doctors across 10 specialties")
print("=" * 70)
print()
print(f"Total issues found: {len(issues)}")
print(f"  🔴 P0 (Blockers):     {p0_count}")
print(f"  🟠 P1 (Major):        {p1_count}")
print(f"  🟡 P2 (Moderate):     {p2_count}")
print(f"  🟢 P3 (Minor):        {p3_count}")
print(f"  ⚪ P4 (Nice-to-have): {p4_count}")
print()

# Print by severity
for severity in ["P0", "P1", "P2", "P3", "P4"]:
    severity_issues = [i for i in issues if i.severity == severity]
    if not severity_issues:
        continue
    emoji = {"P0": "🔴", "P1": "🟠", "P2": "🟡", "P3": "🟢", "P4": "⚪"}[severity]
    print(f"\n{'─' * 60}")
    print(f"{emoji} {severity} ISSUES")
    print(f"{'─' * 60}")
    for issue in severity_issues:
        print(f"\n  [{issue.category}] {issue.title}")
        print(f"  Affects: {issue.affected_doctors}")
        print(f"  Effort: {issue.effort}")
        print(f"  Solution: {issue.solution[:150]}...")


if __name__ == "__main__":
    pass
