// Create components/UI/StatCard.jsx
import React from 'react';
import { 
  Zap, Plant, DollarSign, Calendar, 
  Cloud, Activity, Wind, Share2
} from 'lucide-react';

const iconMap = {
  zap: Zap,
  plant: Plant,
  "dollar-sign": DollarSign,
  calendar: Calendar,
  cloud: Cloud,
  activity: Activity,
  wind: Wind,
  share2: Share2
};

const StatCard = ({ icon, iconColor, value, label }) => {
  const IconComponent = iconMap[icon] || Zap;
  
  return (
    <div className="bg-white rounded-lg shadow p-5">
      <div className="flex items-center mb-2">
        <IconComponent className={`${iconColor} h-6 w-6 mr-2`} />
        <span className="text-gray-700 font-medium">{label}</span>
      </div>
      <div className="text-2xl font-bold">{value}</div>
    </div>
  );
};

export default StatCard;