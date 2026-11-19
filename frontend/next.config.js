/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "https://patientplex-ai-g7ce.onrender.com/api/v1",
    NEXT_PUBLIC_GA4_ID: process.env.NEXT_PUBLIC_GA4_ID || "G-HRN769N8DM",
  },
};

module.exports = nextConfig;
