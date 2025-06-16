import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Personal Safety Discussion", layout="wide")

st.title("📋 Personal Safety Discussion")
st.write("Form ini untuk mengisi diskusi keselamatan antara Coach dan Coachee")

# Tanggal dan lokasi
col1, col2 = st.columns(2)
with col1:
    tanggal = st.date_input("Tanggal", value=datetime.today())
with col2:
    lokasi = st.text_input("Lokasi")

# Informasi Coachee
st.subheader("Penerima Coaching (Coachee)")
coachee_nama = st.text_input("Nama Coachee")
coachee_nik = st.text_input("NIK Coachee")
coachee_jabatan = st.text_input("Jabatan Coachee")
coachee_departemen = st.text_input("Departemen Coachee")
coachee_perusahaan = st.text_input("Perusahaan Coachee")

# Informasi Coach
st.subheader("Pemberi Coaching (Coach)")
coach_nama = st.text_input("Nama Coach")
coach_nik = st.text_input("NIK Coach")
coach_jabatan = st.text_input("Jabatan Coach")
coach_departemen = st.text_input("Departemen Coach")
coach_perusahaan = st.text_input("Perusahaan Coach")

# Pertanyaan pembuka
st.subheader("Pertanyaan Pembuka")
q1 = st.text_area("1. Bagaimana kabar Anda hari ini?")
q2 = st.text_area("2. Apabila cuti Anda pulang kemana?")
q3 = st.text_area("3. Bagaimana kabar keluarga dirumah?")
q4 = st.text_area("4. Apakah anda sedang mengalami masalah di luar pekerjaan?")
q5 = st.text_area("5. Pekerjaan apa yang sedang Anda lakukan hari ini?")
q6 = st.text_area("6. Sudah berapa lama melakukan pekerjaan ini?")
q7 = st.text_area("7. Sudah berapa lama Anda bekerja di IUP SCM?")
q8 = st.text_area("8. Apakah ada kendala di pekerjaan? Jika ada bisa ceritakan.")
q9 = st.text_area("9. Pertanyaan lainnya")

# Diskusi dan Komitmen
st.subheader("Diskusi Umum")
diskusi = st.text_area("Isi Diskusi Umum")

st.subheader("Saran & Komitmen Safety")
komitmen = st.text_area("Saran dan Komitmen Safety")

# Submit
if st.button("Submit Form"):
    data = {
        "Tanggal": tanggal,
        "Lokasi": lokasi,
        "Nama Coachee": coachee_nama,
        "NIK Coachee": coachee_nik,
        "Jabatan Coachee": coachee_jabatan,
        "Departemen Coachee": coachee_departemen,
        "Perusahaan Coachee": coachee_perusahaan,
        "Nama Coach": coach_nama,
        "NIK Coach": coach_nik,
        "Jabatan Coach": coach_jabatan,
        "Departemen Coach": coach_departemen,
        "Perusahaan Coach": coach_perusahaan,
        "Q1": q1, "Q2": q2, "Q3": q3, "Q4": q4, "Q5": q5,
        "Q6": q6, "Q7": q7, "Q8": q8, "Q9": q9,
        "Diskusi Umum": diskusi,
        "Komitmen Safety": komitmen
    }

    df = pd.DataFrame([data])
    df.to_csv("hasil_form_safety.csv", mode="a", index=False, header=False)
    st.success("✅ Data berhasil disimpan!")
