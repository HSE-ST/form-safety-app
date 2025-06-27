# Personal Safety Discussion App with Google Sheets (Secrets-based)
import streamlit as st
import pandas as pd
import gspread
import json
import base64
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="Personal Safety Discussion", page_icon="🛡️", layout="wide")

# Spreadsheet credentials from Streamlit Secrets
creds_dict = st.secrets["GOOGLE_CREDENTIALS"]
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

# Ganti dengan ID dan sheet name milik kamu
SPREADSHEET_ID = "1oAEnIloBQqY2rv_b7_0_djkHmCKytjUOlqvQAYfKIIA"
SHEET_NAME = "Database_PSD"
worksheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

AUTHORIZED_EMAIL = "hset.mbma@sinarterangmandiri.com"

if "email" not in st.session_state:
    st.session_state.email = ""

with st.sidebar:
    email_input = st.text_input("🔐 Masukkan email untuk akses dashboard:", value=st.session_state.email)
    if st.button("Login"):
        st.session_state.email = email_input.strip().lower()

email = st.session_state.email
is_authorized = email == AUTHORIZED_EMAIL

st.title("🛡️ Personal Safety Discussion")

with st.form("psd_form", clear_on_submit=True):
    st.header("📅 Informasi Diskusi")
    col1, col2 = st.columns(2)
    with col1:
        tanggal = st.date_input("Tanggal")
        lokasi = st.text_input("Lokasi")
    with col2:
        perusahaan = st.text_input("Perusahaan Coachee")

    st.header("👥 Data Coachee & Coach")
    col1, col2 = st.columns(2)
    with col1:
        coachee = {
            "Nama": st.text_input("Nama Coachee"),
            "NIK": st.text_input("NIK Coachee"),
            "Jabatan": st.text_input("Jabatan Coachee"),
            "Departemen": st.text_input("Departemen Coachee")
        }
    with col2:
        coach = {
            "Nama": st.text_input("Nama Coach"),
            "NIK": st.text_input("NIK Coach"),
            "Jabatan": st.text_input("Jabatan Coach"),
            "Departemen": st.text_input("Departemen Coach")
        }

    st.header("🗣️ Pertanyaan Pembuka")
    pertanyaan = [
        "1. Bagaimana kabar Anda hari ini?",
        "2. Apabila cuti Anda pulang kemana?",
        "3. Bagaimana kabar keluarga di rumah?",
        "4. Apakah Anda sedang mengalami masalah di luar pekerjaan?",
        "5. Pekerjaan apa yang sedang Anda lakukan hari ini?",
        "6. Sudah berapa lama melakukan pekerjaan ini?",
        "7. Sudah berapa lama Anda bekerja di IUP SCM?",
        "8. Apakah ada kendala di pekerjaan?",
        "9. Pertanyaan lainnya:"
    ]
    jawaban = [st.text_input(q) for q in pertanyaan]

    st.header("💬 Diskusi Umum")
    diskusi = st.text_area("Diskusikan hal-hal umum terkait keselamatan:")

    st.header("✅ Saran & Komitmen")
    saran = st.text_area("Masukkan saran dan komitmen keselamatan:")

    submitted = st.form_submit_button("Submit")

    if submitted:
        new_row = [
            tanggal.strftime("%Y-%m-%d"), lokasi, perusahaan,
            coachee["Nama"], coachee["NIK"], coachee["Jabatan"], coachee["Departemen"],
            coach["Nama"], coach["NIK"], coach["Jabatan"], coach["Departemen"],
            *jawaban, diskusi, saran
        ]
        worksheet.append_row(new_row)
        st.success("Data berhasil disimpan di Google Sheets.")

# Dashboard admin
if is_authorized:
    st.header("📊 Dashboard & Manajemen Data")
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    st.dataframe(df, use_container_width=True)

    with st.expander("⬇️ Unduh sebagai Excel"):
        output = pd.ExcelWriter("rekapan.xlsx", engine="xlsxwriter")
        df.to_excel(output, index=False, sheet_name="Data")
        output.close()

        with open("rekapan.xlsx", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="rekapan_psd.xlsx">📥 Klik di sini untuk download Excel</a>'
            st.markdown(href, unsafe_allow_html=True)

    with st.expander("⚠️ Hapus semua data?"):
        if st.button("Hapus semua data di sheet"):
            worksheet.clear()
            worksheet.append_row([
                "Tanggal", "Lokasi", "Perusahaan",
                "Coachee - Nama", "Coachee - NIK", "Coachee - Jabatan", "Coachee - Departemen",
                "Coach - Nama", "Coach - NIK", "Coach - Jabatan", "Coach - Departemen",
                "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9",
                "Diskusi Umum", "Saran & Komitmen"
            ])
            st.success("Semua data berhasil dihapus.")
else:
    st.info("Login dengan email resmi untuk akses dashboard.")
