import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';

export default function SimulationsPage() {
  const router = useRouter();
  const [simulations, setSimulations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Simplified data fetching function
    const fetchSimulations = async () => {
      setIsLoading(true);
      try {
        // Just a placeholder - you'll replace this with your actual API call
        // const response = await api.simulation.getAllSimulations();
        setSimulations([]); // Empty array for now
        setIsLoading(false);
      } catch (err) {
        console.error('Error:', err);
        setError('Failed to load simulations');
        setIsLoading(false);
      }
    };

    fetchSimulations();
  }, []);

  if (isLoading) {
    return <div className="flex justify-center items-center min-h-screen">Loading...</div>;
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen p-4">
        <div className="bg-red-50 border border-red-200 rounded-md p-4 max-w-md">
          <h2 className="text-red-800 text-lg font-medium mb-2">Error</h2>
          <p className="text-red-700">{error}</p>
          <button
            onClick={() => router.reload()}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Simulations</h1>
          <button
            onClick={() => router.push('/dashboard')}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Back to Dashboard
          </button>
        </div>

        <div className="bg-white shadow overflow-hidden rounded-lg p-6 text-center">
          <p className="text-gray-500">This is the simulations page.</p>
          <p className="text-gray-500 mt-2">No simulations found.</p>
        </div>
      </div>
    </div>
  );
}