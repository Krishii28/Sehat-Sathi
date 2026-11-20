import streamlit as st
import datetime
import re
import urllib.parse
st.set_page_config(page_title="Sehat Saathi - India", page_icon="🩺", layout="centered")

# ---------- LIGHT OMBRE - SITE JAISA, AESTHETIC, HALKA ----------
st.markdown("""
<style>
/* BACKGROUND - BAHUT HALKA OMBRE - PEACH SE LAVENDER SE SKY */
.stApp { background: linear-gradient(180deg, #FFF7ED 0%, #FEF3F2 35%, #EEF2FF 70%, #F0FDF4 100%) !important; }
.block-container { background: transparent !important; max-width: 1100px !important; padding: 1rem 2rem 100px 2rem !important; }
h1, h2, h3, p, label, .stMarkdown, .stWrite, span, div { color: #334155 !important; }
/* SIDEBAR - WHITE, SITE JAISA, PURPLE NAHI */
section[data-testid="stSidebar"] { background: #FFFFFF !important; border-right: 1px solid #E2E8F0; }
section[data-testid="stSidebar"] * { color: #334155 !important; font-weight: 500 !important; }
/* BOXES - WHITE, HALKA BORDER, EMPTY LOOK */
.stTextInput input, .stSelectbox div[data-baseweb="select"] div, .stNumberInput input, .stTextArea textarea {
    background: #FFFFFF !important; color: #334155 !important; border: 1.5px solid #E2E8F0 !important; border-radius: 12px !important; min-height: 50px !important; font-size: 16px !important;
}
.stTextInput input::placeholder { color: #94A3B8 !important; }
/* BUTTON - HALKA OMBRE, PAR TEXT WHITE, SAAF DIKHEGA */
.stButton button, .stLinkButton a {
    background: linear-gradient(90deg, #6366F1, #8B5CF6) !important; color: #FFFFFF !important; border: none !important; border-radius: 12px !important; font-weight: 700 !important; min-height: 50px !important; font-size: 16px !important; box-shadow: 0 2px 8px rgba(99,102,241,0.20) !important;
}
.stButton button *, .stLinkButton a * { color: #FFFFFF !important; font-weight: 700 !important; }
div[data-testid="stChatMessage"] { background: #FFFFFF !important; border-radius: 16px !important; border: 1px solid #E2E8F0 !important; box-shadow: 0 1px 6px rgba(0,0,0,0.04) !important; }
div[data-testid="stChatMessage"] * { color: #334155 !important; }
/* HEADER - HALKA OMBRE, SITE JAISA */
.ai-header { background: linear-gradient(90deg, #EEF2FF, #FDF2F8, #FFF7ED); padding: 20px; border-radius: 20px; text-align: center; margin-bottom: 14px; border: 1px solid #E0E7FF; }
.ai-header h1 { font-size: 28px; margin: 0; color: #4338CA !important; }
.ai-header p { margin: 6px 0 0 0; color: #64748B !important; font-size: 14px; font-weight: 500; }
/* CARDS - WHITE, HALKA SHADOW */
.doctor-card { background: #FFFFFF; border: 1px solid #E0E7FF; border-radius: 16px; padding: 16px; margin: 12px 0; box-shadow: 0 2px 10px rgba(99,102,241,0.08); }
.doctor-card b, .doctor-card span, .doctor-card p { color: #334155 !important; }
.online-card { background: #FFFFFF; border: 1px solid #FCE7F3; border-radius: 16px; padding: 16px; margin: 12px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.04); }
.online-card b, .online-card span { color: #334155 !important; }
.info-box { background: #FFFBEB; border-radius: 14px; padding: 14px; border: 1px solid #FDE68A; }
.info-box * { color: #334155 !important; }
@media (min-width: 1024px) { .block-container { max-width: 1100px !important; padding: 1.5rem 2.5rem 100px 2.5rem !important; } }
@media (min-width: 769px) and (max-width: 1023px) { .block-container { max-width: 92% !important; padding: 1rem 1.5rem 100px 1.5rem !important; } }
@media (max-width: 768px) {
    .block-container { max-width: 100% !important; padding: 10px 12px 100px 12px !important; }
    .ai-header h1 { font-size: 24px !important; }
    .stButton button { min-height: 52px !important; font-size: 17px !important; }
}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "doctor_asked" not in st.session_state:
    st.session_state.doctor_asked = False
if "doctor_step" not in st.session_state:
    st.session_state.doctor_step = "none"
if "doctor_location" not in st.session_state:
    st.session_state.doctor_location = {}
if "reminders" not in st.session_state:
    st.session_state.reminders = []
if "last_audio_id" not in st.session_state:
    st.session_state["last_audio_id"] = ""
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "photo_sent" not in st.session_state:
    st.session_state.photo_sent = False

st.sidebar.write("Language - Menu Ki Bhasha")
lang = st.sidebar.radio("Choose Language", ["English", "Hindi"], label_visibility="collapsed")
IS_HINDI = (lang == "Hindi")
if IS_HINDI:
    menu = st.sidebar.radio("मेनू", ["🏠 होम", "💊 दवाई रिमाइंडर", "👨‍⚕️ डॉक्टर से बात करें", "🚨 आपातकाल", "💡 स्वास्थ्य टिप्स", "⚖️ बीएमआई कैलकुलेटर", "🏛️ सरकारी योजनाएं", "ℹ️ ऐप के बारे में"])
else:
    menu = st.sidebar.radio("Menu", ["🏠 Home", "💊 Medicine Reminder", "👨‍⚕️ Talk To Doctor", "🚨 Emergency", "💡 Health Tips", "⚖️ BMI Calculator", "🏛️ Government Schemes", "ℹ️ About App"])

def T(hi, en):
    return hi if IS_HINDI else en

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

HEALTH_WORDS = ["daane","rash","chot","zakhm","allergy","khujli","itching","bukhar","fever","dard","pain","dawa","medicine","wound","injury","skin","khaansi","cough","cold","sardi","pet","stomach","sir","head","haath","hand","pair","leg","blood","khoon","burn","jal","soojan","swelling","ulti","vomit","dast","kamzori","weak","neend","sleep","saans","breath","chest","seene","gala","throat","kaan","ear","daant","tooth","aankh","eye","ghutna","knee","kamar","back","badan","body","chakkar","dizzy","gas","acidity","kabz","photo","doctor","hospital","bimar","beemar","tabiyat","dawai","diabetes","sugar","bp","thyroid","asthma","dama","anxiety","depression","stress","period","mahwari","pregnancy","garbh","piles","bawasir","stone","pathri","jaundice","piliya","malaria","dengue","typhoid","tb","cancer","hiv","pneumonia","corona","sinus","tonsil","pimple","muhase","dandruff","baal","fungal","eczema","psoriasis","vitiligo","ulcer","appendix","keede","gathiya","arthritis","sciatica","moch","freeze","mirgi","daura","yaadash","ghabrahat","udaasi","peshaab","uti","liver","hepatitis","cholesterol","dil","dhadkan","naak","tonsil","motiyabind","chashma","aids","tumor","kidney","paralysis","lakwa","vitamin","infection","bacteria","virus","haddi","nas","dimaag","brain","heart","lung","fefe","दाने","चोट","खुजली","बुखार","दर्द","सांस","सीने","पेट","सिर","कमर","गला","कान","दांत","आंख","पैर","हाथ","घुटना","चक्कर","उल्टी","कमजोरी","नींद","शुगर","मधुमेह","थायराइड","दमा","माहवारी","गर्भ","बवासीर","पथरी","पीलिया","मलेरिया","डेंगू","टाइफाइड","टीबी","कैंसर","निमोनिया","साइनस","मुहासे","बाल","गठिया","मिर्गी","घबराहट","उदासी","पेशाब","लीवर","कोलेस्ट्रॉल","दिल","नाक","मोतियाबिंद","लकवा","दिमाग","हड्डी"]
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
        return "मैं सिर्फ स्वास्थ्य, चोट और एलर्जी से जुड़ी मदद कर सकती हूँ। अपनी स्वास्थ्य समस्या बताइए - जैसे सिर दर्द, बुखार, दाने, चोट, खुजली, शुगर, बीपी, अस्थमा।"
    else:
        return "I can only help with health, injury and allergy related problems. Please tell your health problem - like headache, fever, rash, injury, itching, sugar, BP, asthma."
def detect_language(user_text):
    t = user_text.lower()
    if re.search(r'[\u0900-\u097F]', user_text):
        return "Hindi"
    hindi_words = ["mere", "mera", "mujhe", "dard", "hai", "sar", "sir", "kamar", "pet", "badan", "bukhar", "sardi", "khansi", "khujli", "daane", "gala", "kaan", "daant", "aankh", "pair", "haath", "ghutna", "chakkar", "ulti", "dast", "kamzori", "neend", "chot", "seene", "saans"]
    for w in hindi_words:
        if w in t:
            return "Hindi"
    return "Hindi" if IS_HINDI else "English"

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

DOCTOR_INFO = {
    "fever": {"spec_hi":"सामान्य चिकित्सक","spec_en":"General Physician","work_hi":"बुखार, सर्दी, बदन दर्द जैसी आम बीमारियों का इलाज करते हैं।","work_en":"Treats common problems like fever, cold and body pain.","when_hi":"बुखार 102 से ऊपर हो, 3 दिन से ज्यादा रहे, तो तुरंत दिखाएं।","when_en":"If fever is above 102 or stays more than 3 days, see immediately.","fees_hi":"₹200 - ₹500","fees_en":"Rs. 200 - Rs. 500"},
    "back": {"spec_hi":"हड्डी रोग विशेषज्ञ","spec_en":"Orthopedic Doctor","work_hi":"कमर, घुटना, हाथ-पैर और हड्डी के दर्द का इलाज करते हैं।","work_en":"Treats back, knee, joint and bone pain.","when_hi":"दर्द पैर तक जा रहा हो या चलने में दिक्कत हो, तो तुरंत दिखाएं।","when_en":"If pain goes to leg or you have difficulty walking, see immediately.","fees_hi":"₹300 - ₹600","fees_en":"Rs. 300 - Rs. 600"},
    "skin": {"spec_hi":"त्वचा रोग विशेषज्ञ","spec_en":"Dermatologist","work_hi":"दाने, खुजली, एलर्जी, पिंपल, फंगल और त्वचा की समस्या का इलाज करते हैं।","work_en":"Treats rash, itching, allergy, pimple, fungal and skin problems.","when_hi":"दानों से मवाद आए या पूरा शरीर लाल हो जाए, तो तुरंत दिखाएं।","when_en":"If pus comes from rash or full body becomes red, see immediately.","fees_hi":"₹300 - ₹600","fees_en":"Rs. 300 - Rs. 600"},
    "stomach": {"spec_hi":"पेट रोग विशेषज्ञ","spec_en":"Gastroenterologist","work_hi":"पेट दर्द, गैस, एसिडिटी, उल्टी-दस्त का इलाज करते हैं।","work_en":"Treats stomach pain, gas, acidity, vomiting and loose motion.","when_hi":"पेट में बहुत तेज दर्द हो या पॉटी में खून आए, तो तुरंत दिखाएं।","when_en":"If stomach pain is very severe or blood in stool, see immediately.","fees_hi":"₹400 - ₹700","fees_en":"Rs. 400 - Rs. 700"},
    "head": {"spec_hi":"न्यूरोलॉजिस्ट","spec_en":"Neurologist","work_hi":"सिर दर्द, माइग्रेन, चक्कर की समस्या का इलाज करते हैं।","work_en":"Treats headache, migraine and dizziness.","when_hi":"अचानक बहुत तेज सिर दर्द हो या उल्टी के साथ दर्द हो, तो तुरंत दिखाएं।","when_en":"If sudden very severe headache with vomiting, see immediately.","fees_hi":"₹500 - ₹800","fees_en":"Rs. 500 - Rs. 800"},
    "chest": {"spec_hi":"हृदय / फेफड़े रोग विशेषज्ञ","spec_en":"Cardiologist / Pulmonologist","work_hi":"सीने में दर्द, सांस, अस्थमा की तकलीफ का इलाज करते हैं।","work_en":"Treats chest pain, breathing and asthma problems.","when_hi":"सीने में तेज दर्द + पसीना आए, तो तुरंत 108 पर कॉल करें।","when_en":"If severe chest pain with sweating, call emergency immediately.","fees_hi":"₹500 - ₹800","fees_en":"Rs. 500 - Rs. 800"},
    "tooth": {"spec_hi":"दांत के डॉक्टर","spec_en":"Dentist","work_hi":"दांत दर्द, कीड़ा, मसूड़े की सूजन का इलाज करते हैं।","work_en":"Treats tooth pain, cavity and gum swelling.","when_hi":"गाल सूज जाए या दर्द 2 दिन से न रुके, तो दिखाएं।","when_en":"If cheek swells or pain does not stop in 2 days, see dentist.","fees_hi":"₹200 - ₹500","fees_en":"Rs. 200 - Rs. 500"},
    "eye": {"spec_hi":"आंख के डॉक्टर","spec_en":"Eye Doctor","work_hi":"आंख में जलन, लालपन, मोतियाबिंद, चश्मा की समस्या का इलाज करते हैं।","work_en":"Treats eye burning, redness, cataract and vision problems.","when_hi":"दिखाई कम हो या आंख से मवाद आए, तो तुरंत दिखाएं।","when_en":"If vision is less or pus comes from eye, see immediately.","fees_hi":"₹300 - ₹500","fees_en":"Rs. 300 - Rs. 500"},
    "ear": {"spec_hi":"कान-नाक-गला विशेषज्ञ","spec_en":"ENT Doctor","work_hi":"कान दर्द, नाक बंद, साइनस, टॉन्सिल का इलाज करते हैं।","work_en":"Treats ear pain, blocked nose, sinus and tonsil.","when_hi":"सुनाई कम दे या कान से पानी आए, तो दिखाएं।","when_en":"If hearing is less or water comes from ear, see doctor.","fees_hi":"₹300 - ₹600","fees_en":"Rs. 300 - Rs. 600"},
    "injury": {"spec_hi":"सर्जन / हड्डी रोग विशेषज्ञ","spec_en":"Surgeon / Orthopedic Doctor","work_hi":"चोट, जख्म, कटने, मोच, जलने का इलाज करते हैं।","work_en":"Treats injury, wound, cuts, sprain and burn.","when_hi":"खून न रुके या चोट गहरी हो, तो तुरंत अस्पताल जाएं।","when_en":"If bleeding does not stop or wound is deep, go to hospital immediately.","fees_hi":"₹300 - ₹700","fees_en":"Rs. 300 - Rs. 700"},
    "diabetes": {"spec_hi":"डायबिटीज / एंडोक्रिनोलॉजिस्ट","spec_en":"Diabetologist / Endocrinologist","work_hi":"शुगर, थायराइड, हार्मोन की समस्या का इलाज करते हैं।","work_en":"Treats diabetes, thyroid and hormone problems.","when_hi":"शुगर बहुत ज्यादा हो या चक्कर आए, तो तुरंत दिखाएं।","when_en":"If sugar is very high or dizziness, see immediately.","fees_hi":"₹400 - ₹700","fees_en":"Rs. 400 - Rs. 700"},
    "heart": {"spec_hi":"हृदय रोग विशेषज्ञ","spec_en":"Cardiologist","work_hi":"बीपी, कोलेस्ट्रॉल, दिल की धड़कन की समस्या का इलाज करते हैं।","work_en":"Treats BP, cholesterol and heart beat problems.","when_hi":"सीने में दर्द + पसीना आए, तो तुरंत 108 पर कॉल करें।","when_en":"If chest pain with sweating, call 108 immediately.","fees_hi":"₹500 - ₹800","fees_en":"Rs. 500 - Rs. 800"},
    "mental": {"spec_hi":"मानसिक रोग विशेषज्ञ","spec_en":"Psychiatrist / Psychologist","work_hi":"घबराहट, उदासी, स्ट्रेस, नींद, मिर्गी की समस्या का इलाज करते हैं।","work_en":"Treats anxiety, depression, stress, sleep and epilepsy.","when_hi":"खुद को नुकसान का मन करे, तो तुरंत 14416 पर कॉल करें।","when_en":"If you feel like harming yourself, call 14416 immediately.","fees_hi":"₹500 - ₹1000","fees_en":"Rs. 500 - Rs. 1000"},
    "kidney": {"spec_hi":"किडनी रोग विशेषज्ञ","spec_en":"Nephrologist / Urologist","work_hi":"पथरी, पेशाब में जलन, किडनी की समस्या का इलाज करते हैं।","work_en":"Treats kidney stone, UTI and kidney problems.","when_hi":"पेशाब में खून आए या पेशाब बंद हो जाए, तो तुरंत दिखाएं।","when_en":"If blood in urine or urine stops, see immediately.","fees_hi":"₹500 - ₹800","fees_en":"Rs. 500 - Rs. 800"},
    "liver": {"spec_hi":"लीवर रोग विशेषज्ञ","spec_en":"Hepatologist","work_hi":"पीलिया, हेपेटाइटिस, लीवर की समस्या का इलाज करते हैं।","work_en":"Treats jaundice, hepatitis and liver problems.","when_hi":"आंखें पीली हो जाएं या पेट फूल जाए, तो तुरंत दिखाएं।","when_en":"If eyes become yellow or stomach swells, see immediately.","fees_hi":"₹500 - ₹800","fees_en":"Rs. 500 - Rs. 800"},
    "piles": {"spec_hi":"सर्जन / पेट रोग विशेषज्ञ","spec_en":"Surgeon / Gastroenterologist","work_hi":"बवासीर, फिशर, अपेंडिक्स, अल्सर का इलाज करते हैं।","work_en":"Treats piles, fissure, appendix and ulcer.","when_hi":"खून ज्यादा आए या बहुत तेज दर्द हो, तो तुरंत दिखाएं।","when_en":"If too much bleeding or severe pain, see immediately.","fees_hi":"₹400 - ₹800","fees_en":"Rs. 400 - Rs. 800"},
    "ladies": {"spec_hi":"स्त्री रोग विशेषज्ञ","spec_en":"Gynecologist","work_hi":"माहवारी, गर्भावस्था, सफेद पानी की समस्या का इलाज करते हैं।","work_en":"Treats periods, pregnancy and white discharge problems.","when_hi":"बहुत ज्यादा खून आए या पेट में तेज दर्द हो, तो तुरंत दिखाएं।","when_en":"If too much bleeding or severe stomach pain, see immediately.","fees_hi":"₹400 - ₹700","fees_en":"Rs. 400 - Rs. 700"},
    "child": {"spec_hi":"बच्चों के डॉक्टर","spec_en":"Pediatrician","work_hi":"बच्चों के बुखार, खांसी, दस्त, दानों का इलाज करते हैं।","work_en":"Treats children fever, cough, loose motion and rash.","when_hi":"बच्चे को तेज बुखार हो या बच्चा दूध न पी रहा हो, तो तुरंत दिखाएं।","when_en":"If child has high fever or is not drinking milk, see immediately.","fees_hi":"₹300 - ₹600","fees_en":"Rs. 300 - Rs. 600"},
    "serious": {"spec_hi":"सामान्य चिकित्सक / स्पेशलिस्ट","spec_en":"General Physician / Specialist","work_hi":"टीबी, मलेरिया, डेंगू, टाइफाइड, कैंसर जैसी बड़ी बीमारियों का इलाज करते हैं।","work_en":"Treats serious diseases like TB, malaria, dengue, typhoid, cancer.","when_hi":"ये बीमारी घर पर ठीक नहीं होती, तुरंत डॉक्टर को दिखाएं, देर मत करें।","when_en":"This disease cannot be cured at home, see doctor immediately, do not wait.","fees_hi":"सरकारी अस्पताल में फ्री","fees_en":"FREE in Govt Hospital"},
    "general": {"spec_hi":"सामान्य चिकित्सक","spec_en":"General Physician","work_hi":"आम बीमारियों का इलाज करते हैं, जरूरत हो तो सही स्पेशलिस्ट के पास भेजते हैं।","work_en":"Treats common diseases and refers to right specialist if needed.","when_hi":"तकलीफ 2-3 दिन से ज्यादा रहे, तो दिखाएं।","when_en":"If problem stays more than 2-3 days, see doctor.","fees_hi":"₹200 - ₹500","fees_en":"Rs. 200 - Rs. 500"},
}

# ---------- ONLINE DOCTOR - DIRECT CONTACT - SACH WALA ----------
def show_doctor_detail_card(user_text, loc):
    cat = get_category_for(user_text)
    info = DOCTOR_INFO[cat]
    city = loc.get("city","")
    pincode = loc.get("pincode","")
    spec = info["spec_hi"] if IS_HINDI else info["spec_en"]
    spec_en = info["spec_en"]
    work = info["work_hi"] if IS_HINDI else info["work_en"]
    when = info["when_hi"] if IS_HINDI else info["when_en"]
    fees = info["fees_hi"] if IS_HINDI else info["fees_en"]
    # PHYSICAL
    st.markdown(f"""<div class="doctor-card"><b>👨‍⚕️ {T('आपको इस डॉक्टर की जरूरत है:','You need this doctor:')} {spec}</b><br><br><span><b>{T('ये डॉक्टर क्या करते हैं?','What does this doctor do?')}</b><br>{work}</span><br><br><span><b>{T('कब दिखाना चाहिए?','When to see?')}</b><br>{when}</span><br><br><span><b>{T('अंदाज़न फीस:','Approx Fees:')}</b> {fees}</span><br><br><span><b>{T('आपका इलाका:','Your Area:')}</b> {city}, {pincode}, India</span></div>""", unsafe_allow_html=True)
    maps_q = urllib.parse.quote(f"{spec_en} doctor near {city} {pincode} India")
    st.markdown(f"""<div class="info-box"><b>{T('आपके पास के डॉक्टर - Maps पर असली डॉक्टर देखें','Doctors Near You - See Real Doctors On Maps')}</b><br>{T('हम किसी भी शहर के डॉक्टर का नाम अपने आप से नहीं बनाते। नीचे वाले बटन पर क्लिक करें, गूगल मैप्स आपके शहर और पिनकोड के असली डॉक्टर दिखा देगा - नाम, नंबर, रेटिंग सब।','We do not make up doctor names for any city. Click below button, Google Maps will show real doctors of your city and pincode - name, number, rating.')}</div>""", unsafe_allow_html=True)
    st.link_button(f"📍 {T('मेरे पास के डॉक्टर देखें - Maps','See Doctors Near Me - Maps')}", f"https://www.google.com/maps/search/{maps_q}", use_container_width=True)
    # ONLINE - DIRECT CONTACT
    st.markdown(f"### {T('🌐 ऑनलाइन डॉक्टर - डायरेक्ट संपर्क करें','🌐 Online Doctors - Contact Directly')}")
    st.write(T(f"आपकी तकलीफ के लिए ऑनलाइन भी यही डॉक्टर चाहिए: {spec}. नीचे से किसी एक को चुनें, सीधा डॉक्टर से बात हो जाएगी।","For your problem, you need same doctor online also: " + spec + ". Choose any one below, you will directly talk to doctor."))
    # 1. eSanjeevani - DIRECT VIDEO CALL - NO NAME NEEDED
    st.markdown(f"""<div class="online-card"><b>🩺 {T('ई-संजीवनी - सरकारी, फ्री - डायरेक्ट वीडियो कॉल','eSanjeevani - Govt, FREE - Direct Video Call')}</b><br><span>{T('कोई नाम ढूंढना नहीं है। लिंक पर क्लिक करते ही सरकारी डॉक्टर से सीधी वीडियो कॉल हो जाएगी।','No need to search name. On clicking link, direct video call with Govt doctor.')}</span><br><span><b>{T('समय:','Timing:')}</b> {T('सुबह 10 - शाम 4','10 AM - 4 PM')}</span><br><span><b>{T('फीस:','Fees:')}</b> {T('बिल्कुल फ्री','Totally FREE')}</span></div>""", unsafe_allow_html=True)
    st.link_button(T("🩺 डायरेक्ट वीडियो कॉल करें - ई-संजीवनी","🩺 Direct Video Call - eSanjeevani"), "https://esanjeevani.mohfw.gov.in", use_container_width=True)
    # 2. 104 - DIRECT CALL
    st.markdown(f"""<div class="online-card"><b>📞 {T('104 - हेल्थ हेल्पलाइन - डायरेक्ट कॉल','104 - Health Helpline - Direct Call')}</b><br><span>{T('इस नंबर पर कॉल करते ही डॉक्टर / नर्स से सीधी बात हो जाएगी।','On calling this number, you will directly talk to doctor / nurse.')}</span><br><span><b>{T('नंबर:','Number:')}</b> 104 - {T('बिल्कुल फ्री','Totally FREE')}</span></div>""", unsafe_allow_html=True)
    st.link_button(T("📞 104 पर डायरेक्ट कॉल करें","📞 Call 104 Directly"), "tel:104", use_container_width=True)
    # 3. Practo - DIRECT DOCTOR PROFILE - CITY + SPECIALITY
    st.markdown(f"""<div class="online-card"><b>💻 {T('प्रैक्टो - डायरेक्ट डॉक्टर से चैट / कॉल','Practo - Chat / Call Doctor Directly')}</b><br><span><b>{T('डॉक्टर:','Doctor:')}</b> {spec}</span><br><span><b>{T('शहर:','City:')}</b> {city}</span><br><span>{T('नीचे क्लिक करते ही प्रैक्टो आपके शहर के असली डॉक्टरों की लिस्ट खोलेगा। किसी भी डॉक्टर के प्रोफाइल पर क्लिक करें, वहां Call / Chat / Book का बटन होगा, उसी से आप सीधा उस डॉक्टर से संपर्क कर सकते हैं। हम नाम अपने आप से नहीं बनाते, साइट खुद असली डॉक्टर दिखाती है।','On clicking below, Practo will open real doctors list of your city. Click any doctor profile, there you will see Call / Chat / Book button, from there you can directly contact that doctor. We do not make up names, site shows real doctors.')}</span></div>""", unsafe_allow_html=True)
    st.link_button(T(f"💻 {city} के {spec} से डायरेक्ट चैट / कॉल करें - प्रैक्टो","💻 Chat / Call Doctor Directly - Practo"), f"https://www.practo.com/search/doctors?speciality={urllib.parse.quote(spec_en)}&city={urllib.parse.quote(city)}", use_container_width=True)
    # 4. Apollo - DIRECT NUMBER + DIRECT LINK
    st.markdown(f"""<div class="online-card"><b>🏥 {T('अपोलो 24/7 - डायरेक्ट कॉल + डायरेक्ट लिंक','Apollo 24/7 - Direct Call + Direct Link')}</b><br><span><b>{T('डॉक्टर:','Doctor:')}</b> {spec}</span><br><span><b>{T('शहर:','City:')}</b> {city}</span><br><span>{T('नीचे वाले नंबर पर कॉल करते ही अपोलो का डॉक्टर आपसे सीधी बात करेगा। या लिंक पर क्लिक करके किसी भी डॉक्टर के प्रोफाइल से Call / Video Call करें।','On calling below number, Apollo doctor will directly talk to you. Or click link and Call / Video Call any doctor from profile.')}</span><br><span><b>{T('डायरेक्ट नंबर:','Direct Number:')}</b> 1860-500-1066</span></div>""", unsafe_allow_html=True)
    st.link_button(T("📞 1860-500-1066 पर डायरेक्ट कॉल करें - अपोलो","📞 Call 1860-500-1066 Directly - Apollo"), "tel:18605001066", use_container_width=True)
    st.link_button(T(f"🏥 {city} के {spec} से डायरेक्ट कॉल करें - अपोलो","🏥 Call Doctor Directly - Apollo"), f"https://www.apollo247.com/search/doctors?speciality={urllib.parse.quote(spec_en)}&city={urllib.parse.quote(city)}", use_container_width=True)
    st.link_button(T("🚑 108 - एम्बुलेंस","🚑 108 - Ambulance"), "tel:108", use_container_width=True)

def show_location_form(for_text):
    st.markdown(f"### {T('📍 डॉक्टर खोजने के लिए अपनी लोकेशन बताइए','📍 Tell Your Location To Find Doctor')}")
    st.write(T("ये ऐप सिर्फ इंडिया के लिए है।","This app is only for India."))
    city = st.text_input(T("शहर का नाम","City Name"), value="", placeholder=T("शहर लिखें...","Write city..."), key="loc_city")
    pincode = st.text_input(T("पिनकोड","Pincode"), value="", placeholder=T("पिनकोड लिखें...","Write pincode..."), key="loc_pincode")
    if st.button(T("✅ डॉक्टर खोजें","✅ Find Doctor"), use_container_width=True, key="find_doctor_btn"):
        if city.strip() == "" or pincode.strip() == "":
            st.warning(T("पहले शहर और पिनकोड लिखिए।","First write city and pincode."))
        else:
            st.session_state.doctor_location = {"country": "India", "city": city.strip(), "pincode": pincode.strip()}
            st.session_state.doctor_step = "done"
            st.session_state.messages.append({"role":"assistant","content":"DOCTORS_BOX","for_text": for_text, "loc": dict(st.session_state.doctor_location)})
            st.rerun()

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
    .banner-wrap {{ position: fixed; bottom: 0; left: 0; right: 0; z-index: 9999; background: linear-gradient(90deg,#EEF2FF,#FDF2F8); height: 48px; overflow: hidden; border-top: 1px solid #E0E7FF; }}
    .banner-wrap .tip {{ position: absolute; left: 0; right: 0; top: 0; height: 48px; display: flex; align-items: center; justify-content: center; color: #4338CA !important; font-weight: 600; font-size: 14px; padding: 0 10px; text-align: center; opacity: 0; animation: tipCycle 24s linear infinite; }}
    @keyframes tipCycle {{ 0% {{opacity: 0;}} 1% {{opacity: 1;}} 15% {{opacity: 1;}} 17% {{opacity: 0;}} 100% {{opacity: 0;}} }}
    </style>
    <div class="banner-wrap">{items}</div>
    """, unsafe_allow_html=True)

def D(hi, en, causes_hi, causes_en, dangers_hi, dangers_en, dos_hi, dos_en, tip_hi, tip_en, sum_hi, sum_en, serious=False):
    return {"hi":hi,"en":en,"causes_hi":causes_hi,"causes_en":causes_en,"dangers_hi":dangers_hi,"dangers_en":dangers_en,"dos_hi":dos_hi,"dos_en":dos_en,"tip_hi":tip_hi,"tip_en":tip_en,"sum_hi":sum_hi,"sum_en":sum_en,"serious":serious}

DISEASES = [
    (["head","sar","sir","सिर","headache","migraine"], D("सिर दर्द / माइग्रेन","Headache / Migraine", [("नींद की कमी","रात को नींद पूरी न होने से सुबह उठते ही सिर भारी लगता है।"),("ज्यादा फोन","दिन भर फोन देखने से आंखों पर जोर पड़ता है।"),("गैस / भूख","लंबी देर भूखे रहने से या गैस बनने से भी सिर में दर्द होता है।")], [("Less Sleep","When you do not sleep well, you wake up with heavy head."),("Too Much Phone","Watching phone all day puts pressure on eyes."),("Gas and Hunger","Staying hungry or gas also causes headache.")], [("बहुत तेज दर्द","अगर अचानक बहुत तेज दर्द हो, तो तुरंत डॉक्टर को दिखाएं।"),("उल्टी / चक्कर","सिर दर्द के साथ उल्टी या चक्कर आए, तो देर मत करें।")], [("Very Severe Pain","If sudden very severe headache, see doctor immediately."),("Vomiting / Dizziness","If vomiting or dizziness with headache, do not wait.")], [("अंधेरे में आराम","लाइट बंद करके अंधेरे कमरे में लेट जाएं, फोन मत देखें।"),("ठंडी पट्टी","सिर पर ठंडे पानी की पट्टी रखें।"),("गुनगुना पानी","थोड़ा-थोड़ा करके गुनगुना पानी पिएं।")], [("Rest in Dark Room","Lie down in dark room, do not see phone."),("Cold Cloth","Keep cold wet cloth on head."),("Warm Water","Drink warm water in small sips.")], ("फोन कम देखें","रोज सोने से 30 मिनट पहले फोन बंद कर दें।"), ("Less Phone","Switch off phone 30 minutes before sleeping."), "आपका सिर दर्द ज्यादातर नींद की कमी और फोन देखने की वजह से लग रहा है।", "Your headache seems mostly because of less sleep and too much phone.")),
    (["back","kamar","spine","कमर"], D("कमर दर्द","Back Pain", [("गलत बैठना","लंबी देर झुककर बैठने से कमर पर जोर पड़ता है।"),("भारी चीज उठाना","भारी बाल्टी उठाने से नस खिंच जाती है।"),("कमजोरी","कैल्शियम और विटामिन डी की कमी से हड्डियां कमजोर होती हैं।")], [("Wrong Sitting","Sitting bent puts pressure on back."),("Lifting Heavy Things","Lifting heavy bag pulls nerve."),("Weakness","Lack of Calcium and Vitamin D makes bones weak.")], [("पैर में दर्द","अगर दर्द कमर से पैर तक जा रहा है, तो तुरंत डॉक्टर को दिखाएं।"),("चलने में दिक्कत","अगर चलने में बहुत तकलीफ हो, तो देर मत करें।")], [("Pain in Leg","If pain goes from back to leg, see doctor immediately."),("Difficulty Walking","If difficulty in walking, do not wait.")], [("सीधा लेटें","सीधे सख्त बिस्तर पर लेट जाएं।"),("गरम सेंक","कमर पर दिन में 2 बार 10 मिनट गरम सेंक करें।"),("भारी काम बंद","2 दिन तक भारी चीज मत उठाएं।")], [("Lie Straight","Lie straight on hard bed."),("Hot Compress","Apply warm cloth 10 minutes, 2 times a day."),("Stop Heavy Work","Do not lift heavy things for 2 days.")], ("रोज टहलें","रोज 20 मिनट सीधा चलिए।"), ("Daily Walk","Walk straight 20 minutes daily."), "आपका कमर दर्द ज्यादातर गलत बैठने और भारी काम की वजह से लग रहा है।", "Your back pain seems mostly because of wrong sitting and heavy work.")),
    (["body","badan","sharir","whole","बदन"], D("पूरा बदन दर्द","Body Pain", [("थकान","दिन भर ज्यादा काम करने से पूरा शरीर थक जाता है।"),("वायरल","मौसम बदलने से हल्का वायरस लग जाता है।"),("पानी की कमी","पानी कम पीने से मांसपेशियों में दर्द होता है।")], [("Tiredness","Working too much makes body tired."),("Viral Infection","Change in weather causes mild virus."),("Less Water","Drinking less water causes muscle pain.")], [("तेज बुखार","बुखार 102 से ऊपर हो, तो तुरंत डॉक्टर को दिखाएं।"),("सांस में दिक्कत","सांस लेने में तकलीफ हो, तो देर मत करें।")], [("High Fever","If fever above 102, see doctor immediately."),("Breathing Problem","If difficulty in breathing, do not wait.")], [("पूरा आराम","आज भारी काम बंद करके पूरा आराम कीजिए।"),("गरम पानी से नहाएं","गुनगुने पानी से नहाने से आराम मिलेगा।"),("गुनगुना पानी पिएं","दिन भर थोड़ा-थोड़ा गुनगुना पानी पिएं।")], [("Full Rest","Stop heavy work and take full rest."),("Warm Water Bath","Bathing with warm water will relax muscles."),("Warm Water","Keep drinking warm water in small sips.")], ("रोज टहलें","रोज 30 मिनट हल्की टहल से मांसपेशियां मजबूत होती हैं।"), ("Daily Walk","Walking 30 minutes daily makes muscles strong."), "आपका बदन दर्द ज्यादातर थकान और वायरल की वजह से लग रहा है।", "Your body pain seems mostly because of tiredness and viral.")),
    (["fever","bukhar","बुखार","viral"], D("बुखार","Fever", [("वायरल बुखार","मौसम बदलने से वायरस से बुखार आ जाता है।"),("सर्दी","गले में खराश और सर्दी के साथ भी हल्का बुखार आ सकता है।"),("पानी की कमी","पानी कम पीने से शरीर गरम हो जाता है।")], [("Viral Fever","Change in weather causes viral infection."),("Cold","Throat infection and cold can also give mild fever."),("Less Water","Drinking less water makes body hot.")], [("तेज बुखार","बुखार 102 से ऊपर हो, तो तुरंत डॉक्टर को दिखाएं।"),("उल्टी / चक्कर","उल्टी या चक्कर आए, तो देर मत करें।")], [("High Fever","If fever above 102, see doctor immediately."),("Vomiting / Dizziness","If vomiting or dizziness, do not wait.")], [("आराम करें","पूरा आराम करें।"),("ठंडी पट्टी","सिर पर ठंडे पानी की पट्टी रखें।"),("गुनगुना पानी","थोड़ा-थोड़ा करके गुनगुना पानी पिएं।")], [("Take Rest","Take full rest."),("Cold Sponge","Keep cold wet cloth on forehead."),("Warm Water","Drink warm water in small sips.")], ("तुलसी काढ़ा","तुलसी और अदरक का काढ़ा पीने से बुखार में आराम मिलता है।"), ("Tulsi Kadha","Tulsi and ginger kadha gives relief in fever."), "आपका बुखार अभी शुरू हुआ लग रहा है, 1 दिन आराम करके देखिए।", "Your fever seems in starting stage, take rest for 1 day.")),
    (["cold","cough","khansi","sardi","throat","gala","गला","सर्दी","खांसी","sinus","tonsil","naak","नाक"], D("सर्दी-खांसी / साइनस / टॉन्सिल","Cold-Cough / Sinus / Tonsil", [("वायरल संक्रमण","मौसम बदलने से गले में वायरस लग जाता है।"),("ठंडा पानी","ठंडा पानी या आइसक्रीम से गला खराब हो जाता है।"),("धूल","धूल-मिट्टी से एलर्जी हो जाती है।")], [("Viral Infection","Change in weather causes virus in throat."),("Cold Water","Cold water or ice-cream makes throat bad."),("Dust Allergy","Dust causes allergy and cough starts.")], [("सांस में दिक्कत","सांस लेने में तकलीफ हो, तो तुरंत डॉक्टर को दिखाएं।"),("खून वाली खांसी","खांसी में खून आए, तो देर मत करें।")], [("Breathing Problem","If difficulty in breathing, see doctor immediately."),("Blood in Cough","If blood comes in cough, do not wait.")], [("गरम पानी","दिन भर गुनगुना पानी पिएं।"),("हल्दी दूध","रात को हल्दी वाला गरम दूध पिएं।"),("भाप","गरम पानी की भाप लेने से नाक खुल जाती है।")], [("Warm Water","Drink warm water through the day."),("Turmeric Milk","Drink warm turmeric milk at night."),("Steam","Take steam from hot water.")], ("तुलसी-अदरक","तुलसी और अदरक की चाय से गले को आराम मिलता है।"), ("Tulsi-Ginger","Tulsi and ginger tea gives relief to throat."), "आपकी सर्दी-खांसी अभी शुरू हुई लग रही है, 2 दिन गरम चीजें लीजिए।", "Your cold-cough seems in starting stage, take warm things for 2 days.")),
    (["stomach","pet","gas","ulti","vomit","dast","loose","diarrhea","पेट","उल्टी","kabz","acidity","bhook","keede","कीड़े","ulcer"], D("पेट दर्द / गैस / कब्ज / दस्त","Stomach Problem / Gas / Constipation", [("गैस","बाहर का खाना या जल्दी खाने से पेट में गैस बन जाती है।"),("एसिडिटी","मसालेदार खाना या खाली पेट रहने से एसिडिटी हो जाती है।"),("कब्ज","पानी कम पीने से कब्ज होता है।")], [("Gas","Eating outside food causes gas."),("Acidity","Spicy food or empty stomach causes acidity."),("Constipation","Drinking less water causes constipation.")], [("तेज दर्द","पेट में बहुत तेज दर्द हो, तो तुरंत डॉक्टर को दिखाएं।"),("खून","पॉटी में खून आए, तो देर मत करें।")], [("Severe Pain","If stomach pain is very severe, see doctor immediately."),("Blood","If blood comes in stool, do not wait.")], [("हल्का खाना","आज खिचड़ी, दही जैसा हल्का खाना खाएं।"),("ओआरएस पानी","थोड़ा-थोड़ा करके ओआरएस पिएं।"),("टहलें","खाने के बाद 10 मिनट हल्की टहल करें।")], [("Light Food","Eat light food like khichdi, curd."),("ORS Water","Drink ORS in small sips."),("Walk","Walk 10 minutes after food.")], ("अजवाइन पानी","अजवाइन का पानी गैस में तुरंत आराम देता है।"), ("Ajwain Water","Ajwain water gives instant relief in gas."), "आपका पेट दर्द गैस और एसिडिटी से लग रहा है, आज हल्का खाना खाएं।", "Your stomach pain seems due to gas and acidity, eat light food today.")),
    (["chest","seene","saans","breath","सीने","सांस","asthma","dama","दमा"], D("सीने में दर्द / अस्थमा","Chest Problem / Asthma", [("गैस","पेट की गैस ऊपर चढ़ने से सीने में भारीपन लगता है।"),("सर्दी","सर्दी और धूल से सीने में जकड़न हो जाती है।"),("थकान","ज्यादा काम करने से सांस फूलने लगती है।")], [("Gas","Gas from stomach goes up and causes heaviness in chest."),("Cold","Cold and dust causes tightness in chest."),("Tiredness","Too much work causes breathlessness.")], [("बहुत तेज दर्द","सीने में बहुत तेज दर्द हो, तो तुरंत 108 पर कॉल करें।"),("पसीना","सीने के दर्द के साथ पसीना आए, तो तुरंत अस्पताल जाएं।")], [("Severe Pain","If chest pain is very severe, call 108 immediately."),("Sweating","If sweating with chest pain, go to hospital fast.")], [("सीधा बैठें","सीधा बैठ जाएं, कपड़े ढीले कर दें।"),("हवा","खिड़की खोल दें।"),("गुनगुना पानी","थोड़ा-थोड़ा गुनगुना पानी पिएं।")], [("Sit Straight","Sit straight, loosen clothes."),("Air","Open windows."),("Warm Water","Drink warm water in small sips.")], ("धूल से बचें","धूल और धुएं से दूर रहें।"), ("Avoid Dust","Stay away from dust and smoke."), "आपके सीने का दर्द गैस और सर्दी से लग रहा है, लेकिन दर्द तेज है तो तुरंत डॉक्टर को दिखाएं।", "Your chest pain seems due to gas and cold, but if pain is severe, see doctor immediately.")),
    (["leg","pair","knee","ghutna","hand","haath","joint","shoulder","kandha","पैर","हाथ","घुटना","arthritis","gathiya","गठिया","sciatica","freeze"], D("हाथ-पैर / घुटना / गठिया दर्द","Leg / Joint / Arthritis Pain", [("थकान","ज्यादा चलने से हाथ-पैर में दर्द हो जाता है।"),("कैल्शियम की कमी","कैल्शियम की कमी से घुटनों में दर्द होता है।"),("गलत बैठना","गलत बैठने से घुटने पर जोर पड़ता है।")], [("Tiredness","Walking too much causes leg pain."),("Calcium Deficiency","Lack of Calcium causes knee pain."),("Wrong Posture","Wrong sitting puts pressure on knee.")], [("सूजन","बहुत सूजन आ जाए, तो डॉक्टर को दिखाएं।"),("तेज दर्द","दर्द 2 दिन से ज्यादा रहे, तो देर मत करें।")], [("Swelling","If too much swelling, see doctor."),("Severe Pain","If pain stays more than 2 days, do not wait.")], [("आराम","उस पैर को आराम दें।"),("गरम सेंक","10 मिनट गरम सेंक करें।"),("पैर ऊपर रखें","पैर को तकिए पर ऊपर रखकर लेटें।")], [("Rest","Give rest to that leg."),("Hot Compress","Apply warm cloth for 10 minutes."),("Raise Leg","Keep leg raised on pillow.")], ("दूध पिएं","रोज 1 गिलास दूध पिएं।"), ("Drink Milk","Drink 1 glass milk daily."), "आपका हाथ-पैर का दर्द थकान और कैल्शियम की कमी से लग रहा है।", "Your leg pain seems due to tiredness and calcium deficiency.")),
    (["eye","aankh","ankh","आंख","motiyabind","मोतियाबिंद","chashma","चश्मा"], D("आंख की समस्या","Eye Problem", [("फोन / धूल","ज्यादा फोन देखने से आंख में जलन होती है।"),("नींद की कमी","नींद पूरी न होने से आंख लाल हो जाती है।"),("एलर्जी","धूल से आंख में एलर्जी हो जाती है।")], [("Phone / Dust","Too much phone causes burning in eyes."),("Less Sleep","Less sleep makes eyes red."),("Allergy","Dust causes allergy in eyes.")], [("दिखाई कम","दिखाई कम हो, तो तुरंत डॉक्टर को दिखाएं।"),("मवाद","आंख से मवाद आए, तो देर मत करें।")], [("Less Vision","If vision is less, see doctor immediately."),("Pus","If pus comes from eyes, do not wait.")], [("आंख मत मसलें","आंख को मसलें नहीं, साफ पानी से धोएं।"),("फोन कम","फोन कम देखिए।"),("ठंडी पट्टी","आंख पर ठंडी पट्टी रखें।")], [("Do Not Rub","Do not rub eyes, wash with clean water."),("Less Phone","Use phone less."),("Cold Cloth","Keep cold cloth on eyes.")], ("धूप से बचें","धूप में चश्मा पहनें।"), ("Avoid Sun","Wear glasses in sunlight."), "आपकी आंख की समस्या फोन और धूल की वजह से लग रही है।", "Your eye problem seems due to phone and dust.")),
    (["ear","kaan","कान"], D("कान में दर्द","Ear Pain", [("सर्दी","सर्दी के साथ कान में दर्द हो जाता है।"),("पानी","नहाते समय कान में पानी जाने से दर्द होता है।"),("मैल","कान में मैल जमने से दर्द होता है।")], [("Cold","Cold causes ear pain."),("Water","Water going in ear during bath causes pain."),("Wax","Wax in ear causes pain.")], [("सुनाई कम","सुनाई कम दे, तो डॉक्टर को दिखाएं।"),("तेज बुखार","कान दर्द के साथ तेज बुखार हो, तो देर मत करें।")], [("Less Hearing","If hearing is less, see doctor."),("High Fever","If high fever with ear pain, do not wait.")], [("कुछ मत डालें","कान में तीली मत डालें।"),("गरम सेंक","हल्का गरम सेंक करें।"),("आराम","थोड़ी देर आराम करें।")], [("Do Not Insert","Do not insert anything in ear."),("Warm Compress","Apply light warm compress."),("Rest","Take rest.")], ("कान साफ रखें","कान को साफ और सूखा रखें।"), ("Keep Ear Clean","Keep ear clean and dry."), "आपके कान का दर्द सर्दी की वजह से लग रहा है।", "Your ear pain seems due to cold.")),
    (["tooth","daant","dant","दांत"], D("दांत में दर्द","Tooth Pain", [("कीड़ा","दांत में कीड़ा लगने से दर्द होता है।"),("ठंडा-गरम","ठंडा-गरम खाने से दांत में झनझनाहट होती है।"),("मसूड़ा","मसूड़े में सूजन से दांत दुखने लगता है।")], [("Cavity","Cavity in tooth causes pain."),("Cold-Hot","Cold-hot food causes sensitivity."),("Gum Swelling","Gum swelling causes tooth pain.")], [("सूजन","गालों पर सूजन आ जाए, तो डॉक्टर को दिखाएं।"),("दर्द न रुके","दर्द 2 दिन से न रुके, तो देर मत करें।")], [("Swelling","If cheek swells, see doctor."),("Pain Not Stopping","If pain does not stop in 2 days, do not wait.")], [("नमक पानी","गुनगुने नमक पानी से कुल्ला करें।"),("लौंग","लौंग का तेल लगाएं।"),("ठंडा मत खाएं","ठंडा और मीठा मत खाएं।")], [("Salt Water","Gargle with warm salt water."),("Clove Oil","Apply clove oil."),("Avoid Cold","Avoid cold and sweet.")], ("ब्रश","दिन में 2 बार ब्रश करें।"), ("Brush","Brush 2 times a day."), "आपके दांत का दर्द कीड़े और मसूड़े की सूजन से लग रहा है।", "Your tooth pain seems due to cavity and gum swelling.")),
    (["daane","rash","khujli","itching","दाने","खुजली","pimple","muhase","मुहासे","dandruff","baal","बाल","fungal","eczema","psoriasis","vitiligo","daag","dhabbe"], D("दाने / खुजली / पिंपल / स्किन","Rash / Itching / Pimple / Skin", [("एलर्जी","नए साबुन, कपड़े या धूल से एलर्जी हो जाती है।"),("गर्मी","गर्मी में पसीना जमने से दाने निकल आते हैं।"),("संक्रमण","साफ-सफाई न रखने से संक्रमण हो जाता है।")], [("Allergy","New soap, clothes or dust causes allergy."),("Heat","Sweat causes rashes in heat."),("Infection","Lack of cleanliness causes infection.")], [("मवाद","दानों से मवाद निकले, तो डॉक्टर को दिखाएं।"),("तेज बुखार","दानों के साथ तेज बुखार हो, तो देर मत करें।"),("सांस में दिक्कत","सांस में दिक्कत हो तो तुरंत 108 पर कॉल करें।")], [("Pus","If pus comes, see doctor."),("High Fever","If high fever with rashes, do not wait."),("Breathing Problem","If breathing problem, call 108 immediately.")], [("खुजलाएं नहीं","दानों को खुजलाएं नहीं, इससे संक्रमण बढ़ता है।"),("साफ रखें","साफ पानी से धोकर सुखा रखें।"),("ठंडा पानी","ठंडे पानी से सेंक करें।"),("नारियल तेल","हल्का नारियल तेल लगाएं।")], [("Do Not Scratch","Do not scratch, it increases infection."),("Keep Clean","Wash with clean water and keep dry."),("Cold Water","Apply cold water compress."),("Coconut Oil","Apply light coconut oil.")], ("साफ कपड़े","रोज साफ कपड़े पहनें, पसीने वाले कपड़े तुरंत बदलें।"), ("Clean Clothes","Wear clean clothes daily, change sweaty clothes immediately."), "आपके दाने एलर्जी या गर्मी की वजह से लग रहे हैं। 2 दिन में कम न हों तो डॉक्टर को दिखाएं।", "Your rash seems due to allergy or heat. If not better in 2 days, see doctor.")),
    (["chot","zakhm","wound","injury","kat","cut","चोट","moch","burn","jalna","जल"], D("चोट / जख्म / जलना","Injury / Wound / Burn", [("गिरना","गिरने या टकराने से चोट लग जाती है।"),("तेज चीज","चाकू या कांच से कटने से जख्म हो जाता है।"),("जलना","गरम चीज से जलने से चोट लगती है।")], [("Fall","Falling or hitting causes injury."),("Sharp Object","Knife or glass cut causes wound."),("Burn","Hot thing causes burn injury.")], [("बहुत खून","खून रुक न रहा हो, तो तुरंत 108 पर कॉल करें।"),("गहरी चोट","गहरी चोट हो या हड्डी दिख रही हो, तो तुरंत अस्पताल जाएं।"),("बुखार","चोट के बाद बुखार आए, तो डॉक्टर को दिखाएं।")], [("Heavy Bleeding","If bleeding is not stopping, call 108 immediately."),("Deep Wound","If wound is deep or bone is visible, go to hospital immediately."),("Fever","If fever after injury, see doctor.")], [("साफ पानी से धोएं","चोट को साफ पानी से धोएं, गंदे पानी से नहीं।"),("खून रोकें","साफ कपड़े से चोट को दबाकर रखें, 10 मिनट तक मत हटाएं।"),("बेटाडीन लगाएं","हल्का बेटाडीन लगाएं, हल्दी / मिट्टी / टूथपेस्ट मत लगाएं।"),("पट्टी बांधें","साफ पट्टी बांधें।")], [("Wash With Clean Water","Wash wound with clean water, not dirty water."),("Stop Bleeding","Press with clean cloth for 10 minutes, do not remove."),("Apply Betadine","Apply light Betadine, do not apply haldi / mud / toothpaste."),("Bandage","Tie clean bandage.")], ("साफ रखें","चोट को गंदा मत होने दें, रोज पट्टी बदलें।"), ("Keep Clean","Keep wound clean, change bandage daily."), "आपकी चोट को साफ रखना सबसे जरूरी है। गहरी चोट हो तो तुरंत अस्पताल जाएं।", "Keeping your wound clean is most important. For deep wound, go to hospital immediately.")),
    (["allergy","एलर्जी"], D("एलर्जी","Allergy", [("धूल / साबुन","धूल, नए साबुन या परफ्यूम से एलर्जी हो जाती है।"),("खाना","किसी खाने की चीज से एलर्जी हो सकती है।"),("दवा","किसी दवा से भी एलर्जी हो सकती है।")], [("Dust / Soap","Dust, new soap or perfume causes allergy."),("Food","Some food can cause allergy."),("Medicine","Some medicine can also cause allergy.")], [("सांस में दिक्कत","सांस में दिक्कत हो तो तुरंत 108 पर कॉल करें।"),("चेहरा सूजना","चेहरा या होंठ सूज जाएं तो तुरंत अस्पताल जाएं।")], [("Breathing Problem","If breathing problem, call 108 immediately."),("Face Swelling","If face or lips swell, go to hospital immediately.")], [("खुजलाएं नहीं","खुजलाएं नहीं।"),("ट्रिगर से दूर रहें","जिस चीज से एलर्जी हुई, उससे दूर रहें।"),("ठंडा पानी","ठंडे पानी से सेंक करें।")], [("Do Not Scratch","Do not scratch."),("Avoid Trigger","Stay away from the thing that caused allergy."),("Cold Water","Apply cold water compress.")], ("साफ कपड़े","रोज साफ कपड़े पहनें।"), ("Clean Clothes","Wear clean clothes daily."), "आपकी एलर्जी धूल या नए साबुन की वजह से लग रही है।", "Your allergy seems due to dust or new soap.")),
    (["chakkar","dizz","kamzori","weak","neend","sleep","चक्कर","कमजोरी","नींद"], D("चक्कर / कमजोरी / नींद","Dizziness / Weakness / Sleep", [("खून की कमी","खून की कमी से चक्कर आता है।"),("भूख","भूखे रहने से चक्कर आता है।"),("नींद की कमी","नींद पूरी न होने से कमजोरी लगती है।")], [("Low Blood","Low blood causes dizziness."),("Hunger","Staying hungry causes dizziness."),("Less Sleep","Less sleep causes weakness.")], [("बेहोश","बेहोश हो जाएं, तो तुरंत डॉक्टर को दिखाएं।"),("सीने में दर्द","चक्कर के साथ सीने में दर्द हो, तो 108 पर कॉल करें।")], [("Faint","If you faint, see doctor immediately."),("Chest Pain","If chest pain with dizziness, call 108.")], [("बैठ जाएं","चक्कर आए तो तुरंत बैठ जाएं।"),("पानी पिएं","थोड़ा-थोड़ा पानी पिएं।"),("कुछ खाएं","हल्का कुछ खा लें।")], [("Sit Down","Sit down immediately when dizzy."),("Drink Water","Drink water in small sips."),("Eat Something","Eat something light.")], ("पालक खाएं","रोज पालक और गुड़ खाएं।"), ("Eat Palak","Eat palak and gud daily."), "आपका चक्कर खून की कमी और नींद की कमी से लग रहा है।", "Your dizziness seems due to low blood and less sleep.")),
    (["diabetes","sugar","शुगर","madhumeh","thyroid","थायराइड"], D("शुगर / डायबिटीज / थायराइड","Diabetes / Sugar / Thyroid", [("खान-पान","मीठा ज्यादा खाने और मोटापे से शुगर बढ़ जाती है।"),("आनुवंशिक","माता-पिता को शुगर हो तो बच्चों को भी हो सकती है।"),("थायराइड","हार्मोन गड़बड़ होने से थायराइड होता है।")], [("Food Habits","Eating too much sweet and obesity increases sugar."),("Hereditary","If parents have sugar, children can also get it."),("Thyroid","Hormone imbalance causes thyroid.")], [("शुगर बहुत ज्यादा","शुगर 300 से ऊपर हो या बेहोश हो जाएं, तो तुरंत डॉक्टर को दिखाएं।"),("पैर में घाव","पैर में घाव हो जो ठीक न हो रहा हो, तो देर मत करें।")], [("Very High Sugar","If sugar above 300 or faint, see doctor immediately."),("Wound in Foot","If wound in foot not healing, do not wait.")], [("मीठा बंद","मीठा, कोल्ड ड्रिंक, मैदा बंद कर दें।"),("रोज टहलें","रोज 30 मिनट टहलें।"),("शुगर जांच","हफ्ते में 1 बार शुगर जांच करवाएं।")], [("Stop Sweet","Stop sweet, cold drink, maida."),("Daily Walk","Walk 30 minutes daily."),("Check Sugar","Check sugar once a week.")], ("करेला","करेला और मेथी शुगर में फायदेमंद हैं।"), ("Karela","Karela and methi are good for sugar."), "आपकी शुगर खान-पान और वजन की वजह से लग रही है, डॉक्टर से जांच करवाएं।", "Your sugar seems due to food habits and weight, get checked by doctor.")),
    (["bp","blood pressure","cholesterol","कोलेस्ट्रॉल","dil","dhadkan","heart"], D("बीपी / कोलेस्ट्रॉल / दिल","BP / Cholesterol / Heart", [("नमक ज्यादा","नमक ज्यादा खाने से बीपी बढ़ जाता है।"),("तनाव","ज्यादा टेंशन से बीपी बढ़ जाता है।"),("तेल","तला हुआ खाना खाने से कोलेस्ट्रॉल बढ़ता है।")], [("Too Much Salt","Eating too much salt increases BP."),("Stress","Too much tension increases BP."),("Oily Food","Fried food increases cholesterol.")], [("सीने में दर्द","सीने में दर्द + पसीना आए, तो तुरंत 108 पर कॉल करें।"),("बीपी बहुत ज्यादा","बीपी 180 से ऊपर हो, तो तुरंत डॉक्टर को दिखाएं।")], [("Chest Pain","If chest pain with sweating, call 108 immediately."),("Very High BP","If BP above 180, see doctor immediately.")], [("नमक कम","नमक और तेल कम कर दें।"),("टेंशन कम","टेंशन कम लें, रोज टहलें।"),("दवाई समय पर","बीपी की दवाई कभी मत छोड़ें।")], [("Less Salt","Reduce salt and oil."),("Less Stress","Take less tension, walk daily."),("Medicine On Time","Never miss BP medicine.")], ("रोज टहलें","रोज 30 मिनट टहलना बीपी के लिए सबसे अच्छी दवा है।"), ("Daily Walk","Walking 30 minutes daily is best medicine for BP."), "आपका बीपी नमक और टेंशन की वजह से लग रहा है, जांच करवाएं।", "Your BP seems due to salt and tension, get checked.")),
    (["anxiety","depression","stress","ghabrahat","घबराहट","udaasi","उदासी","yaadash","mirgi","daura","मिर्गी"], D("घबराहट / उदासी / स्ट्रेस / मिर्गी","Anxiety / Depression / Stress / Epilepsy", [("टेंशन","ज्यादा टेंशन लेने से घबराहट होती है।"),("नींद की कमी","नींद पूरी न होने से मन उदास रहता है।"),("अकेलापन","अकेले रहने से उदासी बढ़ जाती है।")], [("Tension","Taking too much tension causes anxiety."),("Less Sleep","Less sleep makes mind sad."),("Loneliness","Staying alone increases sadness.")], [("खुद को नुकसान","खुद को नुकसान का मन करे, तो तुरंत 14416 पर कॉल करें।"),("मिर्गी का दौरा","मिर्गी का दौरा 5 मिनट से ज्यादा रहे, तो तुरंत 108 पर कॉल करें।")], [("Self Harm","If you feel like harming yourself, call 14416 immediately."),("Epilepsy Attack","If epilepsy attack lasts more than 5 minutes, call 108.")], [("बात करें","किसी अपने से बात करें, अकेले मत रहें।"),("गहरी सांस","गहरी सांस लें, 10 मिनट टहलें।"),("फोन कम","सोने से पहले फोन बंद कर दें।")], [("Talk to Someone","Talk to someone close, do not stay alone."),("Deep Breathing","Take deep breath, walk 10 minutes."),("Less Phone","Switch off phone before sleeping.")], ("रोज टहलें","रोज सुबह टहलना मन को शांत करता है।"), ("Daily Walk","Morning walk calms mind."), "आपकी घबराहट टेंशन और नींद की कमी से लग रही है, किसी अपने से बात करें।", "Your anxiety seems due to tension and less sleep, talk to someone close.")),
    (["stone","pathri","पथरी","kidney","uti","peshaab","पेशाब","urine"], D("पथरी / पेशाब में जलन / UTI","Kidney Stone / UTI", [("पानी कम पीना","पानी कम पीने से पथरी बन जाती है।"),("नमक ज्यादा","नमक ज्यादा खाने से पथरी बनती है।"),("संक्रमण","साफ-सफाई न रखने से पेशाब में संक्रमण हो जाता है।")], [("Less Water","Drinking less water causes stone."),("Too Much Salt","Eating too much salt causes stone."),("Infection","Lack of cleanliness causes urine infection.")], [("पेशाब में खून","पेशाब में खून आए, तो तुरंत डॉक्टर को दिखाएं।"),("बहुत तेज दर्द","पेट में बहुत तेज दर्द हो, तो देर मत करें।")], [("Blood in Urine","If blood in urine, see doctor immediately."),("Severe Pain","If severe stomach pain, do not wait.")], [("पानी ज्यादा पिएं","दिन में 10-12 गिलास पानी पिएं।"),("नमक कम","नमक कम कर दें।"),("पेशाब रोकें नहीं","पेशाब को देर तक रोककर मत रखें।")], [("Drink More Water","Drink 10-12 glasses water daily."),("Less Salt","Reduce salt."),("Do Not Hold Urine","Do not hold urine for long.")], ("नींबू पानी","नींबू पानी पथरी में फायदेमंद है।"), ("Lemon Water","Lemon water is good for stone."), "आपकी पथरी / UTI पानी कम पीने की वजह से लग रही है।", "Your stone / UTI seems due to drinking less water.")),
    (["jaundice","piliya","पीलिया","liver","लीवर","hepatitis"], D("पीलिया / लीवर","Jaundice / Liver", [("गंदा पानी","गंदा पानी पीने से पीलिया हो जाता है।"),("शराब","शराब पीने से लीवर खराब हो जाता है।"),("तला खाना","ज्यादा तला खाना खाने से लीवर पर जोर पड़ता है।")], [("Dirty Water","Drinking dirty water causes jaundice."),("Alcohol","Drinking alcohol damages liver."),("Fried Food","Eating too much fried food puts pressure on liver.")], [("आंखें पीली","आंखें बहुत पीली हो जाएं, तो तुरंत डॉक्टर को दिखाएं।"),("पेट फूलना","पेट फूल जाए या उल्टी आए, तो देर मत करें।")], [("Yellow Eyes","If eyes become very yellow, see doctor immediately."),("Swollen Stomach","If stomach swells or vomiting, do not wait.")], [("हल्का खाना","खिचड़ी, दलिया, गन्ने का रस लें।"),("तला बंद","तला, मसालेदार, शराब बिल्कुल बंद।"),("आराम","पूरा आराम करें।")], [("Light Food","Eat khichdi, daliya, sugarcane juice."),("Stop Fried","Stop fried, spicy, alcohol totally."),("Full Rest","Take full rest.")], ("गन्ने का रस","गन्ने का रस पीलिया में बहुत फायदेमंद है।"), ("Sugarcane Juice","Sugarcane juice is very good in jaundice."), "आपका पीलिया गंदे पानी की वजह से लग रहा है, तुरंत जांच करवाएं।", "Your jaundice seems due to dirty water, get checked immediately.")),
    (["piles","bawasir","बवासीर","fissure","appendix","ulcer"], D("बवासीर / फिशर / अपेंडिक्स","Piles / Fissure / Appendix", [("कब्ज","लंबे समय तक कब्ज रहने से बवासीर हो जाती है।"),("ज्यादा बैठना","लंबी देर बैठने से बवासीर बढ़ जाती है।"),("मसालेदार","ज्यादा मिर्च-मसाला खाने से जलन बढ़ जाती है।")], [("Constipation","Long constipation causes piles."),("Sitting Too Long","Sitting for long increases piles."),("Spicy Food","Eating too much spicy food increases burning.")], [("बहुत खून","खून बहुत ज्यादा आए, तो तुरंत डॉक्टर को दिखाएं।"),("बहुत तेज दर्द","पेट में बहुत तेज दर्द हो, तो देर मत करें, अपेंडिक्स हो सकता है।")], [("Too Much Bleeding","If too much bleeding, see doctor immediately."),("Severe Pain","If severe stomach pain, do not wait, it can be appendix.")], [("पानी ज्यादा","दिन में 8-10 गिलास पानी पिएं।"),("फाइबर","हरी सब्जी, सलाद ज्यादा खाएं।"),("जोर मत लगाएं","पॉटी में जोर मत लगाएं।")], [("More Water","Drink 8-10 glasses water daily."),("Fiber","Eat green vegetables, salad more."),("Do Not Strain","Do not strain during stool.")], ("इसबगोल","रोज रात को इसबगोल लें।"), ("Isabgol","Take isabgol every night."), "आपकी बवासीर कब्ज की वजह से लग रही है।", "Your piles seem due to constipation.")),
    (["period","mahwari","माहवारी","pregnancy","garbh","गर्भ","pregnant","delivery","white discharge"], D("माहवारी / गर्भावस्था","Periods / Pregnancy", [("हार्मोन","हार्मोन गड़बड़ होने से माहवारी में दर्द होता है।"),("खून की कमी","खून की कमी से माहवारी में कमजोरी लगती है।"),("टेंशन","टेंशन से माहवारी आगे-पीछे हो जाती है।")], [("Hormone","Hormone imbalance causes periods pain."),("Low Blood","Low blood causes weakness in periods."),("Tension","Tension makes periods irregular.")], [("बहुत ज्यादा खून","बहुत ज्यादा खून आए या 7 दिन से ज्यादा चले, तो तुरंत डॉक्टर को दिखाएं।"),("गर्भ में दर्द","गर्भावस्था में पेट में तेज दर्द या खून आए, तो तुरंत अस्पताल जाएं।")], [("Too Much Bleeding","If too much bleeding or more than 7 days, see doctor immediately."),("Pain in Pregnancy","If severe pain or bleeding in pregnancy, go to hospital immediately.")], [("आराम","माहवारी में आराम करें, भारी काम मत करें।"),("गरम सेंक","पेट पर गरम पानी की बोतल से सेंक करें।"),("आयरन","पालक, गुड़, चुकंदर खाएं।")], [("Rest","Take rest in periods, do not do heavy work."),("Hot Compress","Apply hot water bottle on stomach."),("Iron","Eat palak, gud, beetroot.")], ("गरम पानी","गुनगुना पानी पीने से दर्द में आराम मिलता है।"), ("Warm Water","Drinking warm water gives relief in pain."), "आपकी माहवारी का दर्द हार्मोन और खून की कमी से लग रहा है।", "Your periods pain seems due to hormone and low blood.")),
    (["bachche","bachcha","baby","child","बच्च"], D("बच्चे की तकलीफ","Child Problem", [("मौसम","मौसम बदलने से बच्चे को जल्दी बुखार आ जाता है।"),("गंदा हाथ","गंदे हाथ से खाना खाने से बच्चे को दस्त हो जाते हैं।"),("दांत आना","दांत आने पर बच्चे को बुखार और दस्त हो जाते हैं।")], [("Weather","Change in weather causes fever in child quickly."),("Dirty Hands","Eating with dirty hands causes loose motion in child."),("Teething","When teeth come, child gets fever and loose motion.")], [("तेज बुखार","बच्चे को 102 से ऊपर बुखार हो, तो तुरंत डॉक्टर को दिखाएं।"),("दूध न पीना","बच्चा दूध न पी रहा हो या सुस्त हो, तो देर मत करें।")], [("High Fever","If child has fever above 102, see doctor immediately."),("Not Drinking Milk","If child is not drinking milk or is dull, do not wait.")], [("ओआरएस","बच्चे को थोड़ा-थोड़ा ओआरएस पिलाते रहें।"),("ठंडी पट्टी","सिर पर ठंडे पानी की पट्टी रखें।"),("हल्का खाना","खिचड़ी, दही जैसा हल्का खाना दें।")], [("ORS","Give ORS to child in small sips."),("Cold Cloth","Keep cold wet cloth on forehead."),("Light Food","Give light food like khichdi, curd.")], ("साफ-सफाई","बच्चे के हाथ बार-बार साबुन से धुलवाएं।"), ("Cleanliness","Wash child's hands with soap again and again."), "बच्चे की तकलीफ मौसम और साफ-सफाई की कमी से लग रही है।", "Child problem seems due to weather and cleanliness.")),
    (["malaria","मलेरिया","dengue","डेंगू","typhoid","टाइफाइड","tb","tuberculosis","टीबी","cancer","कैंसर","hiv","aids","pneumonia","nimoniya","निमोनिया","corona","tumor"], D("बड़ी बीमारी - मलेरिया / डेंगू / टाइफाइड / टीबी / कैंसर","Serious Disease - Malaria / Dengue / Typhoid / TB / Cancer", [("मच्छर","मच्छर काटने से मलेरिया और डेंगू होता है।"),("गंदा पानी","गंदा पानी पीने से टाइफाइड होता है।"),("संक्रमण","एक व्यक्ति से दूसरे व्यक्ति में फैलने से टीबी होता है।")], [("Mosquito","Mosquito bite causes malaria and dengue."),("Dirty Water","Drinking dirty water causes typhoid."),("Infection","Spreading from one person to another causes TB.")], [("तेज बुखार","बुखार 3 दिन से ज्यादा रहे, तो तुरंत डॉक्टर को दिखाएं।"),("खून","खून आए या सांस में दिक्कत हो, तो तुरंत 108 पर कॉल करें।")], [("High Fever","If fever stays more than 3 days, see doctor immediately."),("Blood","If blood comes or breathing problem, call 108 immediately.")], [("घर पर इलाज मत करें","इस बीमारी का घर पर इलाज मत करें, तुरंत सरकारी अस्पताल जाएं।"),("मच्छर से बचें","मच्छरदानी लगाएं, पानी जमा मत होने दें।"),("जांच करवाएं","तुरंत खून की जांच करवाएं।")], [("Do Not Treat At Home","Do not treat this disease at home, go to Govt hospital immediately."),("Avoid Mosquito","Use mosquito net, do not let water collect."),("Get Tested","Get blood test done immediately.")], ("सरकारी अस्पताल","इन बीमारियों का इलाज सरकारी अस्पताल में फ्री होता है।"), ("Govt Hospital","Treatment of these diseases is FREE in Govt hospital."), "ये बीमारी घर पर ठीक नहीं होती, तुरंत डॉक्टर को दिखाएं, देर मत करें।", "This disease cannot be cured at home, see doctor immediately, do not wait.", serious=True)),
    (["paralysis","lakwa","लकवा","tumor","vitamin","infection","bacteria","virus","haddi","nas","dimaag","brain","heart","lung","fefe"], D("दिमाग / नस / हड्डी / फेफड़े की तकलीफ","Brain / Nerve / Bone / Lung Problem", [("खून की कमी","खून की कमी से नसों में कमजोरी आ जाती है।"),("चोट","चोट लगने से नस दब जाती है।"),("संक्रमण","वायरस / बैक्टीरिया से संक्रमण हो जाता है।")], [("Low Blood","Low blood causes weakness in nerves."),("Injury","Injury presses nerve."),("Infection","Virus / Bacteria causes infection.")], [("लकवा","एक तरफ हाथ-पैर काम न करे, तो तुरंत 108 पर कॉल करें।"),("बेहोश","बेहोश हो जाएं, तो तुरंत अस्पताल जाएं।")], [("Paralysis","If one side hand-leg stops working, call 108 immediately."),("Faint","If faint, go to hospital immediately.")], [("आराम","पूरी तरह आराम करें, भारी काम मत करें।"),("तुरंत अस्पताल","लकवा / ट्यूमर में देर मत करें, तुरंत अस्पताल जाएं।"),("पानी","दिन भर गुनगुना पानी पिएं।")], [("Full Rest","Take full rest, do not do heavy work."),("Go To Hospital Immediately","In paralysis / tumor, do not wait, go to hospital immediately."),("Water","Drink warm water through the day.")], ("तुरंत जांच","ऐसी तकलीफ में तुरंत CT / MRI जांच करवाएं।"), ("Immediate Checkup","In such problem, get CT / MRI done immediately."), "आपकी तकलीफ नस / दिमाग से जुड़ी लग रही है, तुरंत डॉक्टर को दिखाएं।", "Your problem seems related to nerve / brain, see doctor immediately.")),
]

def make_answer_from_disease(disease, lang):
    if lang == "Hindi":
        c = "\n".join([f"- **{a}:** {b}" for a,b in disease["causes_hi"]])
        d = "\n".join([f"- **{a}:** {b}" for a,b in disease["dangers_hi"]])
        w = "\n".join([f"- **{a}:** {b}" for a,b in disease["dos_hi"]])
        if disease.get("serious"):
            return f"""⚠️ **ये बड़ी बीमारी है, घर पर इलाज मत कीजिए।**

**संभावित कारण - {disease['hi']} की वजह:**

{c}

**खतरे के लक्षण:**

{d}

**अभी क्या करें:**

{w}

**स्वास्थ्य टिप:**

- **{disease['tip_hi'][0]}:** {disease['tip_hi'][1]}

{disease['sum_hi']}

**तुरंत सरकारी अस्पताल जाएं, वहां इलाज फ्री होता है। 108 पर कॉल करें।**

क्या आप डॉक्टर से बात करना चाहेंगी?"""
        return f"""आपकी तकलीफ समझ सकते हैं, आराम कीजिए।

**संभावित कारण - {disease['hi']} की वजह:**

{c}

**खतरे के लक्षण:**

{d}

**अभी क्या करें:**

{w}

**स्वास्थ्य टिप:**

- **{disease['tip_hi'][0]}:** {disease['tip_hi'][1]}

{disease['sum_hi']}

क्या आप डॉक्टर से बात करना चाहेंगी?"""
    else:
        c = "\n".join([f"- **{a}:** {b}" for a,b in disease["causes_en"]])
        d = "\n".join([f"- **{a}:** {b}" for a,b in disease["dangers_en"]])
        w = "\n".join([f"- **{a}:** {b}" for a,b in disease["dos_en"]])
        if disease.get("serious"):
            return f"""⚠️ **This is a serious disease, do not treat at home.**

**Possible Causes - Why {disease['en']} happens:**

{c}

**Danger Signs:**

{d}

**What To Do Now:**

{w}

**Health Tip:**

- **{disease['tip_en'][0]}:** {disease['tip_en'][1]}

{disease['sum_en']}

**Go to Govt hospital immediately, treatment is FREE there. Call 108.**

Would you like to see a doctor?"""
        return f"""I understand, please take rest.

**Possible Causes - Why {disease['en']} happens:**

{c}

**Danger Signs:**

{d}

**What To Do Now:**

{w}

**Health Tip:**

- **{disease['tip_en'][0]}:** {disease['tip_en'][1]}

{disease['sum_en']}

Would you like to see a doctor?"""

def get_instant_answer(user_text, lang):
    text = user_text.lower()
    for keywords, disease in DISEASES:
        for kw in keywords:
            if kw.lower() in text:
                return make_answer_from_disease(disease, lang)
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

if menu in ["🏠 Home", "🏠 होम"]:
    st.markdown(f"""<div class="ai-header"><h1>🩺 Sehat Saathi</h1><p>{T('आपका एआई हेल्थ असिस्टेंट - अपनी तकलीफ लिखें, तुरंत सलाह पाएं','Your AI Health Assistant - Write your symptom, get instant advice')}</p></div>""", unsafe_allow_html=True)
    st.write(T("नमस्ते, मैं यहाँ आपकी मदद करने के लिए हूँ!","Hello, I am here to help you!"))
    st.write(T("अपनी तकलीफ लिखें, बोलें या फोटो भेजें।","Write your problem, speak or send photo."))
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            if m.get("content") == "DOCTORS_BOX":
                show_doctor_detail_card(m.get("for_text",""), m.get("loc", st.session_state.doctor_location))
            elif m.get("type") == "image":
                st.image(m["image"], caption=T("📸 आपकी फोटो","📸 Your Photo"), use_container_width=True)
                st.markdown(m["content"])
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
    with st.form("chat_form", clear_on_submit=True):
        chat_text = st.text_input("Type...", label_visibility="collapsed", placeholder=T("अपनी तकलीफ लिखें... जैसे शुगर, बीपी, अस्थमा, बवासीर, पथरी...","Write your symptom... like sugar, BP, asthma, piles, stone..."), value="")
        submitted = st.form_submit_button(T("➤ भेजें","➤ Send"), use_container_width=True)
    if submitted and chat_text.strip() != "":
        st.session_state.messages.append({"role": "user", "content": chat_text})
        st.session_state.doctor_asked = False
        st.session_state.doctor_step = "none"
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
        photo_desc = st.text_input(T("फोटो में क्या दिख रहा है?","What is visible in photo? (optional)"), value="", placeholder=T("जैसे: हाथ पर लाल दाने...","Like: red rash on hand..."), key="photo_desc")
        if st.button(T("📸 फोटो भेजें","📸 Send Photo"), use_container_width=True):
            if "चोट" in photo_type or "Injury" in photo_type:
                kw = "चोट जख्म" if IS_HINDI else "chot zakhm"
            elif "खुजली" in photo_type or "Itching" in photo_type:
                kw = "खुजली दाने" if IS_HINDI else "khujli rash"
            else:
                kw = "एलर्जी दाने" if IS_HINDI else "allergy daane"
            photo_text = f"{kw} {photo_desc}".strip()
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
            st.success(T(f"🗣️ आपने बोला: {voice_text}", f"🗣️ You said: {voice_text}"))
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

elif menu in ["💊 Medicine Reminder", "💊 दवाई रिमाइंडर"]:
    st.title(T("💊 दवाई रिमाइंडर","💊 Medicine Reminder"))
    st.write(T("दवाई का समय सेट कीजिए, समय होने पर ऐप याद दिलाएगा।","Set medicine time, app will remind you."))
    with st.form("reminder_form"):
        med_name = st.text_input(T("दवाई का नाम","Medicine Name"), value="", placeholder=T("दवाई का नाम लिखें...","Write medicine name..."))
        st.write(T("समय","Time"))
        c_h, c_m, c_ap = st.columns(3)
        with c_h:
            hour = st.selectbox(T("घंटा","Hour"), list(range(1, 13)), index=None, placeholder=T("घंटा","Hour"))
        with c_m:
            minute = st.selectbox(T("मिनट","Minute"), [f"{i:02d}" for i in range(0, 60)], index=None, placeholder=T("मिनट","Minute"))
        with c_ap:
            ampm = st.radio("AM / PM", ["AM", "PM"], horizontal=True)
        med_days = st.number_input(T("कितने दिन तक?","How many days?"), min_value=1, max_value=30, value=None, placeholder=T("दिन लिखें...","Write days..."))
        if st.form_submit_button(T("✅ रिमाइंडर सेट करें","✅ Set Reminder"), use_container_width=True):
            if med_name.strip() == "" or hour is None or minute is None or med_days is None:
                st.warning(T("पहले दवाई का नाम, समय और दिन लिखिए","First write medicine name, time and days"))
            else:
                hour_24 = hour % 12
                if ampm == "PM":
                    hour_24 += 12
                if ampm == "AM" and hour == 12:
                    hour_24 = 0
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
    talk_symptom = st.text_input(T("अपनी तकलीफ लिखें","Write Your Problem"), value="", placeholder=T("जैसे: शुगर, बीपी, अस्थमा, बवासीर, पथरी","Like: sugar, BP, asthma, piles, stone"), key="talk_symptom")
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
    em_text = st.text_input(T("इमरजेंसी लिखें...","Write emergency..."), value="", placeholder=T("इमरजेंसी लिखें - जैसे हाथ कट गया...","Write emergency - like hand cut..."), key="em_text")
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
        elif "कट" in e or "खून" in e or "blood" in e or "चोट" in e or "cut" in e:
            st.error(T("**कट / खून - एम्बुलेंस आने तक:**\n1. 108 पर कॉल करें\n2. साफ कपड़े से ज़ोर से दबाएं\n3. हाथ / पैर ऊपर रखें\n4. मरीज़ को हिलाएं नहीं","**CUT / BLEEDING - Till Ambulance Arrives:**\n1. Call 108\n2. Press firmly with clean cloth\n3. Keep hand / leg up"))
        elif "सांस" in e or "breath" in e or "गला" in e or "choke" in e:
            st.error(T("**सांस की समस्या - एम्बुलेंस आने तक:**\n1. 108 पर कॉल करें\n2. मरीज़ को सीधा बैठाएं\n3. गले के कपड़े ढीले कर दें\n4. खिड़की खोल दें","**BREATHING PROBLEM - Till Ambulance Arrives:**\n1. Call 108\n2. Make patient sit straight\n3. Loosen clothes around neck"))
        elif "बुखार" in e or "fever" in e:
            st.error(T("**तेज़ बुखार - एम्बुलेंस आने तक:**\n1. ठंडी पट्टी रखें\n2. भारी कपड़े हटा दें\n3. थोड़ा-थोड़ा पानी पिलाते रहें","**HIGH FEVER - Till Ambulance Arrives:**\n1. Keep cold wet cloth\n2. Remove heavy blanket\n3. Give water in small sips"))
        elif "उल्टी" in e or "vomit" in e:
            st.error(T("**उल्टी - एम्बुलेंस आने तक:**\n1. मरीज़ को एक तरफ लिटाएं\n2. थोड़ा-थोड़ा ओआरएस पिलाएं\n3. खाना मत दें","**VOMITING - Till Ambulance Arrives:**\n1. Make patient lie on one side\n2. Give ORS in small sips"))
        elif "बेहोश" in e or "faint" in e:
            st.error(T("**बेहोश - एम्बुलेंस आने तक:**\n1. सांस चेक करें\n2. सांस चल रही है तो एक तरफ लिटाएं\n3. पानी / खाना मत पिलाएं\n4. तुरंत 108 पर कॉल करें","**UNCONSCIOUS - Till Ambulance Arrives:**\n1. Check breathing\n2. If breathing, lie on one side\n3. Do not give water / food\n4. Call 108 immediately"))
        else:
            st.error(T("**इमरजेंसी - एम्बुलेंस आने तक:**\n1. घबराएं नहीं, 108 पर कॉल करें\n2. मरीज़ को सीधा लिटाएं\n3. खून आ रहा है तो साफ कपड़े से दबाएं","**EMERGENCY - Till Ambulance Arrives:**\n1. Do not panic, call 108\n2. Lay patient straight\n3. If bleeding, press with clean cloth"))
    st.markdown("---")
    st.markdown(f"### {T('🆘 इमरजेंसी टिप्स','🆘 Emergency Tips')}")
    st.write(T("- **चोट:** साफ कपड़े से दबाएं, हल्दी / मिट्टी मत लगाएं","- **Injury:** Press with clean cloth, do not apply haldi / mud"))
    st.write(T("- **सांस:** सीधा बैठाएं, कपड़े ढीले करें","- **Breathing:** Sit straight, loosen clothes"))
    st.write(T("- **बुखार:** ठंडी पट्टी, थोड़ा-थोड़ा पानी","- **Fever:** Cold cloth, water in small sips"))
    st.write(T("- **बेहोश:** पानी मत पिलाएं, एक तरफ लिटाएं, 108 पर कॉल करें","- **Unconscious:** Do not give water, lie on side, call 108"))
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
    weight = st.number_input(T("वज़न (kg)","Weight (kg)"), min_value=10.0, max_value=200.0, value=None, placeholder=T("वज़न लिखें...","Write weight..."))
    height = st.number_input(T("ऊंचाई (cm)","Height (cm)"), min_value=100.0, max_value=220.0, value=None, placeholder=T("ऊंचाई लिखें...","Write height..."))
    if st.button(T("हिसाब लगाएं","Calculate")):
        if weight is None or height is None:
            st.warning(T("पहले वज़न और ऊंचाई लिखिए","First write weight and height"))
        else:
            h_m = height / 100
            bmi = weight / (h_m * h_m)
            st.success(f"आपका बीएमआई: {bmi:.1f}" if IS_HINDI else f"Your BMI: {bmi:.1f}")
            if bmi < 18.5:
                st.write(T("कम वज़न - स्वस्थ खाना खाएं","Underweight - Eat healthy food"))
            elif bmi < 25:
                st.write(T("सामान्य - बहुत बढ़िया!","Normal - Good! Keep it up"))
            elif bmi < 30:
                st.write(T("ज्यादा वज़न - रोज़ टहलें","Overweight - Walk daily"))
            else:
                st.write(T("मोटापा - डॉक्टर से बात करें","Obese - Please consult doctor"))
    show_floating_banner()

elif menu in ["🏛️ Government Schemes", "🏛️ सरकारी योजनाएं"]:
    st.title(T("🏛️ सरकारी योजनाएं - फ्री का फायदा उठाएं","🏛️ Government Schemes - Take FREE Benefit"))
    st.success(T("ये सब सरकारी योजनाएं हैं, 100% असली और फ्री। किसी को पैसे मत दें।","All these are Government schemes, 100% Real and FREE. Do not pay money to anyone."))
    st.markdown(f"### {T('1. 🩺 आयुष्मान भारत - पीएमजेएवाई','1. 🩺 Ayushman Bharat - PMJAY')}")
    st.write(T("- **क्या मिलता है:** 5 लाख तक का फ्री इलाज, हर साल, पूरे परिवार के लिए","- **Benefit:** FREE treatment up to 5 Lakh, every year, for whole family"))
    st.write(T("- **क्या चाहिए:** आधार कार्ड + राशन कार्ड","- **Need:** Aadhaar Card + Ration Card"))
    st.link_button(T("आयुष्मान कार्ड चेक करें","Check Ayushman Card"), "https://pmjay.gov.in", use_container_width=True)
    st.markdown("---")
    st.markdown(f"### {T('2. 💊 जन औषधि - सस्ती दवाई','2. 💊 Jan Aushadhi - Cheap Medicines')}")
    st.write(T("- **क्या मिलता है:** दवाई 50% से 90% तक सस्ती मिलती है","- **Benefit:** Medicines 50% to 90% cheaper"))
    st.write(T("- **कौन ले सकता है:** कोई भी, सबके लिए है","- **Who Can Get:** Anyone, for everyone"))
    st.link_button(T("नज़दीकी जन औषधि केंद्र ढूंढें","Find Nearest Jan Aushadhi Kendra"), "https://janaushadhi.gov.in", use_container_width=True)
    st.markdown("---")
    st.markdown(f"### {T('3. 🤰 पीएम सुरक्षित मातृत्व - गर्भवती महिला','3. 🤰 PM Surakshit Matritva - Pregnant Women')}")
    st.write(T("- **क्या मिलता है:** गर्भवती महिला की फ्री जांच, फ्री दवाई, फ्री अल्ट्रासाउंड","- **Benefit:** FREE checkup, FREE medicine, FREE ultrasound for pregnant women"))
    st.write(T("- **कब:** हर महीने की 9 तारीख को पीएचसी में फ्री जांच होती है","- **When:** On 9th of every month, FREE checkup in PHC"))
    st.markdown("---")
    st.markdown(f"### {T('4. 👶 मिशन इंद्रधनुष - बच्चों के टीके','4. 👶 Mission Indradhanush - Children Vaccines')}")
    st.write(T("- **क्या मिलता है:** बच्चों के सारे टीके बिल्कुल फ्री","- **Benefit:** All vaccines of children totally FREE"))
    st.write(T("- **कहां मिलेगा:** गांव के आंगनवाड़ी / पीएचसी में","- **Where:** Village Anganwadi / PHC"))
    st.markdown("---")
    st.markdown(f"### {T('5. 👵 पीएम वय वंदना - बुजुर्गों के लिए','5. 👵 PM Vaya Vandana - For Elderly')}")
    st.write(T("- **क्या मिलता है:** 60 साल से ऊपर के बुजुर्गों को हर महीने पेंशन जैसा पैसा मिलता है","- **Benefit:** Elderly above 60 years get monthly pension-like money"))
    st.markdown("---")
    st.markdown(f"### {T('6. 🦟 राष्ट्रीय स्वास्थ्य मिशन - फ्री जांच','6. 🦟 National Health Mission - FREE Checkup')}")
    st.write(T("- **क्या मिलता है:** पीएचसी में बीपी, शुगर, बुखार, मलेरिया की जांच बिल्कुल फ्री","- **Benefit:** BP, Sugar, Fever, Malaria checkup totally FREE in PHC"))
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
    st.write(T("- **💊 दवाई रिमाइंडर:** दवाई का समय सेट कीजिए","- **💊 Medicine Reminder:** Set medicine time"))
    st.write(T("- **👨‍⚕️ डॉक्टर से बात करें:** सरकारी डॉक्टर, ई-संजीवनी और 104 हेल्पलाइन","- **👨‍⚕️ Talk To Doctor:** Govt doctor, eSanjeevani and 104 helpline"))
    st.write(T("- **🚨 आपातकाल:** इमरजेंसी में क्या करना है, किस नंबर पर कॉल करना है","- **🚨 Emergency:** What to do in emergency, which number to call"))
    st.write(T("- **💡 स्वास्थ्य टिप्स:** रोज़ का रूटीन, खाना-पीना, नींद, टहल","- **💡 Health Tips:** Daily routine, food, sleep, walk"))
    st.write(T("- **⚖️ बीएमआई कैलकुलेटर:** अपना वज़न सही है या नहीं","- **⚖️ BMI Calculator:** Check if your weight is correct"))
    st.write(T("- **🏛️ सरकारी योजनाएं:** आयुष्मान, जन औषधि जैसी योजनाओं की जानकारी फ्री में","- **🏛️ Government Schemes:** Ayushman, Jan Aushadhi info FREE"))
    st.markdown("---")
    st.info(T("⚠️ **ज़रूरी बात:** यह ऐप सिर्फ जानकारी और पहली मदद के लिए है। यह डॉक्टर की जगह नहीं ले सकता। अगर तकलीफ ज़्यादा है, तो तुरंत डॉक्टर को दिखाएं या 108 पर कॉल करें।","⚠️ **Important:** This app is only for information and first help. It cannot replace a doctor. If problem is more, see doctor immediately or call 108."))
    show_floating_banner()
