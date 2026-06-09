import streamlit as st
from openai import OpenAI
import pandas as pd

st.set_page_config(page_title="CBS Racing CAO System", page_icon="📋", layout="wide")
st.title("📋 CBS Automotive CAO & HR System")

# ====================== SIMPLE LOGIN ======================
if "role" not in st.session_state:
    password = st.text_input("Enter password (admin = full access, employee = view only)", type="password")
    if st.button("Login"):
        if password == "admin2026":          # CHANGE THIS PASSWORD
            st.session_state.role = "admin"
        elif password == "employee2026":     # CHANGE THIS PASSWORD
            st.session_state.role = "employee"
        else:
            st.error("Wrong password")
        st.rerun()

if "role" not in st.session_state:
    st.stop()

st.sidebar.success(f"Logged in as: **{st.session_state.role.upper()}**")

# ====================== LOAD YOUR 3 SPREADSHEETS ======================
# You can drag-and-drop your 3 spreadsheets here every time (or we can make it auto-load later)
uploaded_files = st.sidebar.file_uploader("Upload your 3 spreadsheets (late / vacation / sick)", accept_multiple_files=True, type=["csv", "xlsx"])

if uploaded_files:
    data = {}
    for file in uploaded_files:
        if file.name.lower().endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        data[file.name] = df
    st.sidebar.success(f"Loaded {len(uploaded_files)} spreadsheets ✓")
else:
    st.sidebar.info("Upload your 3 spreadsheets here (or we can hard-code the data for testing)")

# ====================== EMPLOYEE DATA (you can edit here or load from spreadsheets) ======================
employees = {
    "Annemiek": {"cao": "Tankstations en Wasbedrijven", "hours": 28, "vacation_entitlement": 20},
    "Tobias": {"cao": "Motorvoertuigen- en Tweewielerbedrijf", "hours": 40, "vacation_entitlement": 23},
    "Job": {"cao": "Motorvoertuigen- en Tweewielerbedrijf", "hours": 38, "vacation_entitlement": 23},
    "Oleg": {"cao": "ICK / ICT-CAO 2025-2026", "hours": 40, "vacation_entitlement": 23}
}

# ====================== GROK CHAT ======================
st.subheader("💬 Ask anything about CAO, contracts, vacation, sick days, lateness...")

client = OpenAI(
    api_key=st.secrets.get("GROK_API_KEY", "YOUR_XAI_KEY_HERE"),  # we'll set this in secrets
    base_url="https://api.x.ai/v1"
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Type your question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # System prompt with ALL your CAO + contract knowledge
    system_prompt = f"""You are the official CBS Automotive CAO & HR assistant.
    You know EVERYTHING about the 3 CAOs and the 4 employees:
    - Annemiek (Carwash): Tankstations CAO, 28h, 20 vacation days
    - Tobias (Sales): Motorvoertuigen CAO, 40h, 23 vacation days + bonus
    - Job (BBL monteur): Motorvoertuigen CAO, 38h, 23 vacation days
    - Oleg (Programmer): ICK/ICT CAO, 40h, 23 vacation days
    Always answer in normal Dutch or English depending on the question.
    Use the uploaded spreadsheet data when available.
    Employee mode = only show own data. Admin mode = show everything.
    Current role: {st.session_state.role}"""

    with st.chat_message("assistant"):
        with st.spinner("Grok is thinking..."):
            response = client.chat.completions.create(
                model="grok-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.messages
                ],
                temperature=0.7
            )
            answer = response.choices[0].message.content
            st.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})