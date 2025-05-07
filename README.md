# Agrivoltaics Simulation

A full-stack Python simulation for optimizing agrivoltaics systems with ML and AI. This project combines solar energy generation with agricultural land use to maximize both energy production and crop yields.

## Features

- Real-time simulation of agrivoltaic systems
- Machine learning-based optimization
- Weather data integration
- Crop yield prediction
- Solar panel configuration optimization
- Interactive dashboard
- RESTful API backend
- Modern React-based frontend

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- TensorFlow/PyTorch
- Celery for background tasks
- PostgreSQL

### Frontend
- Next.js
- TypeScript
- Tailwind CSS
- React Query

## Setup

### Prerequisites
- Python 3.11+
- Node.js 16+
- PostgreSQL

### Backend Setup
1. Create a virtual environment:
   ```bash
   python -m venv agrivoltaics
   source agrivoltaics/bin/activate  # On Windows: .\agrivoltaics\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the database:
   ```bash
   python create_tables.py
   python loaddata.py  # Load initial data
   ```

4. Create an admin user:
   ```bash
   python create_admin.py
   ```

5. Start the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

[MIT License](LICENSE)
