# Sales_Forecasting_and_Optimization_GP

Predict future sales for a retail or e-commerce business using historical sales data from Corporación Favorita. This project includes data exploration, preprocessing, feature engineering, and predictive modeling with XGBoost, LightGBM, and LSTM.

**Dataset:** [HuggingFace Link](https://huggingface.co/datasets/labelHugg23/CORPORATION_FAVORITA_Sales_Forecasting_Data)

---

## 📊 Data Exploration

### Key Insights
- Dataset is **clean**: no missing values or duplicates.
- **Seasonality**: weekly and daily patterns exist.
- **Promotions** significantly impact sales, but effects vary by product family.
- **Returns** exist and are more frequent in store type `[D]` and promotional items.
- **Outliers** correspond to real events (promotions, holidays) and are flagged for modeling.

### Time Patterns
- Higher sales on **weekends**.
- Weekly and monthly aggregations reveal trends and seasonal patterns.

### Store & Regional Analysis
- Sales concentrated in certain **states** (e.g., Pichincha) and **store types**.
- Top product families vary by region, indicating **localized preferences**.

---

## ⚙️ Preprocessing Pipeline

1. **Load & Clean Data**: Convert date column, confirm no missing values or duplicates.
2. **Target Transformation**: Apply `log1p` to `unit_sales` → `unit_sales_log`.
3. **Categorical Encoding**: Label encode `family`, `city`, `state`, `type`.
4. **Outlier Detection**: Flag outliers using IQR (`is_outlier`), retain in dataset.
5. **Returns Flagging**: Create `is_return` for negative sales.
6. **Temporal Features**: `day_of_week`, `is_weekend`, `is_holiday`, `year`, `month`, `day`.
7. **Lag Features**: `lag_7`, `lag_14`, `lag_30` to capture time-series dependencies.
8. **Promotion & Holiday Processing**: Map to numeric values.
9. **Scaling**: Normalize numeric features using `MinMaxScaler`.
10. **Final Cleanup**: Drop unnecessary columns and export as `processed_data.csv`.

---

## 🧠 Modeling

### Models Implemented
- **XGBoost**
- **LightGBM**
- **LSTM** (with look-back period = 7 days)

### Performance Comparison (on `unit_sales_log`)

| Model     | RMSE      | MAE        | R2 Score  |
|-----------|-----------|------------|-----------|
| XGBoost   | 0.007564  | 0.000886   | 0.999931  |
| LightGBM  | 0.005539  | 0.000621   | 0.999963  |
| LSTM      | 0.831718  | 0.665538   | 0.060532  |

> **Insight:** LightGBM is the best-performing model with the lowest errors and highest R2.

---
## 🔧 FastAPI Backend (`Server/main_api.py`)
- **Purpose**: Serves machine learning model predictions via REST API
- **Model**: Uses MLflow to load pre-trained forecasting models
- **Endpoint**: `/predict` - accepts sales parameters and returns predictions
- **Features**:
  - Model loading and validation
  - Input data validation with Pydantic
  - Error handling and status responses
  - Interactive API documentation

---
## 🖥️ Streamlit Frontend (`UI/ui.py`)
- **Purpose**: User-friendly web interface for making sales predictions
- **Features**:
  - Interactive form with dropdown menus for categorical variables
  - Label encoding integration (displays human-readable labels)
  - Real-time API communication
  - Input validation and error handling

---
## 📂 Project Structure

- `train_sample.csv` – Raw sales data.
- `processed_data.csv` – Preprocessed dataset ready for modeling.
- `EDA.ipynb` – Exploratory Data Analysis.
- `preprocessing.ipynb` – Data cleaning & feature engineering.
- `model.ipynb` – Model training, evaluation, and comparison.

---

## 🔧 Requirements

```bash
# Data Analysis & Processing
pandas>=1.5.0
numpy>=1.23.0
matplotlib>=3.6.0
seaborn>=0.12.0
scikit-learn>=1.1.0

# Machine Learning Models
xgboost>=1.6.0
lightgbm>=3.3.0
tensorflow>=2.10.0

# Model Management & Deployment
mlflow>=2.0.0

# API & Web Interface
fastapi>=0.85.0
uvicorn>=0.18.0
streamlit>=1.15.0
requests>=2.28.0
pydantic>=1.10.0

# Visualization & Dashboard
plotly>=5.11.0

# Jupyter Environment
jupyter>=1.0.0
ipykernel>=6.16.0
```

### Installation
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install individually
pip install pandas numpy matplotlib seaborn scikit-learn
pip install xgboost lightgbm tensorflow
pip install mlflow fastapi uvicorn streamlit requests pydantic plotly
pip install jupyter ipykernel
```
---
## 🏃‍♂️ How to Run Each Part

### 1. 📊 Data Analysis & Preprocessing

#### Step 1: Exploratory Data Analysis
```bash
# Open Jupyter notebook
jupyter notebook

# Or use Jupyter Lab
jupyter lab

# Run EDA.ipynb to explore the dataset
# - Data quality checks
# - Sales trends & seasonality
# - Promotion impact analysis
# - Store & regional analysis
```

#### Step 2: Data Preprocessing
```bash
# Run preprocessing.ipynb to clean and engineer features
# This will generate:
# - processed_data.csv (cleaned dataset)
# - label_encodings.csv (category mappings)
```

#### Step 3: Model Training & Evaluation
```bash
# Run model.ipynb to train and compare models
# Models trained: XGBoost, LightGBM, LSTM
# Best model is saved using MLflow
```

### 2. 📈 Interactive Dashboard

```bash
# Run the EDA dashboard
streamlit run ".\Data Exploration\dashboard.py"

# Features:
# - Interactive filtering by date, category, promotion
# - Real-time visualizations
# - Sales trends and patterns
# Access at: http://localhost:8501
```

### 3. 🚀 Model Deployment & API

#### Step 1: Start FastAPI Server
```bash
# Navigate to Server directory
cd Server

# Start the API server
uvicorn main_api:app --reload --port 8000

# Expected output:
# ✅ Model loaded successfully!
# INFO: Uvicorn running on http://127.0.0.1:8000

# Test API documentation at: http://127.0.0.1:8000/docs
```

#### Step 2: Launch Web Interface
```bash
# In a new terminal, navigate to UI directory
cd UI

# Start the Streamlit prediction interface
streamlit run ui.py

# Features:
# - User-friendly prediction form
# - Dropdown menus with readable labels
# - Real-time API communication
# Access at: http://localhost:8501
```
