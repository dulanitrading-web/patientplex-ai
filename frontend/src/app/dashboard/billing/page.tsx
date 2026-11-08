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
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
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
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  const trialDaysRemaining = subscription?.trial_ends_at
    ? Math.max(0, Math.ceil((new Date(subscription.trial_ends_at).getTime() - Date.now()) / (1000 * 60 * 60 * 24)))
    : null;

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-[#0B2545]">Billing & Subscription</h1>
        <p className="text-gray-500 text-sm mt-1">Manage your plan, usage, and billing.</p>
      </div>

      {/* No Subscription CTA */}
      {!subscription && (
        <div className="bg-gradient-to-r from-[#0B2545] to-[#13838C] rounded-2xl p-6 text-white">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-bold flex items-center gap-2">
                <Zap className="w-6 h-6" /> Start Your Free Trial
              </h2>
              <p className="text-white/80 mt-1">
                Get 14 days free with access to AI WhatsApp receptionist, Google campaigns, and more.
              </p>
            </div>
            <Button
              variant="primary"
              size="lg"
              onClick={handleStartTrial}
              loading={startingTrial}
              className="!bg-white !text-[#0B2545] hover:!bg-gray-100 whitespace-nowrap"
            >
              Start Free Trial <ArrowRight className="w-5 h-5" />
            </Button>
          </div>
          {trialError && <p className="text-red-200 text-sm mt-2">{trialError}</p>}
        </div>
      )}

      {/* Current Plan + Usage */}
      {subscription && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Current Plan */}
          <Card>
            <h3 className="font-semibold text-[#0B2545] flex items-center gap-2 mb-4">
              <CreditCard className="w-5 h-5" /> Current Plan
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Plan</span>
                <span className="font-semibold text-[#0B2545]">{formatPlanName(subscription.plan)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Status</span>
                <StatusBadge status={subscription.status} />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Price</span>
                <span className="font-semibold text-[#0B2545]">
                  {subscription.price_inr === 0 ? "Free" : `₹${subscription.price_inr.toLocaleString("en-IN")}/mo`}
                </span>
              </div>
              {trialDaysRemaining !== null && trialDaysRemaining > 0 && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Trial Days Left</span>
                  <span className="font-semibold text-orange-600">{trialDaysRemaining} days</span>
                </div>
              )}
              {subscription.current_period_end && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Next Billing</span>
                  <span className="text-sm text-gray-700">
                    {new Date(subscription.current_period_end).toLocaleDateString("en-IN", {
                      year: "numeric", month: "short", day: "numeric",
                    })}
                  </span>
                </div>
              )}
            </div>
          </Card>

          {/* Usage */}
          <Card>
            <h3 className="font-semibold text-[#0B2545] flex items-center gap-2 mb-4">
              <BarChart3 className="w-5 h-5" /> Usage
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
          </Card>
        </div>
      )}

      {/* Available Plans */}
      <div>
        <h2 className="text-lg font-bold text-[#0B2545] mb-4">Available Plans</h2>
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
      <Card>
        <h3 className="font-semibold text-[#0B2545] mb-4">Plan Comparison</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 pr-4 font-medium text-gray-500">Feature</th>
                {plans.map((p) => (
                  <th key={p.id} className="text-center py-3 px-2 font-medium text-gray-500">
                    {p.name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
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
      </Card>
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
      isCurrent ? "border-blue-500 shadow-md" : isPopular ? "border-teal-400" : "border-gray-200"
    }`}>
      {isPopular && !isCurrent && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-teal-500 text-white text-xs font-bold px-3 py-0.5 rounded-full">
          Most Popular
        </div>
      )}
      {isCurrent && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-600 text-white text-xs font-bold px-3 py-0.5 rounded-full">
          Current Plan
        </div>
      )}

      <div className="flex items-center gap-2 mb-3 text-[#0B2545]">
        {planIcons[plan.id] || <Zap className="w-5 h-5" />}
        <h3 className="text-lg font-bold">{plan.name}</h3>
      </div>

      <div className="mb-4">
        <span className="text-3xl font-bold text-[#0B2545]">{"₹"}{plan.price_inr.toLocaleString("en-IN")}</span>
        <span className="text-gray-500 text-sm">/month</span>
      </div>

      <div className="text-sm text-gray-600 mb-3">
        <div>{plan.max_conversations === -1 ? "Unlimited" : plan.max_conversations} conversations</div>
        <div>{plan.max_campaigns === -1 ? "Unlimited" : plan.max_campaigns} campaigns</div>
        <div>{plan.platforms.join(" + ")} Ads</div>
      </div>

      <div className="flex-1 space-y-1.5 mb-4">
        {plan.features.slice(0, 6).map((f) => (
          <div key={f} className="flex items-center gap-2 text-sm text-gray-600">
            <CheckCircle2 className="w-3.5 h-3.5 text-green-500 shrink-0" />
            {featureLabels[f] || f.replace(/_/g, " ")}
          </div>
        ))}
        {plan.features.length > 6 && (
          <div className="text-xs text-gray-400 mt-1">+{plan.features.length - 6} more features</div>
        )}
      </div>

      <Button
        variant={isCurrent ? "ghost" : isPopular ? "secondary" : "primary"}
        size="sm"
        fullWidth
        disabled={isCurrent}
      >
        {isCurrent ? "Current Plan" : "Upgrade"}
      </Button>
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
        <span className="text-gray-600">{label}</span>
        <span className="font-medium text-gray-900">
          {used} / {isUnlimited ? "Unlimited" : limit}
        </span>
      </div>
      {!isUnlimited && (
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full ${isHigh ? "bg-orange-500" : "bg-blue-500"}`}
            style={{ width: `${pct}%` }}
          />
        </div>
      )}
      {isUnlimited && (
        <div className="h-2 bg-green-100 rounded-full overflow-hidden">
          <div className="h-full bg-green-400 rounded-full w-0" />
        </div>
      )}
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { cls: string; label: string }> = {
    TRIAL: { cls: "bg-blue-50 text-blue-700", label: "Trial" },
    ACTIVE: { cls: "bg-green-50 text-green-700", label: "Active" },
    PAST_DUE: { cls: "bg-orange-50 text-orange-700", label: "Past Due" },
    CANCELLED: { cls: "bg-red-50 text-red-700", label: "Cancelled" },
    EXPIRED: { cls: "bg-gray-100 text-gray-500", label: "Expired" },
  };
  const cfg = config[status] || { cls: "bg-gray-100 text-gray-500", label: status };
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
      <td className={`py-2.5 pr-4 text-gray-700 ${highlight ? "font-medium" : ""}`}>{label}</td>
      {values.map((v, i) => (
        <td key={i} className={`py-2.5 px-2 text-center ${v === "✓" ? "text-green-600 font-bold" : v === "—" ? "text-gray-300" : "text-gray-700"}`}>
          {v}
        </td>
      ))}
    </tr>
  );
}

function formatPlanName(plan: string): string {
  return plan.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
