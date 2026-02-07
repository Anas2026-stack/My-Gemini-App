import streamlit as st
import google.generativeai as genai

# إعداد الصفحة
st.set_page_config(page_title="My Gemini App", layout="wide")
st.title("🤖 My Gemini App")

# 1. مكان لوضع المفتاح مباشرة على الشاشة
# لن نستخدم Secrets الآن لتسهيل الأمور عليك
api_key = st.text_input("ضع مفتاح Google API هنا (يبدأ بـ AIza):", type="password")

if api_key:
    try:
        # 2. إعداد الاتصال
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        # 3. واجهة المحادثة
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # عرض الرسائل القديمة
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # 4. استقبال السؤال والرد
        if prompt := st.chat_input("اكتب سؤالك هنا..."):
            # عرض سؤالك
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # جلب الرد
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                try:
                    response = model.generate_content(prompt)
                    message_placeholder.markdown(response.text)
                    st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"حدث خطأ! تأكد أن المفتاح صحيح. (الخطأ: {e})")

    except Exception as e:
        st.error(f"المفتاح غير صالح: {e}")
else:
    st.warning("⚠️ التطبيق لن يعمل إلا إذا وضعت المفتاح في الخانة أعلاه.")
