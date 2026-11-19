// Google Analytics 4 event tracking utility
export const GA_TRACKING_ID = process.env.NEXT_PUBLIC_GA4_ID;

// Track page views
export const pageview = (url: string) => {
  if (typeof window !== "undefined" && (window as any).gtag) {
    (window as any).gtag("config", GA_TRACKING_ID, {
      page_path: url,
    });
  }
};

// Track custom events
export const event = ({
  action,
  category,
  label,
  value,
}: {
  action: string;
  category: string;
  label?: string;
  value?: number;
}) => {
  if (typeof window !== "undefined" && (window as any).gtag) {
    (window as any).gtag("event", action, {
      event_category: category,
      event_label: label,
      value: value,
    });
  }
};

// Pre-built healthcare marketing events
export const trackLeadCapture = (source: string) =>
  event({ action: "lead_capture", category: "conversion", label: source });

export const trackSignup = () =>
  event({ action: "sign_up", category: "conversion" });

export const trackPricingView = (plan: string) =>
  event({ action: "view_pricing", category: "engagement", label: plan });

export const trackDemoRequest = () =>
  event({ action: "demo_request", category: "conversion" });

export const trackROICalculatorUse = () =>
  event({ action: "roi_calculator", category: "engagement" });

export const trackWhatsAppClick = () =>
  event({ action: "whatsapp_click", category: "engagement" });

export const trackFAQOpen = (question: string) =>
  event({ action: "faq_open", category: "engagement", label: question });

// ---- Booking Funnel Events (Critical for Google Ads optimization) ----

/** Fired when a patient opens the booking page (from ad click) */
export const trackBookingPageView = (doctorSlug: string, source?: string) => {
  event({ action: "booking_page_view", category: "booking_funnel", label: doctorSlug });
  // Google Ads enhanced conversion tracking
  if (typeof window !== "undefined" && (window as any).gtag) {
    (window as any).gtag("event", "page_view", {
      page_title: `Book Appointment - ${doctorSlug}`,
      page_location: window.location.href,
      utm_source: source || new URLSearchParams(window.location.search).get("utm_source") || "direct",
    });
  }
};

/** Fired when patient selects a treatment */
export const trackTreatmentSelected = (treatment: string, doctorSlug: string) =>
  event({ action: "treatment_selected", category: "booking_funnel", label: `${doctorSlug}:${treatment}` });

/** Fired when patient selects a date */
export const trackDateSelected = (date: string, doctorSlug: string) =>
  event({ action: "date_selected", category: "booking_funnel", label: `${doctorSlug}:${date}` });

/** Fired when patient selects a time slot */
export const trackSlotSelected = (time: string, doctorSlug: string) =>
  event({ action: "slot_selected", category: "booking_funnel", label: `${doctorSlug}:${time}` });

/** Fired when patient submits booking — THIS IS THE CONVERSION EVENT */
export const trackBookingCompleted = (doctorSlug: string, treatment: string) => {
  // GA4 event
  event({ action: "booking_completed", category: "conversion", label: `${doctorSlug}:${treatment}`, value: 1 });

  // Google Ads Conversion — this is what Google Ads optimizes for
  if (typeof window !== "undefined" && (window as any).gtag) {
    (window as any).gtag("event", "conversion", {
      send_to: "AW-CONVERSION_ID/CONVERSION_LABEL", // Will be replaced with actual values
      event_callback: () => {},
    });
    // Also fire as a "generate_lead" event for GA4
    (window as any).gtag("event", "generate_lead", {
      currency: "INR",
      value: 500, // Average lead value
      event_label: treatment,
    });
  }
};

/** Fired when patient starts filling their details form */
export const trackFormStarted = (doctorSlug: string) =>
  event({ action: "form_started", category: "booking_funnel", label: doctorSlug });

/** Track WhatsApp click on booking page */
export const trackBookingWhatsAppClick = (doctorSlug: string) =>
  event({ action: "booking_whatsapp_click", category: "conversion", label: doctorSlug });

/** Track phone call click on booking page */
export const trackBookingCallClick = (doctorSlug: string) =>
  event({ action: "booking_call_click", category: "conversion", label: doctorSlug });
