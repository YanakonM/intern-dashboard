import streamlit as st
import pandas as pd

# ต้องอยู่บรรทัดบนสุดหลัง import
st.set_page_config(page_title="New Employee Dashboard", layout="wide")

# --- ฟังก์ชันอ่าน Daily Report ---
def read_daily_reports(uploaded_files):
    report_list = []
    for file in uploaded_files:
        df = pd.read_excel(file)
        df.columns = [c.strip() for c in df.columns]
        # ข้ามแถวที่ Candidate Name หรือ Role ว่าง
        df = df[df['Candidate Name'].notna() & df['Role'].notna()]
        # เฉพาะที่ Interview = Yes และ Status = Pass
        mask = (df["Interview"].str.lower() == "yes") & (df["Status"].str.lower() == "pass")
        filtered = df[mask]
        # ดึงชื่อทีมงานจากชื่อไฟล์
        name_split = file.name.replace(".xls", "").replace(".xlsx", "").split('_')
        team_member = f"{name_split[-2]} {name_split[-1]}"
        filtered["Team Member"] = team_member
        report_list.append(filtered[["Candidate Name", "Role", "Team Member"]])
    if report_list:
        return pd.concat(report_list, ignore_index=True)
    else:
        return pd.DataFrame(columns=["Candidate Name", "Role", "Team Member"])

# --- ฟังก์ชันอ่าน New Employee ---
def read_new_employees(file):
    df = pd.read_excel(file)
    df.columns = [c.strip() for c in df.columns]
    df = df[df['Employee Name'].notna() & df['Role'].notna()]
    # Format Join Date (3-Feb-2025)
    # หมายเหตุ: ถ้าใช้ Windows แล้ว error ให้เปลี่ยนเป็น %#d แทน %-d
    df['Join Date'] = pd.to_datetime(df['Join Date']).dt.strftime('%-d-%b-%Y')
    return df[["Employee Name", "Join Date", "Role"]]

# --- ส่วนแสดงผล Streamlit ---
st.title("New Employee Dashboard (Vanness Plus Skill Test)")

st.sidebar.header("Upload Files")
daily_reports = st.sidebar.file_uploader(
    "Upload Daily Report Excel files (.xls or .xlsx)", type=['xls', 'xlsx'], accept_multiple_files=True)
new_employee_file = st.sidebar.file_uploader(
    "Upload New Employee Excel file (.xls or .xlsx)", type=['xls', 'xlsx'])

if daily_reports and new_employee_file:
    try:
        report = read_daily_reports(daily_reports)
        emp = read_new_employees(new_employee_file)
        # Merge ข้อมูล
        merged = pd.merge(emp, report, how="left",
                          left_on=["Employee Name", "Role"],
                          right_on=["Candidate Name", "Role"])
        dashboard = merged[["Employee Name", "Join Date", "Role", "Team Member"]]
        dashboard = dashboard.rename(columns={"Team Member": "Team Member (Interviewer)"})
        dashboard = dashboard.fillna('-')
        st.success("Dashboard Generated Successfully!")
        st.dataframe(dashboard, use_container_width=True)
        # Export ให้ดาวน์โหลด (Optional)
        csv = dashboard.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="Download Dashboard as CSV",
            data=csv,
            file_name="dashboard.csv",
            mime='text/csv',
        )
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Please upload all required files on the sidebar.")

st.caption("Developed by Yanakon Panyakittisap | For Internship Skill Test | Vanness Plus Consulting")
