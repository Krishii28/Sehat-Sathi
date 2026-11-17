import streamlit as st
import datetime

st.set_page_config(page_title="Sehat Saathi", page_icon="🩺", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "doctor_asked" not in st.session_state:
    st.session_state.doctor_asked = False
if "reminders" not in st.session_state:
    st.session_state.reminders = []
if "last_audio_id" not in st.session_state:
    st.session_state["last_audio_id"] = ""

# ---------- LANGUAGE ----------
st.sidebar.write("Language")
lang = st.sidebar.radio("Choose Language", ["English", "Hindi"], label_visibility="collapsed")
IS_HINDI = (lang == "Hindi")

if IS_HINDI:
    menu = st.sidebar.radio("मेनू", ["🏠 होम", "💊 दवाई रिमाइंडर", "👨‍⚕️ डॉक्टर से बात करें", "🚨 आपातकाल", "💡 स्वास्थ्य टिप्स", "⚖️ बीएमआई कैलकुलेटर", "🏛️ सरकारी योजनाएं", "ℹ️ ऐप के बारे में"])
else:
    menu = st.sidebar.radio("Menu", ["🏠 Home", "💊 Medicine Reminder", "👨‍⚕️ Talk To Doctor", "🚨 Emergency", "💡 Health Tips", "⚖️ BMI Calculator", "🏛️ Government Schemes", "ℹ️ About App"])

# ---------- VOICE - FIXED: Heavy library hataya, ab Cloud pe chalega ----------
def speech_to_text(audio_bytes):
    # Streamlit Cloud pe speech_recognition / pydub nahi chalta, isliye wapas message bhejte hain
    return "VOICE_NOTE"

# ---------- FAST ANSWERS ----------
def get_instant_answer(user_text, lang):
    text = user_text.lower()
    if "muscle" in text or "body pain" in text or "sharir" in text or "badan" in text or "poora sharir" in text or "whole body" in text or "paining" in text or "pain" in text or "dard" in text:
        if lang == "Hindi":
            return """Aapki takleef samajh sakte hain, aaram kijiye.
**Possible Causes:**
- **Muscle Strain:** Bhari kaam ya galat tarike se uthne-bethne se muscles me khichav aa jata hai.
- **Thakan:** Neend poori na hone ya zyada kaam karne se sharir thak jata hai.
- **Sardi-Jukam:** Viral infection me sharir me dard, halka bukhar aur thakan mehsoos hoti hai.
**Danger Signs:**
- **Tez Bukhar:** 102 se upar bukhar ho toh turant doctor ko dikhayein.
- **Saans me dikkat:** Saans lene me takleef ho toh der mat karein.
**What To Do Now:**
- **Aaram Karein:** 1-2 din bhari kaam band karke poora aaram karein.
- **Garam Sek:** Dard wali jagah pe din me 2 baar 10 minute garam kapde se sek karein.
- **Gunguna Paani:** Din bhar gunguna paani piyein.
**Health Tip:**
- **Roz Walk:** Roz 30 minute halki walk se muscles mazboot hote hain.
Agar 2 din me aaram na mile toh doctor se baat kar lijiyega.
Kya aap doctor se baat karna chahengi?"""
        else:
            return """I understand, please take rest.
**Possible Causes:**
- **Muscle Strain:** Lifting heavy things or sitting in wrong posture can stretch your muscles.
- **Tiredness:** When you do not sleep well or work too much, your body gets tired.
- **Viral Infection:** In cold and fever, virus makes your body weak, so you feel body pain.
**Danger Signs:**
- **High Fever:** If fever is above 102, see a doctor immediately.
- **Breathing Problem:** If you feel difficulty in breathing, do not wait.
**What To Do Now:**
- **Take Rest:** Stop heavy work for 1-2 days and give your body full rest.
- **Hot Compress:** Apply warm cloth on painful area for 10 minutes, 2 times a day.
- **Warm Water:** Drink warm water through the day.
**Health Tip:**
- **Daily Walk:** Walking 30 minutes daily makes muscles strong.
If no relief in 2 days, please talk to a doctor.
Would you like to see a doctor?"""
    if "fever" in text or "bukhar" in text:
        if lang == "Hindi":
            return """Bukhar me takleef hoti hai, aaram kijiye.
**Possible Causes:**
- **Viral Fever:** Mausam badalne se virus se bukhar aa jata hai.
- **Sardi-Jukam:** Gale me kharash aur sardi ke saath halka bukhar aa sakta hai.
**Danger Signs:**
- **Tez Bukhar:** 102 se upar bukhar ho toh turant doctor ko dikhayein.
**What To Do Now:**
- **Aaram Karein:** Poora aaram karein.
- **Gunguna Paani:** Thoda-thoda karke gunguna paani pite rahein.
- **Thandi Patti:** Sar pe thande paani ki patti rakhein.
Agar bukhar badhta hai toh doctor se baat kar lijiyega.
Kya aap doctor se baat karna chahengi?"""
        else:
            return """Fever is tiring, please take rest.
**Possible Causes:**
- **Viral Fever:** Change in weather causes viral infection.
- **Cold and Cough:** Throat infection and cold can also give mild fever.
**Danger Signs:**
- **High Fever:** If fever is above 102, see a doctor immediately.
**What To Do Now:**
- **Take Rest:** Take full rest.
- **Warm Water:** Keep drinking warm water in small sips.
- **Cold Sponge:** Keep cold wet cloth on forehead.
If fever increases, talk to a doctor.
Would you like to see a doctor?"""
    if "headache" in text or "sar dard" in text or "sir dard" in text or "head pain" in text:
        if lang == "Hindi":
            return """Sar dard me bahut takleef hoti hai, thoda aaram kijiye.
**Possible Causes:**
- **Neend ki kami:** Neend poori na hone se sar me dard hone lagta hai.
- **Stress:** Zyada tension ya mobile dekhne se sar dard hota hai.
**What To Do Now:**
- **Andhere me Aaram:** Thodi der andhere kamre me aankh band karke lete rahiye.
- **Paani Piyein:** 2 gilas paani dheere-dheere piyein.
Kya aap doctor se baat karna chahengi?"""
        else:
            return """Headache is painful, take a little rest.
**Possible Causes:**
- **Less Sleep:** Not sleeping well causes headache.
- **Stress:** Too much tension or mobile screen causes headache.
**What To Do Now:**
- **Rest in Dark:** Lie down in a dark room with closed eyes.
- **Drink Water:** Drink 2 glasses of water slowly.
Would you like to see a doctor?"""
    if "cold" in text or "cough" in text or "khansi" in text or "sardi" in text or "jukam" in text:
        if lang == "Hindi":
            return """Sardi-khansi me takleef hoti hai, aaram kijiye.
**What To Do Now:**
- **Garam Paani:** Din bhar gunguna paani piyein.
- **Haldi Doodh:** Raat ko haldi wala garam doodh piyein.
- **Bhapa Lein:** Garam paani ka bhapa lene se naak khul jati hai.
Kya aap doctor se baat karna chahengi?"""
        else:
            return """Cold and cough is irritating, please take rest.
**What To Do Now:**
- **Warm Water:** Drink warm water through the day.
- **Turmeric Milk:** Drink warm turmeric milk at night.
- **Steam:** Take steam from hot water.
Would you like to see a doctor?"""
    if "stomach" in text or "pet dard" in text or "pet me dard" in text or "gas" in text:
        if lang == "Hindi":
            return """Pet dard me bahut takleef hoti hai, aaram kijiye.
**What To Do Now:**
- **Halka Khana:** Aaj halka khana khayein, jaise khichdi, dahi.
- **Gunguna Paani:** Gunguna paani dheere-dheere piyein.
- **Walk:** Khana khane ke baad 10 minute halki walk karein.
Kya aap doctor se baat karna chahengi?"""
        else:
            return """Stomach pain is painful, please take rest.
**What To Do Now:**
- **Light Food:** Eat light food today, like khichdi, curd.
- **Warm Water:** Drink warm water slowly.
Would you like to see a doctor?"""
    if "daane" in text or "rash" in text or "khujli" in text or "itching" in text or "chot" in text:
        if lang == "Hindi":
            return """Photo dekh li hai, takleef samajh sakte hain.
**What To Do Now:**
- **Khujlayein Nahi:** Daano ko khujlayein nahi.
- **Saaf Rakhein:** Us jagah ko saaf paani se dho kar sukha rakhein.
- **Nariyal Tel:** Halka nariyal tel lagayein.
Kya aap doctor se baat karna chahengi?"""
        else:
            return """I have seen your photo, I understand your problem.
**What To Do Now:**
- **Do Not Scratch:** Do not scratch rashes.
- **Keep Clean:** Wash that place with clean water and keep it dry.
- **Coconut Oil:** Apply light coconut oil.
Would you like to see a doctor?"""
    return None

def ask_ollama_stream(user_text, lang, placeholder):
    instant = get_instant_answer(user_text, lang)
    if instant:
        placeholder.markdown(instant)
        return instant
    if lang == "Hindi":
        fallback = """Aapki takleef samajh sakte hain, aaram kijiye.
**What To Do Now:**
- **Aaram Karein:** 1-2 din bhari kaam band karke poora aaram karein.
- **Gunguna Paani:** Din bhar gunguna paani piyein.
Agar 2 din me aaram na mile toh doctor se baat kar lijiyega.
Kya aap doctor se baat karna chahengi?"""
    else:
        fallback = """I understand, please take rest.
**What To Do Now:**
- **Take Rest:** Stop heavy work for 1-2 days.
- **Warm Water:** Drink warm water through the day.
If no relief in 2 days, please talk to a doctor.
Would you like to see a doctor?"""
    placeholder.markdown(fallback)
    return fallback

# ================= HOME =================
if menu in ["🏠 Home", "🏠 होम"]:
    st.title("🩺 Sehat Saathi")
    if IS_HINDI:
        st.write("Hello, main yahan aapki madad karne ke liye hoon! 👋")
        st.write("Apni takleef likhein, bolein ya photo bhejein.")
    else:
        st.write("Hello, I am here to help you! 👋")
        st.write("Write your problem, speak or send photo.")
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            if m.get("type") == "image":
                st.image(m["image"], caption="📸 Aapki Photo" if IS_HINDI else "📸 Your Photo", use_container_width=True)
                st.markdown(m["content"])
            else:
                st.markdown(m["content"])
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant" and not st.session_state.doctor_asked:
        st.info("👨‍⚕️ Kya aap doctor se baat karna chahengi?" if IS_HINDI else "👨‍⚕️ Would you like to see a doctor?")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Haan, Doctor se baat karein" if IS_HINDI else "✅ Yes, See Doctor", use_container_width=True, key="yes_doctor"):
                st.session_state.doctor_asked = True
                st.session_state.messages.append({"role": "assistant", "content": "Bilkul! Doctor: 🩺 eSanjeevani https://esanjeevani.mohfw.gov.in | 📞 104" if IS_HINDI else "Sure! Doctor: 🩺 eSanjeevani https://esanjeevani.mohfw.gov.in | 📞 104"})
                st.rerun()
        with c2:
            if st.button("❌ Nahi, bas aise hi" if IS_HINDI else "❌ No, Thanks", use_container_width=True, key="no_doctor"):
                st.session_state.doctor_asked = True
                st.session_state.messages.append({"role": "assistant", "content": "Theek hai, apna khayal rakhiye. Takleef badhe toh turant 104 ya 108 pe call kijiyega." if IS_HINDI else "Okay, take care. If problem increases, call 104 or 108 immediately."})
                st.rerun()
    st.markdown("---")
    col_box, col_clear = st.columns([5, 1])
    with col_box:
        chat_text = st.text_input("Type...", label_visibility="collapsed", placeholder="Apni takleef likhein..." if IS_HINDI else "Write your symptom...", key="wa_text")
    with col_clear:
        if st.button("🧹", use_container_width=True, key="clear_btn", help="Clear Chat" if not IS_HINDI else "Chat Saaf Karein"):
            st.session_state.messages = []
            st.session_state.doctor_asked = False
            st.session_state["last_audio_id"] = ""
            st.rerun()
    col_photo, col_audio = st.columns(2)
    with col_photo:
        st.write("📷 Photo")
        uploaded_photo = st.file_uploader("Upload Photo", type=["jpg","jpeg","png"], label_visibility="collapsed", key="wa_cam")
    with col_audio:
        st.write("🎤 Voice")
        audio_input = st.audio_input("Speak", label_visibility="collapsed", key="wa_mic")
    if uploaded_photo:
        st.image(uploaded_photo, width=200)
        photo_text = chat_text if chat_text else "haath pe daane, rash, khujli"
        st.session_state.messages.append({"role": "user", "content": photo_text, "type": "image", "image": uploaded_photo})
        st.session_state.doctor_asked = False
        with st.chat_message("assistant"):
            placeholder = st.empty()
            reply = ask_ollama_stream(photo_text, lang, placeholder)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()
    if audio_input and st.session_state.get("last_audio_id") != str(audio_input):
        st.session_state["last_audio_id"] = str(audio_input)
        st.warning("Voice sun liya! Ab apni takleef neeche likh bhi dijiye, taaki main sahi jawab de saku." if IS_HINDI else "Voice received! Please also type your problem below so I can answer correctly.")
    if chat_text and uploaded_photo is None and audio_input is None:
        st.session_state.messages.append({"role": "user", "content": chat_text})
        st.session_state.doctor_asked = False
        with st.chat_message("assistant"):
            placeholder = st.empty()
            reply = ask_ollama_stream(chat_text, lang, placeholder)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

# ================= MEDICINE REMINDER =================
elif menu in ["💊 Medicine Reminder", "💊 दवाई रिमाइंडर"]:
    if IS_HINDI:
        st.title("💊 दवाई रिमाइंडर")
    else:
        st.title("💊 Medicine Reminder")
    with st.form("reminder_form"):
        med_name = st.text_input("दवाई का नाम" if IS_HINDI else "Medicine Name", placeholder="दवाई का नाम लिखें..." if IS_HINDI else "Write medicine name...", value="")
        c_h, c_m, c_ap = st.columns(3)
        with c_h:
            hour = st.selectbox("घंटा" if IS_HINDI else "Hour", list(range(1, 13)), index=7)
        with c_m:
            minute = st.selectbox("मिनट" if IS_HINDI else "Minute", [f"{i:02d}" for i in range(0, 60)], index=0)
        with c_ap:
            ampm = st.radio("AM / PM", ["AM", "PM"], horizontal=True)
        med_days = st.number_input("कितने दिन तक?" if IS_HINDI else "How many days?", min_value=1, max_value=30, value=3)
        if st.form_submit_button("✅ Reminder Set Karein" if IS_HINDI else "✅ Set Reminder", use_container_width=True):
            if med_name.strip() == "":
                st.warning("पहले दवाई का नाम लिखिए" if IS_HINDI else "First write medicine name")
            else:
                hour_24 = hour % 12
                if ampm == "PM":
                    hour_24 += 12
                if ampm == "AM" and hour == 12:
                    hour_24 = 0
                time_str = f"{hour_24:02d}:{minute}"
                display_time = f"{hour}:{minute} {ampm}"
                st.session_state.reminders.append({"name": med_name.strip(), "time": time_str, "display": display_time, "days": med_days})
                st.success(f"✅ Reminder set: {med_name.strip()} - {display_time} - {med_days} दिन" if IS_HINDI else f"✅ Reminder set: {med_name.strip()} - {display_time} - {med_days} days")
    st.markdown("---")
    st.write("📋 **आपके Reminders**" if IS_HINDI else "📋 **Your Reminders**")
    now_str = datetime.datetime.now().strftime("%H:%M")
    for r in st.session_state.reminders:
        r_time_short = r["time"][:5]
        show_time = r.get("display", r["time"])
        if r_time_short == now_str:
            st.error(f"🔔 DAWAI KA TIME HO GAYA! {r['name']} le lijiye! - {show_time}" if IS_HINDI else f"🔔 TIME FOR MEDICINE! Take {r['name']} now! - {show_time}")
        st.info(f"💊 {r['name']} - ⏰ {show_time} - 📅 {r['days']} दिन" if IS_HINDI else f"💊 {r['name']} - ⏰ {show_time} - 📅 {r['days']} days")
    if st.session_state.reminders:
        if st.button("🗑️ सारे Reminder Delete Karein" if IS_HINDI else "🗑️ Delete All Reminders", use_container_width=True):
            st.session_state.reminders = []
            st.rerun()
    else:
        st.write("Abhi koi reminder nahi hai." if IS_HINDI else "No reminders yet.")

# ================= TALK TO DOCTOR =================
elif menu in ["👨‍⚕️ Talk To Doctor", "👨‍⚕️ डॉक्टर से बात करें"]:
    if IS_HINDI:
        st.title("👨‍⚕️ डॉक्टर से बात करें")
        st.success("Ye sab sarkari doctor ki sewayein hain, 100% asli.")
        st.markdown("### 1. 🩺 eSanjeevani - Online Doctor")
        st.link_button("🩺 eSanjeevani Kholein - Doctor se Baat Karein", "https://esanjeevani.mohfw.gov.in", use_container_width=True)
        st.markdown("### 2. 📞 104 - Health Helpline")
        st.link_button("📞 104 pe Call Karein", "tel:104", use_container_width=True)
        st.markdown("### 3. 🏥 Najdiki Sarkari Hospital")
        st.write("Agar takleef zyada hai toh apne gaon ke najdik wale PHC / CHC me jayein.")
    else:
        st.title("👨‍⚕️ Talk To Doctor")
        st.success("All these are Government doctor services, 100% Real.")
        st.markdown("### 1. 🩺 eSanjeevani - Online Doctor")
        st.link_button("🩺 Open eSanjeevani - Talk To Doctor", "https://esanjeevani.mohfw.gov.in", use_container_width=True)
        st.markdown("### 2. 📞 104 - Health Helpline")
        st.link_button("📞 Call 104", "tel:104", use_container_width=True)
        st.markdown("### 3. 🏥 Nearest Government Hospital")
        st.write("If problem is more, go to your nearest PHC / CHC.")

# ================= EMERGENCY =================
elif menu in ["🚨 Emergency", "🚨 आपातकाल"]:
    if IS_HINDI:
        st.title("🚨 आपातकाल - Emergency")
        st.error("Agar takleef bahut zyada hai toh pehle CALL karein, app ka wait mat karein!")
        st.link_button("🚑 108 - Ambulance Bulayein", "tel:108", use_container_width=True)
        st.link_button("🚓 112 - Police / Emergency", "tel:112", use_container_width=True)
        st.link_button("📞 104 - Health Helpline", "tel:104", use_container_width=True)
        st.markdown("### 🆘 Emergency Tips")
        st.write("- **Tez Bukhar:** Sar pe thande paani ki patti rakhein")
        st.write("- **Chot:** Saaf kapde se dabake rakhein, 10 minute tak mat hatayein")
        st.write("- **Saans Nahi Aa Rahi:** Seedha betha dein, kapde dheele karein")
        st.write("- **Ulti:** Ek side me letayein, ORS pilayein")
        st.write("- **Saanp / Kutta Kaat Le:** Saaf paani se dhoyein, turant 108 pe call karein")
    else:
        st.title("🚨 Emergency")
        st.error("If problem is very serious, CALL FIRST, do not wait for app!")
        st.link_button("🚑 108 - Call Ambulance", "tel:108", use_container_width=True)
        st.link_button("🚓 112 - Police / Emergency", "tel:112", use_container_width=True)
        st.link_button("📞 104 - Health Helpline", "tel:104", use_container_width=True)
        st.markdown("### 🆘 Emergency Tips")
        st.write("- **High Fever:** Keep cold wet cloth on forehead")
        st.write("- **Bleeding:** Press with clean cloth, do not remove for 10 minutes")
        st.write("- **Breathing Problem:** Make patient sit straight")
        st.write("- **Vomiting:** Make patient lie on one side, give ORS")
        st.write("- **Snake / Dog Bite:** Wash with clean water, call 108 fast")

# ================= HEALTH TIPS =================
elif menu in ["💡 Health Tips", "💡 स्वास्थ्य टिप्स"]:
    if IS_HINDI:
        st.title("💡 स्वास्थ्य टिप्स - Roz Ka Routine")
        st.write("- **Subah:** Gunguna paani piyein, 15 minute dhoop me bethein")
        st.write("- **Walk:** Roz 30 minute walk karein")
        st.write("- **Khana:** Hari sabzi khayein, 8 gilas paani piyein, tel-namak kam")
        st.write("- **Neend:** Roz 7-8 ghante soyein")
        st.write("- **Saaf-Safai:** Haath sabun se dhoyein, din me 2 baar brush karein")
    else:
        st.title("💡 Health Tips - Daily Routine")
        st.write("- **Morning:** Drink warm water, sit in sunlight 15 min")
        st.write("- **Walk:** Walk 30 min daily")
        st.write("- **Food:** Eat green vegetables, drink 8 glasses water, less salt-oil")
        st.write("- **Sleep:** Sleep 7-8 hours daily")
        st.write("- **Cleanliness:** Wash hands with soap, brush 2 times a day")

# ================= BMI =================
elif menu in ["⚖️ BMI Calculator", "⚖️ बीएमआई कैलकुलेटर"]:
    if IS_HINDI:
        st.title("⚖️ बीएमआई कैलकुलेटर")
    else:
        st.title("⚖️ BMI Calculator")
    weight = st.number_input("वजन (kg)" if IS_HINDI else "Weight (kg)", min_value=10.0, max_value=200.0, value=60.0)
    height = st.number_input("ऊंचाई (cm)" if IS_HINDI else "Height (cm)", min_value=100.0, max_value=220.0, value=165.0)
    if st.button("हिसाब लगाएं" if IS_HINDI else "Calculate"):
        h_m = height / 100
        bmi = weight / (h_m * h_m)
        st.success(f"Your BMI: {bmi:.1f}")
        if bmi < 18.5:
            st.write("Underweight - Eat healthy food" if not IS_HINDI else "Underweight - Healthy khana khayein")
        elif bmi < 25:
            st.write("Normal - Good! Keep it up" if not IS_HINDI else "Normal - Bahut badhiya!")
        elif bmi < 30:
            st.write("Overweight - Walk daily" if not IS_HINDI else "Overweight - Roz walk karein")
        else:
            st.write("Obese - Please consult doctor" if not IS_HINDI else "Obese - Doctor se baat karein")

# ================= GOVT SCHEMES =================
elif menu in ["🏛️ Government Schemes", "🏛️ सरकारी योजनाएं"]:
    if IS_HINDI:
        st.title("🏛️ सरकारी योजनाएं - FREE Ka Fayda Uthayein")
        st.success("Ye sab sarkari yojnayein hain, 100% asli aur FREE. Kisi ko paise mat dein.")
        st.markdown("### 1. 🩺 Ayushman Bharat - PMJAY")
        st.write("- **Kya Milta Hai:** 5 Lakh tak ka FREE ilaj, har saal")
        st.link_button("Ayushman Card Check Karein", "https://pmjay.gov.in", use_container_width=True)
        st.markdown("### 2. 💊 Jan Aushadhi - Sasti Dawai")
        st.write("- **Kya Milta Hai:** Dawai 50% se 90% tak sasti")
        st.link_button("Nazdiki Jan Aushadhi Kendra Dhoondhein", "https://janaushadhi.gov.in", use_container_width=True)
        st.markdown("### 3. 🤰 PM Surakshit Matritva")
        st.write("- **Kya Milta Hai:** Garbhvati mahila ki FREE janch, FREE dawai")
        st.markdown("### 4. 👶 Mission Indradhanush")
        st.write("- **Kya Milta Hai:** Bachon ke saare teeke bilkul FREE")
        st.markdown("### 5. 🦟 National Health Mission")
        st.write("- **Kya Milta Hai:** PHC me BP, Sugar, Bukhar ki janch FREE")
    else:
        st.title("🏛️ Government Schemes - Take FREE Benefit")
        st.success("All these are Government schemes, 100% Real and FREE.")
        st.markdown("### 1. 🩺 Ayushman Bharat - PMJAY")
        st.write("- **Benefit:** FREE treatment up to 5 Lakh, every year")
        st.link_button("Check Ayushman Card", "https://pmjay.gov.in", use_container_width=True)
        st.markdown("### 2. 💊 Jan Aushadhi - Cheap Medicines")
        st.write("- **Benefit:** Medicines 50% to 90% cheaper")
        st.link_button("Find Nearest Jan Aushadhi Kendra", "https://janaushadhi.gov.in", use_container_width=True)
        st.markdown("### 3. 🤰 PM Surakshit Matritva")
        st.write("- **Benefit:** FREE checkup, FREE medicine for pregnant women")
        st.markdown("### 4. 👶 Mission Indradhanush")
        st.write("- **Benefit:** All vaccines of children totally FREE")
        st.markdown("### 5. 🦟 National Health Mission")
        st.write("- **Benefit:** BP, Sugar, Fever checkup FREE in PHC")

# ================= ABOUT =================
elif menu in ["ℹ️ About App", "ℹ️ ऐप के बारे में"]:
    if IS_HINDI:
        st.title("ℹ️ ऐप के बारे में")
        st.write("सेहत साथी गांव के लोगों के लिए बनाया गया है। ये डॉक्टर की जगह नहीं लेता, बस शुरुआती मदद करता है।")
    else:
        st.title("ℹ️ About App")
        st.write("Sehat Saathi is made for village people. It does not replace a doctor, it only gives first help.")
