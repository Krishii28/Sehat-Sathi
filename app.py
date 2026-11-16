import streamlit as st
import requests
import json
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

# ---------- LANGUAGE - SIRF EK HI LANGUAGE DIKHEGI ----------
st.sidebar.write("Language")
lang = st.sidebar.radio("Choose Language", ["English", "Hindi"], label_visibility="collapsed")
IS_HINDI = (lang == "Hindi")

# ---------- MENU - SIRF EK LANGUAGE ----------
if IS_HINDI:
    menu = st.sidebar.radio("मेनू", ["🏠 होम", "💊 दवाई रिमाइंडर", "👨‍⚕️ डॉक्टर से बात करें", "🚨 आपातकाल", "💡 स्वास्थ्य टिप्स", "⚖️ बीएमआई कैलकुलेटर", "🏛️ सरकारी योजनाएं", "ℹ️ ऐप के बारे में"])
else:
    menu = st.sidebar.radio("Menu", ["🏠 Home", "💊 Medicine Reminder", "👨‍⚕️ Talk To Doctor", "🚨 Emergency", "💡 Health Tips", "⚖️ BMI Calculator", "🏛️ Government Schemes", "ℹ️ About App"])

# ---------- VOICE INPUT ONLY - SIRF BOLNE KE LIYE, JAWAB TEXT ME HI AAYEGA ----------
def speech_to_text(audio_bytes):
    try:
        import speech_recognition as sr
        import io
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        r = sr.Recognizer()
        r.energy_threshold = 300
        r.dynamic_energy_threshold = True
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
            if len(audio) < 1000:
                return "TOO_SHORT"
            wav_io = io.BytesIO()
            audio.export(wav_io, format="wav")
            wav_io.seek(0)
            with sr.AudioFile(wav_io) as source:
                audio_data = r.record(source)
                try:
                    text = r.recognize_google(audio_data, language="en-IN")
                    return text
                except:
                    text = r.recognize_google(audio_data, language="hi-IN")
                    return text
        except Exception as e1:
            print(f"Pydub fail: {e1}")
            try:
                with sr.AudioFile(tmp_path) as source:
                    audio_data = r.record(source)
                    text = r.recognize_google(audio_data, language="en-IN")
                    return text
            except Exception as e2:
                print(f"Direct fail: {e2}")
                return f"ERROR:{str(e2)[:100]}"
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    except Exception as e:
        return f"ERROR:{str(e)[:100]}"

# ---------- FAST ANSWERS ----------
def get_instant_answer(user_text, lang):
    text = user_text.lower()
    if "muscle" in text or "body pain" in text or "sharir" in text or "badan" in text or "poora sharir" in text:
        if lang == "Hindi":
            return """Aapki takleef samajh sakte hain, aaram kijiye.

**Possible Causes:**
- **Muscle Strain:** Bhari kaam ya galat tarike se uthne-bethne se muscles me khichav aa jata hai, isliye poora sharir dukhne lagta hai.
- **Thakan:** Neend poori na hone ya zyada kaam karne se sharir thak jata hai aur dard hone lagta hai.
- **Sardi-Jukam:** Viral infection me sharir me dard, halka bukhar aur thakan mehsoos hoti hai.

**Danger Signs:**
- **Tez Bukhar:** 102 se upar bukhar ho toh turant doctor ko dikhayein.
- **Saans me dikkat:** Saans lene me takleef ho toh der mat karein.

**What To Do Now:**
- **Aaram Karein:** 1-2 din bhari kaam band karke poora aaram karein.
- **Garam Sek:** Dard wali jagah pe din me 2 baar 10 minute garam kapde se sek karein.
- **Gunguna Paani:** Din bhar gunguna paani piyein, isse muscles ko aaram milta hai.

**Health Tip:**
- **Roz Walk:** Roz 30 minute halki walk se muscles mazboot hote hain aur dard kam hota hai.

Aapke sharir me dard zyada lag raha hai, isliye aaj bhari kaam mat kijiye. Agar 2 din me aaram na mile toh doctor se baat kar lijiyega.
Kya aap doctor se baat karna chahengi?"""
        else:
            return """I understand, please take rest.

**Possible Causes:**
- **Muscle Strain:** Lifting heavy things or sitting in wrong posture can stretch your muscles, that is why your whole body pains.
- **Tiredness:** When you do not sleep well or work too much, your body gets tired and starts paining.
- **Viral Infection:** In cold and fever, virus makes your body weak, so you feel body pain and tiredness.

**Danger Signs:**
- **High Fever:** If fever is above 102, see a doctor immediately.
- **Breathing Problem:** If you feel difficulty in breathing, do not wait.

**What To Do Now:**
- **Take Rest:** Stop heavy work for 1-2 days and give your body full rest.
- **Hot Compress:** Apply warm cloth on painful area for 10 minutes, 2 times a day.
- **Warm Water:** Drink warm water through the day, it relaxes your muscles.

**Health Tip:**
- **Daily Walk:** Walking 30 minutes daily makes muscles strong and reduces pain.

Your body pain seems more due to tiredness and strain, so avoid heavy work today. If no relief in 2 days, please talk to a doctor.
Would you like to see a doctor?"""
    if "fever" in text or "bukhar" in text:
        if lang == "Hindi":
            return """Bukhar me takleef hoti hai, aaram kijiye.

**Possible Causes:**
- **Viral Fever:** Mausam badalne se virus se bukhar aa jata hai, isme sharir dard aur thakan hoti hai.
- **Sardi-Jukam:** Gale me kharash aur sardi ke saath halka bukhar aa sakta hai.
- **Paani ki kami:** Paani kam peene se sharir garam ho jata hai aur bukhar jaisa lagta hai.

**Danger Signs:**
- **Tez Bukhar:** 102 se upar bukhar ho toh turant doctor ko dikhayein.
- **Ulti / Chakkar:** Ulti ya chakkar aaye toh der mat karein.

**What To Do Now:**
- **Aaram Karein:** Poora aaram karein, bahar ka kaam band kar dein.
- **Gunguna Paani:** Thoda-thoda karke gunguna paani pite rahein.
- **Thandi Patti:** Sar pe thande paani ki patti rakhein, isse bukhar kam hoga.

**Health Tip:**
- **Tulsi Kadha:** Tulsi, adrak ka kadha peene se bukhar me aaram milta hai.

Bukhar abhi shuru hua hai toh 1 din aaram karke dekhiye, agar bukhar badhta hai toh doctor se baat kar lijiyega.
Kya aap doctor se baat karna chahengi?"""
        else:
            return """Fever is tiring, please take rest.

**Possible Causes:**
- **Viral Fever:** Change in weather causes viral infection, it gives fever with body pain and tiredness.
- **Cold and Cough:** Throat infection and cold can also give mild fever.
- **Less Water:** Drinking less water makes body hot and fever-like.

**Danger Signs:**
- **High Fever:** If fever is above 102, see a doctor immediately.
- **Vomiting / Dizziness:** If you feel vomiting or dizziness, do not wait.

**What To Do Now:**
- **Take Rest:** Take full rest, stop outside work.
- **Warm Water:** Keep drinking warm water in small sips.
- **Cold Sponge:** Keep cold wet cloth on forehead, it reduces fever.

**Health Tip:**
- **Tulsi Kadha:** Tulsi and ginger kadha gives relief in fever.

Your fever seems in starting stage, take rest for 1 day. If fever increases, talk to a doctor.
Would you like to see a doctor?"""
    if "headache" in text or "sar dard" in text or "sir dard" in text or "head pain" in text:
        if lang == "Hindi":
            return """Sar dard me bahut takleef hoti hai, thoda aaram kijiye.

**Possible Causes:**
- **Neend ki kami:** Neend poori na hone se sar me dard hone lagta hai.
- **Stress:** Zyada tension ya mobile dekhne se sar dard hota hai.
- **Paani ki kami:** Paani kam peene se bhi sar dard ho jata hai.

**Danger Signs:**
- **Tez Dard:** Sar me bahut tez dard ho ya ulti aaye toh turant doctor ko dikhayein.
- **Dhundhla Dikhna:** Aankho se dhundhla dikhe toh der mat karein.

**What To Do Now:**
- **Andhere me Aaram:** Thodi der andhere kamre me aankh band karke lete rahiye.
- **Paani Piyein:** 2 gilas paani dheere-dheere piyein.
- **Sar ki Malish:** Halke haath se sar pe malish karein.

**Health Tip:**
- **Mobile Kam:** Mobile aur TV ko thodi der door rakhne se sar dard kam hota hai.

Aapka sar dard neend aur thakan se lag raha hai, thodi der aaram kijiye.
Kya aap doctor se baat karna chahengi?"""
        else:
            return """Headache is painful, take a little rest.

**Possible Causes:**
- **Less Sleep:** Not sleeping well causes headache.
- **Stress:** Too much tension or mobile screen causes headache.
- **Less Water:** Drinking less water also causes headache.

**Danger Signs:**
- **Severe Pain:** If headache is very severe or you feel vomiting, see doctor immediately.
- **Blurry Vision:** If vision becomes blurry, do not wait.

**What To Do Now:**
- **Rest in Dark:** Lie down in a dark room with closed eyes for some time.
- **Drink Water:** Drink 2 glasses of water slowly.
- **Head Massage:** Massage your head gently with light hands.

**Health Tip:**
- **Less Mobile:** Keeping mobile and TV away for some time reduces headache.

Your headache seems due to less sleep and tiredness, take rest for some time.
Would you like to see a doctor?"""
    if "cold" in text or "cough" in text or "khansi" in text or "sardi" in text or "jukam" in text:
        if lang == "Hindi":
            return """Sardi-khansi me takleef hoti hai, aaram kijiye.

**Possible Causes:**
- **Viral Infection:** Mausam badalne se gale me virus lag jata hai, isse sardi-khansi hoti hai.
- **Thanda Paani:** Thanda paani ya ice-cream se gala kharab ho jata hai.
- **Dhool:** Dhool-mitti se allergy ho jati hai aur khansi aane lagti hai.

**Danger Signs:**
- **Saans me dikkat:** Saans lene me takleef ho toh turant doctor ko dikhayein.
- **Khoon wali khansi:** Khansi me khoon aaye toh der mat karein.

**What To Do Now:**
- **Garam Paani:** Din bhar gunguna paani piyein.
- **Haldi Doodh:** Raat ko haldi wala garam doodh piyein.
- **Bhapa Lein:** Garam paani ka bhapa lene se naak khul jati hai.

**Health Tip:**
- **Tulsi-Adrak:** Tulsi aur adrak ki chai peene se gale ko aaram milta hai.

Aapki sardi-khansi abhi shuru hui lag rahi hai, 2 din garam cheezein lijiye.
Kya aap doctor se baat karna chahengi?"""
        else:
            return """Cold and cough is irritating, please take rest.

**Possible Causes:**
- **Viral Infection:** Change in weather causes virus in throat, it gives cold and cough.
- **Cold Water:** Cold water or ice-cream makes throat bad.
- **Dust Allergy:** Dust and smoke cause allergy and cough starts.

**Danger Signs:**
- **Breathing Problem:** If you feel difficulty in breathing, see doctor immediately.
- **Blood in Cough:** If blood comes in cough, do not wait.

**What To Do Now:**
- **Warm Water:** Drink warm water through the day.
- **Turmeric Milk:** Drink warm turmeric milk at night.
- **Steam:** Take steam from hot water, it opens your nose.

**Health Tip:**
- **Tulsi-Ginger:** Tulsi and ginger tea gives relief to throat.

Your cold and cough seems in starting stage, take warm things for 2 days.
Would you like to see a doctor?"""
    if "stomach" in text or "pet dard" in text or "pet me dard" in text or "gas" in text:
        if lang == "Hindi":
            return """Pet dard me bahut takleef hoti hai, aaram kijiye.

**Possible Causes:**
- **Gas:** Bahar ka khana ya jaldi-jaldi khane se pet me gas ban jati hai.
- **Acidity:** Masaledar khana ya khaali pet rehne se acidity ho jati hai.
- **Kabz:** Paani kam peene se kabz ho jata hai aur pet dukhne lagta hai.

**Danger Signs:**
- **Tez Dard:** Pet me bahut tez dard ho ya ulti aaye toh turant doctor ko dikhayein.
- **Khoon:** Potty me khoon aaye toh der mat karein.

**What To Do Now:**
- **Halka Khana:** Aaj halka khana khayein, jaise khichdi, dahi.
- **Gunguna Paani:** Gunguna paani dheere-dheere piyein.
- **Walk:** Khana khane ke baad 10 minute halki walk karein.

**Health Tip:**
- **Ajwain Paani:** Ajwain ka paani peene se gas me turant aaram milta hai.

Aapka pet dard gas aur acidity se lag raha hai, aaj halka khana khayein.
Kya aap doctor se baat karna chahengi?"""
        else:
            return """Stomach pain is painful, please take rest.

**Possible Causes:**
- **Gas:** Eating outside food or eating fast causes gas in stomach.
- **Acidity:** Spicy food or staying empty stomach causes acidity.
- **Constipation:** Drinking less water causes constipation and stomach pain.

**Danger Signs:**
- **Severe Pain:** If stomach pain is very severe or you feel vomiting, see doctor immediately.
- **Blood:** If blood comes in stool, do not wait.

**What To Do Now:**
- **Light Food:** Eat light food today, like khichdi, curd.
- **Warm Water:** Drink warm water slowly.
- **Walk:** Walk for 10 minutes lightly after food.

**Health Tip:**
- **Ajwain Water:** Ajwain water gives instant relief in gas.

Your stomach pain seems due to gas and acidity, eat light food today.
Would you like to see a doctor?"""
    if "daane" in text or "rash" in text or "khujli" in text or "itching" in text or "chot" in text:
        if lang == "Hindi":
            return """Photo dekh li hai, takleef samajh sakte hain.

**Possible Causes:**
- **Allergy:** Naye sabun, kapde ya dhool se skin pe allergy ho jati hai, isse daane aur khujli hoti hai.
- **Garmi:** Garmi me pasina jamne se bhi daane nikal aate hain.
- **Infection:** Saaf-safai na rakhne se skin pe infection ho jata hai.

**Danger Signs:**
- **Pus / Pani:** Daano se pus ya paani nikle toh turant doctor ko dikhayein.
- **Tez Bukhar:** Daano ke saath tez bukhar ho toh der mat karein.

**What To Do Now:**
- **Khujlayein Nahi:** Daano ko khujlayein nahi, isse infection badhta hai.
- **Saaf Rakhein:** Us jagah ko saaf paani se dho kar sukha rakhein.
- **Nariyal Tel:** Halka nariyal tel lagayein, isse khujli me aaram milega.

**Health Tip:**
- **Saaf Kapde:** Roz saaf aur dhoop me sukhe kapde pehnein.

Aapki photo doctor ko dikhane ke liye save ho gayi hai. Agar khujli badhti hai toh doctor se baat kar lijiyega.
Kya aap doctor se baat karna chahengi?"""
        else:
            return """I have seen your photo, I understand your problem.

**Possible Causes:**
- **Allergy:** New soap, clothes or dust can cause allergy on skin, it gives rashes and itching.
- **Heat:** In heat, sweat gets stuck and rashes come.
- **Infection:** If skin is not kept clean, infection happens.

**Danger Signs:**
- **Pus / Water:** If pus or water comes from rashes, see doctor immediately.
- **High Fever:** If you get high fever with rashes, do not wait.

**What To Do Now:**
- **Do Not Scratch:** Do not scratch rashes, it increases infection.
- **Keep Clean:** Wash that place with clean water and keep it dry.
- **Coconut Oil:** Apply light coconut oil, it gives relief in itching.

**Health Tip:**
- **Clean Clothes:** Wear clean clothes dried in sunlight daily.

Your photo is saved to show to doctor. If itching increases, talk to a doctor.
Would you like to see a doctor?"""
    return None

def ask_ollama_stream(user_text, lang, placeholder):
    instant = get_instant_answer(user_text, lang)
    if instant:
        placeholder.markdown(instant)
        return instant
    if lang == "Hindi":
        system_prompt = "Tum Sehat Saathi ho. Tum doctor NAHI ho. Hamesha simple Hindi me, chhota jawab do. Sirf 4 heading me jawab do: Possible Causes, Danger Signs, What To Do Now, Health Tip. Har heading me sirf 2-3 point. Har point 1 line me. Last me apni taraf se 1 line salah likh kar pucho: Kya aap doctor se baat karna chahengi?"
    else:
        system_prompt = "You are Sehat Saathi. You are NOT a doctor. Reply in simple English, short answer. Only 4 headings: Possible Causes, Danger Signs, What To Do Now, Health Tip. Only 2-3 points in each heading. Each point 1 line. At end write 1 line of your own advice and ask: Would you like to see a doctor?"
    try:
        history = [{"role": "system", "content": system_prompt}]
        for m in st.session_state.messages[-2:]:
            if m.get("type") != "image":
                history.append({"role": m["role"], "content": m["content"]})
        history.append({"role": "user", "content": user_text})
        response = requests.post("http://localhost:11434/api/chat", json={"model": "llama3.2:1b", "messages": history, "stream": True, "options": {"temperature": 0.3, "num_predict": 350}}, stream=True, timeout=60)
        full_text = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    part = data.get("message", {}).get("content", "")
                    full_text += part
                    placeholder.markdown(full_text + "▌")
                except:
                    pass
        placeholder.markdown(full_text)
        return full_text
    except Exception:
        return "Ollama is not running. Please run `ollama serve`"

# ================= HOME - CHANGE: CLEAR CHAT CHHOTA + BOX KE SIDE ME =================
if menu in ["🏠 Home", "🏠 होम"]:
    st.title("🩺 Sehat Saathi")
    if IS_HINDI:
        st.write("Hello, main yahan aapki madad karne ke liye hoon! 👋")
        st.write("Apni takleef likhein, bolein ya photo bhejein.")
    else:
        st.write("Hello, I am here to help you! 👋")
        st.write("Write your problem, speak or send photo.")

    # Chat history - upar bada Clear Chat button HATA DIYA, ab wo neeche box ke side me hai
    for idx, m in enumerate(st.session_state.messages):
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
    # --- NEW: Input Box + Chhota Clear Icon side-by-side ---
    col_box, col_clear = st.columns([5, 1])
    with col_box:
        chat_text = st.text_input("Type...", label_visibility="collapsed", placeholder="Apni takleef likhein..." if IS_HINDI else "Write your symptom...", key="wa_text")
    with col_clear:
        # Chhota sa sirf 🧹 icon, poora "Clear Chat" text nahi
        if st.button("🧹", use_container_width=True, key="clear_btn", help="Clear Chat" if not IS_HINDI else "Chat Saaf Karein"):
            st.session_state.messages = []
            st.session_state.doctor_asked = False
            st.session_state["last_audio_id"] = ""
            if "wa_text" in st.session_state:
                del st.session_state["wa_text"]
            if "wa_cam" in st.session_state:
                del st.session_state["wa_cam"]
            if "wa_mic" in st.session_state:
                del st.session_state["wa_mic"]
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
        with st.spinner("Sun rahe hain... Text ban raha hai..." if IS_HINDI else "Listening... Converting..."):
            voice_text = speech_to_text(audio_input.read())
        if voice_text == "TOO_SHORT":
            st.warning("Thoda lamba bolo - 2-3 second tak bolo, 1 sec wali awaz samajh nahi aati" if IS_HINDI else "Speak a little longer - speak for 2-3 seconds")
        elif voice_text and voice_text.startswith("ERROR:"):
            st.error(f"Problem: {voice_text} - Internet check karo, ya 3-4 second lamba bolo" if IS_HINDI else f"Problem: {voice_text} - Check internet, or speak for 3-4 seconds")
        elif voice_text:
            st.success(f"🗣️ Aapne bola: {voice_text}" if IS_HINDI else f"🗣️ You said: {voice_text}")
            st.session_state.messages.append({"role": "user", "content": voice_text})
            st.session_state.doctor_asked = False
            with st.chat_message("assistant"):
                placeholder = st.empty()
                reply = ask_ollama_stream(voice_text, lang, placeholder)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()
        else:
            st.warning("Awaz samajh nahi aayi, dobara boliye." if IS_HINDI else "Could not understand, please speak again.")

    if chat_text and uploaded_photo is None and audio_input is None:
        st.session_state.messages.append({"role": "user", "content": chat_text})
        st.session_state.doctor_asked = False
        with st.chat_message("assistant"):
            placeholder = st.empty()
            reply = ask_ollama_stream(chat_text, lang, placeholder)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

# ================= MEDICINE REMINDER - SIRF EK LANGUAGE =================
elif menu in ["💊 Medicine Reminder", "💊 दवाई रिमाइंडर"]:
    if IS_HINDI:
        st.title("💊 दवाई रिमाइंडर")
        st.write("Dawai ka time set kijiye, time hone pe app yaad dilayega.")
    else:
        st.title("💊 Medicine Reminder")
        st.write("Set medicine time, app will remind you.")
    with st.form("reminder_form"):
        med_name = st.text_input(
            "दवाई का नाम" if IS_HINDI else "Medicine Name",
            placeholder="दवाई का नाम लिखें..." if IS_HINDI else "Write medicine name...",
            value=""
        )
        st.write("समय" if IS_HINDI else "Time")
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
    st.caption("Note: App khula hone pe reminder dikhega." if IS_HINDI else "Note: Reminder shows when app is open.")

# ================= TALK TO DOCTOR - BINA FEES =================
elif menu in ["👨‍⚕️ Talk To Doctor", "👨‍⚕️ डॉक्टर से बात करें"]:
    if IS_HINDI:
        st.title("👨‍⚕️ डॉक्टर से बात करें")
        st.success("Ye sab sarkari doctor ki sewayein hain, 100% asli.")
        st.markdown("### 1. 🩺 eSanjeevani - Online Doctor")
        st.write("Sarkar ki official website hai. Ghar baithe asli doctor se video call pe baat karein.")
        st.write("- **Samay:** Subah 10 baje se shaam 4 baje tak")
        st.write("- **Kya chahiye:** Sirf mobile number")
        st.link_button("🩺 eSanjeevani Kholein - Doctor se Baat Karein", "https://esanjeevani.mohfw.gov.in", use_container_width=True)
        st.markdown("---")
        st.markdown("### 2. 📞 104 - Health Helpline")
        st.write("Phone pe hi doctor / nurse se baat karein, dawai ke baare me puchein.")
        st.write("- **Samay:** 24 ghante, 7 din")
        st.link_button("📞 104 pe Call Karein", "tel:104", use_container_width=True)
        st.markdown("---")
        st.markdown("### 3. 🏥 Najdiki Sarkari Hospital")
        st.write("Agar takleef zyada hai toh apne gaon ke najdik wale PHC / CHC me jayein.")
        st.write("- **Subah:** 9 baje se 1 baje tak OPD")
    else:
        st.title("👨‍⚕️ Talk To Doctor")
        st.success("All these are Government doctor services, 100% Real.")
        st.markdown("### 1. 🩺 eSanjeevani - Online Doctor")
        st.write("Official Government website. Talk to a real doctor on video call from home.")
        st.write("- **Time:** 10 AM to 4 PM")
        st.write("- **Need:** Only mobile number")
        st.link_button("🩺 Open eSanjeevani - Talk To Doctor", "https://esanjeevani.mohfw.gov.in", use_container_width=True)
        st.markdown("---")
        st.markdown("### 2. 📞 104 - Health Helpline")
        st.write("Talk to doctor / nurse on phone, ask about medicines.")
        st.write("- **Time:** 24 hours, 7 days")
        st.link_button("📞 Call 104", "tel:104", use_container_width=True)
        st.markdown("---")
        st.markdown("### 3. 🏥 Nearest Government Hospital")
        st.write("If problem is more, go to your nearest PHC / CHC.")
        st.write("- **Morning:** 9 AM to 1 PM OPD")

# ================= EMERGENCY =================
elif menu in ["🚨 Emergency", "🚨 आपातकाल"]:
    if IS_HINDI:
        st.title("🚨 आपातकाल - Emergency")
        st.error("Agar takleef bahut zyada hai toh pehle CALL karein, app ka wait mat karein!")
        st.markdown("### 📞 Emergency Numbers - Pehle Inpe Call Karein")
        st.link_button("🚑 108 - Ambulance Bulayein", "tel:108", use_container_width=True)
        st.link_button("🚓 112 - Police / Emergency", "tel:112", use_container_width=True)
        st.link_button("🔥 101 - Fire Brigade", "tel:101", use_container_width=True)
        st.link_button("📞 104 - Health Helpline", "tel:104", use_container_width=True)
        st.link_button("👧 1098 - Child Helpline", "tel:1098", use_container_width=True)
        st.link_button("👩 181 - Women Helpline", "tel:181", use_container_width=True)
        st.markdown("---")
        st.markdown("### 🆘 Emergency Tips - Ambulance Aane Tak Kya Karein?")
        st.markdown("#### 1. 🤒 Tez Bukhar (102 se upar)")
        st.write("- **Thandi Patti:** Sar pe thande paani ki patti rakhein")
        st.write("- **Kapde:** Bhari kapde / razai hata dein, halke kapde pehnayein")
        st.write("- **Paani:** Thoda-thoda karke paani pilate rahein")
        st.write("- **Dawai:** Bina doctor ke puchhe tez dawai mat dein")
        st.markdown("#### 2. 🩸 Chot Lag Gayi / Khoon Beh Raha Hai")
        st.write("- **Dabao:** Saaf kapde se chot wali jagah ko zor se dabake rakhein, 10 minute tak mat hatayein")
        st.write("- **Upar Rakhein:** Haath / pair pe chot hai toh usko upar utha ke rakhein")
        st.write("- **Paani:** Chot ko gande paani se mat dhoyein, saaf paani se hi dhoyein")
        st.write("- **Haldi / Mitti:** Chot pe haldi, mitti, toothpaste mat lagayein")
        st.markdown("#### 3. 😮‍💨 Saans Nahi Aa Rahi / Gala Ghoot Raha Hai")
        st.write("- **Seedha Bethao:** Patient ko seedha betha dein, letayein nahi")
        st.write("- **Kapde Dheele:** Gale ke kapde / dupatta dheela kar dein")
        st.write("- **Hawa:** Khidki-khula darwaza khol dein, bheed mat lagayein")
        st.write("- **Paani:** Zabardasti paani mat pilayein")
        st.markdown("#### 4. 🤮 Ulti / Food Poisoning")
        st.write("- **Side Me Letayein:** Patient ko ek side me letayein, taaki ulti saans me na jaye")
        st.write("- **ORS:** Thoda-thoda karke ORS / namak-cheeni ka paani pilayein")
        st.write("- **Khaana:** Ulti me kuch khane ko mat dein")
        st.write("- **Ulti Rokein Nahi:** Ulti ko zabardasti rokne ki dawai mat dein")
        st.markdown("#### 5. 🐍 Saanp / Kutta Kaat Le Toh")
        st.write("- **Dhoyein:** Kaati hui jagah ko saaf paani aur sabun se dhoyein")
        st.write("- **Hilaayein Nahi:** Us haath / pair ko hilayein nahi, seedha rakhein")
        st.write("- **Kaatna Nahi:** Chot ko blade se kaat ke khoon mat nikaliye")
        st.write("- **Turant Hospital:** Turant 108 pe call karke hospital le jayein, jhaad-phoonk me time mat waste karein")
        st.markdown("#### 6. 🤕 Behosh Ho Gaya Ho Toh")
        st.write("- **Check Karein:** Pehle dekhein saans chal rahi hai ya nahi")
        st.write("- **Side Me:** Agar saans chal rahi hai toh ek side me letayein")
        st.write("- **Paani Mat Pilayein:** Behosh aadmi ko paani / khana mat pilayein")
        st.write("- **Turant Call:** Turant 108 pe call karein")
    else:
        st.title("🚨 Emergency")
        st.error("If problem is very serious, CALL FIRST, do not wait for app!")
        st.markdown("### 📞 Emergency Numbers - Call These First")
        st.link_button("🚑 108 - Call Ambulance", "tel:108", use_container_width=True)
        st.link_button("🚓 112 - Police / Emergency", "tel:112", use_container_width=True)
        st.link_button("🔥 101 - Fire Brigade", "tel:101", use_container_width=True)
        st.link_button("📞 104 - Health Helpline", "tel:104", use_container_width=True)
        st.link_button("👧 1098 - Child Helpline", "tel:1098", use_container_width=True)
        st.link_button("👩 181 - Women Helpline", "tel:181", use_container_width=True)
        st.markdown("---")
        st.markdown("### 🆘 Emergency Tips - What To Do Till Ambulance Comes?")
        st.markdown("#### 1. 🤒 High Fever (Above 102)")
        st.write("- **Cold Sponge:** Keep cold wet cloth on forehead")
        st.write("- **Clothes:** Remove heavy blanket, wear light clothes")
        st.write("- **Water:** Keep giving water in small sips")
        st.write("- **Medicine:** Do not give strong medicine without asking doctor")
        st.markdown("#### 2. 🩸 Injury / Bleeding")
        st.write("- **Press:** Press injury with clean cloth tightly, do not remove for 10 minutes")
        st.write("- **Raise:** If injury is on hand / leg, keep it raised up")
        st.write("- **Water:** Do not wash with dirty water, use clean water only")
        st.write("- **No Haldi / Mud:** Do not apply haldi, mud, toothpaste on wound")
        st.markdown("#### 3. 😮‍💨 Breathing Problem / Choking")
        st.write("- **Sit Straight:** Make patient sit straight, do not make them lie down")
        st.write("- **Loosen Clothes:** Loosen clothes around neck")
        st.write("- **Air:** Open windows, do not crowd")
        st.write("- **Water:** Do not force water")
        st.markdown("#### 4. 🤮 Vomiting / Food Poisoning")
        st.write("- **Side Position:** Make patient lie on one side, so vomit does not go in lungs")
        st.write("- **ORS:** Give ORS / salt-sugar water in small sips")
        st.write("- **Food:** Do not give food during vomiting")
        st.write("- **Do Not Stop:** Do not give medicine to stop vomiting forcefully")
        st.markdown("#### 5. 🐍 Snake / Dog Bite")
        st.write("- **Wash:** Wash bite area with clean water and soap")
        st.write("- **Do Not Move:** Do not move that hand / leg, keep it straight")
        st.write("- **Do Not Cut:** Do not cut wound with blade to take blood out")
        st.write("- **Hospital Fast:** Call 108 and go to hospital fast, do not waste time in jhaad-phoonk")
        st.markdown("#### 6. 🤕 Unconscious Person")
        st.write("- **Check:** First check if breathing is going on or not")
        st.write("- **Side:** If breathing is there, make them lie on one side")
        st.write("- **No Water:** Do not give water / food to unconscious person")
        st.write("- **Call Fast:** Call 108 immediately")

# ================= HEALTH TIPS =================
elif menu in ["💡 Health Tips", "💡 स्वास्थ्य टिप्स"]:
    if IS_HINDI:
        st.title("💡 स्वास्थ्य टिप्स - Roz Ka Routine")
        st.write("Ye chhoti-chhoti aadatien aapko bade rog se bacha sakti hain.")
        st.markdown("### 🌅 1. Subah Uthte Hi")
        st.write("- **Gunguna Paani:** Subah uthte hi 1-2 gilas gunguna paani piyein, isse pet saaf hota hai")
        st.write("- **Dhoop:** Subah 15 minute dhoop me bethein, isse Vitamin D milta hai, haddiyan mazboot hoti hain")
        st.write("- **Phone Mat Dekhein:** Uthte hi phone mat dekhein, 30 minute baad dekhein, dimag shant rahega")
        st.markdown("### 🚶 2. Walk Aur Exercise")
        st.write("- **Roz 30 Minute Walk:** Subah ya shaam 30 minute tez walk karein, isse BP, sugar aur wajan control me rehta hai")
        st.write("- **Seedhi:** Lift ki jagah seedhi use karein, yehi sabse acchi exercise hai")
        st.write("- **Kaam Me Walk:** Ek jagah 1 ghanta mat bethein, har 1 ghante me 5 minute khade ho kar chalein")
        st.markdown("### 🍲 3. Khana-Peena")
        st.write("- **Hari Sabziyan:** Roz ek time hari sabzi khayein, jaise palak, bhindi, lauki")
        st.write("- **Paani:** Din me 8 gilas paani piyein, garmi me aur zyada")
        st.write("- **Namak-Kam:** Khane me namak aur tel kam rakhein, isse BP nahi badhega")
        st.write("- **Bahar Ka Khana:** Hafte me 1 baar se zyada bahar ka tala-bhuna khana mat khayein")
        st.write("- **Raat Ka Khana:** Raat ka khana sone se 2 ghante pehle kha lein, halka khayein")
        st.markdown("### 😴 4. Neend")
        st.write("- **7-8 Ghante:** Roz 7-8 ghante ki neend lein, kam neend se sar dard, BP aur gussa badhta hai")
        st.write("- **Time Fix:** Roz ek hi time pe soyein aur uthein, sharir ko aadat ho jayegi")
        st.write("- **Mobile Door:** Sone se 30 minute pehle mobile band kar dein")
        st.markdown("### 🧼 5. Saaf-Safai")
        st.write("- **Haath Dhoyein:** Khana khane se pehle aur bathroom ke baad haath sabun se dhoyein")
        st.write("- **Daant:** Din me 2 baar brush karein, subah aur raat ko")
        st.write("- **Nakhun:** Hafte me 1 baar nakhun kaatein, gande nakhun se pet ke keede hote hain")
        st.markdown("### 🧠 6. Mann Ko Shant Rakhein")
        st.write("- **Gussa Kam:** Gussa aaye toh 10 tak ginti karein, lambi saans lein")
        st.write("- **Baat Karein:** Mann me baat mat rakhein, ghar walo se baat karein")
        st.write("- **Hasna:** Roz thoda hasein, TV pe comedy dekhein, mann halka rahega")
        st.markdown("### 👶 7. Bachon Ke Liye")
        st.write("- **Teeka:** Bachon ke saare teeke time pe lagwayein, PHC me FREE lagte hain")
        st.write("- **Doodh:** Roz 1 gilas doodh pilayein")
        st.write("- **Mobile Kam:** Bachon ko mobile 1 ghante se zyada mat dein")
        st.markdown("### 👵 8. Bujurgon Ke Liye")
        st.write("- **BP-Sugar Check:** Mahine me 1 baar BP aur sugar check karwayein, PHC me FREE hota hai")
        st.write("- **Girne Se Bachayein:** Bathroom me chappal pehnein, andhere me akele mat chalein")
        st.write("- **Dawai Time Pe:** Dawai ka time kabhi miss mat karein, is app se reminder lagayein")
    else:
        st.title("💡 Health Tips - Daily Routine")
        st.write("These small habits can save you from big diseases.")
        st.markdown("### 🌅 1. Morning")
        st.write("- **Warm Water:** Drink 1-2 glasses of warm water after waking up, it cleans stomach")
        st.write("- **Sunlight:** Sit in sunlight for 15 minutes in morning, you get Vitamin D, bones become strong")
        st.write("- **No Phone:** Do not see phone just after waking up, see after 30 minutes, mind stays calm")
        st.markdown("### 🚶 2. Walk And Exercise")
        st.write("- **30 Min Walk Daily:** Walk fast for 30 minutes morning or evening, it controls BP, sugar and weight")
        st.write("- **Stairs:** Use stairs instead of lift, this is best exercise")
        st.write("- **Move Every Hour:** Do not sit at one place for 1 hour, walk 5 minutes every hour")
        st.markdown("### 🍲 3. Food And Water")
        st.write("- **Green Vegetables:** Eat green vegetables once daily, like palak, bhindi, lauki")
        st.write("- **Water:** Drink 8 glasses of water daily, more in summer")
        st.write("- **Less Salt-Oil:** Keep salt and oil less in food, BP will not increase")
        st.write("- **Outside Food:** Do not eat outside fried food more than once a week")
        st.write("- **Dinner:** Eat dinner 2 hours before sleeping, eat light")
        st.markdown("### 😴 4. Sleep")
        st.write("- **7-8 Hours:** Take 7-8 hours sleep daily, less sleep causes headache, BP and anger")
        st.write("- **Fixed Time:** Sleep and wake at same time daily, body gets habit")
        st.write("- **Mobile Away:** Switch off mobile 30 minutes before sleeping")
        st.markdown("### 🧼 5. Cleanliness")
        st.write("- **Wash Hands:** Wash hands with soap before eating and after bathroom")
        st.write("- **Teeth:** Brush 2 times a day, morning and night")
        st.write("- **Nails:** Cut nails once a week, dirty nails cause stomach worms")
        st.markdown("### 🧠 6. Keep Mind Calm")
        st.write("- **Less Anger:** When angry, count till 10, take long breath")
        st.write("- **Talk:** Do not keep things in heart, talk to family")
        st.write("- **Laugh:** Laugh daily, watch comedy, mind stays light")
        st.markdown("### 👶 7. For Children")
        st.write("- **Vaccination:** Get all vaccines of children on time, they are FREE in PHC")
        st.write("- **Milk:** Give 1 glass milk daily")
        st.write("- **Less Mobile:** Do not give mobile to children more than 1 hour")
        st.markdown("### 👵 8. For Elderly")
        st.write("- **BP-Sugar Check:** Check BP and sugar once a month, it is FREE in PHC")
        st.write("- **Avoid Fall:** Wear chappal in bathroom, do not walk alone in dark")
        st.write("- **Medicine On Time:** Never miss medicine time, set reminder from this app")

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
        st.write("- **Kya Milta Hai:** 5 Lakh tak ka FREE ilaj, har saal, poore parivar ke liye")
        st.write("- **Kaun Le Sakta Hai:** Gareeb parivar, jinke paas ration card hai ya gaon ki list me naam hai")
        st.write("- **Kahan Milega:** Sarkari hospital aur Ayushman wale private hospital me")
        st.write("- **Kaise Banega:** Apna Aadhaar card le kar najdik ke CSC centre ya hospital me jayein, wahan FREE card ban jayega")
        st.write("- **Kya Chahiye:** Aadhaar Card + Ration Card")
        st.link_button("Ayushman Card Check Karein", "https://pmjay.gov.in", use_container_width=True)
        st.markdown("---")
        st.markdown("### 2. 💊 Jan Aushadhi - Sasti Dawai")
        st.write("- **Kya Milta Hai:** Dawai 50% se 90% tak sasti milti hai, jaise 100 Rs. wali dawai 15 Rs. me")
        st.write("- **Kaun Le Sakta Hai:** Koi bhi, sabke liye hai")
        st.write("- **Kahan Milega:** Gaon / shehar me Jan Aushadhi Kendra pe")
        st.write("- **Kaise Lein:** Doctor ki parchi le kar Jan Aushadhi Kendra pe jayein, wahan sasti dawai milegi")
        st.write("- **Kya Chahiye:** Doctor ki parchi")
        st.link_button("Nazdiki Jan Aushadhi Kendra Dhoondhein", "https://janaushadhi.gov.in", use_container_width=True)
        st.markdown("---")
        st.markdown("### 3. 🤰 PM Surakshit Matritva - Garbhvati Mahila")
        st.write("- **Kya Milta Hai:** Garbhvati mahila ki FREE janch, FREE dawai, FREE ultrasound")
        st.write("- **Kaun Le Sakta Hai:** Har garbhvati mahila")
        st.write("- **Kab:** Har mahine ki 9 tarikh ko PHC / Hospital me FREE janch hoti hai")
        st.write("- **Kaise Lein:** 9 tarikh ko apne najdik ke PHC me Aadhaar card le kar jayein")
        st.write("- **Kya Chahiye:** Aadhaar Card")
        st.markdown("---")
        st.markdown("### 4. 👶 Mission Indradhanush - Bachon Ke Teeke")
        st.write("- **Kya Milta Hai:** Bachon ke saare teeke bilkul FREE - Polio, BCG, Measles sab")
        st.write("- **Kaun Le Sakta Hai:** 0 se 5 saal tak ke saare bache aur garbhvati mahilayein")
        st.write("- **Kahan Milega:** Gaon ke Anganwadi / PHC me")
        st.write("- **Kaise Lein:** Anganwadi didi se puchhein, wo teeke ka din bata dengi")
        st.write("- **Kya Chahiye:** Bachon ka Teeka Card")
        st.markdown("---")
        st.markdown("### 5. 👵 PM Vaya Vandana - Bujurgon Ke Liye")
        st.write("- **Kya Milta Hai:** 60 saal se upar ke bujurgon ko har mahine pension jaisa paisa milta hai")
        st.write("- **Kaun Le Sakta Hai:** 60 saal se upar ke sabhi bujurg")
        st.write("- **Kaise Lein:** Bank ya LIC office me jayein")
        st.write("- **Kya Chahiye:** Aadhaar Card + Bank Passbook")
        st.markdown("---")
        st.markdown("### 6. 🦟 National Health Mission - FREE Jaanch")
        st.write("- **Kya Milta Hai:** PHC me BP, Sugar, Bukhar, Malaria ki janch bilkul FREE")
        st.write("- **Kaun Le Sakta Hai:** Sabhi log")
        st.write("- **Kahan Milega:** Apne gaon ke najdik wale PHC / Sub-Centre me")
        st.write("- **Kaise Lein:** Subah 9 baje PHC me jayein, parchi banwayein")
        st.write("- **Kya Chahiye:** Aadhaar Card")
    else:
        st.title("🏛️ Government Schemes - Take FREE Benefit")
        st.success("All these are Government schemes, 100% Real and FREE. Do not pay money to anyone.")
        st.markdown("### 1. 🩺 Ayushman Bharat - PMJAY")
        st.write("- **Benefit:** FREE treatment up to 5 Lakh, every year, for whole family")
        st.write("- **Who Can Get:** Poor families, who have ration card or name in village list")
        st.write("- **Where:** Government hospital and Ayushman private hospitals")
        st.write("- **How To Make:** Take Aadhaar card to nearest CSC centre or hospital, card will be made FREE")
        st.write("- **Need:** Aadhaar Card + Ration Card")
        st.link_button("Check Ayushman Card", "https://pmjay.gov.in", use_container_width=True)
        st.markdown("---")
        st.markdown("### 2. 💊 Jan Aushadhi - Cheap Medicines")
        st.write("- **Benefit:** Medicines 50% to 90% cheaper, like Rs.100 medicine in Rs.15")
        st.write("- **Who Can Get:** Anyone, for everyone")
        st.write("- **Where:** Jan Aushadhi Kendra in village / city")
        st.write("- **How To Get:** Take doctor slip to Jan Aushadhi Kendra, you will get cheap medicine")
        st.write("- **Need:** Doctor slip")
        st.link_button("Find Nearest Jan Aushadhi Kendra", "https://janaushadhi.gov.in", use_container_width=True)
        st.markdown("---")
        st.markdown("### 3. 🤰 PM Surakshit Matritva - Pregnant Women")
        st.write("- **Benefit:** FREE checkup, FREE medicine, FREE ultrasound for pregnant women")
        st.write("- **Who Can Get:** Every pregnant woman")
        st.write("- **When:** On 9th of every month, FREE checkup in PHC / Hospital")
        st.write("- **How To Get:** On 9th, go to nearest PHC with Aadhaar card")
        st.write("- **Need:** Aadhaar Card")
        st.markdown("---")
        st.markdown("### 4. 👶 Mission Indradhanush - Children Vaccines")
        st.write("- **Benefit:** All vaccines of children totally FREE - Polio, BCG, Measles all")
        st.write("- **Who Can Get:** All children 0 to 5 years and pregnant women")
        st.write("- **Where:** Village Anganwadi / PHC")
        st.write("- **How To Get:** Ask Anganwadi didi, she will tell vaccine day")
        st.write("- **Need:** Children Vaccine Card")
        st.markdown("---")
        st.markdown("### 5. 👵 PM Vaya Vandana - For Elderly")
        st.write("- **Benefit:** Elderly above 60 years get monthly pension-like money")
        st.write("- **Who Can Get:** All elderly above 60 years")
        st.write("- **How To Get:** Go to Bank or LIC office")
        st.write("- **Need:** Aadhaar Card + Bank Passbook")
        st.markdown("---")
        st.markdown("### 6. 🦟 National Health Mission - FREE Checkup")
        st.write("- **Benefit:** BP, Sugar, Fever, Malaria checkup totally FREE in PHC")
        st.write("- **Who Can Get:** Everyone")
        st.write("- **Where:** Nearest PHC / Sub-Centre of your village")
        st.write("- **How To Get:** Go to PHC at 9 AM, make slip")
        st.write("- **Need:** Aadhaar Card")

# ================= ABOUT =================
elif menu in ["ℹ️ About App", "ℹ️ ऐप के बारे में"]:
    if IS_HINDI:
        st.title("ℹ️ ऐप के बारे में")
        st.write("सेहत साथी गांव के लोगों के लिए बनाया गया है। ये डॉक्टर की जगह नहीं लेता, बस शुरुआती मदद करता है।")
        st.write("**Features:** Chat, Photo Upload, Voice Input, Medicine Reminder, Doctor, BMI, Schemes")
    else:
        st.title("ℹ️ About App")
        st.write("Sehat Saathi is made for village people. It does not replace a doctor, it only gives first help.")
        st.write("**Features:** Chat, Photo Upload, Voice Input, Medicine Reminder, Doctor, BMI, Schemes")