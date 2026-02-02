import streamlit as st
import google.generativeai as genai
import time

# --- إعداد الصفحة ---
st.set_page_config(page_title="Gemini Pro Workstation", layout="wide")

# --- التنسيق العربي الصارم ---
st.markdown("""
<style>
    .stTextArea textarea {direction: rtl; font-size: 16px; font-family: 'Segoe UI', sans-serif;}
    div[data-testid="stChatMessage"] {direction: rtl; text-align: right; background-color: #1E1E1E; border-radius: 10px; padding: 10px;}
    .stSelectbox, .stButton button {direction: rtl;}
    h1, h2, h3 {text-align: right;}
</style>
""", unsafe_allow_html=True)

# --- سحب المفاتيح ---
api_keys = [v for k, v in st.secrets.items() if k.startswith("KEY_")]
if not api_keys:
    st.error("❌ المفاتيح مفقودة! راجع إعدادات Secrets.")
    st.stop()

# --- القائمة البيضاء (الموديلات المضمونة فقط) ---
# نستبعد الموديلات التجريبية التي تسبب مشاكل (Limit 0)
SAFE_MODELS = {
    "Gemini 1.5 PRO (العقل المدبر - للمهام المعقدة)": "gemini-1.5-pro",
    "Gemini 2.0 Flash Exp (سريع جداً - ذكي)": "gemini-2.0-flash-exp",
    "Gemini 1.5 Flash (اقتصادي)": "gemini-1.5-flash"
}

# --- الشريط الجانبي ---
with st.sidebar:
    st.header("⚙️ وحدة التحكم")
    
    # اختيار الموديل من القائمة الآمنة
    selected_name = st.radio("اختر المحرك:", list(SAFE_MODELS.keys()), index=0)
    model_id = SAFE_MODELS[selected_name]
    
    st.info(f"✅ المحرك النشط: `{model_id}`")
    
    temp = st.slider("درجة الإبداع (Temperature):", 0.0, 1.0, 0.4, help="0.0 للدقة الصارمة، 1.0 للتأليف")
    
    if st.button("🗑️ تنظيف الذاكرة وبدء جديد", type="primary"):
        st.session_state.messages = []
        st.rerun()

# --- إعداد المحرك ---
genai.configure(api_key=api_keys[0])
model = genai.GenerativeModel(model_id)

st.title("🧠 المستشار التقني (Pro)")

# --- إدارة الذاكرة ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة
for msg in st.session_state.messages:
    role = "user" if msg["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(msg["content"])

# --- معالجة الإدخال ---
if prompt := st.chat_input("اكتب مشكلتك المعقدة هنا..."):
    # تخزين وعرض سؤال المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # التفكير والرد
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # تحضير السياق (آخر 10 رسائل فقط لتفادي امتلاء الذاكرة)
            history = [{"role": m["role"].replace("assistant", "model"), "parts": [m["content"]]} 
                       for m in st.session_state.messages[:-1][-10:]]
            
            chat = model.start_chat(history=history)
            
            # البث المباشر (Stream) للرد
            with st.spinner(f'جاري التفكير بعمق عبر {model_id}...'):
                response_stream = chat.send_message(prompt, stream=True, generation_config={"temperature": temp})
                
                for chunk in response_stream:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            # التعامل مع أخطاء الحظر (Quota)
            err_msg = str(e)
            if "429" in err_msg:
                st.error("⏳ تجاوزت الحد المسموح للدقيقة. انتظر 30 ثانية ثم حاول مجدداً.")
            else:
                st.error(f"حدث خطأ تقني: {e}")
