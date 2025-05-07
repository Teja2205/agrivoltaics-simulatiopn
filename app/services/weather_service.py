import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import logging
import requests
import os
import json

from app.models.database import WeatherData
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class WeatherService:
    """Service for weather data retrieval and processing"""
    
    def __init__(self, db: Session):
        """
        Initialize weather service with database session
        
        Args:
            db: Database session
        """
        self.db = db
        self.cache_dir = os.path.join(settings.BASE_DIR, "cache", "weather")
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_weather_data(
        self, location: Dict[str, float], start_date: str, end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Get weather data for a location and date range
        
        Args:
            location: Dict with lat and lng
            start_date: Start date in ISO format
            end_date: End date in ISO format
            
        Returns:
            List of weather data dictionaries
        """
        logger.info(f"Getting weather data for location {location} from {start_date} to {end_date}")
        
        # Convert dates
        try:
            start = datetime.fromisoformat(start_date) if isinstance(start_date, str) else start_date
        except ValueError:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                logger.error(f"Invalid start_date format: {start_date}")
                start = datetime.now() - timedelta(days=7)  # Default to 7 days ago
        
        try:
            end = datetime.fromisoformat(end_date) if isinstance(end_date, str) else end_date
        except ValueError:
            try:
                end = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                logger.error(f"Invalid end_date format: {end_date}")
                end = datetime.now()  # Default to current date
        
        # First check if we have the data in our database
        lat = location.get("lat", 0)
        lng = location.get("lng", 0)
        
        if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
            logger.error(f"Invalid location coordinates: {location}")
            # Set default coordinates
            lat = 40.0
            lng = -75.0
        
        # Allow for some tolerance in location coordinates
        tolerance = 0.01
        
        try:
            weather_data = self.db.query(WeatherData).filter(
                WeatherData.location_lat.between(lat - tolerance, lat + tolerance),
                WeatherData.location_lng.between(lng - tolerance, lng + tolerance),
                WeatherData.date.between(start, end)
            ).all()
            
            days_diff = (end - start).days
            
            # If we don't have enough data in the database, fetch from Open-Meteo API
            if days_diff > 0 and len(weather_data) < days_diff * 0.8:  # If less than 80% of days are available
                logger.info(f"Insufficient weather data in database. Fetching from Open-Meteo API...")
                try:
                    api_data = self._fetch_from_open_meteo({"lat": lat, "lng": lng}, start, end)
                    if api_data and len(api_data) > 0:
                        # Save to database
                        self.save_weather_data(api_data)
                        return api_data
                except Exception as e:
                    logger.error(f"Error fetching weather data from API: {e}")
                    # Fall back to synthetic data if API fails
            
            # If we still don't have enough data, generate synthetic data
            if days_diff > 0 and len(weather_data) < days_diff * 0.8:
                logger.info(f"Still insufficient weather data. Generating synthetic data...")
                synthetic_data = self.generate_synthetic_weather({"lat": lat, "lng": lng}, start, days_diff)
                # Save synthetic data to database for future use
                if synthetic_data:
                    self.save_weather_data(synthetic_data)
                return synthetic_data
            
            # Convert database objects to dictionaries
            result = []
            for data in weather_data:
                result.append({
                    "date": data.date.isoformat() if data.date else None,
                    "location_lat": data.location_lat,
                    "location_lng": data.location_lng,
                    "temperature_high": data.temperature_high,
                    "temperature_low": data.temperature_low,
                    "humidity": data.humidity,
                    "precipitation": data.precipitation,
                    "cloud_cover": data.cloud_cover,
                    "wind_speed": data.wind_speed,
                    "wind_direction": data.wind_direction,
                    "solar_radiation": data.solar_radiation
                })
            
            logger.info(f"Returning {len(result)} weather data records")
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving weather data: {e}")
            # Generate synthetic data as fallback
            logger.info("Generating synthetic weather data as fallback")
            days_diff = (end - start).days if hasattr(end, 'days') and hasattr(start, 'days') else 7
            return self.generate_synthetic_weather({"lat": lat, "lng": lng}, start, days_diff)
    
    def _fetch_from_open_meteo(
        self, location: Dict[str, float], start_date: Any, end_date: Any
    ) -> List[Dict[str, Any]]:
        """
        Fetch weather data from Open-Meteo API
        
        Args:
            location: Dict with lat and lng
            start_date: Start date (string or datetime)
            end_date: End date (string or datetime)
            
        Returns:
            List of weather data dictionaries
        """
        # Ensure dates are in the correct format for the API
        if isinstance(start_date, datetime):
            start_fmt = start_date.strftime("%Y-%m-%d")
        else:
            start_fmt = start_date.split("T")[0] if isinstance(start_date, str) and "T" in start_date else start_date
        
        if isinstance(end_date, datetime):
            end_fmt = end_date.strftime("%Y-%m-%d")
        else:
            end_fmt = end_date.split("T")[0] if isinstance(end_date, str) and "T" in end_date else end_date
        
        logger.info(f"Fetching data from Open-Meteo API for {location} from {start_fmt} to {end_fmt}")
        
        # Build the API URL with all the parameters we need for agrivoltaics
        url = (
            f"https://archive-api.open-meteo.com/v1/archive?"
            f"latitude={location['lat']}"
            f"&longitude={location['lng']}"
            f"&start_date={start_fmt}"
            f"&end_date={end_fmt}"
            f"&hourly=temperature_2m,relative_humidity_2m,precipitation,cloud_cover,"
            f"shortwave_radiation,direct_radiation,direct_normal_irradiance"
        )
        
        # Get daily min/max in separate call for high/low temperatures
        daily_url = (
            f"https://archive-api.open-meteo.com/v1/archive?"
            f"latitude={location['lat']}"
            f"&longitude={location['lng']}"
            f"&start_date={start_fmt}"
            f"&end_date={end_fmt}"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        )
        
        try:
            # Make the API requests
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            hourly_data = response.json()
            
            daily_response = requests.get(daily_url, timeout=10)
            daily_response.raise_for_status()
            daily_data = daily_response.json()
            
            # Process the hourly data
            result = []
            
            # Check for required keys in the response
            if 'hourly' not in hourly_data or 'daily' not in daily_data:
                logger.error("Missing required sections in API response")
                return []
            
            # Get hourly data arrays
            times = hourly_data['hourly'].get('time', [])
            temperatures = hourly_data['hourly'].get('temperature_2m', [])
            humidities = hourly_data['hourly'].get('relative_humidity_2m', [])
            precipitations = hourly_data['hourly'].get('precipitation', [])
            cloud_covers = hourly_data['hourly'].get('cloud_cover', [])
            solar_radiations = hourly_data['hourly'].get('shortwave_radiation', [])
            
            # Check for empty arrays
            if not times:
                logger.error("No time data in API response")
                return []
            
            # Process the daily data to get high/low temps
            daily_dates = daily_data['daily'].get('time', [])
            daily_high_temps = daily_data['daily'].get('temperature_2m_max', [])
            daily_low_temps = daily_data['daily'].get('temperature_2m_min', [])
            
            # Create a mapping of date to high/low temps
            temp_map = {}
            for i, date in enumerate(daily_dates):
                if i < len(daily_high_temps) and i < len(daily_low_temps):
                    temp_map[date] = {
                        'high': daily_high_temps[i],
                        'low': daily_low_temps[i]
                    }
            
            # Create hourly aggregates by day for our database schema
            day_data = {}
            
            for i, time in enumerate(times):
                # Skip invalid entries
                if not time:
                    continue
                    
                # Get just the date part
                day = time.split("T")[0] if "T" in time else time
                
                # Initialize day data if not already done
                if day not in day_data:
                    # Default values
                    default_high = 25.0
                    default_low = 15.0
                    
                    # Get values from temp_map if available
                    if day in temp_map:
                        high_temp = temp_map[day].get('high', default_high)
                        low_temp = temp_map[day].get('low', default_low)
                    else:
                        high_temp = default_high
                        low_temp = default_low
                    
                    day_data[day] = {
                        "date": day,
                        "location_lat": location["lat"],
                        "location_lng": location["lng"],
                        "temperature_high": high_temp,
                        "temperature_low": low_temp,
                        "humidity": [],
                        "precipitation": [],
                        "cloud_cover": [],
                        "solar_radiation": [],
                        "wind_speed": [5.0],  # Default value
                        "wind_direction": [180.0]  # Default value
                    }
                
                # Add hourly data to lists with safety checks
                if i < len(humidities) and humidities[i] is not None:
                    day_data[day]["humidity"].append(humidities[i])
                
                if i < len(precipitations) and precipitations[i] is not None:
                    day_data[day]["precipitation"].append(precipitations[i])
                
                if i < len(cloud_covers) and cloud_covers[i] is not None:
                    day_data[day]["cloud_cover"].append(cloud_covers[i] / 100)  # Convert to 0-1 scale
                
                if i < len(solar_radiations) and solar_radiations[i] is not None:
                    day_data[day]["solar_radiation"].append(solar_radiations[i])
            
            # Calculate averages and sums for daily values with safety checks
            for day, data in day_data.items():
                # Humidity average with safety check
                if data["humidity"]:
                    data["humidity"] = sum(data["humidity"]) / len(data["humidity"])
                else:
                    data["humidity"] = 50.0  # Default value
                
                # Precipitation sum with safety check
                if data["precipitation"]:
                    data["precipitation"] = sum(data["precipitation"])
                else:
                    data["precipitation"] = 0.0  # Default value
                
                # Cloud cover average with safety check
                if data["cloud_cover"]:
                    data["cloud_cover"] = sum(data["cloud_cover"]) / len(data["cloud_cover"])
                else:
                    data["cloud_cover"] = 0.3  # Default value
                
                # Solar radiation average with safety check
                if data["solar_radiation"]:
                    data["solar_radiation"] = sum(data["solar_radiation"]) / len(data["solar_radiation"])
                else:
                    data["solar_radiation"] = 5.0  # Default value
                
                # Wind speed average with safety check
                if data["wind_speed"]:
                    data["wind_speed"] = sum(data["wind_speed"]) / len(data["wind_speed"])
                else:
                    data["wind_speed"] = 5.0  # Default value
                
                # Wind direction average with safety check
                if data["wind_direction"]:
                    data["wind_direction"] = sum(data["wind_direction"]) / len(data["wind_direction"])
                else:
                    data["wind_direction"] = 180.0  # Default value
                
                # Convert string date to datetime
                try:
                    data["date"] = datetime.fromisoformat(day)
                except ValueError:
                    try:
                        data["date"] = datetime.strptime(day, "%Y-%m-%d")
                    except ValueError:
                        logger.error(f"Invalid date format: {day}")
                        continue
                
                # Add to result
                result.append(data)
            
            logger.info(f"Successfully fetched {len(result)} days of weather data from Open-Meteo API")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {e}")
            return []
        except KeyError as e:
            logger.error(f"Missing key in API response: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching data from Open-Meteo API: {e}")
            return []
    
    def generate_synthetic_weather(
        self, location: Dict[str, float], start_date: Any, duration_days: int
    ) -> List[Dict[str, Any]]:
        """
        Generate synthetic weather data for simulation
        
        Args:
            location: Dict with lat and lng
            start_date: Start date (string or datetime)
            duration_days: Number of days to generate
            
        Returns:
            List of weather data dictionaries
        """
        logger.info(f"Generating synthetic weather data for {duration_days} days")
        
        # Convert start date with error handling
        if isinstance(start_date, datetime):
            start = start_date
        else:
            try:
                start = datetime.fromisoformat(start_date) if isinstance(start_date, str) else datetime.now() - timedelta(days=7)
            except ValueError:
                try:
                    start = datetime.strptime(start_date, "%Y-%m-%d")
                except ValueError:
                    logger.error(f"Invalid start_date format: {start_date}")
                    start = datetime.now() - timedelta(days=7)  # Default to 7 days ago
        
        # Validate and set duration
        if not isinstance(duration_days, int) or duration_days <= 0:
            logger.error(f"Invalid duration_days: {duration_days}")
            duration_days = 7  # Default to 7 days
        
        # Extract location with defaults
        lat = location.get("lat", 40.0)
        lng = location.get("lng", -75.0)
        
        # Generate dates
        dates = [start + timedelta(days=i) for i in range(duration_days)]
        
        # Set random seed for reproducibility
        np.random.seed(42)
        
        # Generate synthetic data
        result = []
        
        for date in dates:
            # Day of year for seasonal variations
            day_of_year = date.timetuple().tm_yday
            
            # Calculate seasonal factors (northern hemisphere)
            # Peak in summer (day ~180), low in winter
            seasonal_factor = np.sin(np.radians((day_of_year - 15) / 365 * 360)) * 0.5 + 0.5
            
            # Add some randomness
            random_factor = np.random.random() * 0.4 - 0.2  # -0.2 to 0.2
            
            # Calculate values with seasonal variation
            temp_high = 15 + seasonal_factor * 25 + random_factor * 10
            temp_low = 5 + seasonal_factor * 15 + random_factor * 8
            
            # More rain in spring/fall
            precip_seasonal = np.sin(np.radians((day_of_year - 80) / 365 * 720)) * 0.5 + 0.5
            precip_chance = precip_seasonal * 0.5
            precipitation = 0.0 if np.random.random() > precip_chance else np.random.exponential(5)
            
            # Cloud cover correlated with precipitation
            cloud_base = 0.2 + precipitation / 20
            cloud_cover = min(1.0, max(0.0, cloud_base + np.random.random() * 0.3))
            
            # Solar radiation inversely correlated with cloud cover
            # and positively with seasonal factor
            solar_rad_base = (1 - cloud_cover) * 7 * seasonal_factor
            solar_radiation = max(0.1, solar_rad_base + np.random.random() * 1.5)
            
            # Wind varies throughout the year
            wind_speed = 2 + np.random.gamma(2, 2)
            wind_direction = np.random.randint(0, 360)
            
            # Humidity related to temperature and precipitation
            humidity_base = 40 + 30 * (1 - seasonal_factor) + precipitation * 3
            humidity = min(100, max(10, humidity_base + np.random.random() * 20))
            
            # Create weather data entry
            weather_data = {
                "date": date,
                "location_lat": lat,
                "location_lng": lng,
                "temperature_high": temp_high,
                "temperature_low": temp_low,
                "humidity": humidity,
                "precipitation": precipitation,
                "cloud_cover": cloud_cover,
                "wind_speed": wind_speed,
                "wind_direction": wind_direction,
                "solar_radiation": solar_radiation
            }
            
            result.append(weather_data)
        
        logger.info(f"Generated {len(result)} days of synthetic weather data")
        return result
    
    def save_weather_data(self, weather_data: List[Dict[str, Any]]) -> bool:
        """
        Save weather data to database
        
        Args:
            weather_data: List of weather data dictionaries
            
        Returns:
            Success status
        """
        try:
            added_count = 0
            
            for data in weather_data:
                # Skip invalid data
                if not data:
                    continue
                
                # Convert date string to datetime if needed
                date = data.get("date")
                if not date:
                    logger.warning("Weather data entry missing date, skipping")
                    continue
                
                if isinstance(date, str):
                    try:
                        date = datetime.fromisoformat(date)
                    except ValueError:
                        try:
                            date = datetime.strptime(date, "%Y-%m-%d")
                        except ValueError:
                            logger.error(f"Invalid date format: {date}")
                            continue
                
                # Check for existing record to avoid duplicates
                existing = self.db.query(WeatherData).filter(
                    WeatherData.date == date,
                    WeatherData.location_lat == data.get("location_lat"),
                    WeatherData.location_lng == data.get("location_lng")
                ).first()
                
                if existing:
                    # Optional: update existing record if needed
                    continue
                
                # Create WeatherData object with defaults for missing values
                db_weather = WeatherData(
                    date=date,
                    location_lat=data.get("location_lat", 0),
                    location_lng=data.get("location_lng", 0),
                    temperature_high=data.get("temperature_high", 25.0),
                    temperature_low=data.get("temperature_low", 15.0),
                    humidity=data.get("humidity", 50.0),
                    precipitation=data.get("precipitation", 0.0),
                    cloud_cover=data.get("cloud_cover", 0.3),
                    wind_speed=data.get("wind_speed", 5.0),
                    wind_direction=data.get("wind_direction", 180.0),
                    solar_radiation=data.get("solar_radiation", 5.0)
                )
                
                self.db.add(db_weather)
                added_count += 1
                
                # Commit in batches to avoid large transactions
                if added_count % 100 == 0:
                    self.db.commit()
            
            # Final commit for remaining records
            if added_count % 100 != 0:
                self.db.commit()
                
            logger.info(f"Saved {added_count} weather data records to database")
            return True
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving weather data: {e}")
            return False