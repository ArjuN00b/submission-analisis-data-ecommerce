
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# =========================================================
# 1. KONFIGURASI DASHBOARD
# =========================================================

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
    performa pengiriman, dan kualitas produk berdasarkan
    E-Commerce Public Dataset.
    """
)

# =========================================================
# 2. LOAD DATASET
# =========================================================

@st.cache_data
def load_data():

    # Dataset RFM
    rfm_df = pd.read_csv(
        BASE_DIR / "main_data_rfm.csv",
        usecols=["Segment"]
    )

    # Dataset Geografis dan Logistik
    geo_path = BASE_DIR / "main_data_geo.csv"

    geo_columns = pd.read_csv(
        geo_path,
        nrows=0
    ).columns.tolist()

    if "customer_state" in geo_columns:
        cust_state_col = "customer_state"
    elif "customer_state_x" in geo_columns:
        cust_state_col = "customer_state_x"
    else:
        raise ValueError(
            "Kolom customer_state tidak ditemukan dalam dataset geografis."
        )

    geo_df = pd.read_csv(
        geo_path,
        usecols=[
            cust_state_col,
            "seller_state",
            "actual_delivery_time"
        ]
    )

    # Dataset Produk dan Review
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
    with st.spinner("Memuat dataset..."):
        rfm, geo_delivery_df, product_reviews_df, cust_state_col = load_data()

except Exception as e:
    st.error("Terjadi kesalahan ketika memuat dataset.")
    st.exception(e)
    st.stop()


# =========================================================
# 3. FUNGSI BANTUAN
# =========================================================

def show_chart(fig):
    """Menampilkan grafik dan membersihkan figure."""
    st.pyplot(fig, clear_figure=True)
    plt.close(fig)


def show_error(error):
    """Menampilkan informasi error pada dashboard."""
    st.error("Terjadi kesalahan ketika membuat visualisasi.")
    st.exception(error)


# =========================================================
# 4. SIDEBAR NAVIGASI
# =========================================================

st.sidebar.header("📊 Filter & Navigasi")

menu = st.sidebar.selectbox(
    "Pilih Halaman Analisis:",
    [
        "Segmentasi Pelanggan (RFM)",
        "Analisis Logistik & Geografis",
        "Kualitas Produk & Kepuasan"
    ]
)

st.sidebar.divider()

st.sidebar.success("Dataset berhasil dimuat.")

st.sidebar.caption(
    f"Data RFM: {len(rfm):,} baris\n\n"
    f"Data Geografis: {len(geo_delivery_df):,} baris\n\n"
    f"Data Review: {len(product_reviews_df):,} baris"
)


# =========================================================
# 5. SEGMENTASI PELANGGAN (RFM)
# =========================================================

if menu == "Segmentasi Pelanggan (RFM)":

    st.header("Segmentasi Pelanggan Berdasarkan Analisis RFM")

    st.markdown(
        """
        Halaman ini menampilkan distribusi pelanggan berdasarkan
        hasil segmentasi Recency, Frequency, dan Monetary (RFM).
        """
    )

    try:

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

        # Grafik distribusi segmen
        with col1:

            st.subheader("Distribusi Segmen Pelanggan")

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

        # Persentase segmen
        with col2:

            st.subheader("Persentase Segmen")

            pct = (
                rfm["Segment"]
                .value_counts(normalize=True) * 100
            )

            for seg, val in pct.items():

                st.metric(
                    label=seg,
                    value=f"{val:.2f}%"
                )

    except Exception as e:
        show_error(e)


# =========================================================
# 6. ANALISIS LOGISTIK & GEOGRAFIS
# =========================================================

elif menu == "Analisis Logistik & Geografis":

    st.header("Analisis Sebaran Geografis & Logistik Pengiriman")

    st.markdown(
        """
        Halaman ini digunakan untuk menganalisis rata-rata waktu
        pengiriman berdasarkan lokasi pelanggan serta membandingkan
        pengiriman dalam dan luar state.
        """
    )

    try:

        # Konversi data waktu pengiriman
        geo_delivery_df["actual_delivery_time"] = pd.to_numeric(
            geo_delivery_df["actual_delivery_time"],
            errors="coerce"
        )

        # Menghapus data kosong
        geo_delivery_df = geo_delivery_df.dropna(
            subset=[
                cust_state_col,
                "seller_state",
                "actual_delivery_time"
            ]
        )

        if geo_delivery_df.empty:
            st.warning(
                "Tidak terdapat data geografis yang valid untuk ditampilkan."
            )
            st.stop()

        col1, col2 = st.columns(2)

        # -------------------------------------------------
        # Grafik 1: Rata-rata waktu pengiriman per state
        # -------------------------------------------------

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

            ax.set_title(
                "Rata-rata Waktu Pengiriman per State"
            )

            ax.set_xlabel(
                "Rata-rata Waktu Pengiriman"
            )

            ax.set_ylabel(
                "Customer State"
            )

            fig.tight_layout()

            show_chart(fig)

        # -------------------------------------------------
        # Grafik 2: Perbandingan lokasi penjual dan pembeli
        # -------------------------------------------------

        with col2:

            st.subheader("Dampak Lokasi Penjual-Pembeli")

            same_state_df = geo_delivery_df.copy()

            same_state_df["Lokasi Pengiriman"] = (
                same_state_df[cust_state_col]
                == same_state_df["seller_state"]
            ).map({
                True: "Dalam Negara Bagian",
                False: "Luar Negara Bagian"
            })

            delivery_comparison = (
                same_state_df
                .groupby("Lokasi Pengiriman")[
                    "actual_delivery_time"
                ]
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

            ax.set_title(
                "Perbandingan Waktu Pengiriman"
            )

            ax.set_xlabel(
                "Lokasi Penjual dan Pembeli"
            )

            ax.set_ylabel(
                "Rata-rata Waktu Pengiriman"
            )

            fig.tight_layout()

            show_chart(fig)

    except Exception as e:
        show_error(e)


# =========================================================
# 7. KUALITAS PRODUK & KEPUASAN
# =========================================================

elif menu == "Kualitas Produk & Kepuasan":

    st.header("Analisis Kualitas Kategori Produk & Korelasi Kepuasan")

    st.markdown(
        """
        Halaman ini menampilkan kategori produk dengan pendapatan
        tertinggi, rata-rata skor ulasan, serta hubungan antara
        waktu pengiriman dan kepuasan pelanggan.
        """
    )

    try:

        # -------------------------------------------------
        # Persiapan data
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Agregasi pendapatan dan review per kategori
        # -------------------------------------------------

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

        category_revenue = category_revenue.rename(
            columns={
                "price": "total_revenue"
            }
        )

        # Mengambil 10 kategori dengan pendapatan tertinggi
        top_10_categories = (
            category_revenue
            .sort_values(
                by="total_revenue",
                ascending=False
            )
            .head(10)
        )

        if top_10_categories.empty:
            st.warning(
                "Tidak terdapat data kategori produk yang valid."
            )
            st.stop()

        col1, col2 = st.columns(2)

        # -------------------------------------------------
        # Grafik 1: Review score 10 kategori teratas
        # -------------------------------------------------

        with col1:

            st.subheader(
                "Review Score 10 Kategori Pendapatan Tertinggi"
            )

            review_chart_data = (
                top_10_categories
                .dropna(subset=["review_score"])
                .sort_values(
                    by="review_score",
                    ascending=True
                )
            )

            if review_chart_data.empty:

                st.warning(
                    "Data review score tidak tersedia."
                )

            else:

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

                ax.set_title(
                    "Review Score Berdasarkan Kategori Produk"
                )

                ax.set_xlabel(
                    "Rata-rata Review Score"
                )

                ax.set_ylabel(
                    "Kategori Produk"
                )

                fig.tight_layout()

                show_chart(fig)

        # -------------------------------------------------
        # Grafik 2: Korelasi waktu pengiriman dan review
        # -------------------------------------------------

        with col2:

            st.subheader(
                "Korelasi Waktu Pengantaran vs Skor Ulasan"
            )

            top_10_names = (
                top_10_categories[
                    "product_category_name_english"
                ]
                .tolist()
            )

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

            # Menghapus nilai yang tidak valid
            grouped_reviews = grouped_reviews[
                grouped_reviews[
                    "actual_delivery_time"
                ].apply(
                    lambda x: pd.notna(x) and x >= 0
                )
                &
                grouped_reviews[
                    "review_score"
                ].between(1, 5)
            ]

            if len(grouped_reviews) < 2:

                st.warning(
                    "Data tidak cukup untuk membuat grafik korelasi."
                )

            else:

                # Membatasi data agar visualisasi lebih ringan
                plot_data = grouped_reviews.sample(
                    n=min(5000, len(grouped_reviews)),
                    random_state=42
                )

                fig, ax = plt.subplots(figsize=(10, 6))

                sns.regplot(
                    x="actual_delivery_time",
                    y="review_score",
                    data=plot_data,
                    ax=ax,
                    scatter_kws={
                        "alpha": 0.3,
                        "s": 20
                    },
                    line_kws={
                        "color": "red"
                    }
                )

                ax.set_title(
                    "Waktu Pengiriman vs Skor Ulasan"
                )

                ax.set_xlabel(
                    "Rata-rata Waktu Pengiriman"
                )

                ax.set_ylabel(
                    "Rata-rata Review Score"
                )

                fig.tight_layout()

                show_chart(fig)

    except Exception as e:
        show_error(e)


# =========================================================
# 8. FOOTER
# =========================================================

st.divider()

st.caption(
    "E-Commerce Public Dataset Analysis | "
    "Dashboard dibuat menggunakan Python, Pandas, "
    "Matplotlib, Seaborn, dan Streamlit."
)
