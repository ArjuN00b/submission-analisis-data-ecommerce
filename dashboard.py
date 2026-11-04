
from pathlib import Path

import gc

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ============================================================
# 1. KONFIGURASI DASHBOARD
# ============================================================

st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent

st.title("🛒 E-Commerce Public Dataset Analysis Dashboard")

st.markdown(
    """
    Dashboard interaktif untuk menganalisis perilaku pelanggan,
    performa pengiriman, persebaran geografis, dan ulasan produk.
    """
)

# Tampilan visualisasi
sns.set_theme(style="whitegrid")


# ============================================================
# 2. FUNGSI LOAD DATA (LAZY LOADING + CACHING)
# ============================================================

@st.cache_data(
    max_entries=1,
    show_spinner="Sedang memuat dataset..."
)
def load_data(filename):

    file_path = BASE_DIR / filename

    # Periksa keberadaan file
    if not file_path.exists():
        raise FileNotFoundError(
            f"File dataset tidak ditemukan: {file_path}"
        )

    # Tentukan kolom yang benar-benar diperlukan
    if filename == "main_data_rfm.csv":

        required_columns = ["Segment"]

    elif filename == "main_data_geo.csv":

        # Periksa nama kolom state karena bisa berbeda
        # tergantung hasil proses data wrangling.
        header = pd.read_csv(file_path, nrows=0).columns

        if "customer_state" in header:
            customer_state_col = "customer_state"

        elif "customer_state_x" in header:
            customer_state_col = "customer_state_x"

        else:
            raise ValueError(
                "Kolom customer_state atau customer_state_x "
                "tidak ditemukan pada dataset geografis."
            )

        required_columns = [
            customer_state_col,
            "seller_state",
            "actual_delivery_time"
        ]

    elif filename == "main_data_reviews.csv":

        required_columns = [
            "product_category_name_english",
            "price",
            "review_score",
            "actual_delivery_time",
            "order_id"
        ]

    else:
        raise ValueError(
            f"Nama dataset tidak dikenali: {filename}"
        )

    # Periksa ketersediaan kolom sebelum membaca data
    if filename != "main_data_geo.csv":
        header = pd.read_csv(file_path, nrows=0).columns

    missing_columns = [
        col for col in required_columns
        if col not in header
    ]

    if missing_columns:
        raise ValueError(
            f"Kolom berikut tidak ditemukan dalam {filename}: "
            f"{missing_columns}"
        )

    # Baca hanya kolom yang dibutuhkan
    df = pd.read_csv(
        file_path,
        usecols=required_columns
    )

    if df.empty:
        raise ValueError(
            f"Dataset {filename} tidak memiliki data."
        )

    # Optimasi tipe data kategorikal
    categorical_columns = [
        "Segment",
        "customer_state",
        "customer_state_x",
        "seller_state",
        "product_category_name_english"
    ]

    for col in categorical_columns:
        if col in df.columns:
            df[col] = df[col].astype("category")

    # Pastikan kolom numerik benar-benar numerik
    numeric_columns = [
        "actual_delivery_time",
        "price",
        "review_score"
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    return df


# ============================================================
# 3. FUNGSI PENANGANAN ERROR
# ============================================================

def get_data(filename):

    try:
        return load_data(filename)

    except Exception as error:

        st.error(
            f"Gagal memuat dataset {filename}."
        )

        st.exception(error)

        st.stop()


# ============================================================
# 4. FUNGSI MENAMPILKAN PLOT
# ============================================================

def show_plot(fig):

    st.pyplot(fig)

    # Bebaskan memori figure setelah digunakan
    plt.close(fig)


# ============================================================
# 5. SIDEBAR DAN NAVIGASI
# ============================================================

st.sidebar.header("Filter & Navigasi")

menu = st.sidebar.selectbox(
    "Pilih Halaman Analisis:",
    [
        "Segmentasi Pelanggan (RFM)",
        "Analisis Logistik & Geografis",
        "Kualitas Produk & Kepuasan"
    ]
)


# ============================================================
# 6. HALAMAN 1: SEGMENTASI PELANGGAN RFM
# ============================================================

if menu == "Segmentasi Pelanggan (RFM)":

    st.header(
        "👥 Segmentasi Pelanggan Berdasarkan Analisis RFM"
    )

    st.markdown(
        "Analisis distribusi pelanggan berdasarkan "
        "segmen RFM (Recency, Frequency, Monetary)."
    )

    # Lazy loading: hanya membaca dataset RFM
    rfm = get_data("main_data_rfm.csv")

    # Menghitung jumlah pelanggan setiap segmen
    segment_counts = (
        rfm["Segment"]
        .value_counts()
        .reset_index()
    )

    segment_counts.columns = [
        "Segment",
        "Count"
    ]

    col1, col2 = st.columns([2, 1])

    # Visualisasi distribusi segmen
    with col1:

        st.subheader("Distribusi Segmen Pelanggan")

        fig, ax = plt.subplots(figsize=(10, 5))

        sns.barplot(
            x="Count",
            y="Segment",
            data=segment_counts,
            palette="viridis",
            ax=ax,
            hue="Segment",
            legend=False,
            errorbar=None
        )

        ax.set_title(
            "Distribusi Segmen Pelanggan"
        )

        ax.set_xlabel("Jumlah Pelanggan")
        ax.set_ylabel("Segmen Pelanggan")

        fig.tight_layout()

        show_plot(fig)

    # Persentase setiap segmen
    with col2:

        st.subheader("Persentase Segmen")

        pct = (
            rfm["Segment"]
            .value_counts(normalize=True)
            * 100
        )

        for seg, val in pct.items():

            st.metric(
                label=str(seg),
                value=f"{val:.2f}%"
            )

    st.caption(
        f"Total pelanggan yang dianalisis: {len(rfm):,}"
    )


# ============================================================
# 7. HALAMAN 2: ANALISIS LOGISTIK & GEOGRAFIS
# ============================================================

elif menu == "Analisis Logistik & Geografis":

    st.header(
        "📍 Analisis Sebaran Geografis & Logistik Pengiriman"
    )

    st.markdown(
        "Menganalisis rata-rata waktu pengiriman "
        "berdasarkan lokasi pelanggan dan penjual."
    )

    # Lazy loading: hanya membaca dataset geografis
    geo_delivery_df = get_data("main_data_geo.csv")

    # Menentukan kolom state pelanggan
    if "customer_state" in geo_delivery_df.columns:
        cust_state_col = "customer_state"

    else:
        cust_state_col = "customer_state_x"

    # Menghitung rata-rata waktu pengiriman setiap state
    state_delivery = (
        geo_delivery_df
        .groupby(
            cust_state_col,
            observed=True
        )["actual_delivery_time"]
        .mean()
        .reset_index()
        .dropna()
        .sort_values(
            by="actual_delivery_time",
            ascending=False
        )
    )

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # Visualisasi 1: Rata-rata waktu pengiriman per state
    # --------------------------------------------------------

    with col1:

        st.subheader(
            "Rata-rata Waktu Pengiriman Per State"
        )

        fig, ax = plt.subplots(figsize=(10, 8))

        sns.barplot(
            x="actual_delivery_time",
            y=cust_state_col,
            data=state_delivery,
            palette="coolwarm",
            ax=ax,
            hue=cust_state_col,
            legend=False,
            errorbar=None
        )

        ax.set_xlabel(
            "Rata-rata Waktu Pengiriman"
        )

        ax.set_ylabel("Customer State")

        ax.set_title(
            "Rata-rata Waktu Pengiriman Per State"
        )

        fig.tight_layout()

        show_plot(fig)

    # --------------------------------------------------------
    # Visualisasi 2: Dampak lokasi penjual dan pembeli
    # --------------------------------------------------------

    with col2:

        st.subheader(
            "Dampak Lokasi Penjual-Pembeli"
        )

        # Menentukan apakah penjual dan pembeli
        # berada dalam state yang sama
        geo_delivery_df["same_state"] = (
            geo_delivery_df[cust_state_col]
            == geo_delivery_df["seller_state"]
        )

        # Agregasi data sebelum visualisasi
        same_state_delivery = (
            geo_delivery_df
            .groupby(
                "same_state",
                observed=True
            )["actual_delivery_time"]
            .mean()
            .reset_index()
        )

        same_state_delivery["location_type"] = (
            same_state_delivery["same_state"]
            .map({
                False: "Luar Negara Bagian",
                True: "Dalam Negara Bagian"
            })
        )

        fig, ax = plt.subplots(figsize=(10, 8))

        sns.barplot(
            x="location_type",
            y="actual_delivery_time",
            data=same_state_delivery,
            order=[
                "Luar Negara Bagian",
                "Dalam Negara Bagian"
            ],
            palette="Set2",
            ax=ax,
            hue="location_type",
            legend=False,
            errorbar=None
        )

        ax.set_xlabel(
            "Lokasi Penjual dan Pembeli"
        )

        ax.set_ylabel(
            "Rata-rata Waktu Pengiriman"
        )

        ax.set_title(
            "Perbandingan Waktu Pengiriman"
        )

        fig.tight_layout()

        show_plot(fig)

    st.caption(
        f"Total data pengiriman yang dianalisis: "
        f"{len(geo_delivery_df):,}"
    )


# ============================================================
# 8. HALAMAN 3: KUALITAS PRODUK & KEPUASAN
# ============================================================

elif menu == "Kualitas Produk & Kepuasan":

    st.header(
        "⭐️ Analisis Kualitas Produk & Korelasi Kepuasan"
    )

    st.markdown(
        "Menganalisis pendapatan kategori produk, "
        "skor ulasan pelanggan, serta hubungan "
        "antara waktu pengiriman dan kepuasan pelanggan."
    )

    # Lazy loading: hanya membaca dataset reviews
    product_reviews_df = get_data(
        "main_data_reviews.csv"
    )

    # --------------------------------------------------------
    # Menghitung pendapatan dan rata-rata review kategori
    # --------------------------------------------------------

    category_revenue = (
        product_reviews_df
        .groupby(
            "product_category_name_english",
            observed=True
        )
        .agg({
            "price": "sum",
            "review_score": "mean",
            "actual_delivery_time": "mean"
        })
        .reset_index()
    )

    category_revenue.rename(
        columns={
            "price": "total_revenue"
        },
        inplace=True
    )

    # Mengambil 10 kategori dengan pendapatan tertinggi
    top_10_categories = (
        category_revenue
        .dropna(subset=["total_revenue"])
        .sort_values(
            by="total_revenue",
            ascending=False
        )
        .head(10)
    )

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # Visualisasi 1: Review score 10 kategori tertinggi
    # --------------------------------------------------------

    with col1:

        st.subheader(
            "Review Score 10 Kategori Pendapatan Tertinggi"
        )

        if not top_10_categories.empty:

            fig, ax = plt.subplots(figsize=(10, 6))

            plot_categories = (
                top_10_categories
                .sort_values(by="review_score")
                .dropna(subset=["review_score"])
            )

            sns.barplot(
                x="review_score",
                y="product_category_name_english",
                data=plot_categories,
                palette="coolwarm_r",
                ax=ax,
                hue="product_category_name_english",
                legend=False,
                errorbar=None
            )

            ax.set_xlabel("Rata-rata Review Score")
            ax.set_ylabel("Kategori Produk")

            ax.set_title(
                "Review Score Kategori dengan Pendapatan Tertinggi"
            )

            fig.tight_layout()

            show_plot(fig)

        else:

            st.warning(
                "Tidak ada data kategori produk yang dapat divisualisasikan."
            )

    # --------------------------------------------------------
    # Visualisasi 2: Korelasi waktu pengiriman dan review
    # --------------------------------------------------------

    with col2:

        st.subheader(
            "Korelasi Waktu Pengantaran vs Skor Ulasan"
        )

        top_10_names = (
            top_10_categories[
                "product_category_name_english"
            ].tolist()
        )

        filtered_reviews_df = (
            product_reviews_df[
                product_reviews_df[
                    "product_category_name_english"
                ].isin(top_10_names)
            ]
        )

        # Mengelompokkan berdasarkan order_id
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

        if len(grouped_reviews) >= 2:

            # Membatasi titik scatter agar visualisasi
            # tetap ringan ketika jumlah order sangat besar.
            max_plot_rows = 10000

            if len(grouped_reviews) > max_plot_rows:

                plot_reviews = grouped_reviews.sample(
                    n=max_plot_rows,
                    random_state=42
                )

                st.caption(
                    "Visualisasi menggunakan sampel "
                    f"{max_plot_rows:,} dari "
                    f"{len(grouped_reviews):,} order."
                )

            else:

                plot_reviews = grouped_reviews

            fig, ax = plt.subplots(figsize=(10, 6))

            sns.regplot(
                x="actual_delivery_time",
                y="review_score",
                data=plot_reviews,
                ax=ax,
                scatter_kws={
                    "alpha": 0.3,
                    "s": 20,
                    "rasterized": True
                },
                line_kws={
                    "color": "red"
                },
                ci=None
            )

            ax.set_xlabel(
                "Actual Delivery Time"
            )

            ax.set_ylabel(
                "Review Score"
            )

            ax.set_title(
                "Korelasi Waktu Pengiriman vs Skor Ulasan"
            )

            fig.tight_layout()

            show_plot(fig)

        else:

            st.warning(
                "Data tidak cukup untuk membuat visualisasi korelasi."
            )

    st.caption(
        f"Total data ulasan yang dianalisis: "
        f"{len(product_reviews_df):,}"
    )


# ============================================================
# 9. FOOTER
# ============================================================

st.sidebar.divider()

st.sidebar.caption(
    "E-Commerce Public Dataset Analysis"
)

st.sidebar.caption(
    "Built with Python, Pandas, Matplotlib, Seaborn & Streamlit"
)

# Membersihkan objek yang tidak lagi digunakan
gc.collect()
