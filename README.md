# Backend Flask - Sistem Donor Darah

Aplikasi backend Flask untuk sistem manajemen donor darah dengan fitur CRUD untuk pendonor, permohonan darah, dan berita.

---

## 🚀 Quick Start

1. **Clone repository**
   ```bash
   git clone https://github.com/suryanation88/SedarahBackEnd.git
   cd BackEndFlask
   ```
2. **Buat virtual environment & aktifkan**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Setup database**
   - Import file `stuff/db_donor.sql` ke MySQL
   - Buat file `.env` (lihat contoh di bawah)
5. **Jalankan aplikasi**
   ```bash
   python app.py
   ```
6. **Cek API**
   - Buka Postman/Insomnia, gunakan collection di `stuff/db_backendDonor.postman_collection.json`
   - Set environment variable `flask_local` ke `http://localhost:5000`

---

## 🗂️ Struktur Project

```
BackEndFlask/
├── api/                # Semua endpoint API
│   ├── auth/           # Login & register
│   ├── berita/         # CRUD berita
│   ├── dataprotected/  # Endpoint protected
│   ├── donor_respons/  # Respon donor
│   ├── komentar/       # CRUD komentar
│   ├── pendonor/       # CRUD pendonor
│   ├── permohonan/     # CRUD permohonan
│   ├── profile/        # CRUD profile user
│   └── __init__.py
├── helper/             # Helper functions (JWT, DB, validasi)
├── static/             # Static file server
├── stuff/              # File SQL & Postman collection
├── uploads/            # Upload file/image
├── app.py              # Entry point aplikasi
├── config.py           # Konfigurasi
├── extensions.py       # Ekstensi Flask
├── requirements.txt    # Daftar dependensi
└── README.md
```

---

## 🔑 Contoh .env

```
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ACCESS_TOKEN_EXPIRES=3600
DB_HOST=localhost
DB_NAME=db_donor
DB_USER=your_db_username
DB_PASSWORD=your_db_password
DB_POOL_NAME=donor_pool
POOL_SIZE=5
```

---

## 🛠️ Troubleshooting

- **Error: Cannot connect to database**
  - Pastikan MySQL sudah berjalan & konfigurasi .env sudah benar
  - Cek user/password MySQL
- **Error: ModuleNotFoundError**
  - Pastikan sudah install requirements: `pip install -r requirements.txt`
- **Error: JWT token invalid/expired**
  - Login ulang untuk mendapatkan token baru

---

---

## 📚 Fitur

- **Authentication**: Login dan register dengan JWT
- **Pendonor Management**: CRUD operasi untuk data pendonor
- **Permohonan Management**: CRUD operasi untuk permohonan darah
- **Berita Management**: CRUD operasi untuk berita
- **Protected Routes**: Endpoint yang memerlukan autentikasi
- **User Isolation**: Setiap user hanya dapat mengakses data miliknya sendiri

---

## 🗄️ Struktur Database

### Tabel users

- `user_id` (Primary Key, int, AUTO_INCREMENT)
- `username` (varchar(100), NOT NULL)
- `email` (varchar(100), NOT NULL, UNIQUE)
- `password` (varchar(255), NOT NULL)
- `nama` (varchar(155), NOT NULL)
- `domisili` (varchar(255), NOT NULL)
- `golongan_darah` (enum: A-, A+, B-, B+, AB-, AB+, O-, O+, NOT NULL)
- `photo_path` (varchar(255), NULL)
- `no_telp` (int, NOT NULL)
- `status_pendonor` (enum: Rutin, Baru, default Baru)
- `role` (enum: admin, user, default user)
- `created_at` (timestamp, default CURRENT_TIMESTAMP)
- `update_at` (timestamp, default CURRENT_TIMESTAMP ON UPDATE)

### Tabel berita

- `berita_id` (Primary Key, int, AUTO_INCREMENT)
- `user_id` (Foreign Key ke users)
- `judul_berita` (varchar(255))
- `deskripsi_berita` (varchar(255))
- `url_image` (varchar(255))

### Tabel donor_respons

- `donor_id` (Primary Key, int, AUTO_INCREMENT)
- `user_id` (Foreign Key ke users, int, NOT NULL)
- `permohonan_id` (Foreign Key ke permohonan, int, NOT NULL)
- `status` (enum: DIKONFIRMASI, DIBATALKAN, SELESAI, default DIKONFIRMASI)
- `tanggal_donor` (date, NULL)
- `created_at` (timestamp, default CURRENT_TIMESTAMP)

### Tabel komentar

- `komentar_id` (Primary Key, int, AUTO_INCREMENT)
- `user_id` (Foreign Key ke users)
- `nama` (varchar(255))
- `deskripsi` (varchar(255))

### Tabel permohonan

- `permohonan_id` (Primary Key, int, AUTO_INCREMENT)
- `user_id` (Foreign Key ke users)
- `nama_pasien` (varchar(255))
- `kabupaten` (enum: Gianyar, Tabanan, Bangli, Buleleng, Denpasar, Badung, Klungkung, Karangasem, Jembrana)
- `rumah_sakit` (varchar(255))
- `golongan_darah` (enum: A, B, AB, O, NOT NULL)
- `rhesus` (enum: +, -, NOT NULL)
- `jml_pendonor` (int)
- `nama_pemohon` (varchar(255), NOT NULL)
- `no_telp` (int, NOT NULL)
- `status` (enum: Selesai, Belum selesai, default Belum selesai)
- `tanggal_kebutuhan` (date, NOT NULL)
- `created_at` (timestamp, default CURRENT_TIMESTAMP)
- `update_at` (timestamp, default CURRENT_TIMESTAMP ON UPDATE)

### Tabel stok_darah

- `stok_id` (Primary Key, int, AUTO_INCREMENT)
- `wilayah` (enum: Gianyar, Tabanan, Bangli, Buleleng, Denpasar, Badung, Klungkung, Karangasem, Jembrana)
- `kapasitas_total` (int, NOT NULL)
- `jumlah_tersedia` (int, NOT NULL)
- `updated_at` (timestamp, default CURRENT_TIMESTAMP ON UPDATE)

---
