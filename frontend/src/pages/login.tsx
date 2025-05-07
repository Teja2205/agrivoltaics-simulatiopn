import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { Toaster } from 'react-hot-toast';
import { LoginForm } from '../components/LoginForm';
import { useAuth } from '../contexts/AuthContext';

export default function LoginPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();
  const { from } = router.query;

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      const redirectPath = typeof from === 'string' ? from : '/dashboard';
      router.replace(redirectPath);
    }
  }, [isAuthenticated, isLoading, router, from]);

  // Don't render anything while checking authentication
  if (isLoading) {
    return null;
  }

  // Only render the login form if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Toaster position="top-right" />
        <LoginForm />
      </div>
    );
  }

  return null; // Don't render anything if authenticated (will redirect)
}
