"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Zap } from "lucide-react";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import { signup, ApiError } from "@/lib/api";

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
      document.cookie = `pp_token=${data.access_token}; path=/; max-age=${60*60*24*7}; SameSite=Lax`;
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

  return (
    <div className="min-h-screen gradient-hero flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex items-center justify-center gap-2 mb-8">
          <div className="w-10 h-10 bg-electric rounded-xl flex items-center justify-center">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <span className="text-white text-2xl font-bold">PatientPlex AI</span>
        </div>

        {/* Card */}
        <div className="card-elevated">
          <h1 className="text-2xl font-bold text-navy text-center mb-1">
            Create your account
          </h1>
          <p className="text-gray-500 text-center mb-6 text-sm">
            Start getting patients in under 5 minutes
          </p>

          {apiError && (
            <div className="bg-coral/10 border border-coral/30 text-coral rounded-lg px-4 py-3 mb-4 text-sm">
              {apiError}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Full Name"
              placeholder="Dr. Priya Sharma"
              value={form.full_name}
              onChange={(e) => update("full_name", e.target.value)}
              error={errors.full_name}
            />
            <Input
              label="Email"
              type="email"
              placeholder="priya@clinic.com"
              value={form.email}
              onChange={(e) => update("email", e.target.value)}
              error={errors.email}
            />
            <Input
              label="Phone"
              type="tel"
              placeholder="9876543210"
              value={form.phone}
              onChange={(e) => update("phone", e.target.value)}
              error={errors.phone}
            />
            <Input
              label="Password"
              type="password"
              placeholder="At least 8 characters"
              value={form.password}
              onChange={(e) => update("password", e.target.value)}
              error={errors.password}
            />
            <Input
              label="Confirm Password"
              type="password"
              placeholder="Repeat your password"
              value={form.confirm_password}
              onChange={(e) => update("confirm_password", e.target.value)}
              error={errors.confirm_password}
            />

            <Button type="submit" fullWidth loading={loading} size="lg">
              Create Account
            </Button>
          </form>

          <p className="text-center text-sm text-gray-500 mt-6">
            Already have an account?{" "}
            <Link
              href="/login"
              className="text-electric font-semibold hover:underline"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
