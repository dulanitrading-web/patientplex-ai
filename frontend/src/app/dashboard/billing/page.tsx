"use client";

import { useState, useEffect } from "react";
import {
  Loader2,
  CreditCard,
  BarChart3,
  Zap,
  Crown,
  Building2,
  CheckCircle2,
  ArrowRight,
} from "lucide-react";
import { getSubscription, getBillingPlans, startTrial } from "@/lib/api";

interface SubscriptionData {
  id: string;
  plan: string;
  status: string;
  price_inr: number;
  trial_ends_at: string | null;
  current_period_end: string | null;
  conversations_used: number;
  conversations_limit: number;
  campaigns_used: number;
  campaigns_limit: number;
}

interface PlanData {
  id: string;
  name: string;
  price_inr: number;
  max_conversations: number;
  max_campaigns: number;
  platforms: string[];
  features: string[];
}

export default function BillingPage() {
  const [subscription, setSubscription] = useState<SubscriptionData | null>(null);
  const [plans, setPlans] = useState<PlanData[]>([]);
  const [loading, setLoading] = useState(true);
  const [startingTrial, setStartingTrial] = useState(false);
  const [trialError, setTrialError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [subRes, plansRes] = await Promise.allSettled([
          getSubscription(),
          getBillingPlans(),
        ]);
        if (subRes.status === "fulfilled") setSubscription(subRes.value.subscription);
        if (plansRes.status === "fulfilled") setPlans(plansRes.value.plans || []);
      } catch {
        /* use defaults */
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  async function handleStartTrial() {
    setStartingTrial(true);
    setTrialError(null);
    try {
      await startTrial();
      const subRes = await getSubscription();
      setSubscription(subRes.subscription);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Could not start trial";
      setTrialError(message);
    } finally {
      setStartingTrial(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-slate-900" />
      </div>
    );
  }

  const trialDaysRemaining = subscription?.trial_ends_at
    ? Math.max(0, Math.ceil((new Date(subscription.trial_ends_at).getTime() - Date.now()) / (1000 * 60 * 60 * 24)))
    : null;

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Billing & Subscription</h1>
        <p className="text-slate-600 text-sm mt-1">Manage your plan, usage, and billing.</p>
      </div>

      {/* No Subscription CTA */}
      {!subscription && (
        <div className="rounded-2xl p-6 border border-slate-300 bg-slate-900/[0.06]">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-bold flex items-center gap-2 text-slate-900">
                <Zap className="w-6 h-6 text-black" /> Start Your Free Trial
              </h2>
              <p className="text-slate-500 mt-1">
                Get 14 days free with access to AI WhatsApp receptionist, Google campaigns, and more.
              </p>
            </div>
            <button
              onClick={handleStartTrial}
              disabled={startingTrial}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-[#0A0E1A] font-semibold text-sm transition-colors whitespace-nowrap disabled:opacity-50"
            >
              {startingTrial ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
              Start Free Trial <ArrowRight className="w-5 h-5" />
            </button>
          </div>
          {trialError && <p className="text-red-600 text-sm mt-2">{trialError}</p>}
        </div>
      )}

      {/* Current Plan + Usage */}
      {subscription && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Current Plan */}
          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <h3 className="font-semibold text-slate-900 flex items-center gap-2 mb-4">
              <CreditCard className="w-5 h-5 text-black" /> Current Plan
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">Plan</span>
                <span className="font-semibold text-slate-900">{formatPlanName(subscription.plan)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">Status</span>
                <StatusBadge status={subscription.status} />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">Price</span>
                <span className="font-semibold text-slate-900">
                  {subscription.price_inr === 0 ? "Free" : `₹${subscription.price_inr.toLocaleString("en-IN")}/mo`}
                </span>
              </div>
              {trialDaysRemaining !== null && trialDaysRemaining > 0 && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">Trial Days Left</span>
                  <span className="font-semibold text-amber-600">{trialDaysRemaining} days</span>
                </div>
              )}
              {subscription.current_period_end && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">Next Billing</span>
                  <span className="text-sm text-slate-700">
                    {new Date(subscription.current_period_end).toLocaleDateString("en-IN", {
                      year: "numeric", month: "short", day: "numeric",
                    })}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Usage */}
          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <h3 className="font-semibold text-slate-900 flex items-center gap-2 mb-4">
              <BarChart3 className="w-5 h-5 text-slate-700" /> Usage
            </h3>
            <div className="space-y-4">
              <UsageBar
                label="Conversations"
                used={subscription.conversations_used}
                limit={subscription.conversations_limit}
              />
              <UsageBar
                label="Active Campaigns"
                used={subscription.campaigns_used}
                limit={subscription.campaigns_limit}
              />
            </div>
          </div>
        </div>
      )}

      {/* Available Plans */}
      <div>
        <h2 className="text-lg font-bold text-slate-900 mb-4">Available Plans</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {plans.map((plan) => {
            const isCurrent = subscription?.plan === plan.id;
            const isPopular = plan.id === "GROWTH";
            return (
              <PlanCard
                key={plan.id}
                plan={plan}
                isCurrent={isCurrent}
                isPopular={isPopular}
              />
            );
          })}
        </div>
      </div>

      {/* Plan Comparison */}
      <div className="bg-white rounded-xl border border-slate-200 p-5">
        <h3 className="font-semibold text-slate-900 mb-4">Plan Comparison</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-3 pr-4 font-medium text-slate-600">Feature</th>
                {plans.map((p) => (
                  <th key={p.id} className="text-center py-3 px-2 font-medium text-slate-600">
                    {p.name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              <ComparisonRow
                label="Price"
                values={plans.map((p) => `₹${p.price_inr.toLocaleString("en-IN")}/mo`)}
              />
              <ComparisonRow
                label="Conversations"
                values={plans.map((p) => p.max_conversations === -1 ? "Unlimited" : String(p.max_conversations))}
              />
              <ComparisonRow
                label="Campaigns"
                values={plans.map((p) => p.max_campaigns === -1 ? "Unlimited" : String(p.max_campaigns))}
              />
              <ComparisonRow
                label="Platforms"
                values={plans.map((p) => p.platforms.join(", "))}
              />
              <ComparisonRow
                label="WhatsApp AI"
                values={plans.map(() => "✓")}
                highlight
              />
              <ComparisonRow
                label="Call Recovery"
                values={plans.map((p) => p.features.includes("call_recovery") ? "✓" : "—")}
              />
              <ComparisonRow
                label="Conversion Tracking"
                values={plans.map((p) => p.features.includes("conversion_tracking") ? "✓" : "—")}
              />
              <ComparisonRow
                label="Multi-Location"
                values={plans.map((p) => p.features.includes("multi_location") ? "✓" : "—")}
              />
              <ComparisonRow
                label="API Access"
                values={plans.map((p) => p.features.includes("api_access") ? "✓" : "—")}
              />
              <ComparisonRow
                label="Priority Support"
                values={plans.map((p) => p.features.includes("priority_support") ? "✓" : "—")}
              />
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

/* ---------- Sub-components ---------- */

function PlanCard({ plan, isCurrent, isPopular }: {
  plan: PlanData;
  isCurrent: boolean;
  isPopular: boolean;
}) {
  const planIcons: Record<string, React.ReactNode> = {
    STARTER: <Zap className="w-5 h-5" />,
    GROWTH: <Crown className="w-5 h-5" />,
    ENTERPRISE: <Building2 className="w-5 h-5" />,
  };

  const featureLabels: Record<string, string> = {
    whatsapp_receptionist: "AI WhatsApp Receptionist",
    calendar_booking: "Calendar Booking",
    reminders: "Automated Reminders",
    "1_landing_page": "1 Landing Page",
    treatment_landing_pages: "Treatment Landing Pages",
    call_recovery: "Missed Call Recovery",
    conversion_tracking: "Conversion Tracking",
    competitive_intel: "Competitive Intelligence",
    daily_summary: "Daily Summary Reports",
    doctor_notifications: "Doctor Notifications",
    multi_location: "Multi-Location Support",
    multi_doctor: "Multi-Doctor Support",
    custom_templates: "Custom Templates",
    api_access: "API Access",
    priority_support: "Priority Support",
    revenue_attribution: "Revenue Attribution",
  };

  return (
    <div className={`relative bg-white rounded-xl border-2 p-5 flex flex-col ${
      isCurrent ? "border-black/20" : isPopular ? "border-black/20" : "border-slate-200"
    }`}>
      {isPopular && !isCurrent && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-slate-900 text-white text-xs font-bold px-3 py-0.5 rounded-full">
          Most Popular
        </div>
      )}
      {isCurrent && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-slate-700 text-[#0A0E1A] text-xs font-bold px-3 py-0.5 rounded-full">
          Current Plan
        </div>
      )}

      <div className="flex items-center gap-2 mb-3 text-slate-900">
        {planIcons[plan.id] || <Zap className="w-5 h-5" />}
        <h3 className="text-lg font-bold">{plan.name}</h3>
      </div>

      <div className="mb-4">
        <span className="text-3xl font-bold text-slate-900">{"₹"}{plan.price_inr.toLocaleString("en-IN")}</span>
        <span className="text-slate-600 text-sm">/month</span>
      </div>

      <div className="text-sm text-slate-500 mb-3">
        <div>{plan.max_conversations === -1 ? "Unlimited" : plan.max_conversations} conversations</div>
        <div>{plan.max_campaigns === -1 ? "Unlimited" : plan.max_campaigns} campaigns</div>
        <div>{plan.platforms.join(" + ")} Ads</div>
      </div>

      <div className="flex-1 space-y-1.5 mb-4">
        {plan.features.slice(0, 6).map((f) => (
          <div key={f} className="flex items-center gap-2 text-sm text-slate-500">
            <CheckCircle2 className="w-3.5 h-3.5 text-slate-900 shrink-0" />
            {featureLabels[f] || f.replace(/_/g, " ")}
          </div>
        ))}
        {plan.features.length > 6 && (
          <div className="text-xs text-slate-600 mt-1">+{plan.features.length - 6} more features</div>
        )}
      </div>

      <button
        disabled={isCurrent}
        className={`w-full py-2.5 rounded-lg text-sm font-medium transition-colors ${
          isCurrent
            ? "bg-white/5 text-slate-600 cursor-not-allowed"
            : isPopular
              ? "bg-slate-900 hover:bg-slate-800 text-[#0A0E1A]"
              : "border border-slate-200 hover:border-slate-300 text-slate-700 hover:text-slate-900"
        }`}
      >
        {isCurrent ? "Current Plan" : "Upgrade"}
      </button>
    </div>
  );
}

function UsageBar({ label, used, limit }: { label: string; used: number; limit: number }) {
  const isUnlimited = limit === -1 || limit === 0;
  const pct = isUnlimited ? 0 : Math.min(100, Math.round((used / limit) * 100));
  const isHigh = pct >= 80;

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-slate-500">{label}</span>
        <span className="font-medium text-slate-900 tabular-nums">
          {used} / {isUnlimited ? "Unlimited" : limit}
        </span>
      </div>
      {!isUnlimited && (
        <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full ${isHigh ? "bg-amber-500" : "bg-slate-900"}`}
            style={{ width: `${pct}%` }}
          />
        </div>
      )}
      {isUnlimited && (
        <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
          <div className="h-full bg-black/15 rounded-full w-0" />
        </div>
      )}
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { cls: string; label: string }> = {
    TRIAL: { cls: "bg-slate-50 text-slate-700", label: "Trial" },
    ACTIVE: { cls: "bg-slate-50 text-black", label: "Active" },
    PAST_DUE: { cls: "bg-amber-50 text-amber-600", label: "Past Due" },
    CANCELLED: { cls: "bg-red-50 text-red-600", label: "Cancelled" },
    EXPIRED: { cls: "bg-white/5 text-slate-600", label: "Expired" },
  };
  const cfg = config[status] || { cls: "bg-white/5 text-slate-600", label: status };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${cfg.cls}`}>
      {cfg.label}
    </span>
  );
}

function ComparisonRow({ label, values, highlight }: {
  label: string;
  values: string[];
  highlight?: boolean;
}) {
  return (
    <tr>
      <td className={`py-2.5 pr-4 text-slate-500 ${highlight ? "font-medium text-slate-900" : ""}`}>{label}</td>
      {values.map((v, i) => (
        <td key={i} className={`py-2.5 px-2 text-center ${v === "✓" ? "text-black font-bold" : v === "—" ? "text-slate-600" : "text-slate-700"}`}>
          {v}
        </td>
      ))}
    </tr>
  );
}

function formatPlanName(plan: string): string {
  return plan.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
