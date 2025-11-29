import streamlit as st
import requests
import pandas as pd
import json
import os

# Streamlit App Configuration
st.set_page_config(
    page_title="Sales Forecasting Prediction",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Sales Forecasting Prediction System")
st.markdown("Enter the parameters below to get sales predictions")

# API endpoint
API_URL = "http://localhost:8000/predict"

# Load label encodings
@st.cache_data
def load_encodings():
    try:
        # Try to load from the parent directory first
        if os.path.exists('../label_encodings.csv'):
            encodings = pd.read_csv('../label_encodings.csv')
        elif os.path.exists('label_encodings.csv'):
            encodings = pd.read_csv('label_encodings.csv')
        else:
            st.error("❌ label_encodings.csv file not found. Please make sure it exists.")
            return None
        
        # Create dictionaries for each category
        encoding_dict = {}
        for col in ['family', 'city', 'state', 'type']:
            col_data = encodings[encodings['column'] == col]
            encoding_dict[col] = {
                'original_to_encoded': dict(zip(col_data['original_value'], col_data['encoded_value'])),
                'encoded_to_original': dict(zip(col_data['encoded_value'], col_data['original_value']))
            }
        return encoding_dict
    except Exception as e:
        st.error(f"❌ Error loading encodings: {str(e)}")
        return None

# Load the encodings
encodings = load_encodings()

# Create input form
with st.form("prediction_form"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Store & Item Information")
        store_nbr = st.number_input("Store Number", min_value=0.0, value=1.0)
        item_nbr = st.number_input("Item Number", min_value=0.0, value=1.0)
        unit_sales = st.number_input("Unit Sales", min_value=0.0, value=1.0, step=0.1)
        onpromotion = st.selectbox("On Promotion", [0.0, 1.0], format_func=lambda x: "Yes" if x == 1.0 else "No")
        
    with col2:
        st.subheader("Date Information")
        day = st.number_input("Day", min_value=1, max_value=31, value=1)
        month = st.number_input("Month", min_value=1, max_value=12, value=1)
        dayofweek = st.selectbox("Day of Week", list(range(7)), format_func=lambda x: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][x])
        week = st.number_input("Week", min_value=1, max_value=53, value=1)
        year = st.number_input("Year", min_value=2013, max_value=2025, value=2014)
        
    with col3:
        st.subheader("Location & Category")
        if encodings:
            # Product Family dropdown with original labels
            family_options = list(encodings['family']['original_to_encoded'].keys())
            selected_family = st.selectbox("Product Family", family_options)
            family_encoded = encodings['family']['original_to_encoded'][selected_family]
            
            # City dropdown with original labels
            city_options = list(encodings['city']['original_to_encoded'].keys())
            selected_city = st.selectbox("City", city_options)
            city_encoded = encodings['city']['original_to_encoded'][selected_city]
            
            # State dropdown with original labels
            state_options = list(encodings['state']['original_to_encoded'].keys())
            selected_state = st.selectbox("State", state_options)
            state_encoded = encodings['state']['original_to_encoded'][selected_state]
            
            # Store Type dropdown with original labels
            type_options = list(encodings['type']['original_to_encoded'].keys())
            selected_type = st.selectbox("Store Type", type_options)
            type_encoded = encodings['type']['original_to_encoded'][selected_type]
            
        else:
            # Fallback to numeric inputs if encodings not available
            st.warning("⚠️ Using numeric inputs. Label encodings not available.")
            family_encoded = st.number_input("Product Family (encoded)", min_value=0, value=0, step=1)
            city_encoded = st.number_input("City (encoded)", min_value=0, value=0, step=1)
            state_encoded = st.number_input("State (encoded)", min_value=0, value=0, step=1)
            type_encoded = st.number_input("Store Type (encoded)", min_value=0, value=0, step=1)
        
    col4, col5 = st.columns(2)
    
    with col4:
        st.subheader("Flags")
        is_outlier = st.selectbox("Is Outlier", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
        is_return = st.selectbox("Is Return", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
        
    with col5:
        st.subheader("Special Days")
        holiday = st.selectbox("Holiday", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
        is_weekend = st.selectbox("Is Weekend", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
    
    # Submit button
    submitted = st.form_submit_button("🔮 Predict Sales")

# Handle form submission
if submitted:
    # Prepare data for API call
    prediction_data = {
        "store_nbr": float(store_nbr),
        "item_nbr": float(item_nbr),
        "unit_sales": float(unit_sales),
        "onpromotion": float(onpromotion),
        "day": int(day),
        "month": int(month),
        "dayofweek": int(dayofweek),
        "week": int(week),
        "family_encoded": int(family_encoded),
        "city_encoded": int(city_encoded),
        "state_encoded": int(state_encoded),
        "type_encoded": int(type_encoded),
        "is_outlier": int(is_outlier),
        "is_return": int(is_return),
        "holiday": int(holiday),
        "year": int(year),
        "is_weekend": int(is_weekend)
    }
    
    # Display selected values for confirmation
    if encodings:
        st.info(f"📋 **Selected Values:** Family: {selected_family} ({family_encoded}), City: {selected_city} ({city_encoded}), State: {selected_state} ({state_encoded}), Type: {selected_type} ({type_encoded})")
    
    # Make API call
    with st.spinner("Making prediction..."):
        try:
            response = requests.post(API_URL, json=prediction_data)
            
            if response.status_code == 200:
                result = response.json()
                
                if result["status"] == "success":
                    st.success("✅ Prediction successful!")
                    
                    # Display result in a nice format
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric(
                            label="Predicted Sales",
                            value=f"{result['predicted_sales']:.2f}",
                            delta=None
                        )
                    
                    with col2:
                        st.info(f"Status: {result['status']}")
                        
                else:
                    st.error(f"❌ Prediction failed: {result.get('message', 'Unknown error')}")
                    
            else:
                st.error(f"❌ API request failed with status code: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Could not connect to the API. Make sure the FastAPI server is running on http://localhost:8000")
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

# Sidebar with instructions
st.sidebar.markdown("## 📋 Instructions")
st.sidebar.markdown("""
1. Fill in all the required fields in the form
2. Click **Predict Sales** to get the prediction
3. Make sure the FastAPI server is running

### 🚀 Starting the API Server
```bash
cd Server
uvicorn main_api:app --reload --port 8000
```

### 📊 Running this Streamlit App
```bash
streamlit run ui.py
```
""")


# Display sample data format
with st.expander("📄 Sample Data Format"):
    sample_data = {
        "store_nbr": 1.0,
        "item_nbr": 103665.0,
        "unit_sales": 7.0,
        "onpromotion": 0.0,
        "day": 16,
        "month": 8,
        "dayofweek": 1,
        "week": 33,
        "family_encoded": 13,
        "city_encoded": 5,
        "state_encoded": 11,
        "type_encoded": 0,
        "is_outlier": 0,
        "is_return": 0,
        "holiday": 0,
        "year": 2013,
        "is_weekend": 0
    }
    
    st.json(sample_data)