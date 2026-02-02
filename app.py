import streamlit as st
import google.generativeai as genai

# --- إعداد الصفحة ---
st.set_page_config(page_title="Gemini Smart Hub", layout="wide")

# --- التنسيق العربي ---
st.markdown("""
<style>
    .stTextArea textarea {direction: rtl; font-size: 16px;}
    div[data-testid="stChatMessage"] {direction: rtl; text-align: right;}
</style>
""", unsafe_allow_html=True)

# --- سحب المفاتيح ---
api_keys = [v for k, v in st.secrets.items() if k.startswith("KEY_")]
if not api_keys:
    st.error("❌ المفاتيح مفقودة! تأكد من وضعها في Secrets.")
    st.stop()

# إعداد الاتصال
genai.configure(api_key=api_keys[0])

# --- الشريط الجانبي الذكي (Auto-Detection) ---
with st.sidebar:
    st.header("🎮 إعدادات المحرك")
    
    # جلب الموديلات المتاحة فعلياً لحسابك
    try:
        model_list = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                model_list.append(m.name)
        # ترتيبها ليظهر الأحدث أولاً
        model_list.sort(reverse=True)
    except:
        model_list = ["models/gemini-1.5-flash"] # احتياطي في حال الفشل
    
    # القائمة المنسدلة (لن تختار خطأ بعد اليوم)
    selected_model = st.selectbox("اختر الموديل النشط:", model_list)
    
    # باقي الإعدادات
    temp = st.slider("درجة الإبداع:", 0.0, 1.0, 0.7)
    if st.button("🗑️ مسح الذاكرة"):
        st.session_state.messages = []
        st.rerun()

# --- واجهة الدردشة ---
st.title(f"🤖 {selected_model.split('/')[-1]}")

# تهيئة الذاكرة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة السابقة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# استقبال السؤال
if prompt := st.chat_input("تحدث معي بالعربية..."):
    # عرض سؤال المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # المعالجة
    with st.chat_message("assistant"):
        with st.spinner('جاري التفكير...'):
            try:
                # إعداد الموديل المختار
                model = genai.GenerativeModel(selected_model)
                
                # تحويل الذاكرة لتنسيق جوجل
                history = [{"role": m["role"].replace("assistant", "model"), "parts": [m["content"]]} 
                           for m in st.session_state.messages[:-1]]
                
                chat = model.start_chat(history=history)
                response = chat.send_message(prompt, generation_config={"temperature": temp})
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error(f"⚠️ حدث خطأ: {e}")
