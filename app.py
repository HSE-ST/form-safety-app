
import streamlit as st
import pandas as pd
from io import BytesIO
import xlsxwriter

st.set_page_config(page_title="Personal Safety Discussion", page_icon="🛡️", layout="wide")

AUTHORIZED_EMAIL = "hset.mbma@sinarterangmandiri.com"
if "email" not in st.session_state:
    with st.sidebar:
        st.session_state["email"] = st.text_input("🔒 Masukkan email untuk akses dashboard:", "")

email = st.session_state["email"].strip().lower()
is_authorized = email == AUTHORIZED_EMAIL

st.title("🛡️ Personal Safety Discussion")
st.markdown("Formulir ini berdasarkan format OHS/F-138 untuk mendokumentasikan diskusi keselamatan.")

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
        "3. Bagaimana kabar keluarga dirumah?",
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
    saran = st.text_area("Masukkan saran dan komitmen safety:")

    st.header("📸 Upload Foto Bukti Kegiatan")
    foto = st.file_uploader("Upload foto (jpeg/png)", type=["jpg", "jpeg", "png"])

    submit = st.form_submit_button("Submit")

    if submit:
        st.success("Data berhasil disimpan sementara.")
        if "data" not in st.session_state:
            st.session_state["data"] = []
        st.session_state["data"].append({
            "Tanggal": tanggal.strftime("%Y-%m-%d"),
            "Lokasi": lokasi,
            "Perusahaan": perusahaan,
            **{f"Coachee - {k}": v for k, v in coachee.items()},
            **{f"Coach - {k}": v for k, v in coach.items()},
            **{f"Q{i+1}": jawaban[i] for i in range(len(jawaban))},
            "Diskusi Umum": diskusi,
            "Saran & Komitmen": saran,
            "Foto": foto
        })

# Dashboard and export
if is_authorized:
    st.header("📊 Dashboard & Rekap")
    if "data" in st.session_state and st.session_state["data"]:
        df_display = pd.DataFrame([{k: v for k, v in row.items() if k != "Foto"} for row in st.session_state["data"]])
        st.dataframe(df_display)

        def create_excel(data):
            output = BytesIO()
            wb = xlsxwriter.Workbook(output, {'in_memory': True})
            ws = wb.add_worksheet("Rekap")

            headers = list(data[0].keys())
            headers.remove("Foto")
            headers.append("Foto")

            for col_idx, header in enumerate(headers):
                ws.write(0, col_idx, header)

            for row_idx, entry in enumerate(data, start=1):
                for col_idx, key in enumerate(headers):
                    if key == "Foto":
                        if entry["Foto"]:
                            image_bytes = entry["Foto"].getvalue()
                            ws.insert_image(row_idx, col_idx, entry["Foto"].name,
                                            {"image_data": BytesIO(image_bytes), "x_scale": 0.3, "y_scale": 0.3})
                    else:
                        ws.write(row_idx, col_idx, entry.get(key, ""))

            wb.close()
            output.seek(0)
            return output

        excel_data = create_excel(st.session_state["data"])
        st.download_button("📥 Unduh Rekap Excel", data=excel_data, file_name="rekap_psd.xlsx")
    else:
        st.info("Belum ada data tersedia.")
else:
    st.info("Silakan masukkan email untuk mengakses dashboard.")
