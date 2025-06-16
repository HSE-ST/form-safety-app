import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.drawing.image import Image as ExcelImage
from PIL import Image as PILImage

st.set_page_config(page_title="📋 Safety Coaching Form", layout="wide", page_icon="📋")
st.title("📋 Form Personal Safety Discussion")
st.markdown("---")

# === Input Form ===
st.header("📝 Formulir Coaching")

with st.form("form_coaching"):
    col1, col2 = st.columns(2)
    with col1:
        nama = st.text_input("Nama Karyawan")
        departemen = st.selectbox("Departemen", ["HAULING", "HRGAFINIT", "HSET", "LOGISTIK", "MANAGEMENT", "MAINTENANCE", "MINE OPERATION", "MPE"])
        tanggal = st.date_input("Tanggal Coaching", value=datetime.today())
    with col2:
        topik = st.text_area("Topik Coaching")
        rekomendasi = st.text_area("Rekomendasi atau Tindak Lanjut")

    uploaded_file = st.file_uploader("📷 Upload Foto Bukti Coaching", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        folder = "uploads"
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    else:
        file_path = ""

    submitted = st.form_submit_button("✅ Submit")

    if submitted:
        data_baru = {
            "Nama": nama,
            "Departemen": departemen,
            "Tanggal": tanggal.strftime("%Y-%m-%d"),
            "Topik": topik,
            "Rekomendasi": rekomendasi,
            "Foto": file_path
        }
        df_baru = pd.DataFrame([data_baru])

        if os.path.exists("data_coaching.csv"):
            df_lama = pd.read_csv("data_coaching.csv")
            df = pd.concat([df_lama, df_baru], ignore_index=True)
        else:
            df = df_baru

        df.to_csv("data_coaching.csv", index=False)
        st.success("✅ Data berhasil disimpan!")

# === Dashboard Rekap ===
st.markdown("---")
st.header("📊 Dashboard Rekapan Data Coaching")

if os.path.exists("data_coaching.csv"):
    df = pd.read_csv("data_coaching.csv")

    col1, col2, col3 = st.columns(3)
    with col1:
        nama_filter = st.selectbox("Filter Nama", options=["Semua"] + sorted(df["Nama"].dropna().unique().tolist()))
    with col2:
        dept_filter = st.selectbox("Filter Departemen", options=["Semua"] + sorted(df["Departemen"].dropna().unique().tolist()))
    with col3:
        tanggal_filter = st.date_input("Filter Tanggal", value=None)

    df_filtered = df.copy()
    if nama_filter != "Semua":
        df_filtered = df_filtered[df_filtered["Nama"] == nama_filter]
    if dept_filter != "Semua":
        df_filtered = df_filtered[df_filtered["Departemen"] == dept_filter]
    if tanggal_filter:
        df_filtered = df_filtered[df_filtered["Tanggal"] == tanggal_filter.strftime("%Y-%m-%d")]

    st.dataframe(df_filtered)

    # === Unduh Excel dengan Gambar ===
    st.markdown("### 📥 Unduh Rekapan dalam Excel (termasuk gambar)")

    output = io.BytesIO()
    wb = Workbook()
    ws = wb.active
    ws.append(list(df.columns))

    for idx, row in df.iterrows():
        ws.append(row[:-1].tolist() + [row["Foto"]])
        img_path = row["Foto"]
        if os.path.exists(img_path) and img_path.lower().endswith((".jpg", ".jpeg", ".png")):
            try:
                img = ExcelImage(img_path)
                img.width = 100
                img.height = 100
                ws.add_image(img, f"G{idx+2}")
            except:
                pass

    wb.save(output)
    output.seek(0)

    st.download_button(
        label="📥 Download Excel Rekap Coaching",
        data=output,
        file_name="rekap_coaching.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Belum ada data coaching yang tersedia.")

# === Style ===
st.markdown("""
<style>
    .stApp {
        background-color: #f4f9ff;
        color: #1f2e45;
    }
    .stTextInput > div > div > input {
        background-color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)
