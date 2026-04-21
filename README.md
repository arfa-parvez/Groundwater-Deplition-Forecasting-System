# AquaGuard AI

*Smart Groundwater Intelligence for Sustainable Future*

AquaGuard AI is an end-to-end Machine Learning web application designed to predict groundwater depletion, provide time-series forecasting, and generate smart actionable rule-based recommendations.

## Project Structure
- `/data`: CSV files and generated mock datasets.
- `/models`: Pickled ML models (Random Forest, XGBoost, LR, Prophet).
- `/api`: FastAPI backend running classification and forecasting endpoints.
- `/frontend`: Streamlit dashboard giving users a sleek, intuitive frontend.
- `/utils`: Data generation, feature engineering, and mock scheduling scripts.
- `/notebooks`: Scripts to initialize generating data and training models.

## Pre-requisites
- Docker
- Docker Compose

## Installation & Setup
1. Clone the repository and navigate to the project root directory.
2. Ensure you have an `.env` file containing your `API_KEY`, `GEMINI_API_KEY`, and `GOOGLE_CLIENT` credentials (use `.env.example` as a template).

## Execution (Production Ready)

### Using Docker Compose (Recommended)
This will set up the entire architecture (FastAPI Backend + Streamlit Frontend) in one command:
```bash
docker-compose up --build -d
```
The Frontend Dashboard will be available at: http://localhost:8501
The Backend API will be available at: http://localhost:8000

---

## Local Development Execution

### Step 1: Generate Data and Train Models
```bash
python notebooks/train_models.py
```
This will create `data/groundwater_data.csv` and populate the `/models` directory with pickled `.pkl` ML files.

### Step 2: Start the FastAPI Backend
Open a terminal in the project root and run:
```bash
uvicorn api.main:app --reload --port 8000
```
*Leave this running.* It provides endpoints for prediction, recommendation, forecast, alerts, and chatbot.

### Step 3: Start the Streamlit Frontend
Open a **new terminal** (with the same python environment) and run:
```bash
streamlit run frontend/app.py
```
This will launch the `AquaGuard AI` Dashboard in your browser.

## Features
- **Animations & Branding**: High contrast clean animated UI.
- **Dynamic Multi-lang**: Supports English, Hindi, and Kannada.
- **Charts & Reports**: Interactive Plotly forecast graphs and 1-click PDF report download.
- **Voice / Chat**: Chatbot assistance interface included.
