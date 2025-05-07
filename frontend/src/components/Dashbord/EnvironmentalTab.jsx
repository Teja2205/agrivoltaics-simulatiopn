import React from 'react';
import { Droplet, BarChart2, AlertTriangle, Wind } from 'lucide-react';
import { 
  AreaChart, Area, BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import styles from '../../styles/dashboard.module.css';

const EnvironmentalTab = ({ data }) => {
  return (
    <div>
      <div className={styles.splitContainer}>
        {/* Carbon Emissions Avoided */}
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>
            <BarChart2 className={styles.cardIcon} />
            Carbon Emissions Avoided (Over System Lifetime)
          </h2>
          <div className={styles.chartContainer}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={data.carbonEmissionsAvoided}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis tickFormatter={(value) => `${value.toFixed(1)} tons`} />
                <Tooltip 
                  formatter={(value) => [`${value.toFixed(2)} tons CO₂`, '']} 
                  labelFormatter={(label) => `Year ${label}`}
                />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="annual"
                  stroke="#26a69a"
                  fill="#80cbc4"
                  name="Annual CO₂ Avoided"
                />
                <Area
                  type="monotone"
                  dataKey="cumulative"
                  stroke="#00796b"
                  fill="#b2dfdb"
                  name="Cumulative CO₂ Avoided"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        {/* Land & Water Use Efficiency */}
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>
            <BarChart2 className={styles.cardIcon} />
            Resource Efficiency Comparison
          </h2>
          <div className={styles.chartContainer}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data.resourceEfficiency}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="resource" />
                <YAxis tickFormatter={(value) => `${value}%`} />
                <Tooltip formatter={(value) => [`${value}%`, '']} />
                <Legend />
                <Bar 
                  dataKey="saving" 
                  name="Resource Saving" 
                  fill="#26a69a"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      {/* Water Usage Comparison */}
      <div className={styles.card}>
        <h2 className={styles.cardTitle}>
          <Droplet className={styles.cardIcon} />
          Water Usage Comparison (Monthly)
        </h2>
        <div className={styles.chartContainer}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={data.waterUsage}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis tickFormatter={(value) => `${value} m³`} />
              <Tooltip formatter={(value) => [`${value} m³`, '']} />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="conventional" 
                name="Conventional Agriculture" 
                stroke="#f44336" 
                strokeWidth={2} 
              />
              <Line 
                type="monotone" 
                dataKey="agrivoltaic" 
                name="Agrivoltaic System" 
                stroke="#4caf50" 
                strokeWidth={2} 
              />
              <Line 
                type="monotone" 
                dataKey="rainfall" 
                name="Rainfall Contribution" 
                stroke="#2196f3" 
                strokeWidth={2}
                strokeDasharray="5 5"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* Environmental Metrics */}
      <div className={styles.threeColContainer}>
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>
            <AlertTriangle className={styles.cardIcon} />
            Carbon Metrics
          </h2>
          <ul className="space-y-3">
            <li className="flex justify-between border-b pb-2">
              <span className="text-gray-600">Carbon Emissions Avoided:</span>
              <span className="font-medium">{Math.round(data.carbonEmissionsAvoided[24].cumulative).toLocaleString()} tons CO₂</span>
            </li>
            <li className="flex justify-between border-b pb-2">
              <span className="text-gray-600">System Carbon Footprint:</span>
              <span className="font-medium">{Math.round(data.systemCarbonFootprint).toLocaleString()} kg CO₂</span>
            </li>
            <li className="flex justify-between border-b pb-2">
              <span className="text-gray-600">Net Carbon Benefit:</span>
              <span className="font-medium">{Math.round(data.netCarbonBenefit).toLocaleString()} kg CO₂</span>
            </li>
            <li className="flex justify-between border-b pb-2">
              <span className="text-gray-600">Carbon Payback:</span>
              <span className="font-medium">{data.carbonPaybackYears.toFixed(1)} years</span>
            </li>
            <li className="flex justify-between">
              <span className="text-gray-600">Equivalent Trees Planted:</span>
              <span className="font-medium">{Math.round(data.equivalentTreesPlanted).toLocaleString()}</span>
            </li>
          </ul>
        </div>
        
        {/* Additional environmental metrics sections... */}
      </div>
    </div>
  );
};

export default EnvironmentalTab;