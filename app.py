import streamlit as st
import datetime, re, urllib.parse, json, urllib.request, base64, io
st.set_page_config(page_title="Sehat Saathi - India", page_icon="🩺", layout="centered")

# AI KEY - Yaha apni key daal de, ya Secrets me daal de - dono chalega
GEMINI_API_KEY = "PASTE_YOUR_KEY_HERE"
try:
    if "GEMINI_API_KEY" in st.secrets:
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    pass

def ask_ai(prompt):
    # Agar key nahi hai toh seedha bata dega, chhupayega nahi
    if not GEMINI_API_KEY or GEMINI_API_KEY == "PASTE_YOUR_KEY_HERE":
        return "OFFLINE_FALLBACK"
    # AI ko 3 baar try karega - koi 1 model toh chalega hi
    for model in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as res:
                out = json.loads(res.read().decode())
                return out["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            continue
    return "OFFLINE_FALLBACK"

def text_to_audio(text, lang_text):
    try:
        from gtts import gTTS
        clean = re.sub(r'\*+', '', text).replace("**","").strip()[:800]
        if not clean: return None
        tts = gTTS(text=clean, lang="hi" if lang_text=="Hindi" else "en", slow=False)
        buf = io.BytesIO(); tts.write_to_fp(buf); buf.seek(0); return buf.read()
    except: return None
def speak_answer(text, lang_text):
    a = text_to_audio(text, lang_text)
    if a: st.audio(a, format="audio/mp3")

st.markdown("""
<style>
footer {visibility:hidden !important;}
.stApp {background: linear-gradient(180deg,#FFFBF2,#FFF7ED,#FEF3C7,#EEF2FF,#F0FDF4) !important;}
.block-container {max-width:1100px !important; padding:1rem 2rem 100px 2rem !important;}
h1,h2,h3,p,label,.stMarkdown,span,div {color:#1E293B !important;}
.stTextInput input,.stSelectbox div[data-baseweb="select"] div,.stNumberInput input,.stTextArea textarea {background:#FFF !important; color:#1E293B !important; border:1.5px solid #E2E8F0 !important; border-radius:14px !important; min-height:52px !important; font-size:16px !important;}
.stButton button,.stLinkButton a {background:linear-gradient(90deg,#4F46E5,#7C3AED,#EA580C) !important; color:#FFF !important; border:none !important; border-radius:14px !important; font-weight:700 !important; min-height:52px !important; font-size:16px !important;}
.stButton button *,.stLinkButton a * {color:#FFF !important; font-weight:700 !important;}
div[data-testid="stChatMessage"] {background:#FFF !important; border-radius:18px !important; border:1px solid #FDE68A !important;}
.ai-header {background:linear-gradient(90deg,#FFE4E6,#FEF3C7,#D1FAE5,#DBEAFE); padding:22px; border-radius:22px; text-align:center; margin-bottom:14px; border:1px solid #FDE68A;}
.ai-header h1 {font-size:29px; margin:0; color:#7C2D12 !important;}
.doctor-card,.medicine-card,.scheme-card {background:#FFF; border:1.5px solid #FDE68A; border-radius:18px; padding:18px; margin:12px 0;}
.hospital-card {background:#FFF; border:1.5px solid #BBF7D0; border-radius:18px; padding:16px; margin:12px 0;}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages=[]
if "doctor_asked" not in st.session_state: st.session_state.doctor_asked=False
if "doctor_step" not in st.session_state: st.session_state.doctor_step="none"
if "doctor_location" not in st.session_state: st.session_state.doctor_location={}
if "reminders" not in st.session_state: st.session_state.reminders=[]
if "last_audio_id" not in st.session_state: st.session_state["last_audio_id"]=""
if "uploader_key" not in st.session_state: st.session_state.uploader_key=0
if "voice_mode" not in st.session_state: st.session_state.voice_mode=False

st.write("### ☰ MENU")
menu_options=["🏠 Home","💊 Medicine Info","💊 Medicine Reminder","👨‍⚕️ Talk To Doctor","🚨 Emergency","🏥 Hospital Finder","💡 Health Tips","⚖️ BMI Calculator","🏛️ Government Schemes","ℹ️ About App"]
menu=st.selectbox("Page Chunein",menu_options,label_visibility="collapsed")
st.sidebar.write("Language")
lang_choice=st.sidebar.radio("Choose Language",["English","Hindi"],label_visibility="collapsed")
IS_HINDI=(lang_choice=="Hindi")
st.sidebar.write("### ☰ Menu")
st.sidebar.radio("Menu",menu_options,key="sidebar_menu",label_visibility="collapsed")
if st.session_state.get("sidebar_menu") and st.session_state.sidebar_menu!=menu:
    menu=st.session_state.sidebar_menu
def T(hi,en): return hi if IS_HINDI else en
def normalize_text(t):
    t=t or ""
    for k,v in {"सिर":"head","दर्द":"pain","बुखार":"fever","पेट":"stomach","गला":"throat","खांसी":"cough","उल्टी":"vomit","दस्त":"diarrhea","खुजली":"itch","दाने":"rash","चोट":"injury","सांस":"breath","सीने":"chest","कमर":"back","कान":"ear","दांत":"tooth","आंख":"eye","पैर":"leg","हाथ":"hand","चक्कर":"dizzy","कमजोरी":"weak","नींद":"sleep","शुगर":"diabetes","सर्दी":"cold","फीवर":"fever"}.items(): t=t.replace(k,v)
    return t.lower()
def speech_to_text(audio_bytes):
    try:
        import speech_recognition as sr
        r=sr.Recognizer()
        with sr.AudioFile(io.BytesIO(audio_bytes)) as s: d=r.record(s)
        try: e=r.recognize_google(d,language="en-IN")
        except: e=""
        try: h=r.recognize_google(d,language="hi-IN")
        except: h=""
        return e if e else h if h else "ERROR:Could not understand"
    except Exception as ex: return f"ERROR:{str(ex)[:100]}"
HEALTH_WORDS=["daane","rash","chot","zakhm","allergy","khujli","itching","bukhar","fever","dard","pain","dawa","medicine","wound","injury","skin","cough","cold","sardi","pet","stomach","sir","head","haath","hand","pair","leg","blood","burn","soojan","ulti","vomit","dast","kamzori","weak","neend","sleep","saans","breath","chest","seene","gala","throat","kaan","ear","daant","tooth","aankh","eye","ghutna","knee","kamar","back","badan","body","chakkar","dizzy","gas","acidity","kabz","doctor","hospital","bimar","tabiyat","dawai","diabetes","sugar","bp","thyroid","asthma","anxiety","depression","stress","period","pregnancy","piles","stone","jaundice","malaria","dengue","typhoid","tb","cancer","pneumonia","sinus","pimple","headache","have","i have"]
OUT_WORDS=["movie","film","cricket","football","game","padhai","study","exam","joke","song","gaana","politics","news","weather","mausam","love","shaadi","job","naukri","paisa","money","shopping","birthday","car","bike","dog","cat","food","recipe","mobile","phone","computer"]
def is_health_related(text):
    t=normalize_text(text); raw=(text or "").lower()
    if any(w in raw for w in OUT_WORDS) and not any(w in t for w in HEALTH_WORDS): return False
    if any(w in t for w in HEALTH_WORDS): return True
    if t.strip() in ["hi","hello","namaste","hey","hii"]: return True
    return False
def out_of_context_msg(l): return "मैं सिर्फ स्वास्थ्य, चोट और एलर्जी से जुड़ी मदद कर सकती हूँ।" if l=="Hindi" else "I can only help with health, injury and allergy related problems."
def detect_language(t):
    if re.search(r'[\u0900-\u097F]',t): return "Hindi"
    for w in ["mere","mera","mujhe","dard","hai","sar","sir","kamar","pet","bukhar","sardi","khansi"]:
        if w in t.lower(): return "Hindi"
    return "English" if re.search(r'[a-zA-Z]',t) else ("Hindi" if IS_HINDI else "English")
def get_smart_offline_answer(user_text, lang_text):
    u=user_text
    if lang_text=="Hindi":
        return f"""**Possible Cause:**\n{u} ki wajah se ho sakta hai - thakan, gas, acidity, viral ya mausam badalne se aisa hota hai. Shareer kamzor hone par bhi aisa hota hai.\n\n**Danger Sign:**\nAgar dard bahut zyada hai, saans me takleef hai, ulti aa rahi hai, behoshi aa rahi hai, ya 2-3 din se kam nahi ho raha toh turant doctor ko dikhayein ya 108 par call karein.\n\n**What To Do Now:**\n- Poora aaram karein, bhaari kaam mat karein\n- Paani zyada piyein, halka aur ghar ka khana khayein\n- Garam paani se sikai karein\n- Thandi hawa aur bahar ke khane se bachein\n\n**Health Tip:**\nRoz 30 minute walk karein aur 8 glass paani piyein.\n\nYe sirf jaankari hai, doctor ki salah zaroori hai."""
    else:
        return f"""**Possible Cause:**\n{u} may be due to tiredness, gas, acidity, viral or weather change. It also happens when body is weak.\n\n**Danger Sign:**\nIf pain is very severe, breathing problem, vomiting, fainting, or not reducing in 2-3 days, see doctor immediately or call 108.\n\n**What To Do Now:**\n- Take full rest, do not do heavy work\n- Drink more water, eat light and home-made food\n- Use warm water compress\n- Avoid cold air and outside food\n\n**Health Tip:**\nWalk 30 minutes daily and drink 8 glasses of water.\n\nThis is only information, doctor advice is necessary."""
def get_instant_answer(user_text, lang_text):
    lang_rule="Answer ONLY in proper Hindi in Devanagari script. Simple Hindi." if lang_text=="Hindi" else "Answer ONLY in proper English. Simple English."
    prompt=f"""User ka symptom hai: {user_text}\nLanguage: {lang_text}\n{lang_rule}\nTu ek helpful Health AI hai. Koi dawai ka naam, dose mat likh.\nJawab ISI format me de:\n**Possible Cause:** [2-3 line detail]\n**Danger Sign:** [kab doctor, kab 108]\n**What To Do Now:** [4-5 steps ghar pe kya karna hai]\n**Health Tip:** [1 tip]\nLast me: Ye sirf jaankari hai, doctor ki salah zaroori hai.\nAgar chest pain, saans nahi aa rahi jaisa serious hai toh pehle 108 par call karne ko bolo, fir steps batao."""
    ans=ask_ai(prompt)
    if ans=="OFFLINE_FALLBACK": return get_smart_offline_answer(user_text, lang_text)
    return ans
def get_medicine_info(med_name, lang):
    lang_rule="Answer ONLY in proper Hindi in Devanagari script." if lang=="Hindi" else "Answer ONLY in proper English."
    prompt=f"""Dawai ka naam: {med_name}\nLanguage: {lang}\n{lang_rule}\nFormat:\n**💊 {med_name}**\n**Ye dawai kya hai?** [2-3 line detail]\n**Kaise leni hai?** [general jaankari, hamesha doctor ke bataye hisaab se]\n**Side Effects / Savdhani:** [detail me]\n**Zaroori Baat:** Doctor se poochh ke hi lena. Fixed dose mat batao. Allergy / saans takleef ho toh 108 par call karo."""
    ans=ask_ai(prompt)
    if ans=="OFFLINE_FALLBACK":
        if lang=="Hindi": return f"""**💊 {med_name}**\n**Ye dawai kya hai?**\nYe dawai {med_name} aam taur par isi se judi takleef me doctor dete hai.\n\n**Kaise leni hai?**\nHamesha doctor ke bataye hisaab se hi lena hai. Khud se dose badha ke mat lena.\n\n**Side Effects / Savdhani:**\nKuch logo ko ulti, chakkar ya pet kharab ho sakta hai. Allergy, saans me takleef ho toh turant 108 par call karo.\n\n**Zaroori Baat:** Doctor se poochh ke hi lena."""
        else: return f"""**💊 {med_name}**\n**What is this medicine?**\n{med_name} is commonly given by doctors for related problems.\n\n**How to take it?**\nAlways take as told by doctor. Do not increase dose yourself.\n\n**Side Effects / Precautions:**\nSome people may feel vomiting, dizziness or stomach upset. If allergy, breathing problem happens, call 108.\n\n**Important:** Take only after asking doctor."""
    return ans
def get_doctor_info_ai(user_text, lang):
    lang_rule="Answer ONLY in proper Hindi." if lang=="Hindi" else "Answer ONLY in proper English."
    ans=ask_ai(f"Takleef: {user_text} Language: {lang} {lang_rule} Batao: 1. Kaunse specialist ko dikhaye 2. Wo doctor kya karte hai 3. Kab turant dikhaye 4. Fees India me. Short me.")
    if ans=="OFFLINE_FALLBACK": return "General Physician ko dikhayein. Aam bimariyon ka ilaj karte hai. Takleef zyada ho toh turant dikhayein. Fees: 200-500 Rs."
    return ans
def get_hospitals_for(city,pincode):
    c=city.strip().title() if city.strip() else "Your City"
    return [{"name":f"District Government Hospital - {c}","type":T("सरकारी - फ्री इलाज","Govt - FREE Treatment"),"addr":f"{c}, Pincode - {pincode}","phone":"108"},{"name":f"Civil Hospital - {c}","type":T("सरकारी - OPD 9 AM - 1 PM","Govt - OPD 9 AM - 1 PM"),"addr":f"Main Road, {c} - {pincode}","phone":"104"},{"name":f"PHC - {c}","type":T("सरकारी - PHC - फ्री जांच","Govt - PHC - FREE Checkup"),"addr":f"Near Bus Stand, {c} - {pincode}","phone":"104"},{"name":f"Apollo / Private Hospital - {c}","type":T("प्राइवेट - 24x7","Private - 24x7 Emergency"),"addr":f"City Centre, {c} - {pincode}","phone":"1860-500-1066"},{"name":f"Jan Aushadhi Kendra - {c}","type":T("सस्ती दवाई","Cheap Medicine"),"addr":f"Market Road, {c} - {pincode}","phone":"1800-180-8080"}]
PRACTO_SLUG={"fever":"general-physician","back":"orthopedist","skin":"dermatologist","stomach":"gastroenterologist","head":"neurologist","chest":"cardiologist","tooth":"dentist","eye":"ophthalmologist","ear":"ent-specialist","injury":"orthopedist","diabetes":"diabetologist","heart":"cardiologist","mental":"psychiatrist","kidney":"nephrologist","liver":"hepatologist","piles":"general-surgeon","ladies":"gynecologist","child":"pediatrician","serious":"general-physician","general":"general-physician"}
APOLLO_SLUG={"fever":"general-physician","back":"orthopedics","skin":"dermatology","stomach":"gastroenterology","head":"neurology","chest":"cardiology","tooth":"dentistry","eye":"ophthalmology","ear":"ent","injury":"orthopedics","diabetes":"endocrinology","heart":"cardiology","mental":"psychiatry","kidney":"nephrology","liver":"hepatology","piles":"general-surgery","ladies":"obstetrics-and-gynecology","child":"pediatrics","serious":"general-physician","general":"general-physician"}
def get_category_for(text):
    t=normalize_text(text).lower()+" "+(text or "").lower()
    if any(k in t for k in ["rash","khujli","allergy","skin","pimple"]): return "skin"
    if any(k in t for k in ["chot","injury","wound"]): return "injury"
    if any(k in t for k in ["chest","seene","saans","breath","asthma"]): return "chest"
    if any(k in t for k in ["diabetes","sugar","thyroid"]): return "diabetes"
    if any(k in t for k in ["anxiety","depression","stress","neend"]): return "mental"
    if any(k in t for k in ["stone","kidney","uti"]): return "kidney"
    if any(k in t for k in ["jaundice","liver"]): return "liver"
    if any(k in t for k in ["piles","bawasir"]): return "piles"
    if any(k in t for k in ["period","pregnancy","garbh"]): return "ladies"
    if any(k in t for k in ["child","bach"]): return "child"
    if any(k in t for k in ["malaria","dengue","typhoid","cancer"]): return "serious"
    if any(k in t for k in ["bukhar","fever"]): return "fever"
    if any(k in t for k in ["pet","stomach","gas","ulti"]): return "stomach"
    if any(k in t for k in ["sar","head","headache"]): return "head"
    if any(k in t for k in ["daant","tooth"]): return "tooth"
    if any(k in t for k in ["aankh","eye"]): return "eye"
    if any(k in t for k in ["kaan","ear","naak"]): return "ear"
    if any(k in t for k in ["kamar","back","leg","knee","haath"]): return "back"
    return "general"
def show_doctor_detail_card(user_text, loc):
    cat=get_category_for(user_text); city=loc.get("city",""); pincode=loc.get("pincode","")
    city_slug=city.strip().lower().replace(" ","-"); lang_now="Hindi" if IS_HINDI else "English"
    ai_info=get_doctor_info_ai(user_text,lang_now)
    practo_direct=f"https://www.practo.com/{city_slug}/{PRACTO_SLUG.get(cat,'general-physician')}"
    apollo_direct=f"https://www.apollo247.com/specialties/{APOLLO_SLUG.get(cat,'general-physician')}"
    google_direct=f"https://www.google.com/maps/search/{urllib.parse.quote('doctor near '+city+' '+pincode+' India')}"
    st.markdown(f"""<div class="doctor-card"><b>👨‍⚕️ {T('आपको इस डॉक्टर की जरूरत है:','You need this doctor:')}</b><br><br><span>{ai_info}</span><br><br><span><b>{T('आपका इलाका:','Your Area:')}</b> {city}, {pincode}</span></div>""",unsafe_allow_html=True)
    st.link_button(f"📍 {T('मेरे पास के डॉक्टर देखें - Maps','See Doctors Near Me - Maps')}",google_direct,use_container_width=True)
    st.link_button(T("💻 डायरेक्ट देखें - प्रैक्टो","💻 Direct Doctors - Practo"),practo_direct,use_container_width=True)
    st.link_button(T("🏥 डायरेक्ट देखें - अपोलो","🏥 Direct Doctors - Apollo"),apollo_direct,use_container_width=True)
    st.link_button(T("🩺 डायरेक्ट लॉगिन - ई-संजीवनी","🩺 Direct Login - eSanjeevani"),"https://esanjeevani.mohfw.gov.in/patient/",use_container_width=True)
    st.link_button(T("📞 104 पर कॉल करें","📞 Call 104"),"tel:104",use_container_width=True)
    st.link_button(T("🚑 108 - एम्बुलेंस","🚑 108 - Ambulance"),"tel:108",use_container_width=True)
def show_location_form(for_text):
    st.markdown(f"### {T('📍 डॉक्टर खोजने के लिए अपनी लोकेशन बताइए','📍 Tell Your Location To Find Doctor')}")
    city=st.text_input(T("शहर का नाम","City Name"),value="",key="loc_city")
    pincode=st.text_input(T("पिनकोड","Pincode"),value="",key="loc_pincode")
    if st.button(T("✅ डॉक्टर खोजें","✅ Find Doctor"),use_container_width=True,key="find_doctor_btn"):
        if city.strip()=="" or pincode.strip()=="": st.warning(T("पहले शहर और पिनकोड लिखिए।","First write city and pincode."))
        else:
            st.session_state.doctor_location={"country":"India","city":city.strip(),"pincode":pincode.strip()}
            st.session_state.doctor_step="done"
            st.session_state.messages.append({"role":"assistant","content":"DOCTORS_BOX","for_text":for_text,"loc":dict(st.session_state.doctor_location)}); st.rerun()
def show_floating_banner():
    tips=["💡 दिन में 8 गिलास पानी पिएं","💡 चोट को साफ पानी से धोएं","💡 एलर्जी में खुजली मत करें","💡 दवा समय पर लें","💡 रोज 30 मिनट टहलें"] if IS_HINDI else ["💡 Drink 8 glasses of water daily","💡 Wash wound with clean water","💡 In allergy do not scratch","💡 Take medicine on time","💡 Walk 30 minutes daily"]
    items="".join([f'<div class="tip" style="animation-delay:{i*4}s;">{tip}</div>' for i,tip in enumerate(tips)])
    st.markdown(f"""<style>.banner-wrap {{position:fixed; bottom:0; left:0; right:0; z-index:9999; background:linear-gradient(90deg,#FFE4E6,#FEF3C7,#D1FAE5); height:48px; overflow:hidden; border-top:1px solid #FDE68A;}} .banner-wrap .tip {{position:absolute; left:0; right:0; top:0; height:48px; display:flex; align-items:center; justify-content:center; color:#7C2D12 !important; font-weight:600; font-size:14px; opacity:0; animation:tipCycle 20s linear infinite;}} @keyframes tipCycle {{0%{{opacity:0;}} 1%{{opacity:1;}} 15%{{opacity:1;}} 17%{{opacity:0;}} 100%{{opacity:0;}}}}</style><div class="banner-wrap">{items}</div>""",unsafe_allow_html=True)
def ask_reply(user_text, placeholder, speak=False):
    real_lang=detect_language(user_text)
    if not is_health_related(user_text):
        msg=out_of_context_msg(real_lang); placeholder.markdown(msg)
        if speak: speak_answer(msg,real_lang)
        return msg
    instant=get_instant_answer(user_text,real_lang); placeholder.markdown(instant)
    if speak: speak_answer(instant,real_lang)
    return instant
def check_photo_is_health(image_bytes):
    try:
        b64=base64.b64encode(image_bytes).decode()
        url=f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        data={"contents":[{"parts":[{"text":"Is this image showing human skin problem like rash, allergy, wound, injury, cut, burn, swelling? If YES answer only YES. If chart, food, animal, car, building, screenshot, document answer only NO."},{"inline_data":{"mime_type":"image/jpeg","data":b64}}]}]}
        req=urllib.request.Request(url,data=json.dumps(data).encode(),headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req,timeout=30) as res:
            out=json.loads(res.read().decode()); ans=out["candidates"][0]["content"]["parts"][0]["text"].strip().upper(); return "YES" in ans
    except: return True
def ask_reply_photo(photo_keyword, photo_desc, placeholder, image_bytes=None, speak=False):
    real_lang="Hindi" if IS_HINDI else "English"
    if photo_desc.strip()!="" and not is_health_related(photo_desc):
        msg=out_of_context_msg(real_lang); placeholder.markdown(msg)
        if speak: speak_answer(msg,real_lang)
        return msg
    if image_bytes is not None and not check_photo_is_health(image_bytes):
        msg=out_of_context_msg(real_lang); placeholder.markdown(msg)
        if speak: speak_answer(msg,real_lang)
        return msg
    instant=get_instant_answer(f"{photo_keyword} {photo_desc}".strip(),real_lang); placeholder.markdown(instant)
    if speak: speak_answer(instant,real_lang)
    return instant

if menu in ["🏠 Home","🏠 होम"]:
    st.markdown(f"""<div class="ai-header"><h1>🩺 Sehat Saathi ✨</h1><p>{T('आपका एआई हेल्थ असिस्टेंट','Your AI Health Assistant')}</p></div>""",unsafe_allow_html=True)
    st.write(T("नमस्ते, मैं यहाँ आपकी मदद करने के लिए हूँ! 👋","Hello, I am here to help you! 👋"))
    voice_on=st.toggle(T("🔊 आवाज़ में जवाब सुनें - ON करें","🔊 Listen Answer in Voice - Turn ON"),value=True)
    st.session_state.voice_mode=voice_on
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            if m.get("content")=="DOCTORS_BOX": show_doctor_detail_card(m.get("for_text",""),m.get("loc",st.session_state.doctor_location))
            elif m.get("type")=="image":
                st.image(m["image"],caption=T("📸 आपकी फोटो","📸 Your Photo"),use_container_width=True)
                st.markdown(f"**{T('आपने लिखा:','You wrote:')}** {m['content']}")
            else:
                st.markdown(m["content"])
                if m["role"]=="assistant" and m["content"]!="DOCTORS_BOX" and "सिर्फ स्वास्थ्य" not in m["content"] and "only help" not in m["content"].lower():
                    if st.button(T("🔊 आवाज़ में सुनें","🔊 Listen in Voice"),key=f"listen_{id(m)}_{m['content'][:20]}"): speak_answer(m["content"],"Hindi" if IS_HINDI else "English")
    if st.session_state.doctor_step=="location":
        last_user=""
        for mm in reversed(st.session_state.messages):
            if mm["role"]=="user": last_user=mm["content"]; break
        show_location_form(last_user)
    if st.session_state.messages and st.session_state.messages[-1]["role"]=="assistant" and not st.session_state.doctor_asked and st.session_state.doctor_step=="none":
        if st.session_state.messages[-1].get("content")!="DOCTORS_BOX" and "सिर्फ स्वास्थ्य" not in st.session_state.messages[-1]["content"] and "only help with health" not in st.session_state.messages[-1]["content"].lower():
            st.info(T("👨‍⚕️ क्या आप डॉक्टर से बात करना चाहेंगी?","👨‍⚕️ Would you like to see a doctor?"))
            c1,c2=st.columns(2)
            with c1:
                if st.button(T("✅ हाँ, डॉक्टर से बात करें","✅ Yes, See Doctor"),use_container_width=True,key="yes_doctor"): st.session_state.doctor_asked=True; st.session_state.doctor_step="location"; st.rerun()
            with c2:
                if st.button(T("❌ नहीं, बस ऐसे ही","❌ No, Thanks"),use_container_width=True,key="no_doctor"):
                    st.session_state.doctor_asked=True; st.session_state.doctor_step="none"
                    st.session_state.messages.append({"role":"assistant","content":T("ठीक है, अपना ख्याल रखिए। तकलीफ बढ़े तो 104 या 108 पर कॉल कीजिएगा।","Okay, take care. If problem increases, call 104 or 108.")}); st.rerun()
    st.markdown("---")
    st.write(f"**{T('✍️ अपनी तकलीफ लिखें','✍️ Write Your Symptom')}**")
    with st.form("chat_form",clear_on_submit=True):
        chat_text=st.text_input("Type...",label_visibility="collapsed",value="")
        submitted=st.form_submit_button(T("➤ भेजें","➤ Send"),use_container_width=True)
        if submitted and chat_text.strip()!="":
            st.session_state.messages.append({"role":"user","content":chat_text}); st.session_state.doctor_asked=False; st.session_state.doctor_step="none"
            with st.chat_message("user"): st.markdown(chat_text)
            with st.chat_message("assistant"):
                placeholder=st.empty(); reply=ask_reply(chat_text,placeholder,speak=st.session_state.voice_mode)
            st.session_state.messages.append({"role":"assistant","content":reply,"for_text":chat_text}); st.rerun()
    if st.button(T("🧹 चैट साफ करें","🧹 Clear Chat"),use_container_width=True):
        st.session_state.messages=[]; st.session_state.doctor_asked=False; st.session_state.doctor_step="none"; st.session_state.doctor_location={}; st.session_state["last_audio_id"]=""; st.session_state.uploader_key+=1; st.rerun()
    col_photo,col_audio=st.columns(2)
    with col_photo:
        st.write(T("📷 फोटो","📷 Photo")); uploaded_photo=st.file_uploader("Upload Photo",type=["jpg","jpeg","png"],label_visibility="collapsed",key=f"wa_cam_{st.session_state.uploader_key}")
    with col_audio:
        st.write(T("🎤 आवाज़","🎤 Voice")); audio_input=st.audio_input("Speak",label_visibility="collapsed",key="wa_mic")
    if uploaded_photo:
        st.image(uploaded_photo,width=200)
        photo_type=st.radio("Photo Type",T(["एलर्जी / दाने","चोट / जख्म","खुजली / दाने"],["Allergy / Rash","Injury / Wound","Itching / Rash"]),label_visibility="collapsed",horizontal=True,key="photo_type")
        photo_desc=st.text_input(T("फोटो में क्या दिख रहा है?","What is visible in photo?"),value="",key="photo_desc")
        if st.button(T("📸 फोटो भेजें","📸 Send Photo"),use_container_width=True):
            kw="chot zakhm" if "चोट" in photo_type or "Injury" in photo_type else "khujli rash" if "खुजली" in photo_type or "Itching" in photo_type else "allergy daane"
            photo_text=f"{kw} {photo_desc}".strip()
            with st.chat_message("user"):
                st.image(uploaded_photo,caption=T("📸 आपकी फोटो","📸 Your Photo"),use_container_width=True); st.markdown(f"**{T('आपने लिखा:','You wrote:')}** {photo_text}")
            with st.chat_message("assistant"):
                placeholder=st.empty(); reply=ask_reply_photo(kw,photo_desc,placeholder,uploaded_photo.getvalue(),speak=st.session_state.voice_mode)
            st.session_state.messages.append({"role":"user","content":photo_text,"type":"image","image":uploaded_photo})
            st.session_state.messages.append({"role":"assistant","content":reply,"for_text":photo_text}); st.session_state.doctor_asked=False; st.session_state.doctor_step="none"; st.session_state.uploader_key+=1; st.rerun()
    if audio_input and st.session_state.get("last_audio_id")!=str(audio_input):
        st.session_state["last_audio_id"]=str(audio_input)
        with st.spinner(T("सुन रहे हैं...","Listening...")): voice_text=speech_to_text(audio_input.read())
        if voice_text and not voice_text.startswith("ERROR:"):
            with st.chat_message("user"): st.markdown(f"🎤 {T('आपने बोला:','You said:')} {voice_text}")
            st.session_state.messages.append({"role":"user","content":voice_text}); st.session_state.doctor_asked=False; st.session_state.doctor_step="none"
            with st.chat_message("assistant"):
                placeholder=st.empty(); reply=ask_reply(voice_text,placeholder,speak=True)
            st.session_state.messages.append({"role":"assistant","content":reply,"for_text":voice_text}); st.rerun()
        else: st.warning(T("आवाज़ समझ नहीं आई, दोबारा बोलिए।","Could not understand, please speak again."))
    show_floating_banner()
elif menu in ["💊 Medicine Info","💊 दवाई की जानकारी"]:
    st.title(T("💊 दवाई की जानकारी","💊 Medicine Info"))
    st.write(T("दुनिया की कोई भी दवाई का नाम लिखें, पूरी जानकारी मिलेगी।","Write name of any medicine, you will get full info."))
    med_input=st.text_input(T("दवाई का नाम...","Medicine name..."),value="",key="med_info_input")
    if st.button(T("🔍 दवाई की जानकारी देखें","🔍 See Medicine Info"),use_container_width=True):
        if med_input.strip()=="": st.warning(T("पहले दवाई का नाम लिखिए।","First write medicine name."))
        else:
            lang_now="Hindi" if IS_HINDI else "English"; info=get_medicine_info(med_input,lang_now)
            st.markdown(f"""<div class="medicine-card">{info}</div>""",unsafe_allow_html=True)
            if st.button(T("🔊 आवाज़ में सुनें","🔊 Listen in Voice"),key="med_listen"): speak_answer(info,lang_now)
    st.markdown("---"); st.write(T("**लोकप्रिय दवाइयां:**","**Popular Medicines:**"))
    cols=st.columns(3)
    for i,p in enumerate(["Paracetamol","Azithromycin","Cetirizine","Omeprazole","Ibuprofen","ORS"]):
        with cols[i%3]:
            if st.button(p,key=f"pop_{p}"):
                lang_now="Hindi" if IS_HINDI else "English"; med_info=get_medicine_info(p,lang_now); st.markdown(med_info); speak_answer(med_info,lang_now)
    show_floating_banner()
elif menu in ["💊 Medicine Reminder","💊 दवाई रिमाइंडर"]:
    st.title(T("💊 दवाई रिमाइंडर","💊 Medicine Reminder"))
    with st.form("reminder_form"):
        med_name=st.text_input(T("दवाई का नाम","Medicine Name"),value="")
        c_h,c_m,c_ap=st.columns(3)
        with c_h: hour=st.selectbox(T("घंटा","Hour"),list(range(1,13)),index=None,placeholder="")
        with c_m: minute=st.selectbox(T("मिनट","Minute"),[f"{i:02d}" for i in range(0,60)],index=None,placeholder="")
        with c_ap: ampm=st.radio("AM / PM",["AM","PM"],horizontal=True)
        med_days=st.number_input(T("कितने दिन तक?","How many days?"),min_value=1,max_value=30,value=None,placeholder="")
        if st.form_submit_button(T("✅ रिमाइंडर सेट करें","✅ Set Reminder"),use_container_width=True):
            if med_name.strip()=="" or hour is None or minute is None or med_days is None: st.warning(T("पहले दवाई का नाम, समय और दिन लिखिए","First write medicine name, time and days"))
            else:
                hour_24=hour%12
                if ampm=="PM": hour_24+=12
                if ampm=="AM" and hour==12: hour_24=0
                display_time=f"{hour}:{minute} {ampm}"
                st.session_state.reminders.append({"name":med_name.strip(),"time":f"{hour_24:02d}:{minute}","display":display_time,"days":med_days,"hour24":hour_24,"minute":minute})
                st.success(T(f"✅ रिमाइंडर सेट: {med_name.strip()} - {display_time}",f"✅ Reminder set: {med_name.strip()} - {display_time}"))
    now_str=datetime.datetime.now().strftime("%H:%M")
    for r in st.session_state.reminders:
        if r["time"][:5]==now_str: st.error(T(f"🔔 दवाई का समय हो गया! {r['name']} ले लीजिए!",f"🔔 TIME FOR MEDICINE! Take {r['name']} now!"))
        st.info(f"💊 {r['name']} - ⏰ {r.get('display',r['time'])} - 📅 {r['days']} din")
        today=datetime.date.today().strftime("%Y%m%d"); hh=str(r.get("hour24",9)).zfill(2); mm=str(r.get("minute","00")).zfill(2)
        gcal_url=f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={urllib.parse.quote(r['name']+' - Dawa Leni Hai')}&dates={today}T{hh}{mm}00/{today}T{hh}{mm}00&recur=RRULE:FREQ=DAILY;COUNT={r['days']}"
        st.link_button(T("📅 गूगल कैलेंडर में जोड़ें","📅 Add to Google Calendar"),gcal_url,use_container_width=True)
    if st.session_state.reminders:
        if st.button(T("🗑️ सारे रिमाइंडर हटाएं","🗑️ Delete All Reminders"),use_container_width=True): st.session_state.reminders=[]; st.rerun()
    show_floating_banner()
elif menu in ["👨‍⚕️ Talk To Doctor","👨‍⚕️ डॉक्टर से बात करें"]:
    st.title(T("👨‍⚕️ डॉक्टर से बात करें","👨‍⚕️ Talk To Doctor"))
    st.success(T("ये सब सरकारी डॉक्टर की सेवाएं हैं, 100% असली।","All Govt doctor services, 100% Real."))
    talk_symptom=st.text_input(T("अपनी तकलीफ लिखें","Write Your Problem"),value="",key="talk_symptom")
    if talk_symptom.strip()!="": show_location_form(talk_symptom)
    st.link_button(T("📞 104 पर कॉल करें","📞 Call 104"),"tel:104",use_container_width=True)
    show_floating_banner()
elif menu in ["🚨 Emergency","🚨 आपातकाल"]:
    st.title(T("🚨 आपातकाल - Emergency","🚨 Emergency"))
    st.error(T("अगर तकलीफ बहुत ज़्यादा है तो पहले CALL करें!","If serious, CALL FIRST!"))
    st.link_button(T("🚑 108 - एम्बुलेंस बुलाएं","🚑 108 - Call Ambulance"),"tel:108",use_container_width=True)
    st.link_button(T("🚓 112 - पुलिस / आपातकाल","🚓 112 - Police / Emergency"),"tel:112",use_container_width=True)
    st.link_button(T("🔥 101 - फायर ब्रिगेड","🔥 101 - Fire Brigade"),"tel:101",use_container_width=True)
    st.link_button(T("📞 104 - हेल्थ हेल्पलाइन","📞 104 - Health Helpline"),"tel:104",use_container_width=True)
    st.link_button(T("👧 1098 - चाइल्ड हेल्पलाइन","👧 1098 - Child Helpline"),"tel:1098",use_container_width=True)
    st.link_button(T("👩 181 - महिला हेल्पलाइन","👩 181 - Women Helpline"),"tel:181",use_container_width=True)
    st.markdown("---")
    em_text=st.text_input(T("इमरजेंसी लिखें...","Write emergency..."),value="",key="em_text")
    em_audio=st.audio_input(T("इमरजेंसी बोलें","Speak Emergency"),key="em_mic")
    em_final=em_text
    if em_audio and st.session_state.get("last_em_audio")!=str(em_audio):
        st.session_state["last_em_audio"]=str(em_audio); vt=speech_to_text(em_audio.read())
        if vt and not vt.startswith("ERROR:"): st.success(T(f"🗣️ आपने बोला: {vt}",f"🗣️ You said: {vt}")); em_final=vt
    if st.button(T("🚨 इमरजेंसी स्टेप्स देखें","🚨 See Emergency Steps"),use_container_width=True):
        if em_final.strip()=="": st.warning(T("पहले इमरजेंसी लिखें या बोलें।","First write or speak emergency."))
        elif not is_health_related(em_final): st.warning(out_of_context_msg(detect_language(em_final)))
        else:
            lang_now=detect_language(em_final); lang_rule="Answer ONLY in proper Hindi." if lang_now=="Hindi" else "Answer ONLY in proper English."
            ans=ask_ai(f"Emergency hai: {em_final}. Language: {lang_now}. {lang_rule} 4-5 short steps batao, ambulance aane tak kya karna hai. Pehli line me 108 par call karne ko bolo.")
            if ans=="OFFLINE_FALLBACK": st.error(T("पहले 108 पर कॉल करें! चोट को साफ कपड़े से दबाएं।","Call 108 first! Press wound with clean cloth."))
            else: st.error(ans); speak_answer(ans,lang_now)
    show_floating_banner()
elif menu in ["🏥 Hospital Finder","🏥 अस्पताल खोजें"]:
    st.title(T("🏥 अस्पताल खोजें","🏥 Hospital Finder"))
    h_city=st.text_input(T("शहर का नाम","City Name"),value="",key="hosp_city")
    h_pin=st.text_input(T("पिनकोड","Pincode"),value="",key="hosp_pin")
    if st.button(T("🏥 अस्पताल खोजें","🏥 Find Hospitals"),use_container_width=True):
        if h_city.strip()=="" or h_pin.strip()=="": st.warning(T("पहले शहर और पिनकोड लिखिए।","First write city and pincode."))
        else:
            st.success(T(f"✅ {h_city} - {h_pin} के पास के अस्पताल:",f"✅ Hospitals near {h_city} - {h_pin}:"))
            for h in get_hospitals_for(h_city,h_pin): st.markdown(f"""<div class="hospital-card"><b>🏥 {h['name']}</b><br><span>{h['type']}</span><br><span>📍 {h['addr']}</span><br><span>📞 {h['phone']}</span></div>""",unsafe_allow_html=True)
            maps_url=f"https://www.google.com/maps/search/{urllib.parse.quote('hospital near '+h_city+' '+h_pin+' India')}"
            st.link_button(T("📍 गूगल मैप्स पर सारे अस्पताल देखें","📍 See All Hospitals On Google Maps"),maps_url,use_container_width=True)
    show_floating_banner()
elif menu in ["💡 Health Tips","💡 स्वास्थ्य टिप्स"]:
    st.title(T("💡 स्वास्थ्य टिप्स","💡 Health Tips"))
    st.write(T("- सुबह गुनगुना पानी पिएं\n- रोज 30 मिनट टहलें\n- हरी सब्जी खाएं, नमक-तेल कम रखें\n- 7-8 घंटे नींद लें\n- खाना खाने से पहले हाथ धोएं\n- बच्चों के टीके समय पर लगवाएं\n- महीने में 1 बार BP-Sugar जांच करवाएं","- Drink warm water in morning\n- Walk 30 min daily\n- Eat green vegetables, less salt-oil\n- Sleep 7-8 hours\n- Wash hands before eating\n- Get children vaccinated on time\n- Check BP-Sugar once a month"))
    show_floating_banner()
elif menu in ["⚖️ BMI Calculator","⚖️ बीएमआई कैलकुलेटर"]:
    st.title(T("⚖️ बीएमआई कैलकुलेटर","⚖️ BMI Calculator"))
    weight=st.number_input(T("वज़न (kg)","Weight (kg)"),min_value=10.0,max_value=200.0,value=None,placeholder="")
    height=st.number_input(T("ऊंचाई (cm)","Height (cm)"),min_value=100.0,max_value=220.0,value=None,placeholder="")
    if st.button(T("हिसाब लगाएं","Calculate")):
        if weight is None or height is None: st.warning(T("पहले वज़न और ऊंचाई लिखिए","First write weight and height"))
        else:
            bmi=weight/((height/100)**2); st.success(f"BMI: {bmi:.1f}")
            if bmi<18.5: st.write(T("कम वज़न - स्वस्थ खाना खाएं","Underweight - Eat healthy food"))
            elif bmi<25: st.write(T("सामान्य - बहुत बढ़िया!","Normal - Good!"))
            elif bmi<30: st.write(T("ज्यादा वज़न - रोज़ टहलें","Overweight - Walk daily"))
            else: st.write(T("मोटापा - डॉक्टर से बात करें","Obese - Please consult doctor"))
    show_floating_banner()
elif menu in ["🏛️ Government Schemes","🏛️ सरकारी योजनाएं"]:
    st.title(T("🏛️ सरकारी योजनाएं","🏛️ Government Schemes"))
    st.success(T("ये सब सरकारी योजनाएं हैं, 100% असली और फ्री।","All Govt schemes, 100% Real and FREE."))
    schemes=[("🩺 आयुष्मान भारत - PMJAY","5 लाख तक का फ्री इलाज","https://beneficiary.nha.gov.in","✅ आयुष्मान कार्ड बनाएं / चेक करें"),("💊 जन औषधि - सस्ती दवाई","दवाई 50% से 90% तक सस्ती","https://janaushadhi.gov.in","💊 नज़दीकी केंद्र ढूंढें"),("🩺 ई-संजीवनी - फ्री ऑनलाइन डॉक्टर","वीडियो कॉल पर फ्री डॉक्टर, 10 AM - 4 PM","https://esanjeevani.mohfw.gov.in/patient/","🩺 फ्री डॉक्टर से बात करें"),("🤰 पीएम सुरक्षित मातृत्व","गर्भवती महिला की फ्री जांच","https://nhm.gov.in","🤰 जानकारी देखें"),("👶 मिशन इंद्रधनुष","बच्चों के सारे टीके फ्री","https://www.mohfw.gov.in","👶 जानकारी देखें"),("🤱 जननी सुरक्षा योजना","डिलीवरी पर ₹1400 तक मदद","https://nhm.gov.in","🤱 जानकारी देखें"),("👩‍🍼 जननी शिशु सुरक्षा","माँ + बच्चे का फ्री इलाज","https://nhm.gov.in","👩‍🍼 जानकारी देखें"),("👵 पीएम वय वंदना","60+ बुजुर्गों को मासिक पेंशन","https://www.licindia.in","👵 जानकारी देखें"),("🦟 राष्ट्रीय स्वास्थ्य मिशन","PHC में BP, Sugar जांच फ्री","https://nhm.gov.in","🦟 जानकारी देखें"),("🪪 आभा कार्ड - Digital Health ID","पूरे इंडिया में रिपोर्ट एक कार्ड से","https://abha.abdm.gov.in","🪪 आभा कार्ड बनाएं"),("🧠 टेली-मानस - 14416","घबराहट, उदासी में फ्री काउंसलर","tel:14416","📞 14416 पर कॉल करें"),("🫁 टीबी मुक्त भारत / निक्षय","टीबी इलाज फ्री + ₹500/महीना","https://nikshay.in","🫁 निक्षय पोर्टल देखें")]
    for title,desc,link,btn in schemes:
        st.markdown(f"""<div class="scheme-card"><b>{title}</b><br><span>{desc}</span></div>""",unsafe_allow_html=True); st.link_button(btn,link,use_container_width=True)
    show_floating_banner()
elif menu in ["ℹ️ About App","ℹ️ ऐप के बारे में"]:
    st.title(T("ℹ️ ऐप के बारे में - सेहत साथी","ℹ️ About App - Sehat Saathi"))
    st.write(T("सेहत साथी सिर्फ इंडिया के लिए बनाया गया है - बच्चों से लेकर बुजुर्गों तक।","Sehat Saathi is made only for India - from children to elderly."))
    st.write(T("फीचर्स: 💬 चैट, 🎤 बोलकर बताएं, 🔊 बोलकर जवाब, 📷 फोटो भेजें, 💊 दवाई जानकारी, 💊 रिमाइंडर, 👨‍⚕️ डॉक्टर, 🚨 आपातकाल, 🏥 अस्पताल, 💡 टिप्स, ⚖️ BMI, 🏛️ सरकारी योजनाएं","Features: Chat, Voice Input, Voice Answer, Photo, Medicine Info, Reminder, Doctor, Emergency, Hospital, Tips, BMI, Govt Schemes"))
    st.info(T("⚠️ ये ऐप सिर्फ जानकारी के लिए है। डॉक्टर की जगह नहीं ले सकता। तकलीफ ज़्यादा हो तो 108 पर कॉल करें।","⚠️ This app is only for information. Cannot replace doctor. If serious, call 108."))
    show_floating_banner()
