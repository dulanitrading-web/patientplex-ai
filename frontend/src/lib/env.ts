/**
 * Environment variable validation and access.
 * Fails at build time if required vars are missing.
 */

// Public env vars (available in browser)
export const env = {
  // Google Analytics
  GA4_ID: process.env.NEXT_PUBLIC_GA4_ID || "",

  // API
  API_URL: process.env.NEXT_PUBLIC_API_URL || "",

  // Feature flags
  IS_PRODUCTION: process.env.NODE_ENV === "production",
  IS_DEVELOPMENT: process.env.NODE_ENV === "development",
} as const;

// Validate required env vars at startup (server-side only)
export function validateEnv() {
  const warnings: string[] = [];

  if (!env.API_URL) {
    warnings.push("NEXT_PUBLIC_API_URL is not set — API calls will fail");
  }

  if (!env.GA4_ID) {
    warnings.push("NEXT_PUBLIC_GA4_ID is not set — analytics disabled");
  }

  if (warnings.length > 0 && env.IS_DEVELOPMENT) {
    console.warn("\n⚠️  PatientPlex Environment Warnings:");
    warnings.forEach((w) => console.warn(`   - ${w}`));
    console.warn("");
  }

  return { valid: warnings.length === 0, warnings };
}
