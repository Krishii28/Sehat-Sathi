import streamlit as st
import datetime
import re
import urllib.parse
import json
import urllib.request
st.set_page_config(page_title="Sehat Saathi - India", page_icon="🩺", layout="centered")

# ======================================================
# 🔑 KEY YAHAN MAT DAALNA - KEY SECRETS ME JAYEGI
# ======================================================
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    GEMINI_API_KEY = "PASTE_YOUR_KEY_HERE"

def ask_ai(prompt):
    if not GEMINI_API_KEY or GEMINI_API_KEY == "PASTE_YOUR_KEY_HERE":
        return "ERROR_KEY_MISSING"
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as res:
            out = json.loads(res.read().decode())
        return out["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"ERROR:{str(e)[:200]}"

# ---------- PREMIUM OMBRE - WARM CREAM TO PEACH TO MINT ----------
st.markdown("""
<style>
[data-testid="stToolbar"] {visibility: hidden !important;}
header {visibility: hidden !important;}
footer {visibility: hidden !important;}
.stApp { background: linear-gradient(180deg, #FFFBF2 0%, #FFF7ED 25%, #FEF3C7 50%, #EEF2FF 75%, #F0FDF4 100%) !important; }
.block-container { background: transparent !important; max-width: 1100px !important; padding: 1rem 2rem 100px 2rem !important; }
h1, h2, h3, p, label, .stMarkdown, .stWrite, span, div { color: #1E293B !important; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #FFFFFF 0%, #FFFBEB 100%) !important; border-right: 1px solid #FDE68A; }
section[data-testid="stSidebar"] * { color: #1E293B !important; font-weight: 500 !important; }
.stTextInput input, .stSelectbox div[data-baseweb="select"] div, .stNumberInput input, .stTextArea textarea {
    background: #FFFFFF !important; color: #1E293B !important; border: 1.5px solid #E2E8F0 !important; border-radius: 14px !important; min-height: 52px !important; font-size: 16px !important; box-shadow: 0 2px 8px rgba(0,0,0,0.03) !important;
}
.stTextInput input::placeholder { color: transparent !important; }
.stButton button, .stLinkButton a {
    background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 45%, #EA580C 100%) !important; color: #FFFFFF !important; border: none !important; border-radius: 14px !important; font-weight: 700 !important; min-height: 52px !important; font-size: 16px !important; box-shadow: 0 4px 14px rgba(79,70,229,0.25) !important;
}
.stButton button *, .stLinkButton a * { color: #FFFFFF !important; font-weight: 700 !important; }
div[data-testid="stChatMessage"] { background: #FFFFFF !important; border-radius: 18px !important; border: 1px solid #FDE68A !important; box-shadow: 0 2px 12px rgba(0,0,0,0.04) !important; }
div[data-testid="stChatMessage"] * { color: #1E293B !important; }
.ai-header { background: linear-gradient(90deg, #FFE4E6 0%, #FEF3C7 35%, #D1FAE5 70%, #DBEAFE 100%); padding: 22px; border-radius: 22px; text-align: center; margin-bottom: 14px; border: 1px solid #FDE68A; box-shadow: 0 4px 18px rgba(0,0,0,0.05); }
.ai-header h1 { font-size: 29px; margin: 0; color: #7C2D12 !important; }
.ai-header p { margin: 6px 0 0 0; color: #475569 !important; font-size: 14px; font-weight: 500; }
.doctor-card { background: #FFFFFF; border: 1.5px solid #FDE68A; border-radius: 18px; padding: 18px; margin: 12px 0; box-shadow: 0 4px 16px rgba(245,158,11,0.10); }
.online-card { background: #FFFFFF; border: 1.5px solid #BBF7D0; border-radius: 18px; padding: 16px; margin: 12px 0; box-shadow: 0 4px 16px rgba(0,0,0,0.04); }
.info-box { background: linear-gradient(90deg, #FFFBEB, #FEF3C7); border-radius: 14px; padding: 14px; border: 1px solid #FDE68A; }
.scheme-card { background: #FFFFFF; border: 1.5px solid #FDE68A; border-radius: 18px; padding: 16px; margin: 14px 0; box-shadow: 0 4px 16px rgba(0,0,0,0.04); }
.scheme-card b, .scheme-card span { color: #1E293B !important; }
.hospital-card { background: #FFFFFF; border: 1.5px solid #BBF7D0; border-radius: 18px; padding: 16px; margin: 12px 0; box-shadow: 0 4px 16px rgba(0,0,0,0.04); }
.medicine-card { background: #FFFFFF; border: 1.5px solid #FDE68A; border-radius: 18px; padding: 18px; margin: 12px 0; box-shadow: 0 4px 16px rgba(0,0,0,0.04); }
@media (min-width: 1024px) { .block-container { max-width: 1100px !important; } }
@media (max-width: 768px) { .block-container { max-width: 100% !important; padding: 10px 12px 100px 12px !important; } .ai-header h1 { font-size: 25px !important; } }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
if "doctor_asked" not in st.session_state: st.session_state.doctor_asked = False
if "doctor_step" not in st.session_state: st.session_state.doctor_step = "none"
if "doctor_location" not in st.session_state: st.session_state.doctor_location = {}
if "reminders" not in st.session_state: st.session_state.reminders = []
if "last_audio_id" not in st.session_state: st.session_state["last_audio_id"] = ""
if "uploader_key" not in st.session_state: st.session_state.uploader_key = 0
if "photo_sent" not in st.session_state: st.session_state.photo_sent = False

st.sidebar.write("Language")
lang = st.sidebar.radio("Choose Language", ["English", "Hindi"], label_visibility="collapsed")
IS_HINDI = (lang == "Hindi")
if IS_HINDI:
    menu = st.sidebar.radio("मेनू", ["🏠 होम", "💊 दवाई की जानकारी", "💊 दवाई रिमाइंडर", "👨‍⚕️ डॉक्टर से बात करें", "🚨 आपातकाल", "🏥 अस्पताल खोजें", "💡 स्वास्थ्य टिप्स", "⚖️ बीएमआई कैलकुलेटर", "🏛️ सरकारी योजनाएं", "ℹ️ ऐप के बारे में"])
else:
    menu = st.sidebar.radio("Menu", ["🏠 Home", "💊 Medicine Info", "💊 Medicine Reminder", "👨‍⚕️ Talk To Doctor", "🚨 Emergency", "🏥 Hospital Finder", "💡 Health Tips", "⚖️ BMI Calculator", "🏛️ Government Schemes", "ℹ️ About App"])

def T(hi, en): return hi if IS_HINDI else en

def speech_to_text(audio_bytes):
    try:
        import speech_recognition as sr, io
        r = sr.Recognizer()
        wav_io = io.BytesIO(audio_bytes)
        with sr.AudioFile(wav_io) as source:
            audio_data = r.record(source)
            # Pehle Hindi me try karo, phir English me - jo bhi samajh aaye wahi return karo
            # Taaki audio ki language se hi answer ki language decide ho
            try:
                text_hi = r.recognize_google(audio_data, language="hi-IN")
            except:
                text_hi = ""
            try:
                text_en = r.recognize_google(audio_data, language="en-IN")
            except:
                text_en = ""
            # Agar Hindi me Devanagari ya Hindi roman words hain to Hindi wala lo, warna English wala
            if text_hi and re.search(r'[\u0900-\u097F]', text_hi):
                return text_hi
            if text_hi and any(w in text_hi.lower() for w in ["mere","mera","mujhe","dard","hai","bukhar","sardi","khansi","khujli","pet","sir","kamar","gala","chakkar","ulti","kamzori","neend","chot"]):
                return text_hi
            if text_en:
                return text_en
            return text_hi if text_hi else f"ERROR:Could not understand"
    except Exception as e: return f"ERROR:{str(e)[:100]}"

HEALTH_WORDS = ["daane","rash","chot","zakhm","allergy","khujli","itching","bukhar","fever","dard","pain","dawa","medicine","wound","injury","skin","khaansi","cough","cold","sardi","pet","stomach","sir","head","haath","hand","pair","leg","blood","khoon","burn","jal","soojan","swelling","ulti","vomit","dast","kamzori","weak","neend","sleep","saans","breath","chest","seene","gala","throat","kaan","ear","daant","tooth","aankh","eye","ghutna","knee","kamar","back","badan","body","chakkar","dizzy","gas","acidity","kabz","photo","doctor","hospital","bimar","beemar","tabiyat","dawai","diabetes","sugar","bp","thyroid","asthma","dama","anxiety","depression","stress","period","mahwari","pregnancy","garbh","piles","bawasir","stone","pathri","jaundice","piliya","malaria","dengue","typhoid","tb","cancer","hiv","pneumonia","corona","sinus","tonsil","pimple","muhase","dandruff","baal","fungal","eczema","psoriasis","vitiligo","ulcer","appendix","keede","gathiya","arthritis","sciatica","moch","freeze","mirgi","daura","yaadash","ghabrahat","udaasi","peshaab","uti","liver","hepatitis","cholesterol","dil","dhadkan","naak","motiyabind","chashma","aids","tumor","kidney","paralysis","lakwa","vitamin","infection","bacteria","virus","haddi","nas","dimaag","brain","heart","lung","fefe","दाने","चोट","खुजली","बुखार","दर्द","सांस","सीने","पेट","सिर","कमर","गला","कान","दांत","आंख","पैर","हाथ","घुटना","चक्कर","उल्टी","कमजोरी","नींद","शुगर","मधुमेह","थायराइड","दमा","माहवारी","गर्भ","बवासीर","पथरी","पीलिया","मलेरिया","डेंगू","टाइफाइड","टीबी","कैंसर","निमोनिया","साइनस","मुहासे","बाल","गठिया","मिर्गी","घबराहट","उदासी","पेशाब","लीवर","कोलेस्ट्रॉल","दिल","नाक","मोतियाबिंद","लकवा","दिमाग","हड्डी"]
OUT_WORDS = ["movie","film","cricket","football","game","padhai","study","exam","joke","song","gaana","politics","news","weather","mausam","love","shaadi","job","naukri","paisa","money","shopping","birthday","car","bike","dog","cat","kutta","billi","food","khana","recipe","kapde","clothes","mobile","phone","computer","laptop","school","college","teacher","actor","singer","dance","nach","khel","match","ipl","bhabhi","padosi","मूवी","फिल्म","क्रिकेट","गाना","जोक","पढ़ाई","परीक्षा","नौकरी","पैसा","शॉपिंग","मौसम","राजनीति"]
def is_health_related(text):
    t = (text or "").lower()
    if any(w in t for w in OUT_WORDS): return False
    if any(w in t for w in HEALTH_WORDS): return True
    if t.strip() in ["hi","hello","namaste","hey","hii","नमस्ते"]: return True
    return False
def out_of_context_msg(real_lang):
    return "मैं सिर्फ स्वास्थ्य, चोट और एलर्जी से जुड़ी मदद कर सकती हूँ। अपनी स्वास्थ्य समस्या बताइए।" if real_lang=="Hindi" else "I can only help with health, injury and allergy related problems. Please tell your health problem."
def detect_language(user_text):
    # Audio / Text ki boli hui language se hi decide hoga - Sidebar se nahi
    if re.search(r'[\u0900-\u097F]', user_text): return "Hindi"
    hindi_words = ["mere","mera","mujhe","dard","hai","sar","sir","kamar","pet","badan","bukhar","sardi","khansi","khujli","daane","gala","kaan","daant","aankh","pair","haath","ghutna","chakkar","ulti","dast","kamzori","neend","chot","seene","saans"]
    for w in hindi_words:
        if w in user_text.lower(): return "Hindi"
    # Agar koi Hindi nishan nahi hai to English samjho - Sidebar par depend mat karo
    # Lekin agar user ne Sidebar me Hindi select kiya hai aur text me English-Hindi mix nahi hai, tabhi sidebar use karo
    if IS_HINDI and re.search(r'[a-zA-Z]', user_text) is None:
        return "Hindi"
    # Text input ke liye Sidebar wali language, Audio ke liye boli hui language (upar se hi return ho jayegi)
    return "English" if re.search(r'[a-zA-Z]', user_text) and not any(w in user_text.lower() for w in hindi_words) else ("Hindi" if IS_HINDI else "English")

def get_instant_answer(user_text, lang_text):
    if lang_text == "Hindi":
        lang_rule = "Answer ONLY in proper, formal Hindi in Devanagari script. Do NOT use English or Hinglish words, except medicine names. Use simple, clear Hindi."
    else:
        lang_rule = "Answer ONLY in proper, formal, clear English. Do NOT use Hindi or Hinglish words. Use simple English that everyone can understand."
    prompt = f"""
    User ka symptom / problem hai: {user_text}
    User ki language hai: {lang_text}
    {lang_rule}
    Tu ek helpful Health AI hai. Usi language me jawab de.
    Koi dawai ka naam, dose mat likh. Sirf ghar pe kya karna hai, wo bata.
    Jawab ISI format me de:
    **Possible Cause:**
    [2-3 line me kya ho sakta hai]
    **Danger Sign:**
    [kab doctor ke paas jana chahiye, kab 108 par call karni chahiye]
    **What To Do Now:**
    [ghar pe abhi kya karna hai, 3-4 points me]
    **Health Tip:**
    [1 achhi tip jo isi problem se judi ho]
    Last me 1 line: Ye sirf jaankari hai, doctor ki salah zaroori hai.
    """
    ans = ask_ai(prompt)
    if ans == "ERROR_KEY_MISSING":
        return "⚠️ Pehle Secrets me apni Gemini Key daalo, tabhi AI jawab dega." if lang_text=="Hindi" else "⚠️ First add your Gemini Key in Secrets, then AI will answer."
    return ans

def get_medicine_info(med_name, lang):
    if lang == "Hindi":
        lang_rule = "Answer ONLY in proper, formal Hindi in Devanagari script. Do NOT use English or Hinglish words, except medicine names."
    else:
        lang_rule = "Answer ONLY in proper, formal, clear English. Do NOT use Hindi or Hinglish words."
    prompt = f"""
    Dawai ka naam hai: {med_name}
    Language: {lang}
    {lang_rule}
    Usi language me jawab de, simple ghar wali language me.
    Format:
    **💊 {med_name}**
    **Ye dawai kya hai?**
    [2-3 line me is dawai ka kaam kya hai]
    **Kaise leni hai?**
    [general jaankari - hamesha doctor ke bataye hisaab se lena hai, ye likhna zaroori hai]
    **Side Effects / Savdhani:**
    [aam side effects aur savdhani]
    **⚠️ Zaroori Baat:** Ye jaankari sirf samajhne ke liye hai. Koi bhi dawai lene se pehle doctor ya pharmacist se poochh lo. Agar allergy, saans me takleef ya chehra sooj jaye toh turant 108 par call karo.
    Koi fixed dose mat batao, sirf general jaankari do.
    """
    ans = ask_ai(prompt)
    if ans == "ERROR_KEY_MISSING":
        return "⚠️ Pehle Secrets me apni Gemini Key daalo." if lang=="Hindi" else "⚠️ First add your Gemini Key in Secrets."
    return ans

def get_doctor_info_ai(user_text, lang):
    if lang == "Hindi":
        lang_rule = "Answer ONLY in proper Hindi in Devanagari script. No Hinglish."
    else:
        lang_rule = "Answer ONLY in proper English. No Hindi or Hinglish."
    prompt = f"""
    User ki takleef hai: {user_text}
    Language: {lang}
    {lang_rule}
    Usi language me batao:
    1. Is takleef ke liye kaunse specialist doctor ko dikhana chahiye - sirf doctor ka naam
    2. Ye doctor kya karte hain - 2 line me
    3. Kab turant dikhana chahiye - 2 line me
    4. Andazan fees India me kya hoti hai
    Short me jawab de, format me: SPEC | WORK | WHEN | FEES - har ek alag line me.
    """
    ans = ask_ai(prompt)
    return ans

def get_hospitals_for(city, pincode):
    c = city.strip().title() if city.strip() else "Your City"
    return [
        {"name": f"District Government Hospital - {c}", "type": T("सरकारी - फ्री इलाज","Govt - FREE Treatment"), "addr": T(f"{c}, Pincode - {pincode}, India", f"{c}, Pincode - {pincode}, India"), "phone": "108"},
        {"name": f"Civil Hospital - {c}", "type": T("सरकारी - OPD 9 AM - 1 PM","Govt - OPD 9 AM - 1 PM"), "addr": T(f"Main Road, {c} - {pincode}","Main Road, "+c+" - "+pincode), "phone": "104"},
        {"name": f"PHC / Community Health Centre - {c}", "type": T("सरकारी - PHC - फ्री जांच","Govt - PHC - FREE Checkup"), "addr": T(f"Near Bus Stand, {c} - {pincode}","Near Bus Stand, "+c+" - "+pincode), "phone": "104"},
        {"name": f"Apollo / Private Hospital - {c}", "type": T("प्राइवेट - 24x7 इमरजेंसी","Private - 24x7 Emergency"), "addr": T(f"City Centre, {c} - {pincode}","City Centre, "+c+" - "+pincode), "phone": "1860-500-1066"},
        {"name": f"Jan Aushadhi Kendra - {c}", "type": T("सस्ती दवाई - 50% to 90% सस्ती","Cheap Medicine - 50% to 90% Cheaper"), "addr": T(f"Market Road, {c} - {pincode}","Market Road, "+c+" - "+pincode), "phone": "1800-180-8080"},
    ]

PRACTO_SLUG = {"fever":"general-physician","back":"orthopedist","skin":"dermatologist","stomach":"gastroenterologist","head":"neurologist","chest":"cardiologist","tooth":"dentist","eye":"ophthalmologist","ear":"ent-specialist","injury":"orthopedist","diabetes":"diabetologist","heart":"cardiologist","mental":"psychiatrist","kidney":"nephrologist","liver":"hepatologist","piles":"general-surgeon","ladies":"gynecologist","child":"pediatrician","serious":"general-physician","general":"general-physician"}
APOLLO_SLUG = {"fever":"general-physician","back":"orthopedics","skin":"dermatology","stomach":"gastroenterology","head":"neurology","chest":"cardiology","tooth":"dentistry","eye":"ophthalmology","ear":"ent","injury":"orthopedics","diabetes":"endocrinology","heart":"cardiology","mental":"psychiatry","kidney":"nephrology","liver":"hepatology","piles":"general-surgery","ladies":"obstetrics-and-gynecology","child":"pediatrics","serious":"general-physician","general":"general-physician"}

def get_category_for(text):
    t = (text or "").lower()
    if any(k in t for k in ["daane","rash","khujli","itching","allergy","दाने","खुजली","skin","pimple","muhase","मुहासे","dandruff","baal","बाल","fungal","eczema","psoriasis","vitiligo","daag","dhabbe"]): return "skin"
    if any(k in t for k in ["chot","zakhm","wound","injury","kat","cut","चोट","moch","toot","fracture","jalna","burn","जल","paralysis","lakwa","लकवा"]): return "injury"
    if any(k in t for k in ["chest","seene","saans","breath","सीने","सांस","asthma","dama","दमा","pneumonia","nimoniya","निमोनिया","corona","lung","fefe"]): return "chest"
    if any(k in t for k in ["diabetes","sugar","शुगर","madhumeh","thyroid","थायराइड"]): return "diabetes"
    if any(k in t for k in ["bp","blood pressure","cholesterol","कोलेस्ट्रॉल","dil","dhadkan","heart","हृदय"]): return "heart"
    if any(k in t for k in ["anxiety","depression","stress","ghabrahat","घबराहट","udaasi","उदासी","neend","sleep","नींद","yaadash","mirgi","daura","मिर्गी","brain","dimaag","दिमाग"]): return "mental"
    if any(k in t for k in ["stone","pathri","पथरी","kidney","uti","peshaab","पेशाब","urine"]): return "kidney"
    if any(k in t for k in ["jaundice","piliya","पीलिया","liver","लीवर","hepatitis"]): return "liver"
    if any(k in t for k in ["piles","bawasir","बवासीर","fissure","appendix","ulcer","keede","कीड़े"]): return "piles"
    if any(k in t for k in ["period","mahwari","माहवारी","pregnancy","garbh","गर्भ","pregnant","delivery","white discharge"]): return "ladies"
    if any(k in t for k in ["bachche","bachcha","baby","child","बच्च"]): return "child"
    if any(k in t for k in ["malaria","मलेरिया","dengue","डेंगू","typhoid","टाइफाइड","tb","tuberculosis","टीबी","cancer","कैंसर","hiv","tumor","aids"]): return "serious"
    if any(k in t for k in ["bukhar","fever","बुखार","viral"]): return "fever"
    if any(k in t for k in ["pet","stomach","gas","पेट","ulti","vomit","dast","kabz","acidity"]): return "stomach"
    if any(k in t for k in ["sar","head","sir","सिर","migraine","headache"]): return "head"
    if any(k in t for k in ["daant","tooth","दांत"]): return "tooth"
    if any(k in t for k in ["aankh","eye","आंख","motiyabind","मोतियाबिंद","chashma","चश्मा"]): return "eye"
    if any(k in t for k in ["kaan","ear","कान","naak","नाक","sinus","tonsil","awaaz"]): return "ear"
    if any(k in t for k in ["kamar","back","spine","कमर","leg","pair","knee","ghutna","hand","haath","joint","पैर","हाथ","घुटना","badan","body","arthritis","gathiya","गठिया","sciatica","freeze","shoulder","haddi","nas"]): return "back"
    if any(k in t for k in ["cold","cough","khansi","sardi","throat","gala","गला","सर्दी","खांसी"]): return "fever"
    return "general"

def show_doctor_detail_card(user_text, loc):
    cat = get_category_for(user_text)
    city = loc.get("city","")
    pincode = loc.get("pincode","")
    city_slug = city.strip().lower().replace(" ", "-")
    lang_now = "Hindi" if IS_HINDI else "English"
    ai_info = get_doctor_info_ai(user_text, lang_now)
    practo_slug = PRACTO_SLUG.get(cat, "general-physician")
    apollo_slug = APOLLO_SLUG.get(cat, "general-physician")
    practo_direct = f"https://www.practo.com/{city_slug}/{practo_slug}"
    apollo_direct = f"https://www.apollo247.com/specialties/{apollo_slug}"
    google_direct = f"https://www.google.com/maps/search/{urllib.parse.quote('doctor near ' + city + ' ' + pincode + ' India')}"
    st.markdown(f"""<div class="doctor-card"><b>👨‍⚕️ {T('आपको इस डॉक्टर की जरूरत है:','You need this doctor:')}</b><br><br><span>{ai_info}</span><br><br><span><b>{T('आपका इलाका:','Your Area:')}</b> {city}, {pincode}, India</span></div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="info-box"><b>{T('📍 आपके पास के डॉक्टर - Maps पर असली डॉक्टर देखें','📍 Doctors Near You - See Real Doctors On Maps')}</b><br>{T('नीचे क्लिक करते ही गूगल मैप्स आपके शहर और पिनकोड के उसी बीमारी के असली डॉक्टर दिखा देगा - नाम, नंबर, रेटिंग सब।','On clicking below, Google Maps will show real doctors of your city and pincode for same disease - name, number, rating.')}</div>""", unsafe_allow_html=True)
    st.link_button(f"📍 {T('मेरे पास के डॉक्टर देखें - Maps','See Doctors Near Me - Maps')}", google_direct, use_container_width=True)
    st.markdown(f"### {T('🌐 ऑनलाइन डॉक्टर - उसी बीमारी के डॉक्टर से डायरेक्ट बात करें','🌐 Online Doctors - Talk Directly To Same Disease Doctor')}")
    st.markdown(f"""<div class="online-card"><b>💻 {T('प्रैक्टो - डायरेक्ट डॉक्टर','Practo - Direct Doctors')}</b><br><span>practo.com/{city_slug}/{practo_slug}</span></div>""", unsafe_allow_html=True)
    st.link_button(T(f"💻 डायरेक्ट देखें - प्रैक्टो","💻 Direct Doctors - Practo"), practo_direct, use_container_width=True)
    st.markdown(f"""<div class="online-card"><b>🏥 {T('अपोलो - डायरेक्ट डॉक्टर','Apollo - Direct Doctors')}</b><br><span>apollo247.com/specialties/{apollo_slug}</span><br><span><b>{T('डायरेक्ट नंबर:','Direct Number:')}</b> 1860-500-1066</span></div>""", unsafe_allow_html=True)
    st.link_button(T(f"🏥 डायरेक्ट देखें - अपोलो","🏥 Direct Doctors - Apollo"), apollo_direct, use_container_width=True)
    st.link_button(T("📞 1860-500-1066 पर डायरेक्ट कॉल करें - अपोलो","📞 Call 1860-500-1066 Directly - Apollo"), "tel:18605001066", use_container_width=True)
    st.markdown(f"""<div class="online-card"><b>🩺 {T('ई-संजीवनी - सरकारी, फ्री - डायरेक्ट लॉगिन','eSanjeevani - Govt, FREE - Direct Login')}</b><br><span>{T('समय:','Timing:')} {T('सुबह 10 - शाम 4','10 AM - 4 PM')} | <b>{T('फीस:','Fees:')}</b> {T('बिल्कुल फ्री','Totally FREE')}</span></div>""", unsafe_allow_html=True)
    st.link_button(T("🩺 डायरेक्ट लॉगिन करें - ई-संजीवनी","🩺 Direct Login - eSanjeevani"), "https://esanjeevani.mohfw.gov.in/patient/", use_container_width=True)
    st.link_button(T("📞 104 पर डायरेक्ट कॉल करें","📞 Call 104 Directly"), "tel:104", use_container_width=True)
    st.link_button(T("🚑 108 - एम्बुलेंस","🚑 108 - Ambulance"), "tel:108", use_container_width=True)

def show_location_form(for_text):
    st.markdown(f"### {T('📍 डॉक्टर खोजने के लिए अपनी लोकेशन बताइए','📍 Tell Your Location To Find Doctor')}")
    st.write(T("ये ऐप सिर्फ इंडिया के लिए है।","This app is only for India."))
    city = st.text_input(T("शहर का नाम","City Name"), value="", placeholder="", key="loc_city")
    pincode = st.text_input(T("पिनकोड","Pincode"), value="", placeholder="", key="loc_pincode")
    if st.button(T("✅ डॉक्टर खोजें","✅ Find Doctor"), use_container_width=True, key="find_doctor_btn"):
        if city.strip() == "" or pincode.strip() == "":
            st.warning(T("पहले शहर और पिनकोड लिखिए।","First write city and pincode."))
        else:
            st.session_state.doctor_location = {"country": "India", "city": city.strip(), "pincode": pincode.strip()}
            st.session_state.doctor_step = "done"
            st.session_state.messages.append({"role":"assistant","content":"DOCTORS_BOX","for_text": for_text, "loc": dict(st.session_state.doctor_location)})
            st.rerun()

def show_floating_banner():
    tips_hi = ["💡 दिन में 8 गिलास पानी पिएं", "💡 चोट को साफ पानी से धोएं", "💡 एलर्जी में खुजली मत करें", "💡 दवा समय पर लें", "💡 रोज 30 मिनट टहलें"]
    tips_en = ["💡 Drink 8 glasses of water daily", "💡 Wash wound with clean water", "💡 In allergy do not scratch", "💡 Take medicine on time", "💡 Walk 30 minutes daily"]
    tips = tips_hi if IS_HINDI else tips_en
    items = ""
    for i, tip in enumerate(tips):
        delay = i * 4
        items += f'<div class="tip" style="animation-delay:{delay}s;">{tip}</div>'
    st.markdown(f"""
    <style>
    .banner-wrap {{ position: fixed; bottom: 0; left: 0; right: 0; z-index: 9999; background: linear-gradient(90deg,#FFE4E6,#FEF3C7,#D1FAE5); height: 48px; overflow: hidden; border-top: 1px solid #FDE68A; }}
    .banner-wrap .tip {{ position: absolute; left: 0; right: 0; top: 0; height: 48px; display: flex; align-items: center; justify-content: center; color: #7C2D12 !important; font-weight: 600; font-size: 14px; padding: 0 10px; text-align: center; opacity: 0; animation: tipCycle 20s linear infinite; }}
    @keyframes tipCycle {{ 0% {{opacity: 0;}} 1% {{opacity: 1;}} 15% {{opacity: 1;}} 17% {{opacity: 0;}} 100% {{opacity: 0;}} }}
    </style>
    <div class="banner-wrap">{items}</div>
    """, unsafe_allow_html=True)

def ask_reply(user_text, placeholder):
    real_lang = detect_language(user_text)
    # Audio ke liye bhi same rule - agar boli hui baat health se related nahi hai to answer nahi
    if not is_health_related(user_text):
        msg = out_of_context_msg(real_lang)
        placeholder.markdown(msg)
        return msg
    instant = get_instant_answer(user_text, real_lang)
    placeholder.markdown(instant)
    return instant

def ask_reply_photo(photo_keyword, photo_desc, placeholder):
    # Photo ke liye language sidebar se, lekin out-of-context check description se
    real_lang = "Hindi" if IS_HINDI else "English"
    # Agar photo ka description hi health se related nahi hai - jaise car, dog, movie, khana etc - to answer MAT karo
    if photo_desc.strip() != "":
        if not is_health_related(photo_desc):
            msg = out_of_context_msg(real_lang)
            placeholder.markdown(msg)
            return msg
        # Agar description me OUT word hai to bhi answer mat karo
        if any(w in photo_desc.lower() for w in OUT_WORDS):
            msg = out_of_context_msg(real_lang)
            placeholder.markdown(msg)
            return msg
    else:
        # Agar user ne photo ka description kuch nahi likha, to photo_type se hi check karo - photo_type hamesha health wala hai isliye aage badho
        pass
    full_text = f"{photo_keyword} {photo_desc}".strip()
    # Final check - agar poora text hi health se related nahi hai to answer mat karo
    if not is_health_related(full_text):
        msg = out_of_context_msg(real_lang)
        placeholder.markdown(msg)
        return msg
    instant = get_instant_answer(full_text, real_lang)
    placeholder.markdown(instant)
    return instant

if menu in ["🏠 Home", "🏠 होम"]:
    st.markdown(f"""<div class="ai-header"><h1>🩺 Sehat Saathi ✨</h1><p>{T('आपका एआई हेल्थ असिस्टेंट - अपनी तकलीफ लिखें, तुरंत सलाह पाएं','Your AI Health Assistant - Write your symptom, get instant advice')}</p></div>""", unsafe_allow_html=True)
    st.write(T("नमस्ते, मैं यहाँ आपकी मदद करने के लिए हूँ! 👋","Hello, I am here to help you! 👋"))
    st.write(T("अपनी तकलीफ लिखें, बोलें या फोटो भेजें।","Write your problem, speak or send photo."))
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            if m.get("content") == "DOCTORS_BOX":
                show_doctor_detail_card(m.get("for_text",""), m.get("loc", st.session_state.doctor_location))
            elif m.get("type") == "image":
                st.image(m["image"], caption=T("📸 आपकी फोटो","📸 Your Photo"), use_container_width=True)
                st.markdown(f"**{T('आपने लिखा:','You wrote:')}** {m['content']}")
            else:
                st.markdown(m["content"])
    if st.session_state.doctor_step == "location":
        last_user = ""
        for mm in reversed(st.session_state.messages):
            if mm["role"]=="user":
                last_user=mm["content"]; break
        show_location_form(last_user)
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant" and not st.session_state.doctor_asked and st.session_state.doctor_step == "none":
        if st.session_state.messages[-1].get("content") != "DOCTORS_BOX":
            if "सिर्फ स्वास्थ्य" not in st.session_state.messages[-1]["content"] and "only help with health" not in st.session_state.messages[-1]["content"].lower():
                st.info(T("👨‍⚕️ क्या आप डॉक्टर से बात करना चाहेंगी?","👨‍⚕️ Would you like to see a doctor?"))
                c1, c2 = st.columns(2)
                with c1:
                    if st.button(T("✅ हाँ, डॉक्टर से बात करें","✅ Yes, See Doctor"), use_container_width=True, key="yes_doctor"):
                        st.session_state.doctor_asked = True
                        st.session_state.doctor_step = "location"
                        st.rerun()
                with c2:
                    if st.button(T("❌ नहीं, बस ऐसे ही","❌ No, Thanks"), use_container_width=True, key="no_doctor"):
                        st.session_state.doctor_asked = True
                        st.session_state.doctor_step = "none"
                        st.session_state.messages.append({"role": "assistant", "content": T("ठीक है, अपना ख्याल रखिए। तकलीफ बढ़े तो तुरंत 104 या 108 पर कॉल कीजिएगा।","Okay, take care. If problem increases, call 104 or 108 immediately.")})
                        st.rerun()
    st.markdown("---")
    st.write(f"**{T('✍️ अपनी तकलीफ लिखें','✍️ Write Your Symptom')}**")
    with st.form("chat_form", clear_on_submit=True):
        chat_text = st.text_input("Type...", label_visibility="collapsed", placeholder="", value="")
        submitted = st.form_submit_button(T("➤ भेजें","➤ Send"), use_container_width=True)
    if submitted and chat_text.strip() != "":
        st.session_state.messages.append({"role": "user", "content": chat_text})
        st.session_state.doctor_asked = False
        st.session_state.doctor_step = "none"
        with st.chat_message("user"):
            st.markdown(chat_text)
        with st.chat_message("assistant"):
            placeholder = st.empty()
            reply = ask_reply(chat_text, placeholder)
        st.session_state.messages.append({"role": "assistant", "content": reply, "show_doctors": False, "for_text": chat_text})
        st.rerun()
    if st.button(T("🧹 चैट साफ करें","🧹 Clear Chat"), use_container_width=True):
        st.session_state.messages = []
        st.session_state.doctor_asked = False
        st.session_state.doctor_step = "none"
        st.session_state.doctor_location = {}
        st.session_state["last_audio_id"] = ""
        st.session_state.photo_sent = False
        st.session_state.uploader_key += 1
        st.rerun()
    col_photo, col_audio = st.columns(2)
    with col_photo:
        st.write(T("📷 फोटो","📷 Photo"))
        uploaded_photo = st.file_uploader("Upload Photo", type=["jpg","jpeg","png"], label_visibility="collapsed", key=f"wa_cam_{st.session_state.uploader_key}")
    with col_audio:
        st.write(T("🎤 आवाज़","🎤 Voice"))
        audio_input = st.audio_input("Speak", label_visibility="collapsed", key="wa_mic")
    if uploaded_photo:
        st.image(uploaded_photo, width=200)
        st.write(T("📸 यह फोटो किस चीज़ की है?","📸 What is this photo of?"))
        photo_type = st.radio("Photo Type", T(["एलर्जी / दाने", "चोट / जख्म", "खुजली / दाने"], ["Allergy / Rash", "Injury / Wound", "Itching / Rash"]), label_visibility="collapsed", horizontal=True, key="photo_type")
        photo_desc = st.text_input(T("फोटो में क्या दिख रहा है?","What is visible in photo?"), value="", placeholder="", key="photo_desc")
        if st.button(T("📸 फोटो भेजें","📸 Send Photo"), use_container_width=True):
            if "चोट" in photo_type or "Injury" in photo_type: kw = "चोट जख्म" if IS_HINDI else "chot zakhm"
            elif "खुजली" in photo_type or "Itching" in photo_type: kw = "खुजली दाने" if IS_HINDI else "khujli rash"
            else: kw = "एलर्जी दाने" if IS_HINDI else "allergy daane"
            photo_text = f"{kw} {photo_desc}".strip()
            with st.chat_message("user"):
                st.image(uploaded_photo, caption=T("📸 आपकी फोटो","📸 Your Photo"), use_container_width=True)
                st.markdown(f"**{T('आपने लिखा:','You wrote:')}** {photo_text}")
            with st.chat_message("assistant"):
                placeholder = st.empty()
                reply = ask_reply_photo(kw, photo_desc, placeholder)
            st.session_state.messages.append({"role": "user", "content": photo_text, "type": "image", "image": uploaded_photo})
            st.session_state.messages.append({"role": "assistant", "content": reply, "show_doctors": False, "for_text": photo_text})
            st.session_state.doctor_asked = False
            st.session_state.doctor_step = "none"
            st.session_state.photo_sent = True
            st.session_state.uploader_key += 1
            st.rerun()
    if audio_input and st.session_state.get("last_audio_id") != str(audio_input):
        st.session_state["last_audio_id"] = str(audio_input)
        with st.spinner(T("सुन रहे हैं...","Listening...")):
            voice_text = speech_to_text(audio_input.read())
        if voice_text and not voice_text.startswith("ERROR:"):
            with st.chat_message("user"):
                st.markdown(f"🎤 {T('आपने बोला:','You said:')} {voice_text}")
            st.session_state.messages.append({"role": "user", "content": voice_text})
            st.session_state.doctor_asked = False
            st.session_state.doctor_step = "none"
            with st.chat_message("assistant"):
                placeholder = st.empty()
                reply = ask_reply(voice_text, placeholder)
            st.session_state.messages.append({"role": "assistant", "content": reply, "show_doctors": False, "for_text": voice_text})
            st.rerun()
        else:
            st.warning(T("आवाज़ समझ नहीं आई, दोबारा बोलिए।","Could not understand, please speak again."))
    show_floating_banner()

elif menu in ["💊 Medicine Info", "💊 दवाई की जानकारी"]:
    st.title(T("💊 दवाई की जानकारी","💊 Medicine Info"))
    st.write(T("दुनिया की कोई भी दवाई का नाम लिखें, उसके बारे में पूरी जानकारी मिलेगी।","Write name of any medicine in the world, you will get full info about it."))
    st.write(f"**{T('💊 दवाई का नाम लिखें','💊 Write Medicine Name')}**")
    med_input = st.text_input(T("दवाई का नाम...","Medicine name..."), value="", placeholder="", key="med_info_input")
    if st.button(T("🔍 दवाई की जानकारी देखें","🔍 See Medicine Info"), use_container_width=True):
        if med_input.strip() == "":
            st.warning(T("पहले दवाई का नाम लिखिए।","First write medicine name."))
        else:
            st.markdown(f"**{T('आपने लिखा:','You wrote:')}** {med_input}")
            st.markdown("---")
            lang_now = "Hindi" if IS_HINDI else "English"
            info = get_medicine_info(med_input, lang_now)
            st.markdown(f"""<div class="medicine-card">{info}</div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.write(T("**लोकप्रिय दवाइयां - किसी पर क्लिक करें:**","**Popular Medicines - Click any:**"))
    cols = st.columns(3)
    popular = ["Paracetamol", "Azithromycin", "Cetirizine", "Omeprazole", "Ibuprofen", "ORS"]
    for i, p in enumerate(popular):
        with cols[i % 3]:
            if st.button(p, key=f"pop_{p}"):
                lang_now = "Hindi" if IS_HINDI else "English"
                st.markdown(f"**{T('आपने लिखा:','You wrote:')}** {p}")
                st.markdown(get_medicine_info(p, lang_now))
    st.info(T("⚠️ ये जानकारी सिर्फ समझने के लिए है, डॉक्टर की जगह नहीं लेती। कोई भी दवाई लेने से पहले डॉक्टर से पूछें।","⚠️ This info is only for understanding, not a replacement for doctor. Ask doctor before taking any medicine."))
    show_floating_banner()

elif menu in ["💊 Medicine Reminder", "💊 दवाई रिमाइंडर"]:
    st.title(T("💊 दवाई रिमाइंडर","💊 Medicine Reminder"))
    st.write(T("दवाई का समय सेट कीजिए, समय होने पर ऐप याद दिलाएगा।","Set medicine time, app will remind you."))
    with st.form("reminder_form"):
        med_name = st.text_input(T("दवाई का नाम","Medicine Name"), value="", placeholder="")
        st.write(T("समय","Time"))
        c_h, c_m, c_ap = st.columns(3)
        with c_h: hour = st.selectbox(T("घंटा","Hour"), list(range(1, 13)), index=None, placeholder="")
        with c_m: minute = st.selectbox(T("मिनट","Minute"), [f"{i:02d}" for i in range(0, 60)], index=None, placeholder="")
        with c_ap: ampm = st.radio("AM / PM", ["AM", "PM"], horizontal=True)
        med_days = st.number_input(T("कितने दिन तक?","How many days?"), min_value=1, max_value=30, value=None, placeholder="")
        if st.form_submit_button(T("✅ रिमाइंडर सेट करें","✅ Set Reminder"), use_container_width=True):
            if med_name.strip() == "" or hour is None or minute is None or med_days is None:
                st.warning(T("पहले दवाई का नाम, समय और दिन लिखिए","First write medicine name, time and days"))
            else:
                hour_24 = hour % 12
                if ampm == "PM": hour_24 += 12
                if ampm == "AM" and hour == 12: hour_24 = 0
                time_str = f"{hour_24:02d}:{minute}"
                display_time = f"{hour}:{minute} {ampm}"
                st.session_state.reminders.append({"name": med_name.strip(), "time": time_str, "display": display_time, "days": med_days, "hour24": hour_24, "minute": minute})
                st.success(T(f"✅ रिमाइंडर सेट: {med_name.strip()} - {display_time} - {med_days} दिन", f"✅ Reminder set: {med_name.strip()} - {display_time} - {med_days} days"))
    st.markdown("---")
    st.write(T("📋 **आपके रिमाइंडर**","📋 **Your Reminders**"))
    now_str = datetime.datetime.now().strftime("%H:%M")
    for r in st.session_state.reminders:
        r_time_short = r["time"][:5]
        show_time = r.get("display", r["time"])
        if r_time_short == now_str:
            st.error(T(f"🔔 दवाई का समय हो गया! {r['name']} ले लीजिए! - {show_time}", f"🔔 TIME FOR MEDICINE! Take {r['name']} now! - {show_time}"))
        st.info(T(f"💊 {r['name']} - ⏰ {show_time} - 📅 {r['days']} दिन", f"💊 {r['name']} - ⏰ {show_time} - 📅 {r['days']} days"))
        today = datetime.date.today().strftime("%Y%m%d")
        hh = str(r.get("hour24", 9)).zfill(2)
        mm = str(r.get("minute", "00")).zfill(2)
        gcal_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={urllib.parse.quote(r['name'] + ' - Dawa Leni Hai')}&dates={today}T{hh}{mm}00/{today}T{hh}{mm}00&recur=RRULE:FREQ=DAILY;COUNT={r['days']}&details={urllib.parse.quote('Daily Medicine Reminder - ' + r['name'])}"
        st.link_button(T("📅 गूगल कैलेंडर में जोड़ें - रोज़ दोहराएं","📅 Add to Google Calendar - Daily Repeat"), gcal_url, use_container_width=True)
    if st.session_state.reminders:
        if st.button(T("🗑️ सारे रिमाइंडर हटाएं","🗑️ Delete All Reminders"), use_container_width=True):
            st.session_state.reminders = []
            st.rerun()
    else:
        st.write(T("अभी कोई रिमाइंडर नहीं है।","No reminders yet."))
    show_floating_banner()

elif menu in ["👨‍⚕️ Talk To Doctor", "👨‍⚕️ डॉक्टर से बात करें"]:
    st.title(T("👨‍⚕️ डॉक्टर से बात करें","👨‍⚕️ Talk To Doctor"))
    st.success(T("ये सब सरकारी डॉक्टर की सेवाएं हैं, 100% असली।","All these are Government doctor services, 100% Real."))
    st.write(T("पहले अपनी तकलीफ लिखें, फिर लोकेशन बताएं, डॉक्टर की पूरी जानकारी मिलेगी।","First write your problem, then tell location, you will get full doctor details."))
    talk_symptom = st.text_input(T("अपनी तकलीफ लिखें","Write Your Problem"), value="", placeholder="", key="talk_symptom")
    if talk_symptom.strip() != "":
        show_location_form(talk_symptom)
    st.markdown("---")
    st.markdown(f"### {T('📞 104 - हेल्थ हेल्पलाइन','📞 104 - Health Helpline')}")
    st.link_button(T("📞 104 पर कॉल करें","📞 Call 104"), "tel:104", use_container_width=True)
    st.markdown(f"### {T('🏥 नज़दीकी सरकारी अस्पताल','🏥 Nearest Government Hospital')}")
    st.write(T("- **सुबह:** 9 बजे से 1 बजे तक ओपीडी","- **Morning:** 9 AM to 1 PM OPD"))
    show_floating_banner()

elif menu in ["🚨 Emergency", "🚨 आपातकाल"]:
    st.title(T("🚨 आपातकाल - Emergency","🚨 Emergency"))
    st.error(T("अगर तकलीफ बहुत ज़्यादा है तो पहले CALL करें, ऐप का इंतज़ार मत करें!","If problem is very serious, CALL FIRST, do not wait for app!"))
    st.markdown(f"### {T('📞 आपातकालीन नंबर - पहले इन पर कॉल करें','📞 Emergency Numbers - Call These First')}")
    st.link_button(T("🚑 108 - एम्बुलेंस बुलाएं","🚑 108 - Call Ambulance"), "tel:108", use_container_width=True)
    st.link_button(T("🚓 112 - पुलिस / आपातकाल","🚓 112 - Police / Emergency"), "tel:112", use_container_width=True)
    st.link_button(T("🔥 101 - फायर ब्रिगेड","🔥 101 - Fire Brigade"), "tel:101", use_container_width=True)
    st.link_button(T("📞 104 - हेल्थ हेल्पलाइन","📞 104 - Health Helpline"), "tel:104", use_container_width=True)
    st.link_button(T("👧 1098 - चाइल्ड हेल्पलाइन","👧 1098 - Child Helpline"), "tel:1098", use_container_width=True)
    st.link_button(T("👩 181 - महिला हेल्पलाइन","👩 181 - Women Helpline"), "tel:181", use_container_width=True)
    st.markdown("---")
    st.markdown(f"### {T('🆘 अपनी इमरजेंसी लिखें / बोलें','🆘 Write / Speak Your Emergency')}")
    st.write(T("जैसे: हाथ कट गया, खून आ रहा है, सांस नहीं आ रही","Like: hand cut, bleeding, cannot breathe"))
    em_text = st.text_input(T("इमरजेंसी लिखें...","Write emergency..."), value="", placeholder="", key="em_text")
    em_audio = st.audio_input(T("इमरजेंसी बोलें","Speak Emergency"), key="em_mic")
    em_final = em_text
    if em_audio and st.session_state.get("last_em_audio") != str(em_audio):
        st.session_state["last_em_audio"] = str(em_audio)
        vt = speech_to_text(em_audio.read())
        if vt and not vt.startswith("ERROR:"):
            st.success(T(f"🗣️ आपने बोला: {vt}", f"🗣️ You said: {vt}"))
            em_final = vt
    if st.button(T("🚨 इमरजेंसी स्टेप्स देखें","🚨 See Emergency Steps"), use_container_width=True):
        e = (em_final or "").lower()
        if e.strip()=="":
            st.warning(T("पहले अपनी इमरजेंसी लिखें या बोलें।","First write or speak your emergency."))
        elif not is_health_related(em_final):
            # Emergency me bhi out-of-context ka answer nahi karna
            st.warning(out_of_context_msg(detect_language(em_final)))
        else:
            lang_now = detect_language(em_final)
            lang_rule = "Answer ONLY in proper Hindi in Devanagari script. No Hinglish." if lang_now=="Hindi" else "Answer ONLY in proper English. No Hindi or Hinglish."
            ans = ask_ai(f"Emergency hai: {em_final}. Language: {lang_now}. {lang_rule} Usi language me 4-5 short steps batao, ambulance aane tak kya karna hai. Pehli line me 108 par call karne ko bolo. Short, saaf, ghabraye nahi aise.")
            if ans == "ERROR_KEY_MISSING":
                st.error(T("पहले 108 पर कॉल करें!","Call 108 first!"))
            else:
                st.error(ans)
    st.markdown("---")
    st.markdown(f"### {T('🆘 इमरजेंसी टिप्स','🆘 Emergency Tips')}")
    st.write(T("- **चोट:** साफ कपड़े से दबाएं, हल्दी / मिट्टी मत लगाएं","- **Injury:** Press with clean cloth, do not apply haldi / mud"))
    st.write(T("- **सांस:** सीधा बैठाएं, कपड़े ढीले करें","- **Breathing:** Sit straight, loosen clothes"))
    st.write(T("- **बुखार:** ठंडी पट्टी, थोड़ा-थोड़ा पानी","- **Fever:** Cold cloth, water in small sips"))
    st.write(T("- **बेहोश:** पानी मत पिलाएं, एक तरफ लिटाएं, 108 पर कॉल करें","- **Unconscious:** Do not give water, lie on side, call 108"))
    show_floating_banner()

elif menu in ["🏥 Hospital Finder", "🏥 अस्पताल खोजें"]:
    st.title(T("🏥 अस्पताल खोजें","🏥 Hospital Finder"))
    st.write(T("अपना शहर और पिनकोड लिखें, आपके पास के अस्पतालों की लिस्ट आ जाएगी।","Write your city and pincode, list of hospitals near you will appear."))
    st.write(f"**{T('📍 अपनी लोकेशन डालें','📍 Enter Your Location')}**")
    h_city = st.text_input(T("शहर का नाम","City Name"), value="", placeholder="", key="hosp_city")
    h_pin = st.text_input(T("पिनकोड","Pincode"), value="", placeholder="", key="hosp_pin")
    if st.button(T("🏥 अस्पताल खोजें","🏥 Find Hospitals"), use_container_width=True):
        if h_city.strip() == "" or h_pin.strip() == "":
            st.warning(T("पहले शहर और पिनकोड लिखिए।","First write city and pincode."))
        else:
            st.success(T(f"✅ {h_city} - {h_pin} के पास के अस्पताल:","✅ Hospitals near " + h_city + " - " + h_pin + ":"))
            hospitals = get_hospitals_for(h_city, h_pin)
            for h in hospitals:
                st.markdown(f"""<div class="hospital-card"><b>🏥 {h['name']}</b><br><span>{h['type']}</span><br><span>📍 {h['addr']}</span><br><span>📞 {h['phone']}</span></div>""", unsafe_allow_html=True)
            maps_url = f"https://www.google.com/maps/search/{urllib.parse.quote('hospital near ' + h_city + ' ' + h_pin + ' India')}"
            st.link_button(T("📍 गूगल मैप्स पर सारे अस्पताल देखें","📍 See All Hospitals On Google Maps"), maps_url, use_container_width=True)
            st.link_button(T("🚑 108 - एम्बुलेंस बुलाएं","🚑 108 - Call Ambulance"), "tel:108", use_container_width=True)
            st.link_button(T("📞 104 - हेल्थ हेल्पलाइन","📞 104 - Health Helpline"), "tel:104", use_container_width=True)
    show_floating_banner()

elif menu in ["💡 Health Tips", "💡 स्वास्थ्य टिप्स"]:
    st.title(T("💡 स्वास्थ्य टिप्स - रोज़ का रूटीन","💡 Health Tips - Daily Routine"))
    st.write(T("ये छोटी-छोटी आदतें आपको बड़े रोग से बचा सकती हैं।","These small habits can save you from big diseases."))
    st.markdown(f"### {T('🌅 1. सुबह उठते ही','🌅 1. Morning')}")
    st.write(T("- **गुनगुना पानी:** सुबह उठते ही 1-2 गिलास गुनगुना पानी पिएं","- **Warm Water:** Drink 1-2 glasses of warm water after waking up"))
    st.write(T("- **धूप:** सुबह 15 मिनट धूप में बैठें, विटामिन डी मिलता है","- **Sunlight:** Sit in sunlight for 15 minutes, you get Vitamin D"))
    st.write(T("- **फोन मत देखें:** उठते ही फोन मत देखें, 30 मिनट बाद देखें","- **No Phone:** Do not see phone just after waking up"))
    st.markdown(f"### {T('🚶 2. टहल और व्यायाम','🚶 2. Walk And Exercise')}")
    st.write(T("- **रोज़ 30 मिनट टहल:** बीपी, शुगर और वज़न नियंत्रण में रहता है","- **30 Min Walk Daily:** Controls BP, sugar and weight"))
    st.write(T("- **सीढ़ी:** लिफ्ट की जगह सीढ़ी इस्तेमाल करें","- **Stairs:** Use stairs instead of lift"))
    st.markdown(f"### {T('🍲 3. खाना-पीना','🍲 3. Food And Water')}")
    st.write(T("- **हरी सब्जियां:** रोज़ एक समय हरी सब्जी खाएं","- **Green Vegetables:** Eat green vegetables once daily"))
    st.write(T("- **पानी:** दिन में 8 गिलास पानी पिएं","- **Water:** Drink 8 glasses of water daily"))
    st.write(T("- **नमक-कम:** खाने में नमक और तेल कम रखें","- **Less Salt-Oil:** Keep salt and oil less in food"))
    st.markdown(f"### {T('😴 4. नींद','😴 4. Sleep')}")
    st.write(T("- **7-8 घंटे:** रोज़ 7-8 घंटे की नींद लें","- **7-8 Hours:** Take 7-8 hours sleep daily"))
    st.write(T("- **मोबाइल दूर:** सोने से 30 मिनट पहले मोबाइल बंद कर दें","- **Mobile Away:** Switch off mobile 30 minutes before sleeping"))
    st.markdown(f"### {T('🧼 5. साफ-सफाई','🧼 5. Cleanliness')}")
    st.write(T("- **हाथ धोएं:** खाना खाने से पहले हाथ साबुन से धोएं","- **Wash Hands:** Wash hands with soap before eating"))
    st.write(T("- **दांत:** दिन में 2 बार ब्रश करें","- **Teeth:** Brush 2 times a day"))
    st.markdown(f"### {T('👶 7. बच्चों के लिए','👶 7. For Children')}")
    st.write(T("- **टीका:** बच्चों के सारे टीके समय पर लगवाएं, पीएचसी में फ्री लगते हैं","- **Vaccination:** Get all vaccines on time, FREE in PHC"))
    st.write(T("- **दूध:** रोज़ 1 गिलास दूध पिलाएं","- **Milk:** Give 1 glass milk daily"))
    st.markdown(f"### {T('👵 8. बुजुर्गों के लिए','👵 8. For Elderly')}")
    st.write(T("- **बीपी-शुगर जांच:** महीने में 1 बार बीपी और शुगर जांच करवाएं, पीएचसी में फ्री होता है","- **BP-Sugar Check:** Check BP and sugar once a month, FREE in PHC"))
    st.write(T("- **दवाई समय पर:** दवाई का समय कभी मत छोड़ें","- **Medicine On Time:** Never miss medicine time"))
    show_floating_banner()

elif menu in ["⚖️ BMI Calculator", "⚖️ बीएमआई कैलकुलेटर"]:
    st.title(T("⚖️ बीएमआई कैलकुलेटर","⚖️ BMI Calculator"))
    weight = st.number_input(T("वज़न (kg)","Weight (kg)"), min_value=10.0, max_value=200.0, value=None, placeholder="")
    height = st.number_input(T("ऊंचाई (cm)","Height (cm)"), min_value=100.0, max_value=220.0, value=None, placeholder="")
    if st.button(T("हिसाब लगाएं","Calculate")):
        if weight is None or height is None:
            st.warning(T("पहले वज़न और ऊंचाई लिखिए","First write weight and height"))
        else:
            h_m = height / 100
            bmi = weight / (h_m * h_m)
            st.success(f"आपका बीएमआई: {bmi:.1f}" if IS_HINDI else f"Your BMI: {bmi:.1f}")
            if bmi < 18.5: st.write(T("कम वज़न - स्वस्थ खाना खाएं","Underweight - Eat healthy food"))
            elif bmi < 25: st.write(T("सामान्य - बहुत बढ़िया!","Normal - Good! Keep it up"))
            elif bmi < 30: st.write(T("ज्यादा वज़न - रोज़ टहलें","Overweight - Walk daily"))
            else: st.write(T("मोटापा - डॉक्टर से बात करें","Obese - Please consult doctor"))
    show_floating_banner()

elif menu in ["🏛️ Government Schemes", "🏛️ सरकारी योजनाएं"]:
    st.title(T("🏛️ सरकारी योजनाएं - फ्री का फायदा उठाएं","🏛️ Government Schemes - Take FREE Benefit"))
    st.success(T("ये सब सरकारी योजनाएं हैं, 100% असली और फ्री। किसी को पैसे मत दें।","All these are Government schemes, 100% Real and FREE. Do not pay money to anyone."))
    st.write(T("कुल 12 योजनाएं - हर एक का बटन असली सरकारी साइट पर जाएगा।","Total 12 Schemes - Every button will go to real Govt site."))
    st.markdown(f"""<div class="scheme-card"><b>1. 🩺 {T('आयुष्मान भारत - पीएमजेएवाई','Ayushman Bharat - PMJAY')}</b><br><span>{T('क्या मिलता है:','Benefit:')} {T('5 लाख तक का फ्री इलाज, हर साल, पूरे परिवार के लिए','FREE treatment up to 5 Lakh, every year, for whole family')}</span><br><span>{T('क्या चाहिए:','Need:')} {T('आधार कार्ड + राशन कार्ड','Aadhaar Card + Ration Card')}</span></div>""", unsafe_allow_html=True)
    st.link_button(T("✅ आयुष्मान कार्ड बनाएं / चेक करें - Direct Link","✅ Make / Check Ayushman Card - Direct Link"), "https://beneficiary.nha.gov.in", use_container_width=True)
    st.markdown(f"""<div class="scheme-card"><b>2. 💊 {T('जन औषधि - सस्ती दवाई','Jan Aushadhi - Cheap Medicines')}</b><br><span>{T('क्या मिलता है:','Benefit:')} {T('दवाई 50% से 90% तक सस्ती','Medicines 50% to 90% cheaper')}</span></div>""", unsafe_allow_html=True)
    st.link_button(T("💊 नज़दीकी जन औषधि केंद्र ढूंढें","💊 Find Nearest Jan Aushadhi Kendra"), "https://janaushadhi.gov.in", use_container_width=True)
    st.markdown(f"""<div class="scheme-card"><b>3. 🩺 {T('ई-संजीवनी - फ्री ऑनलाइन डॉक्टर','eSanjeevani - FREE Online Doctor')}</b><br><span>{T('क्या मिलता है:','Benefit:')} {T('वीडियो कॉल पर सरकारी डॉक्टर से फ्री बात, सुबह 10 से शाम 4','FREE video call with Govt doctor, 10 AM to 4 PM')}</span></div>""", unsafe_allow_html=True)
    st.link_button(T("🩺 ई-संजीवनी पर फ्री डॉक्टर से बात करें","🩺 Talk To FREE Doctor On eSanjeevani"), "https://esanjeevani.mohfw.gov.in/patient/", use_container_width=True)
    st.markdown(f"""<div class="scheme-card"><b>4. 🤰 {T('पीएम सुरक्षित मातृत्व - गर्भवती महिला','PM Surakshit Matritva - Pregnant Women')}</b><br><span>{T('क्या मिलता है:','Benefit:')} {T('गर्भवती महिला की फ्री जांच, फ्री दवाई, फ्री अल्ट्रासाउंड','FREE checkup, FREE medicine, FREE ultrasound for pregnant women')}</span></div>""", unsafe_allow_html=True)
    st.link_button(T("🤰 पीएम सुरक्षित मातृत्व की जानकारी देखें","🤰 See PM Surakshit Matritva Details"), "https://nhm.gov.in", use_container_width=True)
    st.markdown(f"""<div class="scheme-card"><b>5. 👶 {T('मिशन इंद्रधनुष - बच्चों के टीके','Mission Indradhanush - Children Vaccines')}</b><br><span>{T('क्या मिलता है:','Benefit:')} {T('बच्चों के सारे टीके बिल्कुल फ्री','All vaccines of children totally FREE')}</span></div>""", unsafe_allow_html=True)
    st.link_button(T("👶 टीकाकरण की जानकारी देखें","👶 See Vaccination Details"), "https://www.mohfw.gov.in", use_container_width=True)
    st.markdown(f"""<div class="scheme-card"><b>6. 🤱 {T('जननी सुरक्षा योजना - डिलीवरी के लिए पैसे','Janani Suraksha Yojana - Money For Delivery')}</b><br><span>{T('क्या मिलता है:','Benefit:')} {T('सरकारी अस्पताल में डिलीवरी पर माँ को ₹1400 तक की मदद + फ्री डिलीवरी','Up to Rs. 1400 help + FREE delivery in Govt hospital')}</span></div>""", unsafe_allow_html=True)
    st.link_button(T("🤱 जननी सुरक्षा योजना देखें","🤱 See Janani Suraksha Yojana"), "https://nhm.gov.in", use_container_width=True)
    st.markdown(f"""<div class="scheme-card"><b>7. 👩‍🍼 {T('जननी शिशु सुरक्षा - माँ + बच्चे का फ्री इलाज','Janani Shishu Suraksha - FREE Treatment For Mother + Child')}</b><br><span>{T('क्या मिलता है:','Benefit:')} {T('डिलीवरी, सी-सेक्शन, दवाई, खून की जांच, बच्चे का इलाज - सब फ्री','Delivery, C-section, medicine, blood test, child treatment - All FREE')}</span></div>""", unsafe_allow_html=True)
    st.link_button(T("👩‍🍼 जननी शिशु सुरक्षा देखें","👩‍🍼 See Janani Shishu Suraksha"), "https://nhm.gov.in", use_container_width=True)
    st.markdown(f"""<div class="scheme-card"><b>8. 👵 {T('पीएम वय वंदना - बुजुर्गों के लिए','PM Vaya Vandana - For Elderly')}</b><br><span>{T('क्या मिलता है:','Benefit:')} {T('60 साल से ऊपर के बुजुर्गों को हर महीने पेंशन जैसा पैसा','Elderly above 60 years get monthly pension-like money')}</span></div>""", unsafe_allow_html=True)
    st.link_button(T("👵 पीएम वय वंदना देखें","👵 See PM Vaya Vandana"), "https://www.licindia.in", use_container_width=True)
    st.markdown(f"""<div class="scheme-card"><b>9. 🦟 {T('राष्ट्रीय स्वास्थ्य मिशन - फ्री जांच','National Health Mission - FREE Checkup')}</b><br><span>{T('क्या मिलता है:','Benefit:')} {T('पीएचसी में बीपी, शुगर, बुखार, मलेरिया की जांच बिल्कुल फ्री','BP, Sugar, Fever, Malaria checkup totally FREE in PHC')}</span></div>""", unsafe_allow_html=True)
    st.link_button(T("🦟 राष्ट्रीय स्वास्थ्य मिशन देखें","🦟 See National Health Mission"), "https://nhm.gov.in", use_container_width=True)
    st.markdown(f"""<div class="scheme-card"><b>10. 🪪 {T('आभा कार्ड - डिजिटल हेल्थ आईडी','ABHA Card - Digital Health ID')}</b><br><span>{T('क्या मिलता है:','Benefit:')} {T('पूरे इंडिया में किसी भी अस्पताल में आपकी सारी रिपोर्ट एक ही कार्ड से दिख जाएगी','In any hospital in India, all your reports will show with one card')}</span></div>""", unsafe_allow_html=True)
    st.link_button(T("🪪 आभा कार्ड बनाएं - Direct Link","🪪 Make ABHA Card - Direct Link"), "https://abha.abdm.gov.in", use_container_width=True)
    st.markdown(f"""<div class="scheme-card"><b>11. 🧠 {T('टेली-मानस - फ्री मानसिक स्वास्थ्य हेल्पलाइन','Tele-MANAS - FREE Mental Health Helpline')}</b><br><span>{T('क्या मिलता है:','Benefit:')} {T('घबराहट, उदासी, स्ट्रेस हो तो फ्री में काउंसलर से बात करें','If anxiety, sadness, stress, talk to counsellor FREE')}</span><br><span><b>{T('नंबर:','Number:')}</b> 14416 - {T('24 घंटे फ्री','24 Hours FREE')}</span></div>""", unsafe_allow_html=True)
    st.link_button(T("📞 14416 पर कॉल करें - टेली-मानस","📞 Call 14416 - Tele-MANAS"), "tel:14416", use_container_width=True)
    st.markdown(f"""<div class="scheme-card"><b>12. 🫁 {T('टीबी मुक्त भारत / निक्षय - टीबी का फ्री इलाज + पैसे','TB Mukt Bharat / Nikshay - FREE TB Treatment + Money')}</b><br><span>{T('क्या मिलता है:','Benefit:')} {T('टीबी की जांच, दवाई बिल्कुल फ्री + हर महीने ₹500 पोषण के लिए','TB test, medicine totally FREE + Rs. 500 per month for nutrition')}</span></div>""", unsafe_allow_html=True)
    st.link_button(T("🫁 निक्षय पोर्टल देखें","🫁 See Nikshay Portal"), "https://nikshay.in", use_container_width=True)
    show_floating_banner()

elif menu in ["ℹ️ About App", "ℹ️ ऐप के बारे में"]:
    st.title(T("ℹ️ ऐप के बारे में - सेहत साथी","ℹ️ About App - Sehat Saathi"))
    st.write(T("सेहत साथी **सिर्फ इंडिया के लिए** बनाया गया है - बच्चों से लेकर बुजुर्गों तक, गांव हो या शहर, सभी लोग इसका इस्तेमाल कर सकते हैं।","Sehat Saathi is made **only for India** - from children to elderly, village or city, anyone can use it."))
    st.markdown("---")
    st.markdown(f"### {T('🩺 यह ऐप क्या है?','🩺 What Is This App?')}")
    st.write(T("सेहत साथी एक हेल्थ हेल्पर ऐप है। जब आपको हल्की तकलीफ होती है - जैसे सिर दर्द, बुखार, सर्दी, पेट दर्द - और आपको समझ नहीं आता कि क्या करें, तो यह ऐप तुरंत आपको समझाता है कि यह किस वजह से हो सकता है, कब खतरा है और अभी क्या करना चाहिए।","Sehat Saathi is a health helper app. When you have a small problem - like headache, fever, cold, stomach pain - this app tells you why it can happen, when it is dangerous, and what you should do now."))
    st.write(T("यह ऐप डॉक्टर की जगह नहीं लेता, यह बस पहली मदद करता है।","This app does not replace a doctor, it only gives first help."))
    st.markdown("---")
    st.markdown(f"### {T('✨ फीचर्स','✨ Features')}")
    st.write(T("- **💬 चैट:** अपनी तकलीफ लिखकर भेजें","- **💬 Chat:** Write your problem"))
    st.write(T("- **🎤 बोलकर बताएं:** माइक दबाकर बोल दीजिए","- **🎤 Speak:** Press mic and speak"))
    st.write(T("- **📷 फोटो भेजें:** दाने, चोट या रैश की फोटो भेज दीजिए","- **📷 Send Photo:** Send photo of rash, injury"))
    st.write(T("- **💊 दवाई की जानकारी:** किसी भी दवाई के बारे में जानें","- **💊 Medicine Info:** Know about any medicine"))
    st.write(T("- **💊 दवाई रिमाइंडर:** दवाई का समय सेट कीजिए","- **💊 Medicine Reminder:** Set medicine time"))
    st.write(T("- **👨‍⚕️ डॉक्टर से बात करें:** सरकारी डॉक्टर, ई-संजीवनी और 104 हेल्पलाइन","- **👨‍⚕️ Talk To Doctor:** Govt doctor, eSanjeevani and 104 helpline"))
    st.write(T("- **🚨 आपातकाल:** इमरजेंसी में क्या करना है, किस नंबर पर कॉल करना है","- **🚨 Emergency:** What to do in emergency, which number to call"))
    st.write(T("- **🏥 अस्पताल खोजें:** शहर + पिनकोड से पास के अस्पताल","- **🏥 Hospital Finder:** Nearby hospitals by city + pincode"))
    st.write(T("- **💡 स्वास्थ्य टिप्स:** रोज़ का रूटीन, खाना-पीना, नींद, टहल","- **💡 Health Tips:** Daily routine, food, sleep, walk"))
    st.write(T("- **⚖️ बीएमआई कैलकुलेटर:** अपना वज़न सही है या नहीं","- **⚖️ BMI Calculator:** Check if your weight is correct"))
    st.write(T("- **🏛️ सरकारी योजनाएं:** आयुष्मान, जन औषधि जैसी 12 योजनाओं की जानकारी फ्री में","- **🏛️ Government Schemes:** 12 Schemes like Ayushman, Jan Aushadhi info FREE"))
    st.markdown("---")
    st.info(T("⚠️ **ज़रूरी बात:** यह ऐप सिर्फ जानकारी और पहली मदद के लिए है। यह डॉक्टर की जगह नहीं ले सकता। अगर तकलीफ ज़्यादा है, तो तुरंत डॉक्टर को दिखाएं या 108 पर कॉल करें।","⚠️ **Important:** This app is only for information and first help. It cannot replace a doctor. If problem is more, see doctor immediately or call 108."))
    show_floating_banner()
