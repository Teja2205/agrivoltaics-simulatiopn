import numpy as np
import pandas as pd
import tensorflow as tf
import xgboost as xgb
import joblib
import os
import logging
from typing import Dict, Any, List, Optional, Tuple

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class MLService:
    """Service for machine learning predictions"""
    
    def __init__(self, model_path=None):
        """Initialize ML service with model path"""
        self.model_path = model_path or os.path.join(settings.BASE_DIR, "models")
        self.energy_model = None
        self.crop_model = None
        self.optimization_model = None
        
        # Create models directory if it doesn't exist
        os.makedirs(self.model_path, exist_ok=True)
        
        # Load models if they exist
        self._load_models()
    
    def _load_models(self):
        """Load ML models from disk"""
        try:
            # Load energy prediction model
            energy_model_path = os.path.join(self.model_path, "energy_model.h5")
            if os.path.exists(energy_model_path):
                self.energy_model = tf.keras.models.load_model(energy_model_path)
                logger.info("Loaded energy prediction model")
            else:
                logger.warning("Energy prediction model not found, will use simplified model")
            
            # Load crop prediction model
            crop_model_path = os.path.join(self.model_path, "crop_model.h5")
            if os.path.exists(crop_model_path):
                self.crop_model = tf.keras.models.load_model(crop_model_path)
                logger.info("Loaded crop prediction model")
            else:
                logger.warning("Crop prediction model not found, will use simplified model")
            
            # Load optimization model
            opt_model_path = os.path.join(self.model_path, "optimization_model.pkl")
            if os.path.exists(opt_model_path):
                self.optimization_model = joblib.load(opt_model_path)
                logger.info("Loaded optimization model")
            else:
                logger.warning("Optimization model not found, will use simplified model")
        
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            # Continue with simplified models
    
    def predict_energy_production(
        self, weather_data: pd.DataFrame, config: Dict[str, Any]
    ) -> List[float]:
        """
        Predict daily energy production based on weather and system configuration
        
        Args:
            weather_data: DataFrame with weather information
            config: System configuration parameters
            
        Returns:
            List of daily energy production values in kWh
        """
        if self.energy_model:
            # Prepare input features
            X = self._prepare_energy_features(weather_data, config)
            
            # Make predictions
            predictions = self.energy_model.predict(X)
            
            # Return daily energy values
            return predictions.flatten().tolist()
        else:
            # Fallback to simplified model
            return self._simplified_energy_model(weather_data, config)
    
    def predict_crop_growth(
        self, weather_data: pd.DataFrame, config: Dict[str, Any], crop_data: Dict[str, Any]
    ) -> List[float]:
        """
        Predict daily crop growth factors
        
        Args:
            weather_data: DataFrame with weather information
            config: System configuration parameters
            crop_data: Crop-specific parameters
            
        Returns:
            List of daily growth factors (0-1 scale)
        """
        if self.crop_model:
            # Prepare input features
            X = self._prepare_crop_features(weather_data, config, crop_data)
            
            # Make predictions
            predictions = self.crop_model.predict(X)
            
            # Return daily growth factors
            return predictions.flatten().tolist()
        else:
            # Fallback to simplified model
            return self._simplified_crop_growth_model(weather_data, config, crop_data)
    
    def predict_crop_yield(
        self, daily_growth: List[float], config: Dict[str, Any], crop_data: Dict[str, Any]
    ) -> float:
        """
        Predict total crop yield based on daily growth factors
        
        Args:
            daily_growth: List of daily growth factors
            config: System configuration parameters
            crop_data: Crop-specific parameters
            
        Returns:
            Total yield in kg
        """
        # Calculate base yield potential
        planting_density = config.get("planting_density", 25)  # plants per m²
        field_size = config.get("field_size", 10000)  # m²
        base_yield = crop_data["typical_yield_per_plant"] * planting_density * field_size
        
        # Calculate effective growth factor
        growth_period = min(crop_data["growth_period_days"], len(daily_growth))
        avg_growth_factor = sum(daily_growth[:growth_period]) / growth_period
        
        # Apply growth factor to base yield
        return base_yield * avg_growth_factor
    
    def calculate_shadow_patterns(
        self, weather_data: List[Dict[str, Any]], config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate shadow patterns based on panel configuration and weather
        
        Args:
            weather_data: List of weather data dictionaries
            config: System configuration parameters
            
        Returns:
            Dictionary with shadow pattern information
        """
        # Extract parameters
        panel_height = config.get("panel_height", 2.5)  # meters
        panel_width = config.get("panel_width", 1.0)  # meters
        panel_angle = config.get("panel_angle", 30)  # degrees
        panel_spacing = config.get("panel_spacing", 5.0)  # meters
        panel_rows = config.get("panel_rows", 10)
        panels_per_row = config.get("panels_per_row", 10)
        latitude = config.get("latitude", 40.0)
        
        # Calculate shadow for each day
        shadow_lengths = []
        shadow_areas = []
        shadow_coverages = []
        
        for i, day in enumerate(weather_data):
            # Day of year
            day_of_year = i % 365
            
            # Calculate solar positions throughout the day
            day_shadows = []
            
            # For simplicity, calculate shadow at noon
            # In a real model, we would calculate for multiple times of day
            declination = 23.45 * np.sin(np.radians(360/365 * (day_of_year - 81)))
            elevation_angle = 90 - latitude + declination
            
            # Calculate shadow length
            shadow_length = panel_height * np.tan(np.radians(90 - elevation_angle - panel_angle))
            shadow_length = max(0, shadow_length)
            shadow_lengths.append(shadow_length)
            
            # Calculate shadow area
            panel_area = panel_width * panels_per_row * panel_rows
            shadow_width = panel_width + shadow_length * np.sin(np.radians(panel_angle))
            shadow_area = shadow_width * panels_per_row * panel_rows
            shadow_areas.append(shadow_area)
            
            # Calculate coverage percentage
            field_size = config.get("field_size", 10000)  # m²
            coverage = min(1.0, shadow_area / field_size)
            shadow_coverages.append(coverage * 100)  # percentage
        
        # Calculate statistics
        avg_shadow_length = sum(shadow_lengths) / len(shadow_lengths)
        max_shadow_length = max(shadow_lengths)
        min_shadow_length = min(shadow_lengths)
        avg_coverage = sum(shadow_coverages) / len(shadow_coverages)
        
        return {
            "average_shadow_length_m": avg_shadow_length,
            "maximum_shadow_length_m": max_shadow_length,
            "minimum_shadow_length_m": min_shadow_length,
            "average_shadow_coverage_percent": avg_coverage,
            "daily_shadow_lengths_m": shadow_lengths,
            "daily_shadow_areas_sqm": shadow_areas,
            "daily_shadow_coverage_percent": shadow_coverages
        }
    
    def optimize_system_configuration(
        self, 
        weather_data: pd.DataFrame, 
        constraints: Dict[str, Any],
        optimization_goals: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Optimize system configuration based on weather, constraints and goals
        
        Args:
            weather_data: DataFrame with weather information
            constraints: System constraints
            optimization_goals: Dict with weights for different objectives
                (e.g. {"energy": 0.6, "crop": 0.4})
            
        Returns:
            Optimized configuration parameters
        """
        if self.optimization_model:
            # Generate candidate configurations
            candidates = self._generate_candidate_configurations(constraints, 1000)
            
            # Evaluate each candidate
            scores = []
            for candidate in candidates:
                score = self._evaluate_configuration(
                    candidate, weather_data, optimization_goals
                )
                scores.append(score)
            
            # Find best configuration
            best_idx = np.argmax(scores)
            best_config = candidates[best_idx]
            
            return best_config
        else:
            # Fallback to simplified optimization
            return self._simplified_optimization(weather_data, constraints, optimization_goals)
    
    def _prepare_energy_features(
        self, weather_data: pd.DataFrame, config: Dict[str, Any]
    ) -> np.ndarray:
        """Prepare features for energy prediction model"""
        # Extract relevant weather features
        features = []
        
        for _, day in weather_data.iterrows():
            # Basic weather features
            day_features = [
                day.get("solar_radiation", 0),
                day.get("temperature_high", 0),
                day.get("temperature_low", 0),
                day.get("cloud_cover", 0),
                day.get("wind_speed", 0),
            ]
            
            # System configuration features
            config_features = [
                config.get("panel_efficiency", 0.2),
                config.get("panel_angle", 30),
                config.get("panel_azimuth", 180),
                config.get("tracking_type_fixed", 1) if config.get("tracking_type") == "fixed" else 0,
                config.get("tracking_type_single", 1) if config.get("tracking_type") == "single-axis" else 0,
                config.get("tracking_type_dual", 1) if config.get("tracking_type") == "dual-axis" else 0,
            ]
            
            # Combine features
            all_features = day_features + config_features
            features.append(all_features)
        
        return np.array(features)
    
    def _prepare_crop_features(
        self, weather_data: pd.DataFrame, config: Dict[str, Any], crop_data: Dict[str, Any]
    ) -> np.ndarray:
        """Prepare features for crop growth prediction model"""
        # Extract relevant weather features
        features = []
        
        for _, day in weather_data.iterrows():
            # Basic weather features
            day_features = [
                day.get("temperature_high", 0),
                day.get("temperature_low", 0),
                day.get("precipitation", 0),
                day.get("humidity", 0),
                day.get("cloud_cover", 0),
            ]
            
            # System configuration features
            config_features = [
                config.get("panel_height", 2.5),
                config.get("panel_spacing", 5.0),
                config.get("shadow_coverage_percent", 30) / 100,
                config.get("irrigation_amount", 5),
            ]
            
            # Crop specific features
            crop_features = [
                crop_data.get("optimal_temp_min", 15),
                crop_data.get("optimal_temp_max", 25),
                crop_data.get("water_requirement_mm_day", 4.5),
                crop_data.get("shade_tolerance", 0.7),
            ]
            
            # Combine features
            all_features = day_features + config_features + crop_features
            features.append(all_features)
        
        return np.array(features)
    
    def _simplified_energy_model(
        self, weather_data: pd.DataFrame, config: Dict[str, Any]
    ) -> List[float]:
        """Simple energy production model"""
        daily_energy = []
        
        panel_efficiency = config.get("panel_efficiency", 0.2)
        panel_area = config.get("panel_area", 1.7)  # m²
        num_panels = config.get("num_panels", 100)
        
        for _, day in weather_data.iterrows():
            # Basic calculation based on solar radiation
            solar_radiation = day.get("solar_radiation", 5)  # kWh/m²/day
            
            # Adjust for temperature
            temp_avg = (day.get("temperature_high", 25) + day.get("temperature_low", 15)) / 2
            temp_coeff = -0.004  # Typical value
            temp_factor = 1 + temp_coeff * (temp_avg - 25)
            
            # Adjust for cloud cover
            cloud_factor = 1 - day.get("cloud_cover", 0) * 0.7
            
            # Calculate energy
            energy = solar_radiation * panel_area * num_panels * panel_efficiency * temp_factor * cloud_factor
            daily_energy.append(energy)
        
        return daily_energy
    
    def _simplified_crop_growth_model(
        self, weather_data: pd.DataFrame, config: Dict[str, Any], crop_data: Dict[str, Any]
    ) -> List[float]:
        """Simple crop growth model"""
        daily_growth = []
        
        for _, day in weather_data.iterrows():
            # Temperature stress
            temp_avg = (day.get("temperature_high", 25) + day.get("temperature_low", 15)) / 2
            temp_min = crop_data["optimal_temp_min"]
            temp_max = crop_data["optimal_temp_max"]
            
            if temp_avg < temp_min:
                temp_stress = 1 - (temp_min - temp_avg) / 10
            elif temp_avg > temp_max:
                temp_stress = 1 - (temp_avg - temp_max) / 10
            else:
                temp_stress = 1.0
            
            temp_stress = max(0.1, min(1.0, temp_stress))
            
            # Water stress
            water_req = crop_data["water_requirement_mm_day"]
            precip = day.get("precipitation", 0)
            irrigation = config.get("irrigation_amount", 5)
            irrigation_eff = config.get("irrigation_efficiency", 0.85)
            
            effective_water = precip + irrigation * irrigation_eff
            water_stress = min(1.0, effective_water / water_req)
            water_stress = max(0.1, water_stress)
            
            # Shade stress
            shade_coverage = config.get("shadow_coverage_percent", 30) / 100
            shade_tolerance = crop_data["shade_tolerance"]
            shade_stress = 1.0 - (shade_coverage * (1.0 - shade_tolerance))
            
            # Combine stresses
            growth_factor = temp_stress * water_stress * shade_stress
            daily_growth.append(growth_factor)
        
        return daily_growth
    
    def _generate_candidate_configurations(
        self, constraints: Dict[str, Any], num_candidates: int = 1000
    ) -> List[Dict[str, Any]]:
        """Generate candidate configurations within constraints"""
        candidates = []
        
        for _ in range(num_candidates):
            # Generate random configuration
            candidate = {
                "panel_height": np.random.uniform(
                    constraints.get("min_panel_height", 1.5),
                    constraints.get("max_panel_height", 4.0)
                ),
                "panel_angle": np.random.uniform(
                    constraints.get("min_panel_angle", 10),
                    constraints.get("max_panel_angle", 40)
                ),
                "panel_spacing": np.random.uniform(
                    constraints.get("min_panel_spacing", 3.0),
                    constraints.get("max_panel_spacing", 8.0)
                ),
                "irrigation_amount": np.random.uniform(
                    constraints.get("min_irrigation", 0),
                    constraints.get("max_irrigation", 10)
                )
            }
            
            # Add other parameters as needed
            if "tracking_options" in constraints:
                options = constraints["tracking_options"]
                candidate["tracking_type"] = options[np.random.randint(0, len(options))]
            else:
                candidate["tracking_type"] = "fixed"
            
            candidates.append(candidate)
        
        return candidates
    
    def _evaluate_configuration(
        self, 
        config: Dict[str, Any], 
        weather_data: pd.DataFrame, 
        optimization_goals: Dict[str, float]
    ) -> float:
        """Evaluate a configuration against optimization goals"""
        # Predict energy production
        energy_production = self.predict_energy_production(weather_data, config)
        total_energy = sum(energy_production)
        
        # Predict crop growth and yield
        crop_data = {
            "optimal_temp_min": 15,
            "optimal_temp_max": 25,
            "water_requirement_mm_day": 4.5,
            "shade_tolerance": 0.7,
            "typical_yield_per_plant": 0.25,
            "growth_period_days": 60
        }
        
        crop_growth = self.predict_crop_growth(weather_data, config, crop_data)
        crop_yield = self.predict_crop_yield(crop_growth, config, crop_data)
        
        # Calculate shadow coverage
        shadow_coverage = config["panel_height"] * np.tan(np.radians(config["panel_angle"]))
        shadow_coverage /= config["panel_spacing"]
        shadow_coverage = min(1.0, shadow_coverage)
        
        # Normalize values to 0-1 scale
        max_energy = 100000  # Example maximum annual energy production
        max_yield = 20000    # Example maximum annual crop yield
        
        norm_energy = total_energy / max_energy
        norm_yield = crop_yield / max_yield
        
        # Apply weights from optimization goals
        energy_weight = optimization_goals.get("energy", 0.5)
        crop_weight = optimization_goals.get("crop", 0.5)
        
        # Calculate weighted score
        score = energy_weight * norm_energy + crop_weight * norm_yield
        
        return score
    
    def _simplified_optimization(
        self, 
        weather_data: pd.DataFrame, 
        constraints: Dict[str, Any],
        optimization_goals: Dict[str, float]
    ) -> Dict[str, Any]:
        """Simple optimization strategy"""
        # Generate candidates
        candidates = self._generate_candidate_configurations(constraints)
        
        # Evaluate each candidate
        scores = []
        for candidate in candidates:
            energy_weight = optimization_goals.get("energy", 0.5)
            crop_weight = optimization_goals.get("crop", 0.5)
            
            # Simplified energy score based on panel angle
            optimal_angle = 30  # for example
            angle_diff = abs(candidate["panel_angle"] - optimal_angle)
            energy_score = 1.0 - angle_diff / 30
            
            # Simplified crop score based on panel height and spacing
            height_ratio = candidate["panel_height"] / candidate["panel_spacing"]
            shade_factor = min(1.0, height_ratio * 1.5)
            crop_score = 1.0 - shade_factor * (1 - 0.7)  # 0.7 = shade tolerance
            
            # Combined score
            score = energy_weight * energy_score + crop_weight * crop_score
            scores.append(score)
        
        # Find best configuration
        best_idx = np.argmax(scores)
        
        return candidates[best_idx]