#  WA Spam & Phishing Guard (Aho-Corasick Based)

Aplikasi deteksi spam dan phishing pesan teks secara real-time yang memanfaatkan efisiensi algoritma **Aho-Corasick**. Sistem ini mengintegrasikan WhatsApp melalui Fonnte API Gateway dan Flask Webhook untuk memberikan perlindungan instan terhadap ancaman siber.

## Fitur Utama
- [cite_start]**Real-time Detection**: Memproses pesan masuk secara instan melalui integrasi Webhook[cite: 83].
- [cite_start]**Aho-Corasick Engine**: Menggunakan algoritma string matching multi-pola untuk pemindaian dataset luas dengan kompleksitas waktu linier $O(n + m)$[cite: 34, 41].
- [cite_start]**Phishing Analysis**: Deteksi tautan (URL) mencurigakan menggunakan Regular Expression (Regex)[cite: 48, 98].
- [cite_start]**Multi-level Classification**: Mengklasifikasikan pesan ke dalam kategori AMAN, POTENSI SPAM, SPAM, dan POTENSI PHISHING[cite: 49, 58].
- [cite_start]**Dashboard Monitoring**: Visualisasi log pesan dan status keamanan menggunakan Streamlit[cite: 40, 81].
- [cite_start]**Auto-Backup System**: Pencadangan otomatis log pesan ke folder permanen untuk integritas data[cite: 77, 83].
- [cite_start]**Sender Reputation**: Melacak jumlah pelanggaran dari setiap nomor pengirim (Daftar Nomor Waspada)[cite: 90].

## 🛠️ Arsitektur Sistem
Sistem ini bekerja melalui beberapa lapisan integrasi:
1. [cite_start]**Fonnte API**: Menerima pesan WhatsApp dan meneruskannya ke Webhook[cite: 95].
2. **Ngrok**: Melakukan tunneling agar localhost dapat diakses oleh server publik Fonnte.
3. [cite_start]**Flask (Backend)**: Menerima data, melakukan normalisasi teks, dan menjalankan mesin algoritma[cite: 40, 45].
4. [cite_start]**Streamlit (Frontend)**: Menampilkan hasil analisis secara visual kepada pengguna[cite: 40, 89].



## 📋 Prasyarat
Sebelum menjalankan aplikasi, pastikan Anda memiliki:
- Python 3.8+
- Akun [Fonnte](https://fonnte.com) (untuk integrasi WhatsApp)
- [Ngrok](https://ngrok.com/) (untuk tunneling localhost)

## 🔧 Instalasi
1. Clone repositori ini:
   ```bash
   git clone [https://github.com/username/wa-spam-guard.git](https://github.com/username/wa-spam-guard.git)
   cd wa-spam-guard

   Instal library yang dibutuhkan:

Bash
pip install streamlit flask pyahocorasick
Jalankan aplikasi:

Bash
python -m streamlit run app.py

Kategori,Contoh Pesan,Status
Aman,"""Besok kita rapat jam 10 pagi di kantor""",AMAN 
Spam,"""Selamat Anda memenangkan hadiah undian mobil gratis""",SPAM 
Phishing,"""Klik link berikut untuk verifikasi akun Anda http://bit.ly/xxx""",POTENSI PHISHING 

Referensi & Akademik
Proyek ini dikembangkan sebagai tugas mata kuliah Desain dan Analisis Algoritma di Universitas Muhammadiyah Makassar. Algoritma Aho-Corasick dipilih karena performanya yang stabil dan ringan dibandingkan metode Deep Learning dalam pemrosesan teks real-time.

Kontributor:

Andi Hilyatul Mar’ah (105841109023) 

Izhar (105841109323) 


---

### Tips Sebelum Mengunggah ke GitHub:
1. **File `.gitignore`**: Buat file bernama `.gitignore` dan masukkan teks berikut agar file sampah tidak ikut terunggah:
   ```text
   __pycache__/
   .streamlit/
   backup_logs/
   wa_incoming_messages.txt
   spam_counts.json
   .env
   
