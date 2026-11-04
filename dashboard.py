
import streamlit as st
import pandas as pd
from pathlib import Path
import time

st.set_page_config(page_title="Tes Pembacaan Dataset", layout="wide")
st.title("Tes Pembacaan Dataset")

BASE_DIR = Path(__file__).resolve().parent

files = [
    "main_data_rfm.csv",
    "main_data_geo.csv",
    "main_data_reviews.csv"
]

for filename in files:
    file_path = BASE_DIR / filename

    st.subheader(filename)

    if not file_path.exists():
        st.error(f"File tidak ditemukan: {filename}")
        continue

    try:
        start = time.time()

        print(f"MULAI MEMBACA: {filename}", flush=True)

        df = pd.read_csv(file_path)

        elapsed = time.time() - start
        memory = df.memory_usage(deep=True).sum() / (1024 ** 2)

        st.success(f"{filename} berhasil dibaca!")

        st.write(f"Jumlah baris: {df.shape[0]:,}")
        st.write(f"Jumlah kolom: {df.shape[1]:,}")
        st.write(f"Ukuran memori: {memory:.2f} MB")
        st.write(f"Waktu membaca: {elapsed:.2f} detik")

        print(
            f"SELESAI: {filename} | "
            f"Shape: {df.shape} | "
            f"Waktu: {elapsed:.2f} detik",
            flush=True
        )

        del df

    except Exception as e:
        st.error(f"Gagal membaca {filename}")
        st.exception(e)
