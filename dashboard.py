
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

st.title("🛒 E-Commerce Public Dataset Analysis Dashboard")
st.markdown("Dashboard interaktif untuk menganalisis perilaku pelanggan, performa pengiriman, dan ulasan produk.")

# Load Data
@st.cache_data
def load_data():
    rfm_df = pd.read_csv('main_data_rfm.csv')
    geo_df = pd.read_csv('main_data_geo.csv')
    reviews_df = pd.read_csv('main_data_reviews.csv')
    return rfm_df, geo_df, reviews_df

rfm, geo_delivery_df, product_reviews_df = load_data()

# Sidebar untuk Filter
st.sidebar.header("Filter & Navigasi")
menu = st.sidebar.selectbox("Pilih Halaman Analisis:", ["Segmentasi Pelanggan (RFM)", "Analisis Logistik & Geografis", "Kualitas Produk & Kepuasan"])

if menu == "Segmentasi Pelanggan (RFM)":
    st.header("👥 Segmentasi Pelanggan Berdasarkan Analisis RFM")
    
    segment_counts = rfm['Segment'].value_counts().reset_index()
    segment_counts.columns = ['Segment', 'Count']
    
    col1, col2 = st.columns([2, 1])
    with col1:
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x='Count', y='Segment', data=segment_counts, palette='viridis', ax=ax, hue='Segment', legend=False)
        ax.set_title('Distribusi Segmen Pelanggan')
        st.pyplot(fig)
    
    with col2:
        st.subheader("Persentase Segmen")
        pct = rfm['Segment'].value_counts(normalize=True) * 100
        for seg, val in pct.items():
            st.metric(label=seg, value=f"{val:.2f}%")

elif menu == "Analisis Logistik & Geografis":
    st.header("📍 Analisis Sebaran Geografis & Logistik Pengiriman")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Rata-rata Waktu Pengiriman Per State")
        cust_state_col = 'customer_state' if 'customer_state' in geo_delivery_df.columns else 'customer_state_x'
        state_delivery = geo_delivery_df.groupby(cust_state_col)['actual_delivery_time'].mean().reset_index().sort_values(by='actual_delivery_time', ascending=False)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.barplot(x='actual_delivery_time', y=cust_state_col, data=state_delivery, palette='coolwarm', ax=ax, hue=cust_state_col, legend=False)
        st.pyplot(fig)
        
    with col2:
        st.subheader("Dampak Lokasi Penjual-Pembeli")
        geo_delivery_df['same_state'] = geo_delivery_df[cust_state_col] == geo_delivery_df['seller_state']
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.barplot(x='same_state', y='actual_delivery_time', data=geo_delivery_df, palette='Set2', ax=ax, hue='same_state', legend=False)
        ax.set_xticklabels(['Luar Negara Bagian', 'Dalam Negara Bagian'])
        st.pyplot(fig)

elif menu == "Kualitas Produk & Kepuasan":
    st.header("⭐️ Analisis Kualitas Kategori Produk & Korelasi Kepuasan")
    
    category_revenue = product_reviews_df.groupby('product_category_name_english').agg({
        'price': 'sum',
        'review_score': 'mean',
        'actual_delivery_time': 'mean'
    }).reset_index()
    category_revenue.rename(columns={'price': 'total_revenue'}, inplace=True)
    top_10_categories = category_revenue.sort_values(by='total_revenue', ascending=False).head(10)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Review Score 10 Kategori Pendapatan Tertinggi")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x='review_score', y='product_category_name_english', data=top_10_categories.sort_values(by='review_score'), palette='coolwarm_r', ax=ax, hue='product_category_name_english', legend=False)
        st.pyplot(fig)
        
    with col2:
        st.subheader("Korelasi Waktu Pengantaran vs Skor Ulasan")
        top_10_names = top_10_categories['product_category_name_english'].tolist()
        filtered_reviews_df = product_reviews_df[product_reviews_df['product_category_name_english'].isin(top_10_names)]
        grouped_reviews = filtered_reviews_df.groupby('order_id').agg({'actual_delivery_time':'mean', 'review_score':'mean'})
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.regplot(x='actual_delivery_time', y='review_score', data=grouped_reviews, ax=ax, scatter_kws={'alpha':0.3}, line_kws={'color':'red'})
        st.pyplot(fig)
