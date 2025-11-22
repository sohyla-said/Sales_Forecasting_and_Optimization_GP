import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EDA Dashboard", layout="wide")

@st.cache_data  #to cache data for faster reload.
def load_data():
    data = pd.read_csv('processed_data.csv')
    data['date'] = pd.to_datetime(data['date'])  # Convert to datetime
    data['is_return'] = data['is_return'].map({0:'No', 1:"Yes"})
    data['is_weekend'] = data['is_weekend'].map({0:"No", 1:"Yes"})
    return data

data = load_data()
data_shown = data[['date', 'store_nbr', 'item_nbr', 'unit_sales', 'onpromotion', 'family', 'city', 'state', 'type', 'is_return', 'holiday', 'is_weekend']]
data_shown = data_shown.rename(columns={'store_nbr':'store_id', 'item_nbr':'item_id', 'family':'item_category', 'type':'store_type', 'holiday':'is_holiday'})

# Sidebar
st.sidebar.header("🔍 Filters")

# Date range filtering
st.sidebar.markdown("### Filter by date range")
min_date = data_shown['date'].min().date()  # Convert to date object
max_date = data_shown['date'].max().date()  # Convert to date object
start_date = st.sidebar.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

# Convert date_input results back to datetime for comparison
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# get categorical columns
categorical_columns = data_shown.select_dtypes(include='object').columns.tolist()
numerical_columns = data_shown.select_dtypes(include='number').columns.to_list()


# Initialize filtered_data with all data
filtered_data = data_shown.copy()

# apply date filtering
filtered_data = filtered_data[(filtered_data['date'] >= start_date) & (filtered_data['date'] <= end_date)]

# Categorical filters
# Allow filtering by multiple categorical columns
st.sidebar.markdown("### Filter by categorical variables")
filter_dict = {}

for col in categorical_columns:
    unique_values = data_shown[col].unique().tolist()
    if col == 'date':
        continue  # Skip date column
    elif col == 'onpromotion':
        selected_value = st.sidebar.radio("On promotion", unique_values, index=None)
        if selected_value:
            filter_dict[col] = [selected_value] 
    elif col == 'is_return':
        selected_value = st.sidebar.radio("Is return", unique_values, index=None)
        if selected_value:
            filter_dict[col] = [selected_value]  
    elif col == 'is_holiday':
        selected_value = st.sidebar.radio("Is holiday", unique_values, index=None)
        if selected_value:
            filter_dict[col] = [selected_value]
    elif col == 'is_weekend':
        selected_value = st.sidebar.radio("Is weekend", unique_values, index=None)
        if selected_value:
            filter_dict[col] = [selected_value]  
    else:
        selected_value = st.sidebar.multiselect(f"Filter by {col}", unique_values, key=col)
        if selected_value:
            filter_dict[col] = selected_value


# apply all categorical filters
if filter_dict:
    for col, value in filter_dict.items():
        filtered_data = filtered_data[filtered_data[col].isin(list(value))]

# Display filtered data count
st.sidebar.markdown(f"**Filtered Records:** {len(filtered_data):,} / {len(data_shown):,}")

# Main section
# dataframe head
st.subheader("💾 Data")
st.markdown("#### First 5 rows of the data")
st.dataframe(filtered_data.head())

# Summary table
st.subheader("📊 Summary Statistics")
st.dataframe(filtered_data.describe())


st.markdown("---")
col1, col2 = st.columns(2)
# Unit sales distribution --> histogram
with col1:
    st.subheader("💰 Unit_sales distribution")
    fig = px.histogram(filtered_data, x='unit_sales', nbins=100, title='Distribution of unit_sales')
    st.plotly_chart(fig, use_container_width=True)

# categorical columns --> bar charts
with col2:
    st.subheader("📊 Categorical variables")
    cat_col = st.selectbox("Select categorical column for bar chart", categorical_columns)
    cat_counts = filtered_data[cat_col].value_counts().reset_index()
    cat_counts.columns = [cat_col, 'count']  # Rename columns explicitly
    fig2 = px.bar(cat_counts,
                 x=cat_col, y='count',
                 labels={cat_col:cat_col, 'count':'Count'},
                 title=f"{cat_col} Bar chart")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
# Time series analysis
st.subheader("📆 Time Series (Sales Over Time)")
daily_sales = filtered_data.groupby(by='date')['unit_sales'].sum().reset_index()
fig3 = px.line(daily_sales, x='date', y='unit_sales', title="Sales Trend Over Time")
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
# Store & Regional Analysis
st.subheader("🏪 Store & Regional Analysis")

col5, col6 = st.columns(2)

with col5:
    # Total sales by state
    state_sales = filtered_data.groupby('state')['unit_sales'].sum().sort_values(ascending=False).reset_index()
    fig6 = px.bar(state_sales, 
                  x='state', 
                  y='unit_sales',
                  title='Total Unit Sales by State',
                  labels={'state': 'State', 'unit_sales': 'Total Unit Sales'},
                  color='unit_sales',
                  color_continuous_scale='Blues')
    # fig6.update_xaxis(tickangle=45)
    st.plotly_chart(fig6, use_container_width=True)

with col6:
    # Total sales by city (top 10)
    city_sales = filtered_data.groupby('city')['unit_sales'].sum().sort_values(ascending=False).head(10).reset_index()
    fig7 = px.bar(city_sales, 
                  x='city', 
                  y='unit_sales',
                  title='Top 10 Cities by Total Unit Sales',
                  labels={'city': 'City', 'unit_sales': 'Total Unit Sales'},
                  color='unit_sales',
                  color_continuous_scale='Greens')
    # fig7.update_xaxis(tickangle=45)
    st.plotly_chart(fig7, use_container_width=True)

col7, col8 = st.columns(2)
with col7:
    # Total sales by store type
    type_sales = filtered_data.groupby('store_type')['unit_sales'].sum().sort_values(ascending=False).reset_index()
    fig8 = px.bar(type_sales, 
                  x='store_type', 
                  y='unit_sales',
                  title='Total Unit Sales by Store Type',
                  labels={'store_type': 'Store Type', 'unit_sales': 'Total Unit Sales'},
                  color='store_type',
                  text='unit_sales')
    fig8.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    st.plotly_chart(fig8, use_container_width=True)

with col8:
    # Total sales by item category (top 10)
    category_sales = filtered_data.groupby('item_category')['unit_sales'].sum().sort_values(ascending=False).head(10).reset_index()
    fig9 = px.bar(category_sales, 
                  x='item_category', 
                  y='unit_sales',
                  title='Top 10 Product Categories by Total Unit Sales',
                  labels={'item_category': 'Product Category', 'unit_sales': 'Total Unit Sales'},
                  color='unit_sales',
                  color_continuous_scale='Oranges')
    # fig9.update_xaxis(tickangle=45)
    st.plotly_chart(fig9, use_container_width=True)

st.markdown("---")
# Promotion impact 
col3, col4 = st.columns(2)
with col3:
    st.subheader("🎯 Promotion Impact on Sales")
    choice = st.selectbox("Select sales aggregate", ['Total', 'Average'])
    if choice == 'Average':
        promo_impact = filtered_data.groupby('onpromotion')['unit_sales'].mean().reset_index()
        promo_impact.columns = ['onpromotion', 'avg_unit_sales']
        fig4 = px.bar(promo_impact, 
                  x='onpromotion', 
                  y='avg_unit_sales',
                  title='Average Unit Sales: Promoted vs Non-Promoted',
                  labels={'onpromotion': 'On Promotion', 'avg_unit_sales': 'Average Unit Sales'},
                  color='onpromotion',
                  text='avg_unit_sales')
        # fig4.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        st.plotly_chart(fig4, use_container_width=True)
    else:
        promo_impact = filtered_data.groupby('onpromotion')['unit_sales'].sum().reset_index()
        promo_impact.columns = ['onpromotion', 'total_unit_sales']
        fig4 = px.bar(promo_impact, 
                  x='onpromotion', 
                  y='total_unit_sales',
                  title='Total Sales: Promoted vs Non-Promoted',
                  labels={'onpromotion': 'On Promotion', 'total_unit_sales': 'Total Sales'},
                  color='onpromotion',
                  text='total_unit_sales')
        # fig4.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        st.plotly_chart(fig4, use_container_width=True)
with col4:
    # Total sales by promotion status
    promo_total = filtered_data.groupby('onpromotion')['unit_sales'].sum().reset_index()
    promo_total.columns = ['onpromotion', 'total_unit_sales']
    fig5 = px.pie(promo_total, 
                  values='total_unit_sales', 
                  names='onpromotion',
                  title='Total Sales Distribution: Promoted vs Non-Promoted',
                  hole=0.3)
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")
# Holiday vs Weekday Sales Analysis
st.subheader("🎉 Holiday vs Weekday Sales Analysis")

col9, col10 = st.columns(2)

with col9:
    # Average sales: Holiday vs Weekday
    holiday_avg = filtered_data.groupby('is_holiday')['unit_sales'].sum().reset_index()
    holiday_avg.columns = ['is_holiday', 'total_unit_sales']
    fig10 = px.bar(holiday_avg, 
                   x='is_holiday', 
                   y='total_unit_sales',
                   title='Total Sales: Holiday vs Weekday',
                   labels={'is_holiday': 'Holiday Status', 'total_unit_sales': 'Total Sales'},
                   color='is_holiday',
                   text='total_unit_sales')
    fig10.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    st.plotly_chart(fig10, use_container_width=True)

with col10:
    # Total sales distribution: Holiday vs Weekday (Pie chart)
    holiday_total = filtered_data.groupby('is_holiday')['unit_sales'].sum().reset_index()
    holiday_total.columns = ['is_holiday', 'total_unit_sales']
    fig11 = px.pie(holiday_total, 
                   values='total_unit_sales', 
                   names='is_holiday',
                   title='Total Sales Distribution: Holiday vs Weekday',
                   hole=0.3)
    st.plotly_chart(fig11, use_container_width=True)

st.markdown("---")
# Weekend vs Weekday Sales Analysis
st.subheader("📅 Weekend vs Weekday Sales Analysis")

col11, col12 = st.columns(2)

with col11:
    # Average sales: Weekend vs Weekday
    weekend_avg = filtered_data.groupby('is_weekend')['unit_sales'].sum().reset_index()
    weekend_avg.columns = ['is_weekend', 'total_unit_sales']
    weekend_avg['is_weekend'] = weekend_avg['is_weekend'].map({"No": 'Weekday', "Yes": 'Weekend'})
    fig12 = px.bar(weekend_avg, 
                   x='is_weekend', 
                   y='total_unit_sales',
                   title='Total Sales: Weekend vs Weekday',
                   labels={'is_weekend': 'Day Type', 'total_unit_sales': 'Total Sales'},
                   color='is_weekend',
                   text='total_unit_sales')
    fig12.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    st.plotly_chart(fig12, use_container_width=True)

with col12:
    # Total sales distribution: Weekend vs Weekday (Pie chart)
    weekend_total = filtered_data.groupby('is_weekend')['unit_sales'].sum().reset_index()
    weekend_total.columns = ['is_weekend', 'total_unit_sales']
    weekend_total['is_weekend'] = weekend_total['is_weekend'].map({"No": 'Weekday', "Yes": 'Weekend'})
    fig13 = px.pie(weekend_total, 
                   values='total_unit_sales', 
                   names='is_weekend',
                   title='Total Sales Distribution: Weekend vs Weekday',
                   hole=0.3)
    st.plotly_chart(fig13, use_container_width=True)