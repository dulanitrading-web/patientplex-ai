export default function PrivacyPage() {
  return (
    <main className="max-w-3xl mx-auto px-6 py-12">
      <h1 className="text-3xl font-bold text-slate-900 mb-6">Privacy Policy</h1>
      <p className="text-sm text-slate-500 mb-8">Last updated: November 2026</p>

      <div className="prose prose-slate max-w-none space-y-6">
        <section>
          <h2 className="text-xl font-semibold text-slate-800">1. Information We Collect</h2>
          <p className="text-slate-600 leading-relaxed">
            PatientPlex AI collects information you provide when registering your clinic,
            including your name, email, phone number, clinic details, and address. We also
            collect data from integrated services (Google Ads, Meta Ads, Google Calendar,
            WhatsApp) that you explicitly authorize through OAuth.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-slate-800">2. How We Use Your Information</h2>
          <p className="text-slate-600 leading-relaxed">
            We use your information to provide AI-powered patient acquisition services,
            manage your advertising campaigns, track appointments, and optimize your
            clinic&apos;s digital marketing performance. We do not sell your data to third parties.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-slate-800">3. Data Security</h2>
          <p className="text-slate-600 leading-relaxed">
            We encrypt sensitive data including OAuth tokens at rest using industry-standard
            encryption (Fernet/AES). All data is transmitted over HTTPS. We follow security
            best practices including CSRF protection and secure session management.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-slate-800">4. Third-Party Integrations</h2>
          <p className="text-slate-600 leading-relaxed">
            When you connect Google Ads, Meta Ads, Google Calendar, or WhatsApp, we access
            only the data necessary to provide our services. You can disconnect any
            integration at any time from your Settings page, which revokes our access.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-slate-800">5. Data Retention</h2>
          <p className="text-slate-600 leading-relaxed">
            We retain your data for as long as your account is active. You may request
            deletion of your account and all associated data by contacting support at
            support@patientplex.ai.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-slate-800">6. Contact Us</h2>
          <p className="text-slate-600 leading-relaxed">
            For privacy-related questions, contact us at support@patientplex.ai.
          </p>
        </section>
      </div>
    </main>
  );
}
