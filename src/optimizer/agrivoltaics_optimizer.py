import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Input, LSTM, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import xgboost as xgb
from prophet import Prophet
import joblib
import os

class AgrivoltaicsOptimizer:
    """
    Core ML model for optimizing agrivoltaics systems by balancing 
    solar energy production and crop yield.
    """
    
    def __init__(self, config=None):
        """
        Initialize the optimizer with configuration settings.
        
        Args:
            config (dict): Configuration parameters
        """
        self.config = config or {
            'model_path': './models/',
            'data_path': './data/',
            'batch_size': 64,
            'epochs': 100,
            'learning_rate': 0.001,
            'validation_split': 0.2,
            'random_state': 42
        }
        
        # Create model directory if it doesn't exist
        os.makedirs(self.config['model_path'], exist_ok=True)
        
        # Initialize models
        self.solar_model = None
        self.crop_model = None
        self.forecasting_model = None
        self.optimization_model = None
        self.scaler_X = StandardScaler()
        self.scaler_y = StandardScaler()
        
    def load_and_preprocess_data(self, data_path=None):
        """
        Load and preprocess the data for training.
        
        Args:
            data_path (str): Path to the data directory
            
        Returns:
            tuple: Processed X_train, X_test, y_train, y_test
        """
        data_path = data_path or self.config['data_path']
        
        # Load data
        # In a real implementation, this would load from files or APIs
        # For simulation, we'll generate synthetic data
        
        # Generate synthetic data for demonstration
        n_samples = 10000
        
        # Features: weather, panel configuration, crop type, soil quality
        X = np.random.rand(n_samples, 15)  
        
        # Targets: [solar_output, crop_yield]
        y = np.zeros((n_samples, 2))
        
        # Simplified model for solar output based on features
        y[:, 0] = (0.7 * X[:, 0] +  # solar irradiance
                  0.2 * X[:, 1] +   # panel angle
                  0.1 * X[:, 2] +   # temperature
                  0.05 * X[:, 3] -  # cloud cover
                  0.05 * X[:, 4] +  # panel efficiency
                  np.random.normal(0, 0.1, n_samples))  # noise
        
        # Simplified model for crop yield based on features
        y[:, 1] = (0.4 * X[:, 5] +  # soil quality
                  0.3 * X[:, 6] +   # water input
                  0.2 * X[:, 7] -   # shadow percentage
                  0.1 * X[:, 8] +   # temperature
                  0.1 * X[:, 9] +   # fertilizer
                  np.random.normal(0, 0.15, n_samples))  # noise
                  
        # Scale features between 0-1 for neural network training
        X_scaled = self.scaler_X.fit_transform(X)
        y_scaled = self.scaler_y.fit_transform(y)
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_scaled, 
            test_size=self.config['validation_split'],
            random_state=self.config['random_state']
        )
        
        # Create a dataframe for time series forecasting
        dates = pd.date_range(start='2023-01-01', periods=n_samples)
        self.time_series_data = pd.DataFrame({
            'ds': dates,
            'y_solar': y[:, 0],
            'y_crop': y[:, 1]
        })
        
        return X_train, X_test, y_train, y_test
    
    def build_deep_model(self):
        """
        Build a deep neural network model for integrated prediction.
        
        Returns:
            tensorflow.keras.Model: Compiled model
        """
        inputs = Input(shape=(15,))
        
        # First branch for solar prediction
        x1 = Dense(64, activation='relu')(inputs)
        x1 = BatchNormalization()(x1)
        x1 = Dense(32, activation='relu')(x1)
        solar_output = Dense(1, name='solar_output')(x1)
        
        # Second branch for crop yield prediction
        x2 = Dense(64, activation='relu')(inputs)
        x2 = BatchNormalization()(x2)
        x2 = Dense(32, activation='relu')(x2)
        crop_output = Dense(1, name='crop_output')(x2)
        
        # Combined model
        model = Model(inputs=inputs, outputs=[solar_output, crop_output])
        
        # Compile the model
        model.compile(
            optimizer=Adam(learning_rate=self.config['learning_rate']),
            loss={'solar_output': 'mse', 'crop_output': 'mse'},
            metrics={'solar_output': 'mae', 'crop_output': 'mae'}
        )
        
        return model
    
    def build_time_series_model(self):
        """
        Build a Prophet model for time series forecasting.
        
        Returns:
            list: List of Prophet models for solar and crop forecasting
        """
        # Solar energy forecasting model
        solar_model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=True,
            changepoint_prior_scale=0.05
        )
        
        # Crop yield forecasting model
        crop_model = Prophet(
            yearly_seasonality=True, 
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=0.01
        )
        
        return [solar_model, crop_model]
    
    def build_optimization_model(self):
        """
        Build an XGBoost model for optimization recommendations.
        
        Returns:
            xgboost.XGBRegressor: Trained XGBoost model
        """
        # XGBoost for panel configuration optimization
        return xgb.XGBRegressor(
            objective='reg:squarederror',
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=self.config['random_state']
        )
    
    def train_deep_model(self, X_train, y_train):
        """
        Train the deep neural network model.
        
        Args:
            X_train (numpy.ndarray): Training features
            y_train (numpy.ndarray): Training targets
            
        Returns:
            tensorflow.keras.callbacks.History: Training history
        """
        self.deep_model = self.build_deep_model()
        
        # Prepare the target for multi-output model
        y_solar = y_train[:, 0].reshape(-1, 1)
        y_crop = y_train[:, 1].reshape(-1, 1)
        
        # Set up callbacks
        callbacks = [
            EarlyStopping(patience=10, restore_best_weights=True),
            ModelCheckpoint(
                filepath=os.path.join(self.config['model_path'], 'deep_model.h5'),
                save_best_only=True
            )
        ]
        
        # Train the model
        history = self.deep_model.fit(
            X_train,
            {'solar_output': y_solar, 'crop_output': y_crop},
            epochs=self.config['epochs'],
            batch_size=self.config['batch_size'],
            validation_split=0.2,
            callbacks=callbacks,
            verbose=1
        )
        
        return history
    
    def train_time_series_model(self):
        """
        Train the Prophet models for time series forecasting.
        
        Returns:
            list: Trained Prophet models
        """
        # Train solar forecasting model
        solar_data = self.time_series_data[['ds', 'y_solar']].rename(columns={'y_solar': 'y'})
        self.solar_prophet = self.build_time_series_model()[0]
        self.solar_prophet.fit(solar_data)
        
        # Train crop forecasting model
        crop_data = self.time_series_data[['ds', 'y_crop']].rename(columns={'y_crop': 'y'})
        self.crop_prophet = self.build_time_series_model()[1]
        self.crop_prophet.fit(crop_data)
        
        return [self.solar_prophet, self.crop_prophet]
    
    def train_optimization_model(self, X_train, y_train):
        """
        Train the XGBoost model for optimization.
        
        Args:
            X_train (numpy.ndarray): Training features
            y_train (numpy.ndarray): Training targets
            
        Returns:
            xgboost.XGBRegressor: Trained XGBoost model
        """
        # We'll train it to optimize a combined metric of solar + crop
        combined_target = 0.6 * y_train[:, 0] + 0.4 * y_train[:, 1]  # 60/40 weight
        
        self.optimization_model = self.build_optimization_model()
        self.optimization_model.fit(X_train, combined_target)
        
        # Save the model
        joblib.dump(
            self.optimization_model, 
            os.path.join(self.config['model_path'], 'optimization_model.pkl')
        )
        
        return self.optimization_model
    
    def train_all_models(self):
        """
        Train all models in the system.
        
        Returns:
            dict: Dictionary containing all trained models
        """
        # Load and preprocess data
        X_train, X_test, y_train, y_test = self.load_and_preprocess_data()
        
        # Train deep model
        deep_history = self.train_deep_model(X_train, y_train)
        
        # Train time series models
        time_series_models = self.train_time_series_model()
        
        # Train optimization model
        opt_model = self.train_optimization_model(X_train, y_train)
        
        # Evaluate models
        deep_eval = self.evaluate_deep_model(X_test, y_test)
        
        return {
            'deep_model': self.deep_model,
            'time_series_models': time_series_models,
            'optimization_model': opt_model,
            'evaluation': deep_eval,
            'training_history': deep_history
        }
    
    def evaluate_deep_model(self, X_test, y_test):
        """
        Evaluate the deep neural network model.
        
        Args:
            X_test (numpy.ndarray): Test features
            y_test (numpy.ndarray): Test targets
            
        Returns:
            dict: Evaluation metrics
        """
        # Prepare the target for multi-output model
        y_solar = y_test[:, 0].reshape(-1, 1)
        y_crop = y_test[:, 1].reshape(-1, 1)
        
        # Evaluate the model
        results = self.deep_model.evaluate(
            X_test, 
            {'solar_output': y_solar, 'crop_output': y_crop},
            verbose=0
        )
        
        # Prepare evaluation dict
        metrics = {
            'loss': results[0],
            'solar_loss': results[1],
            'crop_loss': results[2],
            'solar_mae': results[3],
            'crop_mae': results[4]
        }
        
        return metrics
    
    def forecast_production(self, periods=365):
        """
        Forecast future solar production and crop yield.
        
        Args:
            periods (int): Number of days to forecast
            
        Returns:
            tuple: DataFrames with solar and crop forecasts
        """
        # Generate future dataframe
        future_solar = self.solar_prophet.make_future_dataframe(
            periods=periods, 
            freq='D'
        )
        future_crop = self.crop_prophet.make_future_dataframe(
            periods=periods, 
            freq='D'
        )
        
        # Make predictions
        solar_forecast = self.solar_prophet.predict(future_solar)
        crop_forecast = self.crop_prophet.predict(future_crop)
        
        return solar_forecast, crop_forecast
    
    def optimize_configuration(self, weather_forecast, constraints):
        """
        Optimize panel configuration based on forecasts and constraints.
        
        Args:
            weather_forecast (pandas.DataFrame): Weather forecast data
            constraints (dict): System constraints
            
        Returns:
            dict: Optimized configuration parameters
        """
        # Preprocess inputs
        X = self._prepare_optimization_input(weather_forecast, constraints)
        X_scaled = self.scaler_X.transform(X)
        
        # Generate multiple candidate configurations
        n_candidates = 1000
        candidates = np.random.rand(n_candidates, X.shape[1])
        candidates[:, :X.shape[1]] = X_scaled
        
        # Apply constraints to candidates
        # (In a real implementation, this would enforce physical constraints)
        
        # Predict outcomes for all candidates
        scores = self.optimization_model.predict(candidates)
        
        # Select the best configuration
        best_idx = np.argmax(scores)
        best_config = candidates[best_idx]
        
        # Inverse transform to get real values
        best_config_real = self.scaler_X.inverse_transform(best_config.reshape(1, -1))
        
        # Map numerical values to actual configuration parameters
        config_params = {
            'panel_angle': best_config_real[0, 1],
            'panel_spacing': best_config_real[0, 4],
            'panel_height': best_config_real[0, 5],
            'irrigation_schedule': self._generate_irrigation_schedule(best_config_real),
            'expected_solar_output': self._predict_output(best_config_real)[0],
            'expected_crop_yield': self._predict_output(best_config_real)[1]
        }
        
        return config_params
    
    def _prepare_optimization_input(self, weather_forecast, constraints):
        """
        Prepare input for optimization from weather forecast and constraints.
        
        Args:
            weather_forecast (pandas.DataFrame): Weather forecast data
            constraints (dict): System constraints
            
        Returns:
            numpy.ndarray: Prepared input features
        """
        # This would extract relevant features from the weather forecast
        # and combine them with system constraints
        # For simulation, we'll create random data
        return np.random.rand(1, 15)
    
    def _generate_irrigation_schedule(self, config):
        """
        Generate an optimal irrigation schedule based on configuration.
        
        Args:
            config (numpy.ndarray): System configuration
            
        Returns:
            dict: Irrigation schedule
        """
        # This would generate a daily irrigation schedule
        # For simulation, we'll return a simple schedule
        return {
            'morning_duration': int(config[0, 6] * 60),  # minutes
            'evening_duration': int(config[0, 7] * 30),  # minutes
            'threshold': config[0, 8] * 100  # soil moisture threshold
        }
    
    def _predict_output(self, config):
        """
        Predict solar output and crop yield for a configuration.
        
        Args:
            config (numpy.ndarray): System configuration
            
        Returns:
            tuple: Predicted solar output and crop yield
        """
        # Reshape and scale for prediction
        X = config.reshape(1, -1)
        X_scaled = self.scaler_X.transform(X)
        
        # Get predictions from deep model
        predictions = self.deep_model.predict(X_scaled)
        
        # Inverse transform to get real values
        predictions_real = self.scaler_y.inverse_transform(
            np.hstack([predictions[0], predictions[1]])
        )
        
        return predictions_real[0, 0], predictions_real[0, 1]
    
    def visualize_results(self, history=None, forecasts=None):
        """
        Visualize training results and forecasts.
        
        Args:
            history (tensorflow.keras.callbacks.History): Training history
            forecasts (tuple): Solar and crop forecasts
            
        Returns:
            tuple: Figure objects
        """
        figures = []
        
        # Visualize training history
        if history:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
            
            # Plot solar output loss
            ax1.plot(history.history['solar_output_loss'], label='Train')
            ax1.plot(history.history['val_solar_output_loss'], label='Validation')
            ax1.set_title('Solar Output Loss')
            ax1.set_xlabel('Epoch')
            ax1.set_ylabel('Loss')
            ax1.legend()
            
            # Plot crop output loss
            ax2.plot(history.history['crop_output_loss'], label='Train')
            ax2.plot(history.history['val_crop_output_loss'], label='Validation')
            ax2.set_title('Crop Yield Loss')
            ax2.set_xlabel('Epoch')
            ax2.set_ylabel('Loss')
            ax2.legend()
            
            plt.tight_layout()
            figures.append(fig)
        
        # Visualize forecasts
        if forecasts:
            solar_forecast, crop_forecast = forecasts
            
            # Solar forecast plot
            fig1 = plt.figure(figsize=(14, 7))
            self.solar_prophet.plot(solar_forecast)
            plt.title('Solar Energy Production Forecast')
            plt.tight_layout()
            figures.append(fig1)
            
            # Crop forecast plot
            fig2 = plt.figure(figsize=(14, 7))
            self.crop_prophet.plot(crop_forecast)
            plt.title('Crop Yield Forecast')
            plt.tight_layout()
            figures.append(fig2)
            
            # Components plot for solar
            fig3 = plt.figure(figsize=(14, 10))
            self.solar_prophet.plot_components(solar_forecast)
            plt.tight_layout()
            figures.append(fig3)
        
        return tuple(figures)
    
    def save_models(self):
        """
        Save all models to disk.
        
        Returns:
            bool: Success status
        """
        try:
            # Save deep model
            if self.deep_model:
                self.deep_model.save(os.path.join(self.config['model_path'], 'deep_model.h5'))
            
            # Save Prophet models (requires custom pickling)
            if hasattr(self, 'solar_prophet'):
                with open(os.path.join(self.config['model_path'], 'solar_prophet.pkl'), 'wb') as f:
                    joblib.dump(self.solar_prophet, f)
            
            if hasattr(self, 'crop_prophet'):
                with open(os.path.join(self.config['model_path'], 'crop_prophet.pkl'), 'wb') as f:
                    joblib.dump(self.crop_prophet, f)
            
            # Save XGBoost model
            if self.optimization_model:
                joblib.dump(
                    self.optimization_model, 
                    os.path.join(self.config['model_path'], 'optimization_model.pkl')
                )
            
            # Save scalers
            joblib.dump(
                self.scaler_X, 
                os.path.join(self.config['model_path'], 'scaler_X.pkl')
            )
            joblib.dump(
                self.scaler_y, 
                os.path.join(self.config['model_path'], 'scaler_y.pkl')
            )
            
            return True
        
        except Exception as e:
            print(f"Error saving models: {e}")
            return False
    
    def load_models(self):
        """
        Load all models from disk.
        
        Returns:
            bool: Success status
        """
        try:
            # Load deep model
            self.deep_model = tf.keras.models.load_model(
                os.path.join(self.config['model_path'], 'deep_model.h5')
            )
            
            # Load Prophet models
            with open(os.path.join(self.config['model_path'], 'solar_prophet.pkl'), 'rb') as f:
                self.solar_prophet = joblib.load(f)
            
            with open(os.path.join(self.config['model_path'], 'crop_prophet.pkl'), 'rb') as f:
                self.crop_prophet = joblib.load(f)
            
            # Load XGBoost model
            self.optimization_model = joblib.load(
                os.path.join(self.config['model_path'], 'optimization_model.pkl')
            )
            
            # Load scalers
            self.scaler_X = joblib.load(
                os.path.join(self.config['model_path'], 'scaler_X.pkl')
            )
            self.scaler_y = joblib.load(
                os.path.join(self.config['model_path'], 'scaler_y.pkl')
            )
            
            return True
        
        except Exception as e:
            print(f"Error loading models: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Create optimizer
    optimizer = AgrivoltaicsOptimizer()
    
    # Train all models
    results = optimizer.train_all_models()
    
    # Generate forecasts
    solar_forecast, crop_forecast = optimizer.forecast_production(periods=365)
    
    # Visualize results
    figures = optimizer.visualize_results(
        history=results['training_history'],
        forecasts=(solar_forecast, crop_forecast)
    )
    
    # Sample weather forecast and constraints
    weather_forecast = pd.DataFrame({
        'date': pd.date_range(start='2023-01-01', periods=7),
        'temp_high': [25, 26, 24, 23, 27, 28, 25],
        'temp_low': [15, 16, 14, 13, 17, 18, 15],
        'precipitation': [0, 0, 0.2, 0.5, 0, 0, 0.1],
        'cloud_cover': [0.1, 0.2, 0.8, 0.9, 0.3, 0.1, 0.4],
        'wind_speed': [5, 6, 8, 7, 4, 5, 6]
    })
    
    constraints = {
        'max_panel_height': 4.5,  # meters
        'min_panel_height': 2.5,  # meters
        'field_dimensions': (100, 100),  # meters
        'crop_type': 'lettuce',
        'water_availability': 500  # cubic meters per day
    }
    
    # Get optimized configuration
    optimal_config = optimizer.optimize_configuration(
        weather_forecast=weather_forecast,
        constraints=constraints
    )
    
    print("Optimal Configuration:")
    for key, value in optimal_config.items():
        print(f"{key}: {value}")
    
    # Save models
    optimizer.save_models()