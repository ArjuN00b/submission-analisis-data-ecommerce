
import streamlit as st
import pandas as pd
from pathlib import Path
import time

st.set_page_config(
    page_title="Dashboard Diagnostic",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent

st.title("🔍 Dashboard Diagnostic")

files = [
    "main_data_rfm.csv",
    "main_data_geo.csv",
    "main_data_reviews.csv"
]

st.subheader("1. Pemeriksaan File")

for filename in files:
    file_path = BASE_DIR / filename

    if file_path.exists():
        size_mb = file_path.stat().st_size / (1024 * 1024)

        st.success(
            f"{filename} ditemukan ({size_mb:.2f} MB)"
        )
    else:
        st.error(f"{filename} tidak ditemukan!")

st.divider()
st.subheader("2. Pengujian Pembacaan Dataset")

for filename in files:

    file_path = BASE_DIR / filename

    if not file_path.exists():
        continue

    try:
        start = time.time()

        with st.spinner(f"Membaca {filename}..."):
            df = pd.read_csv(file_path)

        elapsed = time.time() - start

        st.success(
            f"{filename} berhasil dibaca!"
        )

        st.write("Jumlah baris:", len(df))
        st.write("Jumlah kolom:", len(df.columns))
        st.write("Waktu baca:", f"{elapsed:.2f} detik")

    except Exception as e:
        st.error(f"Gagal membaca {filename}")
        st.exception(e)

st.divider()
st.success("Pengujian selesai.")
