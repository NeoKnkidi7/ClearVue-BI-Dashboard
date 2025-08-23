import streamlit as st
import pandas as pd
import numpy as np
import time
import datetime
from dateutil.relativedelta import relativedelta
import plotly.express as px
import plotly.graph_objects as go
import random
import subprocess
import sys

# Install missing packages if needed
try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly"])
    import plotly.express as px
    import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="ClearVue BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling with modern colors and better visibility
st.markdown("""
<style>
    /* Main styling */
    .stApp {
        background-color: #f8f9fc;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Header styling */
    .header {
        background: linear-gradient(135deg, #2c5aa0, #4a7bcc);
        color: white;
        padding: 1.8rem;
        border-radius: 0.8rem;
        box-shadow: 0 6px 12px rgba(0,0,0,0.12);
        margin-bottom: 1.8rem;
    }
    /* Card styling */
    .card {
        background: white;
        border-radius: 0.8rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        padding: 1.8rem;
        margin-bottom: 1.8rem;
        border-left: 4px solid #2c5aa0;
    }
    /* Metric styling */
    .metric-card {
        background: linear-gradient(135deg, #ffffff, #f8f9fc);
        border-radius: 0.8rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        padding: 1.5rem;
        text-align: center;
        border: 1px solid #e0e6ef;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.12);
    }
    .metric-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #4a5568;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #2c5aa0;
        margin: 0.8rem 0;
    }
    .metric-change {
        font-size: 0.9rem;
        font-weight: 500;
    }
    .positive-change {
        color: #38a169;
    }
    /* Financial calendar styling */
    .calendar-header {
        background: linear-gradient(135deg, #2c5aa0, #4a7bcc);
        color: white;
        font-weight: bold;
        padding: 0.8rem;
        border-radius: 0.4rem;
    }
    /* Animation for real-time updates */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.03); }
        100% { transform: scale(1); }
    }
    .pulse {
        animation: pulse 1.5s infinite;
        color: #e53e3e;
        font-weight: bold;
    }
    /* Custom tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #edf2f7;
        border-radius: 8px 8px 0px 0px;
        padding: 12px 24px;
        font-weight: 600;
        color: #4a5568;
        border: 1px solid #e2e8f0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2c5aa0;
        color: white;
        border: 1px solid #2c5aa0;
    }
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #2c5aa0, #4a7bcc);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #234b83, #3b69b3);
        color: white;
    }
    /* Dataframe styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }
    /* Custom select boxes */
    .stSelectbox div div {
        border-radius: 8px;
    }
    /* Custom multiselect */
    .stMultiSelect div div {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Conversion rate USD to ZAR (South African Rand)
USD_TO_ZAR = 18.5

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

# Generate sample sales data (in ZAR)
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
                    # Base sales with some seasonality (in ZAR)
                    base_sales = random.randint(900, 3600)  # Approximately $50-200 converted to ZAR
                    
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

# Generate supplier data (in ZAR)
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
                'Spend (ZAR)': random.randint(185000, 1850000)  # Approximately $10,000-100,000 converted to ZAR
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

# Function to simulate real-time payments (in ZAR)
def simulate_payments():
    products = ['Laptop Pro', 'SmartPhone X', '4K TV', 'Ergo Chair', 'Desk Lamp', 
                'Notebook Set', 'Refrigerator', 'Microwave Oven']
    regions = ['North', 'South', 'East', 'West']
    customers = [f'Cust-{i:03d}' for i in range(1, 101)]
    
    payment = {
        'timestamp': datetime.datetime.now().strftime("%H:%M:%S"),
        'product': random.choice(products),
        'amount': round(random.uniform(180, 18000), 2),  # Approximately $10-1000 converted to ZAR
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
    <h1 style="margin:0; padding:0; font-size:2.5rem;">ClearVue BI Dashboard</h1>
    <p style="margin:0; padding:0; font-size:1.2rem;">Modern Business Intelligence for Dynamic Sales Reporting</p>
</div>
""", unsafe_allow_html=True)

# Create tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Sales Analytics", "Supplier Performance", "Financial Calendar"])

with tab1:
    # Dashboard columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Revenue Today</div>
            <div class="metric-value">R 787,508</div>
            <div class="metric-change positive-change">↑ 12% vs yesterday</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Current Financial Month</div>
            <div class="metric-value">R 22.2M</div>
            <div class="metric-change positive-change">↑ 8% vs target</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Regional Leader</div>
            <div class="metric-value">West</div>
            <div class="metric-change positive-change">↑ 15% growth</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Top Product</div>
            <div class="metric-value">Laptop Pro</div>
            <div class="metric-change positive-change">↑ 22% this month</div>
        </div>
        """, unsafe_allow_html=True)

    # Real-time payments section
    st.markdown("### Real-Time Payment Stream")
    payment_placeholder = st.empty()

    # Performance metrics
    st.markdown("### Performance Overview")
    perf_col1, perf_col2, perf_col3 = st.columns(3)
    
    with perf_col1:
        st.markdown("""
        <div class="card">
            <h4>Data Metrics</h4>
            <p>Report Generation: <span style="color:#38a169; font-weight:600">1.8s ⚡</span></p>
            <p>Data Accuracy: <span style="color:#38a169; font-weight:600">99.7%</span></p>
            <p>Schema Changes: <span style="color:#e53e3e; font-weight:600">Reduced by 78%</span></p>
        </div>
        """, unsafe_allow_html=True)
    
    with perf_col2:
        st.markdown("""
        <div class="card">
            <h4>Business Impact</h4>
            <p>Decision Speed: <span style="color:#38a169; font-weight:600">Improved by 52%</span></p>
            <p>Cost Reduction: <span style="color:#38a169; font-weight:600">23% YoY</span></p>
            <p>Customer Satisfaction: <span style="color:#38a169; font-weight:600">↑ 18%</span></p>
        </div>
        """, unsafe_allow_html=True)
        
    with perf_col3:
        st.markdown("""
        <div class="card">
            <h4>System Health</h4>
            <p>Uptime: <span style="color:#38a169; font-weight:600">99.99%</span></p>
            <p>Data Freshness: <span style="color:#38a169; font-weight:600">< 5min</span></p>
            <p>API Response: <span style="color:#38a169; font-weight:600">120ms avg</span></p>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    # Sales reporting section
    st.markdown("### Sales Performance Analysis")
    report_col1, report_col2 = st.columns([1, 3])

    with report_col1:
        report_period = st.selectbox(
            "Report Period",
            ["Daily", "Weekly", "Monthly", "Quarterly", "Annual"],
            index=2,
            key="report_period"
        )
        
        region_filter = st.multiselect(
            "Filter Regions",
            ['North', 'South', 'East', 'West'],
            default=['North', 'South', 'East', 'West'],
            key="region_filter"
        )
        
        category_filter = st.multiselect(
            "Filter Categories",
            ['Electronics', 'Furniture', 'Office Supplies', 'Appliances'],
            default=['Electronics', 'Furniture', 'Office Supplies', 'Appliances'],
            key="category_filter"
        )
        
        # KPI targets
        st.markdown("""
        <div class="card">
            <h4>Monthly Targets</h4>
            <p>Revenue: R 24.1M / R 27.8M</p>
            <div style="background:#e0e0e0; border-radius:5px; height:10px; margin:5px 0">
                <div style="background:#38a169; width:87%; height:10px; border-radius:5px"></div>
            </div>
            <p>Units: 12.4K / 15K</p>
            <div style="background:#e0e0e0; border-radius:5px; height:10px; margin:5px 0">
                <div style="background:#d69e2e; width:83%; height:10px; border-radius:5px"></div>
            </div>
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
            period_data = filtered_data.groupby('Date').agg({'Revenue':'sum', 'Units':'sum'}).reset_index()
            title = "Daily Revenue Trend"
            x_col = 'Date'
        elif report_period == "Weekly":
            filtered_data['Week'] = pd.to_datetime(filtered_data['Date']).dt.strftime('%Y-%U')
            period_data = filtered_data.groupby('Week').agg({'Revenue':'sum', 'Units':'sum'}).reset_index()
            title = "Weekly Revenue Trend"
            x_col = 'Week'
        elif report_period == "Monthly":
            filtered_data['Month'] = pd.to_datetime(filtered_data['Date']).dt.strftime('%Y-%m')
            period_data = filtered_data.groupby('Month').agg({'Revenue':'sum', 'Units':'sum'}).reset_index()
            title = "Monthly Revenue Trend"
            x_col = 'Month'
        elif report_period == "Quarterly":
            filtered_data['Quarter'] = pd.to_datetime(filtered_data['Date']).dt.quarter
            filtered_data['Year'] = pd.to_datetime(filtered_data['Date']).dt.year
            period_data = filtered_data.groupby(['Year', 'Quarter']).agg({'Revenue':'sum', 'Units':'sum'}).reset_index()
            period_data['Period'] = period_data['Year'].astype(str) + '-Q' + period_data['Quarter'].astype(str)
            title = "Quarterly Revenue Trend"
            x_col = 'Period'
        else:  # Annual
            filtered_data['Year'] = pd.to_datetime(filtered_data['Date']).dt.year
            period_data = filtered_data.groupby('Year').agg({'Revenue':'sum', 'Units':'sum'}).reset_index()
            title = "Annual Revenue Trend"
            x_col = 'Year'
        
        # Create the revenue trend chart
        fig = px.line(
            period_data, 
            x=x_col, 
            y='Revenue',
            title=title,
            markers=True
        )
        fig.update_layout(
            xaxis_title='Period',
            yaxis_title='Revenue (ZAR)',
            hovermode="x unified",
            template="plotly_white",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        fig.update_traces(line=dict(color='#2c5aa0', width=3))
        st.plotly_chart(fig, use_container_width=True)
        
        # Regional performance pie chart
        regional_data = filtered_data.groupby('Region').agg({'Revenue':'sum'}).reset_index()
        fig2 = px.pie(
            regional_data,
            names='Region',
            values='Revenue',
            title='Revenue Distribution by Region',
            hole=0.4,
            color_discrete_sequence=['#2c5aa0', '#4a7bcc', '#6b9ae6', '#8db5ff']
        )
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Category performance
        category_data = filtered_data.groupby('Category').agg({'Revenue':'sum', 'Units':'sum'}).reset_index()
        fig3 = px.bar(
            category_data,
            x='Category',
            y='Revenue',
            title='Revenue by Category',
            color='Category',
            text='Revenue',
            color_discrete_sequence=['#2c5aa0', '#4a7bcc', '#6b9ae6', '#8db5ff']
        )
        fig3.update_traces(texttemplate='R %{text:,.0f}', textposition='outside')
        fig3.update_layout(
            template="plotly_white",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        st.plotly_chart(fig3, use_container_width=True)

with tab3:
    # Supplier analytics section
    st.markdown("### Supplier Performance Analytics")
    supplier_col1, supplier_col2 = st.columns(2)

    with supplier_col1:
        # Supplier performance summary
        fig3 = px.bar(
            st.session_state.supplier_data.sort_values('Spend (ZAR)', ascending=False),
            x='Supplier',
            y='Spend (ZAR)',
            color='Performance',
            title='Supplier Spend & Performance',
            text='Spend (ZAR)',
            color_discrete_map={
                'Excellent': '#38a169',
                'Good': '#d69e2e',
                'Average': '#d69e2e',
                'Poor': '#e53e3e'
            }
        )
        fig3.update_layout(
            xaxis_title='Supplier',
            yaxis_title='Spend (ZAR)',
            template="plotly_white",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        fig3.update_traces(texttemplate='R %{text:,.0f}', textposition='outside')
        st.plotly_chart(fig3, use_container_width=True)
        
        # Delivery time analysis
        fig4 = px.box(
            st.session_state.supplier_data,
            x='Category',
            y='Delivery Time (days)',
            title='Delivery Time by Category',
            color='Category',
            color_discrete_sequence=['#2c5aa0', '#4a7bcc', '#6b9ae6', '#8db5ff']
        )
        fig4.update_layout(
            template="plotly_white",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig4, use_container_width=True)

    with supplier_col2:
        # Supplier metrics
        st.markdown("#### Key Supplier Metrics")
        st.dataframe(
            st.session_state.supplier_data[
                ['Supplier', 'Category', 'Delivery Time (days)', 'Defect Rate (%)', 'Performance']
            ].sort_values('Performance'),
            height=400,
            use_container_width=True
        )
        
        st.markdown("""
        <div class="card">
            <h4>Supplier Analytics Readiness</h4>
            <p>✔️ Hierarchical supplier categorization</p>
            <p>✔️ Dynamic performance scoring</p>
            <p>✔️ Spend analysis by category</p>
            <p>✔️ Flexible schema for future expansion</p>
            <div style="background:#e6fffa; padding:12px; border-radius:8px; margin-top:12px; border-left: 4px solid #38a169;">
                <span style="font-weight:600; color:#234e52;">Schema Flexibility Score: 92% ✅</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Defect rate analysis
        defect_data = st.session_state.supplier_data.groupby('Category')['Defect Rate (%)'].mean().reset_index()
        fig5 = px.bar(
            defect_data,
            x='Category',
            y='Defect Rate (%)',
            title='Average Defect Rate by Category',
            color='Category',
            text='Defect Rate (%)',
            color_discrete_sequence=['#2c5aa0', '#4a7bcc', '#6b9ae6', '#8db5ff']
        )
        fig5.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig5.update_layout(
            template="plotly_white", 
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig5, use_container_width=True)

with tab4:
    # Financial calendar section
    st.markdown("### ClearVue Financial Calendar")
    calendar_placeholder = st.empty()
    
    # Financial metrics
    st.markdown("### Financial Performance")
    finance_col1, finance_col2, finance_col3 = st.columns(3)
    
    with finance_col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Q3 Revenue</div>
            <div class="metric-value">R 70.3M</div>
            <div class="metric-change positive-change">↑ 12% vs target</div>
        </div>
        """, unsafe_allow_html=True)
    
    with finance_col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Operating Margin</div>
            <div class="metric-value">24.5%</div>
            <div class="metric-change positive-change">↑ 3.2% YoY</div>
        </div>
        """, unsafe_allow_html=True)
        
    with finance_col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Cash Flow</div>
            <div class="metric-value">R 22.2M</div>
            <div class="metric-change positive-change">↑ 18% vs Q2</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Year selection for financial calendar
    selected_year = st.selectbox(
        "Select Financial Year",
        [2023, 2024, 2025],
        index=1,
        key="year_selector"
    )
    
    # Generate calendar for selected year
    if 'financial_calendar' not in st.session_state or st.session_state.financial_calendar.iloc[0]['Start Date'][:4] != str(selected_year):
        st.session_state.financial_calendar = generate_financial_calendar(selected_year)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#718096; font-size:0.9rem; padding:1.5rem;">
    ClearVue BI Dashboard • Modern NoSQL Analytics Solution • 
    Report Generated: {date} • 
    <span class="pulse">⚡ Real-time Data</span>
</div>
""".format(date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

# Simulate real-time updates
if st.button('Refresh Data', key='refresh_button'):
    st.session_state.sales_data = generate_sales_data()
    st.session_state.supplier_data = generate_supplier_data()
    st.rerun()

# Update real-time components
if (datetime.datetime.now() - st.session_state.last_update).seconds > 5:
    simulate_payments()
    
    # Create payment stream table
    payment_df = pd.DataFrame(st.session_state.payment_stream)
    with payment_placeholder.container():
        if not payment_df.empty:
            # Style the payment table
            styled_payments = payment_df.style \
                .format({'amount': 'R {:,.2f}'}) \
                .applymap(lambda x: 'color: #38a169; font-weight: bold;', subset=['amount']) \
                .set_properties(**{'background-color': '#f8f9fc', 'border': '1px solid #e0e6ef'}) \
                .set_table_styles([
                    {'selector': 'th', 'props': [('background-color', '#2c5aa0'), ('color', 'white')]},
                    {'selector': 'tr:nth-of-type(odd)', 'props': [('background-color', '#edf2f7')]},
                    {'selector': 'tr:nth-of-type(even)', 'props': [('background-color', '#f8f9fc')]}
                ])
            
            # Display with alternating row colors
            st.dataframe(styled_payments, height=300, use_container_width=True)
        else:
            st.info("Waiting for payment data...")
    
    # Update financial calendar display
    with calendar_placeholder.container():
        # Style the calendar table
        styled_calendar = st.session_state.financial_calendar.style \
            .set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#2c5aa0'), ('color', 'white')]},
                {'selector': 'tr:nth-of-type(odd)', 'props': [('background-color', '#edf2f7')]},
                {'selector': 'tr:nth-of-type(even)', 'props': [('background-color', '#f8f9fc')]}
            ]) \
            .set_properties(**{'text-align': 'center'})
        
        st.dataframe(styled_calendar, height=300, use_container_width=True)
    
    st.session_state.last_update = datetime.datetime.now()
