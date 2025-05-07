// AuthContext.tsx - Fixed implementation
import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';
import toast from 'react-hot-toast';

interface User {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
}

interface AuthCredentials {
  email: string;
  password: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: AuthCredentials) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  login: async () => {},
  logout: () => {},
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Function to handle token refresh
  const refreshToken = async (): Promise<boolean> => {
    try {
      // Make sure the api.auth has a refreshToken method
      const response = await api.auth.refreshToken();
      
      if (response && response.data) {
        // Token refreshed successfully
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to refresh token:', error);
      return false;
    }
  };

  // Check auth status on initial load
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await api.auth.getCurrentUser();
        
        if (response && response.data) {
          setUser(response.data);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        // Try to refresh the token if auth check fails
        const refreshed = await refreshToken();
        if (refreshed) {
          // Try again after refresh
          try {
            const retryResponse = await api.auth.getCurrentUser();
            if (retryResponse && retryResponse.data) {
              setUser(retryResponse.data);
            }
          } catch (retryError) {
            console.error('Auth check failed after token refresh:', retryError);
          }
        }
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  // Set up periodic token refresh
  useEffect(() => {
    if (user) {
      // Refresh token every 6 days (assuming tokens expire after 7 days)
      const refreshInterval = setInterval(() => {
        refreshToken().then(success => {
          if (!success) {
            // If refresh fails, log out the user
            console.warn('Token refresh failed, logging out');
            logout();
          }
        });
      }, 6 * 24 * 60 * 60 * 1000); // 6 days in milliseconds
      
      return () => clearInterval(refreshInterval);
    }
  }, [user]);

  const login = async (credentials: AuthCredentials) => {
    try {
      const response = await api.auth.login(credentials);
      
      if (response && response.data) {
        // Fetch user details after successful login
        const userResponse = await api.auth.getCurrentUser();
        if (userResponse && userResponse.data) {
          setUser(userResponse.data);
          toast.success('Login successful');
        }
      } else {
        toast.error(response?.error || 'Login failed');
        throw new Error(response?.error || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      toast.error('Login failed');
      throw error;
    }
  };

  const logout = () => {
    api.auth.logout();
    setUser(null);
    toast.success('Logged out successfully');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};