"""Clinic Knowledge Base — the brain behind every AI interaction.

Contains everything the AI receptionist needs to know about each clinic:
treatments, pricing, doctors, timings, FAQs, scripts, and objection handling.

This powers:
- WhatsApp AI auto-replies
- Exotel IVR greetings and call routing
- Missed call recovery messages
- Lead capture form responses
- Doctor notification summaries
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Treatment:
    name: str
    name_hindi: str
    min_price: int
    max_price: int
    duration_minutes: int
    description: str
    benefits: List[str]
    faq: Dict[str, str]
    keywords: List[str]  # What patients might say


@dataclass
class ClinicProfile:
    clinic_name: str
    doctor_names: List[str]
    specialty: str
    tagline: str
    address: str
    city: str
    phone: str
    whatsapp: str
    timings: str
    closed_on: str
    google_maps_link: str
    treatments: List[Treatment]
    usp: List[str]  # Unique selling points
    faq: Dict[str, str]
    greeting_script: str
    missed_call_script: str
    follow_up_script: str
    objection_handling: Dict[str, str]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BHARDWAJ DENTAL CLINIC — Complete Knowledge Base
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BDC_TREATMENTS = [
    Treatment(
        name="Root Canal Treatment (RCT)",
        name_hindi="रूट कैनाल",
        min_price=5000,
        max_price=12000,
        duration_minutes=60,
        description="Painless single-sitting root canal treatment using rotary endodontics. Saves your natural tooth from extraction.",
        benefits=["Painless procedure", "Single sitting possible", "Save natural tooth", "German rotary instruments"],
        faq={
            "Does it hurt?": "No, we use advanced anesthesia. Most patients say they felt nothing during the procedure. We also offer sedation for anxious patients.",
            "How many sittings?": "Most cases done in a single sitting (1-2 hours). Complex cases may need 2 sittings.",
            "How long does it last?": "A properly done RCT with a good crown can last 15-20 years or even a lifetime with proper care.",
            "Do I need a cap after RCT?": "Yes, a dental crown (cap) is recommended after RCT to protect the tooth. We offer zirconia, PFM, and metal-free options.",
        },
        keywords=["root canal", "rct", "toothache", "tooth pain", "dard", "dant dard", "nerve treatment", "daant mein dard"],
    ),
    Treatment(
        name="Braces / Orthodontic Treatment",
        name_hindi="ब्रेसेज / तार",
        min_price=25000,
        max_price=60000,
        duration_minutes=45,
        description="Complete teeth alignment with metal braces, ceramic braces, or clear aligners. Transform your smile in 12-18 months.",
        benefits=["Free consultation", "0% EMI available", "Metal & ceramic options", "Clear aligners available"],
        faq={
            "How long does treatment take?": "Typically 12-18 months depending on the case. Some minor cases can be done in 6-8 months.",
            "Which type is best?": "Metal braces are most effective and affordable. Ceramic braces are less visible. Clear aligners are invisible but cost more.",
            "Is it painful?": "Mild discomfort for 3-5 days after adjustment. We provide wax and tips to manage it easily.",
            "What age is best?": "Braces work at any age! We treat patients from 12 to 60+ years.",
            "EMI available?": "Yes! 0% EMI available for 6-12 months. We also accept all major credit cards.",
        },
        keywords=["braces", "tedhe daant", "teeth alignment", "taar", "orthodontic", "clear aligner", "invisible braces"],
    ),
    Treatment(
        name="Teeth Cleaning & Polishing",
        name_hindi="दांत साफ करना / स्केलिंग",
        min_price=800,
        max_price=2500,
        duration_minutes=30,
        description="Professional scaling and polishing to remove tartar, stains, and plaque. Prevents gum disease and keeps your smile bright.",
        benefits=["30-minute procedure", "Removes tobacco/tea stains", "Prevents gum disease", "Recommended every 6 months"],
        faq={
            "Does it weaken teeth?": "No! This is a myth. Professional cleaning actually protects your teeth by removing harmful deposits.",
            "How often should I get it done?": "Every 6 months is ideal. If you smoke or chew tobacco, every 3-4 months.",
            "Will stains come back?": "They can if you consume a lot of tea/coffee/tobacco. Regular cleaning keeps them away.",
        },
        keywords=["cleaning", "scaling", "polish", "safai", "daag", "stain", "yellowing", "peele daant"],
    ),
    Treatment(
        name="Teeth Whitening",
        name_hindi="दांत सफेद करना",
        min_price=5000,
        max_price=15000,
        duration_minutes=60,
        description="Professional in-office teeth whitening that brightens your smile by 5-8 shades in just one hour. Safe and long-lasting.",
        benefits=["Results in 1 hour", "5-8 shades brighter", "Safe LED technology", "Lasts 1-2 years"],
        faq={
            "Is it safe?": "Yes, we use dentist-grade whitening gel with LED activation. Much safer than home remedies.",
            "How long does it last?": "Results last 1-2 years with proper care. Avoid excessive tea/coffee/smoking for best results.",
        },
        keywords=["whitening", "white teeth", "safed daant", "bleaching", "bright smile"],
    ),
    Treatment(
        name="Dental Implants",
        name_hindi="दांत का इम्प्लांट",
        min_price=25000,
        max_price=80000,
        duration_minutes=90,
        description="Permanent tooth replacement with titanium implants. Looks, feels, and functions like a natural tooth. Lifetime solution.",
        benefits=["Lifetime solution", "Looks like natural tooth", "Korean/German implants", "Free 3D CT scan"],
        faq={
            "Is it painful?": "Done under local anesthesia — you won't feel pain during the procedure. Mild soreness for 2-3 days after.",
            "How long does it take?": "The implant is placed in 30-45 minutes. The final crown goes on after 3-4 months of healing.",
            "Is it permanent?": "Yes! Dental implants are designed to last a lifetime with proper oral hygiene.",
            "What if I don't have enough bone?": "We offer bone grafting procedures. Many patients who were told 'no' elsewhere get successful implants here.",
        },
        keywords=["implant", "missing tooth", "toota daant", "replacement", "naqli daant", "permanent tooth"],
    ),
    Treatment(
        name="Crowns & Bridges",
        name_hindi="कैप और ब्रिज",
        min_price=3000,
        max_price=20000,
        duration_minutes=45,
        description="Dental caps (crowns) to protect damaged teeth and bridges to replace missing teeth. Zirconia, PFM, and metal-free options.",
        benefits=["Same-day temporary cap", "Natural appearance", "Zirconia/Metal-free options", "5-year warranty"],
        faq={
            "Which material is best?": "Zirconia is the gold standard — metal-free, natural-looking, and extremely strong. PFM is a budget-friendly option.",
            "How long do crowns last?": "Zirconia crowns last 15-20 years. PFM crowns last 10-15 years with proper care.",
        },
        keywords=["crown", "cap", "bridge", "topi", "broken tooth", "toota daant"],
    ),
    Treatment(
        name="Clear Aligners (Invisible Braces)",
        name_hindi="क्लियर अलाइनर",
        min_price=50000,
        max_price=150000,
        duration_minutes=30,
        description="Invisible teeth straightening with custom-made clear trays. No metal, no wires — just a beautiful smile transformation.",
        benefits=["Completely invisible", "Removable for eating", "No food restrictions", "Faster than traditional braces"],
        faq={
            "Are they really invisible?": "Yes! Clear aligners are virtually invisible. Most people won't even notice you're wearing them.",
            "How long does treatment take?": "Typically 6-14 months, faster than traditional braces for most cases.",
        },
        keywords=["aligner", "invisible", "clear braces", "no wire", "bina taar"],
    ),
    Treatment(
        name="Wisdom Tooth Extraction",
        name_hindi="अक्ल दाढ़ निकालना",
        min_price=2000,
        max_price=8000,
        duration_minutes=45,
        description="Safe and painless wisdom tooth removal by experienced oral surgeons. Impacted, partially erupted, or problematic wisdom teeth.",
        benefits=["Painless extraction", "Experienced surgeon", "Quick recovery", "Stitch removal in 7 days"],
        faq={
            "Is it painful?": "No, done under local anesthesia. You might feel pressure but no pain. We prescribe painkillers for 2-3 days after.",
            "Will my face swell?": "Some swelling is normal for 2-3 days. Ice packs and medication control it well.",
        },
        keywords=["wisdom tooth", "akkal daadh", "extraction", "daant nikalna", "swelling"],
    ),
    Treatment(
        name="Gum Treatment (Periodontics)",
        name_hindi="मसूड़ों का इलाज",
        min_price=3000,
        max_price=15000,
        duration_minutes=45,
        description="Treatment for bleeding gums, gum recession, and periodontal disease. Flap surgery, laser treatment, and gum grafting available.",
        benefits=["Laser treatment available", "Stop bleeding gums", "Prevent tooth loss", "Painless procedures"],
        faq={
            "Why do my gums bleed?": "Bleeding gums indicate gum disease (gingivitis/periodontitis). It's treatable but shouldn't be ignored.",
            "Can I lose teeth from gum disease?": "Yes, untreated gum disease is the #1 cause of tooth loss in adults. Early treatment can save all your teeth.",
        },
        keywords=["gum", "bleeding", "masude", "khoon", "loose tooth", "hilta daant"],
    ),
    Treatment(
        name="Smile Makeover",
        name_hindi="स्माइल मेकओवर",
        min_price=30000,
        max_price=200000,
        duration_minutes=90,
        description="Complete smile transformation combining veneers, whitening, crowns, and alignment. Custom-designed for your face shape.",
        benefits=["Complete transformation", "Custom digital design", "Before/after preview", "Celebrity-grade results"],
        faq={
            "What's included?": "Depends on your case — could include veneers, whitening, crowns, or aligners. We create a custom plan after examination.",
            "How long does it take?": "Simple makeovers take 2-3 visits. Complex cases may take a few weeks.",
        },
        keywords=["smile", "makeover", "cosmetic", "veneers", "sundar daant", "muskaan"],
    ),
    Treatment(
        name="Kids Dentistry (Pedodontics)",
        name_hindi="बच्चों के दांतों का इलाज",
        min_price=500,
        max_price=5000,
        duration_minutes=30,
        description="Gentle and child-friendly dental care. Cavity fillings, fluoride application, sealants, and space maintainers.",
        benefits=["Child-friendly clinic", "Painless fillings", "Fluoride treatment", "Fun dental visits"],
        faq={
            "At what age should I bring my child?": "First visit by age 1, or when the first tooth appears. Regular checkups from age 3.",
            "My child is scared of dentists": "We specialize in making dental visits fun! Our team is trained in pediatric behavior management.",
        },
        keywords=["kids", "child", "baby teeth", "bacche", "doodh ke daant", "cavity"],
    ),
]


BDC_PROFILE = ClinicProfile(
    clinic_name="Bhardwaj Dental Clinic",
    doctor_names=[
        "Dr. Amit Bhardwaj — Orthodontist (BDS, MDS Orthodontics, 26 yrs exp, World Federation of Orthodontists member) — Braces, Aligners, Jaw Correction",
        "Dr. Anuj Bhardwaj — Endodontist & Cosmetic Dentist (BDS, MDS, Diplomate Indian Board of Endodontics, RCPS Glasgow, 20 yrs exp, Director) — Root Canal, Smile Design, Cosmetic Fillings",
        "Dr. Shivani Bhardwaj — Prosthodontist (MDS, BDS, Topper in MDS) — Crowns, Bridges, Dentures, Implants",
        "Dr. Kratika Mishra — Orthodontist (BDS, MDS Orthodontics) — Invisible/Clear Braces, Fixed Orthodontics",
        "Dr. Vihang Naphade — Oral Medicine Specialist (MDS Oral Medicine & Radiology) — TMJ, Craniofacial Pain, Oral Diagnosis",
    ],
    specialty="Multi-specialty Dental Clinic — Orthodontics, Endodontics, Cosmetic, Prosthodontics, Oral Medicine",
    tagline="Indore's Most Trusted Dental Clinic — 20+ Years of Excellence",
    address="LG 9-11, The Horizon 11/5, Nath Mandir Road, South Tukoganj, Indore 452001 (Near Hotel Kalinga)",
    city="Indore",
    phone="9424488558",
    whatsapp="9424488558",
    timings="Mon-Sat: 10:00 AM - 2:00 PM, 5:00 PM - 8:30 PM",
    closed_on="Sunday",
    google_maps_link="https://maps.google.com/?q=Bhardwaj+Dental+Clinic+Indore",
    treatments=BDC_TREATMENTS,
    usp=[
        "5 specialist doctors under one roof",
        "20+ years of experience — established since 2004",
        "Award-winning — Outstanding Endodontist of the Year, Excellence in Microdentistry",
        "International credentials — RCPS Glasgow, Adjunct Faculty Indonesia",
        "478+ happy patients on Practo, 98% recommendation rate",
        "Painless treatments with latest technology",
        "Male and female dentists available",
        "Near Hotel Kalinga, South Tukoganj — easy to reach",
    ],
    faq={
        "Where is the clinic?": "LG 9-11, The Horizon building, Nath Mandir Road, South Tukoganj, Indore. Near Hotel Kalinga.",
        "What are the timings?": "Monday to Saturday: 10 AM - 2 PM and 5 PM - 8:30 PM. Sunday closed.",
        "Do you treat emergencies?": "Haan ji! Dental emergency mein same day dekhte hain — call karein 9424488558.",
        "Which doctor should I see?": "Humari team mein har specialty ke doctor hain — aapki problem batayein, hum sahi doctor se milwayenge.",
        "Is parking available?": "Haan, building ke saamne road parking available hai. Nath Mandir Road pe hai, aasani se pahunch sakte hain.",
    },
    greeting_script=(
        "Namaste! Bhardwaj Dental Clinic, Indore mein aapka swagat hai. "
        "Appointment ke liye 1 dabayein. Treatment ki jaankari ke liye 2 dabayein. "
        "Humari team se baat karne ke liye hold karein."
    ),
    missed_call_script=(
        "Namaste! 🙏 Aapne abhi Bhardwaj Dental Clinic pe call kiya tha — "
        "sorry hum pick nahi kar paaye.\n\n"
        "Main Riya hoon, Bhardwaj Dental Clinic ki assistant. "
        "Aapka appointment abhi book kar sakti hoon!\n\n"
        "Aapko kaunsi treatment chahiye? Batayein — main available slots check kar leti hoon. 😊\n\n"
        "📍 Nath Mandir Rd, South Tukoganj, Indore\n"
        "🕐 Mon-Sat 10AM-2PM, 5PM-9PM\n"
        "📞 9424488558"
    ),
    follow_up_script=(
        "Hi {patient_name}! 👋\n\n"
        "Aapne {days_ago} din pehle Bhardwaj Dental Clinic mein {treatment} ke baare mein enquiry ki thi.\n\n"
        "Kya aap appointment book karna chahenge? "
        "Abhi {available_slot} ka slot available hai.\n\n"
        "Reply karein ya call karein: 9424488558 📞"
    ),
    objection_handling={
        "too expensive": "Main samajh sakti hoon. Jab aap clinic aayenge toh doctor aapko poori jaankari denge treatment aur cost ke baare mein. EMI option bhi available hai. Pehle check-up toh karwa lijiye!",
        "need to think": "Bilkul! Aap apna time lein. Bas yaad rakhein — dental problems delay karne se worse hoti hain. Check-up ke liye koi commitment nahi hai, aap aake dekh sakte hain.",
        "afraid of pain": "Aapki chinta bilkul valid hai! Humare doctors advanced painless techniques use karte hain. 478 se zyada patients ne Practo pe 98% rating di hai — aap clinic aake experience karein.",
        "will come later": "Sure! Kab aana chahenge? Main abhi slot book kar deti hoon taaki aapko wait na karna pade. Hum reminder bhi bhej denge.",
        "how much / kitna lagega": "Cost toh doctor examination ke baad hi bata payenge — har case different hota hai. Aap clinic aayein, doctor check karenge aur poori jaankari denge. Main appointment book kar doon?",
        "other clinic is cheaper": "Bilkul samajh sakti hoon. Humare paas 5 specialist doctors hain, 20+ saal ka experience, international training. Aap ek baar aake clinic dekh lijiye — quality khud samajh aa jayegi.",
        "no time": "Hum 10AM se 8:30PM tak open hain! Evening slots bhi available hain working professionals ke liye. Main aapke hisaab se slot dhundh deti hoon.",
    },
)


def get_clinic_knowledge(clinic_name: str = "Bhardwaj Dental Clinic") -> ClinicProfile:
    """Get the knowledge base for a clinic.

    Currently returns BDC profile. In future, this will look up
    the clinic from the database based on the doctor's profile.
    """
    return BDC_PROFILE


def build_ai_system_prompt(clinic: ClinicProfile) -> str:
    """Build the complete AI receptionist system prompt from clinic knowledge."""

    treatment_list = ""
    for t in clinic.treatments:
        treatment_list += f"\n### {t.name} ({t.name_hindi})\n"
        # NOTE: Prices intentionally excluded — business rule prohibits sharing pricing
        treatment_list += f"- **Pricing**: Doctor will discuss after examination (har case alag hota hai)\n"
        treatment_list += f"- **Duration**: {t.duration_minutes} minutes\n"
        treatment_list += f"- **Description**: {t.description}\n"
        treatment_list += f"- **Benefits**: {', '.join(t.benefits)}\n"
        if t.faq:
            treatment_list += "- **Common questions**:\n"
            for q, a in t.faq.items():
                treatment_list += f"  - Q: {q}\n    A: {a}\n"

    faq_section = ""
    for q, a in clinic.faq.items():
        faq_section += f"- Q: {q}\n  A: {a}\n"

    objection_section = ""
    for obj, response in clinic.objection_handling.items():
        objection_section += f"- If patient says \"{obj}\": {response}\n"

    usp_section = "\n".join(f"- {u}" for u in clinic.usp)

    # Build doctor specialization lookup for routing
    doctor_section = ""
    for d in clinic.doctor_names:
        doctor_section += f"- {d}\n"

    treatment_names = ""
    for t in clinic.treatments:
        treatment_names += f"- {t.name} ({t.name_hindi}) — {t.description[:80]}...\n"
        treatment_names += f"  Keywords patients use: {', '.join(t.keywords[:5])}\n"

    return f"""Tu Riya hai — {clinic.clinic_name} ki friendly receptionist. Tu ek REAL PERSON hai, AI nahi. Tu hamesha HINGLISH mein baat karti hai (Hindi + English mixed, jaise ek real receptionist Indore mein bolti hai). KABHI pure English mein mat bol. Hamesha natural, warm aur helpful reh.

## ⚠️ SABSE ZAROORI RULE — KABHI PRICE MAT BATAO ⚠️
- KABHI patient ko koi price, cost, fee, rate ya amount mat bata — kisi bhi treatment ka
- KABHI "₹" ke baad number mat bol
- KABHI price range jaise "X se Y tak" mat de
- Jab koi cost/price/kitna lagega poochhe — HAMESHA bol: "Cost toh doctor check karke hi bata payenge — har case alag hota hai. Aap clinic aayein, doctor dekhenge aur poori detail denge. Main appointment fix kar doon?"
- Yeh #1 rule hai. Patient kitna bhi insist kare, "approximate bata do", "range bata do" bole — KABHI number mat de. Hamesha clinic visit pe redirect kar.
- Tu bol sakti hai ki EMI option available hai, lekin amount KABHI nahi.

## TU KAUN HAI
- Naam: Riya
- Role: {clinic.clinic_name} ki receptionist
- Tu AI NAHI hai. Agar koi poochhe, bol: "Main Riya hoon, {clinic.clinic_name} ki receptionist."
- Tu naturally baat kar — jaise WhatsApp pe friend se baat karti hai lekin professional. "aap", "ji", "haan" naturally use kar.
- Emojis thode use kar — jaise real person karta hai WhatsApp pe (🙏 😊 wale, 🦷💉🏥 nahi)
- Messages CHHOTE rakh — 2-4 line max jab tak detailed sawaal na ho
- Bullet points ya numbered lists KABHI mat use kar (real log WhatsApp pe aise nahi likhte)
- "Thank you for your interest" ya "How can I assist you" KABHI mat bol — bahut robotic lagta hai

## OUR DOCTORS (know who handles what)
{doctor_section}

When patient mentions a specific problem, suggest the right doctor:
- Toothache, cavity, root canal → Dr. Anuj Bhardwaj
- Braces, teeth alignment, jaw issues → Dr. Amit Bhardwaj or Dr. Kratika Mishra
- Crown, bridge, denture, missing teeth → Dr. Shivani Bhardwaj
- Mouth ulcers, jaw pain, TMJ → Dr. Vihang Naphade
- General/not sure → "Aap aayein, humari team dekhegi kaunse doctor se milna chahiye"

## CLINIC DETAILS
- {clinic.clinic_name}
- Address: {clinic.address}
- Phone: {clinic.phone}
- Timings: {clinic.timings}
- Closed: {clinic.closed_on}
- 5 specialist doctors, 20+ years experience
- 478+ patients on Practo, 98% recommend us

## TREATMENTS WE OFFER (names only — NO prices)
{treatment_names}

## AISE BAAT KAR (real conversation ke examples)

**Patient: "Hi"**
Riya: "Namaste! 🙏 Bhardwaj Dental Clinic mein aapka swagat hai. Main Riya hoon, clinic ki assistant. Kaise help karun?"

**Patient: "mujhe daat mein dard ho raha hai"**
Riya: "Arey, daat mein dard bahut mushkil hota hai 😟 Aap ek baar clinic aayiye na, Dr. Anuj dekhenge — woh endodontist hain, root canal mein expert hain. Aaj ka time suitable hai aapke liye?"

**Patient: "braces ka cost kitna hai?"**
Riya: "Braces ka cost toh doctor examine karke hi bata payenge — har case mein treatment plan alag hota hai na. Aap clinic visit kariye, Dr. Amit ya Dr. Kratika — dono orthodontist hain — woh dekhenge aur poora plan batayenge 😊"

**Patient: "clinic kab khulta hai?"**
Riya: "Monday se Saturday: subah 10 baje se 2 baje tak aur shaam 5 baje se 8:30 baje tak. Sunday ko clinic band rehta hai. Aap kab aana chahenge? 📅"

**Patient: "teeth cleaning karwani hai kitne ka hoga"**
Riya: "Cleaning ke liye aap aayein, doctor check karke batayenge — 30 minute mein ho jaati hai. Kal ka slot doon ya aaj evening ka?"

**Patient: "location kahan hai?"**
Riya: "Hum South Tukoganj mein hain — Nath Mandir Road pe, Hotel Kalinga ke paas. The Horizon building, lower ground floor. Easily mil jayega! Kab aana hai?"

**Patient: "Sunday open ho?"**
Riya: "Sunday toh chutti hoti hai 😊 Monday se Saturday open hain — subah 10 se 2, shaam 5 se 8:30. Kaunsa din suit karega?"

**Patient: "implant ka kya rate hai?"**
Riya: "Implant ke liye pehle Dr. Shivani ko dikhana hoga — woh check karke poori detail denge. Har case alag hota hai na. Aap kab aa sakte hain? Main appointment fix kar deti hoon 😊"

## BAAT KARNE KE RULES
1. Hamesha real person jaisi baat kar — chatbot jaisa KABHI mat bol
2. Patient ka naam use kar jab pata ho
3. KABHI medical advice ya diagnosis mat de — bol "Doctor dekhenge"
4. KABHI koi price/cost/fee mat bata — bol "Clinic aake doctor batayenge"
5. Hamesha appointment ki taraf le ja — yahi tera kaam hai
6. Agar patient date/time bata de, confirm kar aur naam + phone poochh
7. Booking ke baad bol: "Done ji! Aapka appointment fix ho gaya — [din] [time] ko. Hum reminder bhej denge 😊"
8. Agar patient rude ho, professional reh: "Ji, main clinic ki receptionist hoon. Appointment ya treatment ke liye help kar sakti hoon."
9. Agar kuch nahi pata: "Yeh main doctor se puchh ke batati hoon. Tab tak appointment fix kar doon?"
10. Emergency ke liye: "Turant clinic aayiye ya 108 pe call karein"
11. HAMESHA Hinglish mein bol — KABHI pure English mein mat bol

## OBJECTION HANDLING
{objection_section}
"""


def get_exotel_ivr_greeting(clinic: ClinicProfile) -> str:
    """Generate the Exotel IVR greeting script — Hinglish."""
    return (
        f"Namaste! {clinic.clinic_name} mein aapka swagat hai. "
        f"Aapki call connect ho rahi hai, please hold karein. "
        f"Agar hum call nahi utha paaye, toh hum aapko WhatsApp pe message karenge."
    )


def get_exotel_after_hours_greeting(clinic: ClinicProfile) -> str:
    """Greeting when calling outside clinic hours — Hinglish."""
    return (
        f"{clinic.clinic_name} mein call karne ke liye dhanyavaad. "
        f"Humara clinic timing hai {clinic.timings}. Abhi clinic band hai. "
        f"Hum aapko WhatsApp pe message karenge appointment book karne ke liye. "
        f"Emergency ke liye nearest hospital jayein. Dhanyavaad!"
    )


def get_call_summary_prompt(clinic: ClinicProfile) -> str:
    """Prompt for summarizing a recorded call — extracts key info."""
    return f"""Summarize this phone call to {clinic.clinic_name} in a structured format:

1. **Patient Name**: (if mentioned)
2. **Phone Number**: (caller number)
3. **Treatment Interest**: (what they asked about)
4. **Key Concerns**: (pain, cost, timing, etc.)
5. **Action Required**: (needs callback, wants to book, needs pricing, etc.)
6. **Keywords**: (comma-separated relevant keywords for tagging)
7. **Priority**: (HIGH if in pain/emergency, MEDIUM if interested, LOW if just enquiring)
8. **Suggested Follow-up**: (what to do next)

Keep it concise — this goes to the doctor's dashboard."""
