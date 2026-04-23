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
        "image_url": "data:image/jpeg;base64,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",
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
    # Kosongkan tampilan hasil
    hasil_placeholder.empty()
    
    # Bersihkan kolom kanan (placeholder khusus jika perlu, tapi karena hasil placeholder kosong, kolom kanan juga akan bersih secara logika script)
    # Agar input juga ter-reset di mata user saat rerun:
    st.session_state.clear_flag = True 
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