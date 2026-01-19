export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-4">Creative Studio</h1>
      <p className="text-gray-600 mb-8">
        Collaborate with AI specialists to create images and videos
      </p>
      <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition">
        Start Creating
      </button>
    </main>
  );
}
