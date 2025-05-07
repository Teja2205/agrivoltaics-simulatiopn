import { useState } from 'react';
import { useRouter } from 'next/router';
import { Header } from '../../components/Header';  // This path is correct
import { api } from '../../services/api';  // This path is correct
import toast from 'react-hot-toast';

interface SimulationCreateRequest {
  title: string;
  description?: string;
  parameters: {
    panelHeight: number;
    panelAngle: number;
    panelSpacing: number;
    cropType: string;
    irrigationAmount: number;
    trackingType: string;
  };
}

export default function NewSimulationPage() {
  const router = useRouter();
  const [formData, setFormData] = useState<SimulationCreateRequest>({
    title: '',
    description: '',
    parameters: {
      panelHeight: 2.5,
      panelAngle: 30,
      panelSpacing: 5.0,
      cropType: 'lettuce',
      irrigationAmount: 5.0,
      trackingType: 'fixed',
    }
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleParameterChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      parameters: {
        ...formData.parameters,
        [name]: name === 'cropType' || name === 'trackingType' ? value : parseFloat(value)
      }
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await api.simulation.createSimulation(formData);
      
      if (response.success) {
        toast.success('Simulation created successfully');
        router.push('/simulations');
      } else {
        toast.error(response.error || 'Failed to create simulation');
      }
    } catch (err) {
      console.error('Error creating simulation:', err);
      toast.error('An unexpected error occurred');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="py-10">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl font-bold text-gray-900">Create New Simulation</h1>
            <button
              onClick={() => router.push('/dashboard')}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-100"
            >
              Cancel
            </button>
          </div>

          <form onSubmit={handleSubmit} className="bg-white shadow overflow-hidden rounded-lg">
            <div className="p-6 space-y-6">
              <div>
                <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                  Simulation Title
                </label>
                <input
                  type="text"
                  name="title"
                  id="title"
                  required
                  value={formData.title}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  placeholder="Enter a title for your simulation"
                />
              </div>

              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                  Description
                </label>
                <textarea
                  name="description"
                  id="description"
                  rows={3}
                  value={formData.description}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  placeholder="Describe the purpose of this simulation"
                />
              </div>

              <div className="border-t border-gray-200 pt-6">
                <h3 className="text-lg font-medium text-gray-900">System Parameters</h3>
                
                <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="panelHeight" className="block text-sm font-medium text-gray-700">
                      Panel Height (m)
                    </label>
                    <input
                      type="range"
                      name="panelHeight"
                      id="panelHeight"
                      min="1.5"
                      max="4.0"
                      step="0.1"
                      value={formData.parameters.panelHeight}
                      onChange={handleParameterChange}
                      className="mt-1 block w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>1.5m</span>
                      <span className="font-medium">{formData.parameters.panelHeight}m</span>
                      <span>4.0m</span>
                    </div>
                  </div>

                  <div>
                    <label htmlFor="panelAngle" className="block text-sm font-medium text-gray-700">
                      Panel Angle (degrees)
                    </label>
                    <input
                      type="range"
                      name="panelAngle"
                      id="panelAngle"
                      min="10"
                      max="40"
                      step="1"
                      value={formData.parameters.panelAngle}
                      onChange={handleParameterChange}
                      className="mt-1 block w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>10°</span>
                      <span className="font-medium">{formData.parameters.panelAngle}°</span>
                      <span>40°</span>
                    </div>
                  </div>

                  <div>
                    <label htmlFor="panelSpacing" className="block text-sm font-medium text-gray-700">
                      Panel Spacing (m)
                    </label>
                    <input
                      type="range"
                      name="panelSpacing"
                      id="panelSpacing"
                      min="3.0"
                      max="8.0"
                      step="0.1"
                      value={formData.parameters.panelSpacing}
                      onChange={handleParameterChange}
                      className="mt-1 block w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>3.0m</span>
                      <span className="font-medium">{formData.parameters.panelSpacing}m</span>
                      <span>8.0m</span>
                    </div>
                  </div>

                  <div>
                    <label htmlFor="cropType" className="block text-sm font-medium text-gray-700">
                      Crop Type
                    </label>
                    <select
                      name="cropType"
                      id="cropType"
                      value={formData.parameters.cropType}
                      onChange={handleParameterChange}
                      className="mt-1 block w-full rounded-md border border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    >
                      <option value="lettuce">Lettuce</option>
                      <option value="spinach">Spinach</option>
                      <option value="kale">Kale</option>
                      <option value="tomato">Tomato</option>
                      <option value="pepper">Pepper</option>
                    </select>
                  </div>

                  <div>
                    <label htmlFor="irrigationAmount" className="block text-sm font-medium text-gray-700">
                      Irrigation Amount (mm/day)
                    </label>
                    <input
                      type="range"
                      name="irrigationAmount"
                      id="irrigationAmount"
                      min="0"
                      max="10"
                      step="0.5"
                      value={formData.parameters.irrigationAmount}
                      onChange={handleParameterChange}
                      className="mt-1 block w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>0mm</span>
                      <span className="font-medium">{formData.parameters.irrigationAmount}mm</span>
                      <span>10mm</span>
                    </div>
                  </div>

                  <div>
                    <label htmlFor="trackingType" className="block text-sm font-medium text-gray-700">
                      Tracking Type
                    </label>
                    <select
                      name="trackingType"
                      id="trackingType"
                      value={formData.parameters.trackingType}
                      onChange={handleParameterChange}
                      className="mt-1 block w-full rounded-md border border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    >
                      <option value="fixed">Fixed</option>
                      <option value="single-axis">Single-Axis Tracking</option>
                      <option value="dual-axis">Dual-Axis Tracking</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <div className="px-6 py-4 bg-gray-50 text-right">
              <button
                type="submit"
                disabled={isSubmitting}
                className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-blue-300"
              >
                {isSubmitting ? 'Creating...' : 'Create Simulation'}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}