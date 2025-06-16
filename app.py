import streamlit as st
import pandas as pd
import os, io, base64
from datetime import datetime
from PIL import Image
import xlsxwriter

# --- Config & Style ---
st.set_page_config(page_title="Personal Safety Discussion", page_icon="🦺", layout="wide")
st.markdown("""
<style>
.stApp { background-color: #f4f9ff; }
.stButton>button { background-color: #2e8b57; color: white; }
.stDownloadButton>button { background-color: #4682b4; color: white; }
</style>
""", unsafe_allow_html=True)

# --- Inisialisasi Data ---
if "entries" not in st.session_state:
    st.session_state.entries = []

# --- Form Isi ---
with st.form("psd_form"):
    st.header("📋 Personal Safety Discussion")
    col1, col2 = st.columns(2)
    with col1:
        tanggal = st.date_input("Tanggal")
        lokasi = st.text_input("Lokasi")
        st.subheader("📌 Coachee (Penerima)")
        co_nama = st.text_input("Nama Coachee")
        co_nik = st.text_input("NIK Coachee")
        co_jabatan = st.text_input("Jabatan Coachee")
        co_departemen = st.text_input("Departemen Coachee")
        co_perusahaan = st.text_input("Perusahaan Coachee")
    with col2:
        st.subheader("📌 Coach (Pemberi)")
        coach_nama = st.text_input("Nama Coach")
        coach_nik = st.text_input("NIK Coach")
        coach_jabatan = st.text_input("Jabatan Coach")
        coach_departemen = st.text_input("Departemen Coach")
        coach_perusahaan = st.text_input("Perusahaan Coach")
        st.subheader("✍️ Atasan Coachee")
        atasan_name = st.text_input("Nama Atasan Coachee")
        atasan_sign = st.text_input("Tanda Tangan (teks)")
        atasan_tgl = st.date_input("Tanggal Persetujuan")

    st.subheader("🔍 Pertanyaan Pembuka")
    q1 = st.text_area("1. Bagaimana kabar Anda hari ini?")
    q2 = st.text_area("2. Apabila cuti Anda pulang kemana?")
    q3 = st.text_area("3. Bagaimana kabar keluarga dirumah?")
    q4 = st.text_area("4. Apakah anda sedang mengalami masalah diluar pekerjaan?")
    q5 = st.text_area("5. Pekerjaan apa yang sedang Anda lakukan hari ini?")
    q6 = st.text_area("6. Sudah berapa lama melakukan pekerjaan ini?")
    q7 = st.text_area("7. Sudah berapa lama Anda bekerja di IUP SCM?")
    q8 = st.text_area("8. Apakah ada kendala di pekerjaan? Kalau ada anda bisa ceritakan!")
    q9 = st.text_area("9. Pertanyaan lainnya?")

    st.subheader("💬 Diskusi Umum")
    diskusi = st.text_area("")
    st.subheader("✅ Saran & Komitmen Safety")
    komitmen = st.text_area("")
    uploaded = st.file_uploader("📷 Upload Foto Dokumentasi (png/jpg/jpeg)", type=["png","jpg","jpeg"])

    submitted = st.form_submit_button("Submit")
    if submitted:
        foto_path = ""
        if uploaded:
            os.makedirs("uploads", exist_ok=True)
            foto_path = os.path.join("uploads", f"{co_nama}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uploaded.name}")
            with open(foto_path, "wb") as f: f.write(uploaded.getbuffer())
        st.session_state.entries.append({
            "Tanggal": tanggal.strftime("%Y-%m-%d"), "Lokasi": lokasi,
            "Coachee": co_nama, "NIK Coachee": co_nik, "Jabatan Coachee": co_jabatan,
            "Departemen Coachee": co_departemen, "Perusahaan Coachee": co_perusahaan,
            "Coach": coach_nama, "NIK Coach": coach_nik, "Jabatan Coach": coach_jabatan,
            "Departemen Coach": coach_departemen, "Perusahaan Coach": coach_perusahaan,
            "Atasan": atasan_name, "Atasan Sign": atasan_sign,
            "Atasan Tgl": atasan_tgl.strftime("%Y-%m-%d"),
            **{f"Q{i}": eval(f"q{i}") for i in range(1,10)},
            "Diskusi": diskusi, "Komitmen": komitmen, "Foto": foto_path
        })
        st.success("✅ Data berhasil disimpan!")

# --- Tabel dan Filter ---
st.markdown("---")
st.header("📊 Rekap Data Personal Safety Discussion")

df = pd.DataFrame(st.session_state.entries)
if not df.empty:
    df_show = df.drop(columns=["Foto"])
    filters = st.sidebar.expander("🔍 Filter")
    with filters:
        selected_name = st.selectbox("Nama Coachee", ["Semua"] + df_show["Coachee"].unique().tolist())
        selected_dept = st.selectbox("Departemen Coachee", ["Semua"] + df_show["Departemen Coachee"].unique().tolist())
        dates = st.date_input("Tanggal", [])
    filtered = df_show.copy()
    if selected_name!="Semua": filtered=filtered[filtered["Coachee"]==selected_name]
    if selected_dept!="Semua": filtered=filtered[filtered["Departemen Coachee"]==selected_dept]
    if len(dates)==2:
        filtered = filtered[(df["Tanggal"]>=dates[0].strftime("%Y-%m-%d"))&(df["Tanggal"]<=dates[1].strftime("%Y-%m-%d"))]
    st.dataframe(filtered)

    # --- Download Excel ---
    out = io.BytesIO()
    wb = xlsxwriter.Workbook(out)
    ws = wb.add_worksheet("Rekap PSD")
    headers = df.columns.tolist()
    for col_num, header in enumerate(headers): ws.write(0, col_num, header)
    for row_num, entry in enumerate(st.session_state.entries, start=1):
        for col_num, key in enumerate(headers):
            ws.write(row_num, col_num, entry[key] if key!="Foto" else "")
        if entry["Foto"]:
            ws.insert_image(row_num, headers.index("Foto"), entry["Foto"], {'x_scale':0.2, 'y_scale':0.2})

    wb.close()
    out.seek(0)
    st.download_button("📥 Download Rekapan Excel", out, "personal_safety_discussion.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.info("Belum ada data yang dimasukkan.")
