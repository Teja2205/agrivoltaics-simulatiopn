// Update in your auth.ts file
import { API_BASE_URL } from '../config/constants';
import Cookies from 'js-cookie';

// Rest of your auth service code remains the same

export interface User {
  id: string;
  email: string;
  name?: string;
  full_name?: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials extends LoginCredentials {
  name: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

class AuthService {
  private tokenKey = 'auth_token';
  private userKey = 'user_data';

  getToken(): string | null {
    if (typeof window !== 'undefined') {
      return Cookies.get(this.tokenKey) || null;
    }
    return null;
  }

  getUser(): User | null {
    if (typeof window !== 'undefined') {
      const userStr = localStorage.getItem(this.userKey);
      return userStr ? JSON.parse(userStr) : null;
    }
    return null;
  }

  setAuth(token: string, user: User): void {
    // Store token in cookie for better security (httpOnly in production)
    Cookies.set(this.tokenKey, token, { path: '/', secure: process.env.NODE_ENV === 'production' });
    // Store user in localStorage for easy access
    localStorage.setItem(this.userKey, JSON.stringify(user));
  }

  clearAuth(): void {
    Cookies.remove(this.tokenKey, { path: '/' });
    localStorage.removeItem(this.userKey);
  }

  async login(credentials: LoginCredentials): Promise<{ user: User; token: string }> {
    try {
      const formData = new URLSearchParams();
      formData.append('username', credentials.email);
      formData.append('password', credentials.password);

      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      }

      const data: AuthResponse = await response.json();
      
      // Fetch user profile after successful login
      const userProfile = await this.fetchUserProfile(data.access_token);
      
      this.setAuth(data.access_token, userProfile);
      
      return {
        token: data.access_token,
        user: userProfile
      };
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  async fetchUserProfile(token: string): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/api/users/me`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch user profile');
    }

    return await response.json();
  }

  async register(credentials: RegisterCredentials): Promise<{ user: User; token: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Registration failed');
      }

      const data = await response.json();
      this.setAuth(data.token, data.user);
      return data;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }

  async logout(): Promise<void> {
    try {
      const token = this.getToken();
      if (token) {
        await fetch(`${API_BASE_URL}/api/auth/logout`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
      // Continue with logout even if API call fails
    } finally {
      this.clearAuth();
    }
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  // Helper method to refresh token if needed
  async refreshToken(): Promise<string | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Authorization': `Bearer ${this.getToken()}`
        }
      });

      if (!response.ok) {
        this.clearAuth();
        return null;
      }

      const data = await response.json();
      const token = data.access_token;
      
      // Update the token only, keep the same user data
      Cookies.set(this.tokenKey, token, { path: '/', secure: process.env.NODE_ENV === 'production' });
      
      return token;
    } catch (error) {
      console.error('Token refresh error:', error);
      this.clearAuth();
      return null;
    }
  }
}

export const authService = new AuthService();