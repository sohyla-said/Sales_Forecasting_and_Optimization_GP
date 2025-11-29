import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EDA Dashboard", layout="wide")

@st.cache_data  #to cache data for faster reload.
def load_data():
    # Load processed data
    data = pd.read_csv('processed_data.csv')
    data['date'] = pd.to_datetime(data['date'])
    
    # Load label encodings to decode categorical variables
    try:
        encodings = pd.read_csv('label_encodings.csv')
        
        # Create reverse mapping dictionaries
        family_map = dict(zip(encodings[encodings['column'] == 'family']['encoded_value'], 
                             encodings[encodings['column'] == 'family']['original_value']))
        city_map = dict(zip(encodings[encodings['column'] == 'city']['encoded_value'], 
                           encodings[encodings['column'] == 'city']['original_value']))
        state_map = dict(zip(encodings[encodings['column'] == 'state']['encoded_value'], 
                            encodings[encodings['column'] == 'state']['original_value']))
        type_map = dict(zip(encodings[encodings['column'] == 'type']['encoded_value'], 
                           encodings[encodings['column'] == 'type']['original_value']))
        
        # Decode categorical variables back to readable labels
        data['family'] = data['family_encoded'].map(family_map)
        data['city'] = data['city_encoded'].map(city_map)
        data['state'] = data['state_encoded'].map(state_map)
        data['type'] = data['type_encoded'].map(type_map)
        
    except FileNotFoundError:
        st.warning("⚠️ label_encodings.csv not found. Using encoded values.")
        # Use encoded values with readable names
        data['family'] = data['family_encoded']
        data['city'] = data['city_encoded']
        data['state'] = data['state_encoded']
        data['type'] = data['type_encoded']
    
    # Map binary columns to readable labels
    data['onpromotion'] = data['onpromotion'].map({0: 'No', 1: 'Yes'})
    data['holiday'] = data['holiday'].map({0: 'No', 1: 'Yes'})
    data['is_return'] = data['is_return'].map({0: 'No', 1: 'Yes'})
    data['is_weekend'] = data['is_weekend'].map({0: 'No', 1: 'Yes'})
    data['is_outlier'] = data['is_outlier'].map({0: 'No', 1: 'Yes'})
    
    return data

data = load_data()

# Select columns for display (using original and readable columns)
data_shown = data[['date', 'store_nbr', 'item_nbr', 'unit_sales', 'onpromotion', 'family', 'city', 'state', 'type', 'is_return', 'holiday', 'is_weekend', 'is_outlier']]
data_shown = data_shown.rename(columns={
    'store_nbr': 'store_id', 
    'item_nbr': 'item_id', 
    'family': 'item_category', 
    'type': 'store_type', 
    'holiday': 'is_holiday'
})

# Sidebar
st.sidebar.header("🔍 Filters")

# Date range filtering
st.sidebar.markdown("### Filter by date range")
min_date = data_shown['date'].min().date()
max_date = data_shown['date'].max().date()
start_date = st.sidebar.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

# Convert date_input results back to datetime for comparison
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Get categorical columns
categorical_columns = data_shown.select_dtypes(include='object').columns.tolist()
numerical_columns = data_shown.select_dtypes(include='number').columns.tolist()

# Initialize filtered_data with all data
filtered_data = data_shown.copy()

# Apply date filtering
filtered_data = filtered_data[(filtered_data['date'] >= start_date) & (filtered_data['date'] <= end_date)]

# Categorical filters
st.sidebar.markdown("### Filter by categorical variables")
filter_dict = {}

for col in categorical_columns:
    unique_values = filtered_data[col].unique().tolist()
    if col == 'date':
        continue  # Skip date column
    elif col in ['onpromotion', 'is_return', 'is_holiday', 'is_weekend', 'is_outlier']:
        selected_value = st.sidebar.radio(f"{col.replace('_', ' ').title()}", unique_values, index=None, key=col)
        if selected_value:
            filter_dict[col] = [selected_value]
    else:
        selected_value = st.sidebar.multiselect(f"Filter by {col}", unique_values, key=col)
        if selected_value:
            filter_dict[col] = selected_value

# Apply all categorical filters
if filter_dict:
    for col, value in filter_dict.items():
        filtered_data = filtered_data[filtered_data[col].isin(list(value))]

# Display filtered data count
st.sidebar.markdown(f"**Filtered Records:** {len(filtered_data):,} / {len(data_shown):,}")

# Main section
st.title("📊 Sales Forecasting - EDA Dashboard")

# Data overview
st.subheader("💾 Data Overview")
st.markdown("#### First 5 rows of the filtered data")
st.dataframe(filtered_data.head(), use_container_width=True)

# Summary statistics
st.subheader("📊 Summary Statistics")
st.dataframe(filtered_data.describe(), use_container_width=True)

st.markdown("---")

# Sales distribution and categorical analysis
col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 Unit Sales Distribution")
    fig = px.histogram(filtered_data, x='unit_sales', nbins=50, title='Distribution of Unit Sales')
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📊 Categorical Analysis")
    cat_col = st.selectbox("Select categorical column for analysis", categorical_columns)
    if cat_col != 'date':
        cat_counts = filtered_data[cat_col].value_counts().reset_index()
        cat_counts.columns = [cat_col, 'count']
        fig2 = px.bar(cat_counts, x=cat_col, y='count', 
                     title=f"{cat_col.replace('_', ' ').title()} Distribution",
                     color='count', color_continuous_scale='viridis')
        st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# Time series analysis
st.subheader("📆 Sales Trend Over Time")
daily_sales = filtered_data.groupby('date')['unit_sales'].sum().reset_index()
fig3 = px.line(daily_sales, x='date', y='unit_sales', 
               title="Daily Sales Trend",
               labels={'unit_sales': 'Total Unit Sales', 'date': 'Date'})
fig3.update_traces(line=dict(color='blue', width=2))
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# Store & Regional Analysis
st.subheader("🏪 Store & Regional Analysis")

col5, col6 = st.columns(2)

with col5:
    # Total sales by state
    state_sales = filtered_data.groupby('state')['unit_sales'].sum().sort_values(ascending=False).reset_index()
    fig6 = px.bar(state_sales, x='state', y='unit_sales',
                  title='Total Unit Sales by State',
                  labels={'state': 'State', 'unit_sales': 'Total Unit Sales'},
                  color='unit_sales', color_continuous_scale='Blues')
    st.plotly_chart(fig6, use_container_width=True)

with col6:
    # Top 10 cities by sales
    city_sales = filtered_data.groupby('city')['unit_sales'].sum().sort_values(ascending=False).head(10).reset_index()
    fig7 = px.bar(city_sales, x='city', y='unit_sales',
                  title='Top 10 Cities by Total Unit Sales',
                  labels={'city': 'City', 'unit_sales': 'Total Unit Sales'},
                  color='unit_sales', color_continuous_scale='Greens')
    st.plotly_chart(fig7, use_container_width=True)

col7, col8 = st.columns(2)

with col7:
    # Sales by store type
    type_sales = filtered_data.groupby('store_type')['unit_sales'].sum().sort_values(ascending=False).reset_index()
    fig8 = px.bar(type_sales, x='store_type', y='unit_sales',
                  title='Total Unit Sales by Store Type',
                  labels={'store_type': 'Store Type', 'unit_sales': 'Total Unit Sales'},
                  color='store_type')
    st.plotly_chart(fig8, use_container_width=True)

with col8:
    # Top 10 product categories
    category_sales = filtered_data.groupby('item_category')['unit_sales'].sum().sort_values(ascending=False).head(10).reset_index()
    fig9 = px.bar(category_sales, x='item_category', y='unit_sales',
                  title='Top 10 Product Categories by Sales',
                  labels={'item_category': 'Product Category', 'unit_sales': 'Total Unit Sales'},
                  color='unit_sales', color_continuous_scale='Oranges')
    st.plotly_chart(fig9, use_container_width=True)

st.markdown("---")

# Promotion Impact Analysis
st.subheader("🎯 Promotion Impact Analysis")
col3, col4 = st.columns(2)

with col3:
    choice = st.selectbox("Select aggregation method", ['Total Sales', 'Average Sales'])
    
    if choice == 'Average Sales':
        promo_impact = filtered_data.groupby('onpromotion')['unit_sales'].mean().reset_index()
        promo_impact.columns = ['onpromotion', 'avg_unit_sales']
        fig4 = px.bar(promo_impact, x='onpromotion', y='avg_unit_sales',
                      title='Average Unit Sales: Promoted vs Non-Promoted',
                      labels={'onpromotion': 'On Promotion', 'avg_unit_sales': 'Average Unit Sales'},
                      color='onpromotion', color_discrete_map={'Yes': 'orange', 'No': 'lightblue'})
    else:
        promo_impact = filtered_data.groupby('onpromotion')['unit_sales'].sum().reset_index()
        promo_impact.columns = ['onpromotion', 'total_unit_sales']
        fig4 = px.bar(promo_impact, x='onpromotion', y='total_unit_sales',
                      title='Total Sales: Promoted vs Non-Promoted',
                      labels={'onpromotion': 'On Promotion', 'total_unit_sales': 'Total Sales'},
                      color='onpromotion', color_discrete_map={'Yes': 'orange', 'No': 'lightblue'})
    
    st.plotly_chart(fig4, use_container_width=True)

with col4:
    # Promotion distribution pie chart
    promo_total = filtered_data.groupby('onpromotion')['unit_sales'].sum().reset_index()
    fig5 = px.pie(promo_total, values='unit_sales', names='onpromotion',
                  title='Sales Distribution: Promoted vs Non-Promoted',
                  color_discrete_map={'Yes': 'orange', 'No': 'lightblue'},
                  hole=0.4)
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# Holiday & Weekend Analysis
st.subheader("📅 Special Days Impact Analysis")

col9, col10, col11, col12 = st.columns(4)

with col9:
    # Holiday impact
    holiday_sales = filtered_data.groupby('is_holiday')['unit_sales'].sum().reset_index()
    fig10 = px.bar(holiday_sales, x='is_holiday', y='unit_sales',
                   title='Sales by Holiday Status',
                   color='is_holiday',
                   color_discrete_map={'Yes': 'red', 'No': 'lightgreen'})
    st.plotly_chart(fig10, use_container_width=True)

with col10:
    # Holiday distribution
    fig11 = px.pie(holiday_sales, values='unit_sales', names='is_holiday',
                   title='Holiday Sales Distribution',
                   color_discrete_map={'Yes': 'red', 'No': 'lightgreen'})
    st.plotly_chart(fig11, use_container_width=True)

with col11:
    # Weekend impact
    weekend_sales = filtered_data.groupby('is_weekend')['unit_sales'].sum().reset_index()
    fig12 = px.bar(weekend_sales, x='is_weekend', y='unit_sales',
                   title='Sales by Weekend Status',
                   color='is_weekend',
                   color_discrete_map={'Yes': 'purple', 'No': 'lightyellow'})
    st.plotly_chart(fig12, use_container_width=True)

with col12:
    # Weekend distribution
    fig13 = px.pie(weekend_sales, values='unit_sales', names='is_weekend',
                   title='Weekend Sales Distribution',
                   color_discrete_map={'Yes': 'purple', 'No': 'lightyellow'})
    st.plotly_chart(fig13, use_container_width=True)