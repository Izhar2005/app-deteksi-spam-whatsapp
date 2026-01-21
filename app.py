import streamlit as st
import ahocorasick
from flask import Flask, request
import threading
import time
import os
import json
import re

# --- 1. KONFIGURASI DATABASE KATA KUNCI ---
keywords_list = [
    "menang", "hadiah", "undian", "selamat", "pemenang", "jackpot", "rejeki", "kejutan",
    "terpilih", "cek tunai", "saldo", "voucher", "kode unik", "pin pemenang", "gebyar",
    "pesta", "mobil", "motor", "shopee", "lazada", "tokopedia", "whatsapp", "resmi",
    "ambil hadiah", "pemenang undian", "hadiah gratis", "tanpa diundi", "klaim hadiah",
    "pinjaman", "dana", "cair", "cepat", "tanpa jaminan", "bunga rendah", "kredit",
    "tenor", "kta", "modal", "hutang", "fintech", "ojk", "angsuran", "butuh uang",
    "solusi keuangan", "limit", "proses kilat", "syarat mudah", "gadai", "investasi",
    "profit", "trading", "saham", "crypto", "binomo", "lotere", "transfer", "rekening",
    "biaya admin", "pajak", "pinjaman online", "dana cepat", "investasi bodong",
    "promo", "diskon", "sale", "murah", "cuci gudang", "terbatas", "stok", "order",
    "beli", "belanja", "hemat", "penawaran", "eksklusif", "member", "katalog",
    "gratis ongkir", "cashback", "flash sale", "harga miring", "rebutan", "borong"
]

phishing_triggers = ["klik", "link", "bit.ly", "http", "https", "verifikasi", "login", "buka", "kunjungi", "www"]

@st.cache_resource
def build_automaton(words, triggers):
    A = ahocorasick.Automaton()
    for idx, key in enumerate(list(set(words + triggers))):
        A.add_word(key.lower(), (idx, key))
    A.make_automaton()
    return A

automaton = build_automaton(keywords_list, phishing_triggers)

# --- 2. SISTEM PENYIMPANAN & BACKUP ---
LOG_FILE = "wa_incoming_messages.txt"
SPAM_COUNT_FILE = "spam_counts.json"
BACKUP_FOLDER = "backup_logs"

# Pastikan folder backup tersedia
if not os.path.exists(BACKUP_FOLDER):
    os.makedirs(BACKUP_FOLDER)

def load_spam_counts():
    try:
        if os.path.exists(SPAM_COUNT_FILE):
            with open(SPAM_COUNT_FILE, "r") as f:
                return json.load(f)
    except: pass
    return {}

def save_spam_counts(counts):
    with open(SPAM_COUNT_FILE, "w") as f:
        json.dump(counts, f)

def save_to_file(data_string):
    try:
        # Simpan ke Log Utama
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(data_string + "\n")
            
        # --- KODE BACKUP KE TXT ---
        # Membuat file backup harian (Contoh: backup_20260118.txt)
        backup_name = f"backup_{time.strftime('%Y%m%d')}.txt"
        backup_path = os.path.join(BACKUP_FOLDER, backup_name)
        with open(backup_path, "a", encoding="utf-8") as f_backup:
            f_backup.write(data_string + "\n")
            
    except Exception as e:
        print(f"Gagal menulis file log/backup: {e}")

def read_from_file():
    if not os.path.exists(LOG_FILE): return []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return f.readlines()
    except: return []

# --- 3. BACKEND FLASK ---
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        pengirim = request.form.get('sender') or request.form.get('device') or "Unknown"
        pesan = request.form.get('message') or request.form.get('pesan') or ""
        
        if not pesan:
            data_json = request.get_json(silent=True)
            if data_json:
                pengirim = data_json.get('sender') or data_json.get('device') or pengirim
                pesan = data_json.get('message') or data_json.get('pesan') or pesan

        if not pesan: return "Pesan Kosong", 200

        pesan_low = pesan.lower()
        found_all = [val for _, (_, val) in automaton.iter(pesan_low)]
        unique_found = list(set(found_all))
        keywords_only = [w for w in unique_found if w in keywords_list]
        jumlah_keyword = len(keywords_only)

        is_link_present = any(p in pesan_low for p in phishing_triggers) or re.search(r'(https?://\S+|www\.\S+|bit\.ly/\S+)', pesan_low)

        # LOGIKA STATUS
        status = "AMAN"
        if is_link_present and len(unique_found) >= 1:
            status = "🚨 POTENSI PHISHING"
        elif jumlah_keyword == 2:
            status = "POTENSI SPAM"
        elif jumlah_keyword >= 3:
            status = "SPAM"

        # Update Counter
        if status != "AMAN" and pengirim != "Unknown":
            counts = load_spam_counts()
            counts[pengirim] = counts.get(pengirim, 0) + 1
            save_spam_counts(counts)

        waktu_tampil = time.strftime("%H:%M:%S")
        kata_kunci_str = ", ".join(unique_found) if unique_found else "-"
        isi_pesan_safe = pesan.replace("|", " ").replace("\n", " ")
        
        log_entry = f"{waktu_tampil}|{status}|{pengirim}|{kata_kunci_str}|{isi_pesan_safe}"
        save_to_file(log_entry)

        return "OK", 200
    except Exception as e:
        print(f"Error Webhook: {e}")
        return "Internal Error", 500

def run_flask():
    app.run(port=5000, debug=False, use_reloader=False)

if "flask_thread" not in st.session_state:
    thread = threading.Thread(target=run_flask, daemon=True)
    thread.start()
    st.session_state.flask_thread = True

# --- 4. ANTARMUKA STREAMLIT ---
st.set_page_config(page_title="WA Spam & Phishing Guard", layout="wide")
st.title("🛡️ Deteksi Spam & Analisis Phishing Real-time")

col_main, col_side = st.columns([2, 1])

with col_main:
    st.subheader("📬 Log Pesan Terkini")
    if st.button("🗑️ Reset Log & Counter"):
        if os.path.exists(LOG_FILE): os.remove(LOG_FILE)
        if os.path.exists(SPAM_COUNT_FILE): os.remove(SPAM_COUNT_FILE)
        st.rerun()

    raw_logs = read_from_file()
    if not raw_logs:
        st.info("Menunggu pesan masuk dari WhatsApp...")
    else:
        for line in reversed(raw_logs):
            parts = line.strip().split("|")
            if len(parts) < 5: continue
            w_time, stts, sender, keys, msg = parts
            
            with st.container(border=True):
                warna = "red" if "PHISHING" in stts or stts == "SPAM" else "orange" if "POTENSI" in stts else "green"
                st.markdown(f"**Status: :{warna}[{stts}]**")
                st.write(f"Nomor: `{sender}` | Jam: {w_time}")
                st.write(f"Isi: {msg}")
                st.caption(f"Pola Terdeteksi: {keys}")

with col_side:
    st.subheader("⚠️ Daftar Nomor Waspada")
    current_spam_counts = load_spam_counts()
    waspada_list = {k: v for k, v in current_spam_counts.items() if v >= 6}
    
    if not waspada_list:
        st.success("Belum ada nomor mencurigakan.")
    else:
        for nomor, jumlah in waspada_list.items():
            st.warning(f"📱 **{nomor}**\nTotal Pelanggaran: {jumlah} kali")
    
    st.divider()
    st.subheader("📂 Status Backup")
    # Menampilkan informasi backup di sidebar
    files = os.listdir(BACKUP_FOLDER)
    st.caption(f"Folder Backup: `/{BACKUP_FOLDER}`")
    st.caption(f"Jumlah File Backup: {len(files)}")
    st.caption("Algoritma: String Matching Aho-Corasick")

time.sleep(5)
st.rerun()
