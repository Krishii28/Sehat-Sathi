import streamlit as st
import datetime
import re
import urllib.parse
import json
st.set_page_config(page_title="Sehat Saathi", page_icon="🩺", layout="centered")
if "messages" not in st.session_state:
    st.session_state.messages = []
if "doctor_asked" not in st.session_state:
    st.session_state.doctor_asked = False
if "reminders" not in st.session_state:
    st.session_state.reminders = []
if "last_audio_id" not in st.session_state:
    st.session_state["last_audio_id"] = ""

st.sidebar.write("Language - Menu Ki Bhasha")
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

# ---------- OUT OF CONTEXT RULE - SIRF HEALTH / CHOT / ALLERGY ----------
HEALTH_WORDS = ["daane","rash","chot","zakhm","allergy","khujli","itching","bukhar","fever","dard","pain","dawa","medicine","wound","injury","skin","khaansi","cough","cold","sardi","pet","stomach","sir","head","haath","hand","pair","leg","blood","khoon","burn","jal","soojan","swelling","ulti","vomit","dast","kamzori","weak","neend","sleep","saans","breath","chest","seene","gala","throat","kaan","ear","daant","tooth","aankh","eye","ghutna","knee","kamar","back","badan","body","chakkar","dizzy","gas","acidity","kabz","photo","doctor","hospital","bimar","beemar","tabiyat","dawai"]
OUT_WORDS = ["movie","film","cricket","football","game","padhai","study","exam","joke","song","gaana","politics","news","weather","mausam","love","shaadi","job","naukri","paisa","money","shopping","birthday"]
def is_health_related(text):
    t = text.lower()
    if any(w in t for w in HEALTH_WORDS):
        return True
    if any(w in t for w in OUT_WORDS):
        return False
    if t.strip() in ["hi","hello","namaste","hey","hii"]:
        return True
    return False

def out_of_context_msg(real_lang):
    if real_lang=="Hindi":
        return "Main sirf health, chot aur allergy se related help kar sakti hu. Apni health problem batao - jaise sar dard, bukhar, daane, chot, khujli."
    else:
        return "I can only help with health, injury and allergy related problems. Please tell your health problem - like headache, fever, rash, injury, itching."

def detect_language(user_text):
    t = user_text.lower()
    if re.search(r'[\u0900-\u097F]', user_text):
        return "Hindi"
    hindi_words = ["mere", "mera", "mujhe", "mujhko", "dard", "hai", "ho", "raha", "rahi", "gaya", "sar", "sir", "kamar", "pet", "badan", "bukhar", "sardi", "khansi", "khujli", "daane", "gala", "gale", "kaan", "daant", "aankh", "pair", "haath", "ghutna", "chakkar", "ulti", "dast", "kamzori", "neend", "chot", "seene", "saans"]
    for w in hindi_words:
        if w in t:
            return "Hindi"
    english_words = ["my", "i have", "pain", "paining", "head", "back", "body", "fever", "cold", "cough", "stomach", "throat", "chest", "leg", "knee", "eye", "ear", "tooth", "rash", "itching", "dizzy", "vomit"]
    for w in english_words:
        if w in t:
            return "English"
    return "Hindi" if IS_HINDI else "English"

# ---------- FLOATING BANNER BOTTOM - KHUD CHANGE HOGA ----------
def show_floating_banner():
    tips_hi = ["💡 Din me 8 glass paani piyo", "💡 Chot ko saaf paani se dhoyo, ganda kapda mat lagao", "💡 Allergy me khujli mat karo, thanda paani lagao", "💡 Dawa time pe lo, dose miss mat karo", "💡 Roz 30 minute walk karo", "💡 Bukhar 102 se upar ho toh turant doctor ko dikhao"]
    tips_en = ["💡 Drink 8 glasses of water daily", "💡 Wash wound with clean water, do not apply dirty cloth", "💡 In allergy do not scratch, apply cold water", "💡 Take medicine on time, do not miss dose", "💡 Walk 30 minutes daily", "💡 If fever is above 102, see doctor immediately"]
    tips = tips_hi if IS_HINDI else tips_en
    tips_json = json.dumps(tips)
    st.markdown(f"""
    <style>
    .floating-banner {{
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 9999;
        background: #FF4B4B;
        color: white;
        text-align: center;
        padding: 12px 10px;
        font-size: 15px;
        font-weight: 600;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.2);
    }}
    .block-container {{ padding-bottom: 70px !important; }}
    </style>
    <div class="floating-banner" id="sehat-banner">{tips[0]}</div>
    <script>
    const tips = {tips_json};
    let i = 0;
    setInterval(() => {{
        i = (i + 1) % tips.length;
        const el = document.getElementById('sehat-banner');
        if (el) el.innerText = tips[i];
    }}, 4000);
    </script>
    """, unsafe_allow_html=True)

# ---------- HAR SYMPTOM KE HISAB SE ALAG JAWAB - PURE HINDI / PURE ENGLISH ----------
def get_instant_answer(user_text, lang):
    text = user_text.lower()
    def make_answer(symptom_name, causes, dangers, dos, tip, summary, lang):
        if lang == "Hindi":
            c = "\n".join([f"- **{a}:** {b}" for a,b in causes])
            d = "\n".join([f"- **{a}:** {b}" for a,b in dangers])
            w = "\n".join([f"- **{a}:** {b}" for a,b in dos])
            return f"""Aapki takleef samajh sakte hain, aaram kijiye.

**Sambhav Karan - {symptom_name} ki wajah:**

{c}

**Khatre Ke Lakshan:**

{d}

**Abhi Kya Karein:**

{w}

**Sehat Tip:**

- **{tip[0]}:** {tip[1]}

{summary}

Kya aap doctor se baat karna chahengi?"""
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

    if "head" in text or "sar" in text or "sir" in text or "migraine" in text or "headache" in text:
        if lang == "Hindi":
            return make_answer("Sir Dard", [("Neend ki Kami","Raat ko neend poori na hone se subah uthte hi sar bhari lagta hai aur dard hone lagta hai."),("Zyada Phone","Din bhar phone dekhne se aankhon pe zor padta hai, isse sar ke aage wale hisse me dard hota hai."),("Gas / Bhook","Lambi der bhooke rehne se ya gas banne se bhi sar me dard hota hai.")], [("Bahut Tez Dard","Agar achanak bahut tez dard ho, jaise pehle kabhi nahi hua, toh turant doctor ko dikhayein."),("Ulti / Chakkar","Sar dard ke saath ulti ya chakkar aaye, toh der mat karein.")], [("Andhere Me Aaram","Light band karke andhere kamre me let jayein, phone mat dekhein."),("Thandi Patti","Sar pe thande paani ki patti rakhein, isse dard kam hoga."),("Gunguna Paani","Thoda-thoda karke gunguna paani piyein, khaali pet mat rahein.")], ("Phone Kam Dekhein","Roz sone se 30 minute pehle phone band kar dein, sar dard kam ho jayega."), "Aapka sar dard zyada tar neend ki kami aur phone dekhne ki wajah se lag raha hai, isliye aaj phone kam dekhiye aur thodi der so jayiye.", lang)
        else:
            return make_answer("Headache", [("Less Sleep","When you do not sleep well at night, you wake up with a heavy head and headache starts."),("Too Much Phone","Watching phone all day puts pressure on your eyes. This causes pain in the front part of your head."),("Gas and Hunger","Staying hungry for a long time or gas also causes headache.")], [("Very Severe Pain","If you get sudden very severe headache, like never before, see a doctor immediately."),("Vomiting / Dizziness","If you feel vomiting or dizziness with headache, do not wait.")], [("Rest in Dark Room","Lie down in a dark room with lights off, do not see phone."),("Cold Cloth","Keep a cold wet cloth on your head, it will reduce headache."),("Warm Water","Drink warm water in small sips, do not stay empty stomach.")], ("Less Phone","Switch off phone 30 minutes before sleeping daily, headache will reduce."), "Your headache seems mostly because of less sleep and too much phone, so use phone less today and take some sleep.", lang)
    if "back" in text or "kamar" in text or "spine" in text:
        if lang == "Hindi":
            return make_answer("Kamar Dard", [("Galat Bethna","Lambi der jhuk ke bethne se kamar ki haddi pe zor padta hai."),("Bhari Cheez Uthana","Achanak bhari balti uthane se kamar ki nas khich jati hai."),("Kamzori","Calcium aur Vitamin D ki kami se haddiyan kamzor ho jati hain.")], [("Pair Me Dard","Agar dard kamar se pair tak ja raha hai, toh turant doctor ko dikhayein."),("Chalne Me Dikkat","Agar chalne me bahut takleef ho, toh der mat karein.")], [("Seedha Letein","Seedhe sakht bistar pe let jayein."),("Garam Sek","Kamar pe din me 2 baar 10 minute garam sek karein."),("Bhari Kaam Band","2 din tak bhari cheez mat uthayein.")], ("Roz Walk","Roz 20 minute seedha chaliye, kamar mazboot hogi."), "Aapka kamar dard zyada tar galat bethne aur bhari kaam ki wajah se lag raha hai, 2 din aaram kijiye.", lang)
        else:
            return make_answer("Back Pain", [("Wrong Sitting","Sitting bent for a long time puts pressure on back bone."),("Lifting Heavy Things","Suddenly lifting heavy bag pulls the back nerve."),("Weakness","Lack of Calcium and Vitamin D makes bones weak.")], [("Pain in Leg","If pain is going from back to leg, see a doctor immediately."),("Difficulty Walking","If you feel too much difficulty in walking, do not wait.")], [("Lie Straight","Lie straight on a hard bed."),("Hot Compress","Apply warm cloth on back for 10 minutes, 2 times a day."),("Stop Heavy Work","Do not lift heavy things for 2 days.")], ("Daily Walk","Walk straight for 20 minutes daily, your back will become strong."), "Your back pain seems mostly because of wrong sitting and heavy work, take rest for 2 days.", lang)
    if "body" in text or "badan" in text or "sharir" in text or "whole" in text:
        if lang == "Hindi":
            return make_answer("Poora Badan Dard", [("Thakan","Din bhar zyada kaam karne se poora sharir thak jata hai."),("Viral","Mausam badalne se halka virus lag jata hai, badan dard ke saath halka bukhar bhi hota hai."),("Paani ki Kami","Paani kam peene se muscles me dard hone lagta hai.")], [("Tez Bukhar","Bukhar 102 se upar ho, toh turant doctor ko dikhayein."),("Saans me Dikkat","Saans lene me takleef ho, toh der mat karein.")], [("Poora Aaram","Aaj bhari kaam band karke poora aaram kijiye."),("Garam Paani Se Nahaein","Gungune paani se nahane se muscles ko aaram milega."),("Gunguna Paani Piyein","Din bhar thoda-thoda gunguna paani piyein.")], ("Roz Walk","Roz 30 minute halki walk se muscles mazboot hote hain."), "Aapka badan dard zyada tar thakan aur viral ki wajah se lag raha hai, aaj aaram kijiye.", lang)
        else:
            return make_answer("Body Pain", [("Tiredness","Working too much makes the whole body tired."),("Viral Infection","Change in weather causes mild virus, with body pain and mild fever."),("Less Water","Drinking less water causes pain in muscles.")], [("High Fever","If fever goes above 102, see a doctor immediately."),("Breathing Problem","If you feel difficulty in breathing, do not wait.")], [("Full Rest","Stop all heavy work today and take full rest."),("Warm Water Bath","Bathing with warm water will relax muscles."),("Warm Water","Keep drinking warm water in small sips.")], ("Daily Walk","Walking 30 minutes daily makes muscles strong."), "Your body pain seems mostly because of tiredness and viral, take rest today.", lang)
    if "fever" in text or "bukhar" in text:
        if lang == "Hindi":
            return make_answer("Bukhar", [("Viral Fever","Mausam badalne se virus se bukhar aa jata hai."),("Sardi","Gale me kharash aur sardi ke saath bhi halka bukhar aa sakta hai."),("Paani ki Kami","Paani kam peene se sharir garam ho jata hai.")], [("Tez Bukhar","Bukhar 102 se upar ho, toh turant doctor ko dikhayein."),("Ulti / Chakkar","Ulti ya chakkar aaye, toh der mat karein.")], [("Aaram Karein","Poora aaram karein."),("Thandi Patti","Sar pe thande paani ki patti rakhein."),("Gunguna Paani","Thoda-thoda karke gunguna paani piyein.")], ("Tulsi Kadha","Tulsi aur adrak ka kadha peene se bukhar me aaram milta hai."), "Aapka bukhar abhi shuru hua lag raha hai, 1 din aaram karke dekhiye.", lang)
        else:
            return make_answer("Fever", [("Viral Fever","Change in weather causes viral infection."),("Cold","Throat infection and cold can also give mild fever."),("Less Water","Drinking less water makes body hot.")], [("High Fever","If fever goes above 102, see a doctor immediately."),("Vomiting / Dizziness","If you feel vomiting or dizziness, do not wait.")], [("Take Rest","Take full rest."),("Cold Sponge","Keep cold wet cloth on forehead."),("Warm Water","Drink warm water in small sips.")], ("Tulsi Kadha","Tulsi and ginger kadha gives relief in fever."), "Your fever seems in starting stage, take rest for 1 day.", lang)
    if "cold" in text or "cough" in text or "khansi" in text or "sardi" in text or "throat" in text or "gala" in text or "gale" in text:
        if lang == "Hindi":
            return make_answer("Sardi-Khansi", [("Viral Infection","Mausam badalne se gale me virus lag jata hai."),("Thanda Paani","Thanda paani ya ice-cream se gala kharab ho jata hai."),("Dhool","Dhool-mitti se allergy ho jati hai.")], [("Saans me Dikkat","Saans lene me takleef ho, toh turant doctor ko dikhayein."),("Khoon Wali Khansi","Khansi me khoon aaye, toh der mat karein.")], [("Garam Paani","Din bhar gunguna paani piyein."),("Haldi Doodh","Raat ko haldi wala garam doodh piyein."),("Bhapa","Garam paani ka bhapa lene se naak khul jati hai.")], ("Tulsi-Adrak","Tulsi aur adrak ki chai se gale ko aaram milta hai."), "Aapki sardi-khansi abhi shuru hui lag rahi hai, 2 din garam cheezein lijiye.", lang)
        else:
            return make_answer("Cold-Cough", [("Viral Infection","Change in weather causes virus in throat."),("Cold Water","Cold water or ice-cream makes throat bad."),("Dust Allergy","Dust causes allergy and cough starts.")], [("Breathing Problem","If you feel difficulty in breathing, see doctor immediately."),("Blood in Cough","If blood comes in cough, do not wait.")], [("Warm Water","Drink warm water through the day."),("Turmeric Milk","Drink warm turmeric milk at night."),("Steam","Take steam from hot water.")], ("Tulsi-Ginger","Tulsi and ginger tea gives relief to throat."), "Your cold-cough seems in starting stage, take warm things for 2 days.", lang)
    if "stomach" in text or "pet" in text or "gas" in text or "ulti" in text or "vomit" in text or "dast" in text or "loose" in text or "diarrhea" in text:
        if lang == "Hindi":
            return make_answer("Pet Dard", [("Gas","Bahar ka khana ya jaldi khane se pet me gas ban jati hai."),("Acidity","Masaledar khana ya khaali pet rehne se acidity ho jati hai."),("Kabz","Paani kam peene se kabz hota hai.")], [("Tez Dard","Pet me bahut tez dard ho, toh turant doctor ko dikhayein."),("Khoon","Potty me khoon aaye, toh der mat karein.")], [("Halka Khana","Aaj khichdi, dahi jaisa halka khana khayein."),("ORS Paani","Thoda-thoda karke ORS piyein."),("Walk","Khane ke baad 10 minute halki walk karein.")], ("Ajwain Paani","Ajwain ka paani gas me turant aaram deta hai."), "Aapka pet dard gas aur acidity se lag raha hai, aaj halka khana khayein.", lang)
        else:
            return make_answer("Stomach Problem", [("Gas","Eating outside food causes gas."),("Acidity","Spicy food or empty stomach causes acidity."),("Constipation","Drinking less water causes constipation.")], [("Severe Pain","If stomach pain is very severe, see doctor immediately."),("Blood","If blood comes in stool, do not wait.")], [("Light Food","Eat light food like khichdi, curd."),("ORS Water","Drink ORS in small sips."),("Walk","Walk 10 minutes after food.")], ("Ajwain Water","Ajwain water gives instant relief in gas."), "Your stomach pain seems due to gas and acidity, eat light food today.", lang)
    if "chest" in text or "seene" in text or "saans" in text or "breath" in text:
        if lang == "Hindi":
            return make_answer("Seene Me Dard", [("Gas","Pet ki gas upar chadhne se seene me bhari pan lagta hai."),("Sardi","Sardi aur dhool se seene me jakdan ho jati hai."),("Thakan","Zyada kaam karne se saans phoolne lagti hai.")], [("Bahut Tez Dard","Seene me bahut tez dard ho, toh turant 108 pe call karein."),("Pasina","Seene ke dard ke saath pasina aaye, toh turant hospital jayein.")], [("Seedha Bethein","Seedha beth jayein, kapde dheele kar dein."),("Hawa","Khidki khol dein."),("Gunguna Paani","Thoda-thoda gunguna paani piyein.")], ("Dhool Se Bachein","Dhool aur dhuein se door rahein."), "Aapke seene ka dard gas aur sardi se lag raha hai, lekin dard tez hai toh turant doctor ko dikhayein.", lang)
        else:
            return make_answer("Chest Problem", [("Gas","Gas from stomach goes up and causes heaviness in chest."),("Cold","Cold and dust causes tightness in chest."),("Tiredness","Too much work causes breathlessness.")], [("Severe Pain","If chest pain is very severe, call 108 immediately."),("Sweating","If sweating with chest pain, go to hospital fast.")], [("Sit Straight","Sit straight, loosen clothes."),("Air","Open windows."),("Warm Water","Drink warm water in small sips.")], ("Avoid Dust","Stay away from dust and smoke."), "Your chest pain seems due to gas and cold, but if pain is severe, see doctor immediately.", lang)
    if "leg" in text or "pair" in text or "knee" in text or "ghutna" in text or "hand" in text or "haath" in text or "joint" in text or "shoulder" in text or "kandha" in text:
        if lang == "Hindi":
            return make_answer("Haath-Pair Dard", [("Thakan","Zyada chalne se haath-pair me dard ho jata hai."),("Calcium ki Kami","Calcium ki kami se ghutno me dard hota hai."),("Galat Bethna","Galat bethne se ghutne pe zor padta hai.")], [("Sujan","Bahut sujan aa jaye, toh doctor ko dikhayein."),("Tez Dard","Dard 2 din se zyada rahe, toh der mat karein.")], [("Aaram","Us pair ko aaram dein."),("Garam Sek","10 minute garam sek karein."),("Pair Upar Rakhein","Pair ko takiye pe upar rakh ke letein.")], ("Doodh Piyein","Roz 1 gilas doodh piyein."), "Aapka haath-pair ka dard thakan aur calcium ki kami se lag raha hai.", lang)
        else:
            return make_answer("Leg / Joint Pain", [("Tiredness","Walking too much causes leg pain."),("Calcium Deficiency","Lack of Calcium causes knee pain."),("Wrong Posture","Wrong sitting puts pressure on knee.")], [("Swelling","If too much swelling, see doctor."),("Severe Pain","If pain stays more than 2 days, do not wait.")], [("Rest","Give rest to that leg."),("Hot Compress","Apply warm cloth for 10 minutes."),("Raise Leg","Keep leg raised on pillow.")], ("Drink Milk","Drink 1 glass milk daily."), "Your leg pain seems due to tiredness and calcium deficiency.", lang)
    if "eye" in text or "aankh" in text or "ankh" in text:
        if lang == "Hindi":
            return make_answer("Aankh Ki Problem", [("Phone / Dhool","Zyada phone dekhne se aankh me jalan hoti hai."),("Neend ki Kami","Neend poori na hone se aankh laal ho jati hai."),("Allergy","Dhool se aankh me allergy ho jati hai.")], [("Dikhai Kam","Dikhai kam ho, toh turant doctor ko dikhayein."),("Pus","Aankh se pus aaye, toh der mat karein.")], [("Aankh Mat Maslein","Aankh ko maslein nahi, saaf paani se dhoyein."),("Phone Kam","Phone kam dekhiye."),("Thandi Patti","Aankh pe thandi patti rakhein.")], ("Dhoop Se Bachein","Dhoop me chashma pehnein."), "Aapki aankh ki problem phone aur dhool ki wajah se lag rahi hai.", lang)
        else:
            return make_answer("Eye Problem", [("Phone / Dust","Too much phone causes burning in eyes."),("Less Sleep","Less sleep makes eyes red."),("Allergy","Dust causes allergy in eyes.")], [("Less Vision","If vision is less, see doctor immediately."),("Pus","If pus comes from eyes, do not wait.")], [("Do Not Rub","Do not rub eyes, wash with clean water."),("Less Phone","Use phone less."),("Cold Cloth","Keep cold cloth on eyes.")], ("Avoid Sun","Wear glasses in sunlight."), "Your eye problem seems due to phone and dust.", lang)
    if "ear" in text or "kaan" in text:
        if lang == "Hindi":
            return make_answer("Kaan Me Dard", [("Sardi","Sardi ke saath kaan me dard ho jata hai."),("Paani","Nahaate time kaan me paani jaane se dard hota hai."),("Mail","Kaan me mail jamne se dard hota hai.")], [("Sunai Kam","Sunai kam de, toh doctor ko dikhayein."),("Tez Bukhar","Kaan dard ke saath tez bukhar ho, toh der mat karein.")], [("Kuch Mat Dalein","Kaan me teeli mat dalein."),("Garam Sek","Halka garam sek karein."),("Aaram","Thodi der aaram karein.")], ("Kaan Saaf Rakhein","Kaan ko saaf aur sukha rakhein."), "Aapke kaan ka dard sardi ki wajah se lag raha hai.", lang)
        else:
            return make_answer("Ear Pain", [("Cold","Cold causes ear pain."),("Water","Water going in ear during bath causes pain."),("Wax","Wax in ear causes pain.")], [("Less Hearing","If hearing is less, see doctor."),("High Fever","If high fever with ear pain, do not wait.")], [("Do Not Insert","Do not insert anything in ear."),("Warm Compress","Apply light warm compress."),("Rest","Take rest.")], ("Keep Ear Clean","Keep ear clean and dry."), "Your ear pain seems due to cold.", lang)
    if "tooth" in text or "daant" in text or "dant" in text:
        if lang == "Hindi":
            return make_answer("Daant Me Dard", [("Keeda","Daant me keeda lagne se dard hota hai."),("Thanda-Garam","Thanda-garam khane se daant me jhanjhanahat hoti hai."),("Masuda","Masude me sujan se daant dukhne lagta hai.")], [("Sujan","Gaalo pe sujan aa jaye, toh doctor ko dikhayein."),("Dard Na Ruke","Dard 2 din se na ruke, toh der mat karein.")], [("Namak Paani","Gungune namak paani se kullla karein."),("Laung","Laung ka tel lagayein."),("Thanda Mat Khayein","Thanda aur meetha mat khayein.")], ("Brush","Din me 2 baar brush karein."), "Aapke daant ka dard keede aur masude ki sujan se lag raha hai.", lang)
        else:
            return make_answer("Tooth Pain", [("Cavity","Cavity in tooth causes pain."),("Cold-Hot","Cold-hot food causes sensitivity."),("Gum Swelling","Gum swelling causes tooth pain.")], [("Swelling","If cheek swells, see doctor."),("Pain Not Stopping","If pain does not stop in 2 days, do not wait.")], [("Salt Water","Gargle with warm salt water."),("Clove Oil","Apply clove oil."),("Avoid Cold","Avoid cold and sweet.")], ("Brush","Brush 2 times a day."), "Your tooth pain seems due to cavity and gum swelling.", lang)
    # PHOTO / ALLERGY / DAANE / CHOT - PHOTO KE HISAAB SE SAHI JAWAB
    if "daane" in text or "rash" in text or "khujli" in text or "itching" in text:
        if lang == "Hindi":
            return make_answer("Daane / Khujli", [("Allergy","Naye sabun, kapde ya dhool se allergy ho jati hai."),("Garmi","Garmi me pasina jamne se daane nikal aate hain."),("Infection","Saaf-safai na rakhne se infection ho jata hai.")], [("Pus","Daano se pus nikle, toh doctor ko dikhayein."),("Tez Bukhar","Daano ke saath tez bukhar ho, toh der mat karein."),("Saans Me Dikkat","Saans me dikkat ho toh turant 108 pe call karein.")], [("Khujlayein Nahi","Daano ko khujlayein nahi, isse infection badhta hai."),("Saaf Rakhein","Saaf paani se dho kar sukha rakhein."),("Thanda Paani","Thande paani se sek karein."),("Nariyal Tel","Halka nariyal tel lagayein.")], ("Saaf Kapde","Roz saaf kapde pehnein, paseene wale kapde turant badlein."), "Aapke daane allergy ya garmi ki wajah se lag rahe hain. 2 din me kam na hon toh doctor ko dikhayein.", lang)
        else:
            return make_answer("Rash / Itching", [("Allergy","New soap, clothes or dust causes allergy."),("Heat","Sweat causes rashes in heat."),("Infection","Lack of cleanliness causes infection.")], [("Pus","If pus comes, see doctor."),("High Fever","If high fever with rashes, do not wait."),("Breathing Problem","If breathing problem, call 108 immediately.")], [("Do Not Scratch","Do not scratch, it increases infection."),("Keep Clean","Wash with clean water and keep dry."),("Cold Water","Apply cold water compress."),("Coconut Oil","Apply light coconut oil.")], ("Clean Clothes","Wear clean clothes daily, change sweaty clothes immediately."), "Your rash seems due to allergy or heat. If not better in 2 days, see doctor.", lang)
    if "chot" in text or "zakhm" in text or "wound" in text or "injury" in text or "kat" in text or "cut" in text:
        if lang == "Hindi":
            return make_answer("Chot / Zakhm", [("Girna","Girne ya takrane se chot lag jati hai."),("Tez Cheez","Chaku ya kaanch se katne se zakhm ho jata hai."),("Jalan","Garam cheez se jalne se chot lagti hai.")], [("Bahut Khoon","Khoon ruk na raha ho, toh turant 108 pe call karein."),("Gehri Chot","Gehri chot ho ya haddi dikh rahi ho, toh turant hospital jayein."),("Bukhar","Chot ke baad bukhar aaye, toh doctor ko dikhayein.")], [("Saaf Paani Se Dhoyein","Chot ko saaf paani se dhoyein, gande paani se nahi."),("Khoon Rokein","Saaf kapde se chot ko dabake rakhein, 10 minute tak mat hatayein."),("Betadine Lagayein","Halka Betadine lagayein, haldi / mitti / toothpaste mat lagayein."),("Patti Bandhein","Saaf patti bandhein.")], ("Saaf Rakhein","Chot ko ganda mat hone dein, roz patti badlein."), "Aapki chot ko saaf rakhna sabse zaroori hai. Gehri chot ho toh turant hospital jayein.", lang)
        else:
            return make_answer("Injury / Wound", [("Fall","Falling or hitting causes injury."),("Sharp Object","Knife or glass cut causes wound."),("Burn","Hot thing causes burn injury.")], [("Heavy Bleeding","If bleeding is not stopping, call 108 immediately."),("Deep Wound","If wound is deep or bone is visible, go to hospital immediately."),("Fever","If fever after injury, see doctor.")], [("Wash With Clean Water","Wash wound with clean water, not dirty water."),("Stop Bleeding","Press with clean cloth for 10 minutes, do not remove."),("Apply Betadine","Apply light Betadine, do not apply haldi / mud / toothpaste."),("Bandage","Tie clean bandage.")], ("Keep Clean","Keep wound clean, change bandage daily."), "Keeping your wound clean is most important. For deep wound, go to hospital immediately.", lang)
    if "allergy" in text:
        if lang == "Hindi":
            return make_answer("Allergy", [("Dhool / Sabun","Dhool, naye sabun ya perfume se allergy ho jati hai."),("Khana","Kisi khane ki cheez se allergy ho sakti hai."),("Dawai","Kisi dawai se bhi allergy ho sakti hai.")], [("Saans Me Dikkat","Saans me dikkat ho toh turant 108 pe call karein."),("Chehra Sujna","Chehra ya hoth suj jayein toh turant hospital jayein.")], [("Khujlayein Nahi","Khujlayein nahi."),("Trigger Se Door Rahein","Jis cheez se allergy hui, usse door rahein."),("Thanda Paani","Thande paani se sek karein.")], ("Saaf Kapde","Roz saaf kapde pehnein."), "Aapki allergy dhool ya naye sabun ki wajah se lag rahi hai.", lang)
        else:
            return make_answer("Allergy", [("Dust / Soap","Dust, new soap or perfume causes allergy."),("Food","Some food can cause allergy."),("Medicine","Some medicine can also cause allergy.")], [("Breathing Problem","If breathing problem, call 108 immediately."),("Face Swelling","If face or lips swell, go to hospital immediately.")], [("Do Not Scratch","Do not scratch."),("Avoid Trigger","Stay away from the thing that caused allergy."),("Cold Water","Apply cold water compress.")], ("Clean Clothes","Wear clean clothes daily."), "Your allergy seems due to dust or new soap.", lang)
    if "chakkar" in text or "dizz" in text or "kamzori" in text or "weak" in text or "neend" in text or "sleep" in text:
        if lang == "Hindi":
            return make_answer("Chakkar / Kamzori", [("Khoon ki Kami","Khoon ki kami se chakkar aata hai."),("Bhook","Bhooke rehne se chakkar aata hai."),("Neend ki Kami","Neend poori na hone se kamzori lagti hai.")], [("Behosh","Behosh ho jayein, toh turant doctor ko dikhayein."),("Seene Me Dard","Chakkar ke saath seene me dard ho, toh 108 pe call karein.")], [("Beth Jayein","Chakkar aaye toh turant beth jayein."),("Paani Piyein","Thoda-thoda paani piyein."),("Kuch Khayein","Halka kuch kha lein.")], ("Paalak Khayein","Roz paalak aur gud khayein."), "Aapka chakkar khoon ki kami aur neend ki kami se lag raha hai.", lang)
        else:
            return make_answer("Dizziness / Weakness", [("Low Blood","Low blood causes dizziness."),("Hunger","Staying hungry causes dizziness."),("Less Sleep","Less sleep causes weakness.")], [("Faint","If you faint, see doctor immediately."),("Chest Pain","If chest pain with dizziness, call 108.")], [("Sit Down","Sit down immediately when dizzy."),("Drink Water","Drink water in small sips."),("Eat Something","Eat something light.")], ("Eat Palak","Eat palak and gud daily."), "Your dizziness seems due to low blood and less sleep.", lang)
    clean = user_text.strip()
    if lang == "Hindi":
        return f"""Aapki takleef samajh sakte hain, aaram kijiye.

**Sambhav Karan - {clean} ki wajah:**

- **Thakan:** Neend poori na hone ya zyada kaam karne se {clean} me takleef hone lagti hai.
- **Infection:** Mausam badalne se {clean} me infection ho jata hai.
- **Kamzori:** Paani kam peene se {clean} me kamzori aur dard mehsoos hota hai.

**Khatre Ke Lakshan:**

- **Tez Dard:** Agar {clean} me bahut tez dard ho, toh turant doctor ko dikhayein.
- **Bukhar / Sujan:** {clean} ke saath tez bukhar ya sujan ho, toh der mat karein.

**Abhi Kya Karein:**

- **Aaram Karein:** {clean} wali jagah ko aaram dein.
- **Garam Sek:** {clean} pe halka garam sek karein.
- **Gunguna Paani Piyein:** Din bhar gunguna paani piyein.

**Sehat Tip:**

- **Roz Walk:** Roz 30 minute halki walk se {clean} ki takleef kam hoti hai.

Aapki takleef - {clean} - zyada tar thakan ki wajah se lag rahi hai, 1-2 din aaram kijiye.

Kya aap doctor se baat karna chahengi?"""
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

def ask_reply(user_text, sidebar_lang, placeholder):
    real_lang = detect_language(user_text)
    if not is_health_related(user_text):
        msg = out_of_context_msg(real_lang)
        placeholder.markdown(msg)
        return msg
    instant = get_instant_answer(user_text, real_lang)
    placeholder.markdown(instant)
    return instant

def ask_reply_photo(photo_keyword, photo_desc, placeholder):
    # PHOTO KE LIYE - OUT OF CONTEXT CHECK NAHI, SIDEBAR WALI BHASHA
    real_lang = "Hindi" if IS_HINDI else "English"
    full_text = f"{photo_keyword} {photo_desc}".strip()
    instant = get_instant_answer(full_text, real_lang)
    placeholder.markdown(instant)
    return instant

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
        if "sirf health" not in st.session_state.messages[-1]["content"].lower() and "only help with health" not in st.session_state.messages[-1]["content"].lower():
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
    with st.form("chat_form", clear_on_submit=True):
        chat_text = st.text_input("Type...", label_visibility="collapsed", placeholder="Apni takleef likhein... / Write your symptom..." if IS_HINDI else "Write your symptom...")
        submitted = st.form_submit_button("➤ Send", use_container_width=True)
    if submitted and chat_text.strip() != "":
        st.session_state.messages.append({"role": "user", "content": chat_text})
        st.session_state.doctor_asked = False
        with st.chat_message("assistant"):
            placeholder = st.empty()
            reply = ask_reply(chat_text, lang, placeholder)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()
    if st.button("🧹 Clear Chat" if not IS_HINDI else "🧹 Chat Saaf Karein", use_container_width=True):
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
        # PHOTO PROMPT - PHOTO KIS CHEEZ KI HAI?
        st.write("📸 Ye photo kis cheez ki hai?" if IS_HINDI else "📸 What is this photo of?")
        photo_type = st.radio("Photo Type", ["Allergy / Daane", "Chot / Zakhm", "Khujli / Rash"], label_visibility="collapsed", horizontal=True, key="photo_type")
        photo_desc = st.text_input("Photo me kya dikh raha hai? (optional)" if IS_HINDI else "What is visible in photo? (optional)", placeholder="Jaise: haath pe laal daane..." if IS_HINDI else "Like: red daane on hand...", key="photo_desc")
        if st.button("📸 Photo Bhejein" if IS_HINDI else "📸 Send Photo", use_container_width=True):
            # Photo ke hisaab se keyword banao
            if "Chot" in photo_type:
                kw = "chot zakhm"
            elif "Khujli" in photo_type:
                kw = "khujli rash"
            else:
                kw = "allergy daane"
            photo_text = f"{kw} {photo_desc}".strip()
            st.session_state.messages.append({"role": "user", "content": photo_text, "type": "image", "image": uploaded_photo})
            st.session_state.doctor_asked = False
            with st.chat_message("assistant"):
                placeholder = st.empty()
                reply = ask_reply_photo(kw, photo_desc, placeholder)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()
    if audio_input and st.session_state.get("last_audio_id") != str(audio_input):
        st.session_state["last_audio_id"] = str(audio_input)
        with st.spinner("Sun rahe hain..." if IS_HINDI else "Listening..."):
            voice_text = speech_to_text(audio_input.read())
        if voice_text and not voice_text.startswith("ERROR:"):
            st.success(f"🗣️ Aapne bola: {voice_text}" if IS_HINDI else f"🗣️ You said: {voice_text}")
            st.session_state.messages.append({"role": "user", "content": voice_text})
            st.session_state.doctor_asked = False
            with st.chat_message("assistant"):
                placeholder = st.empty()
                reply = ask_reply(voice_text, lang, placeholder)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()
        else:
            st.warning("Awaz samajh nahi aayi, dobara boliye." if IS_HINDI else "Could not understand, please speak again.")
    show_floating_banner()

elif menu in ["💊 Medicine Reminder", "💊 दवाई रिमाइंडर"]:
    if IS_HINDI:
        st.title("💊 दवाई रिमाइंडर")
        st.write("Dawai ka time set kijiye, time hone pe app yaad dilayega.")
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
                st.session_state.reminders.append({"name": med_name.strip(), "time": time_str, "display": display_time, "days": med_days, "hour24": hour_24, "minute": minute})
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
        today = datetime.date.today().strftime("%Y%m%d")
        hh = str(r.get("hour24", 9)).zfill(2)
        mm = str(r.get("minute", "00")).zfill(2)
        gcal_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={urllib.parse.quote(r['name'] + ' - Dawa Leni Hai')}&dates={today}T{hh}{mm}00/{today}T{hh}{mm}00&recur=RRULE:FREQ=DAILY;COUNT={r['days']}&details={urllib.parse.quote('Daily Medicine Reminder - ' + r['name'])}"
        st.link_button("📅 Google Calendar me Add Karo - Daily Repeat" if IS_HINDI else "📅 Add to Google Calendar - Daily Repeat", gcal_url, use_container_width=True)
    if st.session_state.reminders:
        if st.button("🗑️ सारे Reminder Delete Karein" if IS_HINDI else "🗑️ Delete All Reminders", use_container_width=True):
            st.session_state.reminders = []
            st.rerun()
    else:
        st.write("Abhi koi reminder nahi hai." if IS_HINDI else "No reminders yet.")
    st.markdown("---")
    if IS_HINDI:
        st.info("ℹ️ **Note:** Google Calendar wala button dabane pe Calendar khulega, wahan Daily Repeat ke saath save kar lo. Roz usi time pe reminder ayega, app band ho tab bhi.")
    else:
        st.info("ℹ️ **Note:** Press Google Calendar button, Calendar will open, save with Daily Repeat. You will get reminder daily at same time, even if app is closed.")
    show_floating_banner()

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
        st.write("Agar takleef zyada hai toh apne najdik wale PHC / CHC me jayein.")
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
    show_floating_banner()

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
        st.markdown("### 🆘 Apni Emergency Likho / Bolo")
        st.write("Jaise: haath kat gaya, khoon aa raha hai, saans nahi aa rahi")
        em_text = st.text_input("Emergency likho...", placeholder="Emergency likho - jaise haath kat gaya...", key="em_text")
        em_audio = st.audio_input("Emergency Bolo", key="em_mic")
        em_final = em_text
        if em_audio and st.session_state.get("last_em_audio") != str(em_audio):
            st.session_state["last_em_audio"] = str(em_audio)
            vt = speech_to_text(em_audio.read())
            if vt and not vt.startswith("ERROR:"):
                st.success(f"🗣️ Aapne bola: {vt}")
                em_final = vt
        if st.button("🚨 Emergency Steps Dekho", use_container_width=True):
            e = (em_final or "").lower()
            if e.strip()=="":
                st.warning("Pehle apni emergency likho ya bolo.")
            elif not is_health_related(e) and "kat" not in e and "gir" not in e and "accident" not in e:
                st.warning("Main sirf health, chot aur allergy se related help kar sakti hu.")
            elif "kat" in e or "khoon" in e or "blood" in e or "chot" in e:
                st.error("**KAT / KHOON - Ambulance Aane Tak:**\n1. 108 pe call karo\n2. Saaf kapde se zor se dabao, kapda mat hatao\n3. Haath / pair upar rakho\n4. Patient ko hilao mat\n5. Ambulance tak dabaye rakho, saans check karte raho")
            elif "saans" in e or "breath" in e or "gala" in e:
                st.error("**SAANS PROBLEM - Ambulance Aane Tak:**\n1. 108 pe call karo\n2. Patient ko seedha bethao, letayein nahi\n3. Gale ke kapde dheele kar do\n4. Khidki khol do, bheed mat lagao\n5. Zabardasti paani mat pilao")
            elif "bukhar" in e or "fever" in e:
                st.error("**TEZ BUKHAR - Ambulance Aane Tak:**\n1. Thandi patti rakho\n2. Bhari kapde hata do\n3. Thoda-thoda paani pilate raho\n4. Bina doctor ke tez dawai mat do")
            elif "ulti" in e or "vomit" in e:
                st.error("**ULTI - Ambulance Aane Tak:**\n1. Patient ko ek side me letayein\n2. Thoda-thoda ORS pilayein\n3. Khana mat dein\n4. Ulti saans me na jaye, dhyaan rakhein")
            elif "behosh" in e or "faint" in e:
                st.error("**BEHOSH - Ambulance Aane Tak:**\n1. Saans check karo\n2. Saans chal rahi hai toh ek side me letayein\n3. Paani / khana mat pilayein\n4. Turant 108 pe call karo")
            else:
                st.error("**EMERGENCY - Ambulance Aane Tak:**\n1. Ghabrao mat, 108 pe call karo\n2. Patient ko seedha litao\n3. Khoon aa raha hai toh saaf kapde se dabao\n4. Kuch khilao-pilao mat\n5. Ambulance aane tak patient ke paas raho, saans check karte raho")
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
        st.markdown("#### 5. 🐍 Saanp / Kutta Kaat Le Toh")
        st.write("- **Dhoyein:** Kaati hui jagah ko saaf paani aur sabun se dhoyein")
        st.write("- **Hilaayein Nahi:** Us haath / pair ko hilayein nahi, seedha rakhein")
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
        st.markdown("### 🆘 Write / Speak Your Emergency")
        st.write("Like: hand cut, bleeding, breathing problem")
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
            elif not is_health_related(e) and "cut" not in e and "fall" not in e and "accident" not in e:
                st.warning("I can only help with health, injury and allergy related problems.")
            elif "cut" in e or "blood" in e or "bleed" in e or "injury" in e:
                st.error("**CUT / BLEEDING - Till Ambulance Arrives:**\n1. Call 108\n2. Press firmly with clean cloth, do not remove cloth\n3. Keep hand / leg up\n4. Do not move patient\n5. Keep pressing, keep checking breathing")
            elif "breath" in e or "choke" in e:
                st.error("**BREATHING PROBLEM - Till Ambulance Arrives:**\n1. Call 108\n2. Make patient sit straight, do not lie down\n3. Loosen clothes around neck\n4. Open windows, do not crowd\n5. Do not force water")
            elif "fever" in e:
                st.error("**HIGH FEVER - Till Ambulance Arrives:**\n1. Keep cold wet cloth\n2. Remove heavy blanket\n3. Give water in small sips\n4. Do not give strong medicine without doctor")
            elif "vomit" in e:
                st.error("**VOMITING - Till Ambulance Arrives:**\n1. Make patient lie on one side\n2. Give ORS in small sips\n3. Do not give food\n4. Do not let vomit go in lungs")
            elif "faint" in e or "unconscious" in e:
                st.error("**UNCONSCIOUS - Till Ambulance Arrives:**\n1. Check breathing\n2. If breathing, lie on one side\n3. Do not give water / food\n4. Call 108 immediately")
            else:
                st.error("**EMERGENCY - Till Ambulance Arrives:**\n1. Do not panic, call 108\n2. Lay patient straight\n3. If bleeding, press with clean cloth\n4. Do not give food / water\n5. Stay with patient, keep checking breathing")
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
        st.markdown("#### 5. 🐍 Snake / Dog Bite")
        st.write("- **Wash:** Wash bite area with clean water and soap")
        st.write("- **Do Not Move:** Do not move that hand / leg, keep it straight")
        st.write("- **Hospital Fast:** Call 108 and go to hospital fast, do not waste time in jhaad-phoonk")
        st.markdown("#### 6. 🤕 Unconscious Person")
        st.write("- **Check:** First check if breathing is going on or not")
        st.write("- **Side:** If breathing is there, make them lie on one side")
        st.write("- **No Water:** Do not give water / food to unconscious person")
        st.write("- **Call Fast:** Call 108 immediately")
    show_floating_banner()

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
    show_floating_banner()

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
    show_floating_banner()

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
    show_floating_banner()

elif menu in ["ℹ️ About App", "ℹ️ ऐप के बारे में"]:
    if IS_HINDI:
        st.title("ℹ️ ऐप के बारे में - Sehat Saathi")
        st.write("Sehat Saathi **sabke liye** banaya gaya hai - bachon se lekar bujurgon tak, gaon ho ya shehar, sabhi log iska use kar sakte hain.")
        st.markdown("---")
        st.markdown("### 🩺 Ye App Kya Hai?")
        st.write("Sehat Saathi ek health helper app hai. Jab aapko halki takleef hoti hai - jaise sar dard, bukhar, sardi, pet dard - aur aapko samajh nahi aata ki kya karein, toh ye app turant aapko samjhata hai ki ye kis wajah se ho sakta hai, kab danger hai aur abhi kya karna chahiye.")
        st.write("Ye app doctor ki jagah nahi leta, ye bas pehli madad karta hai, taaki aap ghabrayein nahi aur sahi time pe sahi faisla le sakein.")
        st.markdown("---")
        st.markdown("### ✨ Features - Is App Me Kya-Kya Hai?")
        st.write("- **💬 Chat Se Baat Karein:** Apni takleef likh ke bhejein, jaise 'mere sar me dard hai', app turant jawab dega.")
        st.write("- **🎤 Bol Ke Batayein:** Likhna nahi aata toh mic dabake bol dijiye, app aapki awaz sun ke samajh jayega.")
        st.write("- **📷 Photo Bhejein:** Haath pe daane, chot ya rash hai toh photo bhej dijiye, app dekh ke batayega.")
        st.write("- **💊 Medicine Reminder:** Dawai ka time set kijiye, time hone pe app yaad dilayega, dawai kabhi miss nahi hogi.")
        st.write("- **👨‍⚕️ Doctor Se Baat Karein:** Agar takleef zyada hai toh yahan se sarkari doctor, eSanjeevani aur 104 helpline pe baat kar sakte hain.")
        st.write("- **🚨 Emergency:** Emergency me kya karna hai, kis number pe call karna hai, sab ek jagah mil jayega.")
        st.write("- **💡 Health Tips:** Roz ka routine, khana-peena, neend, walk - sabke aasan tips.")
        st.write("- **⚖️ BMI Calculator:** Apna wajan sahi hai ya nahi, ye check kar sakte hain.")
        st.write("- **🏛️ Government Schemes:** Ayushman, Jan Aushadhi jaisi sarkari yojnaon ki poori jankari FREE me.")
        st.write("- **🌐 Hindi / English:** App ko Hindi ya English, dono me chala sakte hain.")
        st.markdown("---")
        st.markdown("### ❤️ Isse Fayda Kya Hoga?")
        st.write("- **Time Bachega:** Chhoti takleef ke liye baar-baar hospital ke chakkar nahi lagane padenge, pehle ghar pe hi pata chal jayega.")
        st.write("- **Paise Bachenge:** Sarkari FREE ilaj aur sasti dawai ki jankari milegi.")
        st.write("- **Ghabrahat Kam Hogi:** Takleef hone pe pata chal jayega ki ye normal hai ya danger hai, isse dar kam lagega.")
        st.write("- **Dawai Yaad Rahegi:** Buzurgon aur bachon ki dawai ka time kabhi miss nahi hoga.")
        st.write("- **Sabke Liye Aasan:** Jo log padhna-likhna kam jaante hain, wo bol ke ya photo bhej ke bhi use kar sakte hain.")
        st.markdown("---")
        st.markdown("### 📱 Kaise Use Karein? - Step By Step")
        st.write("**Step 1:** Left side se apni bhasha chunein - Hindi ya English.")
        st.write("**Step 2:** Home pe jake neeche wale box me apni takleef likhein, jaise 'mere pet me dard hai', aur Send dabayein.")
        st.write("**Step 3:** App aapko batayega - Sambhav Karan kya hain, Khatre Ke Lakshan kya hain, aur Abhi Kya Karna Hai.")
        st.write("**Step 4:** Agar app puche 'Kya aap doctor se baat karna chahengi?' aur takleef zyada lage, toh Yes dabake doctor se baat karein.")
        st.write("**Step 5:** Dawai ka time yaad rakhne ke liye Medicine Reminder me jake dawai ka naam aur time set karein.")
        st.write("**Step 6:** Emergency ho toh Emergency wale page pe jake 108 ya 104 pe call karein.")
        st.write("**Step 7:** Health Tips aur Government Schemes wala page roz ek baar dekh lein, bahut kaam ki cheezein hain.")
        st.markdown("---")
        st.info("⚠️ **Zaroori Baat:** Ye app sirf jankari aur pehli madad ke liye hai. Ye doctor ki jagah nahi le sakta. Agar takleef zyada hai, bukhar 102 se upar hai, saans me dikkat hai ya chot lagi hai, toh turant doctor ko dikhayein ya 108 pe call karein.")
    else:
        st.title("ℹ️ About App - Sehat Saathi")
        st.write("Sehat Saathi is made for **everyone** - from children to elderly, village or city, anyone can use it.")
        st.markdown("---")
        st.markdown("### 🩺 What Is This App?")
        st.write("Sehat Saathi is a health helper app. When you have a small problem - like headache, fever, cold, stomach pain - and you do not understand what to do, this app immediately tells you why it can happen, when it is dangerous, and what you should do now.")
        st.write("This app does not replace a doctor, it only gives first help, so you do not panic and take the right decision at the right time.")
        st.markdown("---")
        st.markdown("### ✨ Features - What Is In This App?")
        st.write("- **💬 Chat:** Write your problem, like 'my head is paining', app will reply immediately.")
        st.write("- **🎤 Speak:** If you cannot type, press mic and speak, app will listen and understand.")
        st.write("- **📷 Send Photo:** If you have rashes, injury or daane on hand, send a photo, app will check and tell you.")
        st.write("- **💊 Medicine Reminder:** Set medicine time, app will remind you on time, you will never miss medicine.")
        st.write("- **👨‍⚕️ Talk To Doctor:** If problem is more, from here you can talk to government doctor, eSanjeevani and 104 helpline.")
        st.write("- **🚨 Emergency:** In emergency, what to do, which number to call, everything is in one place.")
        st.write("- **💡 Health Tips:** Daily routine, food, sleep, walk - all easy tips.")
        st.write("- **⚖️ BMI Calculator:** You can check if your weight is correct or not.")
        st.write("- **🏛️ Government Schemes:** Full information of government schemes like Ayushman, Jan Aushadhi, totally FREE.")
        st.write("- **🌐 Hindi / English:** You can run the app in Hindi or English.")
        st.markdown("---")
        st.markdown("### ❤️ What Is The Benefit?")
        st.write("- **Saves Time:** For small problems, you will not need to go to hospital again and again, you will know at home first.")
        st.write("- **Saves Money:** You will get information about FREE government treatment and cheap medicines.")
        st.write("- **Less Fear:** When you have a problem, you will know if it is normal or dangerous, so you will feel less scared.")
        st.write("- **Medicine Will Not Be Missed:** Medicine time of elderly and children will never be missed.")
        st.write("- **Easy For Everyone:** People who cannot read-write much, can also use by speaking or sending photo.")
        st.markdown("---")
        st.markdown("### 📱 How To Use? - Step By Step")
        st.write("**Step 1:** From left side, choose your language - Hindi or English.")
        st.write("**Step 2:** Go to Home, write your problem in the bottom box, like 'my stomach is paining', and press Send.")
        st.write("**Step 3:** App will tell you - Possible Causes, Danger Signs, and What To Do Now.")
        st.write("**Step 4:** If app asks 'Would you like to see a doctor?' and problem seems more, press Yes and talk to doctor.")
        st.write("**Step 5:** To remember medicine time, go to Medicine Reminder and set medicine name and time.")
        st.write("**Step 6:** If emergency, go to Emergency page and call 108 or 104.")
        st.write("**Step 7:** See Health Tips and Government Schemes page once daily, they have very useful things.")
        st.markdown("---")
        st.info("⚠️ **Important:** This app is only for information and first help. It cannot replace a doctor. If problem is more, fever is above 102, breathing problem, or injury, please see a doctor immediately or call 108.")
    show_floating_banner()
