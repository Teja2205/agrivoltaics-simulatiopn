import React from 'react';
import { Plant, Thermometer, Droplet } from 'lucide-react';
import { 
  BarChart, Bar, LineChart, Line, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts';
import styles from '../../styles/dashboard.module.css';
import { colors } from '../../utils/chartColors';

const CropTab = ({ data, shadowData }) => {
  return (
    <div>
      <div className={styles.splitContainer}>
        {/* Harvest Cycle Yields */}
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>
            <BarChart2 className={styles.cardIcon} />
            Harvest Cycle Yields
          </h2>
          <div className={styles.chartContainer}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data.harvestCycles}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="cycle" />
                <YAxis />
                <Tooltip formatter={(value) => [`${value} kg`, 'Yield']} />
                <Bar dataKey="yield" name="Yield (kg)" fill="#43a047">
                  {data.harvestCycles.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={colors.crop[index % 4]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        {/* Shadow Coverage */}
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>
            <BarChart2 className={styles.cardIcon} />
            Shadow Coverage by Month
          </h2>
          <div className={styles.chartContainer}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={shadowData.monthlyCoverage}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis tickFormatter={(value) => `${value}%`} />
                <Tooltip formatter={(value) => [`${value}%`, 'Shadow Coverage']} />
                <Area 
                  type="monotone" 
                  dataKey="coverage" 
                  stroke="#5e35b1" 
                  fill="#9575cd" 
                  name="Shadow Coverage"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      {/* Crop Growth Factors */}
      <div className={styles.card}>
        <h2 className={styles.cardTitle}>
          <BarChart2 className={styles.cardIcon} />
          Crop Growth Factors
        </h2>
        <div className={styles.chartContainer}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={data.growthFactors}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis domain={[0, 1]} tickFormatter={(value) => `${(value * 100).toFixed(0)}%`} />
              <Tooltip formatter={(value) => [`${(value * 100).toFixed(1)}%`, '']} />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="temperature" 
                name="Temperature Suitability" 
                stroke="#f44336" 
                strokeWidth={2} 
              />
              <Line 
                type="monotone" 
                dataKey="water" 
                name="Water Availability" 
                stroke="#2196f3" 
                strokeWidth={2} 
              />
              <Line 
                type="monotone" 
                dataKey="light" 
                name="Light Conditions" 
                stroke="#ffc107" 
                strokeWidth={2}
              />
              <Line 
                type="monotone" 
                dataKey="overall" 
                name="Overall Growth Factor" 
                stroke="#4caf50" 
                strokeWidth={3}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* Crop Metrics and Crop Details */}
      <div className={styles.card}>
        <h2 className={styles.cardTitle}>
          <Plant className={styles.cardIcon} />
          Crop Details - {data.cropType}
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
          <div>
            <h3 className="text-lg font-medium mb-3">Growth Characteristics</h3>
            <ul className="space-y-2">
              <li className="flex justify-between">
                <span className="text-gray-600">Growth Period:</span>
                <span className="font-medium">{data.cropDetails.growthPeriod} days</span>
              </li>
              <li className="flex justify-between">
                <span className="text-gray-600">Optimal Temperature:</span>
                <span className="font-medium">{data.cropDetails.optimalTempMin}°C - {data.cropDetails.optimalTempMax}°C</span>
              </li>
              <li className="flex justify-between">
                <span className="text-gray-600">Water Requirement:</span>
                <span className="font-medium">{data.cropDetails.waterRequirement} mm/day</span>
              </li>
              <li className="flex justify-between">
                <span className="text-gray-600">Shade Tolerance:</span>
                <span className="font-medium">{(data.cropDetails.shadeTolerance * 100).toFixed(0)}%</span>
              </li>
              <li className="flex justify-between">
                <span className="text-gray-600">Typical Yield:</span>
                <span className="font-medium">{data.cropDetails.typicalYield} kg/m²</span>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-lg font-medium mb-3">Performance in Agrivoltaic System</h3>
            <ul className="space-y-2">
              <li className="flex justify-between">
                <span className="text-gray-600">Actual Growth Period:</span>
                <span className="font-medium">{data.cropDetails.actualGrowthPeriod} days</span>
              </li>
              <li className="flex justify-between">
                <span className="text-gray-600">Temperature Stress:</span>
                <span className="font-medium">{(data.cropDetails.temperatureStress * 100).toFixed(1)}%</span>
              </li>
              <li className="flex justify-between">
                <span className="text-gray-600">Water Stress:</span>
                <span className="font-medium">{(data.cropDetails.waterStress * 100).toFixed(1)}%</span>
              </li>
              <li className="flex justify-between">
                <span className="text-gray-600">Light Stress:</span>
                <span className="font-medium">{(data.cropDetails.lightStress * 100).toFixed(1)}%</span>
              </li>
              <li className="flex justify-between">
                <span className="text-gray-600">Actual Yield:</span>
                <span className="font-medium">{data.cropDetails.actualYield} kg/m²</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CropTab;