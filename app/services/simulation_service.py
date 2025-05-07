import time
import json
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List

from app.models.database import Simulation, Configuration, WeatherData
from app.services.ml_service import MLService
from app.services.weather_service import WeatherService
from app.core.config import settings


class SimulationService:
    def __init__(self, db: Session):
        self.db = db
        self.ml_service = MLService()
        self.weather_service = WeatherService(db)
    
    async def run_simulation(self, simulation_id: int):
        """
        Run a simulation with the given ID
        """
        # Get simulation from database
        simulation = self.db.query(Simulation).filter(Simulation.id == simulation_id).first()
        
        if not simulation:
            return
        
        # Update status to running
        simulation.status = "running"
        self.db.commit()
        
        try:
            # Get simulation parameters
            params = simulation.parameters
            
            # Get configuration
            config = self.db.query(Configuration).filter(
                Configuration.simulation_id == simulation_id,
                Configuration.is_optimized == True
            ).first()
            
            config_id = config.id if config else None
            config_params = config.parameters if config else params.get("default_configuration", {})
            
            # Get or generate weather data
            weather_data = self._get_weather_data(params)
            
            # Run simulation steps
            results = {
                "energy_production": self._simulate_energy_production(config_params, weather_data),
                "crop_yield": self._simulate_crop_yield(config_params, weather_data),
                "shadow_patterns": self._simulate_shadow_patterns(config_params, weather_data),
                "water_usage": self._simulate_water_usage(config_params, weather_data),
                "financial_metrics": self._calculate_financial_metrics(config_params),
                "environmental_metrics": self._calculate_environmental_metrics(config_params),
                "configuration_id": config_id
            }
            
            # Update simulation with results
            simulation.status = "completed"
            simulation.results = results
            simulation.completed_at = datetime.now()
            self.db.commit()
            
        except Exception as e:
            # Update simulation status to failed
            simulation.status = "failed"
            simulation.results = {"error": str(e)}
            self.db.commit()
    
    def _get_weather_data(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get or generate weather data for the simulation
        """
        if "weather_data_id" in params and params["weather_data_id"]:
            # Use existing weather data
            weather_data = self.db.query(WeatherData).filter(
                WeatherData.id == params["weather_data_id"]
            ).all()
            
            if not weather_data:
                # Generate synthetic data if not found
                return self.weather_service.generate_synthetic_weather(
                    params.get("location", {"lat": 40.0, "lng": -75.0}),
                    params.get("start_date", datetime.now().strftime("%Y-%m-%d")),
                    params.get("duration_days", 365)
                )
            
            return [w.__dict__ for w in weather_data]
        
        elif "custom_weather_data" in params and params["custom_weather_data"]:
            # Use custom weather data provided in parameters
            return params["custom_weather_data"]
        
        else:
            # Generate synthetic weather data
            return self.weather_service.generate_synthetic_weather(
                params.get("location", {"lat": 40.0, "lng": -75.0}),
                params.get("start_date", datetime.now().strftime("%Y-%m-%d")),
                params.get("duration_days", 365)
            )
    
    def _simulate_energy_production(
        self, config: Dict[str, Any], weather_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Simulate solar energy production based on configuration and weather
        """
        # Convert weather data to DataFrame for easier processing
        weather_df = pd.DataFrame(weather_data)
        
        # Extract necessary parameters
        panel_efficiency = config.get("panel_efficiency", 0.2)
        panel_area = config.get("panel_area", 1.7)  # m²
        num_panels = config.get("num_panels", 100)
        panel_angle = config.get("panel_angle", 30)  # degrees
        panel_azimuth = config.get("panel_azimuth", 180)  # degrees (south)
        tracking_type = config.get("tracking_type", "fixed")  # fixed, single-axis, dual-axis
        
        # Apply ML model for energy prediction if available
        try:
            energy_daily = self.ml_service.predict_energy_production(
                weather_df, config
            )
        except:
            # Fallback to simple model
            energy_daily = []
            for _, day in weather_df.iterrows():
                # Basic calculation based on solar radiation and system parameters
                efficiency_factor = panel_efficiency
                
                # Adjust for temperature effects
                if "temperature_high" in day:
                    temp_coeff = config.get("temp_coefficient", -0.004)  # Typical value for silicon
                    reference_temp = config.get("reference_temp", 25)
                    efficiency_factor += temp_coeff * (day["temperature_high"] - reference_temp)
                
                # Adjust for cloud cover
                if "cloud_cover" in day:
                    efficiency_factor *= (1 - day["cloud_cover"] * 0.7)
                
                # Calculate energy based on solar radiation
                if "solar_radiation" in day:
                    daily_energy = day["solar_radiation"] * panel_area * num_panels * efficiency_factor
                    energy_daily.append(daily_energy)
                else:
                    # Fallback if no solar radiation data
                    energy_daily.append(0)
        
        # Calculate summary statistics
        total_energy = sum(energy_daily)
        avg_daily_energy = total_energy / len(energy_daily) if energy_daily else 0
        peak_day = max(energy_daily) if energy_daily else 0
        min_day = min(energy_daily) if energy_daily else 0
        
        # Return results
        return {
            "total_annual_energy_kwh": total_energy,
            "average_daily_energy_kwh": avg_daily_energy,
            "peak_daily_production_kwh": peak_day,
            "min_daily_production_kwh": min_day,
            "monthly_production_kwh": self._aggregate_monthly(energy_daily, weather_df),
            "daily_production": energy_daily,
            "capacity_factor": avg_daily_energy / (24 * panel_efficiency * panel_area * num_panels) if panel_efficiency * panel_area * num_panels > 0 else 0
        }
    
    def _simulate_crop_yield(
        self, config: Dict[str, Any], weather_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Simulate crop yield based on configuration and weather
        """
        # Convert weather data to DataFrame
        weather_df = pd.DataFrame(weather_data)
        
        # Extract necessary parameters
        crop_type = config.get("crop_type", "lettuce")
        planting_density = config.get("planting_density", 25)  # plants per m²
        field_size = config.get("field_size", 10000)  # m²
        irrigation_efficiency = config.get("irrigation_efficiency", 0.85)
        shade_impact = config.get("shade_impact", 0.2)  # Yield reduction due to shade
        
        # Get crop-specific parameters from DB or use defaults
        crop_data = {
            "growth_period_days": 60,
            "optimal_temp_min": 15,
            "optimal_temp_max": 25,
            "water_requirement_mm_day": 4.5,
            "shade_tolerance": 0.7,
            "typical_yield_per_plant": 0.25  # kg
        }
        
        # Apply ML model for crop yield prediction if available
        try:
            daily_growth = self.ml_service.predict_crop_growth(
                weather_df, config, crop_data
            )
            total_yield = self.ml_service.predict_crop_yield(
                daily_growth, config, crop_data
            )
        except:
            # Fallback to simple model
            # Calculate temperature stress factor
            temp_stress = []
            for _, day in weather_df.iterrows():
                if "temperature_high" in day and "temperature_low" in day:
                    avg_temp = (day["temperature_high"] + day["temperature_low"]) / 2
                    if avg_temp < crop_data["optimal_temp_min"]:
                        stress = 1 - (crop_data["optimal_temp_min"] - avg_temp) / 10
                    elif avg_temp > crop_data["optimal_temp_max"]:
                        stress = 1 - (avg_temp - crop_data["optimal_temp_max"]) / 10
                    else:
                        stress = 1.0
                    
                    stress = max(0.1, min(1.0, stress))
                    temp_stress.append(stress)
                else:
                    temp_stress.append(0.8)  # Default value
            
            # Calculate water stress factor
            water_stress = []
            for _, day in weather_df.iterrows():
                if "precipitation" in day:
                    irrigation_amount = config.get("irrigation_amount", 0)  # mm/day
                    effective_water = (day["precipitation"] + irrigation_amount) * irrigation_efficiency
                    stress = min(1.0, effective_water / crop_data["water_requirement_mm_day"])
                    water_stress.append(max(0.1, stress))
                else:
                    water_stress.append(0.8)  # Default value
            
            # Calculate shade stress factor
            # Simple assumption: shadow reduces yield by a fixed percentage
            shade_stress = 1.0 - (shade_impact * (1 - crop_data["shade_tolerance"]))
            
            # Combine stress factors to calculate yield
            daily_growth = []
            for i in range(len(temp_stress)):
                growth_factor = temp_stress[i] * water_stress[i] * shade_stress
                daily_growth.append(growth_factor)
            
            # Calculate total yield based on growth factors
            harvest_days = min(crop_data["growth_period_days"], len(daily_growth))
            avg_growth_factor = sum(daily_growth[:harvest_days]) / harvest_days
            
            base_yield = crop_data["typical_yield_per_plant"] * planting_density * field_size
            total_yield = base_yield * avg_growth_factor
        
        # Calculate yield distribution and statistics
        # Assume multiple harvests for year-round crops
        num_cycles = 365 // crop_data["growth_period_days"]
        cycle_yields = [total_yield * (0.9 + 0.2 * np.random.random()) for _ in range(num_cycles)]
        
        return {
            "total_annual_yield_kg": sum(cycle_yields),
            "yield_per_harvest_kg": total_yield,
            "average_yield_per_sqm_kg": sum(cycle_yields) / field_size,
            "number_of_harvest_cycles": num_cycles,
            "harvest_cycle_yields_kg": cycle_yields,
            "crop_type": crop_type,
            "estimated_market_value": sum(cycle_yields) * config.get("crop_price_per_kg", 2.5)
        }
    
    def _simulate_shadow_patterns(
        self, config: Dict[str, Any], weather_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Simulate shadow patterns cast by solar panels
        """
        # Extract panel configuration
        panel_height = config.get("panel_height", 2.5)  # meters
        panel_width = config.get("panel_width", 1.0)  # meters
        panel_angle = config.get("panel_angle", 30)  # degrees
        panel_spacing = config.get("panel_spacing", 5.0)  # meters
        panel_rows = config.get("panel_rows", 10)
        panels_per_row = config.get("panels_per_row", 10)
        tracking_type = config.get("tracking_type", "fixed")
        
        # Use ML model if available
        try:
            shadow_data = self.ml_service.calculate_shadow_patterns(
                weather_data, config
            )
        except:
            # Fallback to simple model
            # Calculate shadow length for each day at noon
            shadow_lengths = []
            shadow_areas = []
            
            for day_idx, day in enumerate(weather_data):
                # Calculate solar elevation at noon (simplified)
                day_of_year = day_idx % 365
                latitude = config.get("latitude", 40.0)
                declination = 23.45 * np.sin(np.radians(360/365 * (day_of_year - 81)))
                elevation_angle = 90 - latitude + declination
                
                # Calculate shadow length
                shadow_length = panel_height * np.tan(np.radians(90 - elevation_angle - panel_angle))
                shadow_length = max(0, shadow_length)
                shadow_lengths.append(shadow_length)
                
                # Calculate total shadow area
                shadow_width = panel_width + shadow_length * np.sin(np.radians(panel_angle))
                shadow_area = shadow_width * panel_rows * panels_per_row
                shadow_areas.append(shadow_area)
        
            # Calculate statistics
            avg_shadow_length = sum(shadow_lengths) / len(shadow_lengths) if shadow_lengths else 0
            max_shadow_length = max(shadow_lengths) if shadow_lengths else 0
            min_shadow_length = min(shadow_lengths) if shadow_lengths else 0
            
            # Calculate shadow coverage percentage
            field_size = config.get("field_size", 10000)  # m²
            avg_shadow_coverage = sum(shadow_areas) / len(shadow_areas) / field_size if shadow_areas else 0
            
            shadow_data = {
                "average_shadow_length_m": avg_shadow_length,
                "maximum_shadow_length_m": max_shadow_length,
                "minimum_shadow_length_m": min_shadow_length,
                "average_shadow_coverage_percent": avg_shadow_coverage * 100,
                "daily_shadow_lengths_m": shadow_lengths,
                "daily_shadow_areas_sqm": shadow_areas
            }
        
        return shadow_data
    
    def _simulate_water_usage(
        self, config: Dict[str, Any], weather_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Simulate water usage for crop irrigation
        """
        # Extract parameters
        field_size = config.get("field_size", 10000)  # m²
        irrigation_efficiency = config.get("irrigation_efficiency", 0.85)
        crop_type = config.get("crop_type", "lettuce")
        
        # Get crop water requirements
        crop_data = {
            "water_requirement_mm_day": 4.5,  # Default for lettuce
        }
        
        # Calculate daily water needs based on weather
        daily_water_needs = []
        daily_irrigation_needs = []
        daily_precipitation = []
        
        for day in weather_data:
            # Extract precipitation if available
            precip = day.get("precipitation", 0)  # mm
            daily_precipitation.append(precip)
            
            # Calculate crop evapotranspiration (simplified)
            temp_avg = (day.get("temperature_high", 25) + day.get("temperature_low", 15)) / 2
            humidity = day.get("humidity", 70)
            wind_speed = day.get("wind_speed", 5)
            
            # Simple evapotranspiration model based on temperature
            et0 = 0.0023 * (temp_avg + 17.8) * np.sqrt(day.get("temperature_high", 25) - day.get("temperature_low", 15)) * 6  # mm/day
            
            # Apply crop coefficient
            etc = et0 * config.get("crop_coefficient", 1.0)
            daily_water_needs.append(etc)
            
            # Calculate irrigation need (accounting for precipitation)
            irrig_need = max(0, etc - precip)
            daily_irrigation_needs.append(irrig_need)
        
        # Calculate total water volumes
        total_water_need = sum(daily_water_needs) * field_size / 1000  # m³
        total_irrigation_need = sum(daily_irrigation_needs) * field_size / 1000  # m³
        total_precipitation = sum(daily_precipitation) * field_size / 1000  # m³
        
        # Account for irrigation efficiency
        actual_irrigation_volume = total_irrigation_need / irrigation_efficiency
        
        # Calculate water savings from panel shade (reduced evaporation)
        shadow_coverage = config.get("shadow_coverage_percent", 30) / 100
        water_savings_percent = shadow_coverage * config.get("evaporation_reduction_factor", 0.3)
        water_savings_volume = total_water_need * water_savings_percent
        
        return {
            "total_water_requirement_cubic_m": total_water_need,
            "total_irrigation_volume_cubic_m": actual_irrigation_volume,
            "total_precipitation_cubic_m": total_precipitation,
            "water_savings_from_panels_cubic_m": water_savings_volume,
            "water_savings_percent": water_savings_percent * 100,
            "daily_irrigation_needs_mm": daily_irrigation_needs,
            "daily_precipitation_mm": daily_precipitation,
            "irrigation_efficiency": irrigation_efficiency
        }
    
    def _calculate_financial_metrics(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate financial metrics for the agrivoltaics system
        """
        # Capital expenses
        panel_cost = config.get("panel_cost", 250)  # $ per panel
        num_panels = config.get("num_panels", 100)
        mounting_cost = config.get("mounting_cost", 150)  # $ per panel
        inverter_cost = config.get("inverter_cost", 10000)  # $
        installation_cost = config.get("installation_cost", 15000)  # $
        
        # Calculate total CAPEX
        total_panel_cost = panel_cost * num_panels
        total_mounting_cost = mounting_cost * num_panels
        total_capex = total_panel_cost + total_mounting_cost + inverter_cost + installation_cost
        
        # Additional agricultural equipment
        ag_equipment_cost = config.get("ag_equipment_cost", 5000)  # $
        total_capex += ag_equipment_cost
        
        # Operating expenses
        maintenance_cost_annual = config.get("maintenance_cost_annual", 1000)  # $
        insurance_cost_annual = config.get("insurance_cost_annual", 500)  # $
        labor_cost_annual = config.get("labor_cost_annual", 2000)  # $
        
        # Agricultural operating expenses
        seeds_cost_annual = config.get("seeds_cost_annual", 1000)  # $
        fertilizer_cost_annual = config.get("fertilizer_cost_annual", 500)  # $
        pesticide_cost_annual = config.get("pesticide_cost_annual", 300)  # $
        water_cost_annual = config.get("water_cost_annual", 800)  # $
        ag_labor_cost_annual = config.get("ag_labor_cost_annual", 3000)  # $
        
        # Calculate total OPEX
        total_opex_annual = (
            maintenance_cost_annual + 
            insurance_cost_annual + 
            labor_cost_annual +
            seeds_cost_annual +
            fertilizer_cost_annual +
            pesticide_cost_annual +
            water_cost_annual +
            ag_labor_cost_annual
        )
        
        # Revenue calculations
        energy_production_annual = config.get("energy_production_annual", 40000)  # kWh
        energy_price = config.get("energy_price", 0.12)  # $ per kWh
        
        crop_yield_annual = config.get("crop_yield_annual", 5000)  # kg
        crop_price = config.get("crop_price", 2.5)  # $ per kg
        
        # Calculate annual revenue
        energy_revenue_annual = energy_production_annual * energy_price
        crop_revenue_annual = crop_yield_annual * crop_price
        total_revenue_annual = energy_revenue_annual + crop_revenue_annual
        
        # Calculate profit metrics
        net_profit_annual = total_revenue_annual - total_opex_annual
        payback_period = total_capex / net_profit_annual if net_profit_annual > 0 else float('inf')
        
        # Calculate ROI and NPV
        project_lifetime = config.get("project_lifetime", 25)  # years
        discount_rate = config.get("discount_rate", 0.05)  # 5%
        
        # Simple ROI
        lifetime_profit = net_profit_annual * project_lifetime
        roi = (lifetime_profit - total_capex) / total_capex * 100
        
        # Calculate NPV
        npv = -total_capex
        for year in range(1, project_lifetime + 1):
            npv += net_profit_annual / ((1 + discount_rate) ** year)
        
        # Calculate IRR (simplified approximation)
        irr = net_profit_annual / total_capex
        
        # Calculate LCOE (Levelized Cost of Energy)
        total_lifetime_energy = energy_production_annual * project_lifetime
        total_lifetime_cost = total_capex + total_opex_annual * project_lifetime
        lcoe = total_lifetime_cost / total_lifetime_energy if total_lifetime_energy > 0 else float('inf')
        
        return {
            "total_capex": total_capex,
            "total_opex_annual": total_opex_annual,
            "energy_revenue_annual": energy_revenue_annual,
            "crop_revenue_annual": crop_revenue_annual,
            "total_revenue_annual": total_revenue_annual,
            "net_profit_annual": net_profit_annual,
            "payback_period_years": payback_period,
            "roi_percent": roi,
            "npv": npv,
            "irr_approx": irr,
            "lcoe": lcoe,
            "capex_breakdown": {
                "panels": total_panel_cost,
                "mounting": total_mounting_cost,
                "inverter": inverter_cost,
                "installation": installation_cost,
                "agricultural_equipment": ag_equipment_cost
            },
            "opex_breakdown": {
                "maintenance": maintenance_cost_annual,
                "insurance": insurance_cost_annual,
                "solar_labor": labor_cost_annual,
                "seeds": seeds_cost_annual,
                "fertilizer": fertilizer_cost_annual,
                "pesticide": pesticide_cost_annual,
                "water": water_cost_annual,
                "agricultural_labor": ag_labor_cost_annual
            }
        }
    
    def _calculate_environmental_metrics(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate environmental impact metrics for the agrivoltaics system
        """
        # Energy production details
        energy_production_annual = config.get("energy_production_annual", 40000)  # kWh
        project_lifetime = config.get("project_lifetime", 25)  # years
        
        # Carbon metrics
        grid_carbon_intensity = config.get("grid_carbon_intensity", 0.5)  # kg CO2 per kWh
        system_carbon_footprint = config.get("system_carbon_footprint", 50)  # kg CO2 per panel
        num_panels = config.get("num_panels", 100)
        
        # Land use metrics
        field_size = config.get("field_size", 10000)  # m²
        conventional_solar_land_use = config.get("conventional_solar_land_use", 0.02)  # m² per kWh annual
        
        # Water usage
        water_usage_annual = config.get("water_usage_annual", 500)  # m³
        conventional_water_usage = config.get("conventional_water_usage", 700)  # m³
        
        # Calculate carbon emissions avoided
        lifetime_energy_production = energy_production_annual * project_lifetime
        carbon_emissions_avoided = lifetime_energy_production * grid_carbon_intensity
        
        # Calculate system carbon footprint
        system_total_carbon = system_carbon_footprint * num_panels
        net_carbon_benefit = carbon_emissions_avoided - system_total_carbon
        carbon_payback_years = system_total_carbon / (energy_production_annual * grid_carbon_intensity)
        
        # Calculate land use efficiency
        conventional_land_required = energy_production_annual * conventional_solar_land_use
        land_use_efficiency = conventional_land_required / field_size
        
        # Calculate water savings
        water_savings = conventional_water_usage - water_usage_annual
        
        return {
            "carbon_emissions_avoided_kg": carbon_emissions_avoided,
            "system_carbon_footprint_kg": system_total_carbon,
            "net_carbon_benefit_kg": net_carbon_benefit,
            "carbon_payback_years": carbon_payback_years,
            "land_use_efficiency_ratio": land_use_efficiency,
            "dual_purpose_land_area_sqm": field_size,
            "water_savings_cubic_m": water_savings,
            "water_savings_percent": (water_savings / conventional_water_usage) * 100 if conventional_water_usage > 0 else 0
        }
    
    def _aggregate_monthly(self, daily_values: List[float], weather_df: pd.DataFrame) -> Dict[str, float]:
        """
        Aggregate daily values into monthly totals
        """
        # Create a dataframe with dates and values
        if "ds" in weather_df.columns:
            dates = weather_df["ds"]
        else:
            # Create dates if not available in weather data
            start_date = datetime.now().replace(day=1)
            dates = [start_date + timedelta(days=i) for i in range(len(daily_values))]
        
        df = pd.DataFrame({"date": dates, "value": daily_values})
        
        # Extract month from date
        df["month"] = df["date"].dt.month
        
        # Group by month and sum
        monthly_values = df.groupby("month")["value"].sum().to_dict()
        
        return monthly_values

