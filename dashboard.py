
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# 1. KONFIGURASI DASHBOARD

st.set_page_config(
    page_title="E-Commerce Dashboard",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent

st.title("🛒 E-Commerce Public Dataset Analysis Dashboard")
st.markdown(
    "Dashboard interaktif untuk menganalisis perilaku pelanggan, "
    "performa pengiriman, dan ulasan produk."
)

# 2. LOAD DATA

@st.cache_data
def load_data():
    # RFM: hanya membutuhkan kolom Segment
    rfm_df = pd.read_csv(
        BASE_DIR / "main_data_rfm.csv",
        usecols=["Segment"]
    )

    # Geo: deteksi nama kolom state yang tersedia
    geo_path = BASE_DIR / "main_data_geo.csv"
    geo_columns = pd.read_csv(geo_path, nrows=0).columns.tolist()

    if "customer_state" in geo_columns:
        cust_state_col = "customer_state"
    elif "customer_state_x" in geo_columns:
        cust_state_col = "customer_state_x"
    else:
        raise ValueError("Kolom customer_state tidak ditemukan.")

    geo_df = pd.read_csv(
        geo_path,
        usecols=[
            cust_state_col,
            "seller_state",
            "actual_delivery_time"
        ]
    )

    # Reviews: hanya membaca kolom yang digunakan dashboard
    reviews_df = pd.read_csv(
        BASE_DIR / "main_data_reviews.csv",
        usecols=[
            "product_category_name_english",
            "price",
            "review_score",
            "actual_delivery_time",
            "order_id"
        ]
    )

    return rfm_df, geo_df, reviews_df, cust_state_col


try:
    rfm, geo_delivery_df, product_reviews_df, cust_state_col = load_data()

except Exception as e:
    st.error("Terjadi kesalahan ketika memuat dataset.")
    st.exception(e)
    st.stop()


# 3. SIDEBAR NAVIGASI

st.sidebar.header("Filter & Navigasi")

menu = st.sidebar.selectbox(
    "Pilih Halaman Analisis:",
    [
        "Segmentasi Pelanggan (RFM)",
        "Analisis Logistik & Geografis",
        "Kualitas Produk & Kepuasan"
    ]
)


# FUNGSI MENAMPILKAN GRAFIK

def show_chart(fig):
    st.pyplot(fig, clear_figure=True)
    plt.close(fig)


# 4. SEGMENTASI PELANGGAN (RFM)

if menu == "Segmentasi Pelanggan (RFM)":

    st.header("Segmentasi Pelanggan Berdasarkan Analisis RFM")

    segment_counts = (
        rfm["Segment"]
        .value_counts()
        .reset_index()
    )

    segment_counts.columns = ["Segment", "Count"]

    col1, col2 = st.columns([2, 1])

    with col1:
        fig, ax = plt.subplots(figsize=(10, 5))

        sns.barplot(
            x="Count",
            y="Segment",
            data=segment_counts,
            hue="Segment",
            palette="viridis",
            legend=False,
            ax=ax
        )

        ax.set_title("Distribusi Segmen Pelanggan")
        ax.set_xlabel("Jumlah Pelanggan")
        ax.set_ylabel("Segmen")

        fig.tight_layout()
        show_chart(fig)

    with col2:
        st.subheader("Persentase Segmen")

        pct = rfm["Segment"].value_counts(normalize=True) * 100

        for seg, val in pct.items():
            st.metric(
                label=seg,
                value=f"{val:.2f}%"
            )


# 5. ANALISIS LOGISTIK & GEOGRAFIS

elif menu == "Analisis Logistik & Geografis":

    st.header("Analisis Sebaran Geografis & Logistik Pengiriman")

    # Pastikan waktu pengiriman berupa angka
    geo_delivery_df["actual_delivery_time"] = pd.to_numeric(
        geo_delivery_df["actual_delivery_time"],
        errors="coerce"
    )

    geo_delivery_df = geo_delivery_df.dropna(
        subset=[
            cust_state_col,
            "seller_state",
            "actual_delivery_time"
        ]
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Rata-rata Waktu Pengiriman Per State")

        state_delivery = (
            geo_delivery_df
            .groupby(cust_state_col)["actual_delivery_time"]
            .mean()
            .reset_index()
            .sort_values(
                by="actual_delivery_time",
                ascending=False
            )
        )

        fig, ax = plt.subplots(figsize=(10, 8))

        sns.barplot(
            x="actual_delivery_time",
            y=cust_state_col,
            data=state_delivery,
            hue=cust_state_col,
            palette="coolwarm",
            legend=False,
            ax=ax
        )

        ax.set_title("Rata-rata Waktu Pengiriman per State")
        ax.set_xlabel("Rata-rata Waktu Pengiriman")
        ax.set_ylabel("Customer State")

        fig.tight_layout()
        show_chart(fig)

    with col2:
        st.subheader("Dampak Lokasi Penjual-Pembeli")

        # Membuat kolom baru tanpa mengubah DataFrame utama
        same_state_df = geo_delivery_df.copy()

        same_state_df["Lokasi Pengiriman"] = (
            same_state_df[cust_state_col]
            == same_state_df["seller_state"]
        ).map({
            True: "Dalam Negara Bagian",
            False: "Luar Negara Bagian"
        })

        # Hitung rata-rata waktu pengiriman
        delivery_comparison = (
            same_state_df
            .groupby("Lokasi Pengiriman")["actual_delivery_time"]
            .mean()
            .reset_index()
        )

        fig, ax = plt.subplots(figsize=(10, 8))

        sns.barplot(
            x="Lokasi Pengiriman",
            y="actual_delivery_time",
            data=delivery_comparison,
            hue="Lokasi Pengiriman",
            palette="Set2",
            legend=False,
            ax=ax
        )

        ax.set_title("Perbandingan Waktu Pengiriman")
        ax.set_xlabel("Lokasi Penjual dan Pembeli")
        ax.set_ylabel("Rata-rata Waktu Pengiriman")

        fig.tight_layout()
        show_chart(fig)


# 6. KUALITAS PRODUK & KEPUASAN

elif menu == "Kualitas Produk & Kepuasan":

    st.header("Analisis Kualitas Kategori Produk & Korelasi Kepuasan")

    # Pastikan kolom numerik memiliki tipe data yang sesuai
    product_reviews_df["price"] = pd.to_numeric(
        product_reviews_df["price"],
        errors="coerce"
    )

    product_reviews_df["review_score"] = pd.to_numeric(
        product_reviews_df["review_score"],
        errors="coerce"
    )

    product_reviews_df["actual_delivery_time"] = pd.to_numeric(
        product_reviews_df["actual_delivery_time"],
        errors="coerce"
    )

    # Agregasi berdasarkan kategori produk
    category_revenue = (
        product_reviews_df
        .groupby("product_category_name_english")
        .agg({
            "price": "sum",
            "review_score": "mean",
            "actual_delivery_time": "mean"
        })
        .reset_index()
    )

    category_revenue.rename(
        columns={"price": "total_revenue"},
        inplace=True
    )

    top_10_categories = (
        category_revenue
        .sort_values(
            by="total_revenue",
            ascending=False
        )
        .head(10)
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Review Score 10 Kategori Pendapatan Tertinggi")

        review_chart_data = top_10_categories.sort_values(
            by="review_score"
        )

        fig, ax = plt.subplots(figsize=(10, 6))

        sns.barplot(
            x="review_score",
            y="product_category_name_english",
            data=review_chart_data,
            hue="product_category_name_english",
            palette="coolwarm_r",
            legend=False,
            ax=ax
        )

        ax.set_title("Review Score Berdasarkan Kategori Produk")
        ax.set_xlabel("Rata-rata Review Score")
        ax.set_ylabel("Kategori Produk")

        fig.tight_layout()
        show_chart(fig)

    with col2:
        st.subheader("Korelasi Waktu Pengantaran vs Skor Ulasan")

        top_10_names = top_10_categories[
            "product_category_name_english"
        ].tolist()

        filtered_reviews_df = product_reviews_df[
            product_reviews_df[
                "product_category_name_english"
            ].isin(top_10_names)
        ]

        grouped_reviews = (
            filtered_reviews_df
            .groupby("order_id")
            .agg({
                "actual_delivery_time": "mean",
                "review_score": "mean"
            })
            .dropna()
            .reset_index()
        )

        fig, ax = plt.subplots(figsize=(10, 6))

        sns.regplot(
            x="actual_delivery_time",
            y="review_score",
            data=grouped_reviews,
            ax=ax,
            scatter_kws={"alpha": 0.3},
            line_kws={"color": "red"}
        )

        ax.set_title("Waktu Pengiriman vs Skor Ulasan")
        ax.set_xlabel("Rata-rata Waktu Pengiriman")
        ax.set_ylabel("Rata-rata Review Score")

        fig.tight_layout()
        show_chart(fig)
