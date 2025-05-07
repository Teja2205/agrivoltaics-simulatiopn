import React from 'react';
import { DollarSign, BarChart2, PieChart as PieChartIcon } from 'lucide-react';
import { 
  AreaChart, Area, BarChart, Bar, PieChart, Pie, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell, ReferenceLine
} from 'recharts';
import styles from '../../styles/dashboard.module.css';
import { colors } from '../../utils/chartColors';

const FinancialTab = ({ data }) => {
  return (
    <div>
      <div className={styles.splitContainer}>
        {/* Capital vs Operating Expenses */}
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>
            <PieChartIcon className={styles.cardIcon} />
            Capital Expenses Breakdown
          </h2>
          <div className={styles.chartContainer}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.capexBreakdown}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {data.capexBreakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={colors.financial[index % colors.financial.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`${value.toLocaleString()}`, '']} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        {/* Revenue Breakdown */}
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>
            <PieChartIcon className={styles.cardIcon} />
            Annual Revenue Breakdown
          </h2>
          <div className={styles.chartContainer}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.revenueBreakdown}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {data.revenueBreakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={colors.crop[index % colors.crop.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`${value.toLocaleString()}`, '']} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      {/* Cash Flow */}
      <div className={styles.card}>
        <h2 className={styles.cardTitle}>
          <BarChart2 className={styles.cardIcon} />
          Projected Cash Flow (25 Years)
        </h2>
        <div className={styles.chartContainer}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={data.cashFlow}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`} />
              <Tooltip formatter={(value) => [`${value.toLocaleString()}`, '']} />
              <Legend />
              <ReferenceLine y={0} stroke="#000" />
              <Area
                type="monotone"
                dataKey="cumulative"
                name="Cumulative Cash Flow"
                stroke="#1e88e5"
                fill="#90caf9"
              />
              <Area
                type="monotone"
                dataKey="annual"
                name="Annual Cash Flow"
                stroke="#43a047"
                fill="#a5d6a7"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* Financial Metrics */}
      <div className={styles.threeColContainer}>
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>
            <DollarSign className={styles.cardIcon} />
            Investment Metrics
          </h2>
          <ul className="space-y-3">
            <li className="flex justify-between border-b pb-2">
              <span className="text-gray-600">Total CAPEX:</span>
              <span className="font-medium">${Math.round(data.totalCapex).toLocaleString()}</span>
            </li>
            <li className="flex justify-between border-b pb-2">
              <span className="text-gray-600">Annual OPEX:</span>
              <span className="font-medium">${Math.round(data.totalOpexAnnual).toLocaleString()}</span>
            </li>
            <li className="flex justify-between border-b pb-2">
              <span className="text-gray-600">LCOE:</span>
              <span className="font-medium">${data.lcoe.toFixed(3)}/kWh</span>
            </li>
            <li className="flex justify-between border-b pb-2">
              <span className="text-gray-600">Payback Period:</span>
              <span className="font-medium">{data.paybackPeriod.toFixed(1)} years</span>
            </li>
            <li className="flex justify-between">
              <span className="text-gray-600">ROI:</span>
              <span className="font-medium">{data.roi.toFixed(1)}%</span>
            </li>
          </ul>
        </div>
        
        {/* More financial metrics sections... */}
        
        {/* Sensitivity Analysis */}
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>
            <BarChart2 className={styles.cardIcon} />
            Sensitivity Analysis
          </h2>
          <p className="mb-4 text-gray-600">
            This chart shows how changes in key parameters affect the project's ROI.
          </p>
          <div className={styles.chartContainer}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data.sensitivityAnalysis}
                layout="vertical"
                margin={{ top: 20, right: 30, left: 150, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={['dataMin', 'dataMax']} />
                <YAxis type="category" dataKey="parameter" width={140} />
                <Tooltip formatter={(value) => [`${value.toFixed(2)}% change in ROI`, '']} />
                <Legend />
                <Bar dataKey="decrease" name="-10% Parameter Change" fill="#ef5350" />
                <Bar dataKey="increase" name="+10% Parameter Change" fill="#66bb6a" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FinancialTab;