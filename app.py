import streamlit as st
import google.generativeai as genai

# إعداد الصفحة وتنسيقها
st.set_page_config(page_title="Gemini Pro Engine", layout="wide")

st.markdown("""
<style>
    .stTextArea textarea {font-size: 16px !important; direction: rtl;}
</style>
""", unsafe_allow_html=True)

st.title("🚀 Gemini Pro - المحرك الخاص")

# --- نظام سحب المفاتيح الذكي ---
# يسحب المفاتيح المخزنة في Secrets تلقائياً
api_keys = [v for k, v in st.secrets.items() if k.startswith("KEY_")]

if not api_keys:
    st.error("⚠️ لم يتم العثور على مفاتيح! المرجو إضافتها في إعدادات Streamlit.")
    st.stop()

# تدوير المفاتيح عند الحاجة (نبدأ بالمفتاح الأول)
if "key_index" not in st.session_state:
    st.session_state.key_index = 0

def get_key():
    return api_keys[st.session_state.key_index]

# إعداد النموذج
try:
    genai.configure(api_key=get_key())
except Exception as e:
    st.error(f"خطأ في المفتاح: {e}")

# --- الواجهة ---
col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("لوحة التحكم")
    model_type = st.selectbox("اختر النموذج:", ["gemini-1.5-pro", "gemini-1.5-flash"])
    temp = st.slider("درجة الإبداع (Temperature):", 0.0, 1.0, 0.7)
    
    # رفع الملفات
    uploaded_file = st.file_uploader("رفع مستند أو صورة (اختياري)", type=["txt", "csv", "py", "md", "png", "jpg"])
    
    # منطقة الكتابة
    user_prompt = st.text_area("أدخل طلبك هنا:", height=200, placeholder="اشرح لي هذا الكود / حلل الصورة...")
    
    btn = st.button("⚡ تشغيل المعالجة", type="primary")

with col2:
    st.subheader("النتائج")
    if btn and user_prompt:
        with st.spinner('جاري الاتصال بـ Google Gemini...'):
            try:
                # تجهيز المحتوى
                content = [user_prompt]
                
                if uploaded_file:
                    # التعامل مع الصور أو النصوص
                    if uploaded_file.type.startswith('image'):
                        from PIL import Image
                        img = Image.open(uploaded_file)
                        content.append(img)
                    else:
                        text_data = uploaded_file.getvalue().decode("utf-8")
                        content.append(text_data)
                
                # الطلب من النموذج
                model = genai.GenerativeModel(model_type)
                response = model.generate_content(
                    content,
                    generation_config={"temperature": temp}
                )
                
                # عرض النتيجة
                st.markdown(response.text)
                st.success("تمت المعالجة بنجاح!")
                
            except Exception as e:
                st.error(f"حدث خطأ: {str(e)}")
                # هنا يمكن إضافة كود لتدوير المفتاح تلقائياً مستقبلاً
