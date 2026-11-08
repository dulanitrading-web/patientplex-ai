import type { Metadata } from "next";
import "@/styles/globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "PatientPlex AI — Stop Paying Agencies. Start Getting Patients.",
  description:
    "AI-powered Google & Meta ads, a WhatsApp receptionist that never sleeps, and appointment booking that fills your calendar. Built for Indian dental and dermatology clinics.",
  openGraph: {
    title: "PatientPlex AI — Healthcare Patient Acquisition Platform",
    description: "AI-powered patient acquisition for Indian clinics. From ₹12 per booking.",
    type: "website",
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
