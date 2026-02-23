import SupportForm from '@/components/SupportForm';

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-2xl mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">TechCorp Support</h1>
          <p className="mt-2 text-gray-600">
            How can we help you today? Fill out the form below and our team will get back to you.
          </p>
        </div>
        <SupportForm apiEndpoint="/api/support/submit" />
      </div>
    </main>
  );
}
