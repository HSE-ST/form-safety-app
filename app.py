# Personal Safety Discussion App
import streamlit as st
import pandas as pd
import os
from io import BytesIO
import xlsxwriter
from PIL import Image

st.set_page_config(page_title="Personal Safety Discussion", page_icon="🛡️", layout="wide")

AUTHORIZED_EMAIL = "hset.mbma@sinarterangmandiri.com"
DATA_CSV = "data.csv"
IMAGE_DIR = "uploaded_images"

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

def create_excel_file(df):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet("Data PSD")

    bold = workbook.add_format({'bold': True})

    for col_num, column in enumerate(df.columns):
        worksheet.write(0, col_num, column, bold)

    for row_num, row in enumerate(df.itertuples(index=False), start=1):
        for col_num, value in enumerate(row):
            if df.columns[col_num] == "Foto" and isinstance(value, str) and os.path.exists(value):
                worksheet.set_row(row_num, 40)
                worksheet.insert_image(row_num, col_num, value, {
                    'x_scale': 0.2,
                    'y_scale': 0.2,
                    'x_offset': 2,
                    'y_offset': 2
                })
            else:
                worksheet.write(row_num, col_num, value)

    workbook.close()
    output.seek(0)
    return output

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

    st.header("📸 Upload Foto Bukti Kegiatan")
    foto = st.file_uploader("Upload foto (jpeg/png)", type=["jpg", "jpeg", "png"])

    submit = st.form_submit_button("Submit")

    if submit:
        image_filename = ""
        if foto:
            image_filename = f"{IMAGE_DIR}/{tanggal.strftime('%Y%m%d')}_{coachee['Nama'].replace(' ', '_')}.png"
            with open(image_filename, "wb") as f:
                f.write(foto.getbuffer())

        new_entry = {
            "Tanggal": tanggal.strftime("%Y-%m-%d"),
            "Lokasi": lokasi,
            "Perusahaan": perusahaan,
            **{f"Coachee - {k}": v for k, v in coachee.items()},
            **{f"Coach - {k}": v for k, v in coach.items()},
            **{f"Q{i+1}": jawaban[i] for i in range(len(jawaban))},
            "Diskusi Umum": diskusi,
            "Saran & Komitmen": saran,
            "Foto": image_filename
        }

        df_new = pd.DataFrame([new_entry])
        if os.path.exists(DATA_CSV):
            df_existing = pd.read_csv(DATA_CSV)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new

        df_combined.to_csv(DATA_CSV, index=False)
        st.success("Data berhasil disimpan.")

if is_authorized:
    st.header("📊 Dashboard & Manajemen Data")
    if os.path.exists(DATA_CSV):
        df = pd.read_csv(DATA_CSV)
        st.dataframe(df.drop(columns=["Foto"]), use_container_width=True)

        excel_data = create_excel_file(df)
        st.download_button("⬇️ Download Excel", data=excel_data, file_name="personal_safety_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        with st.expander("🔧 Hapus semua data?"):
            if st.button("Hapus data CSV"):
                os.remove(DATA_CSV)
                st.success("Data berhasil dihapus.")
    else:
        st.info("Belum ada data.")
else:
    st.info("Login dengan email resmi untuk akses dashboard.")
