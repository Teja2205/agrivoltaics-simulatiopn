import React, { useState, useEffect } from 'react';
import { RefreshCw, Settings, ChevronDown, ChevronUp } from 'lucide-react';
import toast from 'react-hot-toast';
import OverviewTab from './OverviewTab';
import EnergyTab from './EnergyTab';
import CropTab from './CropTab';
import FinancialTab from './FinancialTab';
import EnvironmentalTab from './EnvironmentalTab';
import StatCard from '../UI/StatCard';
import { api } from '../../services/api';
import styles from '../../styles/dashboard.module.css';

const AgrivoltaicsDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [simulationData, setSimulationData] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [showConfigPanel, setShowConfigPanel] = useState(false);
  const [simulationConfig, setSimulationConfig] = useState({
    panelHeight: 2.5,
    panelAngle: 30,
    panelSpacing: 5.0,
    cropType: 'lettuce',
    irrigationAmount: 5.0,
    trackingType: 'fixed',
  });

  // Fetch simulation data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await api.simulation.getSimulationData();
        if (response.data) {
          setSimulationData(response.data);
        } else if (response.error) {
          toast.error(response.error);
        }
      } catch (error) {
        console.error('Error fetching simulation data:', error);
        toast.error('Failed to load simulation data. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  // Run simulation with new config
  const runSimulation = async () => {
    setLoading(true);
    try {
      const response = await api.simulation.runSimulation(simulationConfig);
      if (response.data) {
        setSimulationData(response.data);
        setShowConfigPanel(false);
        toast.success('Simulation completed successfully');
      } else if (response.error) {
        toast.error(response.error);
      }
    } catch (error) {
      console.error('Error running simulation:', error);
      toast.error('Failed to run simulation. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle config changes
  const handleConfigChange = (e) => {
    const { name, value } = e.target;
    setSimulationConfig({
      ...simulationConfig,
      [name]: name === 'cropType' || name === 'trackingType' ? value : parseFloat(value),
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="text-center">
          <RefreshCw className="animate-spin h-12 w-12 text-blue-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-700">Loading simulation data...</h2>
          <p className="text-gray-500 mt-2">This may take a moment as we process the calculations.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <h1 className={styles.title}>Agrivoltaics Simulation Dashboard</h1>
          <p className={styles.subtitle}>
            Optimizing solar energy production and agricultural yield
          </p>
        </div>
      </header>
      
      {/* Main Content */}
      <main className={styles.mainContent}>
        {/* Top Stats */}
        <div className={styles.statContainer}>
          <StatCard 
            icon="zap"
            iconColor="text-yellow-500"
            value={`${Math.round(simulationData.energyProduction.totalAnnual).toLocaleString()} kWh`}
            label="Annual Energy Production"
          />
          <StatCard 
            icon="plant"
            iconColor="text-green-500"
            value={`${Math.round(simulationData.cropYield.totalAnnual).toLocaleString()} kg`}
            label="Annual Crop Yield"
          />
          <StatCard 
            icon="dollar-sign"
            iconColor="text-blue-500" 
            value={`$${Math.round(simulationData.financial.netProfitAnnual).toLocaleString()}`}
            label="Annual Net Profit"
          />
          <StatCard 
            icon="calendar"
            iconColor="text-purple-500"
            value={`${simulationData.financial.paybackPeriod.toFixed(1)} years`}
            label="Payback Period"
          />
        </div>
        
        {/* Tab Navigation */}
        <div className={styles.tabs}>
          <div 
            className={activeTab === 'overview' ? styles.activeTab : styles.tab}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </div>
          <div 
            className={activeTab === 'energy' ? styles.activeTab : styles.tab}
            onClick={() => setActiveTab('energy')}
          >
            Energy Production
          </div>
          <div 
            className={activeTab === 'crop' ? styles.activeTab : styles.tab}
            onClick={() => setActiveTab('crop')}
          >
            Crop Yield
          </div>
          <div 
            className={activeTab === 'financial' ? styles.activeTab : styles.tab}
            onClick={() => setActiveTab('financial')}
          >
            Financial Analysis
          </div>
          <div 
            className={activeTab === 'environmental' ? styles.activeTab : styles.tab}
            onClick={() => setActiveTab('environmental')}
          >
            Environmental Impact
          </div>
        </div>
        
        {/* Tab Content */}
        {activeTab === 'overview' && (
          <OverviewTab data={simulationData} />
        )}
        
        {activeTab === 'energy' && (
          <EnergyTab data={simulationData.energyProduction} />
        )}
        
        {activeTab === 'crop' && (
          <CropTab data={simulationData.cropYield} shadowData={simulationData.shadowPatterns} />
        )}
        
        {activeTab === 'financial' && (
          <FinancialTab data={simulationData.financial} />
        )}
        
        {activeTab === 'environmental' && (
          <EnvironmentalTab data={simulationData.environmental} />
        )}
        
        {/* Configuration Panel */}
        <div className={styles.card}>
          <div 
            className="flex justify-between items-center cursor-pointer"
            onClick={() => setShowConfigPanel(!showConfigPanel)}
          >
            <h2 className={styles.cardTitle}>
              <Settings className={styles.cardIcon} />
              System Configuration
            </h2>
            {showConfigPanel ? <ChevronUp /> : <ChevronDown />}
          </div>
          
          {showConfigPanel && (
            <div className="mt-4">
              <div className={styles.splitContainer}>
                <div>
                  <div className={styles.formGroup}>
                    <label className={styles.inputLabel}>Panel Height (m)</label>
                    <input
                      type="range"
                      name="panelHeight"
                      min="1.5"
                      max="4.0"
                      step="0.1"
                      value={simulationConfig.panelHeight}
                      onChange={handleConfigChange}
                      className={styles.slider}
                    />
                    <div className="flex justify-between">
                      <span>1.5m</span>
                      <span className="font-medium">{simulationConfig.panelHeight}m</span>
                      <span>4.0m</span>
                    </div>
                  </div>
                  
                  <div className={styles.formGroup}>
                    <label className={styles.inputLabel}>Panel Angle (degrees)</label>
                    <input
                      type="range"
                      name="panelAngle"
                      min="10"
                      max="40"
                      step="1"
                      value={simulationConfig.panelAngle}
                      onChange={handleConfigChange}
                      className={styles.slider}
                    />
                    <div className="flex justify-between">
                      <span>10°</span>
                      <span className="font-medium">{simulationConfig.panelAngle}°</span>
                      <span>40°</span>
                    </div>
                  </div>
                  
                  <div className={styles.formGroup}>
                    <label className={styles.inputLabel}>Panel Spacing (m)</label>
                    <input
                      type="range"
                      name="panelSpacing"
                      min="3.0"
                      max="8.0"
                      step="0.1"
                      value={simulationConfig.panelSpacing}
                      onChange={handleConfigChange}
                      className={styles.slider}
                    />
                    <div className="flex justify-between">
                      <span>3.0m</span>
                      <span className="font-medium">{simulationConfig.panelSpacing}m</span>
                      <span>8.0m</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <div className={styles.formGroup}>
                    <label className={styles.inputLabel}>Crop Type</label>
                    <select
                      name="cropType"
                      value={simulationConfig.cropType}
                      onChange={handleConfigChange}
                      className={styles.select}
                    >
                      <option value="lettuce">Lettuce</option>
                      <option value="spinach">Spinach</option>
                      <option value="kale">Kale</option>
                      <option value="tomato">Tomato</option>
                      <option value="pepper">Pepper</option>
                    </select>
                  </div>
                  
                  <div className={styles.formGroup}>
                    <label className={styles.inputLabel}>Irrigation Amount (mm/day)</label>
                    <input
                      type="range"
                      name="irrigationAmount"
                      min="0"
                      max="10"
                      step="0.5"
                      value={simulationConfig.irrigationAmount}
                      onChange={handleConfigChange}
                      className={styles.slider}
                    />
                    <div className="flex justify-between">
                      <span>0mm</span>
                      <span className="font-medium">{simulationConfig.irrigationAmount}mm</span>
                      <span>10mm</span>
                    </div>
                  </div>
                  
                  <div className={styles.formGroup}>
                    <label className={styles.inputLabel}>Tracking Type</label>
                    <select
                      name="trackingType"
                      value={simulationConfig.trackingType}
                      onChange={handleConfigChange}
                      className={styles.select}
                    >
                      <option value="fixed">Fixed</option>
                      <option value="single-axis">Single-Axis Tracking</option>
                      <option value="dual-axis">Dual-Axis Tracking</option>
                    </select>
                  </div>
                </div>
              </div>
              
              <div className="flex justify-end mt-6">
                <button
                  className="mr-2 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-lg"
                  onClick={() => setShowConfigPanel(false)}
                >
                  Cancel
                </button>
                <button
                  className="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-lg"
                  onClick={runSimulation}
                >
                  Run Simulation
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default AgrivoltaicsDashboard;