import streamlit as st
import pandas as pd

st.set_page_config(page_title="📱 WhatsApp Tool", layout="wide")

# Session state setup
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["ID", "Name", "Phone"])
if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# Format phone
def format_phone(phone):
    phone = str(phone).strip()
    if not phone.startswith("+"):
        if phone.startswith("91"):
            return "+" + phone
        elif len(phone) == 10:
            return "+91" + phone
    return phone

st.title("📊 Excel WhatsApp Tool")

# Upload Excel
uploaded_file = st.file_uploader("📤 Upload Excel (must include ID, Name, Phone)", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    if all(col in df.columns for col in ["ID", "Name", "Phone"]):
        df["Phone"] = df["Phone"].apply(format_phone)
        st.session_state.data = pd.concat([st.session_state.data, df], ignore_index=True).drop_duplicates("ID").reset_index(drop=True)
        st.success("✅ Excel Loaded Successfully!")
    else:
        st.error("❌ Excel must contain ID, Name, Phone columns.")

# Add new entry
if st.button("➕ Add New"):
    st.session_state.show_add_form = True

if st.session_state.show_add_form:
    with st.form("add_form"):
        new_id = st.text_input("ID")
        new_name = st.text_input("Name")
        new_phone = st.text_input("Phone (e.g., 9876543210)")
        submit = st.form_submit_button("Submit")
        if submit:
            formatted_phone = format_phone(new_phone)
            new_row = pd.DataFrame([[new_id, new_name, formatted_phone]], columns=["ID", "Name", "Phone"])
            st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
            st.success("✅ Member Added!")
            st.session_state.show_add_form = False

# Search
search_term = st.text_input("🔍 Search by ID, Name, Phone", "")
if search_term:
    filtered_data = st.session_state.data[
        st.session_state.data["ID"].astype(str).str.contains(search_term, case=False, na=False) |
        st.session_state.data["Name"].astype(str).str.contains(search_term, case=False, na=False) |
        st.session_state.data["Phone"].astype(str).str.contains(search_term, case=False, na=False)
    ]
else:
    filtered_data = st.session_state.data

# Select All
select_all = st.checkbox("✅ Select All")
selected_indexes = []

# Message input
st.subheader("💬 Message (use `{name}` and `{id}` to personalize)")
message = st.text_area("Enter your message", "Hi {name}, your ID is {id}. Stay strong and keep going! 💪")

st.subheader("👥 View & Manage Members")
for i, row in filtered_data.iterrows():
    col1, col2, col3, col4, col5, col6 = st.columns([0.5, 2, 2, 2, 1, 1])
    with col1:
        checked = st.checkbox("", key=f"chk_{i}", value=select_all)
        if checked:
            selected_indexes.append(i)

    with col2:
        st.text_input("Name", value=row["Name"], key=f"name_{i}", disabled=True)

    with col3:
        st.text_input("Phone", value=row["Phone"], key=f"phone_{i}", disabled=True)

    with col4:
        st.text_input("ID", value=row["ID"], key=f"id_{i}", disabled=True)

    with col5:
        if st.button("✏️ Edit", key=f"edit_{i}"):
            st.session_state.edit_index = i

    with col6:
        if st.button("🗑️ Delete", key=f"del_{i}"):
            st.session_state.data.drop(index=row.name, inplace=True)
            st.session_state.data.reset_index(drop=True, inplace=True)
            st.rerun()

# Edit section
if st.session_state.edit_index is not None:
    idx = st.session_state.edit_index
    st.subheader("✏️ Edit Member")
    with st.form("edit_form"):
        edit_id = st.text_input("Edit ID", value=st.session_state.data.at[idx, "ID"])
        edit_name = st.text_input("Edit Name", value=st.session_state.data.at[idx, "Name"])
        edit_phone = st.text_input("Edit Phone", value=st.session_state.data.at[idx, "Phone"])
        save = st.form_submit_button("Save Changes")
        if save:
            st.session_state.data.at[idx, "ID"] = edit_id
            st.session_state.data.at[idx, "Name"] = edit_name
            st.session_state.data.at[idx, "Phone"] = format_phone(edit_phone)
            st.session_state.edit_index = None
            st.success("✅ Changes Saved!")
            st.rerun()

# Send WhatsApp - Generate message links
if st.button("📤 Generate WhatsApp Links"):
    if not selected_indexes:
        st.warning("⚠️ Select at least one member.")
    else:
        st.subheader("📲 WhatsApp Message Links")
        for i in selected_indexes:
            person = filtered_data.iloc[i]
            phone = person["Phone"].replace("+", "")
            name = person["Name"]
            id_ = person["ID"]
            final_message = message.replace("{name}", name).replace("{id}", str(id_))
            encoded_msg = final_message.replace(" ", "%20").replace("\n", "%0A")
            link = f"https://wa.me/{phone}?text={encoded_msg}"
            st.markdown(f"👉 [Message {name} on WhatsApp]({link})", unsafe_allow_html=True)

# Delete All
if st.button("🧹 Clear All Data"):
    st.session_state.data = pd.DataFrame(columns=["ID", "Name", "Phone"])
    st.success("🗑️ All data deleted!")

# ✅ Add this block right below ⬇️

# Remove duplicate IDs and preserve manual additions
st.session_state.data.drop_duplicates("ID", keep="last", inplace=True)
st.session_state.data.reset_index(drop=True, inplace=True)

# Save Button Style Fix
st.markdown("""
    <style>
        .stButton > button {
            background-color: #25D366;
            color: white;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# CSV Download Option
st.subheader("⬇️ Download Current Data")
csv = st.session_state.data.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download CSV", data=csv, file_name='whatsapp_members.csv', mime='text/csv')

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center;'>"
    "Made with ❤️ by Harshavasa | "
    "<a href='https://github.com/yourgithubrepo' target='_blank'>GitHub</a>"
    "</div>",
    unsafe_allow_html=True
)

