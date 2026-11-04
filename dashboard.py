
import streamlit as st

print("CHECKPOINT 1: Python started", flush=True)

st.set_page_config(
    page_title="Streamlit Test",
    layout="wide"
)

print("CHECKPOINT 2: Config loaded", flush=True)

st.title("🎉 Streamlit Berhasil!")

st.success("Dashboard berhasil dijalankan di Streamlit Cloud.")

st.write("Jika tulisan ini muncul, deployment dasar berhasil.")

print("CHECKPOINT 3: Dashboard rendered", flush=True)
