# Personal Safety Discussion App (Google Sheets Version)
import streamlit as st
import pandas as pd
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from io import BytesIO
import xlsxwriter

st.set_page_config(page_title="Personal Safety Discussion", page_icon="🛡️", layout="wide")

AUTHORIZED_EMAIL = "hset.mbma@sinarterangmandiri.com"
SPREADSHEET_ID = "1oAEnIloBQqY2rv_b7_0_djkHmCKytjUOlqvQAYfKIIA"
SHEET_NAME = "data"

# Load credentials from Streamlit secrets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

# Session state for login
if "email" not in st.session_state:
    st.session_state["email"] = ""

with st.sidebar:
    email_input = st.text_input("🔐 Masukkan email untuk akses dashboard:", value=st.session_state["email"])
    if st.button("Login"):
        st.session_state["email"] = email_input.strip().lower()

email = st.session_state["email"]
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

    submit = st.form_submit_button("Submit")

    if submit:
        row = [
            tanggal.strftime("%Y-%m-%d"),
            lokasi,
            perusahaan,
            *coachee.values(),
            *coach.values(),
            *jawaban,
            diskusi,
            saran
        ]
        sheet.append_row(row)
        st.success("✅ Data berhasil disimpan ke Google Sheets")

# Dashboard & download
if is_authorized:
    st.header("📊 Dashboard & Unduh Data")
    data = sheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    st.dataframe(df, use_container_width=True)

    def to_excel(df):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='PSD', index=False)
        writer.close()
        return output.getvalue()

    excel_data = to_excel(df)
    st.download_button("📥 Download Excel", data=excel_data, file_name="psd_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.info("Login dengan email resmi untuk akses dashboard.")
