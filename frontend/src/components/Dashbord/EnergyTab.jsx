import React from 'react';
import { Sun, CloudRain, Zap, BarChart2, PieChart as PieChartIcon } from 'lucide-react';
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts';
import styles from '../../styles/dashboard.module.css';
import { colors } from '../../utils/chartColors';

const EnergyTab = ({ data }) => {
  return (
    <div>
      <div className={styles.splitContainer}>
        {/* Monthly Energy Production */}
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>
            <BarChart2 className={styles.cardIcon} />
            Monthly Energy Production
          </h2>
          <div className={styles.chartContainer}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data.monthlyProduction}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => [`${value} kWh`, 'Energy']} />
                <Bar dataKey="energy" name="Energy (kWh)" fill="#f9a825">
                  {data.monthlyProduction.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={colors.energy[index % 4]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        {/* Energy Distribution */}
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>
            <PieChartIcon className={styles.cardIcon} />
            Energy Distribution by Season
          </h2>
          <div className={styles.chartContainer}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.seasonalDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {data.seasonalDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={colors.energy[index % colors.energy.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value, name) => [`${value} kWh`, name]} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      {/* Daily Production Pattern */}
      <div className={styles.card}>
        <h2 className={styles.cardTitle}>
          <BarChart2 className={styles.cardIcon} />
          Daily Production Pattern (Sample Week)
        </h2>
        <div className={styles.chartContainer}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={data.dailyPattern}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip formatter={(value) => [`${value} kW`, 'Power']} />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="summer" 
                name="Summer Day" 
                stroke="#f9a825" 
                strokeWidth={2} 
                dot={false} 
              />
              <Line 
                type="monotone" 
                dataKey="winter" 
                name="Winter Day" 
                stroke="#90caf9" 
                strokeWidth={2} 
                dot={false} 
              />
              <Line 
                type="monotone" 
                dataKey="spring" 
                name="Spring/Fall Day" 
                stroke="#66bb6a" 
                strokeWidth={2} 
                dot={false} 
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* Energy Metrics */}
      <div className={styles.threeColContainer}>
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>
            <Sun className={styles.cardIcon} />
            Production Metrics
          </h2>
          <ul className="space-y-3">
            <li className="flex justify-between border-b pb-2">
              <span className="text-gray-600">Annual Production:</span>
              <span className="font-medium">{Math.round(data.totalAnnual).toLocaleString()} kWh</span>
            </li>
            <li className="flex justify-between border-b pb-2">
              <span className="text-gray-600">Average Daily Production:</span>
              <span className="font-medium">{Math.round(data.averageDaily).toLocaleString()} kWh</span>
            </li>
            <li className="flex justify-between border-b pb-2">
              <span className="text-gray-600">Peak Production Day:</span>
              <span className="font-medium">{Math.round(data.peakDay).toLocaleString()} kWh</span>
            </li>
            <li className="flex justify-between border-b pb-2">
              <span className="text-gray-600">Production per Panel:</span>
              <span className="font-medium">{Math.round(data.productionPerPanel).toLocaleString()} kWh</span>
            </li>
            <li className="flex justify-between">
              <span className="text-gray-600">Capacity Factor:</span>
              <span className="font-medium">{(data.capacityFactor * 100).toFixed(1)}%</span>
            </li>
          </ul>
        </div>
        
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>
            <Zap className={styles.cardIcon} />
            Performance Analysis
          </h2>
          <ul className="space-y-3">
            <li className="flex justify-between border-b pb-2">
              <span className="text-gray-600">System Size:</span>
              <span className="font-medium">{data.systemSize.toFixed(1)} kW</span>
            </li>
            <li className="flex justify-between border-b pb-2">
              <span className="text-gray-600">Performance Ratio:</span>
              <span className="font-medium">{(data.performanceRatio * 100).toFixed(1)}%</span>
            </li>
            <li className="flex justify-between border-b pb-2">
              <span className="text-gray-600">Yearly Degradation:</span>
              <span className="font-medium">{(data.yearlyDegradation * 100).toFixed(2)}%</span>
            </li>
            <li className="flex justify-between border-b pb-2">
              <span className="text-gray-600">Specific Yield:</span>
              <span className="font-medium">{Math.round(data.specificYield)} kWh/kWp</span>
            </li>
            <li className="flex justify-between">
              <span className="text-gray-600">Energy Density:</span>
              <span className="font-medium">{data.energyDensity.toFixed(1)} kWh/m²</span>
            </li>
          </ul>
        </div>
        
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>
            <CloudRain className={styles.cardIcon} />
            Weather Impact
          </h2>
          <ul className="space-y-3">
            <li className="flex justify-between border-b pb-2">
              <span className="text-gray-600">Clear Day Production:</span>
              <span className="font-medium">{Math.round(data.weatherImpact.clearDay).toLocaleString()} kWh</span>
            </li>
            <li className="flex justify-between border-b pb-2">
              <span className="text-gray-600">Partly Cloudy Production:</span>
              <span className="font-medium">{Math.round(data.weatherImpact.partlyCloudyDay).toLocaleString()} kWh</span>
            </li>
            <li className="flex justify-between border-b pb-2">
              <span className="text-gray-600">Cloudy Day Production:</span>
              <span className="font-medium">{Math.round(data.weatherImpact.cloudyDay).toLocaleString()} kWh</span>
            </li>
            <li className="flex justify-between border-b pb-2">
              <span className="text-gray-600">Rainy Day Production:</span>
              <span className="font-medium">{Math.round(data.weatherImpact.rainyDay).toLocaleString()} kWh</span>
            </li>
            <li className="flex justify-between">
              <span className="text-gray-600">Production Lost to Weather:</span>
              <span className="font-medium">{(data.weatherImpact.lossPercent * 100).toFixed(1)}%</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default EnergyTab;