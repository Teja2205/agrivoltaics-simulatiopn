import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const simulationService = {
  // Get the latest simulation results
  getLatestSimulation: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/simulation/latest`);
      return response.data;
    } catch (error) {
      console.error('Error fetching latest simulation:', error);
      throw error;
    }
  },
  
  // Get a specific simulation by ID
  getSimulationById: async (id) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/simulation/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching simulation with ID ${id}:`, error);
      throw error;
    }
  },
  
  // Run a new simulation with specific configuration
  runSimulation: async (config) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/simulation/run`, { config });
      return response.data;
    } catch (error) {
      console.error('Error running simulation:', error);
      throw error;
    }
  },
  
  // Get list of all simulations
  getAllSimulations: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/simulation`);
      return response.data;
    } catch (error) {
      console.error('Error fetching all simulations:', error);
      throw error;
    }
  }
};

export default simulationService;