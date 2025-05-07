import React from 'react';
import { BarChart2, PieChartIcon, Sliders, HelpCircle, Plant } from 'lucide-react';
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts';
import styles from '../../styles/dashboard.module.css';
import { colors } from '../../utils/chartColors';

const OverviewTab = ({ data }) => {
  return (
    <div>
      <div className={styles.splitContainer}>
        {/* Energy vs Crop Production */}
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>
            <BarChart2 className={styles.cardIcon} />
            Energy Production vs Crop Yield (Monthly)
          </h2>
          <div className={styles.chartContainer}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data.monthlyComparison}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis yAxisId="left" orientation="left" stroke="#f9a825" />
                <YAxis yAxisId="right" orientation="right" stroke="#43a047" />
                <Tooltip />
                <Legend />
                <Bar yAxisId="left" dataKey="energyProduction" name="Energy (kWh)" fill="#f9a825" />
                <Bar yAxisId="right" dataKey="cropYield" name="Crop Yield (kg)" fill="#43a047" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        {/* Shadow Pattern */}
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>
            <PieChartIcon className={styles.cardIcon} />
            Land Use Distribution
          </h2>
          <div className="mb-4 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-medium mb-2">Land Use Efficiency: {(data.environmental.landUseEfficiency * 100).toFixed(1)}%</h3>
            <p className="text-gray-600">
              This system uses {data.environmental.dualPurposeLandArea}m² of land to produce both energy and crops,
              compared to {Math.round(data.environmental.dualPurposeLandArea / data.environmental.landUseEfficiency)}m²
              if the two systems were separate.
            </p>
          </div>
          <div className={styles.chartContainer}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.landUseDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {data.landUseDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={colors.environmental[index % colors.environmental.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value, name) => [value, name]} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      {/* Configuration Summary */}
      <div className={styles.card}>
        <h2 className={styles.cardTitle}>
          <Sliders className={styles.cardIcon} />
          System Configuration Summary
        </h2>
        <div className={styles.threeColContainer}>
          {/* Solar Panel Configuration */}
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-medium mb-3">Solar Configuration</h3>
            <ul className="space-y-2">
              <li className="flex justify-between">
                <span className="text-gray-600">Panel Height:</span>
                <span className="font-medium">{data.configuration.panelHeight}m</span>
              </li>
              <li className="flex justify-between">
                <span className="text-gray-600">Panel Angle:</span>
                <span className="font-medium">{data.configuration.panelAngle}°</span>
              </li>
              <li className="flex justify-between">
                <span className="text-gray-600">Panel Spacing:</span>
                <span className="font-medium">{data.configuration.panelSpacing}m</span>
              </li>
              <li className="flex justify-between">
                <span className="text-gray-600">Tracking Type:</span>
                <span className="font-medium">{data.configuration.trackingType}</span>
              </li>
              <li className="flex justify-between">
                <span className="text-gray-600">Number of Panels:</span>
                <span className="font-medium">{data.configuration.numPanels}</span>
              </li>
            </ul>
          </div>
          
          {/* Agricultural Configuration */}
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-medium mb-3">Agricultural Configuration</h3>
            <ul className="space-y-2">
              <li className="flex justify-between">
                <span className="text-gray-600">Crop Type:</span>
                <span className="font-medium">{data.configuration.cropType}</span>
              </li>
              <li className="flex justify-between">
                <span className="text-gray-600">Field Size:</span>
                <span className="font-medium">{data.configuration.fieldSize}m²</span>
              </li>
              <li className="flex justify-between">
                <span className="text-gray-600">Planting Density:</span>
                <span className="font-medium">{data.configuration.plantingDensity} plants/m²</span>
              </li>
              <li className="flex justify-between">
                <span className="text-gray-600">Irrigation Amount:</span>
                <span className="font-medium">{data.configuration.irrigationAmount}mm/day</span>
              </li>
              <li className="flex justify-between">
                <span className="text-gray-600">Irrigation Efficiency:</span>
                <span className="font-medium">{data.configuration.irrigationEfficiency * 100}%</span>
              </li>
            </ul>
          </div>
          
          {/* Key Performance Indicators */}
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-medium mb-3">Key Performance Indicators</h3>
            <ul className="space-y-2">
              <li className="flex justify-between">
                <span className="text-gray-600">Energy-Crop Ratio:</span>
                <span className="font-medium">{data.kpis.energyCropRatio.toFixed(2)}</span>
              </li>
              <li className="flex justify-between">
                <span className="text-gray-600">System Efficiency:</span>
                <span className="font-medium">{(data.kpis.systemEfficiency * 100).toFixed(1)}%</span>
              </li>
              <li className="flex justify-between">
                <span className="text-gray-600">ROI:</span>
                <span className="font-medium">{data.financial.roi.toFixed(1)}%</span>
              </li>
              <li className="flex justify-between">
                <span className="text-gray-600">Water Savings:</span>
                <span className="font-medium">{data.environmental.waterSavingsPercent.toFixed(1)}%</span>
              </li>
              <li className="flex justify-between">
                <span className="text-gray-600">Carbon Offset:</span>
                <span className="font-medium">{Math.round(data.environmental.carbonEmissionsAvoided)} kg CO₂</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
      
      {/* System Insights */}
      <div className={styles.card}>
        <h2 className={styles.cardTitle}>
          <HelpCircle className={styles.cardIcon} />
          System Insights
        </h2>
        <div className="space-y-4">
          <div className={`${styles.alertContainer} ${styles.alertSuccess}`}>
            <h3 className="font-medium mb-1">Optimization Opportunities</h3>
            <p>The current configuration achieves a good balance between energy production and crop yield.
               Adjusting the panel height by +0.3m could further improve crop yield with minimal impact on energy production.</p>
          </div>
          
          <div className={`${styles.alertContainer} ${styles.alertWarning}`}>
            <h3 className="font-medium mb-1">Climate Considerations</h3>
            <p>The summer months show a 15% drop in crop yield due to higher temperatures. Consider adjusting
               irrigation schedules or implementing shade cloth during peak summer periods.</p>
          </div>
          
          <div className={`${styles.alertContainer} ${styles.alertInfo}`}>
            <h3 className="font-medium mb-1">Financial Projection</h3>
            <p>With current market prices, the system will reach break-even in {data.financial.paybackPeriod.toFixed(1)} years.
               Energy sales account for {(data.financial.energyRevenuePercent * 100).toFixed(0)}% of total revenue.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OverviewTab;