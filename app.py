import streamlit as st
import google.generativeai as genai
from google.api_core import retry

# --- إعداد الصفحة ---
st.set_page_config(page_title="Gemini Expert Engine", layout="wide")

# --- التنسيق العربي ---
st.markdown("""
<style>
    .stTextArea textarea {direction: rtl; font-size: 16px; font-family: 'Courier New', monospace;}
    div[data-testid="stChatMessage"] {direction: rtl; text-align: right; background-color: #262730; border: 1px solid #444;}
    .stStatus {direction: rtl;}
</style>
""", unsafe_allow_html=True)

# --- 1. المصادقة ---
api_keys = [v for k, v in st.secrets.items() if k.startswith("KEY_")]
if not api_keys:
    st.error("❌ المفاتيح مفقودة في Secrets")
    st.stop()

genai.configure(api_key=api_keys[0])

# --- 2. الدستور (System Instructions) - سر القوة ---
# هذا ما يجعل الموديل ذكياً حتى لو كان الإصدار أقل
SYSTEM_PROMPT = """
أنت خبير برمجيات (Senior Solutions Architect).
- لغتك الأساسية: العربية التقنية.
- أسلوبك: مباشر، صارم، ويحلل جذور المشكلة (Root Cause).
- ممنوع الاعتذار أو الكلام الزائد.
- عند طلب كود، اكتب الكود كاملاً (Production Ready).
"""

# --- 3. إعداد الموديلات ---
# محاولة البرو أولاً، ثم الفلاش كخطة بديلة
try_models = ["gemini-1.5-pro", "gemini-1.5-flash"]
active_model = None

# فحص سريع أيهما يعمل
with st.sidebar:
    st.header("⚙️ حالة المحرك")
    status_box = st.status("جاري فحص الصلاحيات...", expanded=True)
    
    for m in try_models:
        try:
            status_box.write(f"تجربة الاتصال بـ {m}...")
            test_model = genai.GenerativeModel(m)
            # تجربة وهمية سريعة للتأكد من الكوتا
            test_model.generate_content("test")
            active_model = m
            status_box.update(label=f"✅ تم الاتصال بنجاح: {m}", state="complete", expanded=False)
            break # وجدنا واحداً يعمل، نتوقف
        except Exception as e:
            if "429" in str(e) or "Quota" in str(e):
                status_box.write(f"❌ {m}: الرصيد 0 (محظور في منطقتك)")
            else:
                status_box.write(f"❌ {m}: خطأ غير متوقع")
    
    if not active_model:
        status_box.update(label="⛔ كل المنافذ مغلقة!", state="error")
        st.error("للأسف، جوجل تغلق جميع الموديلات المجانية لهذا المفتاح. الحل الوحيد هو حساب جديد.")
        st.stop()

    st.success(f"المحرك النشط: `{active_model}`")
    if active_model == "gemini-1.5-flash":
        st.warning("⚠️ تنبيه: نعمل على Flash لأن Pro محظور، لكن تم تفعيل 'تعليمات الخبراء' لرفع الكفاءة.")

# --- 4. تشغيل المحرك ---
model = genai.GenerativeModel(
    active_model,
    system_instruction=SYSTEM_PROMPT
)

st.title("🚀 غرفة العمليات (بدون VPN)")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("أدخل الكود أو المشكلة هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner('جاري المعالجة...'):
            try:
                # تحويل الذاكرة
                history = [{"role": m["role"].replace("assistant", "model"), "parts": [m["content"]]} 
                           for m in st.session_state.messages[:-1]]
                
                chat = model.start_chat(history=history)
                response = chat.send_message(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error(f"حدث خطأ: {e}")
