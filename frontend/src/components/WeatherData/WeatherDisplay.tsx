import { useEffect, useState } from 'react';
import { api } from '../../services/api';
import toast from 'react-hot-toast';

interface WeatherData {
  temperature: number;
  humidity: number;
  solar_radiation: number;
  timestamp: string;
}

export default function WeatherDisplay() {
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWeatherData = async () => {
      try {
        const response = await api.weather.getWeatherData();
        if (response.data) {
          setWeatherData(response.data);
        }
      } catch (error) {
        toast.error('Failed to load weather data');
      } finally {
        setLoading(false);
      }
    };

    fetchWeatherData();
    // Refresh weather data every 5 minutes
    const interval = setInterval(fetchWeatherData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-32 bg-gray-200 rounded-lg"></div>
      </div>
    );
  }

  if (!weatherData) {
    return (
      <div className="bg-red-50 p-4 rounded-lg">
        <p className="text-red-700">No weather data available</p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Current Weather Conditions</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-600">Temperature</p>
          <p className="text-2xl font-bold">{weatherData.temperature}°C</p>
        </div>
        <div className="p-4 bg-green-50 rounded-lg">
          <p className="text-sm text-green-600">Humidity</p>
          <p className="text-2xl font-bold">{weatherData.humidity}%</p>
        </div>
        <div className="p-4 bg-yellow-50 rounded-lg">
          <p className="text-sm text-yellow-600">Solar Radiation</p>
          <p className="text-2xl font-bold">{weatherData.solar_radiation} W/m²</p>
        </div>
      </div>
      <p className="text-sm text-gray-500 mt-4">
        Last updated: {new Date(weatherData.timestamp).toLocaleString()}
      </p>
    </div>
  );
}