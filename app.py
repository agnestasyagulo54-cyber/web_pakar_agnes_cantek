import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.express as px
import time
import io

# ====== CONFIG ======
st.set_page_config(page_title="Sistem Pakar", layout="wide")

# ====== STYLE ======
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: #e2e8f0;
}

/* HEADER CENTER */
.header-container {
    display: flex;
    justify-content: center;
    text-align: center;
    margin-top: 20px;
    margin-bottom: 25px;
}

.header-title {
    font-size: 34px;
    font-weight: 700;
    color: #22c55e;
}

.header-sub {
    font-size: 15px;
    color: #94a3b8;
}

/* CARD */
.card {
    background: #1e293b;
    padding: 16px;
    border-radius: 14px;
    margin-top: 10px;
    border: 1px solid #334155;
}

.main-card {
    border: 2px solid #22c55e;
    background: #052e2b;
}

.alert-card {
    border: 2px solid #ef4444;
    background: #450a0a;
    color: #fca5a5;
    padding: 16px;
    border-radius: 14px;
    margin-top: 10px;
}

/* BUTTON UTAMA (Biru) */
.stButton > button {
    border-radius: 10px;
    background: #2563eb;
    color: white;
    border: none;
    padding: 8px 16px;
    font-weight: bold;
    transition: all 0.3s;
}
.stButton > button:hover {
    background: #1d4ed8;
}

/* Tombol Hapus Khusus (Merah) */
button[data-testid^="stButton"][key*="del_btn"] > button {
    background-color: #ef4444 !important;
    padding: 5px 10px;
    font-size: 14px;
}
button[data-testid^="stButton"][key*="del_btn"] > button:hover {
    background-color: #dc2626 !important;
}

/* PROGRESS */
.stProgress > div > div {
    background-color: #22c55e;
}

/* Plotly Chart Background Transparan */
.js-plotly-plot .plotly .main-svg {
    background: transparent !important;
}
</style>
""", unsafe_allow_html=True)

# ====== HEADER ======
st.markdown("""
<div class="header-container">
    <div>
        <div class="header-title">🧠 Sistem Pakar</div>
        <div class="header-sub">Diagnosis Penyakit Berbasis Certainty Factor</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ====== INIT ======
if "history" not in st.session_state:
    st.session_state.history = []

# Inisialisasi flag clear untuk mereset tampilan
if "clear_flag" not in st.session_state:
    st.session_state.clear_flag = False

if st.session_state.clear_flag:
    st.session_state.clear_flag = False

# ====== DATA GEJALA (Basis Pengetahuan - CF Pakar) ======
knowledge_cf = {
    "Influenza": {"demam": 0.8, "batuk": 0.7, "pilek": 0.6},
    "Tifus": {"demam": 0.9, "lemas": 0.7, "mual": 0.6},
    "Maag": {"mual": 0.8, "nyeri perut": 0.9, "perih": 0.7},
    "DBD": {"demam tinggi": 0.9, "bintik merah": 0.8, "lemas": 0.7},
    "Hipertensi": {"pusing": 0.7, "tekanan darah tinggi": 0.9},
    "Varicella (Cacar Air)": {"bintik berair": 0.9, "gatal": 0.8, "demam": 0.6},
    "Covid-19": {"hilang penciuman": 0.9, "sesak napas": 0.8, "batuk kering": 0.7},
    "Diabetes": {"sering kencing": 0.8, "sering haus": 0.7, "berat badan turun": 0.7}
}

# ============================================================
# ====== BAGIAN DETAIL, FOTO & PERINGATAN KHUSUS ========
# ============================================================
detail = {
    "Influenza": {
        "penyebab": "Virus influenza", 
        "obat": "Paracetamol", 
        "makanan_baik": "Sup, buah", 
        "makanan_hindari": "Gorengan",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSas9pwpexBiA29P96fGTJ67eDpGrGgVbrFDA&s",
        "peringatan": None 
    },
    "Tifus": {
        "penyebab": "Bakteri Salmonella typhi", 
        "obat": "Antibiotik (Kloramfenikol)", 
        "makanan_baik": "Bubur, makanan lembut", 
        "makanan_hindari": "Makanan pedas, berserat kasar",
        "image_url": "https://lh5.googleusercontent.com/proxy/5cV2KCl1IRtaqYILmb6ZUgK7kegzCQGP0SQ03v5Wj_WfV0TilnlTteTCb6Dh2D_B2ePLRW-NJHTikAb1YSa8l4g9ZTOIAECyxo7em2R0CmTPyTFee-HEzo-KgltCALW_83hOsF-MCXI0N92rLXjdBqMV_ZSOmOhyke-0RwQQsmIqF1ZJuI-crzU",
        "peringatan": "⚠️ Harap segera ke dokter. Tifus dapat menyebabkan komplikasi serius jika tidak diobati dengan antibiotik tepat waktu."
    },
    "Maag": {
        "penyebab": "Asam lambung naik", 
        "obat": "Antasida (Promag, Maalox)", 
        "makanan_baik": "Makanan lembut, pisang", 
        "makanan_hindari": "Kopi, soda, makanan asam",
        "image_url": "https://pfimegalife.co.id/literasi-keuangan/cfind/source/images/site/libraries/FolderBaru/penyakit_maag.jpg",
        "peringatan": None
    },
    "DBD": {
        "penyebab": "Virus Dengue (Nyamuk Aedes aegypti)", 
        "obat": "Penanganan suportif (Paracetamol, cairan infus)", 
        "makanan_baik": "Jus jambu biji, air kelapa", 
        "makanan_hindari": "Soda, makanan berwarna merah (salak)",
        "image_url": "https://www.cegahdbd.com/sites/default/files/styles/large/public/2022-04/im2.png?itok=6xBiDciV",
        "peringatan": "🚨 PERINGATAN KRITIS! Jika mengalami demam tinggi lebih dari 3 hari, pendarahan, atau nyeri perut hebat, segera ke UGD."
    },
    "Hipertensi": {
        "penyebab": "Tekanan darah tinggi", 
        "obat": "Amlodipine, Captopril", 
        "makanan_baik": "Sayuran hijau, buah-buahan", 
        "makanan_hindari": "Makanan asin, gorengan, makanan kaleng",
        "image_url": "https://unair.ac.id/wp-content/uploads/2021/10/Foto-dari-LifepackID.jpg",
        "peringatan": "⚠️ Hindari stres berat. Rutin cek tekanan darah."
    },
    "Varicella (Cacar Air)": {
        "penyebab": "Virus Varicella zoster", 
        "obat": "Acyclovir (salep/obat minum)", 
        "makanan_baik": "Makanan halus, buah", 
        "makanan_hindari": "Makanan pedas, seafood",
        "image_url": "https://static.rsmurniteguh.app/prod/artikel/2023/10/gor96-a.jpg",
        "peringatan": "⚠️ Jangan menggaruk bintik air agar tidak terinfeksi bakteri."
    },
    "Covid-19": {
        "penyebab": "Virus SARS-CoV-2", 
        "obat": "Obat gejala (Paracetamol, vitamin)", 
        "makanan_baik": "Makanan bergizi tinggi, sup ayam", 
        "makanan_hindari": "Makanan berlemak, alkohol",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRA838oI3ItFGfNWgjOFbEpN86OKmK1_x4RRw&s",
        "peringatan": "🦠 Lakukan isolasi mandiri jika hasil tes positif. Gunakan masker."
    },
    "Diabetes": {
        "penyebab": "Kadar gula darah tinggi", 
        "obat": "Metformin, Insulin", 
        "makanan_baik": "Sayuran, karbohidrat kompleks", 
        "makanan_hindari": "Gula, nasi putih, roti putih",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR8yDY5kDxmS6V2OAKRV6txYGjIWhQRI7HsOg&s",
        "peringatan": "⚠️ Harap kontrol rutin ke dokter penyakit dalam."
    }
}
# ============================================================

# ====== FUNGSI UNTUK MENAMPILKAN DETAIL (GABUNGAN) ======
def show_disease_detail(penyakit_nama):
    """Menampilkan detail penyakit (Info & Foto dalam satu tampilan)"""
    data = detail.get(penyakit_nama)
    if not data:
        st.warning("Data detail tidak ditemukan.")
        return

    # Tampilkan Peringatan Khusus jika ada
    if data.get("peringatan"):
        st.markdown(f"""
        <div class="alert-card">
        {data["peringatan"]}
        </div>
        """, unsafe_allow_html=True)

    # Tampilkan Info Teks
    st.markdown(f"""
    <div class="card main-card">
    <b>{penyakit_nama}</b><br><br>
    <b>🦠 Penyebab:</b><br>{data["penyebab"]}<br><br>
    <b>💊 Obat:</b><br>{data["obat"]}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card">
    <b>✅ Makanan Disarankan:</b><br>{data["makanan_baik"]}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card">
    <b>❌ Makanan Dihindari:</b><br>{data["makanan_hindari"]}
    </div>
    """, unsafe_allow_html=True)

    # Tampilkan Foto (Langsung di bawah, tanpa Tab)
    st.markdown("<br>", unsafe_allow_html=True) 
    if data.get("image_url"):
        st.image(data["image_url"], caption=f"Ilustrasi {penyakit_nama}", width=400)
    else:
        st.info("Tidak ada foto untuk penyakit ini.")

# ====== SIDEBAR ======
with st.sidebar:
    st.header("📋 Menu")

    st.write("Sistem Pakar Diagnosis")

    # FITUR BARU 3: Export Data ke CSV
    if st.session_state.history:
        df_export = pd.DataFrame(st.session_state.history)
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Riwayat (CSV)",
            data=csv,
            file_name=f'riwayat_diagnosa_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv',
        )
        st.markdown("---")

    # Tombol Hapus SEMUA
    if st.button("🗑️ Hapus Semua Riwayat"):
        st.session_state.history = []
        st.rerun()

    st.markdown("---")
    st.subheader("📜 Riwayat Diagnosis")

    if st.session_state.history:
        total_history = len(st.session_state.history)
        
        for idx, h in enumerate(st.session_state.history[::-1]): 
            real_index = total_history - 1 - idx
            
            col_info, col_del = st.columns([4, 1])

            with col_info:
                if st.button(f"📅 {h['waktu']} - {h['hasil']}", key=f"hist_btn_{real_index}", help="Klik untuk lihat detail"):
                    st.session_state.show_detail = h['hasil']
                st.caption(f"👤 {h['nama']} | {h['skor']:.0f}%")
            
            with col_del:
                if st.button("❌", key=f"del_btn_{real_index}", help="Hapus riwayat ini"):
                    del st.session_state.history[real_index]
                    st.rerun()
            
            st.markdown("---")
    else:
        st.caption("Bagian riwayat kosong.")

# ====== MODAL DETAIL ======
if 'show_detail' in st.session_state and st.session_state.show_detail:
    st.markdown("---")
    st.subheader(f"🔍 Detail Riwayat: {st.session_state.show_detail}")
    show_disease_detail(st.session_state.show_detail)
    
    if st.button("✅ Tutup Detail"):
        del st.session_state.show_detail
        st.rerun()
    st.markdown("---")

# ====== LAYOUT UTAMA ======
# Kita menggunakan form atau pengelolaan state untuk handle "Clear" agar tampilan bersih saat tombol ditekan

# Reset input jika flag clear aktif
if st.session_state.clear_flag:
    st.session_state.clear_flag = False
    # Force rerun agar UI bersih
    st.rerun()

left, right = st.columns([2, 1])

with left:
    st.subheader("📝 Input Gejala Pasien")
    
    # Input Nama
    nama_pasien = st.text_input("Masukkan Nama Pasien:", placeholder="Contoh: Budi")
    
    all_gejala = sorted({g for p in knowledge_cf.values() for g in p})
    
    # FITUR BARU 1: Input Keyakinan User (CF User)
    st.markdown("#### 1. Pilih Gejala:")
    gejala_dipilih = st.multiselect("Tandai gejala yang dialami:", all_gejala)
    
    cf_user_map = {} # Dictionary untuk menyimpan keyakinan user
    
    if gejala_dipilih:
        st.markdown("#### 2. Seberapa yakin Anda dengan gejala tersebut?")
        st.caption("Sesuaikan tingkat keyakinan untuk akurasi diagnosa yang lebih baik.")
        
        for g in gejala_dipilih:
            # Slider/select untuk input CF User (0.1 - 1.0)
            cf_val = st.slider(f"Yakin mengalami: **{g}**?", 0.1, 1.0, 0.5, 0.1, key=f"cf_{g}")
            cf_user_map[g] = cf_val

    col1, col2 = st.columns(2)
    diagnosa = col1.button("🔍 Mulai Diagnosa", use_container_width=True)
    clear = col2.button("❌ Clear", use_container_width=True)

# Membuat placeholder kosong
hasil_placeholder = st.empty()

# ====== AKSI CLEAR (RESET SEMUA) ======
if clear:
    # Hapus semua input user
    for key in list(st.session_state.keys()):
        if key.startswith("cf_") or key in ["nama_pasien"]:
            del st.session_state[key]

    # Kosongkan hasil tampilan
    hasil_placeholder.empty()

    # Reset flag
    st.session_state.clear_flag = True

    # Reload halaman
    st.rerun()


# ====== PROSES LOGIC (UPDATED DENGAN CF USER) ======
if diagnosa:
    if gejala_dipilih:
        with hasil_placeholder.container(): 
            with st.spinner("🔍 Menganalisis gejala..."):
                time.sleep(1.5) 

            hasil = []

            # Perhitungan Certainty Factor (CF Combine)
            for penyakit, gejala_pakar in knowledge_cf.items():
                cf_total = 0
                for g in gejala_dipilih:
                    if g in gejala_pakar:
                        # Ambil CF Pakar dari data
                        cf_pakar = gejala_pakar[g]
                        # Ambil CF User dari slider (default 1.0 jika user tidak ubah, tapi di sini kita pakai slider)
                        cf_user = cf_user_map.get(g, 1.0)
                        
                        # Rumus: CF = CF_Pakar * CF_User
                        cf_hybrid = cf_pakar * cf_user
                        
                        # Rumus Combine CF
                        cf_total = cf_total + cf_hybrid * (1 - cf_total)

                if cf_total > 0:
                    hasil.append((penyakit, cf_total * 100))

            # Urutkan dari skor tertinggi
            hasil = sorted(hasil, key=lambda x: x[1], reverse=True)

            # Jika ada hasil
            if hasil:
                penyakit_utama = hasil[0][0]
                skor_utama = hasil[0][1]

                with left:
                    st.subheader("📊 Hasil Diagnosa")

                    # Tampilkan Kartu Hasil
                    for i, (p, score) in enumerate(hasil):
                        kelas = "card main-card" if i == 0 else "card"
                        st.markdown(f"""
                        <div class="{kelas}">
                        <b>{p}</b> - {score:.1f}%
                        </div>
                        """, unsafe_allow_html=True)
                        st.progress(int(score), text=f"{score:.1f}%")

                    # --- VISUALISASI PLOTLY ---
                    st.subheader("📈 Grafik Perbandingan")
                    df_hasil = pd.DataFrame(hasil, columns=["Penyakit", "Skor CF (%)"])
                    
                    fig = px.bar(
                        df_hasil, 
                        x="Penyakit", 
                        y="Skor CF (%)",
                        text="Skor CF (%)",
                        color="Skor CF (%)",
                        color_continuous_scale=["#334155", "#22c55e"],
                        template="plotly_dark"
                    )
                    fig.update_traces(textposition='outside')
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        yaxis_range=[0, 110]
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Detail Penyakit (Kolom Kanan)
                with right:
                    st.subheader("📌 Detail Penyakit")
                    show_disease_detail(penyakit_utama)

                # Simpan ke riwayat
                nama_final = nama_pasien if nama_pasien else "Anonim"
                st.session_state.history.append({
                    "waktu": datetime.now().strftime("%d/%m %H:%M"),
                    "nama": nama_final,
                    "hasil": penyakit_utama,
                    "skor": skor_utama
                })
                
            else:
                st.warning("Gejala yang dipilih tidak cocok dengan penyakit mana pun dalam database.")
    else:
        st.error("❌ Silakan pilih minimal satu gejala terlebih dahulu!")

# Aksi Clear
if clear:
    hasil_placeholder.empty()
    st.rerun()