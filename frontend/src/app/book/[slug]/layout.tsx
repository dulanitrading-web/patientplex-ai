import type { Metadata } from "next";

const API = process.env.NEXT_PUBLIC_API_URL || "https://patientplex-ai-g7ce.onrender.com/api/v1";

export async function generateMetadata({
  params,
}: {
  params: { slug: string };
}): Promise<Metadata> {
  try {
    const res = await fetch(`${API}/public/book/${params.slug}`, {
      next: { revalidate: 3600 },
    });
    if (!res.ok) return { title: "Book Appointment | PatientPlex AI" };
    const doctor = await res.json();

    const title = `Book Appointment — ${doctor.doctor_name} | ${doctor.clinic_name}`;
    const description = `Book your ${doctor.specialty?.toLowerCase() || "medical"} appointment with ${doctor.doctor_name} at ${doctor.clinic_name}, ${doctor.city}. Services: ${(doctor.services || []).slice(0, 5).join(", ")}. Instant online booking, no calls needed.`;

    return {
      title,
      description,
      openGraph: {
        title,
        description,
        type: "website",
        url: `https://patientplex-ai.vercel.app/book/${params.slug}`,
        siteName: "PatientPlex AI",
        locale: "en_IN",
      },
      twitter: {
        card: "summary",
        title,
        description,
      },
      robots: { index: true, follow: true },
    };
  } catch {
    return { title: "Book Appointment | PatientPlex AI" };
  }
}

export default function BookingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
