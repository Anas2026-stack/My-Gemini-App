import streamlit as st
import google.generativeai as genai

# --- إعداد الصفحة ---
st.set_page_config(page_title="Gemini Auto-Pilot", layout="wide")

# --- التنسيق العربي ---
st.markdown("""
<style>
    .stTextArea textarea {direction: rtl; font-size: 16px;}
    div[data-testid="stChatMessage"] {direction: rtl; text-align: right;}
</style>
""", unsafe_allow_html=True)

# --- 1. المصادقة (Auth) ---
api_keys = [v for k, v in st.secrets.items() if k.startswith("KEY_")]
if not api_keys:
    st.error("المفاتيح مفقودة في Secrets")
    st.stop()

genai.configure(api_key=api_keys[0])

# --- 2. الشريط الجانبي (المحرك الذكي) ---
with st.sidebar:
    st.header("⚙️ المحرك التلقائي")
    
    # هذه هي الخطوة السحرية: نسأل جوجل "ماذا لديك؟" بدلاً من التخمين
    available_models = []
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        available_models.sort(reverse=True) # الأحدث أولاً
    except Exception as e:
        st.error(f"فشل الاتصال بجوجل: {e}")
    
    if not available_models:
        st.warning("لم يتم العثور على موديلات. تأكد من المفتاح.")
        st.stop()
        
    # القائمة المنسدلة تعرض فقط ما هو "موجود وحقيقي"
    selected_model = st.selectbox("اختر الموديل المتاح:", available_models)
    
    st.success(f"تم الاتصال بـ: {selected_model}")
    
    # زر إعادة الضبط
    if st.button("بدء محادثة جديدة"):
        st.session_state.messages = []
        st.rerun()

# --- 3. تشغيل التطبيق ---
st.title("🤖 المساعد الذكي (بدون أخطاء)")

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الشات
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# الإدخال والمعالجة
if prompt := st.chat_input("اكتب هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # استخدام الموديل المختار ديناميكياً
            model = genai.GenerativeModel(selected_model)
            
            # تجهيز التاريخ
            history_data = [{"role": m["role"].replace("assistant", "model"), "parts": [m["content"]]} 
                           for m in st.session_state.messages[:-1]]
            
            chat = model.start_chat(history=history_data)
            response = chat.send_message(prompt)
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"حدث خطأ أثناء الرد: {e}")
