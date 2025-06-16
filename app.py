
import streamlit as st
import pandas as pd
import datetime
from io import BytesIO

st.set_page_config(page_title="Personal Safety Discussion", layout="wide")

st.title("📋 Personal Safety Discussion Form")

# === Form Section ===
with st.form("safety_form", clear_on_submit=True):
    st.subheader("🔐 Identitas")
    col1, col2 = st.columns(2)

    with col1:
        coachee_nama = st.text_input("Nama Coachee")
        coachee_nik = st.text_input("NIK Coachee")
        coachee_jabatan = st.text_input("Jabatan Coachee")
        coachee_departemen = st.text_input("Departemen Coachee")
        coachee_perusahaan = st.text_input("Perusahaan Coachee")

    with col2:
        coach_nama = st.text_input("Nama Coach")
        coach_nik = st.text_input("NIK Coach")
        coach_jabatan = st.text_input("Jabatan Coach")
        coach_departemen = st.text_input("Departemen Coach")
        coach_perusahaan = st.text_input("Perusahaan Coach")

    tanggal = st.date_input("Tanggal", datetime.date.today())
    lokasi = st.text_input("Lokasi")

    st.markdown("### 🗨️ Pertanyaan Pembuka")
    q1 = st.text_input("1. Bagaimana kabar Anda hari ini?")
    q2 = st.text_input("2. Apabila cuti Anda pulang kemana?")
    q3 = st.text_input("3. Bagaimana kabar keluarga dirumah?")
    q4 = st.text_input("4. Apakah anda sedang mengalami masalah diluar pekerjaan?")
    q5 = st.text_input("5. Pekerjaan apa yang sedang Anda lakukan hari ini?")
    q6 = st.text_input("6. Sudah berapa lama melakukan pekerjaan ini?")
    q7 = st.text_input("7. Sudah berapa lama Anda bekerja di IUP SCM?")
    q8 = st.text_input("8. Apakah ada kendala di pekerjaan? Kalau ada anda bisa ceritakan!")
    q9 = st.text_input("9. Pertanyaan lainnya?")

    st.markdown("### 💬 Diskusi Umum")
    diskusi = st.text_area("Diskusi Umum")

    st.markdown("### ✅ Saran & Komitmen Safety")
    saran = st.text_area("Saran & Komitmen Safety")

    submitted = st.form_submit_button("✅ Submit")

# === Save to CSV ===
if submitted:
    df = pd.DataFrame([{
        "Tanggal": tanggal,
        "Lokasi": lokasi,
        "Coachee": coachee_nama,
        "NIK Coachee": coachee_nik,
        "Jabatan Coachee": coachee_jabatan,
        "Departemen Coachee": coachee_departemen,
        "Perusahaan Coachee": coachee_perusahaan,
        "Coach": coach_nama,
        "NIK Coach": coach_nik,
        "Jabatan Coach": coach_jabatan,
        "Departemen Coach": coach_departemen,
        "Perusahaan Coach": coach_perusahaan,
        "Q1": q1, "Q2": q2, "Q3": q3, "Q4": q4, "Q5": q5,
        "Q6": q6, "Q7": q7, "Q8": q8, "Q9": q9,
        "Diskusi": diskusi, "Saran": saran
    }])
    try:
        old = pd.read_csv("hasil_form_safety.csv")
        df = pd.concat([old, df], ignore_index=True)
    except:
        pass
    df.to_csv("hasil_form_safety.csv", index=False)
    st.success("Data berhasil disimpan!")

# === Dashboard Rekap ===
st.subheader("📊 Dashboard Rekap Data")
try:
    data = pd.read_csv("hasil_form_safety.csv")

    with st.expander("📁 Lihat Data"):
        st.dataframe(data)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Coaching", len(data))
    with col2:
        st.metric("Jumlah Coach Unik", data["Coach"].nunique())
    with col3:
        st.metric("Jumlah Coachee Unik", data["Coachee"].nunique())

    with st.expander("🔍 Filter Data"):
        tanggal_filter = st.date_input("Tanggal", [])
        nama_filter = st.text_input("Cari nama (coach atau coachee)")
        departemen_filter = st.text_input("Cari departemen")

        filtered = data.copy()
        if tanggal_filter:
            filtered = filtered[filtered["Tanggal"].isin([str(t) for t in tanggal_filter])]
        if nama_filter:
            filtered = filtered[filtered["Coach"].str.contains(nama_filter, case=False) | filtered["Coachee"].str.contains(nama_filter, case=False)]
        if departemen_filter:
            filtered = filtered[filtered["Departemen Coachee"].str.contains(departemen_filter, case=False)]

        st.dataframe(filtered)

    # Download Excel
    excel_buffer = BytesIO()
    filtered.to_excel(excel_buffer, index=False, engine='openpyxl')
    st.download_button("⬇️ Download Excel", data=excel_buffer.getvalue(), file_name="rekap_safety.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

except Exception as e:
    st.warning("Belum ada data coaching yang disubmit.")

