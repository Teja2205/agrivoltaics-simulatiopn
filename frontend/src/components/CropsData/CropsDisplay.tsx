import { useEffect, useState } from 'react';
import { api } from '../../services/api';
import toast from 'react-hot-toast';

interface CropData {
  id: string;
  name: string;
  growth_stage: string;
  health_status: string;
  water_needs: number;
  light_needs: number;
}

export default function CropsDisplay() {
  const [cropsData, setCropsData] = useState<CropData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCropsData = async () => {
      try {
        const response = await api.crops.getCropsData();
        if (response.data) {
          setCropsData(response.data);
        }
      } catch (error) {
        toast.error('Failed to load crops data');
      } finally {
        setLoading(false);
      }
    };

    fetchCropsData();
  }, []);

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-64 bg-gray-200 rounded-lg"></div>
      </div>
    );
  }

  if (!cropsData.length) {
    return (
      <div className="bg-yellow-50 p-4 rounded-lg">
        <p className="text-yellow-700">No crops data available</p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Crops Status</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Crop Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Growth Stage
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Health Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Water Needs
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Light Needs
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {cropsData.map((crop) => (
              <tr key={crop.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {crop.name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {crop.growth_stage}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                      ${
                        crop.health_status === 'good'
                          ? 'bg-green-100 text-green-800'
                          : crop.health_status === 'moderate'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }
                    `}
                  >
                    {crop.health_status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div
                      className="bg-blue-600 h-2.5 rounded-full"
                      style={{ width: `${crop.water_needs}%` }}
                    ></div>
                  </div>
                  <span className="text-xs mt-1">{crop.water_needs}%</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div
                      className="bg-yellow-400 h-2.5 rounded-full"
                      style={{ width: `${crop.light_needs}%` }}
                    ></div>
                  </div>
                  <span className="text-xs mt-1">{crop.light_needs}%</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}