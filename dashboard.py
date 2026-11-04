
import streamlit as st

print("CHECKPOINT 1: Streamlit imported", flush=True)

st.set_page_config(
    page_title="Dashboard Diagnostic",
    layout="wide"
)

st.title("🔍 Dashboard Diagnostic")

# ==================================================
# TEST IMPORT LIBRARIES
# ==================================================

try:
    import pandas as pd
    print("CHECKPOINT 2: Pandas imported", flush=True)
    st.success("Pandas berhasil di-import")

    import matplotlib.pyplot as plt
    print("CHECKPOINT 3: Matplotlib imported", flush=True)
    st.success("Matplotlib berhasil di-import")

    import seaborn as sns
    print("CHECKPOINT 4: Seaborn imported", flush=True)
    st.success("Seaborn berhasil di-import")

except Exception as e:
    st.error(f"Import error: {e}")
    st.exception(e)
    st.stop()


# ==================================================
# TEST FILE DATASET
# ==================================================

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

st.subheader("Pemeriksaan Dataset")

files = [
    "main_data_rfm.csv",
    "main_data_geo.csv",
    "main_data_reviews.csv"
]

for filename in files:

    file_path = BASE_DIR / filename

    if file_path.exists():

        size_mb = file_path.stat().st_size / (1024 * 1024)

        st.success(
            f"{filename} ditemukan ({size_mb:.2f} MB)"
        )

    else:

        st.error(f"{filename} tidak ditemukan")


# ==================================================
# TEST MEMBACA HEADER DAN 5 BARIS DATA
# ==================================================

st.subheader("Tes Pembacaan Dataset")

for filename in files:

    file_path = BASE_DIR / filename

    if not file_path.exists():
        continue

    try:

        print(f"CHECKPOINT 5: Reading {filename}", flush=True)

        df = pd.read_csv(
            file_path,
            nrows=5
        )

        print(
            f"CHECKPOINT 6: {filename} OK, "
            f"columns={len(df.columns)}",
            flush=True
        )

        st.success(f"{filename} berhasil dibaca")

        with st.expander(f"Lihat data {filename}"):

            st.write("Kolom:", df.columns.tolist())
            st.dataframe(df)

    except Exception as e:

        st.error(f"Gagal membaca {filename}")
        st.exception(e)

st.success("Seluruh pengujian diagnostik selesai!")
