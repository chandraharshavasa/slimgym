import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Set up page and session state
st.set_page_config(page_title="📱 WhatsApp Tool", layout="wide")

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["ID", "Name", "Phone"])
if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# Format phone numbers
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

# Search & display data
search_term = st.text_input("🔍 Search by ID, Name, Phone", "")
filtered_data = st.session_state.data[
    st.session_state.data["ID"].astype(str).str.contains(search_term, case=False, na=False) |
    st.session_state.data["Name"].astype(str).str.contains(search_term, case=False, na=False) |
    st.session_state.data["Phone"].astype(str).str.contains(search_term, case=False, na=False)
] if search_term else st.session_state.data

# WhatsApp Message Setup
st.subheader("💬 Message (use `{name}` and `{id}` to personalize)")
message = st.text_area("Enter your message", "Hi {name}, your ID is {id}. Stay strong and keep going! 💪")

# Button to send WhatsApp message via web
if st.button("📤 Send Messages via WhatsApp Web"):
    selected_indexes = [i for i, row in filtered_data.iterrows() if st.checkbox(f"Select {row['Name']}", key=f"select_{i}")]
    if not selected_indexes:
        st.warning("⚠️ Select at least one member.")
    else:
        st.info("🔄 Sending messages, please wait...")
        
        # Start Selenium WebDriver
        options = Options()
        options.add_argument("--headless")  # Run in headless mode
        service = Service("path/to/chromedriver")  # Provide path to ChromeDriver
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://web.whatsapp.com/")
        
        # Wait for WhatsApp Web to load and scan QR code
        st.info("🔄 Waiting for QR code scan...")
        time.sleep(20)  # Wait for QR scan

        for i in selected_indexes:
            person = filtered_data.iloc[i]
            phone = person["Phone"].replace("+", "")
            name = person["Name"]
            id_ = person["ID"]
            final_message = message.replace("{name}", name).replace("{id}", str(id_))
            
            # Open chat window with phone number
            driver.get(f"https://web.whatsapp.com/send?phone={phone}&text={final_message}")
            time.sleep(5)  # Allow time for the chat to load
            
            # Find send button and click it
            try:
                send_button = driver.find_element(By.XPATH, "//span[@data-icon='send']")
                send_button.click()
                time.sleep(2)
                st.success(f"✅ Message sent to {name}")
            except Exception as e:
                st.error(f"❌ Error sending message to {name}: {str(e)}")
        
        driver.quit()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center;'>"
    "Made with ❤️ by Harshavasa | "
    "<a href='https://github.com/yourgithubrepo' target='_blank'>GitHub</a>"
    "</div>",
    unsafe_allow_html=True
)
