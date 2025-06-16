import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime
from PIL import Image

st.set_page_config(page_title="Personal Safety Discussion", page_icon="🦺", layout="wide")
st.markdown("<h1 style='color:#ff4b4b;'>📋 Personal Safety Discussion Form</h1>", unsafe_allow_html=True)

# Inisialisasi penyimpanan data
if "data" not in st.session_state:
    st.session_state.data = []

# Fungsi untuk menyimpan data ke Excel
def save_to_excel(data):
    df = pd.DataFrame(data)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"personal_safety_discussion_{timestamp}.xlsx"
    
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        for i, row in enumerate(data):
            df_single = pd.DataFrame([row])
            df_single.drop(columns=['Foto'], inplace=True)
            df_single.to_excel(writer, index=False, sheet_name=f"Entry{i+1}")

            if row['Foto']:
                worksheet = writer.sheets[f"Entry{i+1}"]
                image_path = row['Foto']
                worksheet.insert_image('J2', image_path, {'x_scale': 0.5, 'y_scale': 0.5})

    return filename

# Fungsi untuk membuat tautan unduhan
def download_link(filename):
    with open(filename, "rb") as f:
        bytes_data = f.read()
    b64 = base64.b64encode(bytes_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">📥 Download Excel</a>'
    return href

with st.form("psd_form"):
    col1, col2 = st.columns(2)
    with col1:
        tanggal = st.date_input("Tanggal")
        nama = st.text_input("Nama")
        departemen = st.selectbox("Departemen", ["HSET", "HRD", "MINE OPERATION", "MAINTENANCE", "LOGISTIK", "MANAGEMENT"])
    with col2:
        topik_diskusi = st.text_area("Topik Diskusi")
        hasil_diskusi = st.text_area("Hasil Diskusi dan Komitmen")
        foto = st.file_uploader("Upload Foto Bukti Kegiatan", type=["png", "jpg", "jpeg"])

    submitted = st.form_submit_button("Submit")
    if submitted:
        if not os.path.exists("uploaded_images"):
            os.makedirs("uploaded_images")
        foto_path = ""
        if foto:
            foto_path = os.path.join("uploaded_images", foto.name)
            with open(foto_path, "wb") as f:
                f.write(foto.getbuffer())

        st.session_state.data.append({
            "Tanggal": tanggal,
            "Nama": nama,
            "Departemen": departemen,
            "Topik Diskusi": topik_diskusi,
            "Hasil Diskusi": hasil_diskusi,
            "Foto": foto_path
        })
        st.success("✅ Data Personal Safety Discussion berhasil disimpan!")

st.markdown("---")
st.markdown("## 📊 Rekapitulasi Personal Safety Discussion")

if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)
    df_show = df.drop(columns=['Foto'])

    # Filter
    with st.expander("🔍 Filter Data"):
        f1, f2, f3 = st.columns(3)
        with f1:
            selected_name = st.selectbox("Filter Nama", ["Semua"] + list(df_show["Nama"].unique()))
        with f2:
            selected_dept = st.selectbox("Filter Departemen", ["Semua"] + list(df_show["Departemen"].unique()))
        with f3:
            selected_date = st.date_input("Filter Tanggal (Opsional)", value=None)

        filtered_df = df_show.copy()
        if selected_name != "Semua":
            filtered_df = filtered_df[filtered_df["Nama"] == selected_name]
        if selected_dept != "Semua":
            filtered_df = filtered_df[filtered_df["Departemen"] == selected_dept]
        if selected_date:
            filtered_df = filtered_df[filtered_df["Tanggal"] == pd.to_datetime(selected_date)]

    st.dataframe(filtered_df, use_container_width=True)

    if st.button("📥 Download Semua Rekapan Excel"):
        filename = save_to_excel(st.session_state.data)
        st.markdown(download_link(filename), unsafe_allow_html=True)
else:
    st.info("Belum ada data yang masuk.")
