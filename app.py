
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from io import BytesIO
import xlsxwriter

# === Konfigurasi ===
SHEET_ID = "1oAEnIloBQqY2rv_b7_0_djkHmCKytjUOlqvQAYfKIIA"
SHEET_NAME = "Sheet1"
CREDENTIALS_FILE = "credentials.json"
AUTHORIZED_EMAIL = "hset.mbma@sinarterangmandiri.com"

# === Setup Google Sheets ===
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# Fungsi bantu
def append_data_to_sheet(data: dict):
    values = list(data.values())
    sheet.append_row(values, value_input_option="USER_ENTERED")

def get_data_as_dataframe():
    records = sheet.get_all_records()
    return pd.DataFrame(records)

def create_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='PSD')
    output.seek(0)
    return output

# UI: Login
st.set_page_config(page_title="Personal Safety Discussion", layout="wide")
if "email" not in st.session_state:
    st.session_state["email"] = ""

with st.sidebar:
    email_input = st.text_input("🔐 Masukkan email admin:", value=st.session_state["email"])
    if st.button("Login"):
        st.session_state["email"] = email_input.strip().lower()

email = st.session_state["email"]
is_authorized = email == AUTHORIZED_EMAIL

st.title("🛡️ Personal Safety Discussion")

# === FORM ===
with st.form("psd_form", clear_on_submit=True):
    st.subheader("📅 Informasi Diskusi")
    tanggal = st.date_input("Tanggal")
    lokasi = st.text_input("Lokasi")
    perusahaan = st.text_input("Perusahaan Coachee")

    st.subheader("👥 Coachee & Coach")
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

    st.subheader("🗣️ Pertanyaan Pembuka")
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

    st.subheader("💬 Diskusi Umum")
    diskusi = st.text_area("Diskusi umum terkait keselamatan:")

    st.subheader("✅ Saran & Komitmen")
    saran = st.text_area("Saran dan komitmen keselamatan:")

    submitted = st.form_submit_button("Submit")

    if submitted:
        new_entry = {
            "Tanggal": tanggal.strftime("%Y-%m-%d"),
            "Lokasi": lokasi,
            "Perusahaan": perusahaan,
            **{f"Coachee - {k}": v for k, v in coachee.items()},
            **{f"Coach - {k}": v for k, v in coach.items()},
            **{f"Q{i+1}": jawaban[i] for i in range(len(jawaban))},
            "Diskusi Umum": diskusi,
            "Saran & Komitmen": saran,
            "Waktu Submit": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        append_data_to_sheet(new_entry)
        st.success("✅ Data berhasil dikirim ke Google Sheets.")

# === DASHBOARD ===
if is_authorized:
    st.subheader("📊 Dashboard PSD")
    df = get_data_as_dataframe()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        excel_data = create_excel(df)
        st.download_button("⬇️ Download Excel", data=excel_data, file_name="rekap_psd.xlsx")
    else:
        st.info("Belum ada data.")
else:
    st.info("Login dengan email admin untuk akses dashboard.")
