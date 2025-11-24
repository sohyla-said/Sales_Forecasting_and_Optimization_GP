# ML Model & Experiment Management Guide

---

## 📁 Location & Purpose

This README is located in the `ML model/` folder. It provides a comprehensive guide for team members to:
- Set up the environment
- Track experiments with **MLflow**
- Version datasets with **DVC**
- Collaborate efficiently
- Prepare deliverables for deployment (Member B)

---

## 🗂️ Project Structure

```
SALES_FORECASTING_AND_OPTIMIZATION/
│
├── .dvc/                  # DVC config & tracking files
├── Data Exploration/      # Data analysis notebooks
├── exported_model/        # Exported trained models (after MLflow export)
├── ML model/
│   ├── Model.ipynb        # Model training notebook
│   └── Model Readme.md    # This guide
├── mlflow_experiments/
│   └── mlruns/            # MLflow experiment runs & artifacts
├── Preprocessing/
│   └── preprocessing.ipynb
├── processed_data.csv     # Final processed dataset
├── processed_data.csv.dvc # DVC tracking for processed data
├── .dvcignore
├── .gitignore
├── README.md              # Project overview
└── Notes
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/sohyla-said/Sales_Forecasting_and_Optimization_GP.git

cd Sales_Forecasting_and_Optimization_GP
```

### 2. Install Dependencies

```bash
pip install lightgbm xgboost tensorflow mlflow dvc cloudpickle
```

### 3. Dataset Versioning with DVC

- DVC tracks `processed_data.csv` via `processed_data.csv.dvc`.


### 4. MLflow Experiment Tracking

- MLflow runs are stored in `mlflow_experiments/mlruns/`.
- To view experiment history and model metrics:

```bash
mlflow ui --backend-store-uri mlflow_experiments/mlruns
```
- Open [http://localhost:5000](http://localhost:5000) in your browser.

**📸 MLflow UI Example:**  
*(i added some mlflow ui screenshots to demonstrate in folder: `MLFlow UI Screens`)*

---

## 🛠️ Model Export & Deliverables for Member B

After training, export the best model for deployment:

```python
import os
import mlflow

run_id = "ba8b863e1d91401aa0d56de754985c43"  # Update as needed
model_uri = f"runs:/{run_id}/model"
project_root = r"D:\IBM Data Scienctist DEPI\Sales_Forecasting_and_Optimization_GP"
dst_path = os.path.join(project_root, "exported_model")

mlflow.artifacts.download_artifacts(
        artifact_uri=model_uri,
        dst_path=dst_path
)
print(f"Model exported to {dst_path}")
```

**Deliverables for Member B:**
- `exported_model/model.pkl` (trained model)


---

## 👨‍💻 How Member B Loads Model & Preprocessing for Prediction

```python
import pickle
import pandas as pd

# Load preprocessing pipeline
with open('Preprocessing/preprocessing.pkl', 'rb') as f:
        preprocessor = pickle.load(f)

# Load trained LightGBM model
with open('exported_model/model_lightgbm.pkl', 'rb') as f:
        model = pickle.load(f)

# Example: Predict on new data
new_data = pd.read_csv('new_data.csv')
X_processed = preprocessor.transform(new_data)
predictions = model.predict(X_processed)
```

*This code can be used in the FastAPI backend for batch or real-time predictions.*

---

## 🧑‍🤝‍🧑 Collaboration Guidelines

- **dependencies:** Ensure all dependencies are installed.
- **Data:** Use the provided `processed_data.csv` or request from Member A.
- **Experiments:** Use MLflow UI to review runs and metrics.
- **Artifacts:** Use exported model and preprocessing files for deployment.
- **DVC:** DVC tracks data locally; remote storage is not configured. Data files are available in the repo.

