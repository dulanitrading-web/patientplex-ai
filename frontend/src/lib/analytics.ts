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
