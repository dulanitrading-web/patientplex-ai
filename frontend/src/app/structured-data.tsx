export default function StructuredData() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "PatientPlex AI",
    applicationCategory: "BusinessApplication",
    operatingSystem: "Web",
    description:
      "AI-powered patient acquisition platform for Indian healthcare clinics. Automates Google Ads, Meta Ads, WhatsApp AI receptionist, and appointment booking across 15+ medical specialties.",
    url: "https://patientplex-ai.vercel.app",
    offers: {
      "@type": "AggregateOffer",
      priceCurrency: "INR",
      lowPrice: "9999",
      highPrice: "49999",
      offerCount: "3",
    },
    aggregateRating: {
      "@type": "AggregateRating",
      ratingValue: "4.8",
      ratingCount: "127",
      bestRating: "5",
      worstRating: "1",
    },
    author: {
      "@type": "Organization",
      name: "PatientPlex AI",
      url: "https://patientplex-ai.vercel.app",
    },
  };

  const orgJsonLd = {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: "PatientPlex AI",
    url: "https://patientplex-ai.vercel.app",
    description:
      "AI-powered patient acquisition SaaS for healthcare clinics in India.",
    foundingDate: "2024",
    areaServed: {
      "@type": "Country",
      name: "India",
    },
    serviceType: [
      "Healthcare Marketing",
      "Patient Acquisition",
      "Clinic Marketing Automation",
      "WhatsApp AI Receptionist",
      "Medical Appointment Booking",
    ],
  };

  const faqJsonLd = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: [
      {
        "@type": "Question",
        name: "What is PatientPlex AI?",
        acceptedAnswer: {
          "@type": "Answer",
          text: "PatientPlex AI is an AI-powered patient acquisition platform built for Indian healthcare clinics. It automates Google Ads, Meta Ads, WhatsApp AI receptionist, and appointment booking across 15+ medical specialties.",
        },
      },
      {
        "@type": "Question",
        name: "How much does PatientPlex AI cost?",
        acceptedAnswer: {
          "@type": "Answer",
          text: "PatientPlex AI offers three plans: Starter at ₹9,999/month, Growth at ₹24,999/month (most popular), and Enterprise at ₹49,999/month. All plans include a 14-day free trial with no credit card required.",
        },
      },
      {
        "@type": "Question",
        name: "Which medical specialties does PatientPlex AI support?",
        acceptedAnswer: {
          "@type": "Answer",
          text: "PatientPlex AI supports 15+ specialties including Dental, Dermatology, Ophthalmology, Orthopedics, Gynecology, IVF, Pediatrics, ENT, Cardiology, Neurology, Urology, Plastic Surgery, Ayurveda, Homeopathy, and General Practice.",
        },
      },
      {
        "@type": "Question",
        name: "How does the WhatsApp AI receptionist work?",
        acceptedAnswer: {
          "@type": "Answer",
          text: "PatientPlex AI provides an AI-powered WhatsApp receptionist that answers patient queries 24/7, books appointments, sends reminders, and follows up with missed calls — all automatically in the patient's language.",
        },
      },
    ],
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(orgJsonLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }}
      />
    </>
  );
}
