import type { Metadata } from "next";
import "@/styles/globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "PatientPlex AI — AI-Powered Patient Acquisition for Indian Clinics",
  description:
    "Stop paying agencies. PatientPlex AI runs your Google & Meta ads, WhatsApp receptionist, and appointment booking — all on autopilot. Used by 200+ healthcare clinics across 15+ specialties in India.",
  keywords: ["patient acquisition", "dental marketing", "dermatology marketing", "ophthalmology marketing", "orthopedic marketing", "gynecology marketing", "IVF clinic marketing", "WhatsApp AI", "clinic marketing India", "healthcare SaaS"],
  openGraph: {
    title: "PatientPlex AI — Stop Paying Agencies. Start Getting Patients.",
    description: "AI-powered Google & Meta ads, WhatsApp receptionist, and appointment booking for Indian clinics. ₹12 avg cost per booking.",
    type: "website",
    url: "https://patientplex-ai.vercel.app",
    siteName: "PatientPlex AI",
  },
  twitter: {
    card: "summary_large_image",
    title: "PatientPlex AI — AI Runs Your Patient Acquisition",
    description: "Stop paying agencies. AI-powered ads, WhatsApp AI receptionist, and smart booking for Indian clinics.",
  },
  icons: {
    icon: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
      </head>
      <body className="font-sans antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
