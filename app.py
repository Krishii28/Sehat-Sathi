import streamlit as st

st.set_page_config(page_title="Sehat Saathi", page_icon="🩺")
st.title("🩺 Sehat Saathi")
st.write("Hello, I am here to help you! 👋")
st.write("Write your problem, speak or send photo.")

# --- SMART DOCTOR LOGIC (No Ollama needed) ---
def get_answer(user_text):
    text = user_text.lower()

    if "fever" in text or "bukhar" in text or "temperature" in text:
        return "🌡️ **Fever ke liye:**\n\n1. Zyada paani piyo\n2. Halka khana khao\n3. Paracetamol doctor ki salah se le sakte ho\n4. Agar 3 din se zyada fever hai toh doctor ko dikhao."
    
    elif "body" in text and "pain" in text or "paining" in text or "dard" in text:
        return "💪 **Body Pain ke liye:**\n\n1. Acche se rest karo\n2. Garam paani se sikai karo\n3. Halki stretching karo\n4. Zyada paani piyo\n\nAgar pain bahut zyada hai ya 2-3 din se hai, toh doctor ko jarur dikhao."
    
    elif "cold" in text or "cough" in text or "khansi" in text or "sardi" in text:
        return "🤧 **Cold & Cough ke liye:**\n\n1. Garam paani + haldi piyo\n2. Steam lo\n3. Thandi cheezein mat khao\n4. Rest karo"
    
    elif "headache" in text or "sir" in text and "dard" in text or "head" in text:
        return "🤕 **Headache ke liye:**\n\n1. Thoda rest karo, phone kam chalao\n2. Paani piyo\n3. Light me baitho\n4. Agar roz headache ho raha hai toh doctor ko dikhao."
    
    elif "stomach" in text or "pet" in text or "gas" in text:
        return "🤰 **Stomach Problem ke liye:**\n\n1. Halka khana khao - khichdi, dahi\n2. Zyada mirch-masala mat khao\n3. ORS / paani piyo"
    
    elif "hi" in text or "hello" in text or "hey" in text:
        return "Hello! 👋 Batao kya problem hai? Jaise - fever, cold, body pain, headache"
    
    else:
        return f"Samajh gayi, tumhe **'{user_text}'** ki problem hai.\n\n1. Rest karo aur paani zyada piyo\n2. Agar problem 2-3 din se zyada hai toh doctor ko dikhao\n\nTum thoda detail me batao - jaise kahan dard hai, kab se hai?"

# --- CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Apni problem likho... jaise - my whole body is paining"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    answer = get_answer(prompt)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)

# --- SIDEBAR FEATURES ---
st.sidebar.title("Menu")
choice = st.sidebar.selectbox("Choose", ["AI Doctor", "BMI Calculator", "Medicine Reminder"])

if choice == "BMI Calculator":
    st.sidebar.header("BMI Calculator")
    w = st.sidebar.number_input("Weight (kg)", 30, 120, 60)
    h = st.sidebar.number_input("Height (cm)", 120, 200, 165)
    if st.sidebar.button("Calculate BMI"):
        bmi = w / ((h/100)**2)
        st.sidebar.success(f"Tumhara BMI hai: {bmi:.1f}")
        if bmi < 18.5:
            st.sidebar.write("Underweight - thoda acche se khao")
        elif bmi < 25:
            st.sidebar.write("Perfect! Normal hai ✅")
        else:
            st.sidebar.write("Thoda overweight hai, exercise karo")

if choice == "Medicine Reminder":
    st.sidebar.header("Medicine Reminder")
    med = st.sidebar.text_input("Dawai ka naam")
    time = st.sidebar.time_input("Time")
    if st.sidebar.button("Set Reminder"):
        st.sidebar.success(f"Reminder set! {med} - {time} ko lena hai 💊")
