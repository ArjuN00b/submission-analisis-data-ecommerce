# E-Commerce Public Dataset Analysis Dashboard

Dashboard interaktif ini dibangun menggunakan **Streamlit** untuk memvisualisasikan analisis data e-commerce mencakup:
- **Analisis RFM** (Recency, Frequency, Monetary) — segmentasi perilaku pelanggan
- **Analisis Logistik & Geografis** — kinerja pengiriman per wilayah negara bagian
- **Analisis Kualitas Produk** — rating ulasan dan korelasi dengan durasi pengiriman

---

## Struktur Direktori Proyek

```
Submission_FundamentalAnalisisData_Arjuna Sandya/
├── dashboard/
│   ├── dashboard.py              <- File utama dashboard Streamlit
│   ├── rfm_data.csv              <- Data hasil analisis RFM
│   ├── logistics_data.csv        <- Data logistik pengiriman
│   └── product_reviews_data.csv  <- Data ulasan produk
├── data/
│   └── E-Commerce Public Dataset/
│       ├── customers_dataset.csv
│       ├── geolocation_dataset.csv
│       ├── orders_dataset.csv
│       ├── order_items_dataset.csv
│       ├── order_payments_dataset.csv
│       ├── order_reviews_dataset.csv
│       ├── products_dataset.csv
│       ├── product_category_name_translation.csv
│       └── sellers_dataset.csv
├── requirements.txt
└── README.md
```

> **Catatan:** File CSV yang digunakan oleh dashboard (`rfm_data.csv`, `logistics_data.csv`, `product_reviews_data.csv`) berada di dalam folder `dashboard/`, **bukan** di folder `data/`. Dashboard membaca file secara relatif terhadap lokasi `dashboard.py`, sehingga direktori kerja saat menjalankan Streamlit harus berada di dalam folder `dashboard/`.

---

## Persyaratan

- Python 3.8 atau lebih baru
- pip (Python package manager)

---

## Cara Menjalankan Dashboard Secara Lokal

### 1. Clone atau ekstrak proyek

Pastikan seluruh struktur folder sudah lengkap seperti diagram di atas.

### 2. Instal dependensi

Jalankan perintah berikut dari **direktori root proyek** (tempat `requirements.txt` berada):

```bash
pip install -r requirements.txt
```

### 3. Masuk ke direktori `dashboard/`

> **Penting:** Dashboard harus dijalankan dari dalam folder `dashboard/` agar pembacaan file CSV tidak mengalami kesalahan path.

```bash
cd dashboard
```

### 4. Jalankan dashboard Streamlit

```bash
streamlit run dashboard.py
```

Dashboard akan otomatis terbuka di browser pada alamat `http://localhost:8501`.

---

### Alternatif: menjalankan dari direktori root proyek

Jika tidak ingin berpindah direktori, gunakan perintah berikut dari direktori root:

```bash
streamlit run dashboard/dashboard.py
```

> Meskipun perintah di atas berhasil memulai server, pembacaan file CSV di dalam `dashboard.py` menggunakan `os.path.dirname(os.path.abspath(__file__))` sehingga path file CSV selalu dihitung relatif terhadap lokasi `dashboard.py`, **bukan** terhadap direktori kerja saat perintah dijalankan. Kedua cara di atas aman digunakan.

---

## Fitur Interaktif Dashboard

Filter pada setiap halaman bersifat **independen** — saat berpindah halaman, filter yang ditampilkan di sidebar akan berubah sesuai konteks analisis halaman tersebut.

### Halaman 1: Overview & RFM Analysis
| Filter | Tipe | Deskripsi |
|--------|------|-----------|
| Segmen Pelanggan | `st.multiselect` | Pilih segmen: VIP/Champions, At-Risk/Lost, New/Low Spender, Potential Loyalist/Active |
| Rentang Recency | `st.slider` | Rentang hari sejak transaksi terakhir pelanggan |
| Rentang Total Belanja | `st.slider` | Rentang nilai Monetary pelanggan (R$) |

### Halaman 2: Logistik & Geografis
| Filter | Tipe | Deskripsi |
|--------|------|-----------|
| Wilayah Pelanggan (State) | `st.multiselect` | Pilih satu atau beberapa negara bagian Brazil |
| Rentang Keterlambatan | `st.slider` | Filter berdasarkan rentang nilai keterlambatan pengiriman (hari) |

### Halaman 3: Kualitas Produk (Reviews)
| Filter | Tipe | Deskripsi |
|--------|------|-----------|
| Kategori Produk | `st.multiselect` | Pilih kategori produk yang ingin dianalisis |
| Rentang Skor Ulasan | `st.select_slider` | Filter berdasarkan bintang ulasan (1–5) |
| Rentang Harga Produk | `st.slider` | Filter berdasarkan rentang harga produk (R$) |

---

## Periode Data

Analisis mencakup data transaksi **Januari 2017 – Agustus 2018** dari dataset Brazilian E-Commerce Public Dataset by Olist.
