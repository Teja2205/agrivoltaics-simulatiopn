import axios, { AxiosError } from 'axios';
import Cookies from 'js-cookie';

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true
});

// Add request interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = Cookies.get('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Remove token and redirect to login only if not already on login page
      Cookies.remove('auth_token');
      if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

interface SimulationStats {
  total: number;
  active: number;
  completed: number;
  lastSimulation?: {
    id: string;
    title: string;
    status: string;
    created_at: string;
    completed_at?: string;
  };
}

// Add interfaces for simulations
interface Simulation {
  id: number;
  title: string;
  description?: string;
  parameters: Record<string, any>;
  owner_id: number;
  status: string;
  results?: Record<string, any>;
  created_at: string;
  updated_at?: string;
  completed_at?: string;
}

interface SimulationCreateRequest {
  title: string;
  description?: string;
  parameters: Record<string, any>;
}

interface SimulationUpdateRequest {
  title?: string;
  description?: string;
  parameters?: Record<string, any>;
  status?: string;
}

export const api = {
  auth: {
    login: async (credentials: { email: string; password: string }) => {
      try {
        const formData = new URLSearchParams();
        formData.append('username', credentials.email);
        formData.append('password', credentials.password);
        
        const response = await axios.post(`${API_BASE_URL}/api/auth/login`, formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          withCredentials: true
        });
        
        if (response.data.access_token) {
          Cookies.set('auth_token', response.data.access_token, { 
            expires: 7,
            path: '/',
            secure: process.env.NODE_ENV === 'production',
            sameSite: 'lax'
          });
          return { success: true, data: response.data };
        }
        
        return { success: false, error: 'Invalid response from server' };
      } catch (error) {
        console.error('Login error:', error);
        if (error.response?.data?.detail) {
          return { success: false, error: error.response.data.detail };
        }
        return { success: false, error: 'Failed to connect to the server' };
      }
    },
    
    refreshToken: async () => {
      try {
        const response = await apiClient.post('/auth/refresh');
        
        if (response.data && response.data.access_token) {
          // Update token in cookie
          Cookies.set('auth_token', response.data.access_token, { 
            expires: 7,
            path: '/',
            secure: process.env.NODE_ENV === 'production',
            sameSite: 'lax'
          });
          return { success: true, data: response.data };
        }
        
        return { success: false, error: 'Invalid response from refresh endpoint' };
      } catch (error) {
        console.error('Token refresh error:', error);
        return { 
          success: false, 
          error: error.response?.data?.detail || 'An error occurred during token refresh' 
        };
      }
    },
    
    getCurrentUser: async () => {
      try {
        const response = await apiClient.get('/users/me');
        return { success: true, data: response.data };
      } catch (error) {
        console.error('Get current user error:', error);
        if (error.response?.status === 401) {
          Cookies.remove('auth_token');
          return { success: false, error: 'Authentication required' };
        }
        return { 
          success: false, 
          error: error.response?.data?.detail || 'Failed to fetch user data' 
        };
      }
    },

    logout: () => {
      Cookies.remove('auth_token', { path: '/' });
      window.location.href = '/login';
    }
  },

  simulation: {
    getSimulationStats: async (): Promise<{ success: boolean; data?: SimulationStats; error?: string }> => {
      try {
        const response = await apiClient.get<SimulationStats>('/simulation/stats');
        return { success: true, data: response.data };
      } catch (error) {
        console.error('Error fetching simulation stats:', error);
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to fetch simulation statistics'
        };
      }
    },

    getSimulationData: async () => {
      try {
        const response = await apiClient.get('/simulation/stats');
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to fetch simulation data'
        };
      }
    },
    
    // Updated methods for simulations
    createSimulation: async (simulationData: SimulationCreateRequest) => {
      try {
        const response = await apiClient.post<Simulation>('/simulation', simulationData);
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to create simulation'
        };
      }
    },
    
    runSimulation: async (config: any) => {
      try {
        const response = await apiClient.post('/simulation/run', { parameters: config });
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to run simulation'
        };
      }
    },
    
    getSimulationById: async (id: number) => {
      try {
        const response = await apiClient.get(`/simulation/${id}`);
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || `Failed to fetch simulation with ID ${id}`
        };
      }
    },
    
    updateSimulation: async (id: number, updateData: SimulationUpdateRequest) => {
      try {
        const response = await apiClient.put<Simulation>(`/simulation/${id}`, updateData);
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || `Failed to update simulation with ID ${id}`
        };
      }
    },
    
    deleteSimulation: async (id: number) => {
      try {
        await apiClient.delete(`/simulation/${id}`);
        return { success: true };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || `Failed to delete simulation with ID ${id}`
        };
      }
    },
    
    getSimulationResults: async (id: number) => {
      try {
        const response = await apiClient.get(`/simulation/${id}/results`);
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || `Failed to fetch results for simulation ${id}`
        };
      }
    },
    
    runExistingSimulation: async (id: number) => {
      try {
        const response = await apiClient.post<Simulation>(`/simulation/${id}/run`);
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || `Failed to run simulation with ID ${id}`
        };
      }
    },
    
    getAllSimulations: async (options?: { skip?: number; limit?: number; status?: string }) => {
      try {
        const params = new URLSearchParams();
        if (options?.skip) params.append('skip', options.skip.toString());
        if (options?.limit) params.append('limit', options.limit.toString());
        if (options?.status) params.append('status', options.status);
        
        const response = await apiClient.get('/simulation', { params });
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to fetch simulations'
        };
      }
    }
  },
  
  weather: {
    getWeatherData: async () => {
      try {
        const response = await apiClient.get('/weather/data');
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to fetch weather data'
        };
      }
    },
    getWeatherForecast: async (params: { latitude: number; longitude: number; days?: number }) => {
      try {
        const queryParams = new URLSearchParams();
        queryParams.append('latitude', params.latitude.toString());
        queryParams.append('longitude', params.longitude.toString());
        if (params.days) queryParams.append('days', params.days.toString());
        
        const response = await apiClient.get(`/weather/forecast?${queryParams}`);
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to fetch weather forecast'
        };
      }
    }
  },
  
  crops: {
    getCropsData: async (options?: { skip?: number; limit?: number }) => {
      try {
        const params = new URLSearchParams();
        if (options?.skip) params.append('skip', options.skip.toString());
        if (options?.limit) params.append('limit', options.limit.toString());
        
        const response = await apiClient.get('/crops', { params });
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to fetch crops data'
        };
      }
    },
    getCropById: async (id: number) => {
      try {
        const response = await apiClient.get(`/crops/${id}`);
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || `Failed to fetch crop with ID ${id}`
        };
      }
    },
    searchCrops: async (params: { 
      name?: string; 
      scientific_name?: string; 
      min_shade_tolerance?: number;
      max_water_requirement?: number;
      skip?: number;
      limit?: number;
    }) => {
      try {
        const queryParams = new URLSearchParams();
        if (params.name) queryParams.append('name', params.name);
        if (params.scientific_name) queryParams.append('scientific_name', params.scientific_name);
        if (params.min_shade_tolerance !== undefined) 
          queryParams.append('min_shade_tolerance', params.min_shade_tolerance.toString());
        if (params.max_water_requirement !== undefined) 
          queryParams.append('max_water_requirement', params.max_water_requirement.toString());
        if (params.skip) queryParams.append('skip', params.skip.toString());
        if (params.limit) queryParams.append('limit', params.limit.toString());
        
        const response = await apiClient.get(`/crops/search/?${queryParams}`);
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to search crops'
        };
      }
    }
  },
  
  optimization: {
    optimizeSimulation: async (simulationId: number, optimizationData: any) => {
      try {
        const response = await apiClient.post(`/optimization/optimize/${simulationId}`, optimizationData);
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to optimize simulation'
        };
      }
    },
    getOptimizationResult: async (configId: number) => {
      try {
        const response = await apiClient.get(`/optimization/configurations/${configId}`);
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to fetch optimization result'
        };
      }
    },
    getOptimizedConfigurations: async (simulationId?: number) => {
      try {
        const params = simulationId ? `?simulation_id=${simulationId}` : '';
        const response = await apiClient.get(`/optimization/configurations${params}`);
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to fetch optimized configurations'
        };
      }
    }
  }
};

export default api;