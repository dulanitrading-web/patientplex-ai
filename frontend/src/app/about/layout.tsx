import { Metadata } from "next";

export const metadata: Metadata = {
  title: "About PatientPlex AI — AI Patient Acquisition for Indian Clinics",
  description:
    "Learn about PatientPlex AI, the AI-powered patient acquisition platform helping Indian clinics get more patients through automated Google Ads, Meta Ads, and WhatsApp AI receptionist.",
  alternates: {
    canonical: "https://patientplex-ai.vercel.app/about",
  },
};

export default function AboutLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
