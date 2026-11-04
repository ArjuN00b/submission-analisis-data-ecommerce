# E-Commerce Public Dataset Analysis & Dashboard 🛒

Proyek ini adalah submission akhir untuk kelas **Analisis Data dengan Python** di Dicoding. Proyek ini mencakup proses *Data Wrangling*, *Exploratory Data Analysis (EDA)*, *Visualisasi Data*, serta pembuatan *Dashboard Interaktif* menggunakan Streamlit.

## 📂 Struktur Direktori

```text
.
├── dashboard/
│   ├── dashboard.py          # Script utama aplikasi Streamlit
│   ├── requirements.txt      # Dependensi untuk dashboard
│   ├── main_data_rfm.csv     # Data siap pakai untuk visualisasi RFM
│   ├── main_data_geo.csv     # Data siap pakai untuk visualisasi Geografis
│   └── main_data_reviews.csv # Data siap pakai untuk visualisasi Ulasan
├── notebook.ipynb            # Analisis data lengkap dari Google Colab
├── requirements.txt          # Dependensi utama proyek
└── README.md                 # Dokumentasi proyek (File ini)
```

## 🛠️ Cara Menjalankan Dashboard Secara Lokal

### 1. Prasyarat
Pastikan Anda sudah menginstal Python (versi 3.8 ke atas direkomendasikan) di komputer Anda.

### 2. Instalasi Dependensi
Buka terminal atau command prompt pada direktori proyek ini, lalu jalankan perintah berikut untuk menginstal semua pustaka yang dibutuhkan:

```bash
pip install -r requirements.txt
```

### 3. Menjalankan Aplikasi Streamlit
Setelah instalasi selesai, jalankan perintah berikut untuk membuka dashboard interaktif di browser Anda:

```bash
streamlit run dashboard/dashboard.py
```

Aplikasi secara otomatis akan terbuka pada alamat lokal default: `http://localhost:8501`.

## 📈 Fitur Utama Dashboard
- **Segmentasi Pelanggan (RFM)**: Menganalisis kelompok pelanggan VIP hingga yang berisiko pergi (*At-Risk*).
- **Analisis Logistik & Geografis**: Menampilkan performa pengiriman barang antar negara bagian.
- **Kualitas Produk & Kepuasan**: Mengidentifikasi korelasi waktu pengiriman dengan skor ulasan produk.