import streamlit as st
import pandas as pd
import io
from datetime import datetime
from PIL import Image
import base64

st.set_page_config(page_title="Personal Safety Coaching", layout="centered", page_icon="🦺")

st.markdown("""
    <style>
    .main {
        background-color: #f0f8ff;
    }
    .stButton>button {
        background-color: #2e8b57;
        color: white;
    }
    .stDownloadButton>button {
        background-color: #4682b4;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🦺 Personal Safety Coaching Form")

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 0

if 'data' not in st.session_state:
    st.session_state.data = []

if 'uploaded_images' not in st.session_state:
    st.session_state.uploaded_images = []

# Form Pages
def page_1():
    st.header("📋 Data Umum")
    with st.form("form1"):
        nama = st.text_input("Nama")
        departemen = st.selectbox("Departemen", ["HSE", "Operasi", "HRD", "Logistik", "Lainnya"])
        tanggal = st.date_input("Tanggal Coaching", value=datetime.today())
        next_btn = st.form_submit_button("Lanjutkan ➡️")
        if next_btn:
            st.session_state.temp = {"Nama": nama, "Departemen": departemen, "Tanggal": tanggal.strftime("%Y-%m-%d")}
            st.session_state.page += 1

def page_2():
    st.header("🧠 Topik Coaching")
    with st.form("form2"):
        topik = st.text_area("Topik yang Dibahas")
        tindak_lanjut = st.text_area("Tindak Lanjut yang Diharapkan")
        next_btn = st.form_submit_button("Lanjutkan ➡️")
        if next_btn:
            st.session_state.temp.update({"Topik": topik, "Tindak Lanjut": tindak_lanjut})
            st.session_state.page += 1

def page_3():
    st.header("📷 Upload Foto Kegiatan")
    with st.form("form3"):
        foto = st.file_uploader("Unggah Foto Bukti (jpg/png)", type=['jpg', 'jpeg', 'png'])
        submit_btn = st.form_submit_button("✅ Simpan Data")
        if submit_btn:
            img_data = None
            if foto:
                img_data = foto.read()
            st.session_state.temp["Foto"] = img_data
            st.session_state.data.append(st.session_state.temp)
            st.success("Data berhasil disimpan!")
            st.session_state.page = 0

# Navigation
pages = [page_1, page_2, page_3]
pages[st.session_state.page]()

st.markdown("---")
st.header("📊 Rekapitulasi Coaching")

if st.session_state.data:
    df = pd.DataFrame([{k: v for k, v in entry.items() if k != "Foto"} for entry in st.session_state.data])

    # Filter Sidebar
    with st.sidebar:
        st.header("🔎 Filter Data")
        nama_filter = st.multiselect("Pilih Nama", df["Nama"].unique())
        departemen_filter = st.multiselect("Pilih Departemen", df["Departemen"].unique())
        tanggal_range = st.date_input("Rentang Tanggal", [])

    filtered_df = df.copy()
    if nama_filter:
        filtered_df = filtered_df[filtered_df["Nama"].isin(nama_filter)]
    if departemen_filter:
        filtered_df = filtered_df[filtered_df["Departemen"].isin(departemen_filter)]
    if len(tanggal_range) == 2:
        start, end = tanggal_range
        filtered_df = filtered_df[(filtered_df["Tanggal"] >= start.strftime("%Y-%m-%d")) & (filtered_df["Tanggal"] <= end.strftime("%Y-%m-%d"))]

    st.dataframe(filtered_df)

    # Ringkasan Dashboard
    st.subheader("📈 Statistik Coaching")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Coaching", len(filtered_df))
    col2.metric("Topik Unik", filtered_df["Topik"].nunique())
    if not filtered_df.empty:
        top_person = filtered_df["Nama"].value_counts().idxmax()
        top_count = filtered_df["Nama"].value_counts().max()
        col3.metric("Nama Terbanyak", f"{top_person} ({top_count}x)")

    # Download Excel
    def generate_excel():
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            pd.DataFrame(st.session_state.data).drop(columns=["Foto"]).to_excel(writer, sheet_name="Data", index=False)
            workbook = writer.book
            worksheet = writer.sheets['Data']
            row = len(st.session_state.data) + 2
            worksheet.write(row, 0, "Foto Dokumentasi")
            for i, entry in enumerate(st.session_state.data):
                if entry.get("Foto"):
                    img = Image.open(io.BytesIO(entry["Foto"])).resize((100, 100))
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format='PNG')
                    worksheet.insert_image(row + i + 1, 0, "image.png", {"image_data": io.BytesIO(img_bytes.getvalue())})
        excel_buffer.seek(0)
        return excel_buffer

    st.download_button("📥 Download Rekapan (Excel)", data=generate_excel(), file_name="rekapan_coaching.xlsx")

else:
    st.info("Belum ada data coaching yang dimasukkan.")
