// Mock data generation function 
export const generateMockData = (variationFactor = 1) => {
    // This would be replaced with actual API data in a real implementation
    return {
      energyProduction: {
        totalAnnual: 42500 * variationFactor,
        averageDaily: 116.4 * variationFactor,
        peakDay: 232.8 * variationFactor,
        productionPerPanel: 425 * variationFactor,
        capacityFactor: 0.186 * variationFactor,
        systemSize: 25.0,
        performanceRatio: 0.78 * variationFactor,
        yearlyDegradation: 0.005,
        specificYield: 1700 * variationFactor,
        energyDensity: 4.25 * variationFactor,
        weatherImpact: {
          clearDay: 180 * variationFactor,
          partlyCloudyDay: 120 * variationFactor,
          cloudyDay: 60 * variationFactor,
          rainyDay: 30 * variationFactor,
          lossPercent: 0.15
        },
        monthlyProduction: [
          { month: 'Jan', energy: 2200 * variationFactor },
          { month: 'Feb', energy: 2800 * variationFactor },
          { month: 'Mar', energy: 3600 * variationFactor },
          { month: 'Apr', energy: 4200 * variationFactor },
          { month: 'May', energy: 4700 * variationFactor },
          { month: 'Jun', energy: 4800 * variationFactor },
          { month: 'Jul', energy: 4600 * variationFactor },
          { month: 'Aug', energy: 4300 * variationFactor },
          { month: 'Sep', energy: 3800 * variationFactor },
          { month: 'Oct', energy: 3200 * variationFactor },
          { month: 'Nov', energy: 2500 * variationFactor },
          { month: 'Dec', energy: 1800 * variationFactor }
        ],
        seasonalDistribution: [
          { name: 'Winter', value: 6800 * variationFactor },
          { name: 'Spring', value: 12500 * variationFactor },
          { name: 'Summer', value: 13700 * variationFactor },
          { name: 'Fall', value: 9500 * variationFactor }
        ],
        dailyPattern: Array.from({ length: 24 }, (_, i) => ({
          hour: i,
          summer: i < 6 || i > 20 ? 0 : Math.sin((i - 6) * Math.PI / 14) * 22 * variationFactor,
          winter: i < 8 || i > 18 ? 0 : Math.sin((i - 8) * Math.PI / 10) * 12 * variationFactor,
          spring: i < 7 || i > 19 ? 0 : Math.sin((i - 7) * Math.PI / 12) * 18 * variationFactor
        }))
      },
      cropYield: {
        totalAnnual: 5600 * variationFactor,
        yieldPerHarvest: 1400 * variationFactor,
        harvestCyclesPerYear: 4,
        yieldPerSqm: 0.56 * variationFactor,
        yieldVsOpenField: 0.85 * variationFactor,
        cropType: 'Lettuce',
        waterUsage: {
          totalAnnual: 3200 * variationFactor,
          perKgYield: 570 * variationFactor,
          savingsPercent: 0.22 * variationFactor,
          rainContribution: 35 * variationFactor,
          irrigationEfficiency: 0.85
        },
        harvestCycles: [
          { cycle: 'Spring', yield: 1350 * variationFactor },
          { cycle: 'Early Summer', yield: 1450 * variationFactor },
          { cycle: 'Late Summer', yield: 1500 * variationFactor },
          { cycle: 'Fall', yield: 1300 * variationFactor }
        ],
        growthFactors: [
          { month: 'Jan', temperature: 0.65, water: 0.8, light: 0.7, overall: 0.6 * variationFactor },
          { month: 'Feb', temperature: 0.7, water: 0.82, light: 0.72, overall: 0.65 * variationFactor },
          { month: 'Mar', temperature: 0.8, water: 0.85, light: 0.75, overall: 0.73 * variationFactor },
          { month: 'Apr', temperature: 0.9, water: 0.9, light: 0.78, overall: 0.82 * variationFactor },
          { month: 'May', temperature: 0.95, water: 0.88, light: 0.8, overall: 0.85 * variationFactor },
          { month: 'Jun', temperature: 0.92, water: 0.85, light: 0.82, overall: 0.84 * variationFactor },
          { month: 'Jul', temperature: 0.85, water: 0.8, light: 0.83, overall: 0.8 * variationFactor },
          { month: 'Aug', temperature: 0.88, water: 0.78, light: 0.81, overall: 0.78 * variationFactor },
          { month: 'Sep', temperature: 0.92, water: 0.83, light: 0.79, overall: 0.82 * variationFactor },
          { month: 'Oct', temperature: 0.85, water: 0.85, light: 0.75, overall: 0.75 * variationFactor },
          { month: 'Nov', temperature: 0.75, water: 0.87, light: 0.7, overall: 0.68 * variationFactor },
          { month: 'Dec', temperature: 0.65, water: 0.82, light: 0.68, overall: 0.62 * variationFactor }
        ],
        cropDetails: {
          growthPeriod: 60,
          optimalTempMin: 15,
          optimalTempMax: 25,
          waterRequirement: 4.5,
          shadeTolerance: 0.7,
          typicalYield: 3.2,
          actualGrowthPeriod: 65 * (1/variationFactor),
          temperatureStress: 0.12 * (1/variationFactor),
          waterStress: 0.08 * (1/variationFactor),
          lightStress: 0.15 * (1/variationFactor),
          actualYield: 2.72 * variationFactor
        }
      },
      shadowPatterns: {
        averageCoverage: 30 * variationFactor,
        maxShadowLength: 4.2 * variationFactor,
        minShadowLength: 1.8 * variationFactor,
        yieldImpact: -0.15 * (1/variationFactor),
        temperatureReduction: 3.5 * variationFactor,
        monthlyCoverage: [
          { month: 'Jan', coverage: 35 * variationFactor },
          { month: 'Feb', coverage: 33 * variationFactor },
          { month: 'Mar', coverage: 30 * variationFactor },
          { month: 'Apr', coverage: 28 * variationFactor },
          { month: 'May', coverage: 25 * variationFactor },
          { month: 'Jun', coverage: 23 * variationFactor },
          { month: 'Jul', coverage: 24 * variationFactor },
          { month: 'Aug', coverage: 26 * variationFactor },
          { month: 'Sep', coverage: 29 * variationFactor },
          { month: 'Oct', coverage: 32 * variationFactor },
          { month: 'Nov', coverage: 34 * variationFactor },
          { month: 'Dec', coverage: 36 * variationFactor }
        ]
      },
      financial: {
        totalCapex: 125000 * variationFactor,
        totalOpexAnnual: 7500 * variationFactor,
        energyRevenueAnnual: 5100 * variationFactor,
        cropRevenueAnnual: 14000 * variationFactor,
        totalRevenueAnnual: 19100 * variationFactor,
        netProfitAnnual: 11600 * variationFactor,
        paybackPeriod: 125000 / (11600 * variationFactor),
        profitMargin: 0.61 * variationFactor,
        roi: (11600 * 25 - 125000) / 125000 * 100 * variationFactor,
        npv: 160000 * variationFactor,
        irr: 0.092 * variationFactor,
        lcoe: 0.08 / variationFactor,
        systemLifetime: 25,
        lifetimeRevenue: 19100 * 25 * variationFactor,
        discountRate: 0.05,
        energyRevenuePercent: 5100 / 19100,
        capexBreakdown: [
          { name: 'Solar Panels', value: 50000 * variationFactor },
          { name: 'Mounting', value: 30000 * variationFactor },
          { name: 'Inverters', value: 15000 * variationFactor },
          { name: 'Installation', value: 20000 * variationFactor },
          { name: 'Agricultural Setup', value: 10000 * variationFactor }
        ],
        revenueBreakdown: [
          { name: 'Energy Sales', value: 5100 * variationFactor },
          { name: 'Crop Sales', value: 14000 * variationFactor }
        ],
        cashFlow: Array.from({ length: 26 }, (_, i) => ({
          year: i,
          annual: i === 0 ? -125000 : 11600 * variationFactor,
          cumulative: i === 0 ? -125000 : -125000 + 11600 * variationFactor * i
        })),
        sensitivityAnalysis: [
          { parameter: 'Energy Price', decrease: -12.8 * variationFactor, increase: 12.8 * variationFactor },
          { parameter: 'Crop Price', decrease: -34.2 * variationFactor, increase: 34.2 * variationFactor },
          { parameter: 'Panel Efficiency', decrease: -14.5 * variationFactor, increase: 13.2 * variationFactor },
          { parameter: 'Crop Yield', decrease: -30.1 * variationFactor, increase: 30.1 * variationFactor },
          { parameter: 'CAPEX', decrease: 25.6 * variationFactor, increase: -20.8 * variationFactor },
          { parameter: 'OPEX', decrease: 16.2 * variationFactor, increase: -16.2 * variationFactor }
        ]
      },
      environmental: {
        carbonEmissionsAvoided: Array.from({ length: 25 }, (_, i) => ({
          year: i + 1,
          annual: 21.25 * variationFactor,
          cumulative: 21.25 * (i + 1) * variationFactor
        })),
        systemCarbonFootprint: 25000 * variationFactor,
        netCarbonBenefit: (21250 * 25 - 25000) * variationFactor,
        carbonPaybackYears: 25000 / (21250 * variationFactor),
        equivalentTreesPlanted: 3200 * variationFactor,
        landUseEfficiency: 1.6 * variationFactor,
        dualPurposeLandArea: 10000,
        landSaved: 10000 * 0.6 * variationFactor,
        biodiversityIndex: 0.78 * variationFactor,
        topsoilPreservation: 0.92 * variationFactor,
        totalWaterUsage: 3200 * variationFactor,
        waterSavings: 900 * variationFactor,
        waterSavingsPercent: 22 * variationFactor,
        rainwaterUtilization: 0.35 * variationFactor,
        groundwaterImpact: 'Minimal',
        microclimateBenefits: {
          temperatureModeration: 3.5 * variationFactor,
          reducedEvapotranspiration: 22 * variationFactor,
          windReduction: 30 * variationFactor,
          humidityIncrease: 15 * variationFactor,
          soilErosionReduction: 40 * variationFactor
        },
        resourceEfficiency: [
          { resource: 'Land', saving: 38 * variationFactor },
          { resource: 'Water', saving: 22 * variationFactor },
          { resource: 'Energy', saving: 12 * variationFactor },
          { resource: 'Carbon', saving: 85 * variationFactor },
          { resource: 'Fertilizer', saving: 18 * variationFactor }
        ],
        waterUsage: Array.from({ length: 12 }, (_, i) => {
          const monthIndex = i;
          const rainfall = [120, 110, 100, 90, 70, 50, 40, 50, 70, 90, 100, 110][monthIndex] * variationFactor;
          const conventional = [350, 320, 300, 280, 320, 380, 400, 380, 320, 280, 300, 330][monthIndex] * variationFactor;
          const agrivoltaic = conventional * (1 - 0.22 * variationFactor);
          return {
            month: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][monthIndex],
            rainfall,
            conventional,
            agrivoltaic
          };
        })
      },
      monthlyComparison: Array.from({ length: 12 }, (_, i) => {
        const monthIndex = i;
        return {
          month: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][monthIndex],
          energyProduction: [2200, 2800, 3600, 4200, 4700, 4800, 4600, 4300, 3800, 3200, 2500, 1800][monthIndex] * variationFactor,
          cropYield: [320, 380, 520, 600, 580, 550, 520, 500, 510, 440, 380, 300][monthIndex] * variationFactor
        };
      }),
      landUseDistribution: [
        { name: 'Crop Area', value: 70 * variationFactor },
        { name: 'Panel Footprint', value: 15 * variationFactor },
        { name: 'Access Paths', value: 10 * variationFactor },
        { name: 'Infrastructure', value: 5 * variationFactor }
      ],
      configuration: {
        panelHeight: 2.5,
        panelAngle: 30,
        panelSpacing: 5.0,
        trackingType: 'Fixed',
        numPanels: 100,
        fieldSize: 10000,
        cropType: 'Lettuce',
        plantingDensity: 25,
        irrigationAmount: 5.0,
        irrigationEfficiency: 0.85
      },
      kpis: {
        energyCropRatio: 42500 / 5600 * variationFactor,
        systemEfficiency: 0.72 * variationFactor
      }
    };
  };
  
  // Import the EnergyTab component
  import React, { useState, useEffect } from 'react';
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
  
  // Example usage of both the data and component together
  import React, { useState, useEffect } from 'react';
  import { generateMockData } from './utils/mockData';
  import EnergyTab from './components/EnergyTab';
  
  const Dashboard = () => {
    const [mockData, setMockData] = useState(null);
    
    useEffect(() => {
      // Generate mock data when component mounts
      const data = generateMockData(1); // Default variation factor
      setMockData(data);
    }, []);
    
    if (!mockData) return <div>Loading...</div>;
    
    return (
      <div className="dashboard-container">
        <h1>Agrivoltaic System Dashboard</h1>
        
        <div className="tab-content">
          <EnergyTab data={mockData.energyProduction} />
        </div>
      </div>
    );
  };
  
  export default Dashboard;