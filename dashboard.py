import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# Setting seaborn theme
sns.set(style="darkgrid")

# Load and preprocess data
df = pd.read_csv("main_data.csv", parse_dates=[
    "shipping_limit_date", "order_purchase_timestamp",
    "order_approved_at", "order_delivered_carrier_date",
    "order_delivered_customer_date", "order_estimated_delivery_date"
])

# Filter data based on sidebar date selection
min_date = df["order_purchase_timestamp"].min()
max_date = df["order_purchase_timestamp"].max()

# Sidebar for date filter
with st.sidebar:
    st.image("https://seeklogo.com/images/E/e-commerce-logo-B0AE7EE720-seeklogo.com.png")
    start_date, end_date = st.date_input("Rentang Waktu", [min_date, max_date], min_value=min_date, max_value=max_date)

filtered_df = df[(df["order_purchase_timestamp"] >= pd.to_datetime(start_date)) & 
                 (df["order_purchase_timestamp"] <= pd.to_datetime(end_date))]

# Summary metrics
st.header('E-commerce Dashboard')
col1, col2, col3 = st.columns(3)

with col1:
    total_orders = filtered_df['order_id'].nunique()
    st.metric("Total Orders", total_orders)

with col2:
    total_revenue = format_currency(filtered_df['payment_value'].sum(), "USD", locale="en_US")
    st.metric("Total Revenue", total_revenue)

with col3:
    avg_freight = format_currency(filtered_df['freight_value'].mean(), "USD", locale="en_US")
    st.metric("Average Freight Cost", avg_freight)

# Plotting order trends
st.subheader("Order Trends Over Time")
daily_orders = filtered_df.resample('D', on='order_purchase_timestamp')['order_id'].nunique()
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(daily_orders.index, daily_orders.values, color="#4c72b0", marker="o")
ax.set_title("Daily Orders", fontsize=16)
ax.set_xlabel("Date", fontsize=12)
ax.set_ylabel("Order Count", fontsize=12)
st.pyplot(fig)

# Payment type distribution
st.subheader("Payment Distribution")
col1, col2 = st.columns(2)

with col1:
    payment_counts = filtered_df['payment_type'].value_counts()
    fig, ax = plt.subplots()
    payment_counts.plot(kind='pie', autopct='%1.1f%%', startangle=140, colors=sns.color_palette("muted"))
    ax.set_ylabel('')
    ax.set_title('Payment Types')
    st.pyplot(fig)

with col2:
    installments = filtered_df['payment_installments'].value_counts().sort_index()
    fig, ax = plt.subplots()
    sns.barplot(x=installments.index, y=installments.values, ax=ax, palette="muted")
    ax.set_title("Installment Distribution")
    ax.set_xlabel("Installment Count")
    ax.set_ylabel("Number of Orders")
    st.pyplot(fig)

# Top and Bottom Products
st.subheader("Product Performance")
top_products = filtered_df.groupby("product_id")['order_item_id'].count().nlargest(5)
bottom_products = filtered_df.groupby("product_id")['order_item_id'].count().nsmallest(5)

fig, ax = plt.subplots(1, 2, figsize=(14, 6))
sns.barplot(x=top_products.values, y=top_products.index, ax=ax[0], palette="viridis")
ax[0].set_title("Top 5 Best Selling Products")
sns.barplot(x=bottom_products.values, y=bottom_products.index, ax=ax[1], palette="magma")
ax[1].set_title("Top 5 Worst Selling Products")
st.pyplot(fig)

# Customer demographics by location
st.subheader("Customer Demographics by Location")
col1, col2 = st.columns(2)

with col1:
    city_counts = filtered_df['customer_city'].value_counts().head(10)
    fig, ax = plt.subplots()
    sns.barplot(x=city_counts.values, y=city_counts.index, palette="Blues_d", ax=ax)
    ax.set_title("Top 10 Customer Cities")
    st.pyplot(fig)

with col2:
    state_counts = filtered_df['customer_state'].value_counts()
    fig, ax = plt.subplots()
    state_counts.plot(kind='pie', autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"), ax=ax)
    ax.set_ylabel('')
    ax.set_title("Customer Distribution by State")
    st.pyplot(fig)

# Delivery Analysis
st.subheader("Delivery Times")
delivery_times = (filtered_df['order_delivered_customer_date'] - filtered_df['order_purchase_timestamp']).dt.days
fig, ax = plt.subplots(figsize=(10, 5))
sns.histplot(delivery_times, bins=20, kde=True, color="skyblue")
ax.set_title("Distribution of Delivery Times")
ax.set_xlabel("Delivery Time (days)")
ax.set_ylabel("Frequency")
st.pyplot(fig)

# Footer
st.caption("Data sourced from E-commerce dataset. Copyright by Raihan © 2024 ")
