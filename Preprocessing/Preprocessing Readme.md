# ⚙️ Preprocessing Overview

Below is the full preprocessing pipeline used to prepare data for modeling.

---

## 1. Data Loading & Cleaning
- Load raw dataset.
- Convert **date** to datetime.
- Confirm **no missing** or **duplicate** values.

---

## 2. Target Transformation
- Apply `log1p` to `unit_sales`.
- Creates new feature: **`unit_sales_log`**.

---

## 3. Categorical Encoding
Label-encode:
- `family`
- `city`
- `state`
- `type`

All encoded via `LabelEncoder`.

---

## 4. Outlier Detection
- Use **IQR** to detect extreme values.
- Create feature:
  - `is_outlier`

Outliers **not removed**, only flagged.

---

## 5. Returns Flagging
- Negative sales → returns.
- Add binary column:
  - `is_return`

---

## 6. Temporal Feature Engineering
From the date column:
- `day_of_week`
- `is_weekend`
- `is_holiday`
- `year`
- `month`
- `day`

---

## 7. Lag Features (Time-Series)
Create:
- `lag_7`
- `lag_14`
- `lag_30`

Lagged missing values handled by median filling or dropping.

---

## 8. Promotion & Holiday Processing
- Convert promo/holiday labels to readable text.
- Then map them into numeric values.

---

## 9. Numerical Scaling
- Use **MinMaxScaler** for:
  - unit_sales
  - other continuous variables

Scaling ensures consistent feature ranges.

---

## 10. Final Cleanup
- Drop unneeded columns.
- Reorder columns for clarity.
- Prepare modeling dataset.

---

## 11. Export Processed Dataset
Final dataset saved as:

