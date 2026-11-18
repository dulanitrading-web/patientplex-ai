import type { Metadata } from "next";
import Script from "next/script";
import "@/styles/globals.css";
import { Providers } from "./providers";
import StructuredData from "./structured-data";

export const metadata: Metadata = {
  metadataBase: new URL("https://patientplex-ai.vercel.app"),
  title: {
    default: "PatientPlex AI — AI-Powered Patient Acquisition for Indian Clinics",
    template: "%s | PatientPlex AI",
  },
  description:
    "Stop paying agencies. PatientPlex AI runs your Google & Meta ads, WhatsApp AI receptionist, and appointment booking — all on autopilot. Built for healthcare clinics across 15+ specialties in India. Starting at ₹9,999/month.",
  keywords: [
    "PatientPlex AI", "PatientPlex", "patient acquisition AI", "dental marketing India",
    "dermatology marketing India", "clinic marketing software", "healthcare SaaS India",
    "WhatsApp AI receptionist", "Google Ads for clinics", "Meta Ads for doctors",
    "appointment booking AI", "clinic lead generation", "doctor marketing platform",
    "ophthalmology marketing", "orthopedic marketing", "gynecology marketing",
    "IVF clinic marketing", "healthcare digital marketing India", "clinic automation",
    "patient booking software", "AI for healthcare India",
  ],
  authors: [{ name: "PatientPlex AI" }],
  creator: "PatientPlex AI",
  publisher: "PatientPlex AI",
  alternates: {
    canonical: "https://patientplex-ai.vercel.app",
  },
  openGraph: {
    title: "PatientPlex AI — Stop Paying Agencies. Start Getting Patients.",
    description: "AI-powered Google & Meta ads, WhatsApp AI receptionist, and appointment booking for Indian clinics. ₹5–8 cost per lead. 15+ specialties. Start free trial today.",
    type: "website",
    url: "https://patientplex-ai.vercel.app",
    siteName: "PatientPlex AI",
    locale: "en_IN",
  },
  twitter: {
    card: "summary_large_image",
    title: "PatientPlex AI — AI Runs Your Patient Acquisition",
    description: "Stop paying agencies. AI-powered ads, WhatsApp AI receptionist, and smart booking for Indian clinics. 14-day free trial.",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  verification: {
    // Add your Google Search Console verification code here
    // google: "your-verification-code",
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
        <link rel="dns-prefetch" href="https://www.googletagmanager.com" />
      </head>
      <body className="font-sans antialiased">
        <StructuredData />
        <Providers>{children}</Providers>
        {/* Google Analytics 4 */}
        {process.env.NEXT_PUBLIC_GA4_ID && (
          <>
            <Script
              src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA4_ID}`}
              strategy="afterInteractive"
            />
            <Script id="gtag-init" strategy="afterInteractive">
              {`
                window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                gtag('js', new Date());
                gtag('config', '${process.env.NEXT_PUBLIC_GA4_ID}', {
                  page_path: window.location.pathname,
                });
              `}
            </Script>
          </>
        )}
      </body>
    </html>
  );
}
