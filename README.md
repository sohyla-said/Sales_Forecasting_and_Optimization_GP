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

## 📂 Project Structure

- `train_sample.csv` – Raw sales data.
- `processed_data.csv` – Preprocessed dataset ready for modeling.
- `EDA.ipynb` – Exploratory Data Analysis.
- `preprocessing.ipynb` – Data cleaning & feature engineering.
- `model.ipynb` – Model training, evaluation, and comparison.

---

## 🔧 Requirements

```bash
pandas
numpy
matplotlib
seaborn
scikit-learn
xgboost
lightgbm
tensorflow
