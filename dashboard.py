import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os


st.set_page_config(page_title="E-Commerce Public Dashboard", layout="wide")

# ── LOAD DATA ──────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_consolidated_data():
    rfm       = pd.read_csv(os.path.join(BASE_DIR, 'rfm_data.csv'))
    logistics = pd.read_csv(os.path.join(BASE_DIR, 'logistics_data.csv'))
    reviews   = pd.read_csv(os.path.join(BASE_DIR, 'product_reviews_data.csv'))
    return rfm, logistics, reviews

rfm_df, logistics_df, reviews_df = load_consolidated_data()

# ── PRE-COMPUTE SEGMEN RFM (sebelum sidebar agar bisa dijadikan opsi filter) ──
rfm_df['R_Score'] = pd.qcut(rfm_df['Recency'], 5, labels=[5, 4, 3, 2, 1], duplicates='drop')
rfm_df['F_Score'] = rfm_df['Frequency'].apply(lambda x: 1 if x == 1 else (2 if x == 2 else 3))
rfm_df['M_Score'] = pd.qcut(rfm_df['Monetary'], 5, labels=[1, 2, 3, 4, 5], duplicates='drop')

def segment_customer(row):
    try:
        r, f, m = int(row['R_Score']), int(row['F_Score']), int(row['M_Score'])
        if r >= 4 and f >= 2 and m >= 4:   return 'VIP/Champions'
        elif r <= 2:                        return 'At-Risk / Lost'
        elif r >= 3 and f == 1 and m <= 2: return 'New / Low Spender'
        else:                              return 'Potential Loyalist / Active'
    except:
        return 'Potential Loyalist / Active'

rfm_df['Segment'] = rfm_df.apply(segment_customer, axis=1)

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/color/96/000000/shop.png", width=80)
st.sidebar.title("Filter Analisis Data")

# Pilih Halaman — selalu tampil
page = st.sidebar.selectbox(
    "Pilih Halaman Analisis:",
    ["Overview & RFM Analysis", "Logistik & Geografis", "Kualitas Produk (Reviews)"]
)

st.sidebar.write("---")

# ── FILTER PER HALAMAN ────────────────────────────────────────────────────────

# ---------- Halaman 1: Overview & RFM -----------------------------------------
if page == "Overview & RFM Analysis":
    st.sidebar.subheader("🔍 Filter RFM")

    # Filter 1a: Segmen pelanggan
    all_segments  = sorted(rfm_df['Segment'].unique())
    sel_segments  = st.sidebar.multiselect(
        "Pilih Segmen Pelanggan:",
        options=all_segments,
        default=all_segments
    )

    # Filter 1b: Rentang Recency (hari sejak transaksi terakhir)
    rec_min, rec_max = int(rfm_df['Recency'].min()), int(rfm_df['Recency'].max())
    sel_recency = st.sidebar.slider(
        "Rentang Recency (hari):",
        min_value=rec_min,
        max_value=rec_max,
        value=(rec_min, rec_max)
    )

    # Filter 1c: Rentang Monetary (nilai belanja)
    mon_min, mon_max = float(rfm_df['Monetary'].min()), float(rfm_df['Monetary'].max())
    sel_monetary = st.sidebar.slider(
        "Rentang Total Belanja (R$):",
        min_value=mon_min,
        max_value=mon_max,
        value=(mon_min, mon_max)
    )

    # Terapkan filter
    filtered_rfm = rfm_df[
        (rfm_df['Segment'].isin(sel_segments)) &
        (rfm_df['Recency'] >= sel_recency[0]) &
        (rfm_df['Recency'] <= sel_recency[1]) &
        (rfm_df['Monetary'] >= sel_monetary[0]) &
        (rfm_df['Monetary'] <= sel_monetary[1])
    ]

# ---------- Halaman 2: Logistik & Geografis ------------------------------------
elif page == "Logistik & Geografis":
    st.sidebar.subheader("🔍 Filter Logistik")

    # Filter 2a: Wilayah pelanggan (state)
    all_states  = sorted(logistics_df['customer_state'].dropna().unique())
    sel_states  = st.sidebar.multiselect(
        "Pilih Wilayah Pelanggan (State):",
        options=all_states,
        default=["SP", "RJ", "MG", "RS", "PR"]
    )

    # Filter 2b: Maksimum keterlambatan pengiriman
    delay_min, delay_max = int(logistics_df['delivery_delay'].min()), int(logistics_df['delivery_delay'].max())
    sel_delay = st.sidebar.slider(
        "Rentang Keterlambatan Pengiriman (hari):",
        min_value=delay_min,
        max_value=delay_max,
        value=(delay_min, delay_max)
    )

    # Terapkan filter
    filtered_logistics = logistics_df[
        (logistics_df['customer_state'].isin(sel_states) if sel_states else pd.Series([True] * len(logistics_df)))
        & (logistics_df['delivery_delay'] >= sel_delay[0])
        & (logistics_df['delivery_delay'] <= sel_delay[1])
    ]

# ---------- Halaman 3: Kualitas Produk (Reviews) --------------------------------
elif page == "Kualitas Produk (Reviews)":
    st.sidebar.subheader("🔍 Filter Ulasan Produk")

    # Filter 3a: Kategori produk
    all_categories = sorted(reviews_df['product_category_name_english'].dropna().unique())
    sel_categories = st.sidebar.multiselect(
        "Pilih Kategori Produk:",
        options=all_categories,
        default=list(
            reviews_df.groupby('product_category_name_english')['price']
            .sum().nlargest(10).index
        )
    )

    # Filter 3b: Rentang skor ulasan
    sel_score = st.sidebar.select_slider(
        "Rentang Skor Ulasan (Bintang):",
        options=[1, 2, 3, 4, 5],
        value=(1, 5)
    )

    # Filter 3c: Rentang harga produk
    price_min, price_max = float(reviews_df['price'].min()), float(reviews_df['price'].max())
    sel_price = st.sidebar.slider(
        "Rentang Harga Produk (R$):",
        min_value=price_min,
        max_value=price_max,
        value=(price_min, min(price_max, 500.0))
    )

    # Terapkan filter
    filtered_reviews = reviews_df[
        (reviews_df['product_category_name_english'].isin(sel_categories) if sel_categories else pd.Series([True] * len(reviews_df)))
        & (reviews_df['review_score'] >= sel_score[0])
        & (reviews_df['review_score'] <= sel_score[1])
        & (reviews_df['price'] >= sel_price[0])
        & (reviews_df['price'] <= sel_price[1])
    ]

# ── HEADER UTAMA ───────────────────────────────────────────────────────────────
st.title("🛍️ E-Commerce Public Performance Dashboard")
st.markdown("**Periode Analisis Aktual (SMART):** Januari 2017 – Agustus 2018")
st.write("---")

# ══════════════════════════════════════════════════════════════════════════════
# HALAMAN 1 — Overview & RFM Analysis
# ══════════════════════════════════════════════════════════════════════════════
if page == "Overview & RFM Analysis":
    st.header("📊 Analisis RFM Pelanggan (Recency, Frequency, Monetary)")
    st.caption(
        f"Filter aktif → Segmen: {', '.join(sel_segments) if sel_segments else 'Semua'} | "
        f"Recency: {sel_recency[0]}–{sel_recency[1]} hari | "
        f"Monetary: R${sel_monetary[0]:,.0f}–R${sel_monetary[1]:,.0f}"
    )

    if filtered_rfm.empty:
        st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")
    else:
        # KPI Cards
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Pelanggan Terfilter",     f"{filtered_rfm['customer_unique_id'].nunique():,}")
        col2.metric("Rata-rata Pengeluaran (R$)",    f"R$ {filtered_rfm['Monetary'].mean():.2f}")
        col3.metric("Total Pendapatan Terfilter",    f"R$ {filtered_rfm['Monetary'].sum():,.2f}")

        col_a, col_b = st.columns(2)

        # Grafik 1: Distribusi segmen
        with col_a:
            st.subheader("Proporsi Segmen Pelanggan")
            fig, ax = plt.subplots(figsize=(8, 4))
            sns.countplot(
                data=filtered_rfm,
                y='Segment',
                order=filtered_rfm['Segment'].value_counts().index,
                palette='viridis', ax=ax
            )
            ax.set_xlabel("Jumlah Pelanggan")
            ax.set_ylabel("Segmen")
            st.pyplot(fig)
            plt.close(fig)

        # Grafik 2: Distribusi Monetary per segmen
        with col_b:
            st.subheader("Rata-rata Pengeluaran per Segmen")
            seg_monetary = (
                filtered_rfm.groupby('Segment')['Monetary']
                .mean().reset_index()
                .sort_values('Monetary', ascending=False)
            )
            fig, ax = plt.subplots(figsize=(8, 4))
            sns.barplot(data=seg_monetary, x='Monetary', y='Segment', palette='mako', ax=ax)
            ax.set_xlabel("Rata-rata Monetary (R$)")
            ax.set_ylabel("Segmen")
            st.pyplot(fig)
            plt.close(fig)

        # Grafik 3: Distribusi Recency
        st.subheader("Distribusi Recency Pelanggan Terfilter")
        fig, ax = plt.subplots(figsize=(12, 3))
        ax.hist(filtered_rfm['Recency'], bins=40, color='steelblue', edgecolor='white')
        ax.set_xlabel("Recency (hari sejak transaksi terakhir)")
        ax.set_ylabel("Jumlah Pelanggan")
        st.pyplot(fig)
        plt.close(fig)

# ══════════════════════════════════════════════════════════════════════════════
# HALAMAN 2 — Logistik & Geografis
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Logistik & Geografis":
    st.header("🚚 Kinerja Logistik dan Analisis Pengiriman")
    st.caption(
        f"Filter aktif → Wilayah: {', '.join(sel_states) if sel_states else 'Semua'} | "
        f"Keterlambatan: {sel_delay[0]}–{sel_delay[1]} hari"
    )

    if filtered_logistics.empty:
        st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Rata-rata Waktu Pengiriman Per Negara Bagian")
            state_logistics = (
                filtered_logistics.groupby('customer_state')
                .agg({'actual_delivery_time': 'mean'})
                .reset_index()
                .sort_values(by='actual_delivery_time', ascending=False)
            )
            fig, ax = plt.subplots(figsize=(10, max(4, len(state_logistics) * 0.4)))
            sns.barplot(data=state_logistics, x='actual_delivery_time', y='customer_state',
                        palette='coolwarm', ax=ax)
            ax.set_xlabel("Waktu Pengiriman (Hari)")
            ax.set_ylabel("Negara Bagian Pelanggan")
            st.pyplot(fig)
            plt.close(fig)

        with col2:
            st.subheader("Dampak Kesamaan State terhadap Kecepatan Pengiriman")
            filtered_logistics = filtered_logistics.copy()
            filtered_logistics['same_state'] = (
                filtered_logistics['customer_state'] == filtered_logistics['seller_state']
            )
            same_state_data = (
                filtered_logistics.groupby('same_state')['actual_delivery_time']
                .mean().reset_index()
            )
            same_state_data['Kondisi'] = same_state_data['same_state'].map(
                {True: 'Dalam State (Sama)', False: 'Luar State (Berbeda)'}
            )
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(data=same_state_data, x='Kondisi', y='actual_delivery_time',
                        palette='Set2', ax=ax)
            ax.set_ylabel("Rata-rata Waktu Pengiriman (Hari)")
            ax.set_xlabel("")
            st.pyplot(fig)
            plt.close(fig)

# ══════════════════════════════════════════════════════════════════════════════
# HALAMAN 3 — Kualitas Produk (Reviews)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Kualitas Produk (Reviews)":
    st.header("⭐️ Analisis Kualitas Produk & Ulasan Pelanggan")
    st.caption(
        f"Filter aktif → Kategori: {len(sel_categories)} dipilih | "
        f"Skor: {sel_score[0]}–{sel_score[1]} bintang | "
        f"Harga: R${sel_price[0]:,.0f}–R${sel_price[1]:,.0f}"
    )

    if filtered_reviews.empty:
        st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")
    else:
        top_categories = (
            filtered_reviews.groupby('product_category_name_english')
            .agg({'price': 'sum', 'review_score': 'mean'})
            .reset_index()
            .sort_values(by='price', ascending=False)
            .head(10)
        )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Rata-rata Rating dari 10 Kategori Teratas")
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(
                data=top_categories.sort_values(by='review_score'),
                x='review_score', y='product_category_name_english',
                palette='coolwarm_r', ax=ax
            )
            ax.set_xlabel("Skor Ulasan Rata-rata (1–5)")
            ax.set_ylabel("Kategori Produk")
            st.pyplot(fig)
            plt.close(fig)

        with col2:
            st.subheader("Korelasi Durasi Pengiriman vs Skor Ulasan")
            sample_reviews = filtered_reviews.sample(
                n=min(len(filtered_reviews), 15000), random_state=42
            )
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.regplot(
                data=sample_reviews,
                x='actual_delivery_time', y='review_score',
                scatter_kws={'alpha': 0.1, 'color': 'skyblue'},
                line_kws={'color': 'red'}, ax=ax
            )
            ax.set_xlabel("Waktu Pengiriman Aktual (Hari)")
            ax.set_ylabel("Skor Ulasan")
            st.pyplot(fig)
            plt.close(fig)

        # Grafik tambahan: distribusi skor ulasan dari data terfilter
        st.subheader("Distribusi Skor Ulasan (Data Terfilter)")
        fig, ax = plt.subplots(figsize=(8, 3))
        score_counts = filtered_reviews['review_score'].value_counts().sort_index()
        ax.bar(score_counts.index, score_counts.values,
               color=sns.color_palette('viridis', 5), edgecolor='white')
        ax.set_xlabel("Skor Ulasan (Bintang)")
        ax.set_ylabel("Jumlah Ulasan")
        ax.set_xticks([1, 2, 3, 4, 5])
        st.pyplot(fig)
        plt.close(fig)
