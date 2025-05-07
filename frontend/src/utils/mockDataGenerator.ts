export const generateMockData = (variationFactor = 1) => {
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
      ]
    }
  };
};
