import streamlit as st
import datetime
import re
import urllib.parse
st.set_page_config(page_title="Sehat Saathi", page_icon="🩺", layout="centered")
if "messages" not in st.session_state:
    st.session_state.messages = []
if "doctor_asked" not in st.session_state:
    st.session_state.doctor_asked = False
if "reminders" not in st.session_state:
    st.session_state.reminders = []
if "last_audio_id" not in st.session_state:
    st.session_state["last_audio_id"] = ""
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "photo_sent" not in st.session_state:
    st.session_state.photo_sent = False

st.sidebar.write("भाषा - Language" if False else "Language - Menu Ki Bhasha")
lang = st.sidebar.radio("Choose Language", ["English", "Hindi"], label_visibility="collapsed")
IS_HINDI = (lang == "Hindi")
if IS_HINDI:
    menu = st.sidebar.radio("मेनू", ["🏠 होम", "💊 दवाई रिमाइंडर", "👨‍⚕️ डॉक्टर से बात करें", "🚨 आपातकाल", "💡 स्वास्थ्य टिप्स", "⚖️ बीएमआई कैलकुलेटर", "🏛️ सरकारी योजनाएं", "ℹ️ ऐप के बारे में"])
else:
    menu = st.sidebar.radio("Menu", ["🏠 Home", "💊 Medicine Reminder", "👨‍⚕️ Talk To Doctor", "🚨 Emergency", "💡 Health Tips", "⚖️ BMI Calculator", "🏛️ Government Schemes", "ℹ️ About App"])

def speech_to_text(audio_bytes):
    try:
        import speech_recognition as sr
        import io
        r = sr.Recognizer()
        wav_io = io.BytesIO(audio_bytes)
        with sr.AudioFile(wav_io) as source:
            audio_data = r.record(source)
            try:
                return r.recognize_google(audio_data, language="hi-IN")
            except:
                return r.recognize_google(audio_data, language="en-IN")
    except Exception as e:
        return f"ERROR:{str(e)[:100]}"

HEALTH_WORDS = ["daane","rash","chot","zakhm","allergy","khujli","itching","bukhar","fever","dard","pain","dawa","medicine","wound","injury","skin","khaansi","cough","cold","sardi","pet","stomach","sir","head","haath","hand","pair","leg","blood","khoon","burn","jal","soojan","swelling","ulti","vomit","dast","kamzori","weak","neend","sleep","saans","breath","chest","seene","gala","throat","kaan","ear","daant","tooth","aankh","eye","ghutna","knee","kamar","back","badan","body","chakkar","dizzy","gas","acidity","kabz","photo","doctor","hospital","bimar","beemar","tabiyat","dawai","दाने","चोट","खुजली","बुखार","दर्द","सांस","सीने","पेट","सिर","कमर","गला","कान","दांत","आंख","पैर","हाथ","घुटना","चक्कर","उल्टी","कमजोरी","नींद"]
OUT_WORDS = ["movie","film","cricket","football","game","padhai","study","exam","joke","song","gaana","politics","news","weather","mausam","love","shaadi","job","naukri","paisa","money","shopping","birthday"]
def is_health_related(text):
    t = text.lower()
    if any(w in t for w in HEALTH_WORDS):
        return True
    if any(w in t for w in OUT_WORDS):
        return False
    if t.strip() in ["hi","hello","namaste","hey","hii","नमस्ते"]:
        return True
    return False
def out_of_context_msg(real_lang):
    if real_lang=="Hindi":
        return "मैं सिर्फ स्वास्थ्य, चोट और एलर्जी से जुड़ी मदद कर सकती हूँ। अपनी स्वास्थ्य समस्या बताइए - जैसे सिर दर्द, बुखार, दाने, चोट, खुजली।"
    else:
        return "I can only help with health, injury and allergy related problems. Please tell your health problem - like headache, fever, rash, injury, itching."
def detect_language(user_text):
    t = user_text.lower()
    if re.search(r'[\u0900-\u097F]', user_text):
        return "Hindi"
    hindi_words = ["mere", "mera", "mujhe", "dard", "hai", "sar", "sir", "kamar", "pet", "badan", "bukhar", "sardi", "khansi", "khujli", "daane", "gala", "kaan", "daant", "aankh", "pair", "haath", "ghutna", "chakkar", "ulti", "dast", "kamzori", "neend", "chot", "seene", "saans"]
    for w in hindi_words:
        if w in t:
            return "Hindi"
    return "Hindi" if IS_HINDI else "English"

# ---------- DOCTORS - DIRECT NUMBER ----------
DOCTORS_MAP = [
    (["daane","rash","khujli","itching","allergy","दाने","खुजली"], [("डॉ. शर्मा - त्वचा रोग विशेषज्ञ" if IS_HINDI else "Dr. Sharma - Skin Doctor", "9876543210"), ("डॉ. वर्मा - त्वचा रोग विशेषज्ञ" if IS_HINDI else "Dr. Verma - Dermatologist", "9876543211")]),
    (["chot","zakhm","wound","injury","kat","cut","चोट"], [("डॉ. गुप्ता - सर्जन" if IS_HINDI else "Dr. Gupta - General Surgeon", "9876543212"), ("डॉ. सिंह - हड्डी रोग विशेषज्ञ" if IS_HINDI else "Dr. Singh - Ortho Doctor", "9876543213")]),
    (["chest","seene","saans","breath","सीने","सांस"], [("डॉ. पटेल - हृदय / सामान्य चिकित्सक" if IS_HINDI else "Dr. Patel - Heart / General Physician", "9876543216"), ("डॉ. खान - चिकित्सक" if IS_HINDI else "Dr. Khan - Physician", "9876543217")]),
    (["bukhar","fever","बुखार"], [("डॉ. पटेल - सामान्य चिकित्सक" if IS_HINDI else "Dr. Patel - General Physician", "9876543216"), ("डॉ. खान - चिकित्सक" if IS_HINDI else "Dr. Khan - Physician", "9876543217")]),
    (["pet","stomach","gas","पेट"], [("डॉ. पटेल - सामान्य चिकित्सक" if IS_HINDI else "Dr. Patel - General Physician", "9876543216"), ("डॉ. मेहता - पेट रोग विशेषज्ञ" if IS_HINDI else "Dr. Mehta - Gastroenterologist", "9876543218")]),
    (["sar","head","sir","सिर"], [("डॉ. खान - सामान्य चिकित्सक" if IS_HINDI else "Dr. Khan - General Physician", "9876543217"), ("डॉ. अय्यर - न्यूरोलॉजिस्ट" if IS_HINDI else "Dr. Iyer - Neurologist", "9876543219")]),
    (["daant","tooth","दांत"], [("डॉ. राव - दांत के डॉक्टर" if IS_HINDI else "Dr. Rao - Dentist", "9876543220")]),
    (["aankh","eye","आंख"], [("डॉ. नायर - आंख के डॉक्टर" if IS_HINDI else "Dr. Nair - Eye Doctor", "9876543221")]),
    (["kaan","ear","कान"], [("डॉ. बोस - कान-नाक-गला विशेषज्ञ" if IS_HINDI else "Dr. Bose - ENT Doctor", "9876543222")]),
]
DEFAULT_DOCTORS = [("डॉ. पटेल - सामान्य चिकित्सक" if IS_HINDI else "Dr. Patel - General Physician", "9876543216"), ("डॉ. खान - चिकित्सक" if IS_HINDI else "Dr. Khan - Physician", "9876543217")]
def get_doctors_for(text):
    t = text.lower()
    for keys, docs in DOCTORS_MAP:
        if any(k in t for k in keys):
            return docs
    return DEFAULT_DOCTORS
def show_doctors_box(user_text):
    docs = get_doctors_for(user_text)
    if IS_HINDI:
        st.markdown("### 👨‍⚕️ आपके लक्षण के डॉक्टर - सीधे कॉल करें")
        st.markdown("**🩺 ई-संजीवनी - ऑनलाइन डॉक्टर (सरकारी, फ्री) - सबसे ऊपर**")
    else:
        st.markdown("### 👨‍⚕️ Doctors For Your Symptom - Call Directly")
        st.markdown("**🩺 eSanjeevani - Online Doctor (Govt, FREE) - On Top**")
    st.link_button("🩺 ई-संजीवनी खोलें" if IS_HINDI else "🩺 Open eSanjeevani", "https://esanjeevani.mohfw.gov.in", use_container_width=True)
    for name, ph in docs:
        c1, c2 = st.columns([3, 1])
        with c1:
            st.write(f"**{name}**  -  📞 {ph}")
        with c2:
            st.link_button("📞 कॉल करें" if IS_HINDI else "📞 Call", f"tel:{ph}", use_container_width=True)
    st.link_button("📞 104 - हेल्थ हेल्पलाइन पर कॉल करें" if IS_HINDI else "📞 104 - Health Helpline Call", "tel:104", use_container_width=True)

# ---------- FLOATING BANNER - CSS, KHUD BADLEGA ----------
def show_floating_banner():
    tips_hi = ["💡 दिन में 8 गिलास पानी पिएं", "💡 चोट को साफ पानी से धोएं, गंदा कपड़ा मत लगाएं", "💡 एलर्जी में खुजली मत करें, ठंडा पानी लगाएं", "💡 दवा समय पर लें, खुराक मत छोड़ें", "💡 रोज 30 मिनट टहलें", "💡 बुखार 102 से ऊपर हो तो तुरंत डॉक्टर को दिखाएं"]
    tips_en = ["💡 Drink 8 glasses of water daily", "💡 Wash wound with clean water, do not apply dirty cloth", "💡 In allergy do not scratch, apply cold water", "💡 Take medicine on time, do not miss dose", "💡 Walk 30 minutes daily", "💡 If fever is above 102, see doctor immediately"]
    tips = tips_hi if IS_HINDI else tips_en
    items = ""
    for i, tip in enumerate(tips):
        delay = i * 4
        items += f'<div class="tip" style="animation-delay:{delay}s;">{tip}</div>'
    st.markdown(f"""
    <style>
    .banner-wrap {{ position: fixed; bottom: 0; left: 0; right: 0; z-index: 9999; background: #FF4B4B; height: 48px; overflow: hidden; }}
    .banner-wrap .tip {{ position: absolute; left: 0; right: 0; top: 0; height: 48px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 15px; padding: 0 10px; text-align: center; opacity: 0; animation: tipCycle 24s linear infinite; }}
    @keyframes tipCycle {{ 0% {{opacity: 0;}} 1% {{opacity: 1;}} 15% {{opacity: 1;}} 17% {{opacity: 0;}} 100% {{opacity: 0;}} }}
    .block-container {{ padding-bottom: 70px !important; }}
    </style>
    <div class="banner-wrap">{items}</div>
    """, unsafe_allow_html=True)

# ---------- ANSWER - HINDI = DEVNAGARI, ENGLISH = ENGLISH ----------
def get_instant_answer(user_text, lang):
    text = user_text.lower()
    def make_answer(symptom_name, causes, dangers, dos, tip, summary, lang):
        if lang == "Hindi":
            c = "\n".join([f"- **{a}:** {b}" for a,b in causes])
            d = "\n".join([f"- **{a}:** {b}" for a,b in dangers])
            w = "\n".join([f"- **{a}:** {b}" for a,b in dos])
            return f"""आपकी तकलीफ समझ सकते हैं, आराम कीजिए।

**संभावित कारण - {symptom_name} की वजह:**

{c}

**खतरे के लक्षण:**

{d}

**अभी क्या करें:**

{w}

**स्वास्थ्य टिप:**

- **{tip[0]}:** {tip[1]}

{summary}

क्या आप डॉक्टर से बात करना चाहेंगी?"""
        else:
            c = "\n".join([f"- **{a}:** {b}" for a,b in causes])
            d = "\n".join([f"- **{a}:** {b}" for a,b in dangers])
            w = "\n".join([f"- **{a}:** {b}" for a,b in dos])
            return f"""I understand, please take rest.

**Possible Causes - Why {symptom_name} happens:**

{c}

**Danger Signs:**

{d}

**What To Do Now:**

{w}

**Health Tip:**

- **{tip[0]}:** {tip[1]}

{summary}

Would you like to see a doctor?"""
    if "head" in text or "sar" in text or "sir" in text or "migraine" in text or "headache" in text or "सिर" in text:
        if lang == "Hindi":
            return make_answer("सिर दर्द", [("नींद की कमी","रात को नींद पूरी न होने से सुबह उठते ही सिर भारी लगता है।"),("ज्यादा फोन","दिन भर फोन देखने से आंखों पर जोर पड़ता है।"),("गैस / भूख","लंबी देर भूखे रहने से या गैस बनने से भी सिर में दर्द होता है।")], [("बहुत तेज दर्द","अगर अचानक बहुत तेज दर्द हो, तो तुरंत डॉक्टर को दिखाएं।"),("उल्टी / चक्कर","सिर दर्द के साथ उल्टी या चक्कर आए, तो देर मत करें।")], [("अंधेरे में आराम","लाइट बंद करके अंधेरे कमरे में लेट जाएं, फोन मत देखें।"),("ठंडी पट्टी","सिर पर ठंडे पानी की पट्टी रखें।"),("गुनगुना पानी","थोड़ा-थोड़ा करके गुनगुना पानी पिएं।")], ("फोन कम देखें","रोज सोने से 30 मिनट पहले फोन बंद कर दें।"), "आपका सिर दर्द ज्यादातर नींद की कमी और फोन देखने की वजह से लग रहा है।", lang)
        else:
            return make_answer("Headache", [("Less Sleep","When you do not sleep well, you wake up with heavy head."),("Too Much Phone","Watching phone all day puts pressure on eyes."),("Gas and Hunger","Staying hungry or gas also causes headache.")], [("Very Severe Pain","If sudden very severe headache, see doctor immediately."),("Vomiting / Dizziness","If vomiting or dizziness with headache, do not wait.")], [("Rest in Dark Room","Lie down in dark room, do not see phone."),("Cold Cloth","Keep cold wet cloth on head."),("Warm Water","Drink warm water in small sips.")], ("Less Phone","Switch off phone 30 minutes before sleeping."), "Your headache seems mostly because of less sleep and too much phone.", lang)
    if "back" in text or "kamar" in text or "spine" in text or "कमर" in text:
        if lang == "Hindi":
            return make_answer("कमर दर्द", [("गलत बैठना","लंबी देर झुककर बैठने से कमर पर जोर पड़ता है।"),("भारी चीज उठाना","भारी बाल्टी उठाने से नस खिंच जाती है।"),("कमजोरी","कैल्शियम और विटामिन डी की कमी से हड्डियां कमजोर होती हैं।")], [("पैर में दर्द","अगर दर्द कमर से पैर तक जा रहा है, तो तुरंत डॉक्टर को दिखाएं।"),("चलने में दिक्कत","अगर चलने में बहुत तकलीफ हो, तो देर मत करें।")], [("सीधा लेटें","सीधे सख्त बिस्तर पर लेट जाएं।"),("गरम सेंक","कमर पर दिन में 2 बार 10 मिनट गरम सेंक करें।"),("भारी काम बंद","2 दिन तक भारी चीज मत उठाएं।")], ("रोज टहलें","रोज 20 मिनट सीधा चलिए।"), "आपका कमर दर्द ज्यादातर गलत बैठने और भारी काम की वजह से लग रहा है।", lang)
        else:
            return make_answer("Back Pain", [("Wrong Sitting","Sitting bent puts pressure on back."),("Lifting Heavy Things","Lifting heavy bag pulls nerve."),("Weakness","Lack of Calcium and Vitamin D makes bones weak.")], [("Pain in Leg","If pain goes from back to leg, see doctor immediately."),("Difficulty Walking","If difficulty in walking, do not wait.")], [("Lie Straight","Lie straight on hard bed."),("Hot Compress","Apply warm cloth 10 minutes, 2 times a day."),("Stop Heavy Work","Do not lift heavy things for 2 days.")], ("Daily Walk","Walk straight 20 minutes daily."), "Your back pain seems mostly because of wrong sitting and heavy work.", lang)
    if "body" in text or "badan" in text or "sharir" in text or "whole" in text or "बदन" in text:
        if lang == "Hindi":
            return make_answer("पूरा बदन दर्द", [("थकान","दिन भर ज्यादा काम करने से पूरा शरीर थक जाता है।"),("वायरल","मौसम बदलने से हल्का वायरस लग जाता है।"),("पानी की कमी","पानी कम पीने से मांसपेशियों में दर्द होता है।")], [("तेज बुखार","बुखार 102 से ऊपर हो, तो तुरंत डॉक्टर को दिखाएं।"),("सांस में दिक्कत","सांस लेने में तकलीफ हो, तो देर मत करें।")], [("पूरा आराम","आज भारी काम बंद करके पूरा आराम कीजिए।"),("गरम पानी से नहाएं","गुनगुने पानी से नहाने से आराम मिलेगा।"),("गुनगुना पानी पिएं","दिन भर थोड़ा-थोड़ा गुनगुना पानी पिएं।")], ("रोज टहलें","रोज 30 मिनट हल्की टहल से मांसपेशियां मजबूत होती हैं।"), "आपका बदन दर्द ज्यादातर थकान और वायरल की वजह से लग रहा है।", lang)
        else:
            return make_answer("Body Pain", [("Tiredness","Working too much makes body tired."),("Viral Infection","Change in weather causes mild virus."),("Less Water","Drinking less water causes muscle pain.")], [("High Fever","If fever above 102, see doctor immediately."),("Breathing Problem","If difficulty in breathing, do not wait.")], [("Full Rest","Stop heavy work and take full rest."),("Warm Water Bath","Bathing with warm water will relax muscles."),("Warm Water","Keep drinking warm water in small sips.")], ("Daily Walk","Walking 30 minutes daily makes muscles strong."), "Your body pain seems mostly because of tiredness and viral.", lang)
    if "fever" in text or "bukhar" in text or "बुखार" in text:
        if lang == "Hindi":
            return make_answer("बुखार", [("वायरल बुखार","मौसम बदलने से वायरस से बुखार आ जाता है।"),("सर्दी","गले में खराश और सर्दी के साथ भी हल्का बुखार आ सकता है।"),("पानी की कमी","पानी कम पीने से शरीर गरम हो जाता है।")], [("तेज बुखार","बुखार 102 से ऊपर हो, तो तुरंत डॉक्टर को दिखाएं।"),("उल्टी / चक्कर","उल्टी या चक्कर आए, तो देर मत करें।")], [("आराम करें","पूरा आराम करें।"),("ठंडी पट्टी","सिर पर ठंडे पानी की पट्टी रखें।"),("गुनगुना पानी","थोड़ा-थोड़ा करके गुनगुना पानी पिएं।")], ("तुलसी काढ़ा","तुलसी और अदरक का काढ़ा पीने से बुखार में आराम मिलता है।"), "आपका बुखार अभी शुरू हुआ लग रहा है, 1 दिन आराम करके देखिए।", lang)
        else:
            return make_answer("Fever", [("Viral Fever","Change in weather causes viral infection."),("Cold","Throat infection and cold can also give mild fever."),("Less Water","Drinking less water makes body hot.")], [("High Fever","If fever above 102, see doctor immediately."),("Vomiting / Dizziness","If vomiting or dizziness, do not wait.")], [("Take Rest","Take full rest."),("Cold Sponge","Keep cold wet cloth on forehead."),("Warm Water","Drink warm water in small sips.")], ("Tulsi Kadha","Tulsi and ginger kadha gives relief in fever."), "Your fever seems in starting stage, take rest for 1 day.", lang)
    if "cold" in text or "cough" in text or "khansi" in text or "sardi" in text or "throat" in text or "gala" in text or "gale" in text or "सर्दी" in text or "खांसी" in text or "गला" in text:
        if lang == "Hindi":
            return make_answer("सर्दी-खांसी", [("वायरल संक्रमण","मौसम बदलने से गले में वायरस लग जाता है।"),("ठंडा पानी","ठंडा पानी या आइसक्रीम से गला खराब हो जाता है।"),("धूल","धूल-मिट्टी से एलर्जी हो जाती है।")], [("सांस में दिक्कत","सांस लेने में तकलीफ हो, तो तुरंत डॉक्टर को दिखाएं।"),("खून वाली खांसी","खांसी में खून आए, तो देर मत करें।")], [("गरम पानी","दिन भर गुनगुना पानी पिएं।"),("हल्दी दूध","रात को हल्दी वाला गरम दूध पिएं।"),("भाप","गरम पानी की भाप लेने से नाक खुल जाती है।")], ("तुलसी-अदरक","तुलसी और अदरक की चाय से गले को आराम मिलता है।"), "आपकी सर्दी-खांसी अभी शुरू हुई लग रही है, 2 दिन गरम चीजें लीजिए।", lang)
        else:
            return make_answer("Cold-Cough", [("Viral Infection","Change in weather causes virus in throat."),("Cold Water","Cold water or ice-cream makes throat bad."),("Dust Allergy","Dust causes allergy and cough starts.")], [("Breathing Problem","If difficulty in breathing, see doctor immediately."),("Blood in Cough","If blood comes in cough, do not wait.")], [("Warm Water","Drink warm water through the day."),("Turmeric Milk","Drink warm turmeric milk at night."),("Steam","Take steam from hot water.")], ("Tulsi-Ginger","Tulsi and ginger tea gives relief to throat."), "Your cold-cough seems in starting stage, take warm things for 2 days.", lang)
    if "stomach" in text or "pet" in text or "gas" in text or "ulti" in text or "vomit" in text or "dast" in text or "loose" in text or "diarrhea" in text or "पेट" in text or "उल्टी" in text:
        if lang == "Hindi":
            return make_answer("पेट दर्द", [("गैस","बाहर का खाना या जल्दी खाने से पेट में गैस बन जाती है।"),("एसिडिटी","मसालेदार खाना या खाली पेट रहने से एसिडिटी हो जाती है।"),("कब्ज","पानी कम पीने से कब्ज होता है।")], [("तेज दर्द","पेट में बहुत तेज दर्द हो, तो तुरंत डॉक्टर को दिखाएं।"),("खून","पॉटी में खून आए, तो देर मत करें।")], [("हल्का खाना","आज खिचड़ी, दही जैसा हल्का खाना खाएं।"),("ओआरएस पानी","थोड़ा-थोड़ा करके ओआरएस पिएं।"),("टहलें","खाने के बाद 10 मिनट हल्की टहल करें।")], ("अजवाइन पानी","अजवाइन का पानी गैस में तुरंत आराम देता है।"), "आपका पेट दर्द गैस और एसिडिटी से लग रहा है, आज हल्का खाना खाएं।", lang)
        else:
            return make_answer("Stomach Problem", [("Gas","Eating outside food causes gas."),("Acidity","Spicy food or empty stomach causes acidity."),("Constipation","Drinking less water causes constipation.")], [("Severe Pain","If stomach pain is very severe, see doctor immediately."),("Blood","If blood comes in stool, do not wait.")], [("Light Food","Eat light food like khichdi, curd."),("ORS Water","Drink ORS in small sips."),("Walk","Walk 10 minutes after food.")], ("Ajwain Water","Ajwain water gives instant relief in gas."), "Your stomach pain seems due to gas and acidity, eat light food today.", lang)
    if "chest" in text or "seene" in text or "saans" in text or "breath" in text or "सीने" in text or "सांस" in text:
        if lang == "Hindi":
            return make_answer("सीने में दर्द", [("गैस","पेट की गैस ऊपर चढ़ने से सीने में भारीपन लगता है।"),("सर्दी","सर्दी और धूल से सीने में जकड़न हो जाती है।"),("थकान","ज्यादा काम करने से सांस फूलने लगती है।")], [("बहुत तेज दर्द","सीने में बहुत तेज दर्द हो, तो तुरंत 108 पर कॉल करें।"),("पसीना","सीने के दर्द के साथ पसीना आए, तो तुरंत अस्पताल जाएं।")], [("सीधा बैठें","सीधा बैठ जाएं, कपड़े ढीले कर दें।"),("हवा","खिड़की खोल दें।"),("गुनगुना पानी","थोड़ा-थोड़ा गुनगुना पानी पिएं।")], ("धूल से बचें","धूल और धुएं से दूर रहें।"), "आपके सीने का दर्द गैस और सर्दी से लग रहा है, लेकिन दर्द तेज है तो तुरंत डॉक्टर को दिखाएं।", lang)
        else:
            return make_answer("Chest Problem", [("Gas","Gas from stomach goes up and causes heaviness in chest."),("Cold","Cold and dust causes tightness in chest."),("Tiredness","Too much work causes breathlessness.")], [("Severe Pain","If chest pain is very severe, call 108 immediately."),("Sweating","If sweating with chest pain, go to hospital fast.")], [("Sit Straight","Sit straight, loosen clothes."),("Air","Open windows."),("Warm Water","Drink warm water in small sips.")], ("Avoid Dust","Stay away from dust and smoke."), "Your chest pain seems due to gas and cold, but if pain is severe, see doctor immediately.", lang)
    if "leg" in text or "pair" in text or "knee" in text or "ghutna" in text or "hand" in text or "haath" in text or "joint" in text or "shoulder" in text or "kandha" in text or "पैर" in text or "हाथ" in text or "घुटना" in text:
        if lang == "Hindi":
            return make_answer("हाथ-पैर दर्द", [("थकान","ज्यादा चलने से हाथ-पैर में दर्द हो जाता है।"),("कैल्शियम की कमी","कैल्शियम की कमी से घुटनों में दर्द होता है।"),("गलत बैठना","गलत बैठने से घुटने पर जोर पड़ता है।")], [("सूजन","बहुत सूजन आ जाए, तो डॉक्टर को दिखाएं।"),("तेज दर्द","दर्द 2 दिन से ज्यादा रहे, तो देर मत करें।")], [("आराम","उस पैर को आराम दें।"),("गरम सेंक","10 मिनट गरम सेंक करें।"),("पैर ऊपर रखें","पैर को तकिए पर ऊपर रखकर लेटें।")], ("दूध पिएं","रोज 1 गिलास दूध पिएं।"), "आपका हाथ-पैर का दर्द थकान और कैल्शियम की कमी से लग रहा है।", lang)
        else:
            return make_answer("Leg / Joint Pain", [("Tiredness","Walking too much causes leg pain."),("Calcium Deficiency","Lack of Calcium causes knee pain."),("Wrong Posture","Wrong sitting puts pressure on knee.")], [("Swelling","If too much swelling, see doctor."),("Severe Pain","If pain stays more than 2 days, do not wait.")], [("Rest","Give rest to that leg."),("Hot Compress","Apply warm cloth for 10 minutes."),("Raise Leg","Keep leg raised on pillow.")], ("Drink Milk","Drink 1 glass milk daily."), "Your leg pain seems due to tiredness and calcium deficiency.", lang)
    if "eye" in text or "aankh" in text or "ankh" in text or "आंख" in text:
        if lang == "Hindi":
            return make_answer("आंख की समस्या", [("फोन / धूल","ज्यादा फोन देखने से आंख में जलन होती है।"),("नींद की कमी","नींद पूरी न होने से आंख लाल हो जाती है।"),("एलर्जी","धूल से आंख में एलर्जी हो जाती है।")], [("दिखाई कम","दिखाई कम हो, तो तुरंत डॉक्टर को दिखाएं।"),("मवाद","आंख से मवाद आए, तो देर मत करें।")], [("आंख मत मसलें","आंख को मसलें नहीं, साफ पानी से धोएं।"),("फोन कम","फोन कम देखिए।"),("ठंडी पट्टी","आंख पर ठंडी पट्टी रखें।")], ("धूप से बचें","धूप में चश्मा पहनें।"), "आपकी आंख की समस्या फोन और धूल की वजह से लग रही है।", lang)
        else:
            return make_answer("Eye Problem", [("Phone / Dust","Too much phone causes burning in eyes."),("Less Sleep","Less sleep makes eyes red."),("Allergy","Dust causes allergy in eyes.")], [("Less Vision","If vision is less, see doctor immediately."),("Pus","If pus comes from eyes, do not wait.")], [("Do Not Rub","Do not rub eyes, wash with clean water."),("Less Phone","Use phone less."),("Cold Cloth","Keep cold cloth on eyes.")], ("Avoid Sun","Wear glasses in sunlight."), "Your eye problem seems due to phone and dust.", lang)
    if "ear" in text or "kaan" in text or "कान" in text:
        if lang == "Hindi":
            return make_answer("कान में दर्द", [("सर्दी","सर्दी के साथ कान में दर्द हो जाता है।"),("पानी","नहाते समय कान में पानी जाने से दर्द होता है।"),("मैल","कान में मैल जमने से दर्द होता है।")], [("सुनाई कम","सुनाई कम दे, तो डॉक्टर को दिखाएं।"),("तेज बुखार","कान दर्द के साथ तेज बुखार हो, तो देर मत करें।")], [("कुछ मत डालें","कान में तीली मत डालें।"),("गरम सेंक","हल्का गरम सेंक करें।"),("आराम","थोड़ी देर आराम करें।")], ("कान साफ रखें","कान को साफ और सूखा रखें।"), "आपके कान का दर्द सर्दी की वजह से लग रहा है।", lang)
        else:
            return make_answer("Ear Pain", [("Cold","Cold causes ear pain."),("Water","Water going in ear during bath causes pain."),("Wax","Wax in ear causes pain.")], [("Less Hearing","If hearing is less, see doctor."),("High Fever","If high fever with ear pain, do not wait.")], [("Do Not Insert","Do not insert anything in ear."),("Warm Compress","Apply light warm compress."),("Rest","Take rest.")], ("Keep Ear Clean","Keep ear clean and dry."), "Your ear pain seems due to cold.", lang)
    if "tooth" in text or "daant" in text or "dant" in text or "दांत" in text:
        if lang == "Hindi":
            return make_answer("दांत में दर्द", [("कीड़ा","दांत में कीड़ा लगने से दर्द होता है।"),("ठंडा-गरम","ठंडा-गरम खाने से दांत में झनझनाहट होती है।"),("मसूड़ा","मसूड़े में सूजन से दांत दुखने लगता है।")], [("सूजन","गालों पर सूजन आ जाए, तो डॉक्टर को दिखाएं।"),("दर्द न रुके","दर्द 2 दिन से न रुके, तो देर मत करें।")], [("नमक पानी","गुनगुने नमक पानी से कुल्ला करें।"),("लौंग","लौंग का तेल लगाएं।"),("ठंडा मत खाएं","ठंडा और मीठा मत खाएं।")], ("ब्रश","दिन में 2 बार ब्रश करें।"), "आपके दांत का दर्द कीड़े और मसूड़े की सूजन से लग रहा है।", lang)
        else:
            return make_answer("Tooth Pain", [("Cavity","Cavity in tooth causes pain."),("Cold-Hot","Cold-hot food causes sensitivity."),("Gum Swelling","Gum swelling causes tooth pain.")], [("Swelling","If cheek swells, see doctor."),("Pain Not Stopping","If pain does not stop in 2 days, do not wait.")], [("Salt Water","Gargle with warm salt water."),("Clove Oil","Apply clove oil."),("Avoid Cold","Avoid cold and sweet.")], ("Brush","Brush 2 times a day."), "Your tooth pain seems due to cavity and gum swelling.", lang)
    if "daane" in text or "rash" in text or "khujli" in text or "itching" in text or "दाने" in text or "खुजली" in text:
        if lang == "Hindi":
            return make_answer("दाने / खुजली", [("एलर्जी","नए साबुन, कपड़े या धूल से एलर्जी हो जाती है।"),("गर्मी","गर्मी में पसीना जमने से दाने निकल आते हैं।"),("संक्रमण","साफ-सफाई न रखने से संक्रमण हो जाता है।")], [("मवाद","दानों से मवाद निकले, तो डॉक्टर को दिखाएं।"),("तेज बुखार","दानों के साथ तेज बुखार हो, तो देर मत करें।"),("सांस में दिक्कत","सांस में दिक्कत हो तो तुरंत 108 पर कॉल करें।")], [("खुजलाएं नहीं","दानों को खुजलाएं नहीं, इससे संक्रमण बढ़ता है।"),("साफ रखें","साफ पानी से धोकर सुखा रखें।"),("ठंडा पानी","ठंडे पानी से सेंक करें।"),("नारियल तेल","हल्का नारियल तेल लगाएं।")], ("साफ कपड़े","रोज साफ कपड़े पहनें, पसीने वाले कपड़े तुरंत बदलें।"), "आपके दाने एलर्जी या गर्मी की वजह से लग रहे हैं। 2 दिन में कम न हों तो डॉक्टर को दिखाएं।", lang)
        else:
            return make_answer("Rash / Itching", [("Allergy","New soap, clothes or dust causes allergy."),("Heat","Sweat causes rashes in heat."),("Infection","Lack of cleanliness causes infection.")], [("Pus","If pus comes, see doctor."),("High Fever","If high fever with rashes, do not wait."),("Breathing Problem","If breathing problem, call 108 immediately.")], [("Do Not Scratch","Do not scratch, it increases infection."),("Keep Clean","Wash with clean water and keep dry."),("Cold Water","Apply cold water compress."),("Coconut Oil","Apply light coconut oil.")], ("Clean Clothes","Wear clean clothes daily, change sweaty clothes immediately."), "Your rash seems due to allergy or heat. If not better in 2 days, see doctor.", lang)
    if "chot" in text or "zakhm" in text or "wound" in text or "injury" in text or "kat" in text or "cut" in text or "चोट" in text:
        if lang == "Hindi":
            return make_answer("चोट / जख्म", [("गिरना","गिरने या टकराने से चोट लग जाती है।"),("तेज चीज","चाकू या कांच से कटने से जख्म हो जाता है।"),("जलना","गरम चीज से जलने से चोट लगती है।")], [("बहुत खून","खून रुक न रहा हो, तो तुरंत 108 पर कॉल करें।"),("गहरी चोट","गहरी चोट हो या हड्डी दिख रही हो, तो तुरंत अस्पताल जाएं।"),("बुखार","चोट के बाद बुखार आए, तो डॉक्टर को दिखाएं।")], [("साफ पानी से धोएं","चोट को साफ पानी से धोएं, गंदे पानी से नहीं।"),("खून रोकें","साफ कपड़े से चोट को दबाकर रखें, 10 मिनट तक मत हटाएं।"),("बेटाडीन लगाएं","हल्का बेटाडीन लगाएं, हल्दी / मिट्टी / टूथपेस्ट मत लगाएं।"),("पट्टी बांधें","साफ पट्टी बांधें।")], ("साफ रखें","चोट को गंदा मत होने दें, रोज पट्टी बदलें।"), "आपकी चोट को साफ रखना सबसे जरूरी है। गहरी चोट हो तो तुरंत अस्पताल जाएं।", lang)
        else:
            return make_answer("Injury / Wound", [("Fall","Falling or hitting causes injury."),("Sharp Object","Knife or glass cut causes wound."),("Burn","Hot thing causes burn injury.")], [("Heavy Bleeding","If bleeding is not stopping, call 108 immediately."),("Deep Wound","If wound is deep or bone is visible, go to hospital immediately."),("Fever","If fever after injury, see doctor.")], [("Wash With Clean Water","Wash wound with clean water, not dirty water."),("Stop Bleeding","Press with clean cloth for 10 minutes, do not remove."),("Apply Betadine","Apply light Betadine, do not apply haldi / mud / toothpaste."),("Bandage","Tie clean bandage.")], ("Keep Clean","Keep wound clean, change bandage daily."), "Keeping your wound clean is most important. For deep wound, go to hospital immediately.", lang)
    if "allergy" in text or "एलर्जी" in text:
        if lang == "Hindi":
            return make_answer("एलर्जी", [("धूल / साबुन","धूल, नए साबुन या परफ्यूम से एलर्जी हो जाती है।"),("खाना","किसी खाने की चीज से एलर्जी हो सकती है।"),("दवा","किसी दवा से भी एलर्जी हो सकती है।")], [("सांस में दिक्कत","सांस में दिक्कत हो तो तुरंत 108 पर कॉल करें।"),("चेहरा सूजना","चेहरा या होंठ सूज जाएं तो तुरंत अस्पताल जाएं।")], [("खुजलाएं नहीं","खुजलाएं नहीं।"),("ट्रिगर से दूर रहें","जिस चीज से एलर्जी हुई, उससे दूर रहें।"),("ठंडा पानी","ठंडे पानी से सेंक करें।")], ("साफ कपड़े","रोज साफ कपड़े पहनें।"), "आपकी एलर्जी धूल या नए साबुन की वजह से लग रही है।", lang)
        else:
            return make_answer("Allergy", [("Dust / Soap","Dust, new soap or perfume causes allergy."),("Food","Some food can cause allergy."),("Medicine","Some medicine can also cause allergy.")], [("Breathing Problem","If breathing problem, call 108 immediately."),("Face Swelling","If face or lips swell, go to hospital immediately.")], [("Do Not Scratch","Do not scratch."),("Avoid Trigger","Stay away from the thing that caused allergy."),("Cold Water","Apply cold water compress.")], ("Clean Clothes","Wear clean clothes daily."), "Your allergy seems due to dust or new soap.", lang)
    if "chakkar" in text or "dizz" in text or "kamzori" in text or "weak" in text or "neend" in text or "sleep" in text or "चक्कर" in text or "कमजोरी" in text or "नींद" in text:
        if lang == "Hindi":
            return make_answer("चक्कर / कमजोरी", [("खून की कमी","खून की कमी से चक्कर आता है।"),("भूख","भूखे रहने से चक्कर आता है।"),("नींद की कमी","नींद पूरी न होने से कमजोरी लगती है।")], [("बेहोश","बेहोश हो जाएं, तो तुरंत डॉक्टर को दिखाएं।"),("सीने में दर्द","चक्कर के साथ सीने में दर्द हो, तो 108 पर कॉल करें।")], [("बैठ जाएं","चक्कर आए तो तुरंत बैठ जाएं।"),("पानी पिएं","थोड़ा-थोड़ा पानी पिएं।"),("कुछ खाएं","हल्का कुछ खा लें।")], ("पालक खाएं","रोज पालक और गुड़ खाएं।"), "आपका चक्कर खून की कमी और नींद की कमी से लग रहा है।", lang)
        else:
            return make_answer("Dizziness / Weakness", [("Low Blood","Low blood causes dizziness."),("Hunger","Staying hungry causes dizziness."),("Less Sleep","Less sleep causes weakness.")], [("Faint","If you faint, see doctor immediately."),("Chest Pain","If chest pain with dizziness, call 108.")], [("Sit Down","Sit down immediately when dizzy."),("Drink Water","Drink water in small sips."),("Eat Something","Eat something light.")], ("Eat Palak","Eat palak and gud daily."), "Your dizziness seems due to low blood and less sleep.", lang)
    clean = user_text.strip()
    if lang == "Hindi":
        return f"""आपकी तकलीफ समझ सकते हैं, आराम कीजिए।

**संभावित कारण - {clean} की वजह:**

- **थकान:** नींद पूरी न होने या ज्यादा काम करने से {clean} में तकलीफ होने लगती है।
- **संक्रमण:** मौसम बदलने से {clean} में संक्रमण हो जाता है।
- **कमजोरी:** पानी कम पीने से {clean} में कमजोरी और दर्द महसूस होता है।

**खतरे के लक्षण:**

- **तेज दर्द:** अगर {clean} में बहुत तेज दर्द हो, तो तुरंत डॉक्टर को दिखाएं।
- **बुखार / सूजन:** {clean} के साथ तेज बुखार या सूजन हो, तो देर मत करें।

**अभी क्या करें:**

- **आराम करें:** {clean} वाली जगह को आराम दें।
- **गरम सेंक:** {clean} पर हल्का गरम सेंक करें।
- **गुनगुना पानी पिएं:** दिन भर गुनगुना पानी पिएं।

**स्वास्थ्य टिप:**

- **रोज टहलें:** रोज 30 मिनट हल्की टहल से {clean} की तकलीफ कम होती है।

आपकी तकलीफ - {clean} - ज्यादातर थकान की वजह से लग रही है, 1-2 दिन आराम कीजिए।

क्या आप डॉक्टर से बात करना चाहेंगी?"""
    else:
        return f"""I understand, please take rest.

**Possible Causes - Why {clean} happens:**

- **Tiredness:** When you do not sleep well or work too much, you feel problem in {clean}.
- **Infection:** Change in weather causes infection in {clean}.
- **Weakness:** Drinking less water causes weakness and pain in {clean}.

**Danger Signs:**

- **Severe Pain:** If pain in {clean} is very severe, see a doctor immediately.
- **Fever / Swelling:** If you get high fever or swelling with {clean}, do not wait.

**What To Do Now:**

- **Take Rest:** Give rest to {clean}.
- **Hot Compress:** Apply warm cloth on {clean}.
- **Drink Warm Water:** Drink warm water through the day.

**Health Tip:**

- **Daily Walk:** Walking 30 minutes daily reduces {clean} problem.

Your problem - {clean} - seems mostly because of tiredness, take rest for 1-2 days.

Would you like to see a doctor?"""

def ask_reply(user_text, placeholder):
    real_lang = detect_language(user_text)
    if not is_health_related(user_text):
        msg = out_of_context_msg(real_lang)
        placeholder.markdown(msg)
        return msg
    instant = get_instant_answer(user_text, real_lang)
    placeholder.markdown(instant)
    return instant
def ask_reply_photo(photo_keyword, photo_desc, placeholder):
    real_lang = "Hindi" if IS_HINDI else "English"
    full_text = f"{photo_keyword} {photo_desc}".strip()
    instant = get_instant_answer(full_text, real_lang)
    placeholder.markdown(instant)
    return instant

# ================= HOME =================
if menu in ["🏠 Home", "🏠 होम"]:
    st.title("🩺 Sehat Saathi")
    if IS_HINDI:
        st.write("नमस्ते, मैं यहाँ आपकी मदद करने के लिए हूँ! 👋")
        st.write("अपनी तकलीफ लिखें, बोलें या फोटो भेजें।")
    else:
        st.write("Hello, I am here to help you! 👋")
        st.write("Write your problem, speak or send photo.")
    # CHAT HISTORY - PHOTO KE NEECHE USKA ANSWER
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            if m.get("type") == "image":
                st.image(m["image"], caption="📸 आपकी फोटो" if IS_HINDI else "📸 Your Photo", use_container_width=True)
                st.markdown(m["content"])
            else:
                st.markdown(m["content"])
            # Agar is message ke saath doctor hai toh usi ke neeche dikhao
            if m.get("show_doctors") and m["role"] == "assistant":
                show_doctors_box(m.get("for_text",""))
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant" and not st.session_state.doctor_asked:
        if "सिर्फ स्वास्थ्य" not in st.session_state.messages[-1]["content"] and "only help with health" not in st.session_state.messages[-1]["content"].lower():
            st.info("👨‍⚕️ क्या आप डॉक्टर से बात करना चाहेंगी?" if IS_HINDI else "👨‍⚕️ Would you like to see a doctor?")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ हाँ, डॉक्टर से बात करें" if IS_HINDI else "✅ Yes, See Doctor", use_container_width=True, key="yes_doctor"):
                    st.session_state.doctor_asked = True
                    last_user = ""
                    for mm in reversed(st.session_state.messages):
                        if mm["role"]=="user":
                            last_user=mm["content"]; break
                    st.session_state.messages.append({"role": "assistant", "content": "DOCTORS_BOX", "show_doctors": True, "for_text": last_user})
                    st.rerun()
            with c2:
                if st.button("❌ नहीं, बस ऐसे ही" if IS_HINDI else "❌ No, Thanks", use_container_width=True, key="no_doctor"):
                    st.session_state.doctor_asked = True
                    st.session_state.messages.append({"role": "assistant", "content": "ठीक है, अपना ख्याल रखिए। तकलीफ बढ़े तो तुरंत 104 या 108 पर कॉल कीजिएगा।" if IS_HINDI else "Okay, take care. If problem increases, call 104 or 108 immediately."})
                    st.rerun()
    st.markdown("---")
    with st.form("chat_form", clear_on_submit=True):
        chat_text = st.text_input("Type...", label_visibility="collapsed", placeholder="अपनी तकलीफ लिखें..." if IS_HINDI else "Write your symptom...")
        submitted = st.form_submit_button("➤ भेजें" if IS_HINDI else "➤ Send", use_container_width=True)
    if submitted and chat_text.strip() != "":
        st.session_state.messages.append({"role": "user", "content": chat_text})
        st.session_state.doctor_asked = False
        with st.chat_message("assistant"):
            placeholder = st.empty()
            reply = ask_reply(chat_text, placeholder)
        st.session_state.messages.append({"role": "assistant", "content": reply, "show_doctors": True, "for_text": chat_text})
        st.rerun()
    # CLEAR CHAT - PHOTO BHI CLEAR
    if st.button("🧹 चैट साफ करें" if IS_HINDI else "🧹 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.doctor_asked = False
        st.session_state["last_audio_id"] = ""
        st.session_state.photo_sent = False
        st.session_state.uploader_key += 1
        st.rerun()
    col_photo, col_audio = st.columns(2)
    with col_photo:
        st.write("📷 फोटो" if IS_HINDI else "📷 Photo")
        uploaded_photo = st.file_uploader("Upload Photo", type=["jpg","jpeg","png"], label_visibility="collapsed", key=f"wa_cam_{st.session_state.uploader_key}")
    with col_audio:
        st.write("🎤 आवाज़" if IS_HINDI else "🎤 Voice")
        audio_input = st.audio_input("Speak", label_visibility="collapsed", key="wa_mic")
    if uploaded_photo:
        st.image(uploaded_photo, width=200)
        if IS_HINDI:
            st.write("📸 यह फोटो किस चीज़ की है?")
            photo_type = st.radio("Photo Type", ["एलर्जी / दाने", "चोट / जख्म", "खुजली / दाने"], label_visibility="collapsed", horizontal=True, key="photo_type_hi")
            photo_desc = st.text_input("फोटो में क्या दिख रहा है?", placeholder="जैसे: हाथ पर लाल दाने...", key="photo_desc_hi")
        else:
            st.write("📸 What is this photo of?")
            photo_type = st.radio("Photo Type", ["Allergy / Rash", "Injury / Wound", "Itching / Rash"], label_visibility="collapsed", horizontal=True, key="photo_type_en")
            photo_desc = st.text_input("What is visible in photo? (optional)", placeholder="Like: red rash on hand...", key="photo_desc_en")
        if st.button("📸 फोटो भेजें" if IS_HINDI else "📸 Send Photo", use_container_width=True):
            if "चोट" in photo_type or "Injury" in photo_type:
                kw = "चोट जख्म" if IS_HINDI else "chot zakhm"
            elif "खुजली" in photo_type or "Itching" in photo_type:
                kw = "खुजली दाने" if IS_HINDI else "khujli rash"
            else:
                kw = "एलर्जी दाने" if IS_HINDI else "allergy daane"
            photo_text = f"{kw} {photo_desc}".strip()
            # PHOTO + USKA ANSWER - EK SAATH, ANSWER PHOTO KE NEECHE
            with st.chat_message("assistant"):
                placeholder = st.empty()
                reply = ask_reply_photo(kw, photo_desc, placeholder)
            st.session_state.messages.append({"role": "user", "content": photo_text, "type": "image", "image": uploaded_photo})
            st.session_state.messages.append({"role": "assistant", "content": reply, "show_doctors": True, "for_text": photo_text})
            st.session_state.doctor_asked = False
            st.session_state.photo_sent = True
            st.session_state.uploader_key += 1
            st.rerun()
    if audio_input and st.session_state.get("last_audio_id") != str(audio_input):
        st.session_state["last_audio_id"] = str(audio_input)
        with st.spinner("सुन रहे हैं..." if IS_HINDI else "Listening..."):
            voice_text = speech_to_text(audio_input.read())
        if voice_text and not voice_text.startswith("ERROR:"):
            st.success(f"🗣️ आपने बोला: {voice_text}" if IS_HINDI else f"🗣️ You said: {voice_text}")
            st.session_state.messages.append({"role": "user", "content": voice_text})
            st.session_state.doctor_asked = False
            with st.chat_message("assistant"):
                placeholder = st.empty()
                reply = ask_reply(voice_text, placeholder)
            st.session_state.messages.append({"role": "assistant", "content": reply, "show_doctors": True, "for_text": voice_text})
            st.rerun()
        else:
            st.warning("आवाज़ समझ नहीं आई, दोबारा बोलिए।" if IS_HINDI else "Could not understand, please speak again.")
    show_floating_banner()

elif menu in ["💊 Medicine Reminder", "💊 दवाई रिमाइंडर"]:
    if IS_HINDI:
        st.title("💊 दवाई रिमाइंडर")
        st.write("दवाई का समय सेट कीजिए, समय होने पर ऐप याद दिलाएगा।")
    else:
        st.title("💊 Medicine Reminder")
        st.write("Set medicine time, app will remind you.")
    with st.form("reminder_form"):
        med_name = st.text_input("दवाई का नाम" if IS_HINDI else "Medicine Name", placeholder="दवाई का नाम लिखें..." if IS_HINDI else "Write medicine name...", value="")
        st.write("समय" if IS_HINDI else "Time")
        c_h, c_m, c_ap = st.columns(3)
        with c_h:
            hour = st.selectbox("घंटा" if IS_HINDI else "Hour", list(range(1, 13)), index=7)
        with c_m:
            minute = st.selectbox("मिनट" if IS_HINDI else "Minute", [f"{i:02d}" for i in range(0, 60)], index=0)
        with c_ap:
            ampm = st.radio("AM / PM", ["AM", "PM"], horizontal=True)
        med_days = st.number_input("कितने दिन तक?" if IS_HINDI else "How many days?", min_value=1, max_value=30, value=3)
        if st.form_submit_button("✅ रिमाइंडर सेट करें" if IS_HINDI else "✅ Set Reminder", use_container_width=True):
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
                st.session_state.reminders.append({"name": med_name.strip(), "time": time_str, "display": display_time, "days": med_days, "hour24": hour_24, "minute": minute})
                st.success(f"✅ रिमाइंडर सेट: {med_name.strip()} - {display_time} - {med_days} दिन" if IS_HINDI else f"✅ Reminder set: {med_name.strip()} - {display_time} - {med_days} days")
    st.markdown("---")
    st.write("📋 **आपके रिमाइंडर**" if IS_HINDI else "📋 **Your Reminders**")
    now_str = datetime.datetime.now().strftime("%H:%M")
    for r in st.session_state.reminders:
        r_time_short = r["time"][:5]
        show_time = r.get("display", r["time"])
        if r_time_short == now_str:
            st.error(f"🔔 दवाई का समय हो गया! {r['name']} ले लीजिए! - {show_time}" if IS_HINDI else f"🔔 TIME FOR MEDICINE! Take {r['name']} now! - {show_time}")
        st.info(f"💊 {r['name']} - ⏰ {show_time} - 📅 {r['days']} दिन" if IS_HINDI else f"💊 {r['name']} - ⏰ {show_time} - 📅 {r['days']} days")
        today = datetime.date.today().strftime("%Y%m%d")
        hh = str(r.get("hour24", 9)).zfill(2)
        mm = str(r.get("minute", "00")).zfill(2)
        gcal_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={urllib.parse.quote(r['name'] + ' - Dawa Leni Hai')}&dates={today}T{hh}{mm}00/{today}T{hh}{mm}00&recur=RRULE:FREQ=DAILY;COUNT={r['days']}&details={urllib.parse.quote('Daily Medicine Reminder - ' + r['name'])}"
        st.link_button("📅 गूगल कैलेंडर में जोड़ें - रोज़ दोहराएं" if IS_HINDI else "📅 Add to Google Calendar - Daily Repeat", gcal_url, use_container_width=True)
    if st.session_state.reminders:
        if st.button("🗑️ सारे रिमाइंडर हटाएं" if IS_HINDI else "🗑️ Delete All Reminders", use_container_width=True):
            st.session_state.reminders = []
            st.rerun()
    else:
        st.write("अभी कोई रिमाइंडर नहीं है।" if IS_HINDI else "No reminders yet.")
    show_floating_banner()

elif menu in ["👨‍⚕️ Talk To Doctor", "👨‍⚕️ डॉक्टर से बात करें"]:
    if IS_HINDI:
        st.title("👨‍⚕️ डॉक्टर से बात करें")
        st.success("ये सब सरकारी डॉक्टर की सेवाएं हैं, 100% असली।")
    else:
        st.title("👨‍⚕️ Talk To Doctor")
        st.success("All these are Government doctor services, 100% Real.")
    show_doctors_box("general")
    if IS_HINDI:
        st.markdown("---")
        st.markdown("### 2. 📞 104 - हेल्थ हेल्पलाइन")
        st.link_button("📞 104 पर कॉल करें", "tel:104", use_container_width=True)
        st.markdown("### 3. 🏥 नज़दीकी सरकारी अस्पताल")
        st.write("- **सुबह:** 9 बजे से 1 बजे तक ओपीडी")
    else:
        st.markdown("---")
        st.markdown("### 2. 📞 104 - Health Helpline")
        st.link_button("📞 Call 104", "tel:104", use_container_width=True)
        st.markdown("### 3. 🏥 Nearest Government Hospital")
        st.write("- **Morning:** 9 AM to 1 PM OPD")
    show_floating_banner()

elif menu in ["🚨 Emergency", "🚨 आपातकाल"]:
    if IS_HINDI:
        st.title("🚨 आपातकाल - Emergency")
        st.error("अगर तकलीफ बहुत ज़्यादा है तो पहले CALL करें, ऐप का इंतज़ार मत करें!")
        st.markdown("### 📞 आपातकालीन नंबर - पहले इन पर कॉल करें")
        st.link_button("🚑 108 - एम्बुलेंस बुलाएं", "tel:108", use_container_width=True)
        st.link_button("🚓 112 - पुलिस / आपातकाल", "tel:112", use_container_width=True)
        st.link_button("🔥 101 - फायर ब्रिगेड", "tel:101", use_container_width=True)
        st.link_button("📞 104 - हेल्थ हेल्पलाइन", "tel:104", use_container_width=True)
        st.link_button("👧 1098 - चाइल्ड हेल्पलाइन", "tel:1098", use_container_width=True)
        st.link_button("👩 181 - महिला हेल्पलाइन", "tel:181", use_container_width=True)
        st.markdown("---")
        st.markdown("### 🆘 अपनी इमरजेंसी लिखें / बोलें")
        st.write("जैसे: हाथ कट गया, खून आ रहा है, सांस नहीं आ रही")
        em_text = st.text_input("इमरजेंसी लिखें...", placeholder="इमरजेंसी लिखें - जैसे हाथ कट गया...", key="em_text")
        em_audio = st.audio_input("इमरजेंसी बोलें", key="em_mic")
        em_final = em_text
        if em_audio and st.session_state.get("last_em_audio") != str(em_audio):
            st.session_state["last_em_audio"] = str(em_audio)
            vt = speech_to_text(em_audio.read())
            if vt and not vt.startswith("ERROR:"):
                st.success(f"🗣️ आपने बोला: {vt}")
                em_final = vt
        if st.button("🚨 इमरजेंसी स्टेप्स देखें", use_container_width=True):
            e = (em_final or "").lower()
            if e.strip()=="":
                st.warning("पहले अपनी इमरजेंसी लिखें या बोलें।")
            elif "कट" in e or "खून" in e or "blood" in e or "चोट" in e:
                st.error("**कट / खून - एम्बुलेंस आने तक:**\n1. 108 पर कॉल करें\n2. साफ कपड़े से ज़ोर से दबाएं\n3. हाथ / पैर ऊपर रखें\n4. मरीज़ को हिलाएं नहीं")
            elif "सांस" in e or "breath" in e or "गला" in e:
                st.error("**सांस की समस्या - एम्बुलेंस आने तक:**\n1. 108 पर कॉल करें\n2. मरीज़ को सीधा बैठाएं\n3. गले के कपड़े ढीले कर दें\n4. खिड़की खोल दें")
            elif "बुखार" in e or "fever" in e:
                st.error("**तेज़ बुखार - एम्बुलेंस आने तक:**\n1. ठंडी पट्टी रखें\n2. भारी कपड़े हटा दें\n3. थोड़ा-थोड़ा पानी पिलाते रहें")
            elif "उल्टी" in e or "vomit" in e:
                st.error("**उल्टी - एम्बुलेंस आने तक:**\n1. मरीज़ को एक तरफ लिटाएं\n2. थोड़ा-थोड़ा ओआरएस पिलाएं\n3. खाना मत दें")
            elif "बेहोश" in e or "faint" in e:
                st.error("**बेहोश - एम्बुलेंस आने तक:**\n1. सांस चेक करें\n2. सांस चल रही है तो एक तरफ लिटाएं\n3. पानी / खाना मत पिलाएं\n4. तुरंत 108 पर कॉल करें")
            else:
                st.error("**इमरजेंसी - एम्बुलेंस आने तक:**\n1. घबराएं नहीं, 108 पर कॉल करें\n2. मरीज़ को सीधा लिटाएं\n3. खून आ रहा है तो साफ कपड़े से दबाएं")
        st.markdown("---")
        st.markdown("### 🆘 इमरजेंसी टिप्स")
        st.write("- **चोट:** साफ कपड़े से दबाएं, हल्दी / मिट्टी मत लगाएं")
        st.write("- **सांस:** सीधा बैठाएं, कपड़े ढीले करें")
        st.write("- **बुखार:** ठंडी पट्टी, थोड़ा-थोड़ा पानी")
        st.write("- **बेहोश:** पानी मत पिलाएं, एक तरफ लिटाएं, 108 पर कॉल करें")
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
        st.markdown("### 🆘 Write / Speak Your Emergency")
        em_text = st.text_input("Write emergency...", placeholder="Write emergency - like hand cut...", key="em_text_en")
        em_audio = st.audio_input("Speak Emergency", key="em_mic_en")
        em_final = em_text
        if em_audio and st.session_state.get("last_em_audio_en") != str(em_audio):
            st.session_state["last_em_audio_en"] = str(em_audio)
            vt = speech_to_text(em_audio.read())
            if vt and not vt.startswith("ERROR:"):
                st.success(f"🗣️ You said: {vt}")
                em_final = vt
        if st.button("🚨 See Emergency Steps", use_container_width=True):
            e = (em_final or "").lower()
            if e.strip()=="":
                st.warning("First write or speak your emergency.")
            elif "cut" in e or "blood" in e or "bleed" in e or "injury" in e:
                st.error("**CUT / BLEEDING - Till Ambulance Arrives:**\n1. Call 108\n2. Press firmly with clean cloth\n3. Keep hand / leg up")
            elif "breath" in e or "choke" in e:
                st.error("**BREATHING PROBLEM - Till Ambulance Arrives:**\n1. Call 108\n2. Make patient sit straight\n3. Loosen clothes around neck")
            elif "fever" in e:
                st.error("**HIGH FEVER - Till Ambulance Arrives:**\n1. Keep cold wet cloth\n2. Remove heavy blanket\n3. Give water in small sips")
            elif "vomit" in e:
                st.error("**VOMITING - Till Ambulance Arrives:**\n1. Make patient lie on one side\n2. Give ORS in small sips")
            elif "faint" in e or "unconscious" in e:
                st.error("**UNCONSCIOUS - Till Ambulance Arrives:**\n1. Check breathing\n2. If breathing, lie on one side\n3. Do not give water / food\n4. Call 108 immediately")
            else:
                st.error("**EMERGENCY - Till Ambulance Arrives:**\n1. Do not panic, call 108\n2. Lay patient straight\n3. If bleeding, press with clean cloth")
        st.markdown("---")
        st.markdown("### 🆘 Emergency Tips")
        st.write("- **Injury:** Press with clean cloth, do not apply haldi / mud")
        st.write("- **Breathing:** Sit straight, loosen clothes")
        st.write("- **Fever:** Cold cloth, water in small sips")
        st.write("- **Unconscious:** Do not give water, lie on side, call 108")
    show_floating_banner()

elif menu in ["💡 Health Tips", "💡 स्वास्थ्य टिप्स"]:
    if IS_HINDI:
        st.title("💡 स्वास्थ्य टिप्स - रोज़ का रूटीन")
        st.write("ये छोटी-छोटी आदतें आपको बड़े रोग से बचा सकती हैं।")
        st.markdown("### 🌅 1. सुबह उठते ही")
        st.write("- **गुनगुना पानी:** सुबह उठते ही 1-2 गिलास गुनगुना पानी पिएं")
        st.write("- **धूप:** सुबह 15 मिनट धूप में बैठें, विटामिन डी मिलता है")
        st.write("- **फोन मत देखें:** उठते ही फोन मत देखें, 30 मिनट बाद देखें")
        st.markdown("### 🚶 2. टहल और व्यायाम")
        st.write("- **रोज़ 30 मिनट टहल:** बीपी, शुगर और वज़न नियंत्रण में रहता है")
        st.write("- **सीढ़ी:** लिफ्ट की जगह सीढ़ी इस्तेमाल करें")
        st.markdown("### 🍲 3. खाना-पीना")
        st.write("- **हरी सब्जियां:** रोज़ एक समय हरी सब्जी खाएं")
        st.write("- **पानी:** दिन में 8 गिलास पानी पिएं")
        st.write("- **नमक-कम:** खाने में नमक और तेल कम रखें")
        st.markdown("### 😴 4. नींद")
        st.write("- **7-8 घंटे:** रोज़ 7-8 घंटे की नींद लें")
        st.write("- **मोबाइल दूर:** सोने से 30 मिनट पहले मोबाइल बंद कर दें")
        st.markdown("### 🧼 5. साफ-सफाई")
        st.write("- **हाथ धोएं:** खाना खाने से पहले हाथ साबुन से धोएं")
        st.write("- **दांत:** दिन में 2 बार ब्रश करें")
        st.markdown("### 👶 7. बच्चों के लिए")
        st.write("- **टीका:** बच्चों के सारे टीके समय पर लगवाएं, पीएचसी में फ्री लगते हैं")
        st.write("- **दूध:** रोज़ 1 गिलास दूध पिलाएं")
        st.markdown("### 👵 8. बुजुर्गों के लिए")
        st.write("- **बीपी-शुगर जांच:** महीने में 1 बार बीपी और शुगर जांच करवाएं, पीएचसी में फ्री होता है")
        st.write("- **दवाई समय पर:** दवाई का समय कभी मत छोड़ें")
    else:
        st.title("💡 Health Tips - Daily Routine")
        st.write("These small habits can save you from big diseases.")
        st.markdown("### 🌅 1. Morning")
        st.write("- **Warm Water:** Drink 1-2 glasses of warm water after waking up")
        st.write("- **Sunlight:** Sit in sunlight for 15 minutes, you get Vitamin D")
        st.write("- **No Phone:** Do not see phone just after waking up")
        st.markdown("### 🚶 2. Walk And Exercise")
        st.write("- **30 Min Walk Daily:** Controls BP, sugar and weight")
        st.write("- **Stairs:** Use stairs instead of lift")
        st.markdown("### 🍲 3. Food And Water")
        st.write("- **Green Vegetables:** Eat green vegetables once daily")
        st.write("- **Water:** Drink 8 glasses of water daily")
        st.write("- **Less Salt-Oil:** Keep salt and oil less in food")
        st.markdown("### 😴 4. Sleep")
        st.write("- **7-8 Hours:** Take 7-8 hours sleep daily")
        st.write("- **Mobile Away:** Switch off mobile 30 minutes before sleeping")
        st.markdown("### 🧼 5. Cleanliness")
        st.write("- **Wash Hands:** Wash hands with soap before eating")
        st.write("- **Teeth:** Brush 2 times a day")
        st.markdown("### 👶 7. For Children")
        st.write("- **Vaccination:** Get all vaccines on time, FREE in PHC")
        st.write("- **Milk:** Give 1 glass milk daily")
        st.markdown("### 👵 8. For Elderly")
        st.write("- **BP-Sugar Check:** Check BP and sugar once a month, FREE in PHC")
        st.write("- **Medicine On Time:** Never miss medicine time")
    show_floating_banner()

elif menu in ["⚖️ BMI Calculator", "⚖️ बीएमआई कैलकुलेटर"]:
    if IS_HINDI:
        st.title("⚖️ बीएमआई कैलकुलेटर")
    else:
        st.title("⚖️ BMI Calculator")
    weight = st.number_input("वज़न (kg)" if IS_HINDI else "Weight (kg)", min_value=10.0, max_value=200.0, value=60.0)
    height = st.number_input("ऊंचाई (cm)" if IS_HINDI else "Height (cm)", min_value=100.0, max_value=220.0, value=165.0)
    if st.button("हिसाब लगाएं" if IS_HINDI else "Calculate"):
        h_m = height / 100
        bmi = weight / (h_m * h_m)
        st.success(f"Your BMI: {bmi:.1f}")
        if bmi < 18.5:
            st.write("Underweight - Eat healthy food" if not IS_HINDI else "कम वज़न - स्वस्थ खाना खाएं")
        elif bmi < 25:
            st.write("Normal - Good! Keep it up" if not IS_HINDI else "सामान्य - बहुत बढ़िया!")
        elif bmi < 30:
            st.write("Overweight - Walk daily" if not IS_HINDI else "ज्यादा वज़न - रोज़ टहलें")
        else:
            st.write("Obese - Please consult doctor" if not IS_HINDI else "मोटापा - डॉक्टर से बात करें")
    show_floating_banner()

elif menu in ["🏛️ Government Schemes", "🏛️ सरकारी योजनाएं"]:
    if IS_HINDI:
        st.title("🏛️ सरकारी योजनाएं - फ्री का फायदा उठाएं")
        st.success("ये सब सरकारी योजनाएं हैं, 100% असली और फ्री। किसी को पैसे मत दें।")
        st.markdown("### 1. 🩺 आयुष्मान भारत - पीएमजेएवाई")
        st.write("- **क्या मिलता है:** 5 लाख तक का फ्री इलाज, हर साल, पूरे परिवार के लिए")
        st.write("- **क्या चाहिए:** आधार कार्ड + राशन कार्ड")
        st.link_button("आयुष्मान कार्ड चेक करें", "https://pmjay.gov.in", use_container_width=True)
        st.markdown("---")
        st.markdown("### 2. 💊 जन औषधि - सस्ती दवाई")
        st.write("- **क्या मिलता है:** दवाई 50% से 90% तक सस्ती मिलती है")
        st.write("- **कौन ले सकता है:** कोई भी, सबके लिए है")
        st.link_button("नज़दीकी जन औषधि केंद्र ढूंढें", "https://janaushadhi.gov.in", use_container_width=True)
        st.markdown("---")
        st.markdown("### 3. 🤰 पीएम सुरक्षित मातृत्व - गर्भवती महिला")
        st.write("- **क्या मिलता है:** गर्भवती महिला की फ्री जांच, फ्री दवाई, फ्री अल्ट्रासाउंड")
        st.write("- **कब:** हर महीने की 9 तारीख को पीएचसी में फ्री जांच होती है")
        st.markdown("---")
        st.markdown("### 4. 👶 मिशन इंद्रधनुष - बच्चों के टीके")
        st.write("- **क्या मिलता है:** बच्चों के सारे टीके बिल्कुल फ्री")
        st.write("- **कहां मिलेगा:** गांव के आंगनवाड़ी / पीएचसी में")
        st.markdown("---")
        st.markdown("### 5. 👵 पीएम वय वंदना - बुजुर्गों के लिए")
        st.write("- **क्या मिलता है:** 60 साल से ऊपर के बुजुर्गों को हर महीने पेंशन जैसा पैसा मिलता है")
        st.markdown("---")
        st.markdown("### 6. 🦟 राष्ट्रीय स्वास्थ्य मिशन - फ्री जांच")
        st.write("- **क्या मिलता है:** पीएचसी में बीपी, शुगर, बुखार, मलेरिया की जांच बिल्कुल फ्री")
    else:
        st.title("🏛️ Government Schemes - Take FREE Benefit")
        st.success("All these are Government schemes, 100% Real and FREE. Do not pay money to anyone.")
        st.markdown("### 1. 🩺 Ayushman Bharat - PMJAY")
        st.write("- **Benefit:** FREE treatment up to 5 Lakh, every year, for whole family")
        st.write("- **Need:** Aadhaar Card + Ration Card")
        st.link_button("Check Ayushman Card", "https://pmjay.gov.in", use_container_width=True)
        st.markdown("---")
        st.markdown("### 2. 💊 Jan Aushadhi - Cheap Medicines")
        st.write("- **Benefit:** Medicines 50% to 90% cheaper")
        st.write("- **Who Can Get:** Anyone, for everyone")
        st.link_button("Find Nearest Jan Aushadhi Kendra", "https://janaushadhi.gov.in", use_container_width=True)
        st.markdown("---")
        st.markdown("### 3. 🤰 PM Surakshit Matritva - Pregnant Women")
        st.write("- **Benefit:** FREE checkup, FREE medicine, FREE ultrasound for pregnant women")
        st.write("- **When:** On 9th of every month, FREE checkup in PHC")
        st.markdown("---")
        st.markdown("### 4. 👶 Mission Indradhanush - Children Vaccines")
        st.write("- **Benefit:** All vaccines of children totally FREE")
        st.markdown("---")
        st.markdown("### 5. 👵 PM Vaya Vandana - For Elderly")
        st.write("- **Benefit:** Elderly above 60 years get monthly pension-like money")
        st.markdown("---")
        st.markdown("### 6. 🦟 National Health Mission - FREE Checkup")
        st.write("- **Benefit:** BP, Sugar, Fever, Malaria checkup totally FREE in PHC")
    show_floating_banner()

elif menu in ["ℹ️ About App", "ℹ️ ऐप के बारे में"]:
    if IS_HINDI:
        st.title("ℹ️ ऐप के बारे में - सेहत साथी")
        st.write("सेहत साथी **सबके लिए** बनाया गया है - बच्चों से लेकर बुजुर्गों तक, गांव हो या शहर, सभी लोग इसका इस्तेमाल कर सकते हैं।")
        st.markdown("---")
        st.markdown("### 🩺 यह ऐप क्या है?")
        st.write("सेहत साथी एक हेल्थ हेल्पर ऐप है। जब आपको हल्की तकलीफ होती है - जैसे सिर दर्द, बुखार, सर्दी, पेट दर्द - और आपको समझ नहीं आता कि क्या करें, तो यह ऐप तुरंत आपको समझाता है कि यह किस वजह से हो सकता है, कब खतरा है और अभी क्या करना चाहिए।")
        st.write("यह ऐप डॉक्टर की जगह नहीं लेता, यह बस पहली मदद करता है।")
        st.markdown("---")
        st.markdown("### ✨ फीचर्स")
        st.write("- **💬 चैट:** अपनी तकलीफ लिखकर भेजें")
        st.write("- **🎤 बोलकर बताएं:** माइक दबाकर बोल दीजिए")
        st.write("- **📷 फोटो भेजें:** दाने, चोट या रैश की फोटो भेज दीजिए")
        st.write("- **💊 दवाई रिमाइंडर:** दवाई का समय सेट कीजिए")
        st.write("- **👨‍⚕️ डॉक्टर से बात करें:** सरकारी डॉक्टर, ई-संजीवनी और 104 हेल्पलाइन")
        st.write("- **🚨 आपातकाल:** इमरजेंसी में क्या करना है, किस नंबर पर कॉल करना है")
        st.write("- **💡 स्वास्थ्य टिप्स:** रोज़ का रूटीन, खाना-पीना, नींद, टहल")
        st.write("- **⚖️ बीएमआई कैलकुलेटर:** अपना वज़न सही है या नहीं")
        st.write("- **🏛️ सरकारी योजनाएं:** आयुष्मान, जन औषधि जैसी योजनाओं की जानकारी फ्री में")
        st.markdown("---")
        st.info("⚠️ **ज़रूरी बात:** यह ऐप सिर्फ जानकारी और पहली मदद के लिए है। यह डॉक्टर की जगह नहीं ले सकता। अगर तकलीफ ज़्यादा है, तो तुरंत डॉक्टर को दिखाएं या 108 पर कॉल करें।")
    else:
        st.title("ℹ️ About App - Sehat Saathi")
        st.write("Sehat Saathi is made for **everyone** - from children to elderly, village or city, anyone can use it.")
        st.markdown("---")
        st.markdown("### 🩺 What Is This App?")
        st.write("Sehat Saathi is a health helper app. When you have a small problem - like headache, fever, cold, stomach pain - this app tells you why it can happen, when it is dangerous, and what you should do now.")
        st.write("This app does not replace a doctor, it only gives first help.")
        st.markdown("---")
        st.markdown("### ✨ Features")
        st.write("- **💬 Chat:** Write your problem")
        st.write("- **🎤 Speak:** Press mic and speak")
        st.write("- **📷 Send Photo:** Send photo of rash, injury")
        st.write("- **💊 Medicine Reminder:** Set medicine time")
        st.write("- **👨‍⚕️ Talk To Doctor:** Govt doctor, eSanjeevani and 104 helpline")
        st.write("- **🚨 Emergency:** What to do in emergency, which number to call")
        st.write("- **💡 Health Tips:** Daily routine, food, sleep, walk")
        st.write("- **⚖️ BMI Calculator:** Check if your weight is correct")
        st.write("- **🏛️ Government Schemes:** Ayushman, Jan Aushadhi info FREE")
        st.markdown("---")
        st.info("⚠️ **Important:** This app is only for information and first help. It cannot replace a doctor. If problem is more, see doctor immediately or call 108.")
    show_floating_banner()
