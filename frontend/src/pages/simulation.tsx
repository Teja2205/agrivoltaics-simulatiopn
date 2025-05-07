import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../contexts/AuthContext';
import AgrivoltaicsDashboard from '../components/Dashbord/AgrivoltaicsDashboard';
import { Toaster } from 'react-hot-toast';

export default function SimulationPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div>
      <Toaster position="top-right" />
      <AgrivoltaicsDashboard />
    </div>
  );
}