# Backend Flask - Sistem Donor Darah

Aplikasi backend Flask untuk sistem manajemen donor darah dengan fitur CRUD untuk pendonor, permohonan darah, dan berita.

## Fitur

- **Authentication**: Login dan register dengan JWT
- **Pendonor Management**: CRUD operasi untuk data pendonor
- **Permohonan Management**: CRUD operasi untuk permohonan darah
- **Berita Management**: CRUD operasi untuk berita
- **Protected Routes**: Endpoint yang memerlukan autentikasi
- **User Isolation**: Setiap user hanya dapat mengakses data miliknya sendiri

## Struktur Database

### Tabel Users

- `user_id` (Primary Key)
- `username`
- `email`
- `password` (hashed)
- `role` (admin/user)

### Tabel Pendonor

- `pendonor_id` (Primary Key)
- `user_id` (Foreign Key)
- `nama`
- `alamat`
- `golongan_darah` (A-, A+, B-, B+, AB-, AB+, O-, O+)
- `created_at`
- `update_at`

### Tabel Permohonan

- `permohonan_id` (Primary Key)
- `user_id` (Foreign Key)
- `lokasi`
- `golongan_darah`
- `jml_darah_ml`
- `jml_darah_sekarang`
- `status` (Tercapai/Belum Tercapai)
- `created_at`
- `update_at`

### Tabel Berita

- `berita_id` (Primary Key)
- `user_id` (Foreign Key)
- `judul_berita`
- `deskripsi_berita`
- `url_image`

## API Endpoints

### Authentication

- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/register` - Register user baru

### Pendonor

- `GET /api/v1/pendonor` - Ambil semua data pendonor milik user
- `GET /api/v1/pendonor/{id}` - Ambil data pendonor berdasarkan ID
- `POST /api/v1/pendonor/create` - Buat pendonor baru
- `PUT /api/v1/pendonor/update/{id}` - Update data pendonor
- `DELETE /api/v1/pendonor/delete/{id}` - Hapus data pendonor

### Permohonan

- `GET /api/v1/permohonan` - Ambil semua data permohonan milik user
- `GET /api/v1/permohonan/{id}` - Ambil data permohonan berdasarkan ID
- `POST /api/v1/permohonan/create` - Buat permohonan baru
- `PUT /api/v1/permohonan/update/{id}` - Update data permohonan
- `DELETE /api/v1/permohonan/delete/{id}` - Hapus data permohonan

### Berita

- `GET /api/v1/berita` - Ambil semua data berita milik user
- `GET /api/v1/berita/{id}` - Ambil data berita berdasarkan ID
- `POST /api/v1/berita/create` - Buat berita baru
- `PUT /api/v1/berita/update/{id}` - Update data berita
- `DELETE /api/v1/berita/delete/{id}` - Hapus data berita

### Protected Data

- `GET /api/v1/protected/data` - Data yang memerlukan autentikasi

## Instalasi

1. Clone repository ini
2. Buat virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # atau
   venv\Scripts\activate  # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Setup database:

   - Import file `stuff/db_donor.sql` ke MySQL
   - Buat file `.env` dengan konfigurasi database

5. Jalankan aplikasi:
   ```bash
   python app.py
   ```

## Environment Variables

Buat file `.env` dengan konfigurasi berikut:

```
# Flask Configuration
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ACCESS_TOKEN_EXPIRES=3600

# Database Configuration
DB_HOST=localhost
DB_NAME=db_donor
DB_USER=your_db_username
DB_PASSWORD=your_db_password
DB_POOL_NAME=donor_pool
POOL_SIZE=5
```

## Testing dengan Postman

Gunakan collection Postman yang tersedia di `stuff/db_backendDonor.postman_collection.json`

1. Import collection ke Postman
2. Set environment variable `flask_local` dengan URL aplikasi (contoh: `http://localhost:5000`)
3. Test endpoint sesuai kebutuhan

## Keamanan

- Semua endpoint (kecuali login/register) memerlukan JWT token
- Password di-hash menggunakan bcrypt
- Validasi input untuk semua endpoint
- User hanya dapat mengakses data miliknya sendiri
- Setiap request memverifikasi kepemilikan data berdasarkan user_id

## Perubahan Logika Endpoint

### Get All Data

- Sekarang hanya menampilkan data milik user yang sedang login
- Menggunakan `user_id` dari JWT token untuk filter

### Get By ID

- Menambahkan endpoint untuk mengambil data berdasarkan ID
- Memverifikasi bahwa data tersebut milik user yang sedang login

### Create/Update/Delete

- Semua operasi memverifikasi kepemilikan data
- User tidak dapat mengakses atau memodifikasi data user lain
- ID sekarang diambil dari parameter URL, bukan dari form/query

## Contoh Penggunaan

### Update Pendonor

```bash
PUT /api/v1/pendonor/update/1
Content-Type: application/x-www-form-urlencoded

nama=John Doe&alamat=Jakarta&golongan_darah=A+
```

### Delete Permohonan

```bash
DELETE /api/v1/permohonan/delete/5
Authorization: Bearer <jwt_token>
```

### Get Berita by ID

```bash
GET /api/v1/berita/3
Authorization: Bearer <jwt_token>
```

## Struktur Project

```
BackEndFlask/
├── api/
│   ├── auth/
│   ├── berita/
│   ├── dataprotected/
│   ├── pendonor/
│   └── permohonan/
├── helper/
├── static/
├── stuff/
├── app.py
├── config.py
├── extensions.py
└── requirements.txt
```
