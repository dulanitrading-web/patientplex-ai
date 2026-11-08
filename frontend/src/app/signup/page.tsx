"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Loader2, CheckCircle2 } from "lucide-react";
import { signup, ApiError } from "@/lib/api";
import Logo from "@/components/Logo";

export default function SignupPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    phone: "",
    password: "",
    confirm_password: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState("");

  function validate(): boolean {
    const errs: Record<string, string> = {};
    if (!form.full_name.trim()) errs.full_name = "Name is required";
    if (!form.email.trim()) errs.email = "Email is required";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email))
      errs.email = "Enter a valid email";
    if (!form.phone.trim()) errs.phone = "Phone is required";
    else if (!/^\d{10}$/.test(form.phone.replace(/\D/g, "")))
      errs.phone = "Enter a valid 10-digit phone number";
    if (!form.password) errs.password = "Password is required";
    else if (form.password.length < 8)
      errs.password = "Password must be at least 8 characters";
    if (form.password !== form.confirm_password)
      errs.confirm_password = "Passwords do not match";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setApiError("");
    if (!validate()) return;

    setLoading(true);
    try {
      const data = await signup({
        full_name: form.full_name,
        email: form.email,
        phone: form.phone,
        password: form.password,
      });
      localStorage.setItem("pp_token", data.access_token);
      if (data.user?.full_name) {
        localStorage.setItem("user_name", data.user.full_name);
      }
      router.push("/onboarding");
    } catch (err) {
      if (err instanceof ApiError) {
        setApiError(err.message);
      } else {
        setApiError("Something went wrong. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  function update(field: string, value: string) {
    setForm((f) => ({ ...f, [field]: value }));
    if (errors[field]) setErrors((e) => ({ ...e, [field]: "" }));
  }

  const inputClass =
    "w-full px-4 py-3 rounded-lg bg-white border border-slate-300 text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:border-slate-500 focus:ring-2 focus:ring-black/15 transition-colors";

  return (
    <div className="min-h-screen bg-[#FAFAF8] flex items-center justify-center px-4 py-12 relative overflow-hidden">
      <div className="w-full max-w-md relative">
        {/* Logo */}
        <Link href="/" className="flex items-center justify-center gap-2.5 mb-10">
          <Logo size={40} />
          <span className="font-black text-xl tracking-tight text-slate-900">PatientPlex</span>
        </Link>

        {/* Card */}
        <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
          <h1 className="text-2xl font-bold text-slate-900 text-center mb-1">
            Start your free trial
          </h1>
          <p className="text-slate-500 text-center mb-2 text-sm">
            Get patients in under 10 minutes
          </p>

          {/* Trust signals */}
          <div className="flex items-center justify-center gap-4 mb-8">
            {["14-day free trial", "No credit card"].map((t) => (
              <span key={t} className="flex items-center gap-1 text-xs text-slate-500">
                <CheckCircle2 className="w-3 h-3 text-slate-500" />
                {t}
              </span>
            ))}
          </div>

          {apiError && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg px-4 py-3 mb-6 text-sm">
              {apiError}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">Full name</label>
              <input
                type="text"
                placeholder="Dr. Priya Sharma"
                value={form.full_name}
                onChange={(e) => update("full_name", e.target.value)}
                className={inputClass}
              />
              {errors.full_name && <p className="text-red-400 text-xs mt-1.5">{errors.full_name}</p>}
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Email</label>
                <input
                  type="email"
                  placeholder="priya@clinic.com"
                  value={form.email}
                  onChange={(e) => update("email", e.target.value)}
                  className={inputClass}
                />
                {errors.email && <p className="text-red-400 text-xs mt-1.5">{errors.email}</p>}
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Phone</label>
                <input
                  type="tel"
                  placeholder="9876543210"
                  value={form.phone}
                  onChange={(e) => update("phone", e.target.value)}
                  className={inputClass}
                />
                {errors.phone && <p className="text-red-400 text-xs mt-1.5">{errors.phone}</p>}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">Password</label>
              <input
                type="password"
                placeholder="At least 8 characters"
                value={form.password}
                onChange={(e) => update("password", e.target.value)}
                className={inputClass}
              />
              {errors.password && <p className="text-red-400 text-xs mt-1.5">{errors.password}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">Confirm password</label>
              <input
                type="password"
                placeholder="Repeat your password"
                value={form.confirm_password}
                onChange={(e) => update("confirm_password", e.target.value)}
                className={inputClass}
              />
              {errors.confirm_password && <p className="text-red-400 text-xs mt-1.5">{errors.confirm_password}</p>}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-lg bg-slate-900 hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm transition-colors flex items-center justify-center gap-2 mt-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Creating account...
                </>
              ) : (
                "Create account"
              )}
            </button>
          </form>

          <p className="text-center text-sm text-slate-500 mt-6">
            Already have an account?{" "}
            <Link href="/login" className="text-black font-medium hover:text-black transition-colors">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
