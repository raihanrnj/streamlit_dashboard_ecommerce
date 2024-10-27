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

# Visualisasi 1: Distribusi Metode Pembayaran
st.subheader("Distribusi Metode Pembayaran (Q1)")
col1, col2 = st.columns(2)

with col1:
    plt.figure(figsize=(8, 6))
    sns.countplot(data=filtered_df, x='payment_type', palette='viridis', order=filtered_df['payment_type'].value_counts().index)
    plt.title("Distribusi Metode Pembayaran")
    plt.xlabel("Tipe Pembayaran")
    plt.ylabel("Jumlah Transaksi")
    st.pyplot(plt)

# Visualisasi 2: Persentase Keterlambatan Berdasarkan Metode Pembayaran
with col2:
    filtered_df['delay_days'] = (filtered_df['order_delivered_customer_date'] - filtered_df['order_estimated_delivery_date']).dt.days
    filtered_df['is_late'] = filtered_df['delay_days'].apply(lambda x: 'Late' if x > 0 else 'On Time')

    payment_delay = filtered_df.groupby(['payment_type', 'is_late']).size().unstack().fillna(0)
    payment_delay['Late_Percentage'] = (payment_delay['Late'] / (payment_delay['Late'] + payment_delay['On Time'])) * 100

    plt.figure(figsize=(10, 6))
    sns.barplot(x=payment_delay.index, y=payment_delay['Late_Percentage'], palette='viridis')
    plt.title('Persentase Keterlambatan Berdasarkan Metode Pembayaran')
    plt.xlabel('Metode Pembayaran')
    plt.ylabel('Persentase Keterlambatan (%)')
    st.pyplot(plt)

# Visualisasi 3: Waktu Pengiriman
st.subheader("Waktu Pengiriman  (Q2)")
col1, col2 = st.columns(2)

with col1:
    delivery_times = (filtered_df['order_delivered_customer_date'] - filtered_df['order_purchase_timestamp']).dt.days
    plt.figure(figsize=(10, 5))
    sns.histplot(delivery_times, bins=20, kde=True, color="skyblue")
    plt.title("Distribusi Waktu Pengiriman")
    plt.xlabel("Waktu Pengiriman (hari)")
    plt.ylabel("Frekuensi")
    st.pyplot(plt)

# Visualisasi 4: Jumlah Keterlambatan Berdasarkan Kota (Top 10)
with col2:
    city_late_counts = filtered_df[filtered_df['is_late'] == 'Late'].groupby('customer_city').size().sort_values(ascending=False).head(10)

    plt.figure(figsize=(12, 6))
    sns.barplot(x=city_late_counts.index, y=city_late_counts.values, palette='magma')
    plt.title('Jumlah Keterlambatan Berdasarkan Kota (Top 10)')
    plt.xlabel('Kota')
    plt.ylabel('Jumlah Keterlambatan')
    plt.xticks(rotation=45)
    st.pyplot(plt)

# Visualisasi 5: Kinerja Produk
st.subheader("Kinerja Produk")
col1, col2 = st.columns(2)

with col1:
    top_products = filtered_df.groupby("product_id")['order_item_id'].count().nlargest(5)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_products.values, y=top_products.index, palette="viridis")
    plt.title("Top 5 Produk Terlaris")
    plt.xlabel("Jumlah Transaksi")
    plt.ylabel("Produk")
    st.pyplot(plt)

# Visualisasi 6: Top 5 Produk Terburuk
with col2:
    bottom_products = filtered_df.groupby("product_id")['order_item_id'].count().nsmallest(5)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=bottom_products.values, y=bottom_products.index, palette="magma")
    plt.title("Top 5 Produk Terburuk")
    plt.xlabel("Jumlah Transaksi")
    plt.ylabel("Produk")
    st.pyplot(plt)

# Visualisasi 7: Distribusi Biaya Pengiriman
st.subheader("Distribusi Biaya Pengiriman")
col1, col2 = st.columns(2)

with col1:
    plt.figure(figsize=(10, 6))
    sns.histplot(filtered_df['freight_value'], bins=30, kde=True, color="green")
    plt.title("Distribusi Biaya Pengiriman")
    plt.xlabel("Biaya Pengiriman")
    plt.ylabel("Frekuensi")
    st.pyplot(plt)

# Visualisasi 8: Distribusi Jumlah Cicilan
with col2:
    plt.figure(figsize=(10, 6))
    sns.countplot(data=filtered_df, x='payment_installments', palette='muted')
    plt.title("Distribusi Jumlah Cicilan")
    plt.xlabel("Jumlah Cicilan")
    plt.ylabel("Jumlah Transaksi")
    st.pyplot(plt)
    
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
    sns.barplot(x=state_counts.index, y=state_counts.values, palette='pastel', ax=ax)
    ax.set_ylabel('Jumlah Pelanggan', fontsize=10)  # Ukuran font label
    ax.set_title("Distribusi Pelanggan berdasarkan Negara Bagian", fontsize=14)  # Ukuran font judul
    ax.set_xticklabels(state_counts.index, rotation=45)  # Rotasi label sumbu x agar lebih mudah dibaca
    st.pyplot(fig)
    

# Footer
st.caption("Data sourced from E-commerce dataset. Copyright by Raihan © 2024 ")
