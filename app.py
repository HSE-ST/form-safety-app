import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Personal Safety Discussion", layout="wide")

DATA_FILE = "data.csv"
UPLOAD_FOLDER = "uploaded_images"
ALLOWED_VIEWER_EMAIL = "hset.mbma@sinarterangmandiri.com"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.title("📋 Personal Safety Discussion")

menu = st.sidebar.radio("Menu", ["Isi Form", "Dashboard & Download (Admin)"])

if menu == "Isi Form":
    with st.form("psd_form"):
        st.subheader("🔹 Informasi Pribadi")
        nama = st.text_input("Nama Lengkap")
        departemen = st.selectbox("Departemen", [
            "HSET", "HAULING", "HRGAFINIT", "LOGISTIK",
            "MAINTENANCE", "MANAGEMENT", "MINE OPERATION", "MPE"
        ])
        jabatan = st.text_input("Jabatan")
        lokasi = st.text_input("Lokasi Diskusi")
        tanggal = st.date_input("Tanggal PSD", value=datetime.today())

        st.subheader("🔹 Pertanyaan Pembuka")
        pembuka = st.text_area("Apa yang sedang kamu kerjakan saat ini?")
        potensi_bahaya = st.text_area("Apa potensi bahayanya?")
        pengendalian = st.text_area("Apa pengendalian yang digunakan?")

        st.subheader("🔹 Diskusi Umum")
        diskusi = st.text_area("Topik atau isi diskusi:")
        saran = st.text_area("Masukan atau saran terkait keselamatan:")
        komitmen = st.text_area("Komitmen terhadap keselamatan:")

        st.subheader("🔹 Upload Foto (opsional)")
        foto = st.file_uploader("Upload Foto Kegiatan", type=["jpg", "jpeg", "png"])

        submitted = st.form_submit_button("Kirim")

        if submitted:
            foto_filename = ""
            if foto:
                foto_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{foto.name}"
                with open(os.path.join(UPLOAD_FOLDER, foto_filename), "wb") as f:
                    f.write(foto.getbuffer())

            new_data = {
                "Tanggal": tanggal.strftime("%Y-%m-%d"),
                "Nama": nama,
                "Departemen": departemen,
                "Jabatan": jabatan,
                "Lokasi": lokasi,
                "Aktivitas": pembuka,
                "Bahaya": potensi_bahaya,
                "Pengendalian": pengendalian,
                "Diskusi": diskusi,
                "Saran": saran,
                "Komitmen": komitmen,
                "Foto": foto_filename,
                "Waktu Submit": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            df_new = pd.DataFrame([new_data])
            if os.path.exists(DATA_FILE):
                df = pd.read_csv(DATA_FILE)
                df = pd.concat([df, df_new], ignore_index=True)
            else:
                df = df_new
            df.to_csv(DATA_FILE, index=False)
            st.success("✅ Data berhasil disimpan.")

# =============== DASHBOARD ================
if menu == "Dashboard & Download (Admin)":
    st.subheader("📊 Dashboard Data PSD")
    email = st.text_input("Masukkan email admin:")

    if email.lower().strip() == ALLOWED_VIEWER_EMAIL:
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)

            st.success("✅ Data ditemukan. Menampilkan dashboard.")
            st.metric("Jumlah Entri", len(df))
            st.dataframe(df[["Tanggal", "Nama", "Departemen", "Lokasi"]])

            st.markdown("---")
            def convert_df_with_images(df):
                from xlsxwriter import Workbook

                output = BytesIO()
                workbook = Workbook(output, {'in_memory': True})
                worksheet = workbook.add_worksheet("PSD")

                headers = list(df.columns)
                for col_num, header in enumerate(headers):
                    worksheet.write(0, col_num, header)

                for row_num, row in df.iterrows():
                    for col_num, value in enumerate(row):
                        if headers[col_num] == "Foto" and value:
                            img_path = os.path.join(UPLOAD_FOLDER, value)
                            if os.path.exists(img_path):
                                worksheet.insert_image(row_num+1, col_num, img_path,
                                    {'x_scale': 0.15, 'y_scale': 0.15, 'x_offset': 2, 'y_offset': 2})
                        else:
                            worksheet.write(row_num+1, col_num, value)
                workbook.close()
                output.seek(0)
                return output

            excel_data = convert_df_with_images(df)
            st.download_button("⬇️ Download Excel + Gambar", data=excel_data,
                               file_name="rekap_psd.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            if st.button("🗑️ Hapus Semua Data"):
                os.remove(DATA_FILE)
                st.success("Semua data berhasil dihapus.")
        else:
            st.warning("Belum ada data.")
    else:
        st.warning("❌ Akses hanya untuk admin.")
