"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useRouter } from "next/navigation";

interface Doctor {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  clinic_name: string | null;
  specialty: string | null;
  services: string[] | null;
  clinic_address: string | null;
  city: string | null;
  state: string | null;
  monthly_budget: number;
  whatsapp_number: string | null;
  subdomain_slug: string | null;
  onboarding_step: number;
  onboarding_completed: boolean;
  is_active: boolean;
}

interface AuthContextType {
  doctor: Doctor | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (data: { full_name: string; email: string; phone: string; password: string }) => Promise<void>;
  logout: () => void;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  try { return localStorage.getItem("pp_token"); } catch { return null; }
}

function setStoredToken(token: string | null) {
  if (typeof window === "undefined") return;
  try {
    if (token) {
      localStorage.setItem("pp_token", token);
      document.cookie = `pp_token=${token}; path=/; max-age=${60 * 60 * 24 * 7}; SameSite=Lax`;
    } else {
      localStorage.removeItem("pp_token");
      document.cookie = "pp_token=; path=/; max-age=0";
    }
  } catch { /* storage unavailable */ }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [doctor, setDoctor] = useState<Doctor | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchMe = useCallback(async (t: string): Promise<Doctor | null> => {
    try {
      const res = await fetch(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${t}` },
      });
      if (!res.ok) {
        if (res.status === 401) {
          setStoredToken(null);
          return null;
        }
        return null;
      }
      return await res.json();
    } catch {
      return null;
    }
  }, []);

  const refresh = useCallback(async () => {
    const t = getStoredToken();
    if (!t) {
      setLoading(false);
      return;
    }
    setToken(t);
    const doc = await fetchMe(t);
    setDoctor(doc);
    if (!doc) {
      setStoredToken(null);
      setToken(null);
    }
    setLoading(false);
  }, [fetchMe]);

  useEffect(() => { refresh(); }, [refresh]);

  const login = useCallback(async (email: string, password: string) => {
    const res = await fetch(`${API}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Login failed" }));
      throw new Error(err.detail || "Login failed");
    }
    const data = await res.json();
    setStoredToken(data.access_token);
    setToken(data.access_token);
    const doc = await fetchMe(data.access_token);
    setDoctor(doc);
    if (doc?.onboarding_completed) {
      router.push("/dashboard");
    } else {
      router.push("/onboarding");
    }
  }, [fetchMe, router]);

  const signup = useCallback(async (formData: { full_name: string; email: string; phone: string; password: string }) => {
    const res = await fetch(`${API}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Signup failed" }));
      throw new Error(err.detail || "Signup failed");
    }
    const data = await res.json();
    setStoredToken(data.access_token);
    setToken(data.access_token);
    const doc = await fetchMe(data.access_token);
    setDoctor(doc);
    router.push("/onboarding");
  }, [fetchMe, router]);

  const logout = useCallback(() => {
    setStoredToken(null);
    setToken(null);
    setDoctor(null);
    router.push("/login");
  }, [router]);

  const value = useMemo(
    () => ({ doctor, token, loading, login, signup, logout, refresh }),
    [doctor, token, loading, login, signup, logout, refresh],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
