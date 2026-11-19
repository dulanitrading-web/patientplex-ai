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

let _refreshing: Promise<string | null> | null = null;

async function tryRefreshToken(): Promise<string | null> {
  const token = typeof window !== "undefined" ? localStorage.getItem("pp_token") : null;
  if (!token) return null;
  try {
    const res = await fetch(`${BASE_URL}/auth/refresh`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    });
    if (res.ok) {
      const data = await res.json();
      const newToken = data.access_token;
      localStorage.setItem("pp_token", newToken);
      const isSecure = window.location.protocol === "https:";
      document.cookie = `pp_token=${newToken}; path=/; max-age=${60 * 60 * 24}; SameSite=Lax${isSecure ? "; Secure" : ""}`;
      return newToken;
    }
  } catch { /* refresh failed */ }
  return null;
}

async function fetchWithAuth(
  url: string,
  options: RequestInit = {},
  _retried = false,
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
    // 401 = token may be expired → try refreshing once before giving up
    if (response.status === 401 && typeof window !== "undefined" && !_retried) {
      // Deduplicate concurrent refresh attempts
      if (!_refreshing) _refreshing = tryRefreshToken().finally(() => { _refreshing = null; });
      const newToken = await _refreshing;
      if (newToken) {
        // Retry the original request with the new token
        return fetchWithAuth(url, options, true);
      }
      // Refresh failed — clear auth and redirect
      localStorage.removeItem("pp_token");
      document.cookie = "pp_token=; path=/; max-age=0";
      if (!window.location.pathname.startsWith("/login") && !window.location.pathname.startsWith("/signup")) {
        window.location.href = "/login?expired=1";
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

export async function updateAppointmentStatus(
  id: string,
  status: string,
  options?: { notes?: string; revenue_amount?: number; treatment_done?: string }
) {
  const res = await fetchWithAuth(`/appointments/${id}/status`, {
    method: "PUT",
    body: JSON.stringify({ status, ...options }),
  });
  return res.json();
}

export async function bookAppointment(data: {
  patient_name: string;
  patient_phone: string;
  treatment: string;
  date: string;
  time: string;
  source: string;
  notes?: string;
}) {
  const res = await fetchWithAuth("/appointments/book", {
    method: "POST",
    body: JSON.stringify(data),
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
  clinic_logo?: string;
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

// AI Chat Assistant
export async function sendChatMessage(message: string, history?: { role: string; content: string }[]) {
  const res = await fetchWithAuth("/ai-chat/message", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history: history || [] }),
  });
  return res.json();
}

export async function getChatSuggestions() {
  const res = await fetchWithAuth("/ai-chat/suggestions");
  return res.json();
}

// Clinic Staff
export async function getClinicStaff() {
  const res = await fetchWithAuth("/staff/");
  return res.json();
}

export async function addClinicStaff(data: {
  full_name: string;
  specialty: string;
  services?: string[];
  phone?: string;
  email?: string;
  calendar_color?: string;
}) {
  const res = await fetchWithAuth("/staff/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function getStaffAvailability(staffId: string, date: string) {
  const res = await fetchWithAuth(`/staff/${staffId}/availability?date=${date}`);
  return res.json();
}

export async function getStaffCalendar(dateFrom?: string, dateTo?: string) {
  const params = new URLSearchParams();
  if (dateFrom) params.set("date_from", dateFrom);
  if (dateTo) params.set("date_to", dateTo);
  const res = await fetchWithAuth(`/staff/calendar?${params}`);
  return res.json();
}

// Patients CRM
export async function getPatients(params?: { search?: string; source?: string; sort_by?: string; limit?: number }) {
  const qs = new URLSearchParams();
  if (params?.search) qs.set("search", params.search);
  if (params?.source) qs.set("source", params.source);
  if (params?.sort_by) qs.set("sort_by", params.sort_by);
  if (params?.limit) qs.set("limit", String(params.limit));
  const res = await fetchWithAuth(`/patients/?${qs}`);
  return res.json();
}

export async function getPatientStats() {
  const res = await fetchWithAuth("/patients/stats");
  return res.json();
}

export async function getPatient(id: string) {
  const res = await fetchWithAuth(`/patients/${id}`);
  return res.json();
}

export async function createPatient(data: { name: string; phone: string; email?: string; source?: string }) {
  const res = await fetchWithAuth("/patients/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function sendFeedbackRequest(appointmentId: string) {
  const res = await fetchWithAuth(`/appointments/${appointmentId}/feedback`, {
    method: "POST",
  });
  return res.json();
}

export { ApiError, fetchWithAuth };
