import time

for filename in files:

    file_path = BASE_DIR / filename

    if not file_path.exists():
        continue

    try:
        start = time.time()

        print(f"MULAI MEMBACA: {filename}", flush=True)

        df = pd.read_csv(file_path)

        elapsed = time.time() - start

        print(
            f"SELESAI: {filename} | "
            f"Shape: {df.shape} | "
            f"Waktu: {elapsed:.2f} detik",
            flush=True
        )

        st.success(f"{filename} berhasil dibaca")

        st.write("Jumlah baris:", len(df))
        st.write("Jumlah kolom:", len(df.columns))
        st.write("Ukuran memori:")

        st.write(
            f"{df.memory_usage(deep=True).sum() / (1024**2):.2f} MB"
        )

        del df

    except Exception as e:
        st.error(f"Gagal membaca {filename}")
        st.exception(e)
