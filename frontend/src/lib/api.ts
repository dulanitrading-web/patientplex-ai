const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class ApiError extends Error {
  status: number;
  data: Record<string, unknown>;

  constructor(status: number, data: Record<string, unknown>) {
    super(data.detail as string || "Something went wrong");
    this.status = status;
    this.data = data;
  }
}

async function fetchWithAuth(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("pp_token") : null;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${url}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    // 401 = token expired or invalid → clear auth and redirect to login
    if (response.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("pp_token");
      document.cookie = "pp_token=; path=/; max-age=0";
      // Only redirect if we're not already on login/signup
      if (!window.location.pathname.startsWith("/login") && !window.location.pathname.startsWith("/signup")) {
        window.location.href = "/login?expired=1";
        // Return a never-resolving promise so callers don't try to use the response
        return new Promise<Response>(() => {});
      }
    }

    let data: Record<string, unknown> = {};
    try {
      data = await response.json();
    } catch {
      data = { detail: response.statusText };
    }
    throw new ApiError(response.status, data);
  }

  return response;
}

// Auth
export async function signup(data: {
  full_name: string;
  email: string;
  phone: string;
  password: string;
}) {
  const res = await fetchWithAuth("/auth/signup", {
    method: "POST",
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function login(email: string, password: string) {
  const res = await fetchWithAuth("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  return res.json();
}

// Onboarding
export async function getOnboardingStatus() {
  const res = await fetchWithAuth("/onboarding/status");
  return res.json();
}

export async function updateStep1(data: {
  specialty: string;
  services: string[];
  clinic_name?: string;
}) {
  const res = await fetchWithAuth("/onboarding/step1", {
    method: "PUT",
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function updateStep2(data: {
  clinic_name?: string;
  clinic_address: string;
  city: string;
  state: string;
  pincode: string;
  geo_radius_km: number;
}) {
  const res = await fetchWithAuth("/onboarding/step2", {
    method: "PUT",
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function updateStep3(data: { monthly_budget: number }) {
  const res = await fetchWithAuth("/onboarding/step3", {
    method: "PUT",
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function updateStep4(data: {
  whatsapp_number: string;
  google_calendar_connected?: boolean;
}) {
  const res = await fetchWithAuth("/onboarding/step4", {
    method: "PUT",
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function getSpecialties() {
  const res = await fetchWithAuth("/onboarding/specialties");
  return res.json();
}

export async function getGoogleCalendarUrl() {
  const res = await fetchWithAuth("/onboarding/google-calendar/connect");
  return res.json();
}

export async function completeOnboarding() {
  const res = await fetchWithAuth("/onboarding/complete", {
    method: "POST",
  });
  return res.json();
}

// Campaigns
export async function launchCampaigns(platforms: string[] = ["GOOGLE", "META"]) {
  const res = await fetchWithAuth("/campaigns/launch", {
    method: "POST",
    body: JSON.stringify({ platforms }),
  });
  return res.json();
}

export async function getCampaigns() {
  const res = await fetchWithAuth("/campaigns/");
  return res.json();
}

export async function getCampaignOverview() {
  const res = await fetchWithAuth("/campaigns/overview/stats");
  return res.json();
}

export async function pauseCampaign(id: string) {
  const res = await fetchWithAuth(`/campaigns/${id}/pause`, { method: "PUT" });
  return res.json();
}

export async function resumeCampaign(id: string) {
  const res = await fetchWithAuth(`/campaigns/${id}/resume`, { method: "PUT" });
  return res.json();
}

// Appointments
export async function getAppointments(params?: { date_from?: string; date_to?: string; status?: string }) {
  const query = params ? "?" + new URLSearchParams(params as Record<string, string>).toString() : "";
  const res = await fetchWithAuth(`/appointments/${query}`);
  return res.json();
}

export async function getTodayAppointments() {
  const res = await fetchWithAuth("/appointments/today");
  return res.json();
}

export async function getAppointmentStats(days = 30) {
  const res = await fetchWithAuth(`/appointments/stats?days=${days}`);
  return res.json();
}

export async function updateAppointmentStatus(id: string, status: string, notes?: string) {
  const res = await fetchWithAuth(`/appointments/${id}/status`, {
    method: "PUT",
    body: JSON.stringify({ status, notes }),
  });
  return res.json();
}

// Conversations
export async function getConversations(status?: string) {
  const query = status ? `?status=${status}` : "";
  const res = await fetchWithAuth(`/whatsapp/conversations${query}`);
  return res.json();
}

export async function getConversation(id: string) {
  const res = await fetchWithAuth(`/whatsapp/conversations/${id}`);
  return res.json();
}

// Landing Pages
export async function generateLandingPage() {
  const res = await fetchWithAuth("/landing/generate", { method: "POST" });
  return res.json();
}

export async function getLandingPages() {
  const res = await fetchWithAuth("/landing/pages");
  return res.json();
}

// Doctor profile
export async function getMe() {
  const res = await fetchWithAuth("/auth/me");
  return res.json();
}

export async function getIntegrationStatus() {
  const res = await fetchWithAuth("/auth/integrations");
  return res.json();
}

// Call Logs
export async function getCallStats(days = 30) {
  const res = await fetchWithAuth(`/calls/stats?days=${days}`);
  return res.json();
}

export async function getCallLogs(status?: string, limit = 50, offset = 0) {
  const params = new URLSearchParams();
  if (status && status !== "ALL") params.set("status", status);
  params.set("limit", String(limit));
  params.set("offset", String(offset));
  const res = await fetchWithAuth(`/calls/logs?${params.toString()}`);
  return res.json();
}

// Conversions / Funnel
export async function getConversionFunnel(days?: number) {
  const params = days ? `?days=${days}` : "";
  const res = await fetchWithAuth(`/conversions/funnel${params}`);
  return res.json();
}

export async function getConversionAttribution(days?: number) {
  const params = days ? `?days=${days}` : "";
  const res = await fetchWithAuth(`/conversions/attribution${params}`);
  return res.json();
}

// Billing
export async function getSubscription() {
  const res = await fetchWithAuth("/billing/subscription");
  return res.json();
}

export async function getBillingPlans() {
  const res = await fetchWithAuth("/billing/plans");
  return res.json();
}

export async function startTrial() {
  const res = await fetchWithAuth("/billing/start-trial", { method: "POST" });
  return res.json();
}

// Integrations — connect ad accounts
export async function connectGoogleAds() {
  const res = await fetchWithAuth("/integrations/google-ads/connect");
  return res.json();
}

export async function disconnectGoogleAds() {
  const res = await fetchWithAuth("/integrations/google-ads/disconnect", { method: "POST" });
  return res.json();
}

export async function connectMetaAds() {
  const res = await fetchWithAuth("/integrations/meta-ads/connect");
  return res.json();
}

export async function disconnectMetaAds() {
  const res = await fetchWithAuth("/integrations/meta-ads/disconnect", { method: "POST" });
  return res.json();
}

export async function verifyWhatsApp() {
  const res = await fetchWithAuth("/integrations/whatsapp/verify", { method: "POST" });
  return res.json();
}

// Google Ads — Import existing campaigns
export async function importGoogleAdsCampaigns() {
  const res = await fetchWithAuth("/integrations/google-ads/import-campaigns", { method: "POST" });
  return res.json();
}

// Twilio — Provision tracking number
export async function provisionTwilioNumber() {
  const res = await fetchWithAuth("/integrations/twilio/provision", { method: "POST" });
  return res.json();
}

export async function getTwilioStatus() {
  const res = await fetchWithAuth("/integrations/twilio/status");
  return res.json();
}

// Razorpay Payments
export async function createRazorpayOrder(plan: string) {
  const res = await fetchWithAuth("/integrations/razorpay/create-order", {
    method: "POST",
    body: JSON.stringify({ plan }),
  });
  return res.json();
}

export async function verifyRazorpayPayment(data: {
  razorpay_payment_id: string;
  razorpay_order_id: string;
  razorpay_signature: string;
}) {
  const res = await fetchWithAuth("/integrations/razorpay/verify", {
    method: "POST",
    body: JSON.stringify(data),
  });
  return res.json();
}

// Profile update
export async function updateProfile(data: {
  full_name?: string;
  phone?: string;
  clinic_name?: string;
  clinic_address?: string;
  city?: string;
  state?: string;
  pincode?: string;
  services?: string[];
  monthly_budget?: number;
}) {
  const res = await fetchWithAuth("/auth/profile", {
    method: "PUT",
    body: JSON.stringify(data),
  });
  return res.json();
}

// Password Reset
export async function requestPasswordReset(email: string) {
  const res = await fetchWithAuth("/auth/forgot-password", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
  return res.json();
}

// Conversion Summary (doctor-friendly metrics)
export async function getConversionSummary(days = 30) {
  const res = await fetchWithAuth(`/conversions/summary?days=${days}`);
  return res.json();
}

// Marketing Brain Audit
export async function getAccountAudit() {
  const res = await fetchWithAuth("/marketing-brain/audit");
  return res.json();
}

// Smart Budget Allocation
export async function getSmartBudget() {
  const res = await fetchWithAuth("/marketing-brain/smart-budget", { method: "POST" });
  return res.json();
}

// AI Campaign Intelligence
export async function getAIIntelligence() {
  const res = await fetchWithAuth("/marketing-brain/intelligence");
  return res.json();
}

// Re-sync all Google Ads campaigns with fresh API data
export async function resyncGoogleAdsCampaigns() {
  const res = await fetchWithAuth("/integrations/google-ads/resync-all", { method: "POST" });
  return res.json();
}

// Update campaign budget
export async function updateCampaignBudget(campaignId: string, dailyBudget: number) {
  const res = await fetchWithAuth(`/campaigns/${campaignId}/budget`, {
    method: "PUT",
    body: JSON.stringify({ daily_budget: dailyBudget }),
  });
  return res.json();
}

// Update campaign keywords
export async function updateCampaignKeywords(campaignId: string, add: string[] = [], remove: string[] = []) {
  const res = await fetchWithAuth(`/campaigns/${campaignId}/keywords`, {
    method: "PUT",
    body: JSON.stringify({ add, remove }),
  });
  return res.json();
}

// Add negative keywords
export async function addNegativeKeywords(campaignId: string, keywords: string[]) {
  const res = await fetchWithAuth(`/campaigns/${campaignId}/negative-keywords`, {
    method: "PUT",
    body: JSON.stringify({ keywords }),
  });
  return res.json();
}

// Update ad copy
export async function updateAdCopy(campaignId: string, headlines: string[], descriptions: string[]) {
  const res = await fetchWithAuth(`/campaigns/${campaignId}/ad-copy`, {
    method: "PUT",
    body: JSON.stringify({ headlines, descriptions }),
  });
  return res.json();
}

// Get keyword performance for a campaign
export async function getKeywordPerformance(campaignId: string, days = 30) {
  const res = await fetchWithAuth(`/campaigns/${campaignId}/keyword-performance?days=${days}`);
  return res.json();
}

// Get search terms for a campaign
export async function getSearchTerms(campaignId: string, days = 30) {
  const res = await fetchWithAuth(`/campaigns/${campaignId}/search-terms?days=${days}`);
  return res.json();
}

// Get campaign details (with keywords etc.)
export async function getCampaignDetail(campaignId: string) {
  const res = await fetchWithAuth(`/campaigns/${campaignId}`);
  return res.json();
}

export { ApiError, fetchWithAuth };
