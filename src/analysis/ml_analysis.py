import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.feature_selection import SelectFromModel
import xgboost as xgb
from prophet import Prophet
import joblib
import os
from datetime import datetime, timedelta
import logging
import warnings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("agrivoltaics_analysis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AgrivoltaicsAnalysis")

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

class AgrivoltaicsAnalysis:
    """
    Class for analyzing and predicting agrivoltaics system performance
    based on historical data.
    """
    
    def __init__(self, data_path=None):
        """
        Initialize the analysis with optional data path
        
        Args:
            data_path (str): Path to data files
        """
        self.data_path = data_path or './data'
        self.energy_data = None
        self.crop_data = None
        self.weather_data = None
        self.combined_data = None
        self.energy_model = None
        self.crop_model = None
        self.forecast_model = None
        self.scaler = None
        self.optimized_config = None
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_path, exist_ok=True)
        
        logger.info(f"Initialized AgrivoltaicsAnalysis with data path: {self.data_path}")
        
    def load_data(self, energy_file=None, crop_file=None, weather_file=None):
        """
        Load data from CSV files
        
        Args:
            energy_file (str): Path to energy production data
            crop_file (str): Path to crop yield data
            weather_file (str): Path to weather data
            
        Returns:
            tuple: Loaded dataframes (energy_data, crop_data, weather_data)
        """
        # Load energy data
        if energy_file:
            try:
                self.energy_data = pd.read_csv(os.path.join(self.data_path, energy_file))
                logger.info(f"Energy data loaded: {self.energy_data.shape}")
                logger.info(f"Energy data columns: {self.energy_data.columns.tolist()}")
            except Exception as e:
                logger.error(f"Error loading energy data: {e}")
                self.energy_data = None
        
        # Load crop data
        if crop_file:
            try:
                self.crop_data = pd.read_csv(os.path.join(self.data_path, crop_file))
                logger.info(f"Crop data loaded: {self.crop_data.shape}")
                logger.info(f"Crop data columns: {self.crop_data.columns.tolist()}")
            except Exception as e:
                logger.error(f"Error loading crop data: {e}")
                self.crop_data = None
        
        # Load weather data
        if weather_file:
            try:
                self.weather_data = pd.read_csv(os.path.join(self.data_path, weather_file))
                logger.info(f"Weather data loaded: {self.weather_data.shape}")
                logger.info(f"Weather data columns: {self.weather_data.columns.tolist()}")
            except Exception as e:
                logger.error(f"Error loading weather data: {e}")
                self.weather_data = None
        
        return self.energy_data, self.crop_data, self.weather_data
    
    def explore_data(self):
        """
        Perform exploratory data analysis on the loaded datasets
        
        Returns:
            dict: Summary statistics and correlation data
        """
        results = {}
        
        # Analyze energy data
        if self.energy_data is not None:
            results['energy'] = {
                'summary': self.energy_data.describe(),
                'missing_values': self.energy_data.isnull().sum(),
                'data_types': self.energy_data.dtypes
            }
            
            # Check for datetime column and convert if needed
            date_cols = [col for col in self.energy_data.columns if 'date' in col.lower() or 'time' in col.lower()]
            if date_cols:
                self.energy_data[date_cols[0]] = pd.to_datetime(self.energy_data[date_cols[0]])
                results['energy']['date_range'] = (
                    self.energy_data[date_cols[0]].min(),
                    self.energy_data[date_cols[0]].max()
                )
        
        # Analyze crop data
        if self.crop_data is not None:
            results['crop'] = {
                'summary': self.crop_data.describe(),
                'missing_values': self.crop_data.isnull().sum(),
                'data_types': self.crop_data.dtypes
            }
            
            # Check for datetime column and convert if needed
            date_cols = [col for col in self.crop_data.columns if 'date' in col.lower() or 'time' in col.lower()]
            if date_cols:
                self.crop_data[date_cols[0]] = pd.to_datetime(self.crop_data[date_cols[0]])
                results['crop']['date_range'] = (
                    self.crop_data[date_cols[0]].min(),
                    self.crop_data[date_cols[0]].max()
                )
        
        # Analyze weather data
        if self.weather_data is not None:
            results['weather'] = {
                'summary': self.weather_data.describe(),
                'missing_values': self.weather_data.isnull().sum(),
                'data_types': self.weather_data.dtypes
            }
            
            # Check for datetime column and convert if needed
            date_cols = [col for col in self.weather_data.columns if 'date' in col.lower() or 'time' in col.lower()]
            if date_cols:
                self.weather_data[date_cols[0]] = pd.to_datetime(self.weather_data[date_cols[0]])
                results['weather']['date_range'] = (
                    self.weather_data[date_cols[0]].min(),
                    self.weather_data[date_cols[0]].max()
                )
        
        logger.info("Exploratory data analysis completed")
        return results
    
    def preprocess_data(self, merge_datasets=True):
        """
        Preprocess and clean the data for analysis
        
        Args:
            merge_datasets (bool): Whether to merge available datasets
            
        Returns:
            pandas.DataFrame: Preprocessed data
        """
        logger.info("Starting data preprocessing")
        
        # Handle missing values in energy data
        if self.energy_data is not None:
            # Fill missing energy values with interpolation for time series
            numeric_cols = self.energy_data.select_dtypes(include=['float64', 'int64']).columns
            self.energy_data[numeric_cols] = self.energy_data[numeric_cols].interpolate(method='time')
            
            # Convert date column to datetime if it exists and isn't already
            date_cols = [col for col in self.energy_data.columns if 'date' in col.lower() or 'time' in col.lower()]
            if date_cols:
                if not pd.api.types.is_datetime64_any_dtype(self.energy_data[date_cols[0]]):
                    self.energy_data[date_cols[0]] = pd.to_datetime(self.energy_data[date_cols[0]])
        
        # Handle missing values in crop data
        if self.crop_data is not None:
            # Fill missing crop values with interpolation for time series
            numeric_cols = self.crop_data.select_dtypes(include=['float64', 'int64']).columns
            self.crop_data[numeric_cols] = self.crop_data[numeric_cols].interpolate(method='time')
            
            # Convert date column to datetime if it exists and isn't already
            date_cols = [col for col in self.crop_data.columns if 'date' in col.lower() or 'time' in col.lower()]
            if date_cols:
                if not pd.api.types.is_datetime64_any_dtype(self.crop_data[date_cols[0]]):
                    self.crop_data[date_cols[0]] = pd.to_datetime(self.crop_data[date_cols[0]])
        
        # Handle missing values in weather data
        if self.weather_data is not None:
            # Fill missing weather values with interpolation for time series
            numeric_cols = self.weather_data.select_dtypes(include=['float64', 'int64']).columns
            self.weather_data[numeric_cols] = self.weather_data[numeric_cols].interpolate(method='time')
            
            # Convert date column to datetime if it exists and isn't already
            date_cols = [col for col in self.weather_data.columns if 'date' in col.lower() or 'time' in col.lower()]
            if date_cols:
                if not pd.api.types.is_datetime64_any_dtype(self.weather_data[date_cols[0]]):
                    self.weather_data[date_cols[0]] = pd.to_datetime(self.weather_data[date_cols[0]])
        
        # Merge datasets if requested and possible
        if merge_datasets:
            dfs_to_merge = []
            date_columns = []
            
            # Add available dataframes to the merge list
            if self.energy_data is not None:
                dfs_to_merge.append(self.energy_data)
                date_cols = [col for col in self.energy_data.columns if 'date' in col.lower() or 'time' in col.lower()]
                if date_cols:
                    date_columns.append(date_cols[0])
            
            if self.crop_data is not None:
                dfs_to_merge.append(self.crop_data)
                date_cols = [col for col in self.crop_data.columns if 'date' in col.lower() or 'time' in col.lower()]
                if date_cols:
                    date_columns.append(date_cols[0])
            
            if self.weather_data is not None:
                dfs_to_merge.append(self.weather_data)
                date_cols = [col for col in self.weather_data.columns if 'date' in col.lower() or 'time' in col.lower()]
                if date_cols:
                    date_columns.append(date_cols[0])
            
            # If we have multiple dataframes and date columns, merge them
            if len(dfs_to_merge) > 1 and len(date_columns) > 0:
                # Use the first date column as the merge key
                merge_col = date_columns[0]
                
                # Start with the first dataframe
                merged_df = dfs_to_merge[0].copy()
                
                # Merge with other dataframes
                for i in range(1, len(dfs_to_merge)):
                    df = dfs_to_merge[i]
                    # Find the date column in this dataframe
                    date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
                    if date_cols:
                        # Rename the date column to match the merge key if needed
                        if date_cols[0] != merge_col:
                            df = df.rename(columns={date_cols[0]: merge_col})
                        
                        # Merge the dataframes
                        merged_df = pd.merge(merged_df, df, on=merge_col, how='outer')
                
                # Store the merged dataframe
                self.combined_data = merged_df
                logger.info(f"Combined data shape: {self.combined_data.shape}")
                return self.combined_data
            elif len(dfs_to_merge) == 1:
                # If only one dataframe is available, return it
                self.combined_data = dfs_to_merge[0].copy()
                logger.info(f"Only one dataset available, using it as combined data.")
                return self.combined_data
            else:
                logger.warning("Could not merge datasets due to missing data or date columns.")
                return None
        else:
            # Return a dictionary of processed dataframes
            return {
                'energy': self.energy_data,
                'crop': self.crop_data,
                'weather': self.weather_data
            }
    
    def feature_engineering(self, data=None):
        """
        Create new features from existing data
        
        Args:
            data (pandas.DataFrame): Data to perform feature engineering on
            
        Returns:
            pandas.DataFrame: Data with new features
        """
        logger.info("Starting feature engineering")
        
        # Use combined data if none provided
        df = data if data is not None else self.combined_data
        
        if df is None:
            logger.warning("No data available for feature engineering.")
            return None
        
        # Find date column
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        if not date_cols:
            logger.warning("No date column found for feature engineering.")
            return df
        
        date_col = date_cols[0]
        
        # Ensure date column is datetime
        if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
            df[date_col] = pd.to_datetime(df[date_col])
        
        # Extract date features
        df['day_of_year'] = df[date_col].dt.dayofyear
        df['month'] = df[date_col].dt.month
        df['day_of_month'] = df[date_col].dt.day
        df['year'] = df[date_col].dt.year
        df['day_of_week'] = df[date_col].dt.dayofweek
        df['quarter'] = df[date_col].dt.quarter
        df['is_weekend'] = df[date_col].dt.dayofweek >= 5
        
        # Create season feature (Northern Hemisphere)
        df['season'] = df['month'].map(
            lambda month: 'Winter' if month in [12, 1, 2] else
                         'Spring' if month in [3, 4, 5] else
                         'Summer' if month in [6, 7, 8] else 'Fall'
        )
        
        # Solar position features (if latitude is available)
        if 'latitude' in df.columns:
            latitude = df['latitude'].mean()
            # Solar declination (simplified)
            df['solar_declination'] = df['day_of_year'].apply(
                lambda doy: 23.45 * np.sin(np.radians((360/365) * (doy - 81)))
            )
            # Solar elevation at noon (simplified)
            df['solar_elevation_noon'] = 90 - latitude + df['solar_declination']
        
        # Check for temperature columns
        temp_cols = [col for col in df.columns if 'temp' in col.lower()]
        if temp_cols:
            # Temperature difference (if min and max are available)
            if 'temp_min' in temp_cols and 'temp_max' in temp_cols:
                df['temp_range'] = df['temp_max'] - df['temp_min']
            
            # Temperature stress for common crops
            if any('temp' in col.lower() for col in temp_cols):
                temp_col = [col for col in temp_cols if 'temp_avg' in col.lower() or 'temperature' in col.lower()]
                if temp_col:
                    # Use first available temperature column
                    df['temp_stress_lettuce'] = df[temp_col[0]].apply(
                        lambda t: 1.0 if 15 <= t <= 25 else 
                                 1.0 - min(1.0, abs(t - 20) / 10)
                    )
        
        # Check for radiation columns
        rad_cols = [col for col in df.columns if 'rad' in col.lower() or 'irrad' in col.lower()]
        if rad_cols:
            # Normalize radiation to 0-1 scale
            rad_col = rad_cols[0]
            df['normalized_radiation'] = (df[rad_col] - df[rad_col].min()) / (df[rad_col].max() - df[rad_col].min())
        
        # Check for shadow-related columns
        shadow_cols = [col for col in df.columns if 'shadow' in col.lower() or 'shade' in col.lower()]
        if shadow_cols:
            # Shadow impact on crop (example for lettuce with 70% shade tolerance)
            shadow_col = shadow_cols[0]
            df['shadow_impact'] = df[shadow_col] * (1 - 0.7)  # Assuming 70% shade tolerance
        
        # Check for panel configuration columns
        panel_height_cols = [col for col in df.columns if 'panel_height' in col.lower()]
        panel_angle_cols = [col for col in df.columns if 'panel_angle' in col.lower()]
        panel_spacing_cols = [col for col in df.columns if 'panel_spacing' in col.lower()]
        
        if panel_height_cols and panel_angle_cols and panel_spacing_cols:
            # Calculate shadow length (simplified)
            df['shadow_length'] = df[panel_height_cols[0]] * np.tan(np.radians(df[panel_angle_cols[0]]))
            
            # Calculate shadow coverage ratio
            df['shadow_coverage_ratio'] = df['shadow_length'] / df[panel_spacing_cols[0]]
        
        # Check for water-related columns
        water_cols = [col for col in df.columns if 'water' in col.lower() or 'rain' in col.lower() or 'precip' in col.lower()]
        if water_cols:
            # Group water-related features
            rain_cols = [col for col in water_cols if 'rain' in col.lower() or 'precip' in col.lower()]
            irrigation_cols = [col for col in water_cols if 'irrig' in col.lower()]
            
            if rain_cols and irrigation_cols:
                # Calculate total water input
                df['total_water_input'] = df[rain_cols[0]] + df[irrigation_cols[0]]
                
                # Water stress for crop (example)
                df['water_stress'] = df['total_water_input'].apply(
                    lambda w: min(1.0, w / 4.5)  # Assuming 4.5mm is optimal for lettuce
                )
                
                # Water efficiency
                if 'temperature' in df.columns or any('temp' in col.lower() for col in temp_cols):
                    temp_col = temp_cols[0] if temp_cols else 'temperature'
                    # Simplified evapotranspiration based on temperature
                    df['water_efficiency'] = df.apply(
                        lambda row: row['total_water_input'] / (0.5 + 0.05 * row[temp_col]),
                        axis=1
                    )
        
        logger.info(f"Feature engineering complete. New features added: {len(df.columns) - len(self.combined_data.columns)}")
        return df
    
    def visualize_data(self, data=None, output_dir=None):
        """
        Create visualizations of the data
        
        Args:
            data (pandas.DataFrame): Data to visualize
            output_dir (str): Directory to save visualization files
            
        Returns:
            dict: Dictionary of matplotlib figures
        """
        logger.info("Starting data visualization")
        
        # Use combined data if none provided
        df = data if data is not None else self.combined_data
        
        if df is None:
            logger.warning("No data available for visualization.")
            return None
        
        # Create output directory if provided
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        figures = {}
        
        # Find date column
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        if not date_cols:
            logger.warning("No date column found for time series visualization.")
        else:
            date_col = date_cols[0]
            
            # Energy production over time (if available)
            energy_cols = [col for col in df.columns if 'energy' in col.lower() or 'power' in col.lower()]
            if energy_cols:
                fig, ax = plt.subplots(figsize=(12, 6))
                df.plot(x=date_col, y=energy_cols[0], ax=ax)
                ax.set_title('Energy Production Over Time')
                ax.set_xlabel('Date')
                ax.set_ylabel('Energy (kWh)')
                ax.grid(True)
                figures['energy_time_series'] = fig
                
                if output_dir:
                    fig.savefig(os.path.join(output_dir, 'energy_time_series.png'))
            
            # Crop yield over time (if available)
            crop_cols = [col for col in df.columns if 'crop' in col.lower() or 'yield' in col.lower()]
            if crop_cols:
                fig, ax = plt.subplots(figsize=(12, 6))
                df.plot(x=date_col, y=crop_cols[0], ax=ax)
                ax.set_title('Crop Yield Over Time')
                ax.set_xlabel('Date')
                ax.set_ylabel('Yield (kg)')
                ax.grid(True)
                figures['crop_time_series'] = fig
                
                if output_dir:
                    fig.savefig(os.path.join(output_dir, 'crop_time_series.png'))
        
        # Correlation heatmap for numeric columns
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) > 1:
            fig, ax = plt.subplots(figsize=(12, 10))
            sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm', ax=ax)
            ax.set_title('Correlation Matrix')
            figures['correlation_heatmap'] = fig
            
            if output_dir:
                fig.savefig(os.path.join(output_dir, 'correlation_heatmap.png'))
        
        # Boxplots for key features
        key_features = []
        for term in ['energy', 'yield', 'temp', 'rad', 'water', 'shadow']:
            cols = [col for col in df.columns if term in col.lower()]
            if cols:
                key_features.extend(cols[:2])  # Add up to 2 columns for each term
        
        if key_features:
            fig, axes = plt.subplots(nrows=len(key_features), figsize=(10, 3*len(key_features)))
            if len(key_features) == 1:
                axes = [axes]
            
            for i, feature in enumerate(key_features):
                sns.boxplot(x=df[feature], ax=axes[i])
                axes[i].set_title(f'{feature} Distribution')
                axes[i].grid(True)
            
            plt.tight_layout()
            figures['feature_boxplots'] = fig
            
            if output_dir:
                fig.savefig(os.path.join(output_dir, 'feature_boxplots.png'))
        
        # Monthly patterns (if date is available)
        if date_cols:
            if 'month' not in df.columns:
                df['month'] = df[date_cols[0]].dt.month
            
            # Monthly energy patterns
            energy_cols = [col for col in df.columns if 'energy' in col.lower() or 'power' in col.lower()]
            if energy_cols:
                fig, ax = plt.subplots(figsize=(12, 6))
                monthly_energy = df.groupby('month')[energy_cols[0]].mean()
                monthly_energy.plot(kind='bar', ax=ax)
                ax.set_title('Average Monthly Energy Production')
                ax.set_xlabel('Month')
                ax.set_ylabel('Energy (kWh)')
                ax.set_xticks(range(12))
                ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
                ax.grid(True)
                figures['monthly_energy'] = fig
                
                if output_dir:
                    fig.savefig(os.path.join(output_dir, 'monthly_energy.png'))
            
            # Monthly crop patterns
            crop_cols = [col for col in df.columns if 'crop' in col.lower() or 'yield' in col.lower()]
            if crop_cols:
                fig, ax = plt.subplots(figsize=(12, 6))
                monthly_crop = df.groupby('month')[crop_cols[0]].mean()
                monthly_crop.plot(kind='bar', ax=ax)
                ax.set_title('Average Monthly Crop Yield')
                ax.set_xlabel('Month')
                ax.set_ylabel('Yield (kg)')
                ax.set_xticks(range(12))
                ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
                ax.grid(True)
                figures['monthly_crop'] = fig
                
                if output_dir:
                    fig.savefig(os.path.join(output_dir, 'monthly_crop.png'))
        
        # Shadow impact visualization (if shadow data available)
        shadow_cols = [col for col in df.columns if 'shadow' in col.lower() or 'shade' in col.lower()]
        crop_cols = [col for col in df.columns if 'crop' in col.lower() or 'yield' in col.lower()]
        
        if shadow_cols and crop_cols:
            fig, ax = plt.subplots(figsize=(10, 6))
            shadow_col = shadow_cols[0]
            crop_col = crop_cols[0]
            
            # Create bins for shadow values
            shadow_bins = pd.cut(df[shadow_col], bins=5)
            shadow_yield = df.groupby(shadow_bins)[crop_col].mean()
            
            shadow_yield.plot(kind='bar', ax=ax)
            ax.set_title('Average Crop Yield by Shadow Level')
            ax.set_xlabel('Shadow Level')
            ax.set_ylabel('Yield (kg)')
            ax.grid(True)
            figures['shadow_yield_impact'] = fig
            
            if output_dir:
                fig.savefig(os.path.join(output_dir, 'shadow_yield_impact.png'))
        
        logger.info(f"Data visualization complete. Generated {len(figures)} visualizations.")
        return figures
    
    def train_energy_model(self, data=None, target_col=None, features=None, test_size=0.2):
        """
        Train a machine learning model to predict energy production
        
        Args:
            data (pandas.DataFrame): Data to use for training
            target_col (str): Target column name (energy production)
            features (list): List of feature column names
            test_size (float): Test set proportion
            
        Returns:
            dict: Model evaluation metrics and model object
        """
        logger.info("Starting energy model training")
        
        # Use combined data if none provided
        df = data if data is not None else self.combined_data
        
        if df is None:
            logger.warning("No data available for model training.")
            return None
        
        # Detect target column if not specified
        if target_col is None:
            energy_cols = [col for col in df.columns if 'energy' in col.lower() or 'power' in col.lower()]
            if energy_cols:
                target_col = energy_cols[0]
            else:
                logger.warning("No energy production column found.")
                return None
        
        # Select features if not specified
        if features is None:
            # Exclude target and non-feature columns
            exclude_cols = [target_col] + [col for col in df.columns if 'date' in col.lower() or 'id' in col.lower()]
            features = [col for col in df.columns if col not in exclude_cols]
        
        # Prepare data
        X = df[features]
        y = df[target_col]
        
        # Identify numeric and categorical features
        numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Create preprocessing pipeline
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numeric_features),
                ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), categorical_features)
            ],
            remainder='drop'
        )
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
        
        # Create and evaluate models
        models = {
            'Linear Regression': LinearRegression(),
            'Ridge Regression': Ridge(alpha=1.0),
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'XGBoost': xgb.XGBRegressor(n_estimators=100, random_state=42)
        }
        
        results = {}
        
        for name, model in models.items():
            # Create pipeline
            pipeline = Pipeline([
                ('preprocessor', preprocessor),
                ('model', model)
            ])
            
            # Fit the model
            pipeline.fit(X_train, y_train)
            
            # Make predictions
            y_pred = pipeline.predict(X_test)
            
            # Evaluate the model
            results[name] = {
                'r2': r2_score(y_test, y_pred),
                'mse': mean_squared_error(y_test, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                'mae': mean_absolute_error(y_test, y_pred),
                'model': pipeline
            }
            
            logger.info(f"{name} - R²: {results[name]['r2']:.4f}, RMSE: {results[name]['rmse']:.4f}")
        
        # Find the best model
        best_model_name = max(results.keys(), key=lambda k: results[k]['r2'])
        best_model = results[best_model_name]['model']
        
        logger.info(f"\nBest model: {best_model_name}")
        logger.info(f"R²: {results[best_model_name]['r2']:.4f}")
        logger.info(f"RMSE: {results[best_model_name]['rmse']:.4f}")
        
        # Save the best model
        self.energy_model = best_model
        
        # Feature importance for tree-based models
        if 'Random Forest' in best_model_name or 'Gradient Boosting' in best_model_name or 'XGBoost' in best_model_name:
            # Extract feature names after preprocessing
            feature_names = numeric_features.copy()
            if categorical_features:
                # Get one-hot encoded feature names
                encoder = preprocessor.transformers_[1][1]
                cat_feature_names = []
                for i, cat_feature in enumerate(categorical_features):
                    categories = encoder.categories_[i][1:]  # Drop first category
                    cat_feature_names.extend([f"{cat_feature}_{cat}" for cat in categories])
                feature_names.extend(cat_feature_names)
            
            # Get feature importances
            model_step = best_model.named_steps['model']
            importances = model_step.feature_importances_
            
            # Sort features by importance
            indices = np.argsort(importances)[::-1]
            
            # Print feature ranking
            logger.info("\nFeature ranking:")
            top_features = []
            for f in range(min(10, len(indices))):
                if f < len(feature_names):
                    logger.info(f"{f+1}. {feature_names[indices[f]]} ({importances[indices[f]]:.4f})")
                    top_features.append((feature_names[indices[f]], importances[indices[f]]))
            
            results['feature_importance'] = top_features
        
        return results