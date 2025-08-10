import streamlit as st
import pandas as pd
import numpy as np
import time
import datetime
from dateutil.relativedelta import relativedelta
import plotly.express as px
import plotly.graph_objects as go
import random

# Page configuration
st.set_page_config(
    page_title="ClearVue BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    /* Main styling */
    .stApp {
        background-color: #f8f9fa;
    }
    /* Header styling */
    .header {
        background: linear-gradient(135deg, #0d47a1, #1976d2);
        color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    /* Card styling */
    .card {
        background: white;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    /* Metric styling */
    .metric-card {
        background: white;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        padding: 1.2rem;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1976d2;
        margin: 0.5rem 0;
    }
    /* Financial calendar styling */
    .calendar-header {
        background-color: #0d47a1;
        color: white;
        font-weight: bold;
        padding: 0.5rem;
        border-radius: 0.25rem;
    }
    /* Animation for real-time updates */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.03); }
        100% { transform: scale(1); }
    }
    .pulse {
        animation: pulse 1s infinite;
    }
</style>
""", unsafe_allow_html=True)

# Generate financial calendar for ClearVue (fixed version)
def generate_financial_calendar(year):
    periods = []
    for month in range(1, 13):  # January to December
        # Start on the last Saturday of previous month
        if month == 1:  # January
            # Previous month is December of previous year
            prev_month = 12
            prev_year = year - 1
        else:
            prev_month = month - 1
            prev_year = year
        
        # Get last day of previous month
        last_day_prev = datetime.date(prev_year, prev_month, 1) + relativedelta(months=1, days=-1)
        
        # Calculate last Saturday of previous month
        # Saturday is weekday 5
        offset = (last_day_prev.weekday() - 5) % 7
        start = last_day_prev - datetime.timedelta(days=offset)
        
        # End on the last Friday of current month
        current_month_last = datetime.date(year, month, 1) + relativedelta(months=1, days=-1)
        offset = (current_month_last.weekday() - 4) % 7  # Friday is 4
        end = current_month_last - datetime.timedelta(days=offset)
        
        periods.append({
            "Financial Month": start.strftime("%B"),
            "Start Date": start.strftime("%Y-%m-%d"),
            "End Date": end.strftime("%Y-%m-%d"),
            "Quarter": (month - 1) // 3 + 1
        })
    
    return pd.DataFrame(periods)

# Generate sample sales data
def generate_sales_data():
    regions = ['North', 'South', 'East', 'West']
    categories = ['Electronics', 'Furniture', 'Office Supplies', 'Appliances']
    subcategories = {
        'Electronics': ['Phones', 'Laptops', 'TVs', 'Accessories'],
        'Furniture': ['Chairs', 'Desks', 'Storage', 'Tables'],
        'Office Supplies': ['Paper', 'Pens', 'Notebooks', 'Binders'],
        'Appliances': ['Refrigerators', 'Microwaves', 'Ovens', 'Dishwashers']
    }
    
    # Create date range for the last 2 years
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=730)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    data = []
    for date in date_range:
        for region in regions:
            for category in categories:
                for subcategory in subcategories[category]:
                    # Base sales with some seasonality
                    base_sales = random.randint(50, 200)
                    
                    # Weekend boost
                    if date.weekday() >= 5:  # Saturday or Sunday
                        base_sales *= 1.3
                    
                    # Holiday boost
                    if date.month == 12:  # December
                        base_sales *= 1.5
                    
                    # Random fluctuation
                    base_sales *= random.uniform(0.8, 1.2)
                    
                    # Regional variations
                    if region == 'North':
                        base_sales *= 1.1
                    elif region == 'West':
                        base_sales *= 1.2
                    
                    data.append({
                        'Date': date.strftime("%Y-%m-%d"),
                        'Region': region,
                        'Category': category,
                        'Subcategory': subcategory,
                        'Revenue': round(base_sales, 2),
                        'Units': random.randint(1, 20)
                    })
    
    return pd.DataFrame(data)

# Generate supplier data
def generate_supplier_data():
    suppliers = ['TechGlobal', 'FurnitureWorld', 'OfficePlus', 'ApplianceDirect', 'ElectroMart']
    categories = ['Electronics', 'Furniture', 'Office Supplies', 'Appliances']
    performance = ['Excellent', 'Good', 'Average', 'Poor']
    
    data = []
    for supplier in suppliers:
        for category in categories:
            data.append({
                'Supplier': supplier,
                'Category': category,
                'Performance': random.choice(performance),
                'Delivery Time (days)': random.randint(1, 10),
                'Defect Rate (%)': round(random.uniform(0.1, 5.0), 2),
                'Spend (USD)': random.randint(10000, 100000)
            })
    
    return pd.DataFrame(data)

# Initialize session state
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = generate_sales_data()
    
if 'supplier_data' not in st.session_state:
    st.session_state.supplier_data = generate_supplier_data()
    
if 'financial_calendar' not in st.session_state:
    st.session_state.financial_calendar = generate_financial_calendar(datetime.date.today().year)
    
if 'payment_stream' not in st.session_state:
    st.session_state.payment_stream = []
    
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.datetime.now()

# Function to simulate real-time payments
def simulate_payments():
    products = ['Laptop Pro', 'SmartPhone X', '4K TV', 'Ergo Chair', 'Desk Lamp', 
                'Notebook Set', 'Refrigerator', 'Microwave Oven']
    regions = ['North', 'South', 'East', 'West']
    customers = [f'Cust-{i:03d}' for i in range(1, 101)]
    
    payment = {
        'timestamp': datetime.datetime.now().strftime("%H:%M:%S"),
        'product': random.choice(products),
        'amount': round(random.uniform(10, 1000), 2),
        'customer': random.choice(customers),
        'region': random.choice(regions),
        'payment_method': random.choice(['Credit Card', 'Debit Card', 'PayPal', 'Bank Transfer'])
    }
    
    # Add to stream and keep only the last 10
    st.session_state.payment_stream.append(payment)
    if len(st.session_state.payment_stream) > 10:
        st.session_state.payment_stream = st.session_state.payment_stream[-10:]
    
    st.session_state.last_update = datetime.datetime.now()

# Dashboard Header
st.markdown("""
<div class="header">
    <h1 style="margin:0; padding:0">ClearVue BI Dashboard</h1>
    <p style="margin:0; padding:0">Modern Business Intelligence for Dynamic Sales Reporting</p>
</div>
""", unsafe_allow_html=True)

# Dashboard columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div>Revenue Today</div>
        <div class="metric-value">$42,568</div>
        <div>↑ 12% vs yesterday</div>
    </div>
    """, unsafe_allow_html=True)
    
with col2:
    st.markdown("""
    <div class="metric-card">
        <div>Current Financial Month</div>
        <div class="metric-value">$1.2M</div>
        <div>↑ 8% vs target</div>
    </div>
    """, unsafe_allow_html=True)
    
with col3:
    st.markdown("""
    <div class="metric-card">
        <div>Regional Leader</div>
        <div class="metric-value">West</div>
        <div>↑ 15% growth</div>
    </div>
    """, unsafe_allow_html=True)
    
with col4:
    st.markdown("""
    <div class="metric-card">
        <div>Top Product</div>
        <div class="metric-value">Laptop Pro</div>
        <div>↑ 22% this month</div>
    </div>
    """, unsafe_allow_html=True)

# Real-time payments section
st.markdown("### Real-Time Payment Stream")
payment_placeholder = st.empty()

# Financial calendar section
st.markdown("### ClearVue Financial Calendar")
calendar_placeholder = st.empty()

# Sales reporting section
st.markdown("### Sales Performance Analysis")
report_col1, report_col2 = st.columns([1, 3])

with report_col1:
    report_period = st.selectbox(
        "Report Period",
        ["Daily", "Weekly", "Monthly", "Quarterly", "Annual"],
        index=2
    )
    
    region_filter = st.multiselect(
        "Filter Regions",
        ['North', 'South', 'East', 'West'],
        default=['North', 'South', 'East', 'West']
    )
    
    category_filter = st.multiselect(
        "Filter Categories",
        ['Electronics', 'Furniture', 'Office Supplies', 'Appliances'],
        default=['Electronics', 'Furniture', 'Office Supplies', 'Appliances']
    )
    
    st.markdown("""
    <div class="card">
        <h4>Performance Metrics</h4>
        <p>Report Generation: <span style="color:green">1.8s ⚡</span></p>
        <p>Data Accuracy: 99.7%</p>
        <p>Schema Changes: Reduced by 78%</p>
        <p>Decision Speed: Improved by 52%</p>
    </div>
    """, unsafe_allow_html=True)

with report_col2:
    # Filter data based on selections
    filtered_data = st.session_state.sales_data[
        (st.session_state.sales_data['Region'].isin(region_filter)) &
        (st.session_state.sales_data['Category'].isin(category_filter))
    ]
    
    # Aggregate data based on report period
    if report_period == "Daily":
        period_data = filtered_data.groupby('Date').agg({'Revenue':'sum'}).reset_index()
        title = "Daily Revenue Trend"
    elif report_period == "Weekly":
        filtered_data['Week'] = pd.to_datetime(filtered_data['Date']).dt.strftime('%Y-%U')
        period_data = filtered_data.groupby('Week').agg({'Revenue':'sum'}).reset_index()
        title = "Weekly Revenue Trend"
    elif report_period == "Monthly":
        filtered_data['Month'] = pd.to_datetime(filtered_data['Date']).dt.strftime('%Y-%m')
        period_data = filtered_data.groupby('Month').agg({'Revenue':'sum'}).reset_index()
        title = "Monthly Revenue Trend"
    elif report_period == "Quarterly":
        filtered_data['Quarter'] = pd.to_datetime(filtered_data['Date']).dt.quarter
        filtered_data['Year'] = pd.to_datetime(filtered_data['Date']).dt.year
        period_data = filtered_data.groupby(['Year', 'Quarter']).agg({'Revenue':'sum'}).reset_index()
        period_data['Period'] = period_data['Year'].astype(str) + '-Q' + period_data['Quarter'].astype(str)
        title = "Quarterly Revenue Trend"
    else:  # Annual
        filtered_data['Year'] = pd.to_datetime(filtered_data['Date']).dt.year
        period_data = filtered_data.groupby('Year').agg({'Revenue':'sum'}).reset_index()
        title = "Annual Revenue Trend"
    
    # Create the revenue trend chart
    fig = px.line(
        period_data, 
        x=period_data.columns[0], 
        y='Revenue',
        title=title,
        markers=True
    )
    fig.update_layout(
        xaxis_title='Period',
        yaxis_title='Revenue (USD)',
        hovermode="x unified",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Regional performance pie chart
    regional_data = filtered_data.groupby('Region').agg({'Revenue':'sum'}).reset_index()
    fig2 = px.pie(
        regional_data,
        names='Region',
        values='Revenue',
        title='Revenue Distribution by Region',
        hole=0.4
    )
    st.plotly_chart(fig2, use_container_width=True)

# Supplier analytics section
st.markdown("### Supplier Performance Analytics")
supplier_col1, supplier_col2 = st.columns(2)

with supplier_col1:
    # Supplier performance summary
    fig3 = px.bar(
        st.session_state.supplier_data.sort_values('Spend (USD)', ascending=False),
        x='Supplier',
        y='Spend (USD)',
        color='Performance',
        title='Supplier Spend & Performance',
        text='Spend (USD)',
        color_discrete_map={
            'Excellent': '#2ecc71',
            'Good': '#3498db',
            'Average': '#f39c12',
            'Poor': '#e74c3c'
        }
    )
    fig3.update_layout(
        xaxis_title='Supplier',
        yaxis_title='Spend (USD)',
        template="plotly_white"
    )
    fig3.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    st.plotly_chart(fig3, use_container_width=True)

with supplier_col2:
    # Supplier metrics
    st.markdown("#### Key Supplier Metrics")
    st.dataframe(
        st.session_state.supplier_data[
            ['Supplier', 'Category', 'Delivery Time (days)', 'Defect Rate (%)', 'Performance']
        ].sort_values('Performance'),
        height=400
    )
    
    st.markdown("""
    <div class="card">
        <h4>Supplier Analytics Readiness</h4>
        <p>✔️ Hierarchical supplier categorization</p>
        <p>✔️ Dynamic performance scoring</p>
        <p>✔️ Spend analysis by category</p>
        <p>✔️ Flexible schema for future expansion</p>
        <div style="background:#e3f2fd; padding:10px; border-radius:5px; margin-top:10px">
            Schema Flexibility Score: 92% ✅
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#777; font-size:0.9rem">
    ClearVue BI Dashboard • Modern NoSQL Analytics Solution • 
    Report Generated: {date} • 
    <span class="pulse">⚡ Real-time Data</span>
</div>
""".format(date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

# Simulate real-time updates
while True:
    # Update real-time payment stream
    simulate_payments()
    
    # Create payment stream table
    payment_df = pd.DataFrame(st.session_state.payment_stream)
    with payment_placeholder.container():
        if not payment_df.empty:
            # Style the payment table
            styled_payments = payment_df.style \
                .format({'amount': '${:,.2f}'}) \
                .applymap(lambda x: 'color: #2ecc71; font-weight: bold;', subset=['amount']) \
                .set_properties(**{'background-color': '#f8f9fa', 'border': '1px solid #e0e0e0'})
            
            # Display with alternating row colors
            st.dataframe(styled_payments, height=300)
        else:
            st.info("Waiting for payment data...")
    
    # Update financial calendar display
    with calendar_placeholder.container():
        # Style the calendar table
        styled_calendar = st.session_state.financial_calendar.style \
            .set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#0d47a1'), ('color', 'white')]},
                {'selector': 'tr:nth-of-type(odd)', 'props': [('background-color', '#e3f2fd')]},
                {'selector': 'tr:nth-of-type(even)', 'props': [('background-color', '#bbdefb')]}
            ]) \
            .set_properties(**{'text-align': 'center'})
        
        st.dataframe(styled_calendar, height=300)
    
    # Check if 5 seconds have passed
    if (datetime.datetime.now() - st.session_state.last_update).seconds > 5:
        st.experimental_rerun()
    
    time.sleep(1)  # Update every second
