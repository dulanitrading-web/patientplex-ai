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
  specialty_id: string;
  services: { name: string; enabled: boolean }[];
}) {
  const res = await fetchWithAuth("/onboarding/step1", {
    method: "POST",
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function updateStep2(data: {
  clinic_name: string;
  address: string;
  city: string;
  state: string;
  pincode: string;
  geo_radius_km: number;
}) {
  const res = await fetchWithAuth("/onboarding/step2", {
    method: "POST",
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function updateStep3(data: { monthly_budget: number }) {
  const res = await fetchWithAuth("/onboarding/step3", {
    method: "POST",
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function updateStep4(data: {
  whatsapp_number: string;
  google_calendar_connected?: boolean;
}) {
  const res = await fetchWithAuth("/onboarding/step4", {
    method: "POST",
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function getSpecialties() {
  const res = await fetchWithAuth("/specialties");
  return res.json();
}

export async function getGoogleCalendarUrl() {
  const res = await fetchWithAuth("/integrations/google-calendar/auth-url");
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

export { ApiError };
